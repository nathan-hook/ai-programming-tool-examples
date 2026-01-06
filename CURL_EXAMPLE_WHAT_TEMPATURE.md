# CURL Example, What Time is it?

This example shows the usage of having an initial tool call with a second call to an LLM with the tool's results.

## What Is The temperature In Boulder?

### Initial Request
```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3:1.7b",
  "messages": [{"role": "user", "content": "What is the temperature in Boulder, Colorado?"}],
  "stream": false,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_temperature",
        "description": "Get the current temperature for a city",
        "parameters": {
          "type": "object",
          "required": ["city"],
          "properties": {
            "city": {"type": "string", "description": "The name of the city"}
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
  "created_at":"2025-12-08T19:21:56.714367375Z",
  "message":{
    "role":"assistant",
    "content":"\u003cthink\u003e\nOkay, the user is asking for the temperature in Boulder, Colorado. Let me check the tools available. There's a function called get_temperature that takes a city parameter. The required parameter is city, which should be a string. So I need to call this function with the city set to \"Boulder, Colorado\". I should make sure the arguments are in JSON format. Let me structure the tool call correctly. The function name is get_temperature, and the arguments should be {\"city\": \"Boulder, Colorado\"}. I'll wrap that in the tool_call tags as specified.\n\u003c/think\u003e\n\n",
    "tool_calls":[
      {
        "function":{
          "name":"get_temperature",
          "arguments":{
            "city":"Boulder, Colorado"
          }
        }
      }
    ]
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":11442915463,
  "load_duration":2372844710,
  "prompt_eval_count":152,
  "prompt_eval_duration":1493105209,
  "eval_count":144,
  "eval_duration":7576258503
}
```

### Second Request Amended with the Tool Output
```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3:1.7b",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the temperature in Boulder, Colorado?"},
    {"role": "assistant", 
      "tool_calls": [
        {"type": "function",
         "function": {
            "index": 0,
            "name": "current_temperature",
            "arguments": {
              "city":"Boulder, Colorado"
            }}
        }]
    },
    {"role": "tool", "tool_name": "current_temperature", "content": "14.8°C"}],
  "stream": false
}'
```

### Second Response with Answer for End User
```
{
  "model":"qwen3:1.7b",
  "created_at":"2025-12-08T19:24:50.304851011Z",
  "message":{
    "role":"assistant",
    "content":"\u003cthink\u003e\nOkay, the user asked for the temperature in Boulder, Colorado. I need to check the current temperature. Let me see, the previous response was 14.8°C. Wait, but I should make sure that's the latest data. Maybe the temperature has changed since then. Hmm, but the user didn't specify a time frame, so I'll go with the most recent available. I should present the answer clearly, stating the temperature and the city. Also, maybe add a note that it's the current temperature. Let me check if there's any recent update. Oh, the system message says to provide the answer based on the previous response. So I'll stick with 14.8°C. Alright, I'll format the response properly.\n\u003c/think\u003e\n\nThe current temperature in Boulder, Colorado is **14.8°C**. Let me know if you'd like a weather forecast or additional details! 🌞"
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":10103353922,
  "load_duration":75269125,
  "prompt_eval_count":70,
  "prompt_eval_duration":679722834,
  "eval_count":191,
  "eval_duration":9326556712
}
```
