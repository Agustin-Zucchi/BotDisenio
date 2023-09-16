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


class ActionShowOrder(Action):

    def name(self) -> Text:
        return "action_listar_existentes"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        request = tracker.get_slot("request")
        if request == "intent":
            ruta = "./actions/intents.json"
        elif request == "response":
            ruta = "./actions/response.json"
        else:
            ruta = "./actions/story.json"  
        archivo = OperarArchivo.cargar(ruta)
        if archivo:
            dispatcher.utter_message(text="Los " + request + " existentes son: " + str(list(archivo.keys())) + ". Para ingresar el nombre del " + request + " que desea, digite 'quiero modificar el nombre del " + request + "'.")
        else:
            dispatcher.utter_message(text="No hay " + request + " existentes.")
        return [SlotSet("request", "")]

class ActionShowAllRequest(Action):
    
        def name(self) -> Text:
            return "action_listar_intents_responses"
    
        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
            ruta_intent = "./actions/intents.json"
            ruta_response = "./actions/response.json"
            archivo_intent = OperarArchivo.cargar(ruta_intent)
            archivo_response = OperarArchivo.cargar(ruta_response)
            if archivo_intent:
                dispatcher.utter_message(text="Los intents existentes son: " + str(list(archivo_intent.keys()))+ "Para ingresar el nombre del intent que desea, digite 'quiero modificar el nombre del intent'.")
            else:
                dispatcher.utter_message(text="No hay intents existentes.")
            if archivo_response:
                dispatcher.utter_message(text="Los responses existentes son: " + str(list(archivo_response.keys()))+ "Para ingresar el nombre del response que desea, digite 'quiero modificar el nombre del response'.")
            else:
                dispatcher.utter_message(text="No hay responses existentes.")
            return []
        
class ActionVerificarIntent(Action):
        
            def name(self) -> Text:
                return "action_verificar_intent"
        
            def run(self, dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
                name = tracker.getlatest_message.get("text")
                ruta = "./actions/intents.json"
                archivo = OperarArchivo.cargar(ruta)
                if name in archivo:
                    dispatcher.utter_message(text="El intent " + name + " existe.")
                else:
                    dispatcher.utter_message(text="El intent " + name + " no existe.")
                return [SlotSet("intentStory", name if name in archivo else None)]

class ActionVerificarResponse(Action):
            
                def name(self) -> Text:
                    return "action_verificar_response"
            
                def run(self, dispatcher: CollectingDispatcher,
                        tracker: Tracker,
                        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
                    name = tracker.getlatest_message.get("text")
                    ruta = "./actions/response.json"
                    archivo = OperarArchivo.cargar(ruta)
                    if name in archivo:
                        dispatcher.utter_message(text="El response " + name + " existe.")
                    else:
                        dispatcher.utter_message(text="El response " + name + " no existe.")
                    return [SlotSet("responseStory", name if name in archivo else None)]

class ActionSetStory(Action):
                
                    def name(self) -> Text:
                        return "action_set_story"
                
                    def run(self, dispatcher: CollectingDispatcher,
                            tracker: Tracker,
                            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
                        intent = tracker.get_slot("intentStory")
                        response = tracker.get_slot("responseStory")
                        name = tracker.get_slot("name")
                        ruta = "./actions/story.json"
                        archivo = OperarArchivo.cargar(ruta)
                        if name in archivo:
                            dispatcher.utter_message(text="El story " + name + " ya existe.")
                        else:
                            archivo[name] = {'intent': intent, 'response': response}
                            OperarArchivo.guardar(archivo, ruta)
                            dispatcher.utter_message(text="Listo. Se guardó con éxito.")
                        return [SlotSet("intentStory", ""), SlotSet("responseStory", ""), SlotSet("name", "")]        
        