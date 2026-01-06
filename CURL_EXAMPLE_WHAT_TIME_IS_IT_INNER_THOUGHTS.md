# CURL Example, What Time is it?  With Inner Thougths

This example shows the usage of having an initial tool call with a second call to an LLM with the tool's results.

This example adds tool parameters for gathering the LLMs reasoning and confidence for why it wants to call a tool.

This is important and needed for future use when we need to debug why a tool was called.

## What Time Is It?  With Inner Thoughts

### Initial Request
```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3:1.7b",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What time is it?"}
  ],
  "stream": false,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "current_time",
        "description": "Get the current time in UTC from the server.",
        "parameters": {
          "type": "object",
          "required": ["innerthoughts", "confidence", "memorynotes"],
          "properties": {
            "innerthoughts": {
              "type": "string",
              "description": "Your step-by-step reasoning for why you are calling this tool and what you expect"},
            "confidence": {
              "type": "string",
              "description": "Confidence level (low, medium, high) in this tool choice"},
            "memorynotes": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Key insights to remember for future interactions"}
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
  "created_at":"2026-01-06T15:39:39.740106959Z",
  "message":{
    "role":"assistant",
    "content":"\u003cthink\u003e\nOkay, the user is asking, \"What time is it?\" I need to figure out what to do. Let me check the tools available. There's a function called current_time that gets the current time in UTC from the server. The parameters required are innerthoughts, confidence, and memorynotes. \n\nWait, the user just wants the current time. So I should call the current_time function. But how do I structure the tool call? The function's parameters are innerthoughts, confidence, and memorynotes. I need to fill those in. \n\nInnerthoughts should explain my reasoning. Since the user is asking for the current time, I need to mention that I'm using the current_time function. Confidence level should be high because I'm directly answering the question. Memorynotes would include the key insight that the function is used to get the current time.\n\nSo the tool call would have the name as current_time and the arguments with innerthoughts, confidence, and memorynotes. I need to make sure the JSON is correctly formatted. Let me check the parameters again. The memorynotes is an array of strings, so I can add a single string there. \n\nPutting it all together, the tool call should include the function name, arguments with the necessary parameters. I think that's all. The user will get the current time from the server once the function is called.\n\u003c/think\u003e\n\n",
    "tool_calls":[
      {
        "function":{
          "name":"current_time",
          "arguments":{
            "confidence":"high",
            "innerthoughts":"Calling the current_time function to retrieve the current UTC time from the server.",
            "memorynotes":[
              "The function will return the current UTC time",
              "Result will be displayed to the user"
            ]
          }
        }
      }
    ]
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":14496581131,
  "load_duration":75005000,
  "prompt_eval_count":222,
  "prompt_eval_duration":1288942375,
  "eval_count":348,
  "eval_duration":13131789839
}
```

### Second Request Amended with the Tool Output
```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3:1.7b",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What time is it?"},
    {"role": "assistant", 
      "tool_calls": [
        {"type": "function",
         "function": {
            "index": 0,
            "name": "current_time",
            "arguments": {}
            }
        }]
    },
    {"role": "tool", "tool_name": "current_time", "content": "2025-11-24 17:32:19.207068"}],
  "stream": false,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "current_time",
        "description": "Get the current time in UTC from the server.",
        "parameters": {
          "type": "object",
          "required": ["innerthoughts", "confidence", "memorynotes"],
          "properties": {
            "innerthoughts": {
              "type": "string",
              "description": "Your step-by-step reasoning for why you are calling this tool and what you expect"},
            "confidence": {
              "type": "string",
              "description": "Confidence level (low, medium, high) in this tool choice"},
            "memorynotes": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Key insights to remember for future interactions"}
          }
        }
      }
    }
  ]
}'
```

### Second Response with Answer for End User
```
{
  "model":"qwen3:1.7b",
  "created_at":"2026-01-06T15:44:10.574356168Z",
  "message":{
    "role":"assistant",
    "content":"\u003cthink\u003e\nOkay, the user asked, \"What time is it?\" I need to provide the current time in UTC. The tool called current_time was used, and the response was 2025-11-24 17:32:19.207068. Let me check if that's correct. The date is November 24th, 2025, and the time is 5:32 PM. Since the user didn't specify a particular time zone, the UTC time is already provided. I should present this information clearly. Maybe start by confirming the date and time, then state the UTC time. Make sure to format it in a friendly manner. Also, check if there's any additional information needed, but the user only asked for the time, so a straightforward answer should be fine.\n\u003c/think\u003e\n\nThe current time in UTC is **November 24, 2025, at 5:32 PM**. Let me know if you need further assistance!"
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":7981351545,
  "load_duration":87778417,
  "prompt_eval_count":277,
  "prompt_eval_duration":446778417,
  "eval_count":215,
  "eval_duration":7445312169
}
```