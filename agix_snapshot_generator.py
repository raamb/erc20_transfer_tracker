import time
import csv
from decimal import Decimal

from repository import Repository
from blockchain_util import BlockChainUtil
from config import INFURA_URL_HTTPS, NET_ID

class AGIXToken():
    def __init__(self, address, is_contract):
        self._address = address
        self._balance_in_cogs = Decimal(0)
        self._is_contract = is_contract
    
    def add_cogs(self, balance_in_cogs):
        self._balance_in_cogs = Decimal(self._balance_in_cogs) + Decimal(balance_in_cogs)
    
    def remove_cogs(self, balance_in_cogs):
        self._balance_in_cogs = Decimal(self._balance_in_cogs) - Decimal(balance_in_cogs)

class AGIXSnapshotGenerator():
    def __init__(self):
        self._repository = Repository()
        self._select_transfers = 'select * from agix_transfers where block_number <= %s limit 1000 offset %s' 
        self._select_contracts = 'select wallet_address from agix_balances where is_contract = 1'
        self._contracts = []
        self._addresses = {}
               
    def _get_address_object(self, address):
        if address in self._addresses:
            object = self._addresses[address]
        else:
            is_contract = 0
            if address in self._contracts:
                is_contract = 1
            object = AGIXToken(address,is_contract)
            self._addresses[address] = object
        return object

    def _dump_balances(self, block_number):
        with open('AGIXTokenBalances_' + str(block_number) + "_"+ time.strftime("%Y%m%d-%H%M%S") + '.csv', mode='w', newline='') as balances:
            balances_file = csv.writer(balances, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            balances_file.writerow(["Address", "Is Contract", "Balance in AGI", "Balance in Cogs"])
            for address in self._addresses:
                object = self._addresses[address]
                balances_file.writerow([object._address, object._is_contract, Decimal(object._balance_in_cogs/100000000), object._balance_in_cogs])

    def generate_snapshot(self, block_number):
        if block_number is None:
            blockchain_util = BlockChainUtil(INFURA_URL_HTTPS, None)
            block_number = blockchain_util.get_current_block_no()
        offset = 0
        result = self._repository.execute(self._select_contracts)
        self._contracts = list(map(lambda x: x['wallet_address'], result))

        while True:
            transfers = self._repository.execute(self._select_transfers, [block_number, offset])
            if len(transfers) == 0:
                break

            for row in transfers:
                from_address = row['from_address']
                to_address = row['to_address']
                amount_in_cogs = row['amount_in_cogs']

                from_object = self._get_address_object(from_address)
                to_object = self._get_address_object(to_address)

                from_object.remove_cogs(amount_in_cogs)
                to_object.add_cogs(amount_in_cogs)
            print(f"Completed {offset} transfers")
            offset += 1000
           
        self._dump_balances(block_number)
        

tp = AGIXSnapshotGenerator()
tp.generate_snapshot(None)