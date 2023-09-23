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
from rasa_sdk.events import ActionExecuted
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
            dispatcher.utter_message(text="Los intents existentes son: " + str(list(archivo_intent.keys())))
        else:
            dispatcher.utter_message(text="No hay intents existentes.")
        if archivo_response:
            dispatcher.utter_message(text="Los responses existentes son: " + str(list(archivo_response.keys())))
        else:
            dispatcher.utter_message(text="No hay responses existentes.")
        return []
        
class ActionVerificarIntent(Action):
        
    def name(self) -> Text:
        return "action_verificar_datos_intent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        name = tracker.latest_message.get("text")
        ruta = "./actions/intents.json"
        archivo = OperarArchivo.cargar(ruta)
        if name in archivo:
            dispatcher.utter_message(text="El intent " + name + " existe.")
        else:
            dispatcher.utter_message(text="El intent " + name + " no existe.")
        return [SlotSet("intentStory", name if name in archivo else None)]

class ActionVerificarResponse(Action):
            
    def name(self) -> Text:
        return "action_verificar_datos_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        name = tracker.latest_message.get("text")
        ruta = "./actions/response.json"
        archivo = OperarArchivo.cargar(ruta)
        if name in archivo:
            dispatcher.utter_message(text="El response " + name + " existe.")
        else:
            dispatcher.utter_message(text="El response " + name + " no existe.")
        return [SlotSet("responseStory", name if name in archivo else None)]

class ActionSetStory(Action):

    def name(self) -> Text:
        return "action_guardar_story"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_slot("intentStory")
        response = tracker.get_slot("responseStory")
        name = tracker.get_slot("name")
        ruta = "./actions/story.json"
        archivo = OperarArchivo.cargar(ruta)

        if not archivo:
            archivo = {}

        if name in archivo:
            # Verifica si la historia ya existe y agrega los intents y responses
            contador = str(int(archivo[name]["contador"]) + 1)
            archivo[name]["contador"] = contador
            archivo[name]["intent " + contador] = intent
            archivo[name]["response " + contador] = response
            dispatcher.utter_message(text=f"Se han agregado intent y response a la historia '{name}'")
        else:
            # Si la historia no existe, la crea con el nuevo intent y response
            archivo[name] = {"contador": "0", 'intent 0': intent, 'response 0': response}
            dispatcher.utter_message(text=f"Se ha creado una nueva historia '{name}' con intent y response")

        # Guarda el archivo actualizado
        OperarArchivo.guardar(archivo, ruta)

        return [SlotSet("intentStory", ""), SlotSet("responseStory", ""), SlotSet("name", ""), SlotSet("actionLast", "")]

class utterPedirIntent(Action):
    def name(self) -> Text:
        return "action_pedirIntent"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            dispatcher.utter_message(text="Ingrese el nombre del intent que desea.")
            return [SlotSet("actionLast", "utter_pedir_intent")]

class utterPedirResponse(Action):
    def name(self) -> Text:
        return "action_pedirResponse"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            dispatcher.utter_message(text="Ingrese el nombre del response que desea.")
            return [SlotSet("actionLast", "utter_pedir_response")]


class listnameStory(Action):
    def name(self) -> Text:
        return "action_listar_storys"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        ruta_story = "./actions/story.json"
        archivo = OperarArchivo.cargar(ruta_story)
        if archivo:
            dispatcher.utter_message(text="Las story existentes son: " + str(list(archivo.keys())))
        else:
            dispatcher.utter_message(text="No hay intents existentes.")
        return []
        
class ImprimirStory(Action):

    def name(self) -> Text:
        return "action_imprimir_story"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Obtener el nombre de la historia desde el slot
        name = tracker.get_slot("name")
        ruta = "./actions/story.json"
        archivo = OperarArchivo.cargar(ruta)

        if not archivo:
            dispatcher.utter_message(text="No se encontró el archivo de historias.")
            return []

        if name not in archivo:
            dispatcher.utter_message(text=f"No se encontró la historia con el nombre '{name}'.")
            return []

        # Obtener todo el contenido de la historia seleccionada
        historia_contenido = archivo[name]

        # Mostrar todo el contenido de la historia
        message = f"Contenido de la historia '{name}':\n{historia_contenido}"
        dispatcher.utter_message(text=message)

        return []
