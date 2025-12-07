分层逻辑说明
config/ 存放配置文件，方便不同环境切换（开发/生产）。

data/ 存放训练数据、缓存结果、向量数据库（如 FAISS、Pinecone）。

models/ 封装大语言模型（LLM）、Embedding 模型，统一接口。

memory/ 管理智能体的记忆（对话历史、长期知识库）。

tools/ 定义智能体可调用的外部工具（搜索、计算、API调用）。

agents/ 每个智能体的核心逻辑，包含角色定义、决策策略。

workflows/ 编排任务流，比如 Prompt Flow、LangChain Chain、AutoGen 对话流。

services/ 与外部系统交互的模块（数据库、消息队列、REST API）。

utils/ 通用工具函数（日志、配置加载、异常处理）。

tests/ 测试代码，保证模块稳定性。
