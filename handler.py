import json
import querystring
from twilio.rest import Client
import os
import boto3
import urllib2
import base64
import collections
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def incoming_text(event, context):
    #print event
    twilioSMS = querystring.parse_qs(event['body-json'])
    print twilioSMS
    logger.debug('text recieved={}'.format(twilioSMS))
    body = {
        "message": twilioSMS['From'],
        "input": event
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    message = {}
    message['From'] = twilioSMS['From'].replace('+','')
    message['sessionAttributes'] = {}
    message['requestAttributes'] = {}
    if twilioSMS['Body']:
      if 'MediaUrl0' in twilioSMS:
        text_and_media(twilioSMS)
      else:
        #just_text(twilioSMS)
        message['Body'] = twilioSMS['Body']
    else:
      if 'MediaUrl0' in twilioSMS:
        print 'just media'
        #just_media(twilioSMS)
        message['Body'] = 'Are there any offers?'
        model_sku = extract_model_sku(rekognize_text(twilioSMS['MediaUrl0']))
        print 'request'
        print model_sku
        message['sessionAttributes'].update(model_sku)
        print message
    #return response
    response = post_to_lex(message)
    #print response
    message['Body'] = response['message']
    return_text(message)

def text_and_media(message):
    return_text(message)
    message['Body'] = message['MediaUrl0']
    print rekognize_text(message['MediaUrl0'])
    return_text(message)

def just_text(message):
    print boto3.__version__
    return_text(message)

def just_media(message):
    message['Body'] = message['MediaUrl0']
    #print process_text(message['MediaUrl0'])
    #hack remove later
    message['Body'] = json.dumps(rekognize_text(message['MediaUrl0']))
    return_text(message)

def rekognize_text(media_url):
    rek_client = boto3.client('rekognition')
    req = urllib2.Request(media_url, headers=hdr)
    try:
      image = urllib2.urlopen(req)
    except urlib2.HTTPError, e:
      print e.fp.read()

    contents = image.read()
    img_dict = {}
    img_dict['Bytes'] = contents
    logger.debug('Sending to rekognition')
    response = rek_client.detect_text(Image=img_dict)
    return response

def extract_model_sku(response):
    logger.debug('Extracting text')
    extraction = {}
    extraction_list = []
    extracted_info = {}
    #Model:4888B001 SKU:2944549 Color:Black
    for text in response['TextDetections']:
        if ('Model' in text['DetectedText']) and ('SKU' in text['DetectedText']):
            extraction_list.append(text['DetectedText'])
        if ('Model' in text['DetectedText']) or ('SKU' in text['DetectedText']):
            extraction_list.append(text['DetectedText'])

    for item in extraction_list:
        if ('Model' in item) or ('SKU' in item):
            temp_list = item.split(' ')
            for temp_item in temp_list:
                if ('Model' in temp_item) or ('SKU' in temp_item):
                    #print temp_item
                    k,v = temp_item.split(':')
                    extracted_info[k] = v
    return extracted_info
def return_text(message):
    client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    client.api.account.messages.create(
      to=message['From'],
      from_="+14692423119",
      body=message['Body']
    )

def post_to_lex(message):
  logger.debug('posting to lex'.format(message))
  #print message
  lex_client = boto3.client('lex-runtime')
  response = lex_client.post_text(
    botName=os.environ['BOT_NAME'],
    botAlias=os.environ['BOT_ALIAS'],
    userId=message['From'],
    sessionAttributes=message['sessionAttributes'],
    requestAttributes=message['requestAttributes'],
    inputText=message['Body']
  )
  return response
