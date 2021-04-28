#!/usr/bin/env python
#  -*- coding: utf-8 -*-


# Use future for Python v2 and v3 compatibility
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from builtins import *
import atexit
import pymongo
from flask import Flask, request
import requests, sys
from webexteamssdk import WebexTeamsAPI, Webhook
import concurrent.futures
if sys.version_info[0] < 3:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin
import card_data




client = pymongo.MongoClient("mongodb://scozma:S3rban1121@ds057548.mlab.com:57548/cisco", retryWrites=False)
db = client.cisco


# Module constants
WEBHOOK_NAME = "botWithCardExampleWebhook"
WEBHOOK_URL_SUFFIX = "/events"
MESSAGE_WEBHOOK_RESOURCE = "messages"
MESSAGE_WEBHOOK_EVENT = "created"
CARDS_WEBHOOK_RESOURCE = "attachmentActions"
CARDS_WEBHOOK_EVENT = "created"
# DEMO_PEOPLE = ["scozma@cisco.com"]
DEMO_PEOPLE = ['scozma@cisco.com', 'asummera@cisco.com', 'elandman@cisco.com', 'egresser@cisco.com', 'lfromman@cisco.com', 'mickober@cisco.com', 'ncervign@cisco.com', 'ramhadda@cisco.com', 'rocicek@cisco.com', 'spensott@cisco.com']
# DEMO_PEOPLE = ['scozma@cisco.com'] * 500
# DEMO_PEOPLE = ["clehance@cisco.com", "ctone@cisco.com", "adonoiu@cisco.com", "agolosoi@cisco.com", "avoicu@cisco.com", "simbogda@cisco.com", "camarica@cisco.com", "crstefan@cisco.com", "dcapsuna@cisco.com", "dcruceru@cisco.com", "dopena@cisco.com", "igradina@cisco.com", "lsavu@cisco.com", "mirumari@cisco.com", "oneghina@cisco.com", "pmaravei@cisco.com", "rcarlan@cisco.com", "rsacuiu@cisco.com", "razatima@cisco.com", "sivultur@cisco.com", "vladiun3@cisco.com", "mihdinca@cisco.com", "scozma@cisco.com", "adaron@cisco.com", "alidavid@cisco.com", "gboulesc@cisco.com", "imanea@cisco.com", "lspirido@cisco.com", "ltudorac@cisco.com", "tmoldove@cisco.com", "vbiriste@cisco.com"]
# Initialize the environment
# Create the web application instance
flask_app = Flask(__name__)
# Create the Webex Teams API connection object
api = WebexTeamsAPI()

def respond_to_button_press(webhook):
    """Respond to a button press on the card we posted"""

    # Some server side debugging
    room = api.rooms.get(webhook.data.roomId)
    attachment_action = api.attachment_actions.get(webhook.data.id)
    person = api.people.get(attachment_action.personId)
    message_id = attachment_action.messageId
    print(
        f"""
        NEW BUTTON PRESS IN ROOM '{room.title}'
        FROM '{person.displayName}'
        """
    )

    comment = None
    if '1' in str(attachment_action.inputs):
        comment = api.messages.create(
        room.id,
        parentId=message_id,
        text="Imi pare rau 😖! Data viitoare sper sa fie mai bine!"
    )
    elif '2' in str(attachment_action.inputs):
        comment = api.messages.create(
        room.id,
        parentId=message_id,
        text="Imi pare rau 😖! Data viitoare sper sa fie mai bine!"
    )
    elif '3' in str(attachment_action.inputs):
        comment = api.messages.create(
        room.id,
        parentId=message_id,
        text="Imi pare rau 😖! Data viitoare sper sa fie mai bine!"
        )
    else:
        comment = api.messages.create(
            room.id,
            parentId=message_id,
            text="Multumesc frumos! 😎"
        )

    db.connect_feedback.insert( { "name" : person.displayName , "rate" : attachment_action.inputs  } )
    time.sleep(5)
    api.messages.delete(comment.to_dict()['id'])
    api.messages.delete(message_id)

