import logging
from app.services.ai_config import AIConfig

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLM 工厂类，支持多提供商（基于 LangChain BaseChatModel 接口）"""

    @staticmethod
    def create_llm(provider=None, model=None, temperature=None):
        """
        创建 LLM 实例
        :param provider: 提供商名称，默认从配置读取
        :param model: 模型名称，默认从配置读取
        :param temperature: 温度参数，默认从配置读取
        :return: LangChain BaseChatModel 实例
        """
        provider = provider or AIConfig.LLM_PROVIDER
        model = model or AIConfig.LLM_MODEL
        temperature = temperature if temperature is not None else AIConfig.LLM_TEMPERATURE

        logger.info(f"创建 LLM 实例: provider={provider}, model={model}")

        if provider == 'openai':
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=AIConfig.OPENAI_API_KEY,
                base_url=AIConfig.OPENAI_BASE_URL,
                max_tokens=AIConfig.LLM_MAX_TOKENS,
                timeout=AIConfig.LLM_TIMEOUT,
            )
        elif provider == 'zhipu':
            from langchain_community.chat_models import ChatZhipuAI
            return ChatZhipuAI(
                model=model,
                temperature=temperature,
                api_key=AIConfig.ZHIPU_API_KEY,
                max_tokens=AIConfig.LLM_MAX_TOKENS,
            )
        elif provider == 'deepseek':
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=AIConfig.DEEPSEEK_API_KEY,
                base_url=AIConfig.DEEPSEEK_BASE_URL,
                max_tokens=AIConfig.LLM_MAX_TOKENS,
                timeout=AIConfig.LLM_TIMEOUT,
            )
        elif provider == 'qwen':
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=AIConfig.QWEN_API_KEY,
                base_url=AIConfig.QWEN_BASE_URL,
                max_tokens=AIConfig.LLM_MAX_TOKENS,
                timeout=AIConfig.LLM_TIMEOUT,
            )
        else:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")
