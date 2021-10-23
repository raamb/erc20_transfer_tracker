import time

from decimal import Decimal
from repository import Repository
from erc20_transfer_handler import ERC20TokenHandler
from config import BATCHES_IN_A_RUN


class UniswapV2TransfersHandler(ERC20TokenHandler):
    BATCH_SIZE = 100

    def __init__(self, ws_provider, net_id, contract_file_name, balances_table_name):
        super().__init__(ws_provider, net_id, contract_file_name)
        self._repository = Repository()
        self._insert_balances = "INSERT INTO {TABLE_NAME} ".format(TABLE_NAME=balances_table_name) + \
               "(wallet_address, is_contract, amount, balance_type, balance_sub_type, block_number, context, row_created, row_updated) " + \
               "VALUES (%s, %s, %s,\'LP_SHARE\',%s, %s, %s, current_timestamp, current_timestamp) " + \
               "ON DUPLICATE KEY UPDATE amount =%s, block_number = %s, context = %s, row_updated = current_timestamp"
        print(self._insert_balances)
        self._select_block_number = "select block_number, pool_name from uniswap_v2_tracker where contract_address = %s"
        self._update_block_number = "update uniswap_v2_tracker set block_number = %s, snapshot_timestamp = current_timestamp,row_updated = current_timestamp where contract_address = %s"
        self._contract_address = ''
        self._pool_name = ''
        self._balances = []
        self._start_block_number = ''
        self._token_handler = None

    def set_token_handler(self, token_handler):
        self._token_handler = token_handler

    def set_base_contract_path(self, base_contract_path):
        self._base_contract_path = base_contract_path        

    def _get_base_contract_path(self):
       return self._base_contract_path

    def _populate_contract_details(self):
        print(f"In populate {self._base_contract_path}")
        contract_network_path, contract_abi_path  = self._blockchain_util._get_contract_file_paths(self._base_contract_path)
        self._contract_address = self._blockchain_util.read_contract_address(net_id=self._net_id, path=contract_network_path,
                                                      key='address')
        result = self._repository.execute(self._select_block_number,[self._contract_address])
        print(result)
        self._pool_name = result[0]['pool_name']
        self._start_block_number = result[0]['block_number']

    def _batch_insert(self, values, force=False):
        start = time.process_time()
        number_of_rows = len(self._balances)
        if (force and number_of_rows > 0) or number_of_rows >= 50:
            self._repository.bulk_query(self._insert_balances, self._balances)
            self._balances.clear()
            print(f"*****Time taken {(time.process_time() - start)} seconds. Inserted {number_of_rows} rows")
        
        if(len(values) > 0):
            self._balances.append(tuple(values))

    def _compute_token_contribution(self, event):
        sender = event['args']['to']
        block_number = event['blockNumber']
        total_supply = 1
        contract_token_balance = 0

        uni_v2_balance = Decimal(self._get_balance(sender))
        if uni_v2_balance > 0:
            total_supply = Decimal(self._call_contract_function("totalSupply", []))
            contract_token_balance = Decimal(self._token_handler._get_balance(self._contract_address))
        
        sender_token_share = uni_v2_balance / total_supply * contract_token_balance
        print(f"{event['event']} - By {sender} with balance {uni_v2_balance}. Total supply {total_supply} Contract Token Balance {contract_token_balance}")

        context = str({'tx_hash': str(event['transactionHash'].hex()), 'uni_v2_balance': uni_v2_balance, 'total_supply' : total_supply, 'contract_token_balance': contract_token_balance})
        print("Inserting ******")
        print([sender, 0, sender_token_share, self._pool_name, block_number, context, sender_token_share, block_number, context])
        self._batch_insert([sender, 0, sender_token_share, self._pool_name, block_number, context, sender_token_share, block_number, context], False)
        return

    def _process_transfer(self, event):
        print(event)
        from_address = event['args']['from']
        if from_address != '0x0000000000000000000000000000000000000000':
            print('Ignoring transfer')
            return
        self._compute_token_contribution(event)
        return

    def _process_mint_burn(self, event):
        print(event)
        self._compute_token_contribution(event)
        return
        
    def _process_events(self, events):
        for event in events:
            if 'event' not in event:
                raise Exception(f"Event not found. Only Transfer events expected")

            if event['event'] == 'Transfer' or event['event'] == 'Burn':
                self._process_mint_burn(event)
            else:
                print(f"Ignoring event {event['event']}")

    def read_events(self):
        self._populate_contract_details()
        batch_index = 0
        from_block_number = self._start_block_number
        end_block_number = self._blockchain_util.get_current_block_no()
        while batch_index < BATCHES_IN_A_RUN:
            to_block_number = from_block_number+int(self.BATCH_SIZE)
            print(f"Reading token event from {from_block_number} to {to_block_number}. Batch {batch_index}.")
            try:
                events = self._read_contract_events(
                    from_block_number, to_block_number, None, None)
                self._process_events(events)
                from_block_number = to_block_number
                self._repository.execute(self._update_block_number,[to_block_number, self._contract_address])
            except Exception as e:
                raise Exception(f"Excetion {e}. Reinitializing Blockchain")
            
            if to_block_number > end_block_number:
                print("Done with all events")
                break
            batch_index += 1
            
        self._batch_insert([],True) 
        print(f"Completed reading events till blocknumber {to_block_number}")
        return