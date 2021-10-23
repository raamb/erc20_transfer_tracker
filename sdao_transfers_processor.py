import os

from transfers_handler import TransfersHandler

class SDAOTransfersProcessor():
    def __init__(self, ws_provider, net_id):
        self._transfers_handler = TransfersHandler(ws_provider, net_id, "SDAOToken.json", "sdao_balances","sdao_transfers","amount")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', 'singularitydao-token-contracts'))
        self._transfers_handler.set_base_contract_path(base_contract_path)
    
    def process(self):
        self._transfers_handler.read_events()