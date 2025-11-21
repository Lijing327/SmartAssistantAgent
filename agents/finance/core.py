import json

from agents.shared.llm_client import client
from .prompts import FINANCE_SYSTEM_PROMPT
from .tools import finance_tools
from .handlers import assess_risk_profile, generate_allocation_plan

FINANCE_TOOL_FUNC_MAP = {
    "assess_risk_profile": assess_risk_profile,
    "generate_allocation_plan": generate_allocation_plan,
}


# 维护对话历史（简单版本，实际应用中可以使用更复杂的会话管理）
_conversation_history = []


def _extract_user_info(conversation_history):
    """从对话历史中提取用户信息"""
    import re
    
    user_info = {
        "age": None,
        "income_level": None,
        "investment_experience_years": None,
        "max_drawdown_tolerance": None,
        "monthly_invest_amount": None,
    }
    
    # 合并所有用户输入
    all_user_input = " ".join([
        msg.get("content", "") 
        for msg in conversation_history 
        if msg.get("role") == "user"
    ])
    
    # 提取年龄
    age_match = re.search(r'(\d+)\s*岁', all_user_input)
    if age_match:
        user_info["age"] = int(age_match.group(1))
    
    # 提取收入水平
    if re.search(r'年收入\s*10\s*w|年薪\s*10\s*万|10\s*万年薪|中等收入|中等', all_user_input, re.I):
        user_info["income_level"] = "medium"
    elif re.search(r'低收入|月收入\s*5000\s*以下', all_user_input, re.I):
        user_info["income_level"] = "low"
    elif re.search(r'高收入|月收入\s*15000\s*以上', all_user_input, re.I):
        user_info["income_level"] = "high"
    
    # 提取投资经验
    if re.search(r'没有.*经验|没有投资|0\s*年', all_user_input, re.I):
        user_info["investment_experience_years"] = 0
    else:
        exp_match = re.search(r'(\d+)\s*年.*经验', all_user_input)
        if exp_match:
            user_info["investment_experience_years"] = int(exp_match.group(1))
    
    # 提取风险承受
    if re.search(r'较小.*亏损|10\s*%|能接受\s*10\s*%', all_user_input, re.I):
        user_info["max_drawdown_tolerance"] = "10%"
    else:
        tol_match = re.search(r'(\d+)\s*%', all_user_input)
        if tol_match:
            user_info["max_drawdown_tolerance"] = f"{tol_match.group(1)}%"
    
    # 提取每月投资金额
    if re.search(r'1\s*k|1000|每月\s*1\s*k|每月\s*1000', all_user_input, re.I):
        user_info["monthly_invest_amount"] = 1000
    else:
        amount_match = re.search(r'每月.*?(\d+)\s*[元块]', all_user_input)
        if amount_match:
            user_info["monthly_invest_amount"] = float(amount_match.group(1))
    
    return user_info


def _format_finance_result(risk_assessment, allocation_plan):
    """格式化理财规划结果"""
    if allocation_plan:
        plan = allocation_plan["plan"]
        risk_level = allocation_plan.get("risk_level", "balanced")
        monthly_amount = allocation_plan.get("monthly_invest_amount", 0)
        
        risk_level_map = {
            "conservative": "保守型",
            "balanced": "平衡型",
            "aggressive": "激进型"
        }
        risk_level_cn = risk_level_map.get(risk_level, risk_level)
        
        result = f"""根据您的风险承受能力评估，您属于【{risk_level_cn}】投资者。

📊 资产配置方案（每月投资 {monthly_amount} 元）：

"""
        for item in plan:
            result += f"• {item['category']}：{item['percent']}%（每月约 {item['amount']} 元）\n"
        
        result += f"""

💡 方案说明：
- 此方案基于您的风险承受能力（{risk_level_cn}）制定
- 建议采用定投方式，长期坚持
- 可根据市场情况和个人需求适当调整

⚠️ 风险提示：
- 投资有风险，入市需谨慎
- 本方案仅供参考，不构成投资建议
- 请根据自身情况谨慎决策"""
        
        return result
    
    return ""


