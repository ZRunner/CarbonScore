import re
from typing import Optional
import spacy

from parsing import parse_msg

nlp = spacy.load("fr_core_news_lg")

def get_heater_carbon(sources: dict[str, int], surface: int) -> Optional[int]:
    if len(sources) == 0:
        return None
    surface = surface/len(sources)
    return round(sum(surface*100*value for value in sources.values()))

def get_heater_surface(sentence: str) -> int:
    if sentence.isnumeric():
        print("surface:", int(sentence))
        return int(sentence)
    result = 0
    for match in re.findall(r'([\d\s]+)(?:[,.]\d+\s*)?(?:m|mètre|metre)', sentence.lower()):
        match: str
        result += int(match.replace(' ', ''))
    print("surface:", result or None)
    return result or None

def get_heater_sources(sentence: str) -> dict[str, int]:
    sources = {
        "fioul": 264,
        "gaz": 208,
        "électricité": 79,
        "radiateur": 79,
        "biométhane": 14,
        "bois": 0
    }
    result = {}
    doc = parse_msg(sentence)

    # on lit tous les mots de la phrase
    for word in doc:
        if word.is_stop or word.text in {"chauffe"}:
            continue
        max_value: float = 0.55 # plus grande similarité de source pour ce mot
        max_src: str = None # source la plus proche de ce mot (None si aucune)
        # on regarde chaque source
        for source in sources.keys():
            score = word.similarity(nlp(source))
            # si ce mot est plus proche que le mot actuel
            if score > max_value:
                max_src = source
                max_value = score
        # si on a trouvé un mot similaire
        if max_src:
            result[max_src] = sources[max_src]
    print("heater sources:", result or None)
    return result or None

def get_distance_km(sentence: str) -> Optional[int]:
    if sentence.isnumeric():
        print("car distance:", int(sentence))
        return int(sentence)
    if nlp(sentence).similarity(nlp("je ne prend pas la voiture")) > 0.8:
        return 0
    result = None
    # distance
    if match := re.search(r'([\d\s]+)(?:[,.]\d+\s*)?(?:km|kilomètres?)', sentence.lower()):
        result = int(match.group(1).replace(' ', ''))
        # number of people
        if match2 := re.search(r'(\d+) (?:passagers?|personnes)', sentence.lower()):
            result *= int(match2.group(1).replace(' ', ''))
        # number of *other* people
        elif match2 := re.search(r'(\d+) autres? (?:passagers?|personnes)?', sentence.lower()):
            result *= int(match2.group(1).replace(' ', '')) + 1
    print("car distance:", result)
    return result

def get_time_hours(sentence: str) -> Optional[int]:
    result = None
    if sentence.isnumeric():
        result = int(sentence)
    elif match := re.search(r'(\d+) ?(?:h)', sentence.lower()):
        result = int(match.group(1))
    # check for aberations
    if result is not None and result > 24*7:
        result = None
    print("screen time:", result)
    return result

def get_diet(sentence: str) -> int:
    sources = [
        "végétarien",
        "végan",
        "normal",
        "tout"
    ]
    
    result = []
    doc = parse_msg(sentence)
    # on lit tous les mots de la phrase
    for word in doc:
        max_value: float = 0.55 # plus grande similarité de source pour ce mot
        max_src: str = None # source la plus proche de ce mot (None si aucune)
        if (word.text in {"vege","végé","vége","vegé"}):
            result.append("végétarien")
        # on regarde chaque source
        for source in sources:
            score = word.similarity(nlp(source))
            if score > max_value:
                max_src = source
                max_value = score
        # si on a trouvé un mot similaire
        if max_src:
            result.append(max_src)
            
    if ("normal" in result #N'est pas vegan ni vegetarien
        or "tout" in result 
        or (not "végan" in result
            and not "végétarien" in result)):
        print("diet: normal")
        return 1144+408
    elif ("végétarien" in result): #Est vegetarien
        print("diet: vetegarien")
        return 408
    else: #Est vegan
        print("diet: vegan")
        return 0
    
def get_clothes_number(sentence: str) -> int:
    if sentence.isnumeric():
        return int(sentence)
    result = 0
    count = 0
    for match in re.findall(r'(\d+) ?(?:vêtements?|vetements)?', sentence.lower()):
        match: str
        count += 1
        result += int(match.replace(' ', ''))
    return int(result/count) if count != 0 else None

if __name__ == '__main__':
    # src = get_heater_sources("Je me réchauffe principalement au fioul")
    # surface = get_heater_surface("J'ai 1 151,7 m²")
    # print(src, surface)
    # print(get_heater_carbon(src, surface))
    # print(get_distance_km("J'utilise la voiture 12km par semaine, on est avec 3 personnes"))
    # print(get_distance_km("5km par semaine en moyenne, avec 4 autres collègues"))
    # print(get_distance_km("je ne prend jamais ma voiture"))
    # print(get_diet("Je mange de tout et de temps en temps je suis vegan"))
    print(get_clothes_number("Environ entre 15 et 8 vêtements"))
    print(get_clothes_number("Je suis pauvre"))
