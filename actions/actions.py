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
        example = tracker.latest_message.get("text")
        examples_actuales = tracker.get_slot("examples")
        request = tracker.get_slot("request")
        if (example):
            examples_actuales.append(example)
            message = "Ejemplo guardado. Si querés podés ingresar otro ejemplo. Hasta ahora el intent " + request + "tiene los siguientes ejemplos: "
            for i, ex in enumerate(examples_actuales, start=1):
                message = message + ex + ", "
            dispatcher.utter_message(text=str(message))
            return [SlotSet("examples", examples_actuales)]
        
class ActionGuardarEjemplos(Action):

    def name(self) -> Text:
        return "action_guardar_ejemplos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        examples = tracker.get_slot("examples")
        request = tracker.get_slot("request")
        if request == "intent":
            ruta = ".//actions//intents.json"
        else:
            ruta = ".//actions//request.json"
        archivo = OperarArchivo.cargar(ruta)
        archivo[request]['examples'] = [examples]
        archivo.update(archivo)
        OperarArchivo.guardar(archivo, ruta)
        dispatcher.utter_message(text="Listo. se guardo con exito")
        return [SlotSet("examples", []), SlotSet("request", "")]
        
    