# SmartAssistantAgent

一个基于 DeepSeek API 的多 Agent 智能助手系统。

## 项目结构

```
SmartAssistantAgent/
├── agents/
│   ├── shared/                # 公共封装（LLM客户端、工具类型等）
│   │   └── llm_client.py
│   ├── weather/               # 天气 Agent
│   │   ├── prompts.py
│   │   ├── tools.py
│   │   ├── handlers.py
│   │   └── core.py
│   └── finance/               # 理财 Agent
│       ├── prompts.py
│       ├── tools.py
│       ├── handlers.py
│       └── core.py
├── config/
│   └── settings.py
├── main.py
├── requirements.txt
└── .env.example
```

## 安装

1. 克隆项目后，安装依赖：

```bash
pip install -r requirements.txt
```

2. 复制 `.env.example` 为 `.env`，并填入你的 API 密钥：

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件，填入：
- `DEEPSEEK_API_KEY`: 你的 DeepSeek API 密钥
- `DEEPSEEK_BASE_URL`: DeepSeek API 地址（默认 https://api.deepseek.com，支持自动切换）
- `WEATHER_API_KEY`: 天气 API 密钥（可选，用于真实天气查询）
- `WEATHER_API_TYPE`: 天气 API 类型（可选，默认 `tianapi`，可选值：`tianapi` 或 `qweather`）

**天气 API 配置说明：**

**天行数据 API（推荐，默认）：**
- 注册地址：https://www.tianapi.com/
- 获取 API KEY 后，在 `.env` 中设置：
  ```env
  WEATHER_API_KEY=你的天行数据API_KEY
  WEATHER_API_TYPE=tianapi
  ```
- 支持城市名称、城市ID、行政区划代码、IP地址查询
- 返回实时天气、温度范围、风向、湿度、空气质量等信息

**和风天气 API（可选）：**
- 注册地址：https://console.qweather.com
- 获取 API KEY 和 API Host 后，在 `.env` 中设置：
  ```env
  WEATHER_API_KEY=你的和风天气API_KEY
  WEATHER_API_HOST=你的API_HOST
  WEATHER_API_TYPE=qweather
  ```
- 每个项目都有独立的 API Host，需要在控制台的项目详情中获取

**注意**：
- `.env.example` 是模板文件，包含在版本控制中，不包含真实密钥
- `.env` 是实际配置文件，包含你的真实 API 密钥，**不会**被提交到版本控制（已在 `.gitignore` 中排除）

## 使用

运行主程序：

```bash
python main.py
```

然后根据提示选择不同的 Agent：
- 输入 `1` 使用天气查询 Agent
- 输入 `2` 使用理财小助手 Agent
- 输入 `exit` 退出程序

## 添加新 Agent

要添加新的 Agent（如 match、todo、chat），只需在 `agents/` 目录下创建新的子包，参考现有 Agent 的结构：

1. 创建 `agents/新agent名/` 目录
2. 创建 `__init__.py`、`prompts.py`、`tools.py`、`handlers.py`、`core.py`
3. 在 `main.py` 中添加对应的调用逻辑

## 功能说明

### 天气 Agent
- 支持查询城市天气信息
- 支持天行数据和和风天气两种 API（默认使用天行数据）
- 自动处理城市名称匹配（如"保定"、"保定市"）
- 返回实时天气、温度范围、风向风力、湿度、空气质量等信息
- 如果没有配置 API 密钥，会返回模拟数据

### 理财 Agent
- 帮助用户进行基础的理财规划
- 评估用户风险承受能力
- 生成资产配置方案
- 仅用于学习参考，不构成投资建议

