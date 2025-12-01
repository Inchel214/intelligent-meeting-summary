# 智能会议摘要智能体 - 快速开始指南

## 🚀 核心功能

这个Python智能体可以：
- 🎥 从视频/音频文件中提取字幕
- 🤖 使用AI生成结构化会议摘要
- 🎯 提取关键决策点和行动项
- 📊 支持上下文工程优化
- 🔌 适配多种AI服务提供商

## 📦 快速安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置API密钥
export OPENAI_API_KEY="your-openai-api-key"

# 3. 运行演示
python run_demo.py
```

## 🎯 三种使用方式

### 方式1：基础使用（推荐）
```bash
python run_demo.py
```
- 使用演示字幕数据
- 快速验证功能
- 无需准备音频文件

### 方式2：核心智能体
```python
from meeting_summary_agent import MeetingSummaryAgent

# 创建智能体
agent = MeetingSummaryAgent("your-api-key")

# 处理视频文件
result = agent.process_meeting("your_meeting.mp4")

# 查看结果
print(f"摘要: {result['summary']['title']}")
print(f"关键点: {len(result['summary']['key_points'])}个")
```

### 方式3：增强版（上下文优化）
```python
from enhanced_agent_demo import EnhancedMeetingAgent

# 创建增强版智能体
agent = EnhancedMeetingAgent()

# 会议信息
meeting_info = {
    "title": "Q1产品规划会议",
    "industry": "tech",
    "meeting_type": "strategic_planning"
}

# 处理字幕文本
result = agent.process_subtitle_directly(subtitle_text, meeting_info)
```

## 🎥 输入格式

### 视频文件支持
- MP4, AVI, MOV, MKV等常见格式
- 自动提取音频进行转录

### 字幕文本格式
```
[00:00:00] 张总: 各位同事好，今天我们讨论Q1产品规划
[00:00:30] 李经理: 我负责移动端开发，计划新增三个核心功能
[00:01:00] 王总监: 预算方面我们需要控制在500万以内
```

## 📊 输出格式

```json
{
  "meeting_id": "meeting_1234567890",
  "summary": {
    "title": "Q1产品规划会议摘要",
    "overview": "本次会议主要讨论了...",
    "key_points": [
      {
        "topic": "新功能规划",
        "content": "确定了三个核心功能的开发优先级",
        "participants": ["张三", "李四"],
        "timestamp": "14:15-14:30"
      }
    ],
    "decisions": [
      {
        "content": "确定采用React作为前端框架",
        "responsible": "张三",
        "deadline": "2024-12-15"
      }
    ],
    "action_items": [
      {
        "task": "完成竞品分析报告",
        "assignee": "李四",
        "deadline": "2024-12-08"
      }
    ]
  }
}
```

## 🔧 适配器配置

### 本地GPU服务器配置
```yaml
# ai_config.yaml
ai_services:
  local_model:
    enabled: true
    model_path: "/path/to/your/chatglm3"
    type: "chatglm3"
    device: "cuda"

adapter_config:
  primary_adapter: "local_model"
```

### 云服务配置
```yaml
ai_services:
  openai:
    enabled: true
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-3.5-turbo"
  
  baidu:
    enabled: true
    api_key: "${BAIDU_API_KEY}"
    secret_key: "${BAIDU_SECRET_KEY}"
```

## 🚀 快速测试

```bash
# 1. 基础测试
python run_demo.py

# 2. 增强版测试（推荐）
python enhanced_agent_demo.py

# 3. 处理真实视频
python -c "
from meeting_summary_agent import MeetingSummaryAgent
import os
os.environ['OPENAI_API_KEY'] = 'your-key'
agent = MeetingSummaryAgent()
result = agent.process_meeting('meeting.mp4')
print('✅ 完成！摘要:', result['summary']['title'])
"
```

## 📋 环境要求

- Python 3.8+
- OpenAI API密钥
- 可选：本地GPU（CUDA 11.8+）

## 🎉 下一步

1. **测试基础功能** → 运行 `python run_demo.py`
2. **准备真实数据** → 替换为自己的会议录音
3. **配置AI服务** → 修改 `ai_config.yaml`
4. **集成到工作流** → 调用API处理批量文件

## 💡 提示

- 🎯 先用演示数据验证功能
- 🔧 根据需求调整AI配置
- 📊 关注输出质量和处理时间
- 🔒 保护好API密钥

运行演示后，您将得到完整的会议摘要JSON文件，包含所有关键信息！🎊