def call_finance_agent(user_input: str) -> str:
    # 将用户输入添加到对话历史
    _conversation_history.append({"role": "user", "content": user_input})
    
    # 尝试从对话历史中提取用户信息
    user_info = _extract_user_info(_conversation_history)
    
    # 检查信息完整度，如果信息足够（至少3个），就可以给出建议
    info_count = sum(1 for v in user_info.values() if v is not None)
    has_enough_info = info_count >= 3  # 至少需要3个信息就可以给出建议
    
    # 如果信息足够，直接调用工具（使用默认值填充缺失信息）
    if has_enough_info:
        # 为缺失的信息设置默认值
        if user_info["age"] is None:
            user_info["age"] = 30  # 默认年龄
        if user_info["income_level"] is None:
            user_info["income_level"] = "medium"  # 默认中等收入
        if user_info["investment_experience_years"] is None:
            user_info["investment_experience_years"] = 0  # 默认无经验
        if user_info["max_drawdown_tolerance"] is None:
            user_info["max_drawdown_tolerance"] = "10%"  # 默认10%
        if user_info["monthly_invest_amount"] is None:
            user_info["monthly_invest_amount"] = 1000  # 默认1000元
        # 先评估风险
        risk_assessment = assess_risk_profile(
            age=user_info["age"],
            income_level=user_info["income_level"],
            investment_experience_years=user_info["investment_experience_years"],
            max_drawdown_tolerance=user_info["max_drawdown_tolerance"],
        )
        
        # 再生成资产配置方案
        allocation_plan = generate_allocation_plan(
            risk_level=risk_assessment["risk_level"],
            monthly_invest_amount=user_info["monthly_invest_amount"],
        )
        
        # 格式化结果
        result = _format_finance_result(risk_assessment, allocation_plan)
        
        # 用模型生成更友好的回答
        messages = [
            {"role": "system", "content": FINANCE_SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "auto_assess",
                        "type": "function",
                        "function": {
                            "name": "assess_risk_profile",
                            "arguments": json.dumps({
                                "age": user_info["age"],
                                "income_level": user_info["income_level"],
                                "investment_experience_years": user_info["investment_experience_years"],
                                "max_drawdown_tolerance": user_info["max_drawdown_tolerance"],
                            }, ensure_ascii=False)
                        }
                    },
                    {
                        "id": "auto_plan",
                        "type": "function",
                        "function": {
                            "name": "generate_allocation_plan",
                            "arguments": json.dumps({
                                "risk_level": risk_assessment["risk_level"],
                                "monthly_invest_amount": user_info["monthly_invest_amount"],
                            }, ensure_ascii=False)
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "tool_call_id": "auto_assess",
                "content": json.dumps(risk_assessment, ensure_ascii=False)
            },
            {
                "role": "tool",
                "tool_call_id": "auto_plan",
                "content": json.dumps(allocation_plan, ensure_ascii=False)
            }
        ]
        
        final_resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
        )
        final_message = final_resp.choices[0].message.content or result
        
        # 如果模型回答为空或太短，使用格式化结果
        if not final_message or len(final_message.strip()) < 50:
            final_message = result
        
        _conversation_history.append({"role": "assistant", "content": final_message})
        return final_message
    
    # 如果信息不足，让模型继续询问
    messages = [
        {"role": "system", "content": FINANCE_SYSTEM_PROMPT},
    ] + _conversation_history[-10:]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=finance_tools,
        tool_choice="auto",
    )
    message = response.choices[0].message

    # 将助手回复添加到对话历史
    if message.content:
        _conversation_history.append({"role": "assistant", "content": message.content})

    if not getattr(message, "tool_calls", None):
        return message.content or ""

    # 记录工具调用
    tool_call_message = {
        "role": message.role,
        "content": message.content or "",
        "tool_calls": [tc.model_dump() for tc in message.tool_calls],
    }
    messages.append(tool_call_message)
    _conversation_history.append(tool_call_message)

    # 执行工具调用
    tool_results_data = []  # 保存工具结果，用于后续格式化
    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        func = FINANCE_TOOL_FUNC_MAP.get(func_name)
        if func is None:
            result = f"未找到名为 {func_name} 的工具。"
        else:
            result_obj = func(**args)
            result = json.dumps(result_obj, ensure_ascii=False)
            tool_results_data.append(result_obj)  # 保存结果对象

        tool_result = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        }
        messages.append(tool_result)
        _conversation_history.append(tool_result)

    # 生成最终回答
    final_resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    final_message = final_resp.choices[0].message.content or ""
    
    # 清理工具调用标记（如果存在）
    if final_message:
        import re
        # 移除工具调用相关的标记
        final_message = re.sub(r'<\|redacted_tool_calls.*?\|>', '', final_message, flags=re.DOTALL)
        final_message = re.sub(r'<\|.*?\|>', '', final_message, flags=re.DOTALL)
        final_message = final_message.strip()
    
    # 如果最终回答为空、太短或包含工具调用标记，从工具结果中生成详细回答
    should_use_fallback = (
        not final_message or 
        len(final_message.strip()) < 50 or 
        'tool_call' in final_message.lower() or
        'redacted' in final_message.lower()
    )
    
    if should_use_fallback:
        # 优先使用保存的工具结果对象
        risk_assessment = None
        allocation_plan = None
        
        for result_obj in tool_results_data:
            if "plan" in result_obj:
                allocation_plan = result_obj
            elif "risk_level" in result_obj and "plan" not in result_obj:
                risk_assessment = result_obj
        
        # 如果工具结果对象中没有，再从 messages 中提取
        if not allocation_plan and not risk_assessment:
            tool_results = [msg for msg in messages if msg.get("role") == "tool"]
            for tool_result in tool_results:
                try:
                    result_data = json.loads(tool_result.get("content", "{}"))
                    if "plan" in result_data:
                        allocation_plan = result_data
                    elif "risk_level" in result_data:
                        risk_assessment = result_data
                except Exception:
                    continue
        
        # 生成详细的回答
        if allocation_plan:
            plan = allocation_plan["plan"]
            risk_level = allocation_plan.get("risk_level", "balanced")
            monthly_amount = allocation_plan.get("monthly_invest_amount", 0)
            
            # 风险等级中文映射
            risk_level_map = {
                "conservative": "保守型",
                "balanced": "平衡型",
                "aggressive": "激进型"
            }
            risk_level_cn = risk_level_map.get(risk_level, risk_level)
            
            final_message = f"""根据您的风险承受能力评估，您属于【{risk_level_cn}】投资者。

📊 资产配置方案（每月投资 {monthly_amount} 元）：

"""
            for item in plan:
                final_message += f"• {item['category']}：{item['percent']}%（每月约 {item['amount']} 元）\n"
            
            final_message += f"""

💡 方案说明：
- 此方案基于您的风险承受能力（{risk_level_cn}）制定
- 建议采用定投方式，长期坚持
- 可根据市场情况和个人需求适当调整

⚠️ 风险提示：
- 投资有风险，入市需谨慎
- 本方案仅供参考，不构成投资建议
- 请根据自身情况谨慎决策"""
        
        elif risk_assessment:
            risk_level = risk_assessment.get("risk_level", "balanced")
            score = risk_assessment.get("score", 0)
            explanation = risk_assessment.get("explanation", "")
            
            risk_level_map = {
                "conservative": "保守型",
                "balanced": "平衡型",
                "aggressive": "激进型"
            }
            risk_level_cn = risk_level_map.get(risk_level, risk_level)
            
            final_message = f"""✅ 风险评估完成

{explanation}

风险等级：{risk_level_cn}（评分：{score}分）

请继续提供每月可投资金额，我将为您生成具体的资产配置方案。"""
        
        if not final_message:
            final_message = "已为您完成评估，请查看上述配置方案。"
    
    # 将最终回答添加到对话历史
    _conversation_history.append({"role": "assistant", "content": final_message})
    
    return final_message

