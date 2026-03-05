# LiFocus 知识库系统技术方案

## 一、系统架构总览

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               Client Layer                                          │
│         (Web Frontend / Mobile App / Browser Extension)                             │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              API Gateway Layer                                      │
│              Flask 3.1.1 + Flask-RESTful + Flask-JWT-Extended                       │
│              - JWT Token 认证与鉴权                                                  │
│              - 请求限流与防护                                                        │
│              - 统一响应格式                                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
        ▼                               ▼                               ▼
┌───────────────────┐         ┌───────────────────┐         ┌───────────────────┐
│   现有业务模块     │         │   知识库核心模块   │         │   AI 服务模块      │
│                   │         │                   │         │                   │
│  ┌─────────────┐  │         │  ┌─────────────┐  │         │  ┌─────────────┐  │
│  │   Article   │  │         │  │  Knowledge  │  │         │  │  LLM Chat   │  │
│  │   Manager   │  │         │  │   Manager   │  │         │  │   Service   │  │
│  └─────────────┘  │         │  └─────────────┘  │         │  └─────────────┘  │
│  ┌─────────────┐  │         │  ┌─────────────┐  │         │  ┌─────────────┐  │
│  │   Category  │  │         │  │  Document   │  │         │  │   RAG       │  │
│  │   Manager   │  │         │  │   Manager   │  │         │  │  Pipeline   │  │
│  └─────────────┘  │         │  └─────────────┘  │         │  └─────────────┘  │
│  ┌─────────────┐  │         │  ┌─────────────┐  │         │  ┌─────────────┐  │
│  │   Project   │  │         │  │  Embedding  │  │         │  │ Web Summary │  │
│  │   Manager   │  │         │  │   Service   │  │         │  │   Service   │  │
│  └─────────────┘  │         │  └─────────────┘  │         │  └─────────────┘  │
│  ┌─────────────┐  │         │  ┌─────────────┐  │         │  ┌─────────────┐  │
│  │    User     │  │         │  │   Crawler   │  │         │  │  Search     │  │
│  │   Manager   │  │         │  │   Service   │  │         │  │  Service    │  │
│  └─────────────┘  │         │  └─────────────┘  │         │  └─────────────┘  │
└───────────────────┘         └───────────────────┘         └───────────────────┘
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
        ▼                               ▼                               ▼
┌───────────────────┐         ┌───────────────────┐         ┌───────────────────┐
│     MySQL 8.0     │         │   向量数据库       │         │    文件存储        │
│                   │         │                   │         │                   │
│  - user           │         │  - ChromaDB       │         │  - 本地文件系统    │
│  - project        │         │    (开发)         │         │    (开发)         │
│  - category       │         │  - Milvus         │         │  - MinIO/OSS      │
│  - article        │         │    (生产)         │         │    (生产)         │
│  - knowledge_base │         │  - Collection     │         │                   │
│  - document       │         │    per KB         │         │                   │
│  - chat_history   │         │                   │         │                   │
└───────────────────┘         └───────────────────┘         └───────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           异步任务队列 (Celery + Redis)                              │
│              - 大文档处理任务                                                        │
│              - Embedding 批量计算                                                    │
│              - 网页抓取任务                                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 架构设计原则

| 原则 | 说明 |
|------|------|
| **模块化设计** | 知识库模块与现有业务解耦，通过接口交互 |
| **渐进式集成** | 现有 Article 可作为知识库数据源，平滑过渡 |
| **可扩展性** | 支持多种 LLM、向量数据库、文档格式的插件化扩展 |
| **数据隔离** | 知识库按项目和用户隔离，确保数据安全 |
| **异步处理** | 耗时操作（大文档处理、Embedding）异步执行 |

## 二、核心技术选型

### 2.1 LLM 与 Embedding 选型

#### 2.1.1 LLM 方案对比

| 方案 | 推荐模型 | 优点 | 缺点 | 适用场景 | 成本估算 |
|------|---------|------|------|---------|---------|
| **OpenAI** | gpt-4o-mini / gpt-4o | 效果稳定、生态完善 | 需要翻墙、数据出境 | 生产环境首选 | $0.15-5/1M tokens |
| **智谱AI** | GLM-4 / GLM-4-Flash | 国内可用、中文优化好 | 长文本能力稍弱 | 国内生产环境 | ¥0.001-0.1/1K tokens |
| **DeepSeek** | DeepSeek-V3 | 性价比高、中文强 | 新模型稳定性待观察 | 成本敏感场景 | ¥0.002-0.008/1K tokens |
| **本地部署** | Qwen2.5-72B / Llama3.1-70B | 数据安全、无网络依赖 | 硬件要求高、维护复杂 | 隐私敏感场景 | 一次性硬件投入 |

**推荐策略**:
- **开发阶段**: 使用智谱GLM-4-Flash或DeepSeek-V3（国内访问稳定）
- **生产阶段**: 根据用户分布选择 OpenAI（海外用户）或 智谱（国内用户）
- **私有化部署**: 提供本地模型配置选项，满足企业用户需求

#### 2.1.2 Embedding 方案对比

| 方案 | 模型 | 维度 | 上下文长度 | 优点 | 成本 |
|------|------|------|-----------|------|------|
| **OpenAI** | text-embedding-3-small | 1536 | 8192 | 效果好、多语言支持 | $0.02/1M tokens |
| **OpenAI** | text-embedding-3-large | 3072 | 8192 | 效果最佳 | $0.13/1M tokens |
| **BAAI** | bge-large-zh-v1.5 | 1024 | 512 | 中文优化、开源免费 | 免费 |
| **MokaAI** | m3e-base | 768 | 512 | 轻量快速、中文好 | 免费 |
| **本地** | bge-small-zh | 512 | 512 | 可离线使用 | 免费 |

**推荐**: 开发使用 `bge-large-zh-v1.5`（免费且中文效果好），生产可选择 `text-embedding-3-small`

#### 2.1.3 RAG 框架选型

| 框架 | 优点 | 缺点 | 推荐场景 |
|------|------|------|---------|
| **LangChain** | 生态最完善、文档丰富、社区活跃 | 版本更新快、API变动大 | 快速开发、功能丰富 |
| **LlamaIndex** | 检索能力强、索引优化好 | 学习曲线陡、社区相对小 | 复杂检索场景 |
| **Haystack** | 企业级、Pipeline清晰 | 较重、配置复杂 | 企业级应用 |

**推荐**: LangChain 0.3.x（生态完善，与现有Flask集成简单）

### 2.2 向量数据库选型

#### 2.2.1 方案详细对比

| 特性 | Chroma | Milvus | pgvector | Weaviate |
|------|--------|--------|----------|----------|
| **部署方式** | 嵌入式/独立 | 独立服务 | PostgreSQL插件 | 独立服务 |
| **数据规模** | <100万 | 十亿级 | <1000万 | 亿级 |
| **性能** | 中等 | 优秀 | 中等 | 优秀 |
| **功能丰富度** | 基础 | 丰富 | 基础 | 丰富 |
| **运维成本** | 低 | 中 | 低 | 中 |
| **混合检索** | 不支持 | 支持 | 支持 | 支持 |
| **多租户** | 不支持 | 支持 | 需自行实现 | 支持 |

#### 2.2.2 推荐方案

**阶段一：开发/测试环境**
- 使用 **Chroma** 嵌入式模式
- 数据持久化到 `./data/chroma`
- 零运维成本，快速启动

**阶段二：生产环境**
- 使用 **Milvus** 独立部署
- 支持多租户（按知识库隔离 Collection）
- 支持混合检索（向量+关键词）
- 提供监控和运维工具

**阶段三：大规模生产**
- 考虑 **Milvus Cluster** 模式
- 或迁移到 **Zilliz Cloud**（托管服务）

### 2.3 文档处理技术栈

#### 2.3.1 文档解析方案

| 格式 | 推荐库 | 备选库 | 处理要点 |
|------|--------|--------|---------|
| **PDF** | PyMuPDF (fitz) | pdfplumber, pdf2image | 支持文本提取、图片提取、表格识别 |
| **Word** | python-docx | mammoth | 保留段落结构、图片提取 |
| **PPT** | python-pptx | - | 按幻灯片分页、备注提取 |
| **Excel** | openpyxl | pandas | 多Sheet处理、表格转文本 |
| **Markdown** | markdown | mistune | 保留格式标记 |
| **HTML** | BeautifulSoup | trafilatura | 正文提取、标签过滤 |

#### 2.3.2 图片 OCR 方案

| 方案 | 引擎 | 优点 | 缺点 | 推荐场景 |
|------|------|------|------|---------|
| **PaddleOCR** | PP-OCRv4 | 中文效果极佳、免费 | 模型较大(100MB+) | 中文文档为主 |
| **Tesseract** | Tesseract 5 | 轻量、多语言 | 中文效果一般 | 英文文档为主 |
| **EasyOCR** | CRAFT+CRNN | 多语言支持好 | 速度较慢 | 多语言混合 |
| **API服务** | 百度/腾讯/阿里OCR | 效果最佳 | 按量付费 | 高精度要求 |

**推荐**: PaddleOCR（中文场景首选，可本地部署）

#### 2.3.3 视频处理方案

```
视频文件
    │
    ├─> 音频提取 ──> Whisper ──> 语音转文字
    │
    └─> 关键帧提取 ──> OCR/CLIP ──> 画面内容描述
```

| 组件 | 推荐方案 | 说明 |
|------|---------|------|
| 音频提取 | ffmpeg-python | 提取音频轨道 |
| 语音识别 | openai-whisper | 本地部署，多语言支持 |
| 关键帧提取 | opencv-python | 按时间间隔提取帧 |
| 画面理解 | CLIP / Qwen-VL | 生成画面描述（可选） |

### 2.4 网络爬虫与搜索技术栈

#### 2.4.1 网页抓取方案

| 方案 | 适用场景 | 技术栈 | 反爬能力 |
|------|---------|--------|---------|
| **静态页面** | 新闻、博客 | requests + BeautifulSoup | 弱 |
| **动态页面** | SPA应用、需要JS渲染 | Playwright / Selenium | 中 |
| **大规模爬取** | 站点全站抓取 | Scrapy | 强 |

**推荐**: Playwright（支持动态渲染，反爬能力强）

#### 2.4.2 内容清洗方案

| 库 | 功能 | 优点 |
|----|------|------|
| **trafilatura** | 正文提取 | 准确率高、自动去噪 |
| **newspaper3k** | 新闻提取 | 针对新闻优化 |
| **readability-lxml** | 可读性提取 | 轻量快速 |

#### 2.4.3 搜索引擎 API

| 服务 | 免费额度 | 价格 | 特点 |
|------|---------|------|------|
| **Tavily** | 1000次/月 | $0.025/次 | 专为AI设计，返回结构化结果 |
| **SerpAPI** | 100次/月 | $0.005/次 | Google搜索结果 |
| **DuckDuckGo** | 免费 | 免费 | 无需API Key，有限流 |
| **Bing Search** | 1000次/月 | $7/1000次 | 微软生态 |

