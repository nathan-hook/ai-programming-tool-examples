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

chat_model = "qwen3:1.7b"

def get_latitude_longitude(city:str):

  prompt = f'''
  You are an assistant that is an expert at geography.

  Here is the end user's query:

  <QUERY>
  {city}
  </QUERY>

  Your job is to take the end user's query and return a reasonable latitude and longitude point for that location.

  when you receive the named location, assume it is a city, but if the query is specific, than use the more specific
  location.

  If you cannot determine the location, return an empty json response.

  Example 1:
  Input: "New York City"
  Output:
  {{
    "latitude": 40.730610,
    "longitude": -73.935242
  }}

  Example 2:
  Input: "Boulder, Colorado"
  Output:
  {{
    "latitude": 40.014984,
    "longitude": -105.270546
  }}

  Example 2:
  Input: "Uppsala"
  Output:
  {{
    "latitude": 59.86993,
    "longitude": 17.64749
  }}

  Example 4:
  Input: "SomeUnknownPlaceThatDoesNotExist"
  Output:
  {{ }}
  '''

  print("Prompt to get lat/long: "+prompt)
  
  print("prompt: " + prompt)

  messages = [{"role":"system", "content":prompt}]

  agent_res = client.chat(
    model=chat_model,
    stream=False,
    messages=messages,
    think=False)

  print(agent_res)

  return json.loads(agent_res.message.content)
##Test
#print(get_latitude_longitude("New York"))
#print(get_latitude_longitude("Boulder"))

def current_temperature_lat_long(latitude:float, longitude:float) -> str:
  parameters = {'latitude': latitude, 'longitude': longitude, 'current': 'temperature_2m'}
  response = requests.get('https://api.open-meteo.com/v1/forecast', params=parameters)
  print("response: " + str(response))
  print("response as json: " + str(response.json()))
  return str(response.json()["current"]["temperature_2m"]) + response.json()["current_units"]["temperature_2m"]
## Test
#temp = current_temperature_lat_long(40.710335, -73.99309)
#print(temp)

def current_temperature(location:str) -> str:

  lat_long_json = get_latitude_longitude(location)

  print("lat_long_json: " + json.dumps(lat_long_json))

  return current_temperature_lat_long(lat_long_json["latitude"], lat_long_json["longitude"])
## Test
#temperature = current_temperature("What's the temperature in New York?")
#print(temperature)

tool_current_temperature = {
  'type':'function',
  'function':{
    'name': 'current_temperature',
    'description': 'Current temperature for the given location',
    'parameters': {
      'type': 'object',
      'required': ['location'],
      'properties': {
        'location': {'type':'str', 'description':'the name of the location to get the current temperature for'}
      }
    }
  }}

prompt = '''You are an assistant with access to tools, you must decide when to use tools to answer user message.'''
query = '''What's the temperature in Boulder, Colorado?'''
messages = [{"role":"system", "content":prompt},
  {"role":"user", "content":query}]

agent_response = client.chat(
  model=chat_model,
  stream=False,
  tools=[tool_current_temperature],
  messages=messages)

print("agent_response: " + str(agent_response))

dic_tools = {'current_temperature':current_temperature}

if agent_response.message.tool_calls:
  for tool in agent_response.message.tool_calls:

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

      print("tool_messages: " + str(tool_messages))

      agent_response = client.chat(
        model=chat_model,
        stream=False,
        messages=tool_messages)
      
      print("agent_response: " + str(agent_response))
      print("content: " + agent_response.message.content)
