
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

#print(lambda_handler(payload1, None))
#print(lambda_handler(payload2, None))
#print(lambda_handler(payload3, None))
#print(lambda_handler(payload4, None))
#print(lambda_handler(payload5, None))

#print(lambda_handler(payload8, None))
#print(lambda_handler(payload9, None))

print(lambda_handler(payload11, None))
#print(lambda_handler(payload10, None))