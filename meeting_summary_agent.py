#!/usr/bin/env python3
"""
智能会议摘要智能体
核心功能：从视频/音频文件中提取字幕并生成结构化会议摘要
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import whisper
import openai
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MeetingSegment:
    """会议片段"""
    start_time: str
    end_time: str
    speaker: str
    content: str

@dataclass
class MeetingSummary:
    """会议摘要结果"""
    title: str
    overview: str
    key_points: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float

class MeetingSummaryAgent:
    """会议摘要智能体"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        初始化智能体
        
        Args:
            openai_api_key: OpenAI API密钥，如果不提供则使用环境变量
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("请提供OpenAI API密钥")
        
        openai.api_key = self.openai_api_key
        
        # 加载Whisper模型
        logger.info("正在加载Whisper模型...")
        self.whisper_model = whisper.load_model("base")
        logger.info("Whisper模型加载完成")
        
        # 上下文工程提示词
        self.summary_prompt = """
        你是一名专业的会议记录分析师，请根据以下会议转录内容生成结构化的会议摘要。
        
        要求：
        1. 提取会议的核心议题和关键讨论点
        2. 识别并列出重要决策
        3. 提取具体的行动项，包括责任人和截止时间
        4. 按照重要性排序
        5. 使用简洁专业的语言
        
        会议转录内容：
        {transcript}
        
        请以JSON格式输出，结构如下：
        {{
            "title": "会议标题",
            "overview": "会议概述",
            "key_points": [
                {{
                    "topic": "议题",
                    "content": "内容描述",
                    "participants": ["参与者1", "参与者2"],
                    "timestamp": "时间戳"
                }}
            ],
            "decisions": [
                {{
                    "content": "决策内容",
                    "responsible": "负责人",
                    "deadline": "截止时间"
                }}
            ],
            "action_items": [
                {{
                    "task": "任务描述",
                    "assignee": "负责人",
                    "deadline": "截止时间"
                }}
            ]
        }}
        """
    
    def extract_audio_from_video(self, video_path: str) -> str:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            音频文件路径
        """
        logger.info(f"正在从视频中提取音频: {video_path}")
        
        # 这里简化处理，实际项目中可以使用ffmpeg-python
        audio_path = video_path.rsplit('.', 1)[0] + '_audio.wav'
        
        # 注意：实际项目中需要安装ffmpeg并处理提取逻辑
        # 这里假设音频已存在或直接使用视频文件
        if not os.path.exists(audio_path):
            logger.warning(f"音频文件不存在，将尝试直接使用视频文件: {video_path}")
            return video_path
            
        return audio_path
    
    def transcribe_audio(self, audio_path: str, language: str = "zh") -> List[MeetingSegment]:
        """
        使用Whisper转录音频
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码，默认中文
            
        Returns:
            转录片段列表
        """
        logger.info(f"开始转录音频: {audio_path}")
        
        try:
            # 使用Whisper进行转录
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=True
            )
            
            segments = []
            for segment in result["segments"]:
                meeting_segment = MeetingSegment(
                    start_time=self._format_timestamp(segment["start"]),
                    end_time=self._format_timestamp(segment["end"]),
                    speaker="未知发言人",  # Whisper不识别说话人
                    content=segment["text"].strip()
                )
                segments.append(meeting_segment)
            
            logger.info(f"转录完成，共{len(segments)}个片段")
            return segments
            
        except Exception as e:
            logger.error(f"转录失败: {str(e)}")
            raise
    
    def generate_summary(self, segments: List[MeetingSegment]) -> MeetingSummary:
        """
        使用OpenAI GPT生成会议摘要
        
        Args:
            segments: 转录片段列表
            
        Returns:
            会议摘要
        """
        logger.info("开始生成会议摘要...")
        
        # 将转录内容合并为文本
        transcript_text = self._segments_to_text(segments)
        
        try:
            # 调用OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名专业的会议记录分析师，擅长提取关键信息和生成结构化摘要。"
                    },
                    {
                        "role": "user",
                        "content": self.summary_prompt.format(transcript=transcript_text)
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 解析JSON响应
            summary_json = response.choices[0].message.content
            summary_data = json.loads(summary_json)
            
            # 创建摘要对象
            summary = MeetingSummary(
                title=summary_data.get("title", "会议摘要"),
                overview=summary_data.get("overview", ""),
                key_points=summary_data.get("key_points", []),
                decisions=summary_data.get("decisions", []),
                action_items=summary_data.get("action_items", []),
                confidence_score=0.9,  # GPT模型置信度较高
                processing_time=0.0
            )
            
            logger.info("会议摘要生成完成")
            return summary
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            logger.error(f"API响应: {summary_json}")
            # 降级处理：返回基础摘要
            return self._create_basic_summary(transcript_text)
            
        except Exception as e:
            logger.error(f"摘要生成失败: {str(e)}")
            raise
    
    def process_meeting(self, video_path: str, language: str = "zh") -> Dict[str, Any]:
        """
        完整的会议处理流程
        
        Args:
            video_path: 视频文件路径
            language: 语言代码
            
        Returns:
            完整的处理结果
        """
        start_time = datetime.now()
        logger.info(f"开始处理会议视频: {video_path}")
        
        try:
            # 步骤1：提取音频
            audio_path = self.extract_audio_from_video(video_path)
            
            # 步骤2：转录音频
            segments = self.transcribe_audio(audio_path, language)
            
            # 步骤3：生成摘要
            summary = self.generate_summary(segments)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            summary.processing_time = processing_time
            
            # 构建完整结果
            result = {
                "meeting_id": f"meeting_{int(start_time.timestamp())}",
                "file_path": video_path,
                "transcript_segments": [
                    {
                        "start_time": seg.start_time,
                        "end_time": seg.end_time,
                        "speaker": seg.speaker,
                        "content": seg.content
                    }
                    for seg in segments
                ],
                "summary": {
                    "title": summary.title,
                    "overview": summary.overview,
                    "key_points": summary.key_points,
                    "decisions": summary.decisions,
                    "action_items": summary.action_items,
                    "confidence_score": summary.confidence_score,
                    "processing_time": summary.processing_time
                },
                "metadata": {
                    "language": language,
                    "total_segments": len(segments),
                    "processing_completed_at": datetime.now().isoformat()
                }
            }
            
            logger.info(f"会议处理完成，用时: {processing_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"会议处理失败: {str(e)}")
            raise
    
    def _format_timestamp(self, seconds: float) -> str:
        """格式化时间戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _segments_to_text(self, segments: List[MeetingSegment]) -> str:
        """将转录片段合并为文本"""
        lines = []
        for i, segment in enumerate(segments, 1):
            line = f"[{segment.start_time}] {segment.speaker}: {segment.content}"
            lines.append(line)
        return "\n".join(lines)
    
    def _create_basic_summary(self, transcript_text: str) -> MeetingSummary:
        """创建基础摘要（降级处理）"""
        logger.warning("使用基础摘要作为降级处理")
        
        # 简单的文本摘要逻辑
        lines = transcript_text.split('\n')
        key_points = []
        
        # 提取前5个重要片段作为关键点
        for i, line in enumerate(lines[:5]):
            if line.strip():
                key_points.append({
                    "topic": f"讨论点{i+1}",
                    "content": line.strip(),
                    "participants": ["未知"],
                    "timestamp": "未知"
                })
        
        return MeetingSummary(
            title="会议摘要（基础版）",
            overview=f"会议共包含{len(lines)}个发言片段",
            key_points=key_points,
            decisions=[],
            action_items=[],
            confidence_score=0.5,  # 基础摘要置信度较低
            processing_time=0.0
        )

def main():
    """演示主函数"""
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置OPENAI_API_KEY环境变量")
        return
    
    # 创建智能体
    agent = MeetingSummaryAgent(api_key)
    
    # 示例视频文件路径
    video_path = "demo_meeting.mp4"  # 请替换为实际文件路径
    
    if not os.path.exists(video_path):
        print(f"示例文件不存在: {video_path}")
        print("请提供有效的视频文件路径")
        return
    
    try:
        # 处理会议
        result = agent.process_meeting(video_path, language="zh")
        
        # 保存结果
        output_file = f"meeting_summary_{result['meeting_id']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"会议摘要已生成并保存到: {output_file}")
        print(f"摘要标题: {result['summary']['title']}")
        print(f"处理时间: {result['summary']['processing_time']:.2f}秒")
        print(f"关键点数量: {len(result['summary']['key_points'])}")
        print(f"决策数量: {len(result['summary']['decisions'])}")
        print(f"行动项数量: {len(result['summary']['action_items'])}")
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
        logger.error(f"演示失败: {str(e)}")

if __name__ == "__main__":
    main()