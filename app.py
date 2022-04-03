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

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id: str = message['sender']['id']
                if message['message'].get('text'):
                    # response_sent_text = get_message()
                    user_message: str = message['message'].get('text')
                    # retrieve user session
                    if recipient_id in sessions:
                        session = sessions.get(recipient_id)
                    else:
                        session = Session(recipient_id)
                        sessions[recipient_id] = session
                    if callback := session.get_callback():
                        app.logger.info(f"{recipient_id=}  msg={user_message} callback={callback.__name__} next={session.get_next_question()}")
                        callback(user_message)
                        send_message(recipient_id, session.get_next_question())
                    else:
                        app.logger.info(f"NO CALLBACK {recipient_id=}  msg={user_message}")
                        send_message(recipient_id, WolframAlpha.answer(user_message))
                        
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent: str):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    err = 'Invalid verification token'
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge") or err
    return err


#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
