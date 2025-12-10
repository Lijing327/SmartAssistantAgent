# SmartAssistantAgent 项目梳理文档

> 本文档用于全面梳理项目当前状态，便于 ChatGPT 或其他开发者快速了解项目情况。

---

## 📋 项目概述

**SmartAssistantAgent** 是一个基于 DeepSeek API 的多 Agent 智能助手系统。项目采用模块化设计，支持多个独立的智能 Agent，每个 Agent 专注于特定领域（如天气查询、理财规划等）。

### 核心特点
- ✅ **多 Agent 架构**：每个 Agent 独立运行，互不干扰
- ✅ **工具调用（Tool Calling）**：Agent 可以调用外部工具获取实时数据
- ✅ **智能 LLM 客户端**：支持自动切换 API 端点、代理配置、错误重试
- ✅ **对话历史管理**：支持上下文记忆，提供连贯的对话体验
- ✅ **灵活配置**：通过 `.env` 文件管理所有配置项
[3.py](../../../../Users/YH/Documents/xwechat_files/wxid_bra6g5iibv9n21_6cf0/msg/file/2025-12/3.py)
---

## 🛠️ 技术栈

| 技术 | 版本/说明 | 用途 |
|------|----------|------|
| **Python** | 3.x | 主要开发语言 |
| **openai** | 最新版 | DeepSeek API 客户端（兼容 OpenAI 格式） |
| **httpx** | 最新版 | HTTP 客户端，用于 API 请求 |
| **requests** | 最新版 | 同步 HTTP 请求（天气 API） |
| **python-dotenv** | 最新版 | 环境变量管理 |

---

## 📁 项目结构

```
SmartAssistantAgent/
├── agents/                          # Agent 模块目录
│   ├── __init__.py
│   ├── shared/                      # 共享模块
│   │   ├── __init__.py
│   │   └── llm_client.py           # 智能 LLM 客户端（核心）
│   ├── weather/                     # 天气查询 Agent
│   │   ├── __init__.py
│   │   ├── prompts.py              # 系统提示词
│   │   ├── tools.py                # 工具定义（OpenAI 格式）
│   │   ├── handlers.py             # 工具实现（实际 API 调用）
│   │   └── core.py                 # Agent 核心逻辑
│   └── finance/                     # 理财规划 Agent
│       ├── __init__.py
│       ├── prompts.py              # 系统提示词
│       ├── tools.py                # 工具定义
│       ├── handlers.py             # 工具实现（风险评估、资产配置）
│       └── core.py                 # Agent 核心逻辑（含对话历史）
│
├── config/                          # 配置模块
│   ├── __init__.py
│   └── settings.py                 # 环境变量加载与配置管理
│
├── main.py                          # 主程序入口
├── requirements.txt                 # Python 依赖
├── .env.example                     # 环境变量模板
├── .gitignore                      # Git 忽略文件
└── README.md                        # 项目说明文档
```

---

## 🔧 核心模块详解

### 1. **LLM 客户端** (`agents/shared/llm_client.py`)

**功能**：封装 DeepSeek API 调用，提供智能重试和端点切换。

**核心特性**：
- ✅ **自动端点切换**：连接失败时自动在 `.cn` 和 `.com` 之间切换
- ✅ **代理支持**：支持 HTTP/HTTPS 代理配置（VPN 友好）
- ✅ **错误处理**：捕获网络错误并自动重试
- ✅ **超时控制**：30 秒超时设置

**关键类**：
- `SmartOpenAIClient`：智能客户端主类
- `SmartChatCompletions`：聊天完成接口封装
- `SmartCompletions`：实际 API 调用封装

**使用方式**：
```python
from agents.shared.llm_client import client

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    tools=[...],
)
```

---

### 2. **配置管理** (`config/settings.py`)

**功能**：统一管理所有环境变量和配置项。

