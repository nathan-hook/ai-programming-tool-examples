# CURL Example, What temperature is it?  With Inner Thougths

This example shows the usage of having an initial tool call with a second and third call to an LLM with the tool's results.

This example adds tool parameters for gathering the LLMs reasoning and confidence for why it wants to call a tool.

This is important and needed for future use when we need to debug why a tool was called.

## What temperatureIs It?  With Inner Thoughts

### Initial Request
```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3:1.7b",
  "messages": [
    {"role": "system", "content": "You are an assistant with access to tools, you must decide when to use tools to answer user message."},
    {"role": "user", "content": "What is the temperature in Boulder?"}
  ],
  "stream": false,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "current_temperature_lat_long",
        "description": "Current temperature for the given location",
        "parameters":{
          "type": "object",
          "required": [
            "latitude",
            "longitude",
            "innerthoughts",
            "confidence",
            "memorynotes"
          ],
          "properties": {
            "latitude": {
              "type": "float",
              "description": "the latitude of the location to get the current temperature for"
            },
            "logitude": {
              "type": "float",
              "description": "the longitude of the location to get the current temperature for"
            },
            "innerthoughts": {
              "type": "string",
              "description": "Your step-by-step reasoning for why you are calling this tool and what you expect"
            },
            "confidence": {
              "type": "string",
              "description": "Confidence level (low, medium, high) in this tool choice"
            },
            "memorynotes":{
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Key insights to remember for future interactions"
            }
          }
        }
      }
    },
    {
      "type":"function",
      "function": {
        "name": "latitude_longitude",
        "description": "Latitude and longitude for the given location",
        "parameters": {
          "type": "object",
          "required": [
            "location",
            "innerthoughts",
            "confidence",
            "memorynotes"
          ],
          "properties": {
            "location": {
              "type": "str",
              "description": "the name of the location to get the latitude and longitude for"
            },
            "innerthoughts": {
              "type": "string",
              "description": "Your step-by-step reasoning for why you are calling this tool and what you expect"
            },
            "confidence": {
              "type": "string",
              "description": "Confidence level (low, medium, high) in this tool choice"
            },
            "memorynotes": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Key insights to remember for future interactions"
            }
          }
        }
      }
    }
  ]
}'
```

### Initial Response with tool_calls
```
{
  "model":"qwen3:1.7b",
  "created_at":"2026-01-06T16:29:23.630746799Z",
  "message":{
    "role":"assistant",
    "content":"\u003cthink\u003e\nOkay, the user is asking for the weather in Boulder. Let me see how to approach this.\n\nFirst, I need to determine the latitude and longitude of Boulder. The user didn't specify a particular date, so I'll assume they want the current weather. The tools available include a function called latitude_longitude, which gives the latitude and longitude for a given location. Another tool, current_temperature_lat_long, provides the current temperature based on latitude and longitude. \n\nBut wait, the latitude_longitude function requires the location name, which the user provided (Boulder). So I should use that first to get the coordinates. Once I have the latitude and longitude, I can then use the current_temperature_lat_long function to check the temperature. \n\nHowever, the user's question is about the weather, which includes temperature, but maybe they just want the temperature. But since the tools are available, I should check if the latitude_longitude function can provide the coordinates, and then use the other tool to get the temperature. \n\nSo the steps are: call latitude_longitude with location \"Boulder\" to get the coordinates, then use current_temperature_lat_long with the obtained coordinates to get the temperature. \n\nBut the user might not know the coordinates, so I need to first get the coordinates. Therefore, the first tool call should be latitude_longitude with location Boulder. Then, once I have the coordinates, I can call the current_temperature_lat_long function with those coordinates. \n\nWait, the user's question is \"What is the weather in Boulder?\" So I need to provide the current temperature. But the tools require me to first get the coordinates. So I need to call latitude_longitude first to get the coordinates, then use the current_temperature_lat_long with those coordinates. \n\nSo the assistant should first call latitude_longitude with Boulder as the location. Then, once the coordinates are obtained, call the current_temperature_lat_long function with those coordinates. \n\nBut the assistant can only make one tool call at a time. So in this case, the assistant needs to first call latitude_longitude to get the coordinates, then in the next step, call the current_temperature_lat_long. However, since the user's question is a single query, the assistant might need to make two tool calls. But according to the instructions, the assistant can call one or more functions. \n\nSo the first step is to call latitude_longitude with Boulder. Then, once the coordinates are known, call current_temperature_lat_long with those coordinates. \n\nTherefore, the assistant should first make the latitude_longitude call.\n\u003c/think\u003e\n\n",
    "tool_calls":[
      {
        "function":{
          "name":"latitude_longitude",
          "arguments":{
            "confidence":"high",
            "innerthoughts":"First, I need to determine the latitude and longitude of Boulder to retrieve the current temperature.",
            "location":"Boulder",
            "memorynotes":[
              "Boulder is a city in Colorado",
              "Coordinates are essential for weather data"
            ]
          }
        }
      }
    ]
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":77301802869,
  "load_duration":119799959,
  "prompt_eval_count":429,
  "prompt_eval_duration":118084333,
  "eval_count":594,
  "eval_duration":77062862952
}
```

