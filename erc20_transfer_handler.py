import time

from web3 import Web3
from blockchain_util import BlockChainUtil

insert_events = 'INSERT INTO raw_events ' + \
'(block_number, transaction_hash, contract_address, log_index, transaction_index, event_name, raw_event, row_created, row_updated) ' + \
'VALUES (%s, %s, %s, %s, %s, %s, %s, current_timestamp, current_timestamp) ' + \
'ON DUPLICATE KEY UPDATE row_updated = current_timestamp'

class ERC20TokenHandler():
    def __init__(self, ws_provider, net_id, contract_file_name, base_contract_path):
        self._provider = ws_provider
        self._net_id = net_id
        self.__contract = None
        self._contract_file_name = contract_file_name
        self._contract_address = "0x0"
        self._base_contract_path = base_contract_path
        self._initialize_blockchain()
        

    def _initialize_blockchain(self):
        self.__contract = None
        if self._provider.startswith('wss://'):
            self._blockchain_util = BlockChainUtil(self._provider, self._contract_file_name)
        else:
            self._blockchain_util = BlockChainUtil(self._provider, self._contract_file_name)
        print("**** PATH " + str(self._base_contract_path))
        contract_network_path, contract_abi_path  = self._blockchain_util._get_contract_file_paths(self._base_contract_path)
        self._contract_address = self._blockchain_util.read_contract_address(net_id=self._net_id, path=contract_network_path,
                                                      key='address')

    def _is_contract(self, address):
        is_contract = False
        contract_code = self._blockchain_util.get_code(address)
        if len(contract_code) > 3:
            print(f"Found contract {address}")
            is_contract = True
        return is_contract
        
    def _get_contract(self):
        if not self.__contract:
            self.__contract = self._blockchain_util.get_contract_instance(
            base_path=self._base_contract_path, net_id=self._net_id)
        return self.__contract

    def _call_contract_function(self, method_name, positional_inputs):
        contract = self._get_contract()
        return self._blockchain_util.call_contract_function(
            contract=contract, contract_function=method_name, positional_inputs=positional_inputs)

    def __get_filtered_events(self,event_object, start_block_number, end_block_number, argument_filters):
        if argument_filters:
            transfer_events = event_object.createFilter(fromBlock=start_block_number,
                                           toBlock=end_block_number, argument_filters=argument_filters)
        else:
            transfer_events = event_object.createFilter(fromBlock=start_block_number,
                                           toBlock=end_block_number)
        return transfer_events

    def _persist_raw_events(self, event):   
        #(block_number, tranasction_hash, contract_address, log_index, transaction_index, event_name, raw_event, row_created, row_updated) 
        self._repository.execute(insert_events,[event['blockNumber'], str(event['transactionHash'].hex()), self._contract_address, event['logIndex'], event['transactionIndex'], event['event'], str(event)])

    def _get_events_from_blockchain(self, start_block_number, end_block_number, event_name, argument_filters=None):
        contract = self._get_contract()
        all_blockchain_events = []
        if event_name is None:
            contract_events = contract.events
            for attributes in contract_events.abi:
                if attributes['type'] == 'event':
                    event_object = getattr(contract.events, str(attributes['name']))
                    filtered_events = self.__get_filtered_events(event_object, start_block_number, end_block_number, argument_filters)
                    event_data = filtered_events.get_all_entries()
                    if len(event_data) > 0:
                        all_blockchain_events.extend(event_data)            
        else:
            event_object = getattr(contract.events, event_name)
            filtered_events = self.__get_filtered_events(event_object, start_block_number, end_block_number, argument_filters)
            all_blockchain_events = filtered_events.get_all_entries() 

        for event in all_blockchain_events:
            self._persist_raw_events(event)
        return all_blockchain_events

    def _read_contract_events(self, start_block_number, end_block_number, event_name, from_address):
        events = self._get_events_from_blockchain(start_block_number, end_block_number, event_name, from_address)
        return events

    def read_events(self):
        raise Exception("Not implemented read_events")
    
    def get_contract_address_path(self):
        raise Exception("Not implemented get_contract_address")

    def _get_balance(self, address):
        balance = self._call_contract_function("balanceOf", [Web3.toChecksumAddress(address)])
        #print(f"{(time.process_time() - start)} seconds. Balance of {address} is :: {balance}")
        return balance   