**推荐**: Tavily（专为LLM设计，返回内容已清洗）

## 三、新增模块设计

### 3.1 项目目录结构扩展

```
app/
├── controllers/
│   ├── article/          # 现有
│   ├── knowledge/        # 新增：知识库管理
│   │   ├── __init__.py
│   │   ├── knowledge_api_model.py
│   │   ├── knowledge_manager.py      # 知识库CRUD
│   │   ├── document_manager.py       # 文档上传/处理
│   │   └── chat_manager.py           # 智能问答接口
│   └── crawler/          # 新增：爬虫服务
│       ├── __init__.py
│       ├── web_crawler.py            # 网页抓取
│       └── search_engine.py          # 搜索引擎集成
├── models/
│   └── entities/
│       ├── article.py    # 现有
│       ├── knowledge_base.py         # 新增：知识库实体
│       ├── document.py               # 新增：文档实体
│       └── chat_history.py           # 新增：对话历史
├── services/             # 新增：服务层
│   ├── __init__.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── llm_factory.py            # LLM工厂类
│   │   ├── embedding_service.py      # 向量化服务
│   │   └── rag_service.py            # RAG检索服务
│   ├── document/
│   │   ├── __init__.py
│   │   ├── parser_factory.py         # 文档解析工厂
│   │   ├── pdf_parser.py
│   │   ├── word_parser.py
│   │   ├── ppt_parser.py
│   │   ├── image_parser.py           # OCR处理
│   │   └── video_parser.py           # 视频处理
│   └── crawler/
│       ├── __init__.py
│       ├── web_scraper.py            # 网页内容提取
│       └── content_summarizer.py     # 内容总结
├── utils/
│   ├── vector_store.py               # 新增：向量存储工具
│   └── text_splitter.py              # 新增：文本分块工具
└── extension.py          # 扩展：添加向量数据库连接
```

### 3.2 数据模型设计

#### 3.2.1 知识库表 (knowledge_base)

```python
class KnowledgeBase(db.Model):
    """知识库主表"""
    __tablename__ = 'knowledge_base'
    
    # 主键与关联
    id = db.Column(db.String(36), primary_key=True, comment='知识库唯一ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True, comment='创建者ID')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True, comment='所属项目ID')
    
    # 基本信息
    name = db.Column(db.String(255), nullable=False, comment='知识库名称')
    description = db.Column(db.Text, nullable=True, comment='知识库描述')
    icon = db.Column(db.String(255), nullable=True, comment='知识库图标URL')
    
    # AI配置
    embedding_model = db.Column(db.String(64), default='bge-large-zh-v1.5', comment='使用的embedding模型')
    llm_model = db.Column(db.String(64), default='glm-4-flash', comment='默认对话模型')
    vector_collection = db.Column(db.String(64), nullable=False, unique=True, comment='向量库collection名称')
    
    # 处理配置
    chunk_size = db.Column(db.Integer, default=500, comment='文本分块大小')
    chunk_overlap = db.Column(db.Integer, default=50, comment='文本分块重叠大小')
    
    # 统计信息
    document_count = db.Column(db.Integer, default=0, comment='文档数量')
    total_chunks = db.Column(db.Integer, default=0, comment='总块数')
    total_tokens = db.Column(db.BigInteger, default=0, comment='总token数')
    
    # 状态管理
    status = db.Column(db.String(32), default='ACTIVE', comment='状态: ACTIVE/ARCHIVED/DELETED')
    is_public = db.Column(db.Boolean, default=False, comment='是否公开分享')
    
    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    # 关联关系
    user = db.relationship('User', backref='knowledge_bases')
    project = db.relationship('Project', backref='knowledge_bases')
    documents = db.relationship('Document', backref='knowledge_base', lazy='dynamic', cascade='all, delete-orphan')
    
    # 索引
    __table_args__ = (
        db.Index('idx_kb_user_project', 'user_id', 'project_id'),
        db.Index('idx_kb_status', 'status'),
    )
```

#### 3.2.2 文档表 (document)

```python
class Document(db.Model):
    """知识库文档表"""
    __tablename__ = 'document'
    
    # 主键与关联
    id = db.Column(db.String(36), primary_key=True, comment='文档唯一ID')
    knowledge_base_id = db.Column(db.String(36), db.ForeignKey('knowledge_base.id'), nullable=False, index=True, comment='所属知识库ID')
    
    # 来源信息
    source_type = db.Column(db.String(32), nullable=False, comment='来源类型: ARTICLE/FILE/URL/NOTE')
    source_id = db.Column(db.String(36), nullable=True, comment='关联的article_id或其他来源ID')
    source_url = db.Column(db.String(2048), nullable=True, comment='原始URL（如果是网页抓取）')
    
    # 文件信息
    file_type = db.Column(db.String(32), nullable=False, comment='文件类型: PDF/DOCX/PPTX/XLSX/MD/TXT/IMAGE/VIDEO/HTML/OTHER')
    file_name = db.Column(db.String(255), nullable=False, comment='原始文件名')
    file_path = db.Column(db.String(512), nullable=True, comment='文件存储路径')
    file_size = db.Column(db.BigInteger, default=0, comment='文件大小(字节)')
    file_hash = db.Column(db.String(64), nullable=True, index=True, comment='文件MD5哈希（用于去重）')
    
    # 内容信息
    title = db.Column(db.String(512), nullable=True, comment='文档标题')
    content_preview = db.Column(db.Text, nullable=True, comment='内容预览（前500字符）')
    content_length = db.Column(db.Integer, default=0, comment='内容总字符数')
    language = db.Column(db.String(16), default='zh', comment='内容语言')
    
    # 处理状态
    embed_status = db.Column(db.String(32), default='PENDING', comment='向量化状态: PENDING/PROCESSING/COMPLETED/FAILED')
    process_error = db.Column(db.Text, nullable=True, comment='处理错误信息')
    chunk_count = db.Column(db.Integer, default=0, comment='分块数量')
    
    # 元数据
    meta_data = db.Column(db.JSON, nullable=True, comment='额外元数据（作者、页数等）')
    tags = db.Column(db.JSON, nullable=True, comment='标签列表')
    
    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    process_time = db.Column(db.DateTime, nullable=True, comment='处理完成时间')
    
    # 关联关系
    chunks = db.relationship('DocumentChunk', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    
    # 索引
    __table_args__ = (
        db.Index('idx_doc_kb_status', 'knowledge_base_id', 'embed_status'),
        db.Index('idx_doc_source', 'source_type', 'source_id'),
        db.Index('idx_doc_type', 'file_type'),
    )
```

#### 3.2.3 文档分块表 (document_chunk)

```python
class DocumentChunk(db.Model):
    """文档分块表 - 记录每个文本块的信息，便于溯源"""
    __tablename__ = 'document_chunk'
    
    id = db.Column(db.String(36), primary_key=True, comment='块唯一ID')
    document_id = db.Column(db.String(36), db.ForeignKey('document.id'), nullable=False, index=True, comment='所属文档ID')
    knowledge_base_id = db.Column(db.String(36), db.ForeignKey('knowledge_base.id'), nullable=False, index=True, comment='所属知识库ID')
    
    # 块内容
    chunk_index = db.Column(db.Integer, nullable=False, comment='块序号')
    content = db.Column(db.Text, nullable=False, comment='块内容')
    content_length = db.Column(db.Integer, default=0, comment='内容长度')
    token_count = db.Column(db.Integer, default=0, comment='token数量')
    
    # 位置信息（用于溯源）
    page_number = db.Column(db.Integer, nullable=True, comment='页码（PDF等）')
    start_char = db.Column(db.Integer, nullable=True, comment='起始字符位置')
    end_char = db.Column(db.Integer, nullable=True, comment='结束字符位置')
    
    # 向量ID（在向量数据库中的ID）
    vector_id = db.Column(db.String(64), nullable=True, unique=True, comment='向量数据库中的ID')
    
    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 索引
    __table_args__ = (
        db.Index('idx_chunk_doc', 'document_id', 'chunk_index'),
        db.Index('idx_chunk_kb', 'knowledge_base_id'),
    )
```

#### 3.2.4 对话会话表 (chat_session)

```python
class ChatSession(db.Model):
    """对话会话表"""
    __tablename__ = 'chat_session'
    
    id = db.Column(db.String(36), primary_key=True, comment='会话唯一ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True, comment='用户ID')
    knowledge_base_id = db.Column(db.String(36), db.ForeignKey('knowledge_base.id'), nullable=True, index=True, comment='关联知识库ID')
    
    # 会话信息
    title = db.Column(db.String(255), nullable=True, comment='会话标题（自动生成的摘要）')
    session_type = db.Column(db.String(32), default='KNOWLEDGE', comment='会话类型: KNOWLEDGE/WEB_SEARCH/CHAT')
    
    # 配置
    llm_model = db.Column(db.String(64), nullable=True, comment='使用的模型')
    temperature = db.Column(db.Float, default=0.7, comment='温度参数')
    
    # 统计
    message_count = db.Column(db.Integer, default=0, comment='消息数量')
    total_tokens = db.Column(db.BigInteger, default=0, comment='总token消耗')
    
    # 状态
    is_pinned = db.Column(db.Boolean, default=False, comment='是否置顶')
    status = db.Column(db.String(32), default='ACTIVE', comment='状态: ACTIVE/ARCHIVED')
    
    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    # 关联关系
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    # 索引
    __table_args__ = (
        db.Index('idx_session_user', 'user_id', 'update_time'),
        db.Index('idx_session_kb', 'knowledge_base_id'),
    )
```

#### 3.2.5 对话消息表 (chat_message)

```python
class ChatMessage(db.Model):
    """对话消息表"""
    __tablename__ = 'chat_message'
    
    id = db.Column(db.String(36), primary_key=True, comment='消息唯一ID')
    session_id = db.Column(db.String(36), db.ForeignKey('chat_session.id'), nullable=False, index=True, comment='所属会话ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True, comment='用户ID')
    
    # 消息内容
    role = db.Column(db.String(16), nullable=False, comment='角色: user/assistant/system')
    content = db.Column(db.Text, nullable=False, comment='消息内容')
    content_type = db.Column(db.String(32), default='TEXT', comment='内容类型: TEXT/MARKDOWN/HTML')
    
    # 引用来源（RAG检索结果）
    sources = db.Column(db.JSON, nullable=True, comment='引用来源列表')
    """
    sources格式示例:
    [
        {
            "document_id": "xxx",
            "document_name": "xxx.pdf",
            "chunk_id": "xxx",
            "content_preview": "...",
            "similarity": 0.95,
            "page_number": 5
        }
    ]
    """
    
    # 搜索信息（如果是联网搜索）
    search_results = db.Column(db.JSON, nullable=True, comment='搜索结果')
    
    # Token消耗
    prompt_tokens = db.Column(db.Integer, default=0, comment='输入token数')
    completion_tokens = db.Column(db.Integer, default=0, comment='输出token数')
    total_tokens = db.Column(db.Integer, default=0, comment='总token数')
    
    # 性能指标
    response_time = db.Column(db.Integer, nullable=True, comment='响应时间(ms)')
    
    # 反馈
    feedback = db.Column(db.String(16), nullable=True, comment='用户反馈: like/dislike')
    feedback_comment = db.Column(db.Text, nullable=True, comment='反馈评论')
    
    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 索引
    __table_args__ = (
        db.Index('idx_msg_session', 'session_id', 'create_time'),
        db.Index('idx_msg_user', 'user_id', 'create_time'),
    )
```

