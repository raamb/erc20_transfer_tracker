import time

from decimal import Decimal
from web3 import Web3
from erc20_transfer_handler import ERC20TokenHandler
from contract_details import DETAILS

insert_balances = 'INSERT INTO {TABLE_NAME} ' + \
'(wallet_address, amount, balance_type, balance_sub_type, block_number, row_created, row_updated) ' + \
'VALUES (%s, %s, \'STAKED\', \'{STAKE_TYPE}\', \'0\', current_timestamp, current_timestamp) ' + \
'ON DUPLICATE KEY UPDATE amount = %s, row_updated = current_timestamp'
select_existing_stakes = "select wallet_address from {TABLE_NAME} where balance_type = \'STAKED\'"

class StakingHandler(ERC20TokenHandler):
    def __init__(self, ws_provider, net_id, transfer_type, repository):
        super().__init__(ws_provider, net_id, DETAILS[transfer_type]['contract_file_name'], DETAILS[transfer_type]['contract_path'])
        self._repository = repository
        self._insert_balances = insert_balances.format(TABLE_NAME=DETAILS[transfer_type]["table_name"], STAKE_TYPE=DETAILS[transfer_type]['stake_type'])
        self._select_existing_stakes = select_existing_stakes.format(TABLE_NAME=DETAILS[transfer_type]['table_name'])
        self._balances = []
        self._stake_map_index = 0
        self._window_total_stake = 0
        self._window_reward_amount = 0
        self._window_reward_amount_index = DETAILS[transfer_type]['window_reward_amount_index']
                    
    def _batch_insert(self, values, force=False):
        start = time.process_time()
        number_of_rows = len(self._balances)
        if (force and number_of_rows > 0) or number_of_rows >= 50:
            self._repository.bulk_query(self._insert_balances, self._balances)
            self._balances.clear()       
            print(f"*****Staked {(time.process_time() - start)} seconds. Inserted {number_of_rows} rows")
        
        if(len(values) > 0):
            self._balances.append(tuple(values))
    
    def _populate_stake_info(self):
        index = self._call_contract_function("currentStakeMapIndex", [])
        self._stake_map_index = Decimal(index)
        self._window_total_stake = Decimal(self._call_contract_function("windowTotalStake", []))
        stake_map = self._call_contract_function("stakeMap", [index])
        self._window_reward_amount = Decimal(stake_map[self._window_reward_amount_index])
        print(f"Index: {self._stake_map_index} _window_total_stake: {self._window_total_stake} Reward: {self._window_reward_amount}")

  
    # First call GetStakeHolders method
    # for each user call balances method
    # for sdao unbonded - for each deposited user call userInfo and pendingRewards to compute staked + reward amount
    def process(self):
        start = time.process_time()
        self._populate_stake_info()

        seen_stakers = {}
        result = self._repository.execute(self._select_existing_stakes)
        
        for address in result:
            seen_stakers[address['wallet_address']] = 0
        print(f"Seen Stakes {len(seen_stakers)}")

        all_stakers = self._call_contract_function("getStakeHolders", [])
        print(f"TIMETAKEN: {(time.process_time() - start)} seconds to get stakers")

        for staker in all_stakers:
            stake = Decimal(self._call_contract_function("balances", [Web3.toChecksumAddress(staker)]))
            if staker in seen_stakers:
                seen_stakers.pop(staker)
            reward = stake * (self._window_reward_amount / (self._window_total_stake - self._window_reward_amount))
            balance = stake + reward
            self._batch_insert([staker, balance, balance], False)
        
        if len(seen_stakers) == 0 :
            print("No unstakes")

        for seen in seen_stakers:
            print(f"Setting {seen} to {0}")
            self._batch_insert([seen, 0, 0], False)

        self._batch_insert([],True) 
        print(f"Completed processing {len(all_stakers)} stakers")
        print(f"TIMETAKEN: {(time.process_time() - start)} seconds to process all stakes")
        return


class UnBondedStakingHandler(StakingHandler):
    def __init__(self, ws_provider, net_id, transfer_type, repository):
        super().__init__(ws_provider, net_id, transfer_type, repository)
        self._limit=500
        self._offset=0
        self._count_of_stakers=0
    
    def process(self):       
        print(f"Unbonded {self._base_contract_path} {self._net_id} {'address'}") 
        query = 'select * from sdao_transfers where to_address = \'{ADDRESS}\' limit {RUN_LIMIT} offset {RUN_OFFSET}' \
            .format(ADDRESS=self._contract_address, RUN_LIMIT=self._limit, RUN_OFFSET=self._offset)
        
        result = self._repository.execute(query)
        if len(result) == 0:
            self._batch_insert([],True) 
            print(f"Completed processing {self._count_of_stakers} stakers")
            return

        for address in result:
            self._count_of_stakers += 1
            staker = address['from_address']
            response = self._call_contract_function("userInfo", [0, Web3.toChecksumAddress(staker)])
            balance = Decimal(response[0])
            rewards = self._call_contract_function("pendingRewards", [0, Web3.toChecksumAddress(staker)])
            total = Decimal(rewards) + balance
            print(f"{staker} {total} {balance} {rewards}")
            self._batch_insert([staker, total, total], False)
        
        self._offset += self._limit
        self.process()
        return
