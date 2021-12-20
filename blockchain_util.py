import json
import uuid
import math

import web3
from eth_account.messages import defunct_hash_message
from web3 import Web3
from websockets.exceptions import ConnectionClosed
from config import GAS_PRICE_MULTIPLE,LOW_GAS_THRESHOLD, LOW_GAS_DEFAULT

class BlockChainUtil(object):
    def __init__(self, provider_url, contract_file_name):
        self._contract_file_name = contract_file_name
        self._provider_url = provider_url
        self.provider = None
        self.web3_object = None
        self._initialize_provider()

    def _initialize_provider(self):
        provider_lc = self._provider_url.lower()
        if str(provider_lc).startswith("https://"):
            self.provider = Web3.HTTPProvider(self._provider_url)
        elif str(provider_lc).startswith("ws://"):
            self.provider = web3.providers.WebsocketProvider(self._provider_url)
        else:
            raise Exception("Only HTTP_PROVIDER and WS_PROVIDER provider type are supported.")
        self.web3_object = Web3(self.provider)

    def get_code(self,address):
        return self.web3_object.eth.get_code(Web3.toChecksumAddress(address))

    def load_contract(self, path):
        with open(path) as f:
            contract = json.load(f)
        return contract

    def read_contract_address(self, net_id, path, key):
        contract = self.load_contract(path)
        return Web3.toChecksumAddress(contract[str(net_id)][key])

    #def contract_instance(self, contract_abi, address):
    #    if self._provider_type == "HTTP_PROVIDER":
    #        provider = Web3.HTTPProvider(self._provider_url)
    #    elif self._provider_type == "WS_PROVIDER":
    #        provider = web3.providers.WebsocketProvider(self._provider_url)
    #    web3_object = Web3(provider)
    #    self.provider = provider
    #    self.web3_object = web3_object
    #    return web3_object.eth.contract(abi=contract_abi, address=address)

    def get_contract_instance(self, base_path, net_id):
        contract_network_path, contract_abi_path = self._get_contract_file_paths(base_path)

        contract_address = self.read_contract_address(net_id=net_id, path=contract_network_path,
                                                      key='address')
        contract_abi = self.load_contract(contract_abi_path)
        print(f"contract address is {contract_address}")
        #contract_instance = self.contract_instance(contract_abi=contract_abi, address=contract_address)
        contract_instance = self.web3_object.eth.contract(abi=contract_abi, address=contract_address)

        return contract_instance

    def generate_signature(self, data_types, values, signer_key):
        signer_key = "0x" + signer_key if not signer_key.startswith("0x") else signer_key
        message = web3.Web3.soliditySha3(data_types, values)
        signature = self.web3_object.eth.account.signHash(defunct_hash_message(message), signer_key)
        return signature.signature.hex()

    def generate_signature_bytes(self, data_types, values, signer_key):
        signer_key = "0x" + signer_key if not signer_key.startswith("0x") else signer_key
        message = web3.Web3.soliditySha3(data_types, values)
        signature = self.web3_object.eth.account.signHash(defunct_hash_message(message), signer_key)
        return bytes(signature.signature)

    def get_nonce(self, address):
        """ transaction count includes pending transaction also. """
        nonce = self.web3_object.eth.getTransactionCount(address)
        return nonce

    def sign_transaction_with_private_key(self, private_key, transaction_object):
        return self.web3_object.eth.account.signTransaction(transaction_object, private_key).rawTransaction

    def create_transaction_object(self, net_id, contract_instance, method_name, address, *positional_inputs, gas=None):
        nonce = self.get_nonce(address=address)

        print(f"Base gas_price :: {self.web3_object.eth.gasPrice}")
        print(f"nonce :: {nonce}")
        print(f"positional_inputs :: {positional_inputs}")
        gas_price = math.floor(GAS_PRICE_MULTIPLE * (self.web3_object.eth.gasPrice))
        print(f"{GAS_PRICE_MULTIPLE} times gas_price :: {gas_price}")
        
        if LOW_GAS_THRESHOLD != "" and LOW_GAS_THRESHOLD > 0:
            if gas_price < LOW_GAS_THRESHOLD:
                gas_price = LOW_GAS_DEFAULT #Gas Price as 121 Gwei (121000000000)
                print(f"Increaed gas_price as threshold breached :: {gas_price}")

        options = {
            "from": address,
            "nonce": nonce,
            "gasPrice": gas_price,
            "chainId": net_id
        }
        if gas is not None:
            options.update({"gas": gas})
        transaction_object = getattr(contract_instance.functions, method_name)(
            *positional_inputs).buildTransaction(options)
        return transaction_object

    def process_raw_transaction(self, raw_transaction):
        return self.web3_object.eth.sendRawTransaction(raw_transaction).hex()

    def create_account(self):
        account = self.web3_object.eth.account.create(uuid.uuid4().hex)
        return account.address, account.privateKey.hex()

    def __revive_connection(self):
        try:
            connected = self.web3_object.isConnected()
        except ConnectionClosed as e:
            print(f"Connection is closed:: {repr(e)}")
            connected = False
        if not connected:
            self._initialize_provider()
        return

    def get_block(self, block_number):
        self.__revive_connection()
        return self.web3_object.eth.get_block(block_number)

    def get_current_block_no(self):
        self.__revive_connection()
        return self.web3_object.eth.blockNumber

    def get_transaction(self, transaction_hash):
        return self.web3_object.eth.get_transaction(transaction_hash)

    def get_transaction_receipt_from_blockchain(self, transaction_hash):
        return self.web3_object.eth.getTransactionReceipt(transaction_hash)

    def _get_contract_file_paths(self, base_path):
        contract_network_path = base_path + "/{}/{}".format("networks", self._contract_file_name)
        contract_abi_path = base_path + "/{}/{}".format("abi", self._contract_file_name)

        return contract_network_path, contract_abi_path

    @staticmethod
    def call_contract_function(contract, contract_function, positional_inputs):
        function = getattr(contract.functions, contract_function)
        result = function(*positional_inputs).call()
        return result