def respond_to_message(webhook):
    """Respond to a message to our bot"""

    # Some server side debugging
    room = api.rooms.get(webhook.data.roomId)
    message = api.messages.get(webhook.data.id)
    person = api.people.get(message.personId)
    if person.emails[0] in DEMO_PEOPLE:
        print(
            f"""
            NEW MESSAGE IN ROOM '{room.title}'
            FROM '{person.displayName}'
            MESSAGE '{message.text}'
            """
        )

        # This is a VERY IMPORTANT loop prevention control step.
        # If you respond to all messages...  You will respond to the messages
        # that the bot posts and thereby create a loop condition.
        me = api.people.me()
        if message.personId == me.id:
            # Message was sent by me (bot); do not respond.
            return "OK"

        else:
            # Message was sent by someone else; parse message and respond.
            if "/stop" in message.text:
                print(person)
                api.messages.create(
                room.id,
                text="OK! Distracție plăcuta!",
                )
                DEMO_PEOPLE.remove(person.emails[0])
            elif "/help" in message.text:
                print(person)
                api.messages.create(
                room.id,
                text="Dacă vrei sa nu mai vorbim scrie /stop. Vorbește cu scozma@cisco.com pentru feedback!",
                )
            else:
                api.messages.create(
                room.id,
                text="Salutare!\nBine ai venit la 🇷🇴 Cisco Connect 2020 🇷🇴.\nEu sunt asistentul tău pe durata acestui eveniment. Scopul meu este sa te informez de inceperea evenimentelor și sa iți cer un mic feedback.\nDacă nu ai nevoie de mine scrie /stop și dacă vrei ajutor scrie /help.")
            return "OK"
    return "Intruder"

@flask_app.route("/events", methods=["POST"])
def webex_teams_webhook_events():
    """Respond to inbound webhook JSON HTTP POST from Webex Teams."""
    # Create a Webhook object from the JSON data
    webhook_obj = Webhook(request.json)

    # Handle a new message event
    if (webhook_obj.resource == MESSAGE_WEBHOOK_RESOURCE
            and webhook_obj.event == MESSAGE_WEBHOOK_EVENT):
        respond_to_message(webhook_obj)

    # Handle an Action.Submit button press event
    elif (webhook_obj.resource == CARDS_WEBHOOK_RESOURCE
          and webhook_obj.event == CARDS_WEBHOOK_EVENT):
        respond_to_button_press(webhook_obj)

    # Ignore anything else (which should never happen
    else:
        print(f"IGNORING UNEXPECTED WEBHOOK:\n{webhook_obj}")

    return "OK"

def create_ngrok_webhook(api):
    """Create a Webex Teams webhook pointing to the public ngrok URL."""
    print("Creating Webhook...")
    webhook = api.webhooks.create(
        name=WEBHOOK_NAME,
        targetUrl=urljoin("http://2c6c98cfa9a2.ngrok.io", WEBHOOK_URL_SUFFIX),
        resource=MESSAGE_WEBHOOK_RESOURCE,
        event=MESSAGE_WEBHOOK_EVENT,
    )
    print(webhook)
    print("Webhook successfully created.")
    
    print("Creating Attachment Actions Webhook...")
    webhook = api.webhooks.create(
        resource=CARDS_WEBHOOK_RESOURCE,
        event=CARDS_WEBHOOK_EVENT,
        name=WEBHOOK_NAME,
        targetUrl=urljoin("http://2c6c98cfa9a2.ngrok.io", WEBHOOK_URL_SUFFIX)
    )
    print(webhook)
    print("Webhook successfully created.")

def delete_webhooks_with_name(api, name):
    """Find a webhook by name."""
    for webhook in api.webhooks.list():
        if webhook.name == name:
            print("Deleting Webhook:", webhook.name, webhook.targetUrl)
            api.webhooks.delete(webhook.id)

def day_0():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for name in DEMO_PEOPLE:
            futures.append(executor.submit(api.messages.create, toPersonEmail=name, text="🇷🇴Cisco Connect România 2020🇷🇴 începe mâine la ora 10.00.\nVă așteptăm pe cs.co/connectro! "))
            time.sleep(0.3333)
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

