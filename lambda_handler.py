import json
import traceback

from config import INFURA_URL_HTTPS, NET_ID, INFURA_URL_HTTPS_1
from repository import Repository
from transfers_handler import TransfersHandler
from staking_handler import StakingHandler, UnBondedStakingHandler
from uniswap_event_handler import UniswapV2TransfersHandler

processor_map = {
    'AGIX': {'TRANSFER': TransfersHandler, 'LPWETH':UniswapV2TransfersHandler, 'LPUSDT':UniswapV2TransfersHandler, 'STAKE1': StakingHandler},
    'SDAO': {'TRANSFER': TransfersHandler, 'LPWETH':UniswapV2TransfersHandler, 'LPUSDT':UniswapV2TransfersHandler, 'STAKE1': StakingHandler, 
            'STAKE2': StakingHandler, 'STAKE3' : UnBondedStakingHandler}
}

def response(status, message):
    return {
        'statusCode': status,
        'body': json.dumps(message)
    }

def lambda_handler(event, context):
    if 'token' not in event or 'type' not in event:
        return response(500,"Invalid payload provided " + str(event))
    
    token = event['token']
    type = event['type']
    transfer_type= token + "_" + type

    if token not in processor_map and type not in processor_map[token]:
        return response(500,"Unknown token or type - " + str(event))

    status_code = 200
    message = 'Success'
    repository = Repository()
    insert_job_status = 'INSERT INTO job_runs ' + \
        '(name, end_block_number, context, row_created, row_updated) ' + \
        'VALUES (%s, %s, %s, current_timestamp, current_timestamp) '    
    tp = None
    try:
        infura_url=INFURA_URL_HTTPS
        if token == 'AGIX':
            infura_url = INFURA_URL_HTTPS_1        
        tp = processor_map[token][type](infura_url, NET_ID, transfer_type, repository)
        tp.process()
    except Exception as e:
        traceback.print_exc()
        status_code = 500
        message = repr(e)
        print(message)

    if tp is not None:
        tp._repository.execute(insert_job_status, [str(token + "_" + type), 0, message])
    event['message'] = message
    return response(status_code, event)

