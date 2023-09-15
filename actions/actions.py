# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import random
import os.path
import json

class OperarArchivo():

    @staticmethod
    def guardar(save, ruta):
        with open(ruta,"w") as archivo:
            json.dump(save, archivo, indent=4)
        archivo.close()

    @staticmethod
    def cargar(ruta): 
        if os.path.isfile(ruta):
            with open(ruta,"r") as archivo:
                retorno=json.load(archivo)
                archivo.close()
        else:
            retorno={}
        return retorno


class ActionAgregarEjemplos(Action):

    def name(self) -> Text:
        return "action_ejemplos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        request = tracker.get_slot("request")
        name = tracker.get_slot("name")
        if request == "intent":
            ruta = "./actions/intents.json"
        elif request == "response":
            ruta = "./actions/response.json"
        else:
            ruta = "./actions/story.json"        

        archivo = OperarArchivo.cargar(ruta)

        # Verificar si hay ejemplos
        if name in archivo and 'examples' in archivo[name] and archivo[name]['examples']:
            valores = archivo[name]['examples']
            dispatcher.utter_message(text="Los ejemplos actuales son: " + str(valores) + ". Agrega el ejemplo que usted desea a continuación.")
            return [SlotSet("examples", valores)]       
        else:
            dispatcher.utter_message(text="el nombre que dices no existe en el archivo, si desea empiece de nuevo y crealo.")
            return [SlotSet("examples", [])]

class ActionGuardarEjemplos(Action):

    def name(self) -> Text:
        return "action_guardar_ejemplo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        request = tracker.get_slot("request")
        name = tracker.get_slot("name")
        examples = tracker.latest_message.get("text")

        if request == "intent":
            ruta = "./actions/intents.json"
        elif request == "response":
            ruta = "./actions/response.json"
        else:
            ruta = "./actions/story.json"        

        archivo = OperarArchivo.cargar(ruta)
        ##devolver mensaje del nombre del request 
        dispatcher.utter_message(text="El nombre del " + request + " es: " + name)
        if name not in archivo:
            archivo[name] = {'examples': [examples]}
            OperarArchivo.guardar(archivo, ruta)
            dispatcher.utter_message(text="Listo. Se guardó con éxito.")
        elif 'examples' in archivo[name] and archivo[name]['examples']:
            archivo[name]['examples'].append(examples)
            OperarArchivo.guardar(archivo, ruta)
            dispatcher.utter_message(text="Nombre de " + request + " ya existe. Se ha actualizado la lista de ejemplos.")
        else:
            dispatcher.utter_message(text="El nombre de " + request + " ya existe, pero no tiene ejemplos. No se ha realizado ninguna actualización.")
        
        return [SlotSet("examples", archivo[name]['examples'] if 'examples' in archivo[name] else []), SlotSet("request", "")]