#### 3.2.6 数据模型关系图

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│      User       │         │     Project     │         │    Category     │
│   (现有表)      │         │   (现有表)      │         │   (现有表)      │
└────────┬────────┘         └────────┬────────┘         └─────────────────┘
         │                           │
         │ 1:N                       │ 1:N
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│ KnowledgeBase   │◄────────│  Article        │
│   (知识库表)     │  N:1    │   (现有表)      │
│                 │         │                 │
│ - id            │         │ - id            │
│ - user_id       │         │ - category_id   │
│ - project_id    │         │ - title         │
│ - name          │         │ - content       │
│ - embedding_model│        │ - ...           │
│ - vector_collection│      └─────────────────┘
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐         ┌─────────────────┐
│    Document     │◄────────│ DocumentChunk   │
│   (文档表)       │  1:N    │   (分块表)       │
│                 │         │                 │
│ - id            │         │ - id            │
│ - knowledge_base_id      │ - document_id   │
│ - source_type   │         │ - chunk_index   │
│ - file_type     │         │ - content       │
│ - file_path     │         │ - vector_id     │
│ - embed_status  │         └─────────────────┘
└─────────────────┘
         ▲
         │ N:1 (source_type='ARTICLE'时)
         │
┌─────────────────┐
│  ChatSession    │         ┌─────────────────┐
│  (会话表)        │◄────────│  ChatMessage    │
│                 │  1:N    │   (消息表)       │
│ - id            │         │                 │
│ - user_id       │         │ - id            │
│ - knowledge_base_id      │ - session_id    │
│ - title         │         │ - role          │
│ - session_type  │         │ - content       │
│ - message_count │         │ - sources       │
└─────────────────┘         │ - total_tokens  │
                            └─────────────────┘
```

### 3.3 与现有 Article 模块的集成

#### 3.3.1 集成架构设计

现有文章系统与知识库系统的双向集成方案：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         现有 Article 系统                                    │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │  article    │    │  category   │    │   project   │                     │
│  │   表        │    │    表       │    │    表       │                     │
│  └──────┬──────┘    └─────────────┘    └─────────────┘                     │
│         │                                                                   │
│         │ 1. 创建/更新文章                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────┐                                   │
│  │     ArticleManager (article_manager.py)                                  │
│  │     - add_article()                                                 │
│  │     - update_article()                                              │
│  │     - delete_article()                                              │
│  └──────────────┬──────────────────────┘                                   │
│                 │                                                           │
│                 │ 2. 触发同步（可选）                                         │
│                 ▼                                                           │
│  ┌─────────────────────────────────────┐                                   │
│  │     KnowledgeSyncService                                            │
│  │     - sync_article_to_kb()          │ 同步文章到知识库                  │
│  │     - remove_article_from_kb()      │ 从知识库移除                      │
│  └──────────────┬──────────────────────┘                                   │
└─────────────────┼───────────────────────────────────────────────────────────┘
                  │
                  ▼ 写入
┌─────────────────────────────────────────────────────────────────────────────┐
│                         知识库系统                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Document 表                                  │   │
│  │  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐ │   │
│  │  │     id      │  source_type│  source_id  │  knowledge_base_id  │ │   │
│  │  ├─────────────┼─────────────┼─────────────┼─────────────────────┤ │   │
│  │  │  doc_001    │  ARTICLE    │  art_123    │  kb_456             │ │   │
│  │  │  doc_002    │  FILE       │  NULL       │  kb_456             │ │   │
│  │  │  doc_003    │  URL        │  NULL       │  kb_789             │ │   │
│  │  └─────────────┴─────────────┴─────────────┴─────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼ 1:N                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      DocumentChunk 表                                │   │
│  │  - 文章内容分块存储                                                  │   │
│  │  - 支持向量检索                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3.3.2 集成实现方案

**方案一：自动同步模式（推荐）**

在 `article_manager.py` 中集成同步逻辑：

```python
# 在 ArticleManager 中添加同步钩子
class ArticleResource(Resource):
    @jwt_required()
    def put(self, article_id):
        # ... 原有更新逻辑 ...
        
        # 同步到知识库
        if article.category and article.category.knowledge_base_id:
            KnowledgeSyncService.sync_article_to_kb(
                article_id=article.id,
                knowledge_base_id=article.category.knowledge_base_id
            )
```

**方案二：手动导入模式**

提供独立接口，允许用户选择文章导入知识库：

```python
# knowledge_manager.py
class KnowledgeArticleImportResource(Resource):
    @jwt_required()
    def post(self, knowledge_base_id):
        """批量导入文章到知识库"""
        parser = reqparse.RequestParser()
        parser.add_argument('article_ids', type=list, required=True, help='文章ID列表')
        parser.add_argument('category_id', type=int, required=False, help='筛选特定目录')
        args = parser.parse_args()
        
        # 查询文章并导入
        articles = Article.query.filter(
            Article.id.in_(args['article_ids']),
            Article.is_deleted == False
        ).all()
        
        for article in articles:
            KnowledgeSyncService.sync_article_to_kb(
                article_id=article.id,
                knowledge_base_id=knowledge_base_id
            )
```

#### 3.3.3 数据映射关系

| Article 字段 | Document 字段 | 说明 |
|-------------|--------------|------|
| id | source_id | 关联ID |
| title | title | 标题映射 |
| content | content_preview | 内容预览 |
| category_id | - | 通过目录关联知识库 |
| type | meta_data['article_type'] | 文章类型 |
| status | - | 仅同步 ACTIVE 状态 |
| create_time | create_time | 创建时间 |
| update_time | update_time | 更新时间 |

#### 3.3.4 同步策略

```python
class KnowledgeSyncService:
    """知识库同步服务"""
    
    @staticmethod
    def sync_article_to_kb(article_id: str, knowledge_base_id: str):
        """同步文章到知识库"""
        article = Article.query.get(article_id)
        if not article or article.is_deleted:
            return False, "文章不存在或已删除"
        
        # 查找或创建文档记录
        document = Document.query.filter_by(
            source_type='ARTICLE',
            source_id=article_id,
            knowledge_base_id=knowledge_base_id
        ).first()
        
        if document:
            # 更新现有文档
            document.title = article.title
            document.content_preview = article.content[:500]
            document.update_time = datetime.now()
            document.embed_status = 'PENDING'  # 标记需要重新向量化
        else:
            # 创建新文档
            document = Document(
                id=str(uuid.uuid4()),
                knowledge_base_id=knowledge_base_id,
                source_type='ARTICLE',
                source_id=article_id,
                file_type='MARKDOWN',
                title=article.title,
                content_preview=article.content[:500],
                embed_status='PENDING'
            )
            db.session.add(document)
        
        db.session.commit()
        
        # 触发异步向量化任务
        from tasks import process_document_task
        process_document_task.delay(document.id)
        
        return True, document
    
    @staticmethod
    def remove_article_from_kb(article_id: str, knowledge_base_id: str = None):
        """从知识库移除文章"""
        query = Document.query.filter_by(
            source_type='ARTICLE',
            source_id=article_id
        )
        if knowledge_base_id:
            query = query.filter_by(knowledge_base_id=knowledge_base_id)
        
        documents = query.all()
        for doc in documents:
            # 删除向量数据
            VectorStoreService.delete_document_chunks(doc.id)
            # 删除文档记录
            db.session.delete(doc)
        
        db.session.commit()
        return True
```

## 四、核心功能流程

### 4.1 文档处理与向量化流程

#### 4.1.1 完整处理流程

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           文档处理与向量化流程                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

用户上传/导入
      │
      ▼
┌─────────────────┐     失败     ┌─────────────────┐
│   1. 文件接收    │─────────────>│   错误处理       │
│   - 格式验证     │              │   - 记录日志     │
│   - 大小检查     │              │   - 返回错误     │
│   - 病毒扫描     │              └─────────────────┘
└────────┬────────┘
         │ 成功
         ▼
┌─────────────────┐     失败     ┌─────────────────┐
│   2. 文件存储    │─────────────>│   错误处理       │
│   - 生成唯一ID   │              └─────────────────┘
│   - 存储到磁盘   │
│   - 计算文件哈希 │
└────────┬────────┘
         │ 成功
         ▼
┌─────────────────┐     失败     ┌─────────────────┐
│   3. 格式识别    │─────────────>│   标记失败       │
│   - 扩展名识别   │              │   - 等待重试     │
│   - MIME检测    │              └─────────────────┘
│   - 文件头校验   │
└────────┬────────┘
         │ 成功
         ▼
┌─────────────────────────────────────────────────────────┐
│   4. 文档解析（根据格式选择解析器）                       │
│                                                          │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│   │  PDF     │  │  Word    │  │  PPT     │  │  Image  │ │
│   │ 解析器   │  │ 解析器   │  │ 解析器   │  │ OCR     │ │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│        │             │             │             │      │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│   │  Video   │  │  Audio   │  │  HTML    │  │  Text   │ │
│   │ 解析器   │  │ 解析器   │  │ 解析器   │  │ 解析器  │ │
│   └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │ 提取文本内容
                         ▼
┌─────────────────┐     失败     ┌─────────────────┐
│   5. 内容预处理  │─────────────>│   标记失败       │
│   - 编码统一     │              └─────────────────┘
│   - 特殊字符清理 │
│   - 空白规范化   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│   6. 文本分块 (Text Splitter)                            │
│                                                          │
│   输入: "这是一段很长的文本内容..."                         │
│                                                          │
│   策略: RecursiveCharacterTextSplitter                   │
│   - chunk_size: 500 (可配置)                              │
│   - chunk_overlap: 50 (可配置)                            │
│   - separators: ["\n\n", "\n", "。", " ", ""]             │
│                                                          │
│   输出: [块1, 块2, 块3, ...]                              │
│   ┌────────┐ ┌────────┐ ┌────────┐                      │
│   │ 块1    │ │ 块2    │ │ 块3    │ ...                   │
│   │ 0-500  │ │ 450-950│ │900-1400│                      │
│   └────────┘ └────────┘ └────────┘                      │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   7. 元数据提取  │ │   8. 关键词提取  │ │   9. 摘要生成   │
│   - 标题         │ │   - TF-IDF      │ │   (可选)        │
│   - 作者         │ │   - TextRank    │ │                 │
│   - 页数         │ │                 │ │                 │
└────────┬────────┘ └─────────────────┘ └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│   10. Embedding 向量化                                   │
│                                                          │
│   批量处理:                                              │
│   for chunk in chunks:                                   │
│       embedding = embedding_model.encode(chunk)          │
│       vector_id = vector_store.add(embedding, metadata)  │
│                                                          │
│   优化策略:                                              │
│   - 批量编码 (batch_size=32)                             │
│   - 异步处理 (Celery)                                    │
│   - 进度追踪                                             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────┐
│   11. 完成标记   │
│   - 更新状态     │
│   - 记录统计     │
│   - 发送通知     │
└─────────────────┘
```

