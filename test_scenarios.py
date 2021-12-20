
from lambda_handler import lambda_handler


payload1 = {"token": "AGIX","type": "BALANCE"}
payload2 = {"token": "AGIX1","type": "BALANCE"}

payload3 = {"token1": "AGIX","type1": "TRANSFER"}
payload4 = {"token": "AGIX","type1": "STAKE1"}
payload5 = {"token1": "AGIX","type": "STAKE1"}

payload6 = {"token": "SDAO","type": "TRANSFER"}
payload7 = {"token": "SDAO","type": "STAKE1"}

payload8 = {"token": "AGIX","type": "TRANSFER"}
payload9 = {"token": "AGIX","type": "STAKE1"}

payload10 = {"token": "SDAO","type": "STAKE2"}
payload11 = {"token": "SDAO","type": "STAKE3"}

payload12 = {"token": "AGIX","type": "LPWETH"}
payload13 = {"token": "AGIX","type": "LPUSDT"}

payload14 = {"token": "SDAO","type": "LPWETH"}
payload15 = {"token": "SDAO","type": "LPUSDT"}

#print(lambda_handler(payload1, None))
#print(lambda_handler(payload2, None))
#print(lambda_handler(payload3, None))
#print(lambda_handler(payload4, None))
#print(lambda_handler(payload5, None))

#print(lambda_handler(payload8, None))
#print(lambda_handler(payload9, None))
#print(lambda_handler(payload12, None))
#print(lambda_handler(payload13, None))

#print(lambda_handler(payload6, None))
#print(lambda_handler(payload7, None))
#print(lambda_handler(payload10, None))
#print(lambda_handler(payload11, None))

#print(lambda_handler(payload14, None))
#print(lambda_handler(payload15, None))

from config import INFURA_URL_HTTPS, NET_ID
from repository import Repository
from staking_handler import StakingHandler

s = StakingHandler(INFURA_URL_HTTPS, NET_ID, 'AGIX_STAKE1', Repository())
s.process()
#u = UniswapV2TransfersHandler(INFURA_URL_HTTPS, NET_ID, 'AGIX_LPWETH', Repository())
#u.test_address()