#!/usr/bin/env python3
"""
增强版会议摘要智能体 - 集成上下文工程和适配器模式
支持多种AI服务提供商和上下文优化
"""

import os
import sys
import json
import yaml
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# 导入核心模块
from meeting_summary_agent import MeetingSummaryAgent
from context_optimizer import ContextOptimizer, ContextAwareMeetingAgent
from ai_service_adapter import create_ai_service_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedMeetingAgent:
    """增强版会议摘要智能体"""
    
    def __init__(self, config_path: str = "ai_config.yaml"):
        """初始化增强版智能体"""
        logger.info("初始化增强版会议摘要智能体...")
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 创建AI服务管理器
        self.ai_manager = create_ai_service_manager(self.config.get("ai_services", {}))
        
        # 创建基础智能体
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key and self.config.get("ai_services", {}).get("openai", {}).get("enabled"):
            raise ValueError("请设置OPENAI_API_KEY环境变量")
        
        self.base_agent = MeetingSummaryAgent(openai_key)
        
        # 创建上下文优化器
        self.context_optimizer = ContextOptimizer()
        
        # 创建上下文感知智能体
        self.context_agent = ContextAwareMeetingAgent(self.base_agent, self.context_optimizer)
        
        logger.info("增强版智能体初始化完成")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"配置文件不存在，使用默认配置: {config_path}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"配置文件加载失败: {str(e)}")
            raise
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "ai_services": {
                "openai": {
                    "enabled": True,
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "model": "gpt-3.5-turbo"
                }
            },
            "context_engineering": {
                "enabled": True
            }
        }
    
    def process_video_with_enhanced_context(self, video_path: str, meeting_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        使用增强上下文处理视频
        
        Args:
            video_path: 视频文件路径
            meeting_info: 会议信息（可选）
            
        Returns:
            增强处理结果
        """
        logger.info(f"开始增强处理: {video_path}")
        
        if meeting_info is None:
            meeting_info = {}
        
        # 使用上下文感知智能体处理
        result = self.context_agent.process_meeting_with_context(video_path, meeting_info)
        
        # 添加增强信息
        result["enhanced_info"] = {
            "processing_engine": "enhanced_context_aware",
            "ai_service": self.ai_manager.get_available_adapters(),
            "context_optimization": True,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def process_subtitle_directly(self, subtitle_text: str, meeting_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        直接处理字幕文本（用于演示和测试）
        
        Args:
            subtitle_text: 字幕文本
            meeting_info: 会议信息（可选）
            
        Returns:
            处理结果
        """
        logger.info("直接处理字幕文本...")
        
        if meeting_info is None:
            meeting_info = {}
        
        # 解析字幕文本为转录片段
        from meeting_summary_agent import MeetingSegment
        segments = self._parse_subtitle_text(subtitle_text)
        
        # 分析上下文
        transcript_text = self.base_agent._segments_to_text(segments)
        context = self.context_optimizer.analyze_meeting_context(transcript_text, meeting_info)
        
        # 生成优化的提示词
        optimized_prompt = self.context_optimizer.optimize_summary_prompt(transcript_text, context)
        
        # 使用AI服务管理器生成摘要
        try:
            summary_data = self.ai_manager.generate_summary_with_fallback(transcript_text, optimized_prompt)
        except Exception as e:
            logger.error(f"AI服务失败，使用基础摘要: {str(e)}")
            summary_data = self.base_agent.generate_summary(segments).__dict__
        
        # 后处理优化
        optimized_summary = self.context_optimizer.post_process_summary(summary_data, context)
        
        # 构建结果
        result = {
            "meeting_id": f"subtitle_meeting_{int(datetime.now().timestamp())}",
            "input_type": "subtitle_text",
            "transcript_segments": [
                {
                    "start_time": seg.start_time,
                    "end_time": seg.end_time,
                    "speaker": seg.speaker,
                    "content": seg.content
                }
                for seg in segments
            ],
            "summary": optimized_summary,
            "context": {
                "meeting_type": context.meeting_type,
                "industry": context.industry,
                "keywords": context.keywords,
                "participants": context.participants
            },
            "enhanced_info": {
                "processing_engine": "enhanced_subtitle_direct",
                "ai_service_used": self._get_successful_adapter(),
                "context_optimization": True,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return result
    
    def _parse_subtitle_text(self, subtitle_text: str) -> List[Any]:
        """解析字幕文本"""
        segments = []
        lines = subtitle_text.strip().split('\n')
        
        for i, line in enumerate(lines):
            if line.strip() and ']' in line and ':' in line:
                try:
                    # 解析格式: [时间戳] 说话人: 内容
                    time_part = line.split(']')[0] + ']'
                    speaker_part = line.split(']')[1].strip()
                    
                    if ':' in speaker_part:
                        speaker = speaker_part.split(':')[0].strip()
                        content = speaker_part.split(':', 1)[1].strip()
                        
                        # 创建片段
                        from meeting_summary_agent import MeetingSegment
                        segment = MeetingSegment(
                            start_time=f"00:00:{i*15:02d}",
                            end_time=f"00:00:{(i+1)*15:02d}",
                            speaker=speaker,
                            content=content
                        )
                        segments.append(segment)
                except Exception as e:
                    logger.warning(f"解析字幕行失败: {line}, 错误: {str(e)}")
                    continue
        
        return segments
    
    def _get_successful_adapter(self) -> str:
        """获取成功使用的适配器"""
        # 这里简化处理，返回当前主适配器
        return "openai"  # 可以根据实际情况判断哪个适配器成功了
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "status": "operational",
            "ai_services": self.ai_manager.get_available_adapters(),
            "context_engineering": self.config.get("context_engineering", {}).get("enabled", False),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    def get_meeting_insights(self, **filters) -> Dict[str, Any]:
        """获取会议洞察"""
        return self.context_agent.get_meeting_insights(**filters)

def create_demo_meeting():
    """创建演示会议数据"""
    return """[00:00:00] 张总: 各位同事好，今天我们讨论Q1产品规划，主要围绕移动端新功能开发
[00:00:30] 李经理: 我负责移动端开发，计划新增三个核心功能：AI语音助手、离线缓存、智能推荐
[00:01:00] 王总监: 预算方面我们需要控制在500万以内，ROI要求达到150%以上
[00:01:30] 张总: 同意，重点投入AI功能和用户体验优化，技术选型要考虑到团队现状
[00:02:00] 李经理: 我建议采用React Native框架，可以跨平台开发，减少维护成本
[00:02:30] 王总监: 这个方案可行，但需要评估团队学习成本和技术风险
[00:03:00] 张总: 决策已定，采用React Native技术栈，李经理负责技术选型文档
[00:03:30] 李经理: 我将在下周三前完成技术方案文档，包括架构设计和风险评估
[00:04:00] 王总监: 预算审批我会在本周五前完成，确保项目按时启动
[00:04:30] 张总: 好的，希望大家按计划推进，下次会议我们评审技术方案
[00:05:00] 张总: 会议结束，谢谢大家参与"""

def main():
    """主函数 - 增强版演示"""
    print("🚀 增强版会议摘要智能体 Demo")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误: 请设置OPENAI_API_KEY环境变量")
        print("💡 设置方法: export OPENAI_API_KEY='your-api-key'")
        return
    
    try:
        # 创建增强版智能体
        print("🤖 初始化增强版智能体...")
        agent = EnhancedMeetingAgent()
        
        # 显示系统状态
        print("\n📊 系统状态:")
        status = agent.get_system_status()
        print(f"✅ AI服务: {len(status['ai_services'])}个适配器")
        for name, info in status['ai_services'].items():
            print(f"   - {name}: {'✅' if info['available'] else '❌'} {info['info']['provider']}")
        
        # 会议信息
        meeting_info = {
            "title": "Q1产品规划会议",
            "participants": ["张总", "李经理", "王总监"],
            "duration": 60,
            "industry": "tech",
            "meeting_type": "strategic_planning"
        }
        
        # 处理演示字幕
        print(f"\n📝 处理会议: {meeting_info['title']}")
        subtitle_text = create_demo_meeting()
        
        result = agent.process_subtitle_directly(subtitle_text, meeting_info)
        
        # 显示结果
        print("\n✅ 处理完成！")
        print("=" * 60)
        
        summary = result['summary']
        context = result['context']
        
        print(f"📋 会议标题: {summary['title']}")
        print(f"🏢 行业: {context['industry']}")
        print(f"📅 类型: {context['meeting_type']}")
        print(f"👥 参会者: {', '.join(context['participants'])}")
        print(f"⏱️ 处理时间: {summary.get('processing_time', 0):.2f}秒")
        print(f"💯 置信度: {summary.get('confidence_score', 0):.2f}")
        
        print(f"\n📝 会议概述:")
        print(f"{summary['overview']}")
        
        if summary.get('key_points'):
            print(f"\n🔑 关键讨论点 ({len(summary['key_points'])}个):")
            for i, point in enumerate(summary['key_points'][:5], 1):
                importance = point.get('importance', 'medium')
                importance_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(importance, '⚪')
                print(f"{importance_icon} {i}. {point.get('topic', '未知议题')}: {point.get('content', '')}")
        
        if summary.get('decisions'):
            print(f"\n🎯 重要决策 ({len(summary['decisions'])}个):")
            for i, decision in enumerate(summary['decisions'][:3], 1):
                urgency = decision.get('urgency', 'medium')
                urgency_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(urgency, '⚪')
                print(f"{urgency_icon} {i}. {decision.get('content', '')}")
                if decision.get('responsible'):
                    print(f"   👤 负责人: {decision['responsible']}")
        
        if summary.get('action_items'):
            print(f"\n✅ 行动项 ({len(summary['action_items'])}个):")
            for i, action in enumerate(summary['action_items'][:3], 1):
                priority = action.get('priority', 'medium')
                priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
                print(f"{priority_icon} {i}. {action.get('task', '')}")
                print(f"   👤 {action.get('assignee', '未知')} | 📅 {action.get('deadline', '未指定')}")
        
        if summary.get('risks'):
            print(f"\n⚠️ 识别的风险 ({len(summary['risks'])}个):")
            for i, risk in enumerate(summary['risks'][:3], 1):
                severity = risk.get('severity', 'medium')
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
                print(f"{severity_icon} {i}. {risk.get('description', '')}")
        
        if summary.get('opportunities'):
            print(f"\n🚀 识别的机会 ({len(summary['opportunities'])}个):")
            for i, opp in enumerate(summary['opportunities'][:3], 1):
                potential = opp.get('potential', 'medium')
                potential_icon = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}.get(potential, '⚪')
                print(f"{potential_icon} {i}. {opp.get('description', '')}")
        
        # 保存结果
        output_file = f"enhanced_meeting_summary_{result['meeting_id']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 完整结果已保存到: {output_file}")
        
        # 获取会议洞察
        print(f"\n📊 会议洞察:")
        insights = agent.get_meeting_insights(industry="tech", meeting_type="strategic_planning")
        if insights.get("total_meetings", 0) > 0:
            print(f"📈 已分析 {insights['total_meetings']} 场相关会议")
            print(f"📊 平均每场会议 {insights['average_metrics']['key_points_per_meeting']} 个关键点")
            print(f"🎯 平均每场会议 {insights['average_metrics']['decisions_per_meeting']} 个决策")
            print(f"✅ 平均每场会议 {insights['average_metrics']['action_items_per_meeting']} 个行动项")
        
        print("\n🎉 增强版演示完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 运行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()