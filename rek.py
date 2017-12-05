import json
import querystring
import os
import boto3
import urllib2
import base64
import collections

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

client = boto3.client('rekognition')
#media_url = 'https://api.twilio.com/2010-04-01/Accounts/AC48c08d5fbec733189523e7f9f289aacd/Messages/MMc0830a55e90a4a470605385c857b7a08/Media/ME39f23de47f4cbf06aa9d421eec306cf0'
#media_url = 'https://upload.wikimedia.org/wikipedia/commons/5/5f/Dr._Jekyll_and_Mr._Hyde_Text.jpg'
#media_url = 'https://s3.amazonaws.com/fcandela-ward/20171130_184820.jpg'
#media_url = 'https://api.twilio.com/2010-04-01/Accounts/AC48c08d5fbec733189523e7f9f289aacd/Messages/MM3b998e17c8d3532c0cefb4950c7c3da1/Media/ME3fd80b3d31141f3e4308d09d32ccdaa4'
media_url = 'https://s3-external-1.amazonaws.com/media.twiliocdn.com/AC48c08d5fbec733189523e7f9f289aacd/ad8c0d975e72fc4a8214b9bbdc4897bd'
#media_url = 'https://s3-external-1.amazonaws.com/media.twiliocdn.com/AC48c08d5fbec733189523e7f9f289aacd/fcae888aecf96ba4bff9f1c3b1efe8a6'
req = urllib2.Request(media_url, headers=hdr)
try:
  image = urllib2.urlopen(req)
except urlib2.HTTPError, e:
  print e.fp.read()

contents = image.read()
data = base64.encodestring(contents)
img_dict = {}
img_dict['Bytes'] = contents
response = client.detect_text(Image=img_dict)

def extract_model_sku(response):

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

print extract_model_sku(response)
