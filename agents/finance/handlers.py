from typing import Dict, List


def assess_risk_profile(
    age: int,
    income_level: str,
    investment_experience_years: int,
    max_drawdown_tolerance: str,
) -> Dict:
    score = 0

    # 年龄
    if age < 30:
        score += 30
    elif age < 45:
        score += 20
    else:
        score += 10

    # 收入
    income_level = income_level.lower()
    if income_level == "high":
        score += 30
    elif income_level == "medium":
        score += 20
    else:
        score += 10

    # 经验
    if investment_experience_years >= 5:
        score += 20
    elif investment_experience_years >= 2:
        score += 15
    elif investment_experience_years >= 1:
        score += 10
    else:
        score += 5

    # 回撤容忍
    try:
        tol = int(max_drawdown_tolerance.strip().replace("%", ""))
    except Exception:
        tol = 10

    if tol >= 30:
        score += 20
    elif tol >= 20:
        score += 15
    elif tol >= 10:
        score += 10
    else:
        score += 5

    if score >= 80:
        level = "aggressive"
    elif score >= 55:
        level = "balanced"
    else:
        level = "conservative"

    return {
        "risk_level": level,
        "score": score,
        "explanation": (
            f"综合打分 {score} 分，因此判断为 {level} 类型投资者（仅供参考）。"
        ),
    }


def generate_allocation_plan(
    risk_level: str,
    monthly_invest_amount: float,
) -> Dict:
    risk_level = risk_level.lower()

    if risk_level == "conservative":
        plan = [
            {"category": "现金及货币基金", "percent": 40},
            {"category": "债券基金", "percent": 40},
            {"category": "宽基指数基金", "percent": 20},
        ]
    elif risk_level == "balanced":
        plan = [
            {"category": "现金及货币基金", "percent": 20},
            {"category": "债券基金", "percent": 40},
            {"category": "宽基指数基金", "percent": 40},
        ]
    else:
        plan = [
            {"category": "现金及货币基金", "percent": 10},
            {"category": "债券基金", "percent": 20},
            {"category": "宽基指数基金", "percent": 70},
        ]

    for p in plan:
        p["amount"] = round(monthly_invest_amount * p["percent"] / 100, 2)

    return {
        "risk_level": risk_level,
        "monthly_invest_amount": monthly_invest_amount,
        "plan": plan,
    }

