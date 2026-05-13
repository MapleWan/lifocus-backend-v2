import logging
from app.extension import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='tasks.process_document', max_retries=3)
def process_document_task(self, document_id: str):
    """
    异步处理文档任务：解析 → 分块 → 向量化 → 存储
    """
    logger.info(f"[Celery] 开始处理文档任务: document_id={document_id}")
    try:
        from app.services.document.pipeline import DocumentPipeline
        DocumentPipeline.process(document_id)
        logger.info(f"[Celery] 文档处理任务完成: document_id={document_id}")
    except Exception as exc:
        logger.exception(f"[Celery] 文档处理任务异常: document_id={document_id}, error={exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task(bind=True, name='tasks.reprocess_document', max_retries=3)
def reprocess_document_task(self, document_id: str):
    """
    异步重新处理文档任务：清除旧数据 → 重新 Pipeline
    """
    logger.info(f"[Celery] 开始重新处理文档任务: document_id={document_id}")
    try:
        from app.services.document.pipeline import DocumentPipeline
        DocumentPipeline.reprocess(document_id)
        logger.info(f"[Celery] 文档重新处理任务完成: document_id={document_id}")
    except Exception as exc:
        logger.exception(f"[Celery] 文档重新处理任务异常: document_id={document_id}, error={exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