#### 4.1.2 异常处理与重试机制

| 阶段 | 可能的错误 | 处理策略 | 重试次数 |
|------|-----------|---------|---------|
| 文件接收 | 格式不支持 | 返回明确错误信息 | 0 |
| 文件存储 | 磁盘满/权限 | 清理临时文件，延迟重试 | 3 |
| 文档解析 | 文件损坏 | 记录错误，跳过处理 | 0 |
| 文本分块 | 内容为空 | 标记为空文档 | 0 |
| Embedding | API限流/超时 | 指数退避重试 | 5 |
| 向量存储 | 连接失败 | 延迟重试 | 3 |

### 4.2 RAG 智能问答流程

#### 4.2.1 完整问答流程

```
用户提问
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. 请求预处理                                                    │
│  - 参数验证 (question, knowledge_base_id, session_id)            │
│  - 权限检查 (用户是否有该知识库访问权限)                           │
│  - 输入过滤 (敏感词、SQL注入等)                                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. 会话管理                                                      │
│  - 获取或创建 session                                            │
│  - 加载历史消息 (最近 N 条)                                        │
│  - 构建对话上下文                                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. 查询重写与扩展 (可选)                                          │
│  - HyDE (Hypothetical Document Embeddings)                       │
│  - 查询扩展 (Query Expansion)                                     │
│  - 多查询生成 (Multi-Query)                                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. 向量检索                                                       │
│                                                                  │
│  question ──> Embedding Model ──> query_vector                   │
│                                          │                       │
│                                          ▼                       │
│                          ┌───────────────────────────┐           │
│                          │    向量数据库检索          │           │
│                          │  - 相似度计算 (cosine)     │           │
│                          │  - Top-K 召回 (K=10)       │           │
│                          │  - 相似度阈值过滤          │           │
│                          └───────────────┬───────────┘           │
│                                          │                       │
│  召回结果: [chunk_1, chunk_2, ..., chunk_k]                      │
│  (相似度: 0.95, 0.92, 0.89, ...)                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. 重排序 (Re-ranking) (可选)                                    │
│  - Cross-Encoder 重排序                                           │
│  - 基于历史点击的个性化排序                                         │
│  - 多样性增强 (MMR: Maximal Marginal Relevance)                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. 上下文构建                                                    │
│                                                                  │
│  system_prompt = """你是一个专业的知识库助手..."""                │
│                                                                  │
│  context = """基于以下参考资料回答问题：\n\n"""                    │
│  for i, chunk in enumerate(retrieved_chunks[:5]):                │
│      context += f"[文档{i+1}] {chunk.document.title}\n"           │
│      context += f"{chunk.content}\n\n"                           │
│                                                                  │
│  user_prompt = f"问题：{question}\n请基于上述资料回答。"          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. LLM 生成回答                                                  │
│                                                                  │
│  messages = [                                                    │
│      {"role": "system", "content": system_prompt},               │
│      *history_messages,                                          │
│      {"role": "user", "content": user_prompt}                    │
│  ]                                                               │
│                                                                  │
│  response = llm.chat_completion(                                 │
│      messages=messages,                                          │
│      temperature=0.7,                                            │
│      stream=True  # 流式输出                                     │
│  )                                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. 后处理与溯源                                                   │
│  - 答案格式化 (Markdown)                                          │
│  - 引用标注 [^1^] [^2^]                                           │
│  - 来源链接生成                                                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  9. 结果存储                                                      │
│  - 保存用户消息到 chat_message                                    │
│  - 保存助手回复到 chat_message                                    │
│  - 更新会话统计 (message_count, total_tokens)                     │
│  - 异步记录日志                                                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  10. 响应返回                                                     │
│  {                                                               │
│      "code": 200,                                                │
│      "message": "success",                                       │
│      "data": {                                                   │
│          "answer": "根据资料，...",                              │
│          "sources": [                                            │
│              {"doc_id": "xxx", "title": "...", "page": 5},       │
│              ...                                                 │
│          ],                                                      │
│          "session_id": "sess_xxx",                               │
│          "tokens": {"prompt": 1500, "completion": 500}           │
│      }                                                           │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.2.2 RAG 优化策略

| 优化点 | 策略 | 效果 |
|--------|------|------|
| **查询理解** | HyDE、查询扩展 | 提升召回率 15-20% |
| **检索质量** | 混合检索 (向量+关键词) | 提升准确率 10-15% |
| **重排序** | Cross-Encoder 重排 | 提升相关性 20% |
| **上下文压缩** | 语义压缩、关键词提取 | 减少 token 消耗 30% |
| **缓存优化** | 查询缓存、Embedding 缓存 | 降低延迟 50% |

### 4.3 网页抓取与总结流程

#### 4.3.1 网页内容处理流程

```
用户输入 URL
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. URL 预处理                                                    │
│  - 格式验证                                                       │
│  - 协议补全 (http/https)                                          │
│  - 域名解析检查                                                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. 网页抓取                                                      │
│                                                                  │
│  方案 A: 静态页面 (requests + BeautifulSoup)                      │
│  ┌─────────────────────────────────────────────┐                 │
│  │  - 发送 HTTP 请求                            │                 │
│  │  - 设置 User-Agent、Referer                 │                 │
│  │  - 处理重定向 (max_redirects=5)              │                 │
│  │  - 超时控制 (timeout=30s)                    │                 │
│  └─────────────────────────────────────────────┘                 │
│                                                                  │
│  方案 B: 动态页面 (Playwright)                                     │
│  ┌─────────────────────────────────────────────┐                 │
│  │  - 启动 headless 浏览器                      │                 │
│  │  - 等待页面加载完成 (networkidle)            │                 │
│  │  - 执行 JavaScript                           │                 │
│  │  - 滚动加载更多内容                          │                 │
│  │  - 关闭浏览器                                │                 │
│  └─────────────────────────────────────────────┘                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. 内容清洗与提取                                                 │
│                                                                  │
│  输入: 原始 HTML                                                 │
│                                                                  │
│  处理:                                                           │
│  ┌─────────────────────────────────────────────┐                 │
│  │  - 移除 script、style、nav、footer 等标签    │                 │
│  │  - 提取 title、meta description             │                 │
│  │  - 使用 trafilatura 提取正文                 │                 │
│  │  - 保留段落结构                              │                 │
│  │  - 处理相对链接转为绝对链接                  │                 │
│  └─────────────────────────────────────────────┘                 │
│                                                                  │
│  输出: {                                                         │
│      "title": "页面标题",                                        │
│      "url": "原始URL",                                           │
│      "content": "正文内容...",                                   │
│      "publish_date": "2024-01-01",                               │
│      "author": "作者",                                           │
│      "images": ["img1.jpg", "img2.jpg"]                          │
│  }                                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  4A. 直接存储    │ │  4B. LLM总结    │ │  4C. 问答提取   │
│  到知识库       │ │                 │ │                 │
│                 │ │  输入: 正文     │ │  输入: 正文     │
│  - 创建 Document│ │  输出: 摘要     │ │  输出: FAQ列表  │
│  - 触发向量化   │ │                 │ │                 │
│                 │ │  Prompt:        │ │  Prompt:        │
│                 │ │  "请总结以下    │ │  "从以下内容    │
│                 │ │  文章的核心    │ │  提取关键问答   │
│                 │ │  观点和要点..." │ │  对..."         │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

#### 4.3.2 内容总结策略

```python
class ContentSummarizer:
    """内容总结服务"""
    
    SUMMARY_PROMPT = """请对以下内容进行总结：

要求：
1. 提取核心观点和关键信息
2. 保持逻辑清晰，分点陈述
3. 保留重要的数据、事实和引用
4. 总结长度控制在原文的 20% 以内

内容：
{content}

请按以下格式输出：
## 核心观点
...

## 关键要点
1. ...
2. ...

## 重要细节
- ...
"""

    @staticmethod
    def summarize(content: str, max_length: int = 4000) -> str:
        """长文本总结（支持分块处理）"""
        if len(content) <= max_length:
            # 直接总结
            return llm.generate(SUMMARY_PROMPT.format(content=content))
        
        # 长文本分块总结
        chunks = TextSplitter.split(content, chunk_size=max_length)
        chunk_summaries = []
        
        for chunk in chunks:
            summary = llm.generate(SUMMARY_PROMPT.format(content=chunk))
            chunk_summaries.append(summary)
        
        # 合并总结
        combined = "\n\n".join(chunk_summaries)
        return llm.generate(SUMMARY_PROMPT.format(content=combined))
```

### 4.4 网络搜索问答流程

```
用户提问
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. 搜索查询生成                                                  │
│  - 从问题提取关键词                                               │
│  - 生成多个搜索变体                                               │
│  - 添加时间/地域限定词 (可选)                                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. 执行搜索                                                      │
│                                                                  │
│  调用搜索 API (Tavily/SerpAPI/DuckDuckGo)                        │
│  ┌─────────────────────────────────────────────┐                 │
│  │  参数:                                       │                 │
│  │  - query: 搜索词                             │                 │
│  │  - num_results: 10                           │                 │
│  │  - time_range: "d" (当天) / "w" (本周)        │                 │
│  │  - include_domains: []                       │                 │
│  │  - exclude_domains: []                       │                 │
│  └─────────────────────────────────────────────┘                 │
│                                                                  │
│  返回: [{title, url, snippet, content}, ...]                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. 结果筛选与去重                                                │
│  - 基于相似度去重                                                 │
│  - 基于域名可信度排序                                              │
│  - 过滤低质量内容                                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. 内容抓取（可选）                                               │
│  - 对重要结果进行全文抓取                                          │
│  - 使用 trafilatura 提取正文                                      │
│  - 限制抓取深度和数量                                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. 构建回答上下文                                                │
│                                                                  │
│  context = """基于以下搜索结果回答问题：\n\n"""                    │
│  for i, result in enumerate(search_results[:5]):                 │
│      context += f"[{i+1}] {result.title}\n"                       │
│      context += f"来源: {result.url}\n"                           │
│      context += f"内容: {result.content[:500]}...\n\n"            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. LLM 生成回答                                                  │
│  - 使用与 RAG 相同的 Prompt 模板                                  │
│  - 要求标注信息来源 [^1^]                                         │
│  - 提醒验证信息时效性                                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. 返回结果                                                      │
│  {                                                               │
│      "answer": "根据搜索结果...",                                │
│      "sources": [                                                │
│          {"title": "...", "url": "...", "snippet": "..."},       │
│          ...                                                     │
│      ],                                                          │
│      "search_query": "原始搜索词",                               │
│      "search_time": "2024-01-01 12:00:00"                        │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## 五、API 接口设计

### 5.1 知识库管理接口

#### 5.1.1 创建知识库

```http
POST /api/knowledge
Authorization: Bearer <jwt_token>
X-Project-Id: <project_id>

