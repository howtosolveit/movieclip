import os
from dotenv import load_dotenv
from pathlib import Path

def get_env_var(key, default=None):
    """
    获取环境变量，按优先级顺序：
    1. 系统环境变量
    2. .env文件中的变量
    3. 默认值
    """
    # 首先检查系统环境变量
    system_value = os.environ.get(key)
    if system_value is not None:
        return system_value
    
    # 如果系统环境变量不存在，则尝试从.env文件加载
    # 保存当前环境变量状态
    original_value = os.environ.get(key)
    
    # 尝试多个可能的.env文件位置
    possible_env_paths = [
        Path(__file__).parent.parent / '.env',  # src/.env
        Path(__file__).parent.parent.parent / '.env',  # 项目根目录/.env
        Path(__file__).parent.parent / 'backend' / '.env',  # src/backend/.env
        Path('.env'),  # 当前工作目录/.env
    ]
    
    for env_path in possible_env_paths:
        if env_path.exists():
            # 临时加载这个.env文件
            load_dotenv(dotenv_path=env_path, override=False)
            # 检查是否获取到了值
            dotenv_value = os.environ.get(key)
            if dotenv_value is not None and dotenv_value != original_value:
                return dotenv_value
    
    # 如果都没有找到，返回默认值
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
    debug_mode = os.environ.get('ENV_DEBUG', 'false').lower() == 'true'
    if debug_mode:
        print("=== Environment Variable Loading Debug ===")
        
        # 检查可能的.env文件
        possible_env_paths = [
            Path(__file__).parent.parent / '.env',
            Path(__file__).parent.parent.parent / '.env',
            Path(__file__).parent.parent / 'backend' / '.env',
            Path('.env'),
        ]
        
        for i, env_path in enumerate(possible_env_paths):
            print(f"{i+1}. {env_path.absolute()}: {'存在' if env_path.exists() else '不存在'}")
        
        # 测试关键变量
        test_vars = ['MC_BUCKET_NAME', 'PROJECT_ID', 'LOCATION']
        for var in test_vars:
            sys_val = os.environ.get(var)
            env_val = get_env_var(var)
            print(f"{var}: 系统={sys_val}, 最终={env_val}")

# 执行调试检查
_debug_env_loading()

# 项目配置
PROJECT_ID = get_env_var("PROJECT_ID")
SPEECH_PROJECT_ID = get_env_var("SPEECH_PROJECT_ID")
IMAGE_PROJECT_ID = get_env_var("IMAGE_PROJECT_ID")
VIDEO_PROJECT_ID = get_env_var("VIDEO_PROJECT_ID")
GCS_PROJECT_ID = get_env_var("GCS_PROJECT_ID")
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

# 其他配置
FFMPEG_EXECUTABLE = get_env_var("FFMPEG_EXECUTABLE", "ffmpeg")
FFPROBE_EXECUTABLE = get_env_var("FFPROBE_EXECUTABLE", "ffprobe")
PROXY = get_env_var("PROXY")

# 输出重要配置信息（仅在调试模式下）
if os.environ.get('ENV_DEBUG', 'false').lower() == 'true':
    print("\n=== Final Configuration ===")
    print(f"PROJECT_ID: {PROJECT_ID}")
    print(f"LOCATION: {LOCATION}")
    print(f"MC_BUCKET_NAME: {MC_BUCKET_NAME}")
    print(f"MC_OBJECT_PREFIX: {MC_OBJECT_PREFIX}")
    print(f"MC_NEED_GCS: {MC_NEED_GCS}")
    print(f"FFMPEG_EXECUTABLE: {FFMPEG_EXECUTABLE}")
