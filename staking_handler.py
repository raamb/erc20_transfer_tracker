import time

from web3 import Web3
from repository import Repository
from erc20_transfer_handler import ERC20TokenHandler

insert_balances = 'INSERT INTO TABLE_NAME ' + \
'(wallet_address, amount, balance_type, balance_sub_type, block_number, row_created, row_updated) ' + \
'VALUES (%s, %s, \'STAKED\', \'STAKE_TYPE\', \'0\', current_timestamp, current_timestamp) ' + \
'ON DUPLICATE KEY UPDATE amount = %s, row_updated = current_timestamp'
select_existing_stakes = "select wallet_address from TABLE_NAME where balance_type = \'STAKED\'"

class StakingHandler(ERC20TokenHandler):
    
    def __init__(self, ws_provider, net_id, contract_file_name, table_name, stake_type):
        super().__init__(ws_provider, net_id, contract_file_name)
        self._repository = Repository()
        self._insert_balances = insert_balances.replace("TABLE_NAME", table_name).replace("STAKE_TYPE", stake_type)
        self._select_existing_stakes = select_existing_stakes.replace("TABLE_NAME", table_name)
        self._balances = []
        self._base_contract_path = ''
   
    def set_base_contract_path(self, base_contract_path):
        self._base_contract_path = base_contract_path
        
    def _get_base_contract_path(self):
        return self._base_contract_path
               
    def __batch_insert(self, values, force=False):
        start = time.process_time()
        number_of_rows = len(self._balances)
        if (force and number_of_rows > 0) or number_of_rows >= 50:
            self._repository.bulk_query(self._insert_balances, self._balances)
            self._balances.clear()       
            print(f"*****Staked {(time.process_time() - start)} seconds. Inserted {number_of_rows} rows")
        
        if(len(values) > 0):
            self._balances.append(tuple(values))
  
    # First call GetStakeHolders method
    # for each user call balances method
    # for sdao unbonded - for each deposited user call userInfo and pendingRewards to compute staked + reward amount
    def process_stake(self):
        start = time.process_time()
        seen_stakers = {}
        result = self._repository.execute(self._select_existing_stakes)
        
        for address in result:
            seen_stakers[address['wallet_address']] = 0
        print(f"Seen Stakes {len(seen_stakers)}")

        all_stakers = self._call_contract_function("getStakeHolders", [])
        print(f"TIMETAKEN: {(time.process_time() - start)} seconds to get stakers")

        for staker in all_stakers:
            balance = self._call_contract_function("balances", [Web3.toChecksumAddress(staker)])
            if staker in seen_stakers:
                seen_stakers.pop(staker)
            self.__batch_insert([staker, balance, balance], False)
        
        if len(seen_stakers) == 0 :
            print("No unstakes")

        for seen in seen_stakers:
            print(f"Setting {seen} to {0}")
            self.__batch_insert([seen, 0, 0], False)

        self.__batch_insert([],True) 
        print(f"Completed processing {len(all_stakers)} stakers")
        print(f"TIMETAKEN: {(time.process_time() - start)} seconds to process all stakes")
        return