### Second Request, Calling the latitude_longitude Function

The latitude_longitude function has it's own call to the LLM.

Important to note that thinking is turned off.

```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3:1.7b",
  "messages": [
    {"role": "system", "content": "You are an assistant that is an expert at geography.\\nHere is the end user'\''s query:\\n<QUERY>\\nBoulder\\n</QUERY>\\nYour job is to take the end user'\''s query and return a reasonable latitude and longitude point for that location.\\nWhen you receive the named location, assume it is a city, but if the query is specific, than use the more specific location.\\nHere is an example json response:\\n{\\n\"latitude\":decimal_latitude_value\\n\"longitude\":decimal_longitude_value\\n}\\nIf you cannot determine the location, return an empty json response."}
  ],
  "stream": false,
  "think": false
}'
```

### latitude_longitude Response with tool_calls
```
{
  "model":"qwen3:1.7b",
  "created_at":"2026-01-06T17:30:53.382238048Z",
  "message":{
    "role":"assistant",
    "content":"{\"latitude\": 39.7392, \"longitude\": -104.9845}"
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":2236253542,
  "load_duration":74754833,
  "prompt_eval_count":134,
  "prompt_eval_duration":997239501,
  "eval_count":26,
  "eval_duration":1163730209
}
```

### Third Request, Amended with the Tool Output
```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model":"qwen3:1.7b",
  "messages":[
    {
      "role":"system",
      "content":"You are an assistant with access to tools, you must decide when to use tools to answer user message."
    },
    {
      "role":"user",
      "content":"What is the temperature in Boulder?"
    },
    {
      "role":"assistant",
      "tool_calls":[
        {
          "type":"function",
          "function":{
            "index":0,
            "name":"latitude_longitude",
            "arguments":{
              "location":"Boulder"
            }
          }
        }
      ]
    },
    {
      "role":"tool",
      "tool_name":"current_temperature",
      "content":"{\n  \"latitude\": 39.7392,\n  \"longitude\": -104.9847\n}"
    }
  ],
  "stream":false,
  "tools":[
    {
      "type":"function",
      "function":{
        "name":"current_temperature_lat_long",
        "description":"Current temperature for the given location",
        "parameters":{
          "type":"object",
          "required":[
            "latitude",
            "longitude",
            "innerthoughts",
            "confidence",
            "memorynotes"
          ],
          "properties":{
            "latitude":{
              "type":"float",
              "description":"the latitude of the location to get the current temperature for"
            },
            "logitude":{
              "type":"float",
              "description":"the longitude of the location to get the current temperature for"
            },
            "innerthoughts":{
              "type":"string",
              "description":"Your step-by-step reasoning for why you are calling this tool and what you expect"
            },
            "confidence":{
              "type":"string",
              "description":"Confidence level (low, medium, high) in this tool choice"
            },
            "memorynotes":{
              "type":"array",
              "items":{
                "type":"string"
              },
              "description":"Key insights to remember for future interactions"
            }
          }
        }
      }
    },
    {
      "type":"function",
      "function":{
        "name":"latitude_longitude",
        "description":"Latitude and longitude for the given location",
        "parameters":{
          "type":"object",
          "required":[
            "location",
            "innerthoughts",
            "confidence",
            "memorynotes"
          ],
          "properties":{
            "location":{
              "type":"str",
              "description":"the name of the location to get the latitude and longitude for"
            },
            "innerthoughts":{
              "type":"string",
              "description":"Your step-by-step reasoning for why you are calling this tool and what you expect"
            },
            "confidence":{
              "type":"string",
              "description":"Confidence level (low, medium, high) in this tool choice"
            },
            "memorynotes":{
              "type":"array",
              "items":{
                "type":"string"
              },
              "description":"Key insights to remember for future interactions"
            }
          }
        }
      }
    }
  ]
}'
```

