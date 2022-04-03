from datetime import datetime
import logging
import os
import random

from dotenv import load_dotenv
from flask import Flask, request
from pymessenger.bot import Bot

import answering.wolframAlpha as WolframAlpha
from session import Session

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_MESSENGER")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN_MESSENGER")
bot = Bot(ACCESS_TOKEN)

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)

sessions: dict[str, Session] = {}

# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output: dict = request.get_json()
        for event in output['entry']:
            messaging: list[dict] = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id: str = message['sender']['id']
                    # response_sent_text = get_message()
                    user_message: str = message['message'].get('text')
                    if message['message'].get('text'):
                        treat_message(recipient_id, user_message)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    elif message['message'].get('attachments'):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)
    return "Message Processed"

def treat_message(recipient_id: str, user_message: str):
    "Read a message from a given user and correctly answers"
    # retrieve user session
    if recipient_id in sessions:
        session = sessions.get(recipient_id)
    else:
        session = Session(recipient_id)
        sessions[recipient_id] = session
    # update last activity
    session.last_activity = datetime.now()
    if callback := session.get_callback():
        # if a carbon report is in progress, process the user response then answer
        callback(user_message)
        app.logger.info(f"{recipient_id=}  msg=\"{user_message}\" callback={callback.__name__} next=\"{session.get_next_question()}\"")
        send_message(recipient_id, session.get_next_question())
    else:
        # use WolframAlpha to get an answer
        app.logger.info(f"{recipient_id=}  msg=\"{user_message}\"")
        send_message(recipient_id, WolframAlpha.answer(user_message))


def verify_fb_token(token_sent: str):
    """Takes token sent by facebook and verify it matches the verify token you sent
    if they match, allow the request, else return an error"""
    err = 'Invalid verification token'
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge") or err
    return err


def get_message():
    "Chooses a random message to send to the user"
    sample_responses = ["You are stunning!", "We're proud of you.",
                        "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

def send_message(recipient_id: str, response: str):
    "Uses PyMessenger to send response to a user"
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run()
