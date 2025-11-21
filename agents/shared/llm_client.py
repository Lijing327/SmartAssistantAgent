import os
import httpx
from openai import OpenAI
from openai._exceptions import APIConnectionError

from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, HTTP_PROXY, HTTPS_PROXY

# 检查 API 密钥是否存在
if not DEEPSEEK_API_KEY:
    raise ValueError(
        "DEEPSEEK_API_KEY 未设置！请确保 .env 文件存在并包含 DEEPSEEK_API_KEY。"
        "\n可以复制 .env.example 为 .env 并填入你的 API 密钥。"
    )

# 定义两个可用的 API 端点
DEEPSEEK_CN_URL = "https://api.deepseek.cn/v1"
DEEPSEEK_COM_URL = "https://api.deepseek.com/v1"

# 获取备用 URL（如果当前是 .cn 则备用是 .com，反之亦然）
def get_alternative_url(current_url: str) -> str:
    """获取备用 URL"""
    if "api.deepseek.cn" in current_url:
        return DEEPSEEK_COM_URL
    elif "api.deepseek.com" in current_url:
        return DEEPSEEK_CN_URL
    else:
        # 如果都不是，默认返回 .com
        return DEEPSEEK_COM_URL

# 配置代理（如果设置了的话）
proxies = {}
if HTTP_PROXY:
    proxies["http://"] = HTTP_PROXY
if HTTPS_PROXY:
    proxies["https://"] = HTTPS_PROXY

# 创建 httpx 客户端
# 如果有代理配置，使用代理；否则使用 trust_env=True 允许使用系统代理（VPN）
if proxies:
    _http_client = httpx.Client(proxies=proxies, timeout=30.0, verify=True)
else:
    # 如果使用 VPN，允许使用系统代理设置
    # trust_env=True 会读取环境变量中的代理设置
    _http_client = httpx.Client(trust_env=True, timeout=30.0, verify=True)


class SmartOpenAIClient:
    """智能 OpenAI 客户端，支持自动切换 API 端点"""
    
    def __init__(self, initial_url: str):
        self._current_url = initial_url
        self._api_key = DEEPSEEK_API_KEY
        self._http_client = _http_client
        self._client = self._create_client(initial_url)
    
    def _create_client(self, base_url: str) -> OpenAI:
        """创建 OpenAI 客户端"""
        return OpenAI(
            api_key=self._api_key,
            base_url=base_url,
            http_client=self._http_client,
        )
    
    def _switch_to_alternative(self):
        """切换到备用 URL"""
        alternative_url = get_alternative_url(self._current_url)
        print(f"⚠️  连接 {self._current_url} 失败，正在尝试切换到 {alternative_url}...")
        self._current_url = alternative_url
        self._client = self._create_client(self._current_url)
        print(f"✅ 已切换到 {alternative_url}")
    
    @property
    def chat(self):
        """返回 chat 对象，支持自动切换"""
        return SmartChatCompletions(self)
    
    @property
    def base_url(self):
        """返回当前使用的 base_url"""
        return self._current_url


class SmartChatCompletions:
    """智能 Chat Completions，支持自动切换端点"""
    
    def __init__(self, smart_client: SmartOpenAIClient):
        self._smart_client = smart_client
    
    @property
    def completions(self):
        return SmartCompletions(self._smart_client)


class SmartCompletions:
    """智能 Completions，支持自动切换端点"""
    
    def __init__(self, smart_client: SmartOpenAIClient):
        self._smart_client = smart_client
    
    def create(self, *args, **kwargs):
        """创建 completion，失败时自动切换端点"""
        max_retries = 1  # 最多重试一次（切换端点）
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return self._smart_client._client.chat.completions.create(*args, **kwargs)
            except (APIConnectionError, httpx.ConnectError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < max_retries:
                    self._smart_client._switch_to_alternative()
                else:
                    raise
            except Exception as e:
                # 其他错误直接抛出，不切换端点
                raise
        
        if last_error:
            raise last_error


# 导出智能客户端
client = SmartOpenAIClient(DEEPSEEK_BASE_URL)

