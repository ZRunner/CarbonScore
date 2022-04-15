from datetime import datetime
from typing import Callable, Optional

from typing import Literal

from carbonscore import get_clothes_number, get_diet, get_distance_km, get_heater_carbon, get_heater_sources, get_heater_surface, get_time_hours


class Session:
    def __init__(self, userid: str):
        self.userid = userid
        self.started_report = False
        self.last_activity = datetime.now()
        self.car_usage: Optional[int] = None # km/semaine
        self.flat_surface: Optional[int] = None # m²
        self.heating_sources: Optional[set[str]] = None
        self.screen_time: Optional[float] = None # par jour
        self.diet: Optional[Literal['normal', 'vegetarien', 'vegan']] = None # par an
        #self.redmeal_count: Optional[int] = None # par semaine
        self.clothes_count: Optional[int] = None # par mois
    
    @property
    def doing_report(self):
        "If the user should be currently answering questions"
        return self.started_report and not self.has_ended
    
    @property
    def has_ended(self):
        "If the user finished answering questions"
        return self.clothes_count is not None
    
    def reset(self):
        "Reset every counter to default"
        self.car_usage = None
        self.flat_surface = None
        self.heating_sources = None
        self.screen_time = None
        self.diet = None
        self.clothes_count = None

    def get_callback(self) -> Optional[Callable[[str], None]]:
        if not self.doing_report:
            return None
        if self.car_usage is None:
            return self.get_car_usage
        if self.flat_surface is None:
            return self.get_flat_surface
        if self.heating_sources is None:
            return self.get_heating_sources
        if self.screen_time is None:
            return self.get_screen_time
        if self.diet is None:
            return self.get_alimentation_diet
        if self.clothes_count is None:
            return self.get_clothes_count
        return None
    
    def get_next_message(self) -> Optional[str]:
        if self.car_usage is None:
            return "Combien de kilomètres parcourez-vous en voiture par semaine ?"
        if self.flat_surface is None:
            return "Quelle est la surface en m² de votre habitat ?"
        if self.heating_sources is None:
            return "Quel type de chauffage utilisez-vous ? (fioul, électricité, bois...)"
        if self.screen_time is None:
            return "Combien d'heures en moyenne passez-vous sur un écran chaque semaine ? (ordinateur, smartphone, télévision)"
        if self.diet is None:
            return "Quel est votre régime alimentaire ? (Végan, végétarien, mange de tout)"
            #return "Combien de vos repas sont composés de viande rouge par semaine ? (bœuf, mouton...)"
        if self.clothes_count is None:
            return "Dernière question !\nCombien de vêtements neufs achetez-vous chaque mois ?"
        total = round(self.total/1000)
        # voiture + energies + habillement + technologies + viandes/poissons + lait/œufs
        delta = total - (1972+1696+763+1180+1144+408)
        return f"""Votre empreinte carbonne moyenne est de {total}kg de CO2 par an, soit {abs(delta)}kg {'de plus' if delta>0 else 'de moins'} que la moyenne française.
        
Si vous avez d'autres question, je reste à votre disposition !"""
    
    def get_car_usage(self, msg: str):
        self.car_usage = get_distance_km(msg)
        print("Car usage:", self.car_usage)
    
    def get_flat_surface(self, msg: str):
        self.flat_surface = get_heater_surface(msg)
        print("Flat surface:", self.flat_surface)

    def get_heating_sources(self, msg: str):
        self.heating_sources = get_heater_sources(msg)
        print("heating sources:", self.heating_sources)
    
    def get_screen_time(self, msg: str):
        self.screen_time = get_time_hours(msg)
        print("screen time:", self.screen_time)
    
    def get_alimentation_diet(self, msg: str):
        self.diet = get_diet(msg)
        print("diet:", self.diet)
    
    def get_clothes_count(self, msg: str):
        self.clothes_count = get_clothes_number(msg)
        print("clothes count:", self.clothes_count)

    @property
    def car_emission(self): # /semaine
        return self.car_usage*55 if self.car_usage is not None else None
    
    @property
    def heating_emission(self): # /an
        if self.heating_sources is None or self.flat_surface is None:
            return None
        return get_heater_carbon(self.heating_sources, self.flat_surface)

    @property
    def screen_emission(self): # /jour
        return self.screen_time*40 if self.screen_time is not None else None
    
    @property
    def meal_emission(self): # gCO2/an
        emissions = {
            "normal": 1144+408,
            "vegetarien": 408,
            "vegan": 0
        }
        return emissions[self.diet]*1000 if self.diet is not None else None
    
    @property
    def clothes_emission(self): # / mois
        return self.clothes_count*15_000 if self.clothes_count is not None else None
    
    @property
    def total(self): # gCO2/an
        return round(self.car_emission*52 + self.heating_emission + self.screen_emission*365.25 + self.meal_emission + self.clothes_emission*12)
    
    def __str__(self):
        return f"Session(userid={self.userid} total={self.total})"
    
    def to_dict(self):
        return {
            "car": self.car_emission,
            "heating": self.heating_emission,
            "screen": self.screen_emission,
            "meal": self.meal_emission,
            "clothes": self.clothes_emission,
            "total": self.total
        }
