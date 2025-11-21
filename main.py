from agents.weather.core import call_weather_agent
from agents.finance.core import call_finance_agent


def main():
    print("=== SmartAssistantAgent 已启动 ===")
    print("1. 天气查询 Agent")
    print("2. 理财小助手 Agent")
    print("输入数字选择 Agent，输入 exit 退出。")

    while True:
        mode = input("\n请选择 Agent（1/2 或 exit）：").strip().lower()

        if mode in {"exit", "quit"}:
            print("再见～")
            break

        if mode not in {"1", "2"}:
            print("请输入 1 / 2 或 exit。")
            continue

        if mode == "1":
            print("\n【天气 Agent】已启动，输入城市相关问题，back 返回主菜单。")
            while True:
                user_input = input("你：")
                if user_input.strip().lower() in {"back", "exit", "quit"}:
                    print("返回主菜单。")
                    break
                reply = call_weather_agent(user_input)
                print("天气Agent：", reply)

        if mode == "2":
            print("\n【理财 Agent】已启动，可以跟我聊你的收入、风险偏好等，back 返回主菜单。")
            while True:
                user_input = input("你：")
                if user_input.strip().lower() in {"back", "exit", "quit"}:
                    print("返回主菜单。")
                    break
                reply = call_finance_agent(user_input)
                print("理财Agent：", reply)


if __name__ == "__main__":
    main()

