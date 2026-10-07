import os, json
from openai import OpenAI
def get_weather(city):
    return "南昌今天25℃，小雨" if city == "南昌" else "当前只能查询南昌天气"
def calculate(a, b):
    return a + b
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询城市天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算两个数字的和",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    }
]
functions = {
    "get_weather": get_weather,
    "calculate": calculate
}
messages = [
    {"role": "system", "content": "你是一个可以调用工具的助手"}
]
while True:
    user_input = input("你：")
    if user_input == "退出":
        break
    messages.append({
        "role": "user",
        "content": user_input
    })
    # 第一次问 LLM
    msg = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        tools=tools
    ).choices[0].message
    while msg.tool_calls:
        call = msg.tool_calls[0]
        args = json.loads(call.function.arguments)
        result = functions[call.function.name](**args)
        messages.append(msg)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": str(result)
        })
        msg = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            tools=tools
        ).choices[0].message
    print("Agent：", msg.content)
    messages.append({
        "role": "assistant",
        "content": msg.content
    })