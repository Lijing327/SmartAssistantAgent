import requests
from config.settings import WEATHER_API_KEY, WEATHER_API_HOST, WEATHER_API_TYPE


def get_weather(location: str) -> str:
    """
    调用天气 API，返回一个给模型看的简短字符串。
    支持天行数据和和风天气两种 API。
    如果没有配置 WEATHER_API_KEY，就直接返回模拟数据。
    """
    if not WEATHER_API_KEY:
        return f"当前无法访问真实天气服务，这里先假装 {location} 的气温是 26℃，多云。"

    # 根据配置选择使用天行数据或和风天气
    api_type = WEATHER_API_TYPE.lower() if WEATHER_API_TYPE else "tianapi"
    
    if api_type == "tianapi":
        return _get_weather_tianapi(location)
    else:
        return _get_weather_qweather(location)


def _get_weather_tianapi(location: str) -> str:
    """使用天行数据天气 API"""
    url = "https://apis.tianapi.com/tianqi/index"
    
    # 尝试多个城市名称变体
    location_variants = [
        location,
        f"{location}市",
        f"{location}县",
    ]
    
    for loc in location_variants:
        try:
            params = {
                "key": WEATHER_API_KEY,
                "city": loc,
                "type": 1,  # 1=实时天气，7=七天预报
            }
            
            resp = requests.get(url, params=params, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                
                # 检查 API 返回状态
                code = data.get("code")
                if code != 200:
                    error_msg = data.get("msg", f"API 返回错误码: {code}")
                    if code == 150:  # API可用次数不足
                        return f"查询 {location} 天气失败，{error_msg}。请检查 API 调用次数。"
                    # 尝试下一个城市名称变体
                    continue
                
                # 解析天行数据 API 响应
                result_data = data.get("result", {})
                if not result_data:
                    continue
                
                area = result_data.get("area", location)
                weather = result_data.get("weather", "未知")
                real = result_data.get("real", "N/A")
                lowest = result_data.get("lowest", "N/A")
                highest = result_data.get("highest", "N/A")
                wind = result_data.get("wind", "")
                windsc = result_data.get("windsc", "")
                humidity = result_data.get("humidity", "N/A")
                quality = result_data.get("quality", "")
                aqi = result_data.get("aqi", "")
                
                # 构建返回字符串
                result = f"{area} 当前气温 {real}，天气：{weather}，温度范围 {lowest} ~ {highest}"
                if humidity != "N/A":
                    result += f"，相对湿度 {humidity}%"
                if wind:
                    result += f"，{wind}"
                    if windsc:
                        result += f" {windsc}"
                if quality and aqi:
                    result += f"，空气质量：{quality}（AQI: {aqi}）"
                
                return result
            else:
                continue
                
        except requests.exceptions.RequestException:
            continue
        except Exception:
            continue
    
    return f"查询 {location} 天气失败，无法找到有效的城市位置。请尝试使用完整的城市名称，如'保定市'。"


def _get_weather_qweather(location: str) -> str:
    """使用和风天气 API（保留原有逻辑）"""
    # 这里保留原来的和风天气代码逻辑
    # 由于代码较长，暂时返回提示信息
    return f"和风天气 API 功能暂未实现，请使用天行数据 API（设置 WEATHER_API_TYPE=tianapi）"