Request:
{
    "name": "产品文档知识库",           // required, 2-100字符
    "description": "存储产品相关文档",   // optional, max 500字符
    "icon": "https://...",              // optional, 图标URL
    "embedding_model": "bge-large-zh-v1.5", // optional, default: bge-large-zh-v1.5
    "llm_model": "glm-4-flash",         // optional, default: glm-4-flash
    "chunk_size": 500,                  // optional, default: 500
    "chunk_overlap": 50,                // optional, default: 50
    "is_public": false                  // optional, default: false
}

Response 200:
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "kb_xxx",
        "name": "产品文档知识库",
        "description": "存储产品相关文档",
        "embedding_model": "bge-large-zh-v1.5",
        "vector_collection": "kb_kb_xxx_v1",
        "document_count": 0,
        "create_time": "2024-01-01T12:00:00Z"
    }
}

Response 400:
{
    "code": 400,
    "message": "知识库名称已存在"
}
```

#### 5.1.2 获取知识库列表

```http
GET /api/knowledge?page=1&size=20&keyword=产品
Authorization: Bearer <jwt_token>
X-Project-Id: <project_id>  // optional, 筛选特定项目

Response 200:
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 15,
        "page": 1,
        "size": 20,
        "list": [
            {
                "id": "kb_xxx",
                "name": "产品文档知识库",
                "description": "...",
                "document_count": 25,
                "total_chunks": 1500,
                "status": "ACTIVE",
                "create_time": "2024-01-01T12:00:00Z",
                "update_time": "2024-01-15T10:30:00Z"
            }
        ]
    }
}
```

#### 5.1.3 获取知识库详情

```http
GET /api/knowledge/{knowledge_base_id}
Authorization: Bearer <jwt_token>

Response 200:
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "kb_xxx",
        "name": "产品文档知识库",
        "description": "...",
        "user_id": 1,
        "project_id": 2,
        "embedding_model": "bge-large-zh-v1.5",
        "llm_model": "glm-4-flash",
        "chunk_size": 500,
        "chunk_overlap": 50,
        "document_count": 25,
        "total_chunks": 1500,
        "total_tokens": 500000,
        "status": "ACTIVE",
        "is_public": false,
        "create_time": "2024-01-01T12:00:00Z",
        "update_time": "2024-01-15T10:30:00Z"
    }
}
```

#### 5.1.4 更新知识库

```http
PUT /api/knowledge/{knowledge_base_id}
Authorization: Bearer <jwt_token>

Request:
{
    "name": "新产品文档知识库",         // optional
    "description": "更新后的描述",      // optional
    "llm_model": "gpt-4o-mini",         // optional
    "is_public": true                   // optional
}

Response 200:
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "kb_xxx",
        "name": "新产品文档知识库",
        ...
    }
}
```

#### 5.1.5 删除知识库

```http
DELETE /api/knowledge/{knowledge_base_id}?force=false
Authorization: Bearer <jwt_token>

Query Params:
- force: boolean, default false, true时强制删除（包括所有文档）

Response 200:
{
    "code": 200,
    "message": "知识库已删除"
}

Response 400:
{
    "code": 400,
    "message": "知识库包含文档，请使用 force=true 强制删除"
}
```

### 5.2 文档管理接口

#### 5.2.1 上传文档

```http
POST /api/knowledge/{knowledge_base_id}/documents
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

Request:
- file: File, required, 支持 PDF/DOCX/PPTX/TXT/MD/PNG/JPG/MP4/MP3
- tags: string, optional, JSON数组字符串 ["标签1", "标签2"]

Response 200:
{
    "code": 200,
    "message": "文档上传成功，正在处理中",
    "data": {
        "document_id": "doc_xxx",
        "file_name": "产品手册.pdf",
        "file_size": 1024000,
        "file_type": "PDF",
        "embed_status": "PENDING",
        "create_time": "2024-01-01T12:00:00Z"
    }
}
```

#### 5.2.2 通过 URL 添加文档

```http
POST /api/knowledge/{knowledge_base_id}/documents/url
Authorization: Bearer <jwt_token>

Request:
{
    "url": "https://example.com/article",   // required
    "title": "自定义标题",                   // optional, 自动提取
    "auto_summary": true,                   // optional, default: true
    "tags": ["网页", "技术"]                 // optional
}

Response 200:
{
    "code": 200,
    "message": "网页内容已获取，正在处理中",
    "data": {
        "document_id": "doc_xxx",
        "source_url": "https://example.com/article",
        "title": "网页标题",
        "file_type": "HTML",
        "embed_status": "PENDING"
    }
}
```

#### 5.2.3 从现有文章导入

```http
POST /api/knowledge/{knowledge_base_id}/documents/article
Authorization: Bearer <jwt_token>

Request:
{
    "article_ids": ["art_1", "art_2", "art_3"],  // required, 文章ID列表
    "sync_future": true                           // optional, 是否同步未来更新
}

Response 200:
{
    "code": 200,
    "message": "成功导入 3 篇文章",
    "data": {
        "imported_count": 3,
        "failed_count": 0,
        "documents": [
            {
                "document_id": "doc_xxx",
                "source_id": "art_1",
                "title": "文章标题",
                "embed_status": "PENDING"
            }
        ]
    }
}
```

#### 5.2.4 获取文档列表

```http
GET /api/knowledge/{knowledge_base_id}/documents?page=1&size=20&status=COMPLETED&type=PDF
Authorization: Bearer <jwt_token>

Query Params:
- page: int, default 1
- size: int, default 20, max 100
- status: string, optional, PENDING/PROCESSING/COMPLETED/FAILED
- type: string, optional, PDF/DOCX/PPTX/...
- keyword: string, optional, 搜索文件名/标题

Response 200:
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 25,
        "page": 1,
        "size": 20,
        "list": [
            {
                "id": "doc_xxx",
                "source_type": "FILE",
                "file_type": "PDF",
                "file_name": "产品手册.pdf",
                "title": "产品手册",
                "file_size": 1024000,
                "chunk_count": 50,
                "embed_status": "COMPLETED",
                "process_error": null,
                "tags": ["产品", "手册"],
                "create_time": "2024-01-01T12:00:00Z"
            }
        ]
    }
}
```

#### 5.2.5 获取文档详情

```http
GET /api/knowledge/{knowledge_base_id}/documents/{document_id}
Authorization: Bearer <jwt_token>

Response 200:
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "doc_xxx",
        "knowledge_base_id": "kb_xxx",
        "source_type": "FILE",
        "source_url": null,
        "file_type": "PDF",
        "file_name": "产品手册.pdf",
        "title": "产品手册",
        "content_preview": "这是文档的前500字符预览...",
        "file_size": 1024000,
        "file_hash": "md5_hash",
        "chunk_count": 50,
        "embed_status": "COMPLETED",
        "process_error": null,
        "meta_data": {
            "pages": 100,
            "author": "张三"
        },
        "tags": ["产品", "手册"],
        "create_time": "2024-01-01T12:00:00Z",
        "update_time": "2024-01-01T12:05:00Z",
        "process_time": "2024-01-01T12:05:00Z"
    }
}
```

#### 5.2.6 删除文档

```http
DELETE /api/knowledge/{knowledge_base_id}/documents/{document_id}
Authorization: Bearer <jwt_token>

Response 200:
{
    "code": 200,
    "message": "文档已删除"
}
```

#### 5.2.7 重新处理文档

```http
POST /api/knowledge/{knowledge_base_id}/documents/{document_id}/reprocess
Authorization: Bearer <jwt_token>

Response 200:
{
    "code": 200,
    "message": "文档已加入重新处理队列",
    "data": {
        "document_id": "doc_xxx",
        "embed_status": "PENDING"
    }
}
```

### 5.3 智能问答接口

#### 5.3.1 知识库问答 (流式)

```http
POST /api/knowledge/{knowledge_base_id}/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
    "question": "产品的核心功能有哪些？",    // required, 问题内容
    "session_id": "sess_xxx",               // optional, 会话ID，不传则创建新会话
    "history_count": 5,                     // optional, default: 5, 携带历史消息数
    "temperature": 0.7,                     // optional, default: 0.7
    "stream": true,                         // optional, default: true
    "search_top_k": 5                       // optional, default: 5, 检索结果数
}

Response (stream=true, SSE格式):
event: message
data: {"type": "start", "session_id": "sess_xxx"}

event: message
data: {"type": "searching", "message": "正在检索相关知识..."}

event: message
data: {"type": "sources", "sources": [{"doc_id": "...", "title": "...", "similarity": 0.95}]}

event: message
data: {"type": "content", "delta": "根据", "content": "根据"}

event: message
data: {"type": "content", "delta": "产品", "content": "根据产品"}

...

event: message
data: {
    "type": "finish",
    "content": "根据产品文档，核心功能包括...",
    "usage": {"prompt_tokens": 1500, "completion_tokens": 500, "total_tokens": 2000},
    "sources": [...]
}

Response (stream=false):
{
    "code": 200,
    "message": "success",
    "data": {
        "session_id": "sess_xxx",
        "answer": "根据产品文档，核心功能包括...",
        "sources": [
            {
                "document_id": "doc_xxx",
                "document_name": "产品手册.pdf",
                "chunk_id": "chunk_xxx",
                "content_preview": "相关段落预览...",
                "similarity": 0.95,
                "page_number": 5
            }
        ],
        "usage": {
            "prompt_tokens": 1500,
            "completion_tokens": 500,
            "total_tokens": 2000
        }
    }
}
```

#### 5.3.2 获取对话历史

```http
GET /api/knowledge/{knowledge_base_id}/chat/history?session_id=sess_xxx&page=1&size=20
Authorization: Bearer <jwt_token>

Response 200:
{
    "code": 200,
    "message": "success",
    "data": {
        "session": {
            "id": "sess_xxx",
            "title": "产品功能咨询",
            "message_count": 10,
            "create_time": "2024-01-01T12:00:00Z"
        },
        "messages": [
            {
                "id": "msg_1",
                "role": "user",
                "content": "产品的核心功能有哪些？",
                "create_time": "2024-01-01T12:00:00Z"
            },
            {
                "id": "msg_2",
                "role": "assistant",
                "content": "根据产品文档，核心功能包括...",
                "sources": [...],
                "total_tokens": 2000,
                "create_time": "2024-01-01T12:00:05Z"
            }
        ]
    }
}
```

#### 5.3.3 获取会话列表

```http
GET /api/chat/sessions?page=1&size=20&knowledge_base_id=kb_xxx
Authorization: Bearer <jwt_token>

