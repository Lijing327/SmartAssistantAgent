import json

from agents.shared.llm_client import client
from .prompts import FINANCE_SYSTEM_PROMPT
from .tools import finance_tools
from .handlers import assess_risk_profile, generate_allocation_plan

FINANCE_TOOL_FUNC_MAP = {
    "assess_risk_profile": assess_risk_profile,
    "generate_allocation_plan": generate_allocation_plan,
}


def call_finance_agent(user_input: str) -> str:
    messages = [
        {"role": "system", "content": FINANCE_SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=finance_tools,
        tool_choice="auto",
    )
    message = response.choices[0].message

    if not getattr(message, "tool_calls", None):
        return message.content or ""

    messages.append(
        {
            "role": message.role,
            "content": message.content or "",
            "tool_calls": [tc.model_dump() for tc in message.tool_calls],
        }
    )

    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        func = FINANCE_TOOL_FUNC_MAP.get(func_name)
        if func is None:
            result = f"未找到名为 {func_name} 的工具。"
        else:
            result_obj = func(**args)
            result = json.dumps(result_obj, ensure_ascii=False)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
        )

    final_resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    return final_resp.choices[0].message.content or ""

