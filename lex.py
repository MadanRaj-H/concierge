import boto3
import json
import sys
from botocore.exceptions import ClientError
#boto3.set_stream_logger(name='botocore')

def post_to_lex(botName, botAlias, userId, inputText):
  lex_client = boto3.client('lex-runtime', region_name='us-east-1')
  try:
    response = lex_client.post_text(
      botName=botName,
      botAlias=botAlias,
      userId=userId,
      inputText=inputText
    )
  except ClientError as e:
    print e
  return response

response = post_to_lex('Boxey_Credit', 'prod', '123456789', sys.argv[1])
print json.dumps(response, indent=4, sort_keys=True)
