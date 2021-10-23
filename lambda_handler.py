import json
import traceback

from config import INFURA_URL_HTTPS, NET_ID
from agix_staking_processor import AGIXStakingHandler
from sdao_staking_processor import SDAOStakingHandler, SDAO6MonthStakingHandler, SDAOUnbondedStakingHandler
from agix_transfers_processor import AGIXTransfersProcessor
from sdao_transfers_processor import SDAOTransfersProcessor
from lp_processor import AGIXUSDTLPProcessor, AGIXWETHLPProcessor, SDAOUSDTLPProcessor, SDAOWETHLPProcessor

processor_map = {
    'AGIX': {'TRANSFER': AGIXTransfersProcessor, 'LPWETH':AGIXWETHLPProcessor, 'LPUSDT':AGIXUSDTLPProcessor, 'STAKE1': AGIXStakingHandler},
    'SDAO': {'TRANSFER': SDAOTransfersProcessor, 'LPWETH':SDAOWETHLPProcessor, 'LPUSDT':SDAOUSDTLPProcessor, 'STAKE1': SDAOStakingHandler, 
            'STAKE2': SDAO6MonthStakingHandler, 'STAKE3' : SDAOUnbondedStakingHandler}
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

    if token not in processor_map or type not in processor_map[token]:
        return response(500,"Unknown token or type - " + str(event))

    status_code = 200
    message = 'Success'
    insert_job_status = 'INSERT INTO job_status ' + \
        '(name, end_block_number, context, row_created, row_updated) ' + \
        'VALUES (%s, %s, %s, current_timestamp, current_timestamp) '    
    tp = None
    try:
        tp = processor_map[token][type](INFURA_URL_HTTPS, NET_ID)
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

