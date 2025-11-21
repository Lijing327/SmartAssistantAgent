finance_tools = [
    {
        "type": "function",
        "function": {
            "name": "assess_risk_profile",
            "description": (
                "根据用户的年龄、收入、投资经验和可承受最大回撤，评估用户的风险承受能力。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "age": {
                        "type": "integer",
                        "description": "用户年龄（岁）。"
                    },
                    "income_level": {
                        "type": "string",
                        "description": "收入水平：low / medium / high。"
                    },
                    "investment_experience_years": {
                        "type": "integer",
                        "description": "投资经验年数。"
                    },
                    "max_drawdown_tolerance": {
                        "type": "string",
                        "description": "可承受最大亏损比例，如 '10%'、'20%'。"
                    },
                },
                "required": [
                    "age",
                    "income_level",
                    "investment_experience_years",
                    "max_drawdown_tolerance",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_allocation_plan",
            "description": (
                "根据风险等级和每月可投资金额，生成简单的资产配置方案。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_level": {
                        "type": "string",
                        "description": "风险等级：conservative / balanced / aggressive。"
                    },
                    "monthly_invest_amount": {
                        "type": "number",
                        "description": "每月可投资金额（元）。"
                    },
                },
                "required": ["risk_level", "monthly_invest_amount"],
            },
        },
    },
]

