weather_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "根据城市名称查询当前天气信息。用户需要先提供城市名称。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市名称，例如：'Beijing' 或 'Shanghai' 等。",
                    }
                },
                "required": ["location"],
            },
        },
    },
]

