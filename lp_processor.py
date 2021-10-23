import os
from erc20_transfer_handler import ERC20TokenHandler

from uniswap_event_handler import UniswapV2TransfersHandler

def get_token_handler(ws_provider, net_id, token_json, token_contract_folder):
    base_contract_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'node_modules', token_contract_folder))
    return ERC20TokenHandler(ws_provider, net_id, token_json, base_contract_path)

class SDAOWETHLPProcessor():
    def __init__(self, ws_provider, net_id):
        sdao_handler = get_token_handler(ws_provider, net_id,"SDAOToken.json","singularitydao-token-contracts")
        self._transfers_handler = UniswapV2TransfersHandler(ws_provider, net_id, "SDAOWETHPair.json", "sdao_balances")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', 'uniswap-v2'))
        self._transfers_handler.set_base_contract_path(base_contract_path)
        self._transfers_handler.set_token_handler(sdao_handler)
    
    def process(self):
        self._transfers_handler.read_events()

class SDAOUSDTLPProcessor():
    def __init__(self, ws_provider, net_id):
        sdao_handler = get_token_handler(ws_provider, net_id,"SDAOToken.json","singularitydao-token-contracts")
        self._transfers_handler = UniswapV2TransfersHandler(ws_provider, net_id, "SDAOUSDTPair.json", "sdao_balances")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', 'uniswap-v2'))
        self._transfers_handler.set_base_contract_path(base_contract_path)
        self._transfers_handler.set_token_handler(sdao_handler)
    
    def process(self):
        self._transfers_handler.read_events()

class AGIXWETHLPProcessor():
    def __init__(self, ws_provider, net_id):
        agix_handler = get_token_handler(ws_provider, net_id,"SingularityNetToken.json","singularitynet-token-contracts")
        self._transfers_handler = UniswapV2TransfersHandler(ws_provider, net_id, "AGIXWETHPair.json", "agix_balances")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', 'uniswap-v2'))
        self._transfers_handler.set_base_contract_path(base_contract_path)
        self._transfers_handler.set_token_handler(agix_handler)
    
    def process(self):
        self._transfers_handler.read_events()

class AGIXUSDTLPProcessor():
    def __init__(self, ws_provider, net_id):
        agix_handler = get_token_handler(ws_provider, net_id,"SingularityNetToken.json","singularitynet-token-contracts")
        self._transfers_handler = UniswapV2TransfersHandler(ws_provider, net_id, "AGIXUSDTPair.json", "agix_balances")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', 'uniswap-v2'))
        self._transfers_handler.set_base_contract_path(base_contract_path)
        self._transfers_handler.set_token_handler(agix_handler)
    
    def process(self):
        self._transfers_handler.read_events()
