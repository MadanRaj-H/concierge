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

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


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

""" --- Functions that control the bot's behavior --- """

def learn_more(intent_request):
    print intent_request
    session_attributes = {}
    if try_ex(lambda: intent_request['invocationSource'] == 'FulfillmentCodeHook'):
      session_attributes = intent_request['currentIntent']['slots'] 
      if intent_request['currentIntent']['slots']['slotOne'] == 'Visa':
        message = 'On top of 5% back at Boxey and special FINANCING offers, you can earn 3% back on gas, 2% on dining and 1% everywhere else! Would you like to APPLY NOW and LEARN MORE?' 
        return close(
          session_attributes, 
          'Fulfilled', 
          {
            'contentType': 'PlainText',
            'content': message
          }
          )
      if intent_request['currentIntent']['slots']['slotOne'] == 'Credit':
        message = '"With Boxey Credit, you can earn 5% back on purchases at Boxey or get special FINANCING options! Would you like to APPLY NOW and LEARN MORE?"'
        return close(
          session_attributes, 
          'Fulfilled', 
          {
            'contentType': 'PlainText',
            'content': message
          }
          )
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hello! I can help you learn more about Boxey credit. Try texting me an image of a pricetag/SKU or ask to LEARN MORE. You can also ask me to STOP at any time'
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
    if intent_name == 'Learn_More':
        return learn_more(intent_request)
    else:
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
