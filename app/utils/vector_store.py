import logging
import chromadb
from app.services.ai_config import AIConfig

logger = logging.getLogger(__name__)


class VectorStoreService:
    """ChromaDB 向量数据库封装，设计为可替换的抽象层"""

    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            persist_dir = AIConfig.CHROMA_PERSIST_DIR
            logger.info(f"初始化 ChromaDB，持久化目录: {persist_dir}")
            cls._client = chromadb.PersistentClient(path=persist_dir)
        return cls._client

    @classmethod
    def get_or_create_collection(cls, collection_name):
        """获取或创建 Collection"""
        client = cls._get_client()
        return client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    @classmethod
    def add_documents(cls, collection_name, ids, embeddings, documents, metadatas=None):
        """批量写入向量数据"""
        collection = cls.get_or_create_collection(collection_name)
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"向 Collection '{collection_name}' 写入 {len(ids)} 条向量")

    @classmethod
    def query(cls, collection_name, query_embedding, top_k=5, where=None):
        """向量相似度查询"""
        collection = cls.get_or_create_collection(collection_name)
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        if where:
            kwargs["where"] = where

        results = collection.query(**kwargs)

        items = []
        if results and results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                item = {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i] if results.get('documents') else None,
                    'metadata': results['metadatas'][0][i] if results.get('metadatas') else None,
                    'distance': results['distances'][0][i] if results.get('distances') else None,
                }
                items.append(item)
        return items

    @classmethod
    def delete_by_ids(cls, collection_name, ids):
        """删除指定向量"""
        if not ids:
            return
        collection = cls.get_or_create_collection(collection_name)
        collection.delete(ids=ids)
        logger.info(f"从 Collection '{collection_name}' 删除 {len(ids)} 条向量")

    @classmethod
    def delete_collection(cls, collection_name):
        """删除整个 Collection"""
        client = cls._get_client()
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"删除 Collection '{collection_name}'")
        except Exception as e:
            logger.warning(f"删除 Collection '{collection_name}' 失败: {e}")

    @classmethod
    def count(cls, collection_name):
        """统计向量数量"""
        try:
            collection = cls.get_or_create_collection(collection_name)
            return collection.count()
        except Exception:
            return 0