**配置项**：
- `DEEPSEEK_API_KEY`：DeepSeek API 密钥（必需）
- `DEEPSEEK_BASE_URL`：API 基础地址（默认 `https://api.deepseek.com`）
- `WEATHER_API_KEY`：天气 API 密钥（可选）
- `WEATHER_API_TYPE`：天气 API 类型（`tianapi` 或 `qweather`，默认 `tianapi`）
- `WEATHER_API_HOST`：和风天气 API Host（仅和风天气需要）
- `HTTP_PROXY` / `HTTPS_PROXY`：代理设置（可选）

**特殊处理**：
- 自动处理 BOM 字符（Windows 编码问题）
- 自动补全 `/v1` 后缀
- 支持从项目根目录加载 `.env` 文件

---

### 3. **天气 Agent** (`agents/weather/`)

**功能**：查询城市天气信息。

**工作流程**：
1. 用户输入城市名称或天气查询
2. Agent 判断是否需要调用工具
3. 调用 `get_weather` 工具获取天气数据
4. 使用 LLM 将工具结果转换为友好回答

**工具实现** (`handlers.py`)：
- 支持**天行数据 API**（默认）和**和风天气 API**
- 自动尝试多个城市名称变体（如"保定"、"保定市"、"保定县"）
- 返回格式：`{城市} 当前气温 {温度}，天气：{天气}，温度范围 {最低} ~ {最高}，相对湿度 {湿度}%，{风向} {风力}，空气质量：{质量}（AQI: {AQI}）`

**优化特性**：
- 短文本输入（如"北京"）直接调用工具，跳过 LLM 判断
- 支持复杂查询（如"北京明天天气怎么样"）

---

### 4. **理财 Agent** (`agents/finance/`)

**功能**：帮助用户进行理财规划和资产配置建议。

**工作流程**：
1. 用户提供个人信息（年龄、收入、投资经验、风险承受、每月投资金额）
2. Agent 从对话历史中提取信息（使用正则表达式）
3. 如果信息足够（≥3 项），自动调用工具：
   - `assess_risk_profile`：评估风险等级（保守型/平衡型/激进型）
   - `generate_allocation_plan`：生成资产配置方案
4. 格式化工具结果，生成用户友好的回答

**工具实现** (`handlers.py`)：
- `assess_risk_profile`：基于年龄、收入、经验、风险承受计算风险评分（0-100），返回风险等级
- `generate_allocation_plan`：根据风险等级生成资产配置方案（股票、债券、货币基金、其他等）

**优化特性**：
- ✅ **信息提取**：自动从自然语言中提取结构化信息
- ✅ **默认值填充**：信息不足时使用合理默认值（年龄=30，收入=中等，经验=0年，风险=10%，投资=1000元）
- ✅ **对话历史**：维护上下文，支持多轮对话
- ✅ **格式化输出**：将 JSON 结果转换为清晰的中文说明
- ✅ **容错机制**：如果 LLM 返回异常，使用格式化结果作为后备

**信息映射规则**：
- 年龄：`27岁` → `age = 27`
- 收入：`10w年薪` / `中等收入` → `income_level = "medium"`
- 经验：`没有经验` / `0年` → `investment_experience_years = 0`
- 风险：`10%` / `较小亏损` → `max_drawdown_tolerance = "10%"`
- 投资：`1k` / `每月1000` → `monthly_invest_amount = 1000`

---

## 🎯 当前功能状态

### ✅ 已实现功能

1. **天气查询 Agent**
   - ✅ 支持天行数据 API（默认）
   - ✅ 支持和风天气 API（可选）
   - ✅ 自动城市名称匹配
   - ✅ 友好的天气信息展示

2. **理财规划 Agent**
   - ✅ 风险评估（基于年龄、收入、经验、风险承受）
   - ✅ 资产配置方案生成
   - ✅ 自然语言信息提取
   - ✅ 对话历史管理
   - ✅ 格式化输出

