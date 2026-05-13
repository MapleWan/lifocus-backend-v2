import logging
from app.services.ai_config import AIConfig

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding 服务，支持多提供商（基于 LangChain Embeddings 接口）"""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_model(self):
        if self._model is None:
            provider = AIConfig.EMBEDDING_PROVIDER
            logger.info(f"初始化 Embedding 模型，提供商: {provider}")

            if provider == 'local':
                from langchain_huggingface import HuggingFaceEmbeddings
                model_name = AIConfig.EMBEDDING_MODEL
                self._model = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': AIConfig.EMBEDDING_DEVICE},
                    encode_kwargs={'normalize_embeddings': True, 'batch_size': AIConfig.EMBEDDING_BATCH_SIZE}
                )
            elif provider == 'openai':
                from langchain_openai import OpenAIEmbeddings
                self._model = OpenAIEmbeddings(
                    model=AIConfig.OPENAI_EMBEDDING_MODEL,
                    openai_api_key=AIConfig.OPENAI_API_KEY,
                    openai_api_base=AIConfig.OPENAI_BASE_URL,
                )
            elif provider == 'zhipu':
                from langchain_community.embeddings import ZhipuAIEmbeddings
                self._model = ZhipuAIEmbeddings(
                    api_key=AIConfig.ZHIPU_API_KEY,
                )
            else:
                raise ValueError(f"不支持的 Embedding 提供商: {provider}")

            logger.info(f"Embedding 模型初始化完成: {provider}")
        return self._model

    def embed_text(self, text):
        """单条文本向量化"""
        model = self._get_model()
        return model.embed_query(text)

    def embed_texts(self, texts):
        """批量文本向量化"""
        model = self._get_model()
        return model.embed_documents(texts)

    def get_dimension(self):
        """获取向量维度"""
        return AIConfig.EMBEDDING_DIMENSION


# 模块级单例
embedding_service = EmbeddingService()
