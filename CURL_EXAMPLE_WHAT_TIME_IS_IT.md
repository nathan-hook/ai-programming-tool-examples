# CURL Example, What Time is it?

This example shows the usage of having an initial tool call with a second call to an LLM with the tool's results.

## What Time Is It?

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
        "parameters": {}
      }
    }
  ]
}'
```

### Initial Response with tool_calls
```
{
  "model":"qwen3:1.7b",
  "created_at":"2025-12-08T19:10:50.931696511Z",
  "message":{
    "role":"assistant",
    "content":"\u003cthink\u003e\nOkay, the user is asking, \"What time is it?\" I need to figure out the current time in UTC. Let me check the tools provided. There's a function called current_time that gets the current time in UTC from the server. The parameters section says it's optional with no required fields. So I should call that function. I don't need any arguments because the function doesn't require them. Just invoke current_time without any parameters. Then wait for the response to give the time.\n\u003c/think\u003e\n\n",
    "tool_calls":[
      {
        "function":{
          "name":"current_time",
          "arguments":{
            
          }
        }
      }
    ]
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":10590579505,
  "load_duration":2663247543,
  "prompt_eval_count":141,
  "prompt_eval_duration":1453118626,
  "eval_count":120,
  "eval_duration":6451149170
}
```

# Second Request Amended with the Tool Output
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
  "stream": false
}'
```

### Second Response with Answer for End User
```
{
  "model":"qwen3:1.7b",
  "created_at":"2025-12-08T19:13:38.095174047Z",
  "message":{
    "role":"assistant",
    "content":"\u003cthink\u003e\nOkay, the user asked, \"What time is it?\" I need to provide the current time. The assistant responded with the timestamp 2025-11-24 17:32:19.207068. Wait, 2025? That's a future year. Maybe there's a mistake here. Let me check the system time. If the current date is 2025, then the answer is correct. But if the system is set to a different date, like 2024, then the response would be wrong. However, the user's message was generated in 2025, so the assistant's response is accurate. I should inform the user that the current time is 2025-11-24 17:32:19.207068, but note that it's a future date. Maybe the user is testing if I can handle a future date or there's an error in the system time. I should clarify that the time is as given, even though it's in the future.\n\u003c/think\u003e\n\nThe current time is **2025-11-24 17:32:19.207068**. Note that this is a future date, as the system time appears to be set to 2025. Let me know if you'd like to verify the actual current date!"
  },
  "done":true,
  "done_reason":"stop",
  "total_duration":18318640216,
  "load_duration":69093500,
  "prompt_eval_count":79,
  "prompt_eval_duration":724551292,
  "eval_count":309,
  "eval_duration":17521849466
}
```