# Balances Tracker
Track 
* Wallet Balances
* Staked tokens
* Liquidity Provisioning
for all SNet family of tokens. Currently tracks for AGIX and SDAO

# Staking Events
## Bonded Staking (SDAO and AGIX)
** SubmitStake - Emitted when user stakes
** RequestForClaim - Emitted when user opts out or opts in to the next stake window
** ClaimStake - Emitted when user claims
** AddReward - Emitted when rewards are compuited in each window
** WithdrawStake - Emitted when user withdraws before window closes

# Set up

npm i singularitynet-token-contracts
npm i singularitynet-stake-contracts

npm i singularitydao-token-contracts
npm i @singularitydao/v1-farming-contracts

cp ./SDAOBonded6MonthTokenStake.json ./node_modules/@singularitydao/v1-farming-contracts/networks/
cp ./node_modules/@singularitydao/v1-farming-contracts/abi/SDAOBondedTokenStake.json ./node_modules/@singularitydao/v1-farming-contracts/abi/SDAOBonded6MonthTokenStake.json

pip install -r requirements.txt

cp -r setup/uniswap-v2 ./node_modules/

Execute the SQLs in the setup folder on your DB