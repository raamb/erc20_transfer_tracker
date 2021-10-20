import os

from staking_handler import StakingHandler, UnBondedStakingHandler

class SDAOStakingHandler():
    def __init__(self, ws_provider, net_id):
        self._staking_handler = StakingHandler(ws_provider, net_id, "SDAOBondedTokenStake.json", "sdao_balances","3_MONTH_EPOCH")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', '@singularitydao','v1-farming-contracts'))
        self._staking_handler.set_base_contract_path(base_contract_path)

    def process_stake(self):
        self._staking_handler.process_stake()

class SDAO6MonthStakingHandler():
    def __init__(self, ws_provider, net_id):
        self._staking_handler = StakingHandler(ws_provider, net_id, "SDAOBonded6MonthTokenStake.json", "sdao_balances","6_MONTH_EPOCH")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', '@singularitydao','v1-farming-contracts'))
        self._staking_handler.set_base_contract_path(base_contract_path)

    def process_stake(self):
        self._staking_handler.process_stake()

class SDAOUnbondedStakingHandler():
    def __init__(self, ws_provider, net_id):
        self._staking_handler = UnBondedStakingHandler(ws_provider, net_id, "SDAOTokenStaking.json", "sdao_balances","UNBONDED_STAKE")
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'node_modules', '@singularitydao','v1-farming-contracts'))
        self._staking_handler.set_base_contract_path(base_contract_path)

    def process_stake(self):
        self._staking_handler.process_stake()


