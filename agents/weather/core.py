import json

from agents.shared.llm_client import client
from .prompts import SYSTEM_PROMPT
from .tools import weather_tools
from .handlers import get_weather

TOOL_FUNC_MAP = {
    "get_weather": get_weather,
}


def call_weather_agent(user_input: str) -> str:
    user_input_clean = user_input.strip()
    
    # 如果输入看起来像城市名称（短文本，没有问号等），直接调用工具
    # 这样可以避免模型不调用工具的问题
    is_likely_city = (
        len(user_input_clean) < 20 
        and "?" not in user_input_clean 
        and "？" not in user_input_clean
        and "天气" not in user_input_clean  # 如果包含"天气"，让模型处理
        and "温度" not in user_input_clean
        and "气温" not in user_input_clean
    )
    
    if is_likely_city:
        # 直接调用工具，不经过模型判断
        result = get_weather(user_input_clean)
        # 用工具结果让模型生成友好的回答
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"查询 {user_input_clean} 的天气"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "auto_call",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": json.dumps({"location": user_input_clean}, ensure_ascii=False)
                    }
                }]
            },
            {
                "role": "tool",
                "tool_call_id": "auto_call",
                "content": result
            }
        ]
        final_resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
        )
        return final_resp.choices[0].message.content or result
    
    # 对于更复杂的查询，让模型决定是否调用工具
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    # 第一次请求：让模型决定是否调用工具
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=weather_tools,
        tool_choice="auto",
    )
    message = response.choices[0].message

    # 没有调用工具，返回模型的回复
    if not getattr(message, "tool_calls", None):
        return message.content or ""

    # 记录工具调用请求
    messages.append(
        {
            "role": message.role,
            "content": message.content or "",
            "tool_calls": [tc.model_dump() for tc in message.tool_calls],
        }
    )

    # 执行工具
    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        func = TOOL_FUNC_MAP.get(func_name)
        if func is None:
            result = f"未找到名为 {func_name} 的工具。"
        else:
            result = func(**args)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
        )

    # 第二次请求：基于工具结果生成最终回答
    final_resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    return final_resp.choices[0].message.content or ""

