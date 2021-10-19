import json

from config import INFURA_URL_HTTPS, NET_ID
from agix_staking_processor import AGIXStakingHandler
from sdao_staking_processor import SDAOStakingHandler
from agix_transfers_processor import AGIXTransfersProcessor
from sdao_transfers_processor import SDAOTransfersProcessor

processor_map = {
    'AGIX': {'TRANSFER': AGIXTransfersProcessor, 'STAKE': AGIXStakingHandler},
    'SDAO': {'TRANSFER': SDAOTransfersProcessor, 'STAKE': SDAOStakingHandler}
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
    try:
        tp = processor_map[token][type](INFURA_URL_HTTPS, NET_ID)
        if type == 'TRANSFER':        
            tp.read_events()
        else:
            tp.process_stake()
    except Exception as e:
        status_code = 500
        message = repr(e)
        print(message)

    event['message'] = message
    return response(status_code, event)