### Third Response with the Tool Output
```
{
  "model":"qwen3:1.7b",
  "created_at":"2026-01-06T19:23:33.834836928Z",
  "message":{
    "role":"assistant",
    "content":"\u003cthink\u003e\nOkay, the user asked for the temperature in Boulder. I first needed to find Boulder's latitude and longitude. I used the latitude_longitude function with \"Boulder\" as the location. The response gave me the coordinates: 39.7392 latitude and -104.9847 longitude. \n\nNow, I need to use the current_temperature_lat_long function with these coordinates. The parameters required are latitude, longitude, innerthoughts, confidence, and memorynotes. I'll make sure to include the provided latitude and longitude from the previous response. \n\nI should set the confidence level to high since the function is reliable. The innerthoughts should explain that I'm using the coordinates to fetch the current temperature. The memorynotes can note that the coordinates were obtained from the latitude_longitude function. \n\nWait, the user didn't specify a date, so maybe the temperature is for the current day. I'll assume that and proceed. The function will return the temperature, which I can then present to the user.\n\u003c/think\u003e\n\n",
    "tool_calls":[
      {
        "function":{
          "name":"current_temperature_lat_long",
          "arguments":{
            "confidence":"high",
            "innerthoughts":"Using coordinates from previous lookup to fetch current temperature",
            "latitude":39.7392,
            "longitude":-104.9847,
            "memorynotes":[
              "Coordinates obtained from latitude_longitude function",
              "Assuming current day's temperature"
            ]
          }
        }
      }
    ]
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":117481913262,
  "load_duration":1432657918,
  "prompt_eval_count":491,
  "prompt_eval_duration":4154006001,
  "eval_count":299,
  "eval_duration":111855448510
}
```

### Forth Request, Amended with the Tool Output
```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model":"qwen3:1.7b",
  "messages":[
    {
      "role":"system",
      "content":"You are an assistant with access to tools, you must decide when to use tools to answer user message."
    },
    {
      "role":"user",
      "content":"What is the temperature in Boulder?"
    },
    {
      "role":"assistant",
      "tool_calls":[
        {
          "type":"function",
          "function":{
            "index":0,
            "name":"current_temperature_lat_long",
            "arguments":{
              "latitude": 40.0149,
              "longitude": -105.2705
            }
          }
        }
      ]
    },
    {
      "role":"tool",
      "tool_name":"current_temperature_lat_long",
      "content":"11.2°C"
    }
  ],
  "stream":false,
  "tools":[
    {
      "type":"function",
      "function":{
        "name":"current_temperature_lat_long",
        "description":"Current temperature for the given location",
        "parameters":{
          "type":"object",
          "required":[
            "latitude",
            "longitude",
            "innerthoughts",
            "confidence",
            "memorynotes"
          ],
          "properties":{
            "latitude":{
              "type":"float",
              "description":"the latitude of the location to get the current temperature for"
            },
            "logitude":{
              "type":"float",
              "description":"the longitude of the location to get the current temperature for"
            },
            "innerthoughts":{
              "type":"string",
              "description":"Your step-by-step reasoning for why you are calling this tool and what you expect"
            },
            "confidence":{
              "type":"string",
              "description":"Confidence level (low, medium, high) in this tool choice"
            },
            "memorynotes":{
              "type":"array",
              "items":{
                "type":"string"
              },
              "description":"Key insights to remember for future interactions"
            }
          }
        }
      }
    },
    {
      "type":"function",
      "function":{
        "name":"latitude_longitude",
        "description":"Latitude and longitude for the given location",
        "parameters":{
          "type":"object",
          "required":[
            "location",
            "innerthoughts",
            "confidence",
            "memorynotes"
          ],
          "properties":{
            "location":{
              "type":"str",
              "description":"the name of the location to get the latitude and longitude for"
            },
            "innerthoughts":{
              "type":"string",
              "description":"Your step-by-step reasoning for why you are calling this tool and what you expect"
            },
            "confidence":{
              "type":"string",
              "description":"Confidence level (low, medium, high) in this tool choice"
            },
            "memorynotes":{
              "type":"array",
              "items":{
                "type":"string"
              },
              "description":"Key insights to remember for future interactions"
            }
          }
        }
      }
    }
  ]
}'
```

### Forth Response with the Tool Output and Answer for End User
```
{
  "model":"qwen3:1.7b",
  "created_at":"2026-01-06T19:38:35.487154845Z",
  "message":{
    "role":"assistant",
    "content":"\u003cthink\u003e\nOkay, the user asked for the temperature in Boulder. I called the current_temperature_lat_long function with Boulder's coordinates. The response was 11.2°C. Now I need to present this answer clearly. Let me check if the coordinates were correct. Boulder's latitude is around 40.0149 and longitude -105.2705, which matches the input. The temperature seems reasonable for that area. I should state the temperature and maybe mention the coordinates to confirm. Also, keep it simple and straightforward.\n\u003c/think\u003e\n\nThe current temperature in Boulder is **11.2°C**. This corresponds to the coordinates approximately **40.0149° N, 105.2705° W**. Let me know if you need further details!"
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":11716715172,
  "load_duration":983399501,
  "prompt_eval_count":487,
  "prompt_eval_duration":4052640127,
  "eval_count":170,
  "eval_duration":6655524503
}
```