Response 200:
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 15,
        "list": [
            {
                "id": "sess_xxx",
                "title": "产品功能咨询",
                "knowledge_base_id": "kb_xxx",
                "knowledge_base_name": "产品文档知识库",
                "message_count": 10,
                "is_pinned": true,
                "create_time": "2024-01-01T12:00:00Z",
                "update_time": "2024-01-01T12:30:00Z"
            }
        ]
    }
}
```

#### 5.3.4 删除会话

```http
DELETE /api/chat/sessions/{session_id}
Authorization: Bearer <jwt_token>

Response 200:
{
    "code": 200,
    "message": "会话已删除"
}
```

### 5.4 网页处理接口

#### 5.4.1 网页内容总结

```http
POST /api/chat/web-summary
Authorization: Bearer <jwt_token>

Request:
{
    "url": "https://example.com/article",   // required
    "summary_length": "medium",             // optional, short/medium/long
    "save_to_knowledge_base": null,         // optional, 保存到指定知识库ID
    "tags": ["网页", "技术"]                 // optional
}

Response 200:
{
    "code": 200,
    "message": "success",
    "data": {
        "url": "https://example.com/article",
        "title": "文章标题",
        "summary": "## 核心观点\n...\n\n## 关键要点\n1. ...",
        "document_id": "doc_xxx",  // 如果保存到知识库
        "fetch_time_ms": 2500,
        "word_count": 1500
    }
}
```

#### 5.4.2 联网搜索问答

```http
POST /api/chat/search
Authorization: Bearer <jwt_token>

Request:
{
    "question": "最新的AI技术趋势是什么？",   // required
    "session_id": "sess_xxx",               // optional
    "search_engine": "tavily",              // optional, default: tavily
    "time_range": "w",                      // optional, d/w/m/y (天/周/月/年)
    "result_count": 5,                      // optional, default: 5
    "stream": true                          // optional, default: true
}

Response (与知识库问答格式相同):
{
    "code": 200,
    "message": "success",
    "data": {
        "session_id": "sess_xxx",
        "answer": "根据搜索结果，最新的AI技术趋势包括...",
        "sources": [
            {
                "title": "2024年AI技术趋势报告",
                "url": "https://...",
                "snippet": "...",
                "source": "tavily"
            }
        ],
        "search_query": "最新AI技术趋势 2024",
        "search_time": "2024-01-01T12:00:00Z"
    }
}
```

### 5.5 接口汇总表

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| **知识库** | POST | /api/knowledge | 创建知识库 |
| | GET | /api/knowledge | 获取知识库列表 |
| | GET | /api/knowledge/{id} | 获取知识库详情 |
| | PUT | /api/knowledge/{id} | 更新知识库 |
| | DELETE | /api/knowledge/{id} | 删除知识库 |
| **文档** | POST | /api/knowledge/{id}/documents | 上传文档 |
| | POST | /api/knowledge/{id}/documents/url | URL添加文档 |
| | POST | /api/knowledge/{id}/documents/article | 导入文章 |
| | GET | /api/knowledge/{id}/documents | 获取文档列表 |
| | GET | /api/knowledge/{id}/documents/{doc_id} | 获取文档详情 |
| | DELETE | /api/knowledge/{id}/documents/{doc_id} | 删除文档 |
| | POST | /api/knowledge/{id}/documents/{doc_id}/reprocess | 重新处理 |
| **问答** | POST | /api/knowledge/{id}/chat | 知识库问答 |
| | GET | /api/knowledge/{id}/chat/history | 获取对话历史 |
| | GET | /api/chat/sessions | 获取会话列表 |
| | DELETE | /api/chat/sessions/{id} | 删除会话 |
| **网页** | POST | /api/chat/web-summary | 网页总结 |
| | POST | /api/chat/search | 联网搜索问答 |

## 六、新增依赖包

### 6.1 核心依赖

```txt
# ==================== LangChain 生态 ====================
langchain==0.3.15
langchain-community==0.3.15
langchain-openai==0.3.0
langchain-chroma==0.1.4

# ==================== LLM API 客户端 ====================
openai==1.59.0
zhipuai==2.1.5           # 智谱AI SDK
deepseek-sdk==0.1.0      # DeepSeek SDK (如有)

# ==================== Embedding 模型 ====================
sentence-transformers==3.3.1  # 本地 embedding 模型
# 如需使用 BGE 模型，首次运行时会自动下载

# ==================== 向量数据库 ====================
chromadb==0.5.23         # 开发环境
pymilvus==2.4.9          # 生产环境 Milvus

# ==================== 文档处理 ====================
# PDF 解析
PyMuPDF==1.25.1          # fitz，推荐
pdfplumber==0.11.4       # 备选，表格识别更好

# Office 文档
python-docx==1.1.2       # Word
python-pptx==1.0.2       # PPT
openpyxl==3.1.5          # Excel

# 图片 OCR
paddleocr==2.9.1         # PaddleOCR，中文效果好
paddlepaddle==2.6.2      # Paddle 基础库
# 备选: pytesseract==0.3.13

# 视频/音频处理
openai-whisper==20240930 # 语音识别
ffmpeg-python==0.2.0     # ffmpeg 封装

# HTML/Markdown
beautifulsoup4==4.12.3
markdown==3.7
mistune==3.0.2
trafilatura==1.12.2      # 网页正文提取
newspaper3k==0.2.8       # 新闻提取

# ==================== 网页抓取 ====================
playwright==1.49.1       # 动态页面抓取
requests==2.32.4         # 静态页面
selenium==4.27.1         # 备选

# ==================== 搜索引擎 ====================
tavily-python==0.5.0     # Tavily 搜索 API
duckduckgo-search==7.2.1 # DuckDuckGo 搜索

# ==================== 异步任务队列 ====================
celery==5.4.0
redis==5.2.1             # 升级现有版本

# ==================== 其他工具 ====================
tiktoken==0.8.0          # Token 计算
python-magic==0.4.27     # 文件类型检测
chardet==5.2.0           # 编码检测
langdetect==1.0.9        # 语言检测
numpy==1.26.4            # 数值计算
scikit-learn==1.6.0      # 机器学习工具
```

### 6.2 依赖安装建议

```bash
# 1. 创建 requirements-ai.txt 单独管理 AI 相关依赖

# 2. 分阶段安装

# 阶段一：基础依赖
pip install langchain langchain-community langchain-openai openai

# 阶段二：向量数据库
pip install chromadb sentence-transformers

# 阶段三：文档处理
pip install PyMuPDF python-docx python-pptx openpyxl

# 阶段四：OCR（模型较大，单独安装）
pip install paddlepaddle paddleocr

# 阶段五：视频处理
pip install openai-whisper ffmpeg-python

# 阶段六：网页抓取
pip install playwright trafilatura beautifulsoup4
playwright install  # 安装浏览器

# 阶段七：搜索引擎
pip install tavily-python

# 阶段八：异步任务
pip install celery
```

### 6.3 系统依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    ffmpeg \
    libmagic1 \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    poppler-utils

# macOS
brew install ffmpeg libmagic tesseract poppler

# CentOS/RHEL
sudo yum install -y ffmpeg file-libs tesseract tesseract-langpack-chi-sim poppler-utils
```

## 七、配置扩展

### 7.1 配置文件结构

在 `app/config.py` 中添加 AI 相关配置类：

