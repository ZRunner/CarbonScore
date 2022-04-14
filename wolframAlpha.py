import os
import urllib.parse

import requests
from dotenv import load_dotenv
from googletrans import Translator

load_dotenv()
translator = Translator()


def answer(question: str) -> str:
    """Answer to a question using WolframAlpha API

    Args:
        question (str): French question

    Returns:
        str: French response
    """
    print("Question: "+question)
    question = translator.translate(question, dest="en").text
    print("Translated question: "+question)
    url: str = "https://api.wolframalpha.com/v1/result?appid=" + \
        os.getenv("WOLFRAMALPHA_API_KEY")+"&i=" + \
        urllib.parse.quote(question, safe="")
    response = requests.get(url)
    print("Response:", response.text)
    translated: str = translator.translate(response.text, dest="fr").text
    print("Translated answer:", translated)
    if (response.status_code == 501):
        translated = "Je ne sais pas répondre à ce message"
    return translated
