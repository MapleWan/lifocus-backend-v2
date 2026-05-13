import uuid
import logging
from datetime import datetime

from app.extension import db
from app.models import Document, DocumentChunk, KnowledgeBase
from app.services.document.parsers import ParserFactory
from app.services.document.text_splitter import TextSplitterService
from app.services.llm.embedding_service import embedding_service
from app.utils.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class DocumentPipeline:
    """
    文档处理 Pipeline: 解析 → 分块 → 向量化 → 存储
    用于 Celery 异步任务调用
    """

    @staticmethod
    def process(document_id: str):
        """
        处理单个文档的完整流程。
        :param document_id: 文档ID
        """
        doc = Document.get_by_id(document_id)
        if not doc:
            logger.error(f"文档不存在: {document_id}")
            return

        kb = KnowledgeBase.get_by_id(doc.knowledge_base_id)
        if not kb:
            logger.error(f"知识库不存在: {doc.knowledge_base_id}")
            DocumentPipeline._mark_failed(doc, '知识库不存在')
            return

        try:
            # 1. 更新状态为处理中
            doc.embed_status = 'PROCESSING'
            doc.update_document()
            logger.info(f"开始处理文档: {doc.file_name} (id={document_id})")

            # 2. 解析文档
            parse_result = ParserFactory.parse(doc.file_path)
            if not parse_result.content:
                DocumentPipeline._mark_failed(doc, '文档内容为空')
                return

            # 更新文档元信息
            doc.title = parse_result.title or doc.file_name
            doc.content_preview = parse_result.preview
            doc.content_length = parse_result.content_length
            if parse_result.metadata:
                doc.meta_data = parse_result.metadata
            doc.update_document()

            # 3. 文本分块
            chunks = TextSplitterService.split_text(
                parse_result.content,
                chunk_size=kb.chunk_size,
                chunk_overlap=kb.chunk_overlap,
            )
            if not chunks:
                DocumentPipeline._mark_failed(doc, '文本分块结果为空')
                return

            logger.info(f"文档 {doc.file_name} 分块完成: {len(chunks)} 个块")

            # 4. 向量化
            chunk_contents = [c['content'] for c in chunks]
            embeddings = embedding_service.embed_texts(chunk_contents)
            logger.info(f"文档 {doc.file_name} 向量化完成: {len(embeddings)} 条")

            # 5. 存储分块到数据库 & 向量数据库
            vector_ids = []
            chunk_records = []

            for idx, chunk_data in enumerate(chunks):
                vector_id = f"doc_{document_id}_chunk_{idx}"
                vector_ids.append(vector_id)

                chunk_record = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    knowledge_base_id=kb.id,
                    chunk_index=chunk_data['chunk_index'],
                    content=chunk_data['content'],
                    content_length=chunk_data['content_length'],
                    start_char=chunk_data.get('start_char'),
                    end_char=chunk_data.get('end_char'),
                    vector_id=vector_id,
                )
                chunk_records.append(chunk_record)

            # 批量写入数据库
            db.session.bulk_save_objects(chunk_records)
            db.session.commit()

            # 写入向量数据库
            metadatas = [
                {
                    'document_id': document_id,
                    'knowledge_base_id': kb.id,
                    'chunk_index': c['chunk_index'],
                    'file_name': doc.file_name,
                }
                for c in chunks
            ]

            VectorStoreService.add_documents(
                collection_name=kb.vector_collection,
                ids=vector_ids,
                embeddings=embeddings,
                documents=chunk_contents,
                metadatas=metadatas,
            )

            # 6. 更新文档和知识库统计
            doc.embed_status = 'COMPLETED'
            doc.chunk_count = len(chunks)
            doc.process_time = datetime.now()
            doc.process_error = None
            doc.update_document()

            kb.document_count = Document.query.filter_by(
                knowledge_base_id=kb.id, is_deleted=False
            ).count()
            kb.total_chunks = DocumentChunk.query.filter_by(
                knowledge_base_id=kb.id
            ).count()
            kb.update_knowledge_base()

            logger.info(f"文档处理完成: {doc.file_name}, {len(chunks)} 个块已写入")

        except Exception as e:
            logger.exception(f"文档处理失败: {document_id}, 错误: {e}")
            db.session.rollback()
            DocumentPipeline._mark_failed(doc, str(e))

    @staticmethod
    def reprocess(document_id: str):
        """
        重新处理文档：先清理旧数据，再重新执行 pipeline。
        """
        doc = Document.get_by_id(document_id)
        if not doc:
            logger.error(f"文档不存在: {document_id}")
            return

        kb = KnowledgeBase.get_by_id(doc.knowledge_base_id)
        if not kb:
            logger.error(f"知识库不存在: {doc.knowledge_base_id}")
            return

        # 删除旧的分块
        old_chunks = DocumentChunk.query.filter_by(document_id=document_id).all()
        old_vector_ids = [c.vector_id for c in old_chunks if c.vector_id]

        # 删除向量数据库中的旧数据
        if old_vector_ids:
            VectorStoreService.delete_by_ids(kb.vector_collection, old_vector_ids)

        # 删除数据库中的旧分块
        DocumentChunk.query.filter_by(document_id=document_id).delete()
        db.session.commit()

        logger.info(f"已清理旧数据: {len(old_chunks)} 个分块, 准备重新处理")

        # 重新处理
        DocumentPipeline.process(document_id)

    @staticmethod
    def _mark_failed(doc: Document, error_msg: str):
        """标记文档为处理失败"""
        doc.embed_status = 'FAILED'
        doc.process_error = error_msg[:2000]
        doc.update_document()
        logger.error(f"文档处理失败: {doc.file_name}, 原因: {error_msg}")
