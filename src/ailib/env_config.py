import os
from dotenv import load_dotenv
from pathlib import Path

def get_env_var(key, default=None):
    """
    获取环境变量，仅从 src/.env 文件读取
    """
    # 指定 src/.env 文件路径
    env_path = Path(__file__).parent.parent / '.env'  # src/.env
    
    if env_path.exists():
        
        # 加载 src/.env 文件
        load_dotenv(dotenv_path=env_path, override=True)
        
        # 获取值
        dotenv_value = os.environ.get(key)
        
        # 如果原来没有这个环境变量，加载后有了，就使用它
        if dotenv_value is not None:
            return dotenv_value
    
    # 如果没有找到，返回默认值
    return default

def get_env_bool(key, default=False):
    """获取布尔类型的环境变量"""
    value = get_env_var(key)
    if value is None:
        return default
    return str(value).lower() in ('true', '1', 'yes', 'on')

def get_env_int(key, default=0):
    """获取整数类型的环境变量"""
    value = get_env_var(key)
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# 初始化时输出加载信息（仅在调试时启用）
def _debug_env_loading():
    """调试环境变量加载情况"""
    # 从 src/.env 读取 ENV_DEBUG 设置
    env_path = Path(__file__).parent.parent / '.env'
    debug_mode = False
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        debug_mode = os.environ.get('ENV_DEBUG', 'false').lower() == 'true'
    
    if debug_mode:
        print("=== Environment Variable Loading Debug ===")
        print(f"仅从 src/.env 文件加载环境变量")
        print(f"src/.env 路径: {env_path.absolute()}")
        print(f"src/.env 存在: {'是' if env_path.exists() else '否'}")
        
        # 测试关键变量
        test_vars = ['MC_BUCKET_NAME', 'PROJECT_ID', 'LOCATION']
        for var in test_vars:
            env_val = get_env_var(var)
            print(f"{var}: {env_val}")

# 执行调试检查
_debug_env_loading()

# 项目配置
PROJECT_ID = get_env_var("PROJECT_ID")
SPEECH_PROJECT_ID = get_env_var("SPEECH_PROJECT_ID")
IMAGE_PROJECT_ID = get_env_var("IMAGE_PROJECT_ID")
VIDEO_PROJECT_ID = get_env_var("VIDEO_PROJECT_ID")
GCS_PROJECT_ID = get_env_var("GCS_PROJECT_ID")
DOWNLOAD_GCS_PROJECT_ID = get_env_var("DOWNLOAD_GCS_PROJECT_ID")
LOCATION = get_env_var("LOCATION")

# 服务账户配置
SA_KEY_FILE_PATH = get_env_var("SA_KEY_FILE_PATH")

# API Key 配置
API_KEY = get_env_var("API_KEY")

# 认证配置
GEMINI_AUTH_TYPE = get_env_var("GEMINI_AUTH_TYPE", "ADC")
SPEECH_AUTH_TYPE = get_env_var("SPEECH_AUTH_TYPE", "ADC")
IMAGE_AUTH_TYPE = get_env_var("IMAGE_AUTH_TYPE", "ADC")
VIDEO_AUTH_TYPE = get_env_var("VIDEO_AUTH_TYPE", "ADC")
GCS_AUTH_TYPE = get_env_var("GCS_AUTH_TYPE", "ADC")
DOWNLOAD_GCS_AUTH_TYPE = get_env_var("DOWNLOAD_GCS_AUTH_TYPE", "ADC")

# 超时配置
GEMINI_TIMEOUT = get_env_int("GEMINI_CLIENT_TIMEOUT", 300000)

# MiniMax 配置
MINIMAX_GROUP_ID = get_env_var("MINIMAX_GROUP_ID")
MINIMAX_API_KEY = get_env_var("MINIMAX_API_KEY")

# Movie clip 参数
MC_PARTITION_SECONDS = get_env_int("MC_PARTITION_SECONDS", 600)
MC_BUCKET_NAME = get_env_var("MC_BUCKET_NAME")
MC_OBJECT_PREFIX = get_env_var("MC_OBJECT_PREFIX")
MC_NEED_GCS = get_env_bool("MC_NEED_GCS", True)
UI_SUPPORT_GCS_URI = get_env_bool("UI_SUPPORT_GCS_URI", True)

# 其他配置
FFMPEG_EXECUTABLE = get_env_var("FFMPEG_EXECUTABLE", "ffmpeg")
FFPROBE_EXECUTABLE = get_env_var("FFPROBE_EXECUTABLE", "ffprobe")
PROXY = get_env_var("PROXY")

# 输出重要配置信息（仅在调试模式下）
env_path = Path(__file__).parent.parent / '.env'
debug_mode = False
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    debug_mode = os.environ.get('ENV_DEBUG', 'false').lower() == 'true'

if debug_mode:
    print("\n=== Final Configuration ===")
    print(f"PROJECT_ID: {PROJECT_ID}")
    print(f"LOCATION: {LOCATION}")
    print(f"MC_BUCKET_NAME: {MC_BUCKET_NAME}")
    print(f"MC_OBJECT_PREFIX: {MC_OBJECT_PREFIX}")
    print(f"MC_NEED_GCS: {MC_NEED_GCS}")
    print(f"FFMPEG_EXECUTABLE: {FFMPEG_EXECUTABLE}")
