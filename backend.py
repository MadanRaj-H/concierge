"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages reservations for hotel rooms and car rentals.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'BookTrip' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""

import json
import datetime
import time
import os
import dateutil.parser
import logging
import requests
baseURL = 'https://api.bestbuy.com/v1/products'
apiKey = os.environ['BEST_BUY_API_KEY']

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- External API code ---

def search_best_buy(sku, model):
  found_item = search_sku(sku)
  if found_item:
    return found_item
  else:
    return search_model(model)

def search_sku(sku):
  url = baseURL + '(sku={})'.format(sku) + '?apiKey={}'.format(apiKey) + '&format=json'
  request = requests.get(url)
  response_object = json.loads(request.content)
  if 'products' in response_object.keys():
    if response_object['products']:
      return response_object['products'][0]['name']

def search_model(model):
  url = baseURL + '(modelNumber={})'.format(model) + '?apiKey={}'.format(apiKey) + '&format=json'
  request = requests.get(url)
  response_object = json.loads(request.content)
  if 'products' in response_object.keys():
    if response_object['products']:
      return response_object['products'][0]['name']

# --- Helpers that build all of the responses ---

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


def isvalid_Model(Model):
  product_name = search_model(Model)
  if product_name is not None:
    return True

def isvalid_SKU(SKU):
  product_name = search_sku(SKU)
  if product_name is not None:
    return True


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate_item(slots):
    Model = try_ex(lambda: slots['Model'])
    SKU = try_ex(lambda: slots['SKU'])

    if Model and not isvalid_Model(Model):
        return build_validation_result(
            False,
            'Model',
            'This {} is not a valid model number.  Can you try a different model number?'.format(Model)
        )

    if SKU and not isvalid_SKU(SKU):
        return build_validation_result(
            False,
            'SKU',
            'This {} is not a valid SKU.  Can you try a different SKU?'.format(SKU)
        )
    return {'isValid': True}

""" --- Functions that control the bot's behavior --- """

def check_offer(intent_request):
    print intent_request

    Model = try_ex(lambda: intent_request['currentIntent']['slots']['Model'])
    SKU = try_ex(lambda: intent_request['currentIntent']['slots']['SKU'])
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    print 'session after assign'
    print session_attributes

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_item(intent_request['currentIntent']['slots'])
        print 'validation results'
        print validation_result
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
        if ('Model' in session_attributes.keys()) or ('SKU' in session_attributes.keys()):
          print 'setting current intents to session attributes'
          intent_request['currentIntent']['slots'] = session_attributes
          print 'current slots'
          print intent_request['currentIntent']['slots']
          return close(
            session_attributes,
            'Fulfilled',
            {
              'contentType': 'PlainText',
              'content': 'Pay no interest for 6 months when you purchase a {} with a My Best Buy Credit Card! Reply with the phrase call me if you want to apply!'.format(search_best_buy(session_attributes['SKU'], session_attributes['Model'])) 
            }
          )
        return delegate(session_attributes, intent_request['currentIntent']['slots'])
    print 'intent_request'
    print intent_request

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Pay no interest for 6 months when you purchase a {} with a My Best Buy Credit Card! Reply with the phrase call me if you want to apply!'.format(search_best_buy(intent_request['currentIntent']['slots']['SKU'], intent_request['currentIntent']['slots']['Model']))
        }
    )

# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'BookHotel':
        return book_hotel(intent_request)
    elif intent_name == 'BookCar':
        return book_car(intent_request)
    elif intent_name == 'check_offer':
        return check_offer(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
