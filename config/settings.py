import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载 .env 文件（从项目根目录）
env_path = BASE_DIR / ".env"

# 先尝试使用 load_dotenv
load_dotenv(dotenv_path=env_path, override=True)

# 如果 load_dotenv 没有加载到值，使用 dotenv_values 直接读取（处理 BOM 问题）
if not os.getenv("DEEPSEEK_API_KEY"):
    env_values = dotenv_values(dotenv_path=env_path)
    # 处理 BOM 字符问题：检查是否有带 BOM 的键名
    for key, value in env_values.items():
        # 去除键名中的 BOM 字符
        clean_key = key.lstrip('\ufeff')
        if clean_key != key:
            # 如果键名有 BOM，设置正确的环境变量
            os.environ[clean_key] = value
        else:
            # 正常设置环境变量
            os.environ[key] = value

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
# 如果你在国内用 .cn 更稳定，可以改成 https://api.deepseek.cn/v1
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 确保 BASE_URL 格式正确（OpenAI 客户端需要完整的 URL）
if DEEPSEEK_BASE_URL and not DEEPSEEK_BASE_URL.endswith("/v1"):
    if DEEPSEEK_BASE_URL.endswith("/"):
        DEEPSEEK_BASE_URL = DEEPSEEK_BASE_URL + "v1"
    else:
        DEEPSEEK_BASE_URL = DEEPSEEK_BASE_URL + "/v1"

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
# 天行数据天气 API（默认使用天行数据）
# 如果使用和风天气，需要配置 WEATHER_API_HOST
WEATHER_API_HOST = os.getenv("WEATHER_API_HOST")
WEATHER_API_TYPE = os.getenv("WEATHER_API_TYPE", "tianapi")  # tianapi 或 qweather

# 代理设置（可选）
HTTP_PROXY = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
HTTPS_PROXY = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

