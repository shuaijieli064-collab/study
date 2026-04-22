import logging
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# AI API 配置（兼容 OpenAI 接口标准）
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_API_BASE = os.getenv("AI_API_BASE", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")

# Flask 配置
_DEFAULT_SECRET_KEY = "zhixiaotong-secret-key-2024"
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)
    logger.warning(
        "SECRET_KEY 未在环境变量中设置，已自动生成随机密钥。"
        "生产环境请在 .env 文件中配置固定的 SECRET_KEY。"
    )
elif SECRET_KEY == _DEFAULT_SECRET_KEY:
    logger.warning(
        "SECRET_KEY 使用了不安全的默认值，存在安全风险。"
        "生产环境请在 .env 文件中配置强随机密钥。"
    )

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 上传限制

# CORS 允许的来源（生产环境应配置具体域名，多个域名用逗号分隔）
_cors_env = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()] if _cors_env else "*"

# 知识库路径
KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "campus_knowledge.json")

# 输入长度限制
MAX_TEXT_LENGTH = 10000       # 通用文本输入最大字符数
MAX_QUERY_LENGTH = 1000       # 查询字段最大字符数
MAX_HISTORY_MSG_LENGTH = 2000 # 对话历史单条消息最大字符数
MAX_HISTORY_TURNS = 10        # 最大保留对话轮次
MAX_EXAM_COUNT = 20           # 考试提醒最大条数