```python
import os

class AIConfig:
    """AI 相关配置"""
    
    # ==================== LLM 配置 ====================
    # 提供商: openai / zhipu / deepseek / local
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'zhipu')
    
    # OpenAI 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # 智谱AI配置
    ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '')
    ZHIPU_MODEL = os.getenv('ZHIPU_MODEL', 'glm-4-flash')
    
    # DeepSeek 配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    # 本地模型配置 (Ollama / vLLM)
    LOCAL_LLM_BASE_URL = os.getenv('LOCAL_LLM_BASE_URL', 'http://localhost:11434')
    LOCAL_LLM_MODEL = os.getenv('LOCAL_LLM_MODEL', 'qwen2.5:14b')
    
    # 默认模型参数
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '4096'))
    LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '60'))
    
    # ==================== Embedding 配置 ====================
    # 提供商: openai / local / huggingface
    EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'local')
    
    # OpenAI Embedding
    OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    
    # 本地 Embedding 模型
    LOCAL_EMBEDDING_MODEL = os.getenv('LOCAL_EMBEDDING_MODEL', 'BAAI/bge-large-zh-v1.5')
    # 备选轻量模型: BAAI/bge-small-zh-v1.5, moka-ai/m3e-base
    
    # Embedding 参数
    EMBEDDING_DEVICE = os.getenv('EMBEDDING_DEVICE', 'cpu')  # cpu / cuda / mps
    EMBEDDING_BATCH_SIZE = int(os.getenv('EMBEDDING_BATCH_SIZE', '32'))
    
    # ==================== 向量数据库配置 ====================
    # 类型: chroma / milvus
    VECTOR_DB_TYPE = os.getenv('VECTOR_DB_TYPE', 'chroma')
    
    # Chroma 配置
    CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './data/chroma')
    CHROMA_ANONYMIZED_TELEMETRY = False
    
    # Milvus 配置
    MILVUS_HOST = os.getenv('MILVUS_HOST', 'localhost')
    MILVUS_PORT = int(os.getenv('MILVUS_PORT', '19530'))
    MILVUS_USER = os.getenv('MILVUS_USER', '')
    MILVUS_PASSWORD = os.getenv('MILVUS_PASSWORD', '')
    MILVUS_COLLECTION_PREFIX = os.getenv('MILVUS_COLLECTION_PREFIX', 'kb_')
    
    # 向量检索参数
    VECTOR_SEARCH_TOP_K = int(os.getenv('VECTOR_SEARCH_TOP_K', '10'))
    VECTOR_SEARCH_SCORE_THRESHOLD = float(os.getenv('VECTOR_SEARCH_SCORE_THRESHOLD', '0.5'))
    
    # ==================== 文档处理配置 ====================
    # 上传配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './data/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', str(100 * 1024 * 1024)))  # 100MB
    ALLOWED_EXTENSIONS = {
        'pdf', 'docx', 'pptx', 'xlsx', 'txt', 'md', 'html',
        'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp',
        'mp4', 'avi', 'mov', 'wmv', 'mp3', 'wav', 'm4a'
    }
    
    # 文本分块配置
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '500'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '50'))
    CHUNK_SEPARATORS = ['\n\n', '\n', '。', '．', '. ', ' ', '']
    
    # OCR 配置
    OCR_LANG = os.getenv('OCR_LANG', 'ch_sim+en')  # PaddleOCR 语言包
    OCR_GPU = os.getenv('OCR_GPU', 'false').lower() == 'true'
    
    # 视频处理配置
    VIDEO_FRAME_INTERVAL = int(os.getenv('VIDEO_FRAME_INTERVAL', '10'))  # 每10秒提取一帧
    VIDEO_MAX_DURATION = int(os.getenv('VIDEO_MAX_DURATION', '3600'))  # 最大处理1小时
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')  # tiny/base/small/medium/large
    
    # ==================== 网页抓取配置 ====================
    # 请求配置
    WEB_REQUEST_TIMEOUT = int(os.getenv('WEB_REQUEST_TIMEOUT', '30'))
    WEB_REQUEST_RETRY = int(os.getenv('WEB_REQUEST_RETRY', '3'))
    WEB_REQUEST_USER_AGENT = os.getenv('WEB_REQUEST_USER_AGENT', 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Playwright 配置
    PLAYWRIGHT_HEADLESS = os.getenv('PLAYWRIGHT_HEADLESS', 'true').lower() == 'true'
    PLAYWRIGHT_BROWSER = os.getenv('PLAYWRIGHT_BROWSER', 'chromium')  # chromium/firefox/webkit
    
    # 内容提取配置
    WEB_CONTENT_MAX_LENGTH = int(os.getenv('WEB_CONTENT_MAX_LENGTH', '50000'))  # 最大5万字符
    WEB_CONTENT_MIN_LENGTH = int(os.getenv('WEB_CONTENT_MIN_LENGTH', '100'))   # 最少100字符
    
    # ==================== 搜索引擎配置 ====================
    # 默认搜索引擎: tavily / duckduckgo / serpapi
    SEARCH_ENGINE = os.getenv('SEARCH_ENGINE', 'duckduckgo')
    
    # Tavily 配置
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
    TAVILY_SEARCH_DEPTH = os.getenv('TAVILY_SEARCH_DEPTH', 'basic')  # basic/advanced
    
    # SerpAPI 配置
    SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY', '')
    
    # 搜索参数
    SEARCH_MAX_RESULTS = int(os.getenv('SEARCH_MAX_RESULTS', '10'))
    SEARCH_TIMEOUT = int(os.getenv('SEARCH_TIMEOUT', '10'))
    
    # ==================== 异步任务配置 ====================
    # Celery 配置
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_TASK_ALWAYS_EAGER', 'false').lower() == 'true'
    
    # 任务队列配置
    CELERY_TASK_QUEUE_DOCUMENT = 'document_processing'
    CELERY_TASK_QUEUE_EMBEDDING = 'embedding_generation'
    CELERY_TASK_QUEUE_CRAWLER = 'web_crawling'
    
    # ==================== 缓存配置 ====================
    # Embedding 缓存
    EMBEDDING_CACHE_ENABLED = os.getenv('EMEDDING_CACHE_ENABLED', 'true').lower() == 'true'
    EMBEDDING_CACHE_TTL = int(os.getenv('EMBEDDING_CACHE_TTL', '86400'))  # 24小时
    
    # 查询缓存
    QUERY_CACHE_ENABLED = os.getenv('QUERY_CACHE_ENABLED', 'true').lower() == 'true'
    QUERY_CACHE_TTL = int(os.getenv('QUERY_CACHE_TTL', '300'))  # 5分钟
    
    # ==================== 安全与限流配置 ====================
    # 文件上传限制
    UPLOAD_RATE_LIMIT = os.getenv('UPLOAD_RATE_LIMIT', '10/minute')  # 每分钟10个文件
    
    # 问答限流
    CHAT_RATE_LIMIT = os.getenv('CHAT_RATE_LIMIT', '30/minute')  # 每分钟30次问答
    
    # 搜索限流
    SEARCH_RATE_LIMIT = os.getenv('SEARCH_RATE_LIMIT', '20/minute')  # 每分钟20次搜索
    
    # 内容安全
    CONTENT_FILTER_ENABLED = os.getenv('CONTENT_FILTER_ENABLED', 'true').lower() == 'true'
    MAX_INPUT_LENGTH = int(os.getenv('MAX_INPUT_LENGTH', '4000'))  # 最大输入长度


# 在 config 字典中添加 AI 配置
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'ai': AIConfig  # 添加 AI 配置
}
```

### 7.2 环境变量示例 (.env.ai)

```bash
# 复制到 .env.ai 并根据实际情况修改

# ==================== LLM 配置 ====================
LLM_PROVIDER=zhipu
ZHIPU_API_KEY=your_zhipu_api_key_here
ZHIPU_MODEL=glm-4-flash

# 备选 OpenAI 配置
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-xxx
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL=gpt-4o-mini

LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# ==================== Embedding 配置 ====================
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
EMBEDDING_DEVICE=cpu

# ==================== 向量数据库配置 ====================
VECTOR_DB_TYPE=chroma
CHROMA_PERSIST_DIR=./data/chroma

# 生产环境 Milvus 配置
# VECTOR_DB_TYPE=milvus
# MILVUS_HOST=localhost
# MILVUS_PORT=19530

# ==================== 文档处理配置 ====================
UPLOAD_FOLDER=./data/uploads
MAX_CONTENT_LENGTH=104857600  # 100MB
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# OCR 配置
OCR_GPU=false

# 视频处理配置
WHISPER_MODEL=base
VIDEO_MAX_DURATION=3600

# ==================== 网页抓取配置 ====================
WEB_REQUEST_TIMEOUT=30
PLAYWRIGHT_HEADLESS=true

# ==================== 搜索引擎配置 ====================
SEARCH_ENGINE=duckduckgo

# Tavily 配置（如需使用）
# TAVILY_API_KEY=tvly-xxx

# ==================== 异步任务配置 ====================
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# ==================== 安全与限流配置 ====================
CHAT_RATE_LIMIT=30/minute
SEARCH_RATE_LIMIT=20/minute
CONTENT_FILTER_ENABLED=true
```

### 7.3 配置加载方式

```python
# app/extension.py 扩展

from app.config import AIConfig

class ConfigMixin:
    """配置混入类，提供便捷的 AI 配置访问"""
    
    @property
    def ai_config(self):
        return AIConfig

# 在 Flask app 中注册
# app/config.py 中的 Config 类继承 ConfigMixin
class DevelopmentConfig(Config, ConfigMixin):
    DEBUG = True
    # ...
```

## 八、实施路线图

### 8.1 总体时间规划

```
月份:    M1                              M2                              M3
周:      W1      W2      W3      W4      W1      W2      W3      W4      W1      W2
        ├───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┤
阶段一:  ████████████████
阶段二:          ████████████████████████████████
阶段三:                                          ████████████████
阶段四:                                                          ████████████████
阶段五:                                                                  ████████████████
```

**总工期**: 约 8-10 周（2-2.5 个月）

### 8.2 详细实施计划

#### 阶段一：基础设施搭建 (第 1-2 周)

**目标**: 搭建知识库基础架构，实现知识库管理功能

**Week 1 任务**:
- [ ] **数据库设计** (2天)
  - 创建 `knowledge_base` 表
  - 创建 `document` 表
  - 创建 `document_chunk` 表
  - 创建 `chat_session` 表
  - 创建 `chat_message` 表
  - 编写 Alembic 迁移脚本
  
- [ ] **项目结构搭建** (2天)
  - 创建 `app/services/` 目录结构
  - 创建 `app/controllers/knowledge/` 目录
  - 创建 `app/controllers/crawler/` 目录
  - 初始化 `__init__.py` 文件
  
- [ ] **配置扩展** (1天)
  - 扩展 `app/config.py` 添加 AIConfig
  - 创建 `.env.ai` 模板文件
  - 更新 `requirements.txt`

**Week 2 任务**:
- [ ] **向量数据库集成** (3天)
  - 集成 ChromaDB
  - 实现 `VectorStoreService` 基础类
  - 实现 Collection 管理（创建/删除/查询）
  - 实现基础的增删改查接口
  
- [ ] **Embedding 服务** (2天)
  - 实现 `EmbeddingService` 类
  - 支持本地模型 (BGE)
  - 支持 OpenAI Embedding API
  - 实现 Embedding 缓存机制

**阶段一交付物**:
- 可创建/管理知识库的 API
- 可连接向量数据库并执行基本操作
- 可将文本转换为向量

---

#### 阶段二：文档处理系统 (第 2-5 周)

**目标**: 实现多格式文档的上传、解析、分块、向量化完整流程

**Week 3 任务 - 基础文档处理**:
- [ ] **文档解析器框架** (2天)
  - 设计 `DocumentParser` 抽象基类
  - 实现 `ParserFactory` 工厂类
  - 实现文件类型检测
  
- [ ] **PDF 解析器** (2天)
  - 集成 PyMuPDF
  - 实现文本提取
  - 实现图片提取
  - 实现表格识别
  - 支持页码追踪
  
- [ ] **Office 文档解析器** (1天)
  - 实现 Word 解析 (python-docx)
  - 实现 PPT 解析 (python-pptx)
  - 实现 Excel 解析 (openpyxl)

**Week 4 任务 - 多媒体处理**:
- [ ] **图片 OCR 处理** (3天)
  - 集成 PaddleOCR
  - 实现图片预处理（旋转、裁剪）
  - 实现文本区域检测
  - 实现多语言 OCR
  
- [ ] **视频/音频处理** (2天)
  - 集成 Whisper
  - 实现音频提取 (ffmpeg)
  - 实现语音转文字
  - 实现关键帧提取

**Week 5 任务 - 文本处理与向量化**:
- [ ] **文本分块** (2天)
  - 集成 LangChain TextSplitter
  - 实现 RecursiveCharacterTextSplitter
  - 支持自定义分块策略
  - 实现元数据保留（页码、位置）
  
- [ ] **文档处理 Pipeline** (3天)
  - 实现完整的文档处理流程
  - 实现状态管理 (PENDING/PROCESSING/COMPLETED/FAILED)
  - 实现错误处理和重试机制
  - 实现进度追踪

**阶段二交付物**:
- 支持 PDF/Word/PPT/图片/视频的上传和处理
- 文档自动分块并向量化
- 可查看处理状态和进度

---

#### 阶段三：智能问答系统 (第 5-7 周)

**目标**: 实现基于 RAG 的智能问答功能

**Week 6 任务 - RAG 核心**:
- [ ] **检索服务** (3天)
  - 实现向量检索
  - 实现混合检索（向量+关键词）
  - 实现重排序 (Cross-Encoder)
  - 实现相似度阈值过滤
  
- [ ] **Prompt 工程** (2天)
  - 设计 System Prompt
  - 设计 RAG Prompt 模板
  - 实现上下文构建
  - 实现引用标注

**Week 7 任务 - 问答接口**:
- [ ] **问答 API** (3天)
  - 实现 `/chat` 接口
  - 支持流式输出 (SSE)
  - 支持对话历史
  - 实现来源追踪
  
- [ ] **会话管理** (2天)
  - 实现会话创建/获取/删除
  - 实现消息历史存储
  - 实现会话标题自动生成
  - 实现会话置顶功能

