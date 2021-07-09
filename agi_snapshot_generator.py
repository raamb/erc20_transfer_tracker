import time
import csv
from decimal import Decimal

from repository import Repository
from blockchain_util import BlockChainUtil
from config import INFURA_URL_HTTPS

class AGIToken():
    def __init__(self, address):
        self._address = address
        self._balance_in_cogs = Decimal(0)
    
    def add_cogs(self, balance_in_cogs):
        self._balance_in_cogs = Decimal(self._balance_in_cogs) + Decimal(balance_in_cogs)
    
    def remove_cogs(self, balance_in_cogs):
        self._balance_in_cogs = Decimal(self._balance_in_cogs) - Decimal(balance_in_cogs)

class AGISnapshotGenerator():
    def __init__(self):
        self._repository = Repository()
        self._select_transfers = 'select * from all_agi_transfers where block_number <= %s limit 1000 offset %s' 
        self._addresses = {}
               
    def _get_address_object(self, address):
        if address in self._addresses:
            object = self._addresses[address]
        else:
            object = AGIToken(address)
            self._addresses[address] = object
        return object

    def _dump_balances(self, block_number):
        with open('AGITokenBalances_' + str(block_number) + "_"+ time.strftime("%Y%m%d-%H%M%S") + '.csv', mode='w', newline='') as balances:
            balances_file = csv.writer(balances, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            balances_file.writerow(["Address", "Balance in AGI", "Balance in Cogs"])
            for address in self._addresses:
                object = self._addresses[address]
                balances_file.writerow([object._address, Decimal(object._balance_in_cogs/100000000), object._balance_in_cogs])

    def generate_snapshot(self, block_number):
        if block_number is None:
            blockchain_util = BlockChainUtil(INFURA_URL_HTTPS, None)
            block_number = blockchain_util.get_current_block_no()
        offset = 0

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
        

tp = AGISnapshotGenerator()
#tp.generate_snapshot(12260705)
tp.generate_snapshot(12434110)