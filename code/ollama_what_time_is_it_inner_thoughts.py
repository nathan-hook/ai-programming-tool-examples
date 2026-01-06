#pip install ollama

import json

# Used to see the function called...
import inspect

from datetime import datetime

from ollama import chat
from ollama import Client
from ollama import ChatResponse


# Here is an example of tool calling from the official ollama website:
# https://docs.ollama.com/capabilities/tool-calling

client = Client(
  host='http://ollama:11434'
)

def current_time() -> str:
  return datetime.now()

tool_current_time = {
  'type':'function',
  'function':{
    'name': 'current_time',
    'description': 'Current local time',
    'parameters': {
      'type': 'object',
      'required': ['innerthoughts', 'confidence', 'memorynotes'],
      'properties': {
        'innerthoughts': {'type':'string', 'description':'Your step-by-step reasoning for why you are calling this tool and what you expect'},
        'confidence': {
          'type': 'string',
          'description': 'Confidence level (low, medium, high) in this tool choice'
        },
        'memorynotes': {
          'type': 'array',
          'items': { 'type': 'string' },
          'description': 'Key insights to remember for future interactions'
        }
      }
    }
  }}

def handle_tool_call(tool:dict) -> dict:

  t_name = tool["function"]["name"]
  t_inputs = tool["function"]["arguments"]

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
  
  return output_dict

prompt = '''You are an assistant with access to tools, you must decide when to use tools to answer user message.'''
query = '''What time is it?'''

messages = [{"role":"system", "content":prompt},
  {"role":"user", "content":query}]

agent_response = client.chat(
  model='qwen3:1.7b',
  stream=False,
  tools=[tool_current_time],
  messages=messages)

print("agent_response: " + str(agent_response))

dic_tools = {'current_time':current_time}

if agent_response.message.tool_calls:
  for tool in agent_response.message.tool_calls:

    output_dict = handle_tool_call(tool)
    print("output_dict: " + str(output_dict))

    t_name = tool["function"]["name"]
    print(t_name)
    t_inputs = tool["function"]["arguments"]
    print(t_inputs)

    if f := dic_tools.get(t_name):
      ### tool output
      t_output = f(**tool["function"]["arguments"])
      print(t_output)
      ### final response
      prompt = '''You are a concise assistant.'''
      tool_messages = [
        {"role":"system", "content": prompt},
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
        model='qwen3:1.7b',
        stream=False,
        messages=tool_messages)

      print("agent_response: " + str(agent_response))
      print("content: " + agent_response.message.content)