**阶段三交付物**:
- 可向知识库提问并获得回答
- 支持多轮对话
- 可查看回答来源

---

#### 阶段四：网络功能 (第 7-9 周)

**目标**: 实现网页抓取、内容总结、联网搜索功能

**Week 8 任务 - 网页抓取**:
- [ ] **网页抓取服务** (3天)
  - 集成 Playwright
  - 实现动态页面渲染
  - 实现内容提取 (trafilatura)
  - 实现反爬策略
  
- [ ] **内容总结** (2天)
  - 实现单页总结
  - 实现长文本分块总结
  - 实现结构化输出

**Week 9 任务 - 搜索集成**:
- [ ] **搜索引擎集成** (2天)
  - 集成 DuckDuckGo (免费)
  - 集成 Tavily (高质量)
  - 实现搜索结果格式化
  
- [ ] **联网问答** (3天)
  - 实现搜索+问答 Pipeline
  - 实现搜索结果缓存
  - 实现时效性提示

**阶段四交付物**:
- 可通过 URL 添加网页到知识库
- 可自动总结网页内容
- 可进行联网搜索问答

---

#### 阶段五：优化与生产 (第 9-10 周)

**目标**: 性能优化、生产环境准备、监控运维

**Week 10 任务**:
- [ ] **异步任务队列** (2天)
  - 集成 Celery
  - 实现文档处理异步化
  - 实现任务监控
  - 实现失败重试
  
- [ ] **性能优化** (2天)
  - 实现 Embedding 缓存
  - 实现查询缓存
  - 实现连接池优化
  - 实现批量处理
  
- [ ] **生产环境准备** (2天)
  - 向量数据库迁移到 Milvus
  - 文件存储迁移到 OSS
  - 配置生产环境参数
  - 编写部署文档
  
- [ ] **监控与日志** (2天)
  - 集成 Prometheus 监控
  - 实现关键指标采集
  - 配置日志收集
  - 实现告警机制

**阶段五交付物**:
- 生产环境可用的系统
- 完整的监控和告警
- 部署和运维文档

### 8.3 里程碑检查点

| 里程碑 | 时间 | 验收标准 |
|--------|------|---------|
| M1 | Week 2 结束 | 可创建知识库，文本可向量化存储 |
| M2 | Week 5 结束 | 可上传 PDF/Word/图片并自动处理 |
| M3 | Week 7 结束 | 可向知识库提问，获得带来源的回答 |
| M4 | Week 9 结束 | 可抓取网页、联网搜索问答 |
| M5 | Week 10 结束 | 系统生产就绪，性能满足要求 |

### 8.4 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|---------|
| PaddleOCR 模型过大 | 中 | 部署困难 | 提供 Docker 镜像，或使用云端 OCR API |
| 向量数据库性能瓶颈 | 中 | 查询慢 | 提前设计索引，准备 Milvus 迁移方案 |
| LLM API 不稳定 | 高 | 问答失败 | 实现多提供商 fallback 机制 |
| 大文档处理超时 | 中 | 用户体验差 | 异步处理 + 进度通知 |
| 网页抓取被封 | 中 | 功能不可用 | 实现代理池，限制抓取频率 |

## 九、关键技术点详解

### 9.1 文本分块策略

#### 9.1.1 分块策略选择

| 策略 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **固定字符数** | 通用场景 | 简单、均匀 | 可能切断语义 |
| **递归字符** | 结构化文本 | 保持段落完整 | 块大小不均匀 |
| **语义分块** | 高质量要求 | 语义完整 | 计算成本高 |
| **Markdown分块** | Markdown文档 | 保留标题结构 | 仅适用于MD |

#### 9.1.2 推荐配置

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,           # 每块约 500 字符
    chunk_overlap=50,         # 重叠 50 字符，保持上下文
    length_function=len,      # 使用字符数计算长度
    separators=[              # 分隔符优先级
        "\n\n",               # 1. 段落
        "\n",                 # 2. 换行
        "。", "．", ". ",     # 3. 句号
        "；", ";",            # 4. 分号
        "，", ",",            # 5. 逗号
        " ",                  # 6. 空格
        ""                    # 7. 字符
    ]
)
```

#### 9.1.3 元数据保留

每个 chunk 需要保留以下元数据，用于溯源：

```python
{
    "document_id": "doc_xxx",      # 所属文档ID
    "chunk_index": 0,               # 块序号
    "page_number": 5,               # 页码（PDF等）
    "start_char": 0,                # 起始字符位置
    "end_char": 500,                # 结束字符位置
    "source_type": "PDF",           # 来源类型
    "file_name": "产品手册.pdf"      # 文件名
}
```

### 9.2 Embedding 缓存策略

#### 9.2.1 缓存设计

```python
import hashlib
import json
from app.extension import redis_client

class EmbeddingCache:
    """Embedding 缓存服务"""
    
    CACHE_PREFIX = "emb:"
    CACHE_TTL = 86400  # 24小时
    
    @staticmethod
    def _get_cache_key(text: str, model: str) -> str:
        """生成缓存 key"""
        content = f"{model}:{text}"
        hash_key = hashlib.md5(content.encode()).hexdigest()
        return f"{EmbeddingCache.CACHE_PREFIX}{hash_key}"
    
    @classmethod
    def get(cls, text: str, model: str) -> list | None:
        """获取缓存的 embedding"""
        key = cls._get_cache_key(text, model)
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    @classmethod
    def set(cls, text: str, model: str, embedding: list):
        """设置缓存"""
        key = cls._get_cache_key(text, model)
        redis_client.setex(
            key, 
            cls.CACHE_TTL, 
            json.dumps(embedding)
        )
```

#### 9.2.2 缓存命中率优化

- **文本预处理**: 去除多余空格、统一换行符
- **相似文本合并**: 使用 SimHash 检测相似文本
- **批量缓存**: 批量查询 Redis，减少网络开销

### 9.3 混合检索策略

#### 9.3.1 检索流程

```
用户查询
    │
    ├─> 向量检索 ──> Top-K 向量结果 (相似度: 0.9, 0.85, 0.82...)
    │
    ├─> 关键词检索 ──> Top-K 关键词结果 (BM25分数: 25, 22, 18...)
    │
    ▼
  结果融合 (RRF: Reciprocal Rank Fusion)
    │
    ▼
  重排序 (可选)
    │
    ▼
  最终 Top-K 结果
```

#### 9.3.2 RRF 融合算法

```python
def reciprocal_rank_fusion(vector_results, keyword_results, k=60):
    """
    RRF 融合算法
    score = Σ(1 / (k + rank))
    """
    scores = {}
    
    # 向量检索结果打分
    for rank, doc in enumerate(vector_results):
        doc_id = doc['id']
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    
    # 关键词检索结果打分
    for rank, doc in enumerate(keyword_results):
        doc_id = doc['id']
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    
    # 按分数排序
    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results
```

### 9.4 流式响应实现

#### 9.4.1 SSE 服务端实现

```python
from flask import Response, stream_with_context
import json

def chat_stream(knowledge_base_id: str, question: str, session_id: str):
    """流式问答接口"""
    
    def generate():
        # 1. 发送开始事件
        yield f"event: message\ndata: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"
        
        # 2. 执行检索
        yield f"event: message\ndata: {json.dumps({'type': 'searching'})}\n\n"
        sources = retrieve_documents(knowledge_base_id, question)
        yield f"event: message\ndata: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
        
        # 3. 流式调用 LLM
        full_content = ""
        for chunk in llm.stream_chat(question, sources):
            content_delta = chunk['content']
            full_content += content_delta
            yield f"event: message\ndata: {json.dumps({'type': 'content', 'delta': content_delta, 'content': full_content})}\n\n"
        
        # 4. 发送结束事件
        yield f"event: message\ndata: {json.dumps({'type': 'finish', 'content': full_content})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )
```

#### 9.4.2 客户端接收示例

```javascript
const eventSource = new EventSource('/api/knowledge/xxx/chat');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'start':
            console.log('开始回答');
            break;
        case 'sources':
            displaySources(data.sources);
            break;
        case 'content':
            appendContent(data.delta);
            break;
        case 'finish':
            eventSource.close();
            break;
    }
};
```

### 9.5 异步任务处理

#### 9.5.1 Celery 任务定义

```python
# tasks/document_tasks.py
from celery import Celery
from app.extension import celery_app

@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    """处理文档异步任务"""
    try:
        document = Document.query.get(document_id)
        if not document:
            return {'status': 'failed', 'error': 'Document not found'}
        
        # 更新状态为处理中
        document.embed_status = 'PROCESSING'
        db.session.commit()
        
        # 1. 下载/读取文件
        file_content = download_file(document.file_path)
        
        # 2. 解析文档
        parser = ParserFactory.get_parser(document.file_type)
        text_content = parser.parse(file_content)
        
        # 3. 文本分块
        chunks = text_splitter.split_text(text_content)
        
        # 4. 生成 Embedding
        embeddings = embedding_service.embed_documents(chunks)
        
        # 5. 存入向量数据库
        vector_store.add_documents(document_id, chunks, embeddings)
        
        # 6. 更新状态
        document.embed_status = 'COMPLETED'
        document.chunk_count = len(chunks)
        document.process_time = datetime.now()
        db.session.commit()
        
        return {'status': 'success', 'chunk_count': len(chunks)}
        
    except Exception as exc:
        # 更新失败状态
        document.embed_status = 'FAILED'
        document.process_error = str(exc)
        db.session.commit()
        
        # 重试
        raise self.retry(exc=exc, countdown=60)
```

#### 9.5.2 任务监控

```python
# 获取任务状态
from celery.result import AsyncResult

def get_task_status(task_id: str):
    result = AsyncResult(task_id)
    return {
        'task_id': task_id,
        'status': result.status,  # PENDING/SUCCESS/FAILURE/RETRY
        'result': result.result if result.ready() else None
    }
```

### 9.6 性能优化建议

| 优化点 | 策略 | 预期效果 |
|--------|------|---------|
| **Embedding 批处理** | 批量编码，batch_size=32 | 提升 3-5 倍 |
| **向量检索索引** | 使用 HNSW 索引 | 查询速度提升 10 倍 |
| **查询缓存** | 缓存相似查询结果 | 减少 50% LLM 调用 |
| **连接池** | 复用 LLM/DB 连接 | 减少延迟 100ms |
| **预加载模型** | 服务启动时加载模型 | 首次请求加速 |

### 9.7 安全注意事项

1. **文件上传安全**
   - 限制文件类型和大小
   - 扫描恶意文件
   - 使用随机文件名存储

2. **Prompt 注入防护**
   - 输入过滤和转义
   - 使用系统消息隔离
   - 限制输出长度

3. **API 密钥管理**
   - 使用环境变量
   - 定期轮换密钥
   - 监控异常调用

4. **数据隔离**
   - 知识库按用户隔离
   - 验证用户权限
   - 审计日志记录