3. **基础设施**
   - ✅ 智能 LLM 客户端（自动切换端点、代理支持）
   - ✅ 配置管理（环境变量加载、BOM 处理）
   - ✅ 主程序交互界面

### 🔄 可扩展功能

- 添加更多 Agent（如 `match`、`todo`、`chat` 等）
- 持久化对话历史（数据库/文件）
- 多用户会话管理
- Web 界面（Flask/FastAPI）
- 更多天气 API 支持

---

## 📝 配置说明

### 必需配置

创建 `.env` 文件（从 `.env.example` 复制）：

```env
# DeepSeek API（必需）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 天气 API（可选，不配置会返回模拟数据）
WEATHER_API_KEY=你的天行数据API_KEY
WEATHER_API_TYPE=tianapi
```

### 可选配置

```env
# 代理设置（如果使用 VPN）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# 和风天气（如果使用和风天气 API）
WEATHER_API_HOST=你的API_HOST
WEATHER_API_TYPE=qweather
```

---

## 🚀 运行方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
# 复制 .env.example 为 .env 并填入 API 密钥

# 3. 运行主程序
python main.py

# 4. 选择 Agent
# 输入 1 使用天气 Agent
# 输入 2 使用理财 Agent
# 输入 exit 退出
```

---

## 🔍 代码质量

- ✅ **模块化设计**：每个 Agent 独立，易于扩展
- ✅ **错误处理**：完善的异常捕获和错误提示
- ✅ **代码注释**：关键函数和类都有中文注释
- ✅ **配置分离**：敏感信息通过 `.env` 管理，不提交到版本控制
- ✅ **Git 管理**：`.gitignore` 已配置，排除敏感文件和缓存

---

## 📊 项目统计

- **总文件数**：约 15 个 Python 文件
- **核心代码行数**：约 800+ 行
- **Agent 数量**：2 个（weather、finance）
- **工具数量**：3 个（get_weather、assess_risk_profile、generate_allocation_plan）
- **支持的外部 API**：DeepSeek、天行数据、和风天气

---

## 🐛 已知问题与限制

1. **对话历史**：理财 Agent 使用内存存储，程序重启后丢失
2. **错误处理**：部分 API 错误可能返回通用提示，需要查看日志
3. **城市匹配**：天气 API 对某些小城市可能无法识别
4. **理财建议**：仅用于学习参考，不构成实际投资建议

---

## 🔮 未来规划

- [ ] 添加数据库持久化（SQLite/PostgreSQL）
- [ ] 实现多用户会话管理
- [ ] 添加更多 Agent（如股票查询、新闻摘要等）
- [ ] 开发 Web 界面（Flask/FastAPI + React）
- [ ] 添加日志系统（logging）
- [ ] 单元测试和集成测试
- [ ] Docker 容器化部署

---

## 📚 相关文档

- `README.md`：项目使用说明
- `.env.example`：环境变量模板
- 各 Agent 的 `prompts.py`：系统提示词（可调整 Agent 行为）

---

## 💡 开发建议

### 添加新 Agent 的步骤

1. 在 `agents/` 下创建新目录（如 `agents/todo/`）
2. 创建以下文件：
   - `__init__.py`
   - `prompts.py`：定义系统提示词
   - `tools.py`：定义工具（OpenAI 格式）
   - `handlers.py`：实现工具函数
   - `core.py`：实现 Agent 核心逻辑
3. 在 `main.py` 中添加对应的调用逻辑

### 调试技巧

- 查看 `config/settings.py` 确认环境变量是否正确加载
- 检查 `agents/shared/llm_client.py` 的端点切换日志
- 在 `handlers.py` 中添加 `print` 语句查看 API 响应
- 使用 `python -c "from config.settings import *; print(DEEPSEEK_API_KEY)"` 测试配置加载

---

**最后更新**：2024年（当前版本）

**维护者**：项目开发者

**许可证**：待定

---

*本文档由项目代码自动梳理生成，如有疑问请查看源代码或联系维护者。*

