import os

from staking_handler import StakingHandler

class SDAOStakingHandler():
    def __init__(self, ws_provider, net_id):
        self._staking_handler = StakingHandler(ws_provider, net_id, "SDAOBondedTokenStake.json", "sdao_balances","30_DAY_EPOCH")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', '@singularitydao','v1-farming-contracts'))
        self._staking_handler.set_base_contract_path(base_contract_path)

    def process_stake(self):
        self._staking_handler.process_stake()


