import time

from web3 import Web3
from decimal import Decimal
from erc20_transfer_handler import ERC20TokenHandler
from config import BATCHES_IN_A_RUN
from contract_details import DETAILS

class UniswapV2TransfersHandler(ERC20TokenHandler):
    BATCH_SIZE = 100

    def __init__(self,ws_provider, net_id, transfer_type, repository):
        super().__init__(ws_provider, net_id, DETAILS[transfer_type]['contract_file_name'], DETAILS[transfer_type]['contract_path'])
        self._repository = repository
        self._insert_balances = "INSERT INTO {TABLE_NAME} ".format(TABLE_NAME=DETAILS[transfer_type]['balances_table_name']) + \
               "(wallet_address, is_contract, amount, balance_type, balance_sub_type, block_number, context, row_created, row_updated) " + \
               "VALUES (%s, %s, %s,\'LP_SHARE\',%s, %s, %s, current_timestamp, current_timestamp) " + \
               "ON DUPLICATE KEY UPDATE amount =%s, block_number = %s, context = %s, row_updated = current_timestamp"
        print(self._insert_balances)
        base_token = DETAILS[transfer_type]['token_details']
        self._token_handler = ERC20TokenHandler(ws_provider, net_id, DETAILS[base_token]['contract_file_name'], DETAILS[base_token]['contract_path'])
        self.__populate_yield_farming_address(ws_provider, net_id,DETAILS[transfer_type]['yield_farming_token'])
        self._select_block_number = "select block_number, pool_name from uniswap_v2_tracker where contract_address = %s"
        self._update_block_number = "update uniswap_v2_tracker set block_number = %s, snapshot_timestamp = current_timestamp,row_updated = current_timestamp where contract_address = %s"
        self._pool_name = ''
        self._balances = []
        self._start_block_number = ''
        self._pool_index = DETAILS[transfer_type]['pool_index']

    ## TODO simplify reading contract address
    def __populate_yield_farming_address(self, ws_provider, net_id,yield_contract):
        self._yield_farming_handler = ERC20TokenHandler(ws_provider, net_id, DETAILS[yield_contract]['contract_file_name'], DETAILS[yield_contract]['contract_path'])
        contract_network_path, contract_abi_path = self._yield_farming_handler._blockchain_util._get_contract_file_paths(DETAILS[yield_contract]['contract_path'])
        self._yield_farming_address = self._yield_farming_handler._blockchain_util.read_contract_address(net_id=net_id, path=contract_network_path,
                                                      key='address')
        print("**** Yield address " + str(self._yield_farming_handler))

    
    def _populate_contract_details(self):
        print(f"In populate {self._base_contract_path}")
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

    def _compute_token_contribution(self, event, balance_from_yield_farming=False):
        sender = event['args']['to']
        if balance_from_yield_farming:
            # User is yield farming so we need to consider the user as the sender
            sender = event['args']['from']

        block_number = event['blockNumber']
        total_supply = 1
        contract_token_balance = 0

        uni_v2_balance = Decimal(self._get_balance(sender))
        if balance_from_yield_farming:
            #consider the share that the user has yield farmed as well
            response = self._yield_farming_handler._call_contract_function("userInfo", [self._pool_index, Web3.toChecksumAddress(sender)])
            balance = Decimal(response[0])
            uni_v2_balance = uni_v2_balance + balance
            print(f"######## Yield farmed user {sender} with balance {uni_v2_balance}")


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
        #print(event)
        from_address = event['args']['from']
        to_address = event['args']['to']
        balance_from_yield_farming = False
        print(f"************ Sender {to_address} YieldFarming {self._yield_farming_address}")
        if str(to_address).lower() == self._yield_farming_address.lower():
            print(f"##### Transfer to {self._yield_farming_address} from {from_address}.")
            balance_from_yield_farming = True

        self._compute_token_contribution(event, balance_from_yield_farming)
        return

    def _process_mint_burn(self, event):
        print(event)
        self._compute_token_contribution(event)
        return
        
    def _process_events(self, events):
        for event in events:
            if 'event' not in event:
                raise Exception(f"Event not found. Only Transfer events expected")

            if event['event'] == 'Transfer':
                self._process_transfer(event)
            elif event['event'] == 'Burn':
                self._process_mint_burn(event)
            #else:
            #    print(f"Ignoring event {event['event']}")

    def process(self):
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
        