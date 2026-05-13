import os


class AIConfig:
    """AI 相关配置，统一从环境变量读取"""

    # ==================== LLM 配置 ====================
    # 提供商: openai / zhipu / deepseek / qwen
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'zhipu')
    LLM_MODEL = os.getenv('LLM_MODEL', 'glm-4-flash')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '4096'))
    LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '60'))

    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

    # 智谱AI
    ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '')

    # DeepSeek
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')

    # Qwen (DashScope 兼容 OpenAI 接口)
    QWEN_API_KEY = os.getenv('QWEN_API_KEY', '')
    QWEN_BASE_URL = os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')

    # ==================== Embedding 配置 ====================
    # 提供商: local / openai / zhipu
    EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'local')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-large-zh-v1.5')
    EMBEDDING_DIMENSION = int(os.getenv('EMBEDDING_DIMENSION', '1024'))
    EMBEDDING_DEVICE = os.getenv('EMBEDDING_DEVICE', 'cpu')  # cpu / cuda / mps
    EMBEDDING_BATCH_SIZE = int(os.getenv('EMBEDDING_BATCH_SIZE', '32'))

    # OpenAI Embedding
    OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

    # ==================== 向量数据库配置 ====================
    VECTOR_DB_TYPE = os.getenv('VECTOR_DB_TYPE', 'chroma')
    CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './data/chroma')

    # 向量检索参数
    VECTOR_SEARCH_TOP_K = int(os.getenv('VECTOR_SEARCH_TOP_K', '10'))
    VECTOR_SEARCH_SCORE_THRESHOLD = float(os.getenv('VECTOR_SEARCH_SCORE_THRESHOLD', '0.5'))

    # ==================== 文档处理配置 ====================
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './data/uploads')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', str(50 * 1024 * 1024)))  # 50MB
    ALLOWED_EXTENSIONS = {
        'pdf', 'docx', 'pptx', 'xlsx', 'txt', 'md', 'html'
    }

    # 文本分块配置
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '500'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '50'))

    # ==================== Celery 配置 ====================
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
