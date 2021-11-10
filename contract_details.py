import os

DETAILS = {
    "AGIX_TRANSFER": {
        "contract_file_name": "SingularityNetToken.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "singularitynet-token-contracts")),
        "balances_table_name":"agix_balances", 
        "transfers_table_name":"agix_transfers", 
        "amount_key":"value"
    },
    "AGIX_STAKE1": {
        "contract_file_name": "TokenStake.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "singularitynet-stake-contracts")),
        "table_name": "agix_balances",
        "stake_type": "DEFAULT_STAKE",
        "window_reward_amount_index": 7
    },
    "AGIX_LPWETH": {
        "contract_file_name": "AGIXWETHPair.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "uniswap-v2")),
        "balances_table_name":"agix_balances",
        "token_details":"AGIX_TRANSFER",
        "yield_farming_token": "SDAO_STAKE3",
        "pool_index":2
    },
    "AGIX_LPUSDT": {
        "contract_file_name": "AGIXUSDTPair.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "uniswap-v2")),
        "balances_table_name":"agix_balances",
        "token_details":"AGIX_TRANSFER",
        "yield_farming_token": "SDAO_STAKE3",
        "pool_index":4
    },
    "SDAO_TRANSFER": {
        "contract_file_name": "SDAOToken.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "singularitydao-token-contracts")),
        "balances_table_name":"sdao_balances", 
        "transfers_table_name":"sdao_transfers", 
        "amount_key":"amount"
    },
    "SDAO_LPWETH": {
        "contract_file_name": "SDAOWETHPair.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "uniswap-v2")),
        "balances_table_name":"sdao_balances",
        "token_details":"SDAO_TRANSFER",
        "yield_farming_token": "SDAO_STAKE3",
        "pool_index":1
    },
    "SDAO_LPUSDT": {
        "contract_file_name": "SDAOUSDTPair.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "uniswap-v2")),
        "balances_table_name":"sdao_balances",
        "token_details":"SDAO_TRANSFER",
        "yield_farming_token": "SDAO_STAKE3",
        "pool_index":3
    },
    "SDAO_STAKE1": {
        "contract_file_name": "SDAOBondedTokenStake.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "@singularitydao","v1-farming-contracts")),
        "table_name": "sdao_balances",
        "stake_type": "3_MONTH_EPOCH",
        "window_reward_amount_index": 4    
    },
    "SDAO_STAKE2": {
        "contract_file_name": "SDAOBonded6MonthTokenStake.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "@singularitydao","v1-farming-contracts")),
        "table_name": "sdao_balances",
        "stake_type": "6_MONTH_EPOCH",
        "window_reward_amount_index": 4
    },
    "SDAO_STAKE3": {
        "contract_file_name": "SDAOTokenStaking.json",
        "contract_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "node_modules", "@singularitydao","v1-farming-contracts")),
        "table_name": "sdao_balances",
        "stake_type": "UNBONDED_STAKE",
        "window_reward_amount_index": -1
    }    
}
