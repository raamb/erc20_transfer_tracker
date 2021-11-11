import time

from erc20_transfer_handler import ERC20TokenHandler
from config import BATCHES_IN_A_RUN, STARTING_BLOCK_NUMBER
from contract_details import DETAILS

select_contracts = 'select wallet_address, is_contract from {TABLE_NAME} where is_contract = 1'
insert_balances = 'INSERT INTO {TABLE_NAME} ' + \
    '(wallet_address, is_contract, amount, balance_type, balance_sub_type, block_number, row_created, row_updated) ' + \
    'VALUES (%s, %s, %s,\'BALANCE\',\'BALANCE\', %s, current_timestamp, current_timestamp) ' + \
    'ON DUPLICATE KEY UPDATE amount = %s, block_number = %s, row_updated = current_timestamp'
insert_transfers = 'INSERT INTO {TABLE_NAME} ' + \
'(from_address, to_address, amount, transaction_hash, block_number, logIndex, transactionIndex, raw_event, row_created, row_updated) ' + \
'VALUES (%s, %s, %s, %s, %s, %s,%s,%s, current_timestamp, current_timestamp) ' + \
'ON DUPLICATE KEY UPDATE amount = %s, row_updated = current_timestamp '  
select_block_number = "select max(block_number) as starting_block_number from {TABLE_NAME}"

class TransfersHandler(ERC20TokenHandler):
    BATCH_SIZE = 200

    def __init__(self, ws_provider, net_id, transfer_type, repository):
        super().__init__(ws_provider, net_id, DETAILS[transfer_type]['contract_file_name'], DETAILS[transfer_type]['contract_path'])
        self._repository = repository
        self._transfer_type = transfer_type
        self._select_contracts = select_contracts.format(TABLE_NAME=DETAILS[transfer_type]['balances_table_name'])
        self._insert_balances = insert_balances.format(TABLE_NAME=DETAILS[transfer_type]['balances_table_name'])
        self._insert_transfers = insert_transfers.format(TABLE_NAME=DETAILS[transfer_type]['transfers_table_name'])
        self._select_block_number = select_block_number.format(TABLE_NAME=DETAILS[transfer_type]['transfers_table_name'])
        self._amount_key = DETAILS[transfer_type]['amount_key']
        self._balances = []
        self._transfers = []
        self._contracts = None
        self.__populate_seen_contracts()

    def __populate_seen_contracts(self):
        result = self._repository.execute(self._select_contracts)
        self._contracts = []
        for row in result:
            self._contracts.append(row['wallet_address'])
        print(f"Pre-populated {len(self._contracts)} contract addresses")

    def __batch_insert(self, values, is_transfer, force=False):
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

            #print(event)
            from_address = event['args']['from']
            to_address = event['args']["to"]
            value = event['args'][self._amount_key]
            block_number = event['blockNumber']

            #print(f"Transfer of {value} cogs from {from_address} to {to_address}")

            from_balance = self._get_balance(from_address)
            self.__batch_insert([from_address, self._get_is_contract(from_address), from_balance, block_number, from_balance, block_number], False)
            to_balance = self._get_balance(to_address)
            self.__batch_insert([to_address, self._get_is_contract(to_address), to_balance, block_number, to_balance, block_number], False)

            self.__batch_insert([from_address, to_address, value, 
                                    str(event['transactionHash'].hex()), block_number, event['logIndex'], 
                                    event['transactionIndex'], str(event), value], True)
            

    def _get_starting_block_number(self):
        result = self._repository.execute(self._select_block_number)
        print(result)
        starting_block_number = result[0]['starting_block_number']
        if starting_block_number is None:
            starting_block_number = STARTING_BLOCK_NUMBER
        
        return int(starting_block_number)

    def process(self):
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