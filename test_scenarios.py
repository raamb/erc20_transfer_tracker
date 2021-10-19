
from lambda_handler import lambda_handler


payload1 = {"token": "AGIX","type": "BALANCE"}
payload2 = {"token": "AGIX1","type": "BALANCE"}

payload3 = {"token1": "AGIX","type1": "TRANSFER"}
payload4 = {"token": "AGIX","type1": "STAKE"}
payload5 = {"token1": "AGIX","type": "STAKE"}

payload6 = {"token": "SDAO","type": "TRANSFER"}
payload7 = {"token": "SDAO","type": "STAKE"}

payload8 = {"token": "AGIX","type": "TRANSFER"}
payload9 = {"token": "AGIX","type": "STAKE"}


#print(lambda_handler(payload1, None))
#print(lambda_handler(payload2, None))
#print(lambda_handler(payload3, None))
#print(lambda_handler(payload4, None))
#print(lambda_handler(payload5, None))

#print(lambda_handler(payload8, None))
#print(lambda_handler(payload9, None))

#print(lambda_handler(payload6, None))
print(lambda_handler(payload7, None))