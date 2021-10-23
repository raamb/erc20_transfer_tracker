# erc20_transfer_tracker
Track all transfers for a given ERC20 token

# Set up

npm i singularitynet-token-contracts
npm i singularitynet-stake-contracts

npm i singularitydao-token-contracts
npm i @singularitydao/v1-farming-contracts

cp ./SDAOBonded6MonthTokenStake.json ./node_modules/@singularitydao/v1-farming-contracts/networks/
cp ./node_modules/@singularitydao/v1-farming-contracts/abi/SDAOBondedTokenStake.json ./node_modules/@singularitydao/v1-farming-contracts/abi/SDAOBonded6MonthTokenStake.json

pip install -r requirements.txt

cp -r uniswap-v2 ./node_modules/