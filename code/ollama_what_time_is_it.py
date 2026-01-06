#pip install ollama

import json

from datetime import datetime

from ollama import chat
from ollama import Client
from ollama import ChatResponse


# Here is an example of tool calling from the official ollama website:
# https://docs.ollama.com/capabilities/tool-calling

client = Client(
  host='http://ollama:11434'
)

chat_model = "qwen3:1.7b"

def current_time() -> str:
  return datetime.now()


tool_current_time = {
  'type':'function',
  'function':{
    'name': 'current_time',
    'description': 'Current local time'
  }}


prompt = '''You are an assistant with access to tools, you must decide when to use tools to answer user message.
            
            Please don't be too chatty with the end user.'''
query = '''What time is it?'''

messages = [{"role":"system", "content":prompt},
  {"role":"user", "content":query}]

agent_response = client.chat(
  model=chat_model,
  stream=False,
  tools=[tool_current_time],
  messages=messages)

print("agent_response: " + str(agent_response))

dic_tools = {'current_time':current_time}

if agent_response.message.tool_calls:
  for tool in agent_response.message.tool_calls:

    t_name = tool["function"]["name"]
    print(t_name)
    t_inputs = tool["function"]["arguments"]
    print(t_inputs)

    if f := dic_tools.get(t_name):
      #messages.append( {"role":"user", "content":"use tool '"+t_name+"' with inputs: "+str(t_inputs)} )
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
