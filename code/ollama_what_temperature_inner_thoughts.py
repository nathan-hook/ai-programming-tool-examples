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

def latitude_longitude(location:str):
  prompt = f'''You are an assistant that is an expert at geography.

  Here is the end user's query:

  <QUERY>
  {location}
  </QUERY>

  Your job is to take the end user's query and return a reasonable latitude and longitude point for that location.

  when you receive the named location, assume it is a city, but if the query is specific, than use the more specific
  location.

  Here is an example json response:
  {{
    "latitude":decimal_latitude_value
    "longitude":decimal_longitude_valule
  }}

  If you cannot determine the location, return an empty json response.'''
  
  messages = [{"role":"system", "content":prompt}]

  agent_response = client.chat(
    model='qwen3:1.7b',
    stream=False,
    think=False,
    messages=messages)

  print("agent_response: " + str(agent_response))

  # TODO return the raw string content or a json object?
  # TODO Should this return text or a json object?
  #return json.loads(agent_response.message.content)
  return agent_response.message.content
##Test
#print(get_latitude_longitude("New York"))
#print(get_latitude_longitude("Boulder"))

def current_temperature_lat_long(latitude:float, longitude:float) -> str:
  print("current_temperature_lat_long")
  parameters = {'latitude': latitude, 'longitude': longitude, 'current': 'temperature_2m'}
  response = requests.get('https://api.open-meteo.com/v1/forecast', params=parameters)
  print("response.json(): " + str(response.json()))
  return str(response.json()["current"]["temperature_2m"]) + response.json()["current_units"]["temperature_2m"]
## Test
#temp = current_temperature_lat_long(40.710335, -73.99309)
#print(temp)

def create_tool_argument(name:str, value:str):
  return {
    name: value
  }
## Test
# print("create_tool_argument: " + str(create_tool_argument("name", "value")))

def create_tool_response(name:str, arguments:list, output:str):
  return {
    "name":name,
    "arguments":arguments,
    "output":str(output)
  }

def create_llm_messages(prompt:str, query:str, tools:list = None) -> dict:
  
  messages_dict = [
    {"role":"system", "content":prompt},
    {"role":"user", "content":query}
  ]

  if tools:

    tool_calls = []
    
    for index, tool in enumerate(tools):

      function = {
        "type": "function",
        "function": {
          "index": index,
          "name": tool["name"]
        }
      }
      
      if tool["arguments"]:

        function["function"]["arguments"] = tool["arguments"]

      tool_calls.append(function)

    role_assistant = {"role":"assistant", 
      "tool_calls": tool_calls}
    messages_dict.append(role_assistant)

    for tool in tools:
      tool = {"role": "tool", "tool_name": tool["name"], "content": tool["output"]}
      messages_dict.append(tool)

  return messages_dict

## Test
# messages_dict = create_llm_messages("test_prompt", "test_query")
# print("messages_dict: " + str(messages_dict))

# tool_response = create_tool_response("test_name", [], "test_output")
# messages_dict = create_llm_messages("test_prompt", "test_query", [tool_response])
# print("messages_dict: " + str(messages_dict))

# tool_argument = create_tool_argument("location", "boulder")
# tool_response = create_tool_response("test_name", [tool_argument], "test_output")
# messages_dict = create_llm_messages("test_prompt", "test_query", [tool_response])
# print("messages_dict: " + str(messages_dict))

tool_current_temperature = {
  'type':'function',
  'function':{
    'name': 'current_temperature_lat_long',
    'description': 'Current temperature for the given location',
    'parameters': {
      'type': 'object',
      'required': ['latitude', 'longitude', 'innerthoughts', 'confidence', 'memorynotes'],
      'properties': {
        'latitude': {
          'type':'float',
          'description':'the latitude of the location to get the current temperature for'},
        'longitude': {
          'type':'float',
          'description':'the longitude of the location to get the current temperature for'},
        'innerthoughts': {
          'type':'string',
          'description':'Your step-by-step reasoning for why you are calling this tool and what you expect'},
        'confidence': {
          'type': 'string',
          'description': 'Confidence level (low, medium, high) in this tool choice'},
        'memorynotes': {
          'type': 'array',
          'items': { 'type': 'string' },
          'description': 'Key insights to remember for future interactions'}
      }
    }
  }}
tool_latitude_longitude = {
  'type':'function',
  'function':{
    'name': 'latitude_longitude',
    'description': 'Latitude and longitude for the given location',
    'parameters': {
      'type': 'object',
      'required': ['location', 'innerthoughts', 'confidence', 'memorynotes'],
      'properties': {
        'location': {
          'type':'str',
          'description':'the name of the location to get the latitude and longitude for'},
        'innerthoughts': {
          'type':'string',
          'description':'Your step-by-step reasoning for why you are calling this tool and what you expect'},
        'confidence': {
          'type': 'string',
          'description': 'Confidence level (low, medium, high) in this tool choice'},
        'memorynotes': {
          'type': 'array',
          'items': { 'type': 'string' },
          'description': 'Key insights to remember for future interactions'}
        }
      }
    }
  }

def handle_tool_call(tool:dict) -> dict:

  t_name = tool["function"]["name"]
  print("t_name: " + t_name)
  t_inputs = tool["function"]["arguments"]
  print("t_inputs: " + str(t_inputs))

  innerthoughts = t_inputs.pop("innerthoughts", None)
  print("innerthoughts: " + str(innerthoughts))
  confidence = t_inputs.pop("confidence", None)
  print("confidence: " + str(confidence))
  memorynotes = t_inputs.pop("memorynotes", None)
  print("memorynotes: " + str(memorynotes))

  output_dict = {}

  if f := dic_tools.get(t_name):
    t_output = f(**t_inputs)
    output_dict["output"] = t_output
    output_dict["tool"] = tool
    output_dict["memorynotes"] = memorynotes
  # TODO Throw exception here if the tool isn't found via an else?
  
  return output_dict

prompt = '''You are an assistant with access to tools, you must decide when to use tools to answer user message.'''
query = '''What is the temperature in Boulder?'''
messages = [{"role":"system", "content":prompt},
  {"role":"user", "content":query}]

print("tools: " + str([tool_current_temperature, tool_latitude_longitude]))

agent_response = client.chat(
  model='qwen3:1.7b',
  stream=False,
  tools=[tool_current_temperature, tool_latitude_longitude],
  messages=messages)

print("agent_response: " + str(agent_response))

dic_tools = {'current_temperature_lat_long':current_temperature_lat_long, 'latitude_longitude':latitude_longitude}

tool_calls = agent_response.message.tool_calls

while tool_calls:

  tool_call_results = []

  for tool in tool_calls:

    t_name = tool["function"]["name"]
    t_inputs = tool["function"]["arguments"]

    output_dict = handle_tool_call(tool)

    tool_call_results.append(create_tool_response(t_name, t_inputs, output_dict["output"]))

  tool_messages = create_llm_messages(prompt, query, tool_call_results)

  print("tool_messages: " + str(tool_messages))

  agent_response = client.chat(
    model='qwen3:1.7b',
    stream=False,
    tools=[tool_current_temperature, tool_latitude_longitude],
    messages=tool_messages)

  tool_calls = agent_response.message.tool_calls

  print("agent_response: " + str(agent_response))
  print("content: " + agent_response.message.content)
