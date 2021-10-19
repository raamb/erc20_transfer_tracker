import os
from staking_handler import StakingHandler

class AGIXStakingHandler():
    def __init__(self, ws_provider, net_id):
        self._staking_handler = StakingHandler(ws_provider, net_id, "TokenStake.json", "agix_balances","DEFAULT_STAKE")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', 'singularitynet-stake-contracts'))
        self._staking_handler.set_base_contract_path(base_contract_path)        
   
    def process_stake(self):
        self._staking_handler.process_stake()