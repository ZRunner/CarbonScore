from urllib import response
import requests
import os
import urllib.parse
from dotenv import load_dotenv
from googletrans import Translator

load_dotenv()
translator = Translator()

def answer(question : str) -> str:
    """Respond to question using Wolframalpha API

    Args:
        question (str): French question

    Returns:
        str: French response
    """
    print("Question : "+question)
    question = answer(translator.translate(question, dest="en").text)
    print("Translated question : "+question)
    url : str = "https://api.wolframalpha.com/v1/result?appid="+os.getenv("WOLFRAMALPHA_API_KEY")+"&i="+urllib.parse.quote(question,safe="")
    response : str = requests.get(url)
    print("Response : "+response.text)
    translated : str = translator.translate(response.text, dest="fr").text
    print("Translated answer : "+translated)
    return translated
    