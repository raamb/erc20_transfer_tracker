import os
import time

from repository import Repository
from erc20_transfer_handler import ERC20TokenHandler
from config import BATCHES_IN_A_RUN, INFURA_URL_HTTPS, NET_ID, STARTING_BLOCK_NUMBER

class AGIXTransfersHandler(ERC20TokenHandler):
    BATCH_SIZE = 200

    def __init__(self, ws_provider, net_id):
        super().__init__(ws_provider, net_id, "SingularityNetToken.json")
        self._repository = Repository()
        self._contract_name = "SingularityNetToken"
        self._insert_balances = 'INSERT INTO agix_balances ' + \
           '(wallet_address, is_contract, balance_in_cogs, block_number, row_created, row_updated) ' + \
           'VALUES (%s, %s, %s, %s, current_timestamp, current_timestamp) ' + \
           'ON DUPLICATE KEY UPDATE block_number = %s, row_updated = current_timestamp'
        self._insert_transfers = 'INSERT INTO agix_transfers ' + \
        '(from_address, to_address, amount_in_cogs, transaction_hash, block_number, logIndex, transactionIndex, raw_event, row_created, row_updated) ' + \
        'VALUES (%s, %s, %s, %s, %s, %s,%s,%s, current_timestamp, current_timestamp) ' + \
        'ON DUPLICATE KEY UPDATE amount_in_cogs = %s, row_updated = current_timestamp '  
        self._balances = []
        self._transfers = []
        self._contracts = []

   
    def _get_base_contract_path(self):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', 'singularitynet-token-contracts'))
               
    def __batch_insert(self, values, is_transfer, force=False):
        #print(values)
        if is_transfer:
            query = self._insert_transfers
            all_values = self._transfers
        else:
            query = self._insert_balances
            all_values = self._balances

        start = time.process_time()
        number_of_rows = len(all_values)
        if (force and number_of_rows > 0) or number_of_rows >= 50:
            self._repository.bulk_query(query, all_values)
            if is_transfer:
                self._transfers.clear()
            else:
                self._balances.clear()       
            print(f"*****Transfer {(time.process_time() - start)} seconds. Inserted {number_of_rows} rows")
        
        if(len(values) > 0):
            all_values.append(tuple(values))

    def _get_is_contract(self, address):
        is_contract = 0
        if address in self._contracts:
            is_contract = 1
        else:
            if self._is_contract(address):
                self._contracts.append(address)
                is_contract = 1
        return is_contract

    def _process_events(self, events):
        for event in events:
            if 'event' not in event:
                raise Exception(f"Event not found. Only Transfer events expected")

            if event['event'] != "Transfer":
                raise Exception(f"Found event {event['event']}. Only Transfer events expected")

            from_address = event['args']['from']
            to_address = event['args']["to"]
            value = event['args']['value']
            block_number = event['blockNumber']

            print(f"Transfer of {value} cogs from {from_address} to {to_address}")

            self.__batch_insert([from_address, self._get_is_contract(from_address), self._get_balance(from_address), block_number, block_number], False)
            self.__batch_insert([to_address, self._get_is_contract(to_address), self._get_balance(to_address), block_number, block_number], False)

            self.__batch_insert([from_address, to_address, value, 
                                    str(event['transactionHash'].hex()), block_number, event['logIndex'], 
                                    event['transactionIndex'], str(event), value], True)
            

    def _get_starting_block_number(self):
        result = self._repository.execute("select max(block_number) as starting_block_number from agix_transfers")
        print(result)
        starting_block_number = result[0]['starting_block_number']
        if starting_block_number is None:
            starting_block_number = STARTING_BLOCK_NUMBER
        
        return int(starting_block_number)

    def read_events(self):
        batch_index = 0
        from_block_number = self._get_starting_block_number()
        end_block_number = self._blockchain_util.get_current_block_no()
        while batch_index < BATCHES_IN_A_RUN:
            to_block_number = from_block_number+int(self.BATCH_SIZE)
            print(f"Reading token event from {from_block_number} to {to_block_number}. Batch {batch_index}. Size of transfers {len(self._transfers)}")
            try:
                events = self._read_contract_events(
                    from_block_number, to_block_number, 'Transfer', None)
                self._process_events(events)
                from_block_number = to_block_number
            except Exception as e:
                raise Exception(f"Excetion {e}. Reinitializing Blockchain")
            
            if to_block_number > end_block_number:
                print("Done with all events")
                break

            batch_index += 1
            
        self.__batch_insert([],False, True) 
        self.__batch_insert([],True, True) 
        print(f"Completed reading events till blocknumber {to_block_number}")
        return

tp = AGIXTransfersHandler(INFURA_URL_HTTPS, NET_ID)
tp.read_events()