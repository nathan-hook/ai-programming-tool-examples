#pip install ollama
#pip install requests

import json
import requests

from ollama import chat
from ollama import Client
from ollama import ChatResponse


# Here is an example of tool calling from the official ollama website:
# https://docs.ollama.com/capabilities/tool-calling

client = Client(
  host='http://ollama:11434'
)

def get_latitude_longitude(city:str):
  prompt = '''You are an assistant that is an expert at geography.

  Here is the end user's query:

  {query}

  Your job is to take the end user's query and return a reasonable latitude and longitude point for that location.

  when you receive the named location, assume it is a city, but if the query is specific, than use the more specific
  location.

  Here is an example json response for New York City:
  {
    "latitude":40.710335
    "longitude":-73.99309
  }

  If you cannot determine the location, return an empty json response.'''
  
  messages = [{"role":"system", "content":prompt}]

  agent_res = client.chat(
    #model='qwen3:4b',
    model='qwen3:1.7b',
    #format="json", #or schema
    stream=False,
    messages=messages)

  print(agent_res)

  return json.loads(agent_res.message.content)
##Test
#print(get_latitude_longitude("New York"))
#print(get_latitude_longitude("Boulder"))

def current_tempature_lat_long(latitude:float, longitude:float) -> str:
  parameters = {'latitude': latitude, 'longitude': longitude, 'current': 'temperature_2m'}
  response = requests.get('https://api.open-meteo.com/v1/forecast', params=parameters)
  print(response)
  print(response.json())
  return str(response.json()["current"]["temperature_2m"]) + response.json()["current_units"]["temperature_2m"]
## Test
#temp = current_tempature_lat_long(40.710335, -73.99309)
#print(temp)

def current_tempature(location:str) -> str:

  lat_long_json = get_latitude_longitude(location)

  print(json.dumps(lat_long_json))

  # do stuff here...
  # call a simple model to get the lat/long of the entered city as a json response.
  ## Give example of how to return the json response.
  # Take the returned lat/long and call the Open-Meteo api to get current tempature.
  # https://open-meteo.com/en/docs
  # Example:
  # https://api.open-meteo.com/v1/forecast?latitude=40.7143&longitude=-74.006&hourly=temperature_2m
  # Returns the following json:

  return current_tempature_lat_long(lat_long_json["latitude"], lat_long_json["longitude"])
## Test
#tempature = current_tempature("What's the tempature in New York?")
#print(tempature)

tool_current_tempature = {
  'type':'function',
  'function':{
    'name': 'current_tempature',
    'description': 'Current tempature for the given location',
    'parameters': {
      'type': 'object',
      'required': ['location'],
      'properties': {
        'location': {'type':'str', 'description':'the name of the location to get the current tempature for'}
      }
    }
  }}

prompt = '''You are an assistant with access to tools, you must decide when to use tools to answer user message.'''
query = '''What's the weather in Boulder?'''
messages = [{"role":"system", "content":prompt},
  {"role":"user", "content":query}]

agent_res = client.chat(
  model='qwen3:1.7b',
  stream=False,
  tools=[tool_current_tempature],
  messages=messages)

dic_tools = {'current_tempature':current_tempature}

if agent_res.message.tool_calls:
  for tool in agent_res.message.tool_calls:

    t_name = tool["function"]["name"]
    print(t_name)
    t_inputs = tool["function"]["arguments"]
    print(t_inputs)

    if f := dic_tools.get(t_name):
      ### tool output
      t_output = f(**tool["function"]["arguments"])
      print(t_output)
      ### final res
      tool_messages = [
        {"role":"system", "content": "You are a helpful assistant."},
        {"role":"user", "content":query},
        {"role":"assistant", 
          "tool_calls": [
            {
              "type": "function",
              "function": {
                "index": 0,
                "name": t_name,
                "arguments": t_inputs
              }
            }]},
        {"role": "tool", "tool_name": t_name, "content": str(t_output)}
      ]

      print(tool_messages)

      agent_res = client.chat(
        #model='qwen3:4b',
        model='qwen3:1.7b',
        stream=False,
        messages=tool_messages)
      print(agent_res)