def start_day_1():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for name in DEMO_PEOPLE:
            futures.append(executor.submit(api.messages.create, toPersonEmail=name, text="Bună dimineața!\nLa ora 10.00 începe Cisco Connect România 2020 cu sesiunea de keynote a lui Paul Maravei, Director General, Cisco România.😎 \nVă așteptăm pe cs.co/connectro!"))
            time.sleep(0.3333)
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
def Jamey():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for name in DEMO_PEOPLE:
            futures.append(executor.submit(api.messages.create, toPersonEmail=name, text="În curând începe prezentarea lui Jamey Heary, Chief Security Architect, Cisco.🥳\nVă așteptăm pe cs.co/connectro!"))
            time.sleep(0.3333)
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

def feedback():
     with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for name in DEMO_PEOPLE:
            futures.append(executor.submit(api.messages.create(
            toPersonEmail=name,
            text="If you see this your client cannot render cards",
            attachments=[{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card_data.cards[0]
            }]
        )))
            time.sleep(0.3333)
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
def mid_day_1(): 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for name in DEMO_PEOPLE:
            futures.append(executor.submit(api.messages.create, toPersonEmail=name, text="Vă mulțumim 👏 pentru participarea la sesiunile de keynote și vă așteptăm începând cu ora 14.00 la prezentările susținute de colegii nostri de la Cisco.\nVedeți aici mai multe detalii despre ceea ce urmează: cs.co/connectro"))
            time.sleep(0.3333)
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
def end_day_1():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for name in DEMO_PEOPLE:
            futures.append(executor.submit(api.messages.create, toPersonEmail=name, text="Vă mulțumim că ați fost alături de noi astăzi si sperăm că prezentările vi s-au părut interesante.👋 👋\nNu uitați că mâine începem la ora 10.00!\nVedeți aici mai multe detalii despre ceea ce urmează: cs.co/connectro"))
            time.sleep(0.3333)
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
def start_day_2():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for name in DEMO_PEOPLE:
            futures.append(executor.submit(api.messages.create, toPersonEmail=name, text="Bună dimineața!✌️\nÎncepând cu ora 10.00 vă așteptăm la sesiunile de breakout prezentate de colegii nostri de la Cisco.\nVedeți aici mai multe detalii despre prezentări: cs.co/connectro"))
            time.sleep(0.3333)
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
def mid_day_2():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for name in DEMO_PEOPLE:
            futures.append(executor.submit(api.messages.create, toPersonEmail=name, text="Începând cu ora 14.00 vă așteptăm la sesiunile de breakout susținute de partenerii noștri.\nVedeți aici mai multe detalii despre prezentări: cs.co/connectro"))
            time.sleep(0.3333)
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
def end_connect(): 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for name in DEMO_PEOPLE:
            futures.append(executor.submit(api.messages.create, toPersonEmail=name, text="Vă mulțumim pentru participare la Cisco Connect România 2020!👋 👋"))
            time.sleep(0.3333)
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

if __name__ == '__main__':
    # Start the Flask web server
    delete_webhooks_with_name(api, name=WEBHOOK_NAME)
    create_ngrok_webhook(api)
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=day_0, trigger="date", run_date=datetime(2020, 11, 12, 23, 39, 0))
    scheduler.add_job(func=start_day_1, trigger="date", run_date=datetime(2020, 11, 13, 9, 15, 0))
    scheduler.add_job(func=Jamey, trigger="date", run_date=datetime(2020, 11, 13, 11, 15, 0))
    scheduler.add_job(func=feedback, trigger="date", run_date=datetime(2020, 11, 23, 19, 3, 0))
    scheduler.add_job(func=mid_day_1, trigger="date", run_date=datetime(2020, 11, 13, 13, 45, 0))
    scheduler.add_job(func=end_day_1, trigger="date", run_date=datetime(2020, 11, 13, 17, 30, 0))
    scheduler.add_job(func=start_day_2, trigger="date", run_date=datetime(2020, 11, 14, 9, 30, 0))
    scheduler.add_job(func=mid_day_2, trigger="date", run_date=datetime(2020, 11, 14, 13, 45, 0))
    scheduler.add_job(func=end_connect, trigger="date", run_date=datetime(2020, 11, 14, 17, 30, 0))
   
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    flask_app.run(host='0.0.0.0', port=5000, debug=False)