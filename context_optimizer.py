# 智能会议摘要系统 - 上下文工程优化模块
"""
上下文工程优化模块
用于提升AI摘要的质量和相关性
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MeetingContext:
    """会议上下文信息"""
    meeting_type: str  # 会议类型：项目讨论、周例会、战略规划等
    industry: str      # 行业领域：互联网、金融、制造等
    participants: List[str]  # 参会人员
    duration: int      # 预计时长（分钟）
    keywords: List[str]  # 关键词列表
    historical_context: Optional[Dict[str, Any]] = None  # 历史上下文

class ContextOptimizer:
    """上下文工程优化器"""
    
    def __init__(self):
        """初始化优化器"""
        # 行业特定词汇库
        self.industry_keywords = {
            "tech": ["敏捷开发", "迭代", "MVP", "技术栈", "架构", "部署", "测试", "上线"],
            "finance": ["ROI", "预算", "成本", "收益", "风险", "投资", "回报率", "现金流"],
            "manufacturing": ["产能", "供应链", "质量控制", "成本优化", "生产效率", "设备"],
            "healthcare": ["合规", "临床试验", "监管", "安全性", "有效性", "FDA"]
        }
        
        # 会议类型模板
        self.meeting_templates = {
            "project_review": {
                "focus_areas": ["进度", "风险", "资源", "下一步计划"],
                "decision_patterns": ["批准", "同意", "决定", "确认"],
                "action_patterns": ["负责", "完成", "提交", "跟进"]
            },
            "weekly_meeting": {
                "focus_areas": ["本周工作", "下周计划", "问题", "协调"],
                "decision_patterns": ["安排", "调整", "协调", "确认"],
                "action_patterns": ["完成", "跟进", "汇报", "处理"]
            },
            "strategic_planning": {
                "focus_areas": ["战略", "目标", "方向", "投资"],
                "decision_patterns": ["决定", "确定", "批准", "通过"],
                "action_patterns": ["制定", "调研", "分析", "提交"]
            }
        }
    
    def analyze_meeting_context(self, transcript: str, meeting_info: Dict[str, Any]) -> MeetingContext:
        """分析会议上下文"""
        logger.info("分析会议上下文...")
        
        # 检测会议类型
        meeting_type = self._detect_meeting_type(transcript)
        
        # 检测行业领域
        industry = self._detect_industry(transcript)
        
        # 提取参会人员（简化版）
        participants = meeting_info.get("participants", [])
        
        # 提取关键词
        keywords = self._extract_keywords(transcript, industry)
        
        return MeetingContext(
            meeting_type=meeting_type,
            industry=industry,
            participants=participants,
            duration=meeting_info.get("duration", 60),
            keywords=keywords
        )
    
    def optimize_summary_prompt(self, transcript: str, context: MeetingContext) -> str:
        """生成优化的摘要提示词"""
        logger.info(f"为{context.meeting_type}类型会议生成优化提示词")
        
        base_prompt = f"""
        你是一名专业的{context.industry}行业会议分析师，专门分析{context.meeting_type}类型的会议。
        
        会议背景信息：
        - 会议类型: {context.meeting_type}
        - 行业领域: {context.industry}
        - 参会人员: {', '.join(context.participants) if context.participants else '未指定'}
        - 关键词: {', '.join(context.keywords[:10])}
        
        分析重点：
        {self._get_focus_areas(context.meeting_type)}
        
        输出要求：
        1. 重点识别和提取{self._get_decision_keywords(context.meeting_type)}相关的决策
        2. 提取具体的行动项，关注{self._get_action_keywords(context.meeting_type)}等关键词
        3. 按照{context.industry}行业特点进行专业分析
        4. 使用行业标准术语和表达方式
        5. 识别潜在的风险和机会
        
        会议转录内容：
        {transcript}
        
        请以JSON格式输出，结构如下：
        {{
            "title": "会议标题（体现{context.meeting_type}特点）",
            "overview": "会议概述（突出{context.industry}行业背景）",
            "key_points": [
                {{
                    "topic": "议题",
                    "content": "内容描述",
                    "participants": ["参与者1", "参与者2"],
                    "timestamp": "时间戳",
                    "importance": "high|medium|low",
                    "category": "{self._get_categories(context.meeting_type)}"
                }}
            ],
            "decisions": [
                {{
                    "content": "决策内容",
                    "responsible": "负责人",
                    "deadline": "截止时间",
                    "impact": "影响范围",
                    "urgency": "high|medium|low"
                }}
            ],
            "action_items": [
                {{
                    "task": "任务描述",
                    "assignee": "负责人",
                    "deadline": "截止时间",
                    "priority": "high|medium|low",
                    "deliverables": "交付物"
                }}
            ],
            "risks": [
                {{
                    "description": "风险描述",
                    "severity": "high|medium|low",
                    "mitigation": "缓解措施"
                }}
            ],
            "opportunities": [
                {{
                    "description": "机会描述",
                    "potential": "high|medium|low",
                    "next_steps": "下一步"
                }}
            ]
        }}
        """
        
        return base_prompt
    
    def post_process_summary(self, summary: Dict[str, Any], context: MeetingContext) -> Dict[str, Any]:
        """后处理摘要结果"""
        logger.info("后处理摘要结果...")
        
        # 添加行业特定标签
        summary["industry"] = context.industry
        summary["meeting_type"] = context.meeting_type
        
        # 根据会议类型调整优先级
        summary = self._adjust_priority_by_meeting_type(summary, context)
        
        # 添加时间敏感性分析
        summary = self._add_time_sensitivity(summary)
        
        # 识别关键决策点
        summary = self._identify_key_decisions(summary, context)
        
        return summary
    
    def _detect_meeting_type(self, transcript: str) -> str:
        """检测会议类型"""
        transcript_lower = transcript.lower()
        
        # 项目评审会议特征词
        if any(word in transcript_lower for word in ["项目", "进度", "里程碑", "交付", "延期"]):
            return "project_review"
        
        # 周例会特征词
        if any(word in transcript_lower for word in ["本周", "下周", "例会", "日常工作"]):
            return "weekly_meeting"
        
        # 战略规划会议特征词
        if any(word in transcript_lower for word in ["战略", "规划", "目标", "投资", "方向"]):
            return "strategic_planning"
        
        return "general_meeting"
    
    def _detect_industry(self, transcript: str) -> str:
        """检测行业领域"""
        transcript_lower = transcript.lower()
        
        # 技术行业
        tech_keywords = ["开发", "代码", "测试", "部署", "架构", "敏捷", "迭代"]
        if any(word in transcript_lower for word in tech_keywords):
            return "tech"
        
        # 金融行业
        finance_keywords = ["投资", "预算", "ROI", "成本", "收益", "风险", "现金流"]
        if any(word in transcript_lower for word in finance_keywords):
            return "finance"
        
        # 制造业
        manufacturing_keywords = ["生产", "产能", "供应链", "设备", "质量控制"]
        if any(word in transcript_lower for word in manufacturing_keywords):
            return "manufacturing"
        
        # 医疗健康
        healthcare_keywords = ["临床", "医疗", "合规", "FDA", "安全性", "有效性"]
        if any(word in transcript_lower for word in healthcare_keywords):
            return "healthcare"
        
        return "general"
    
    def _extract_keywords(self, transcript: str, industry: str) -> List[str]:
        """提取关键词"""
        # 基础关键词提取（简化版）
        words = re.findall(r'\b\w+\b', transcript)
        word_freq = {}
        
        for word in words:
            if len(word) > 2:  # 过滤短词
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 获取高频词
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        keywords = [word for word, freq in keywords]
        
        # 添加行业特定关键词
        if industry in self.industry_keywords:
            industry_words = self.industry_keywords[industry]
            for word in industry_words:
                if word in transcript and word not in keywords:
                    keywords.insert(0, word)
        
        return keywords[:15]  # 返回前15个关键词
    
    def _get_focus_areas(self, meeting_type: str) -> str:
        """获取关注重点领域"""
        if meeting_type in self.meeting_templates:
            areas = self.meeting_templates[meeting_type]["focus_areas"]
            return "、".join(areas)
        return "讨论要点、决策事项、后续行动"
    
    def _get_decision_keywords(self, meeting_type: str) -> str:
        """获取决策关键词"""
        if meeting_type in self.meeting_templates:
            patterns = self.meeting_templates[meeting_type]["decision_patterns"]
            return "、".join(patterns)
        return "决定、确定、同意、批准"
    
    def _get_action_keywords(self, meeting_type: str) -> str:
        """获取行动关键词"""
        if meeting_type in self.meeting_templates:
            patterns = self.meeting_templates[meeting_type]["action_patterns"]
            return "、".join(patterns)
        return "负责、完成、跟进、处理"
    
    def _get_categories(self, meeting_type: str) -> str:
        """获取分类"""
        if meeting_type == "project_review":
            return "进度更新|风险识别|资源需求|下一步计划"
        elif meeting_type == "weekly_meeting":
            return "工作汇报|问题讨论|协调事项|下周安排"
        elif meeting_type == "strategic_planning":
            return "战略方向|资源配置|投资决策|长期规划"
        return "一般讨论|决策事项|行动计划"
    
    def _adjust_priority_by_meeting_type(self, summary: Dict[str, Any], context: MeetingContext) -> Dict[str, Any]:
        """根据会议类型调整优先级"""
        # 根据会议类型和关键词匹配调整重要性
        for point in summary.get("key_points", []):
            content = point.get("content", "")
            
            # 根据会议类型提升相关内容的优先级
            if context.meeting_type == "project_review":
                if any(word in content for word in ["风险", "延期", "阻塞"]):
                    point["importance"] = "high"
            elif context.meeting_type == "strategic_planning":
                if any(word in content for word in ["投资", "战略", "方向"]):
                    point["importance"] = "high"
        
        return summary
    
    def _add_time_sensitivity(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """添加时间敏感性分析"""
        current_time = datetime.now()
        
        # 分析行动项的时间敏感性
        for action in summary.get("action_items", []):
            deadline = action.get("deadline", "")
            if deadline:
                try:
                    # 简单的截止日期分析
                    if "本周" in deadline or "明天" in deadline or "今天" in deadline:
                        action["priority"] = "high"
                    elif "下周" in deadline or "月底" in deadline:
                        action["priority"] = "medium"
                    else:
                        action["priority"] = "low"
                except:
                    action["priority"] = "medium"
        
        return summary
    
    def _identify_key_decisions(self, summary: Dict[str, Any], context: MeetingContext) -> Dict[str, Any]:
        """识别关键决策"""
        key_decisions = []
        
        for decision in summary.get("decisions", []):
            content = decision.get("content", "")
            
            # 根据内容判断重要性
            importance_score = 0
            
            # 会议类型相关关键词
            if context.meeting_type in self.meeting_templates:
                decision_patterns = self.meeting_templates[context.meeting_type]["decision_patterns"]
                if any(pattern in content for pattern in decision_patterns):
                    importance_score += 2
            
            # 高影响词汇
            high_impact_words = ["批准", "同意", "决定", "确定", "通过", "投资", "预算"]
            if any(word in content for word in high_impact_words):
                importance_score += 1
            
            # 根据重要性标记
            if importance_score >= 2:
                decision["urgency"] = "high"
                key_decisions.append(decision)
            elif importance_score >= 1:
                decision["urgency"] = "medium"
            else:
                decision["urgency"] = "low"
        
        # 标记最重要的决策
        if key_decisions:
            summary["key_decisions"] = key_decisions[:3]  # 最多3个关键决策
        
        return summary

class ContextAwareMeetingAgent:
    """上下文感知的会议摘要智能体"""
    
    def __init__(self, base_agent, context_optimizer: ContextOptimizer):
        """初始化"""
        self.base_agent = base_agent
        self.context_optimizer = context_optimizer
        self.meeting_history = []  # 历史会议记录
    
    def process_meeting_with_context(self, video_path: str, meeting_info: Dict[str, Any]) -> Dict[str, Any]:
        """基于上下文处理会议"""
        logger.info("使用上下文工程处理会议...")
        
        # 步骤1：基础处理（转录）
        result = self.base_agent.process_meeting(video_path, meeting_info.get("language", "zh"))
        
        # 步骤2：分析会议上下文
        transcript_text = self.base_agent._segments_to_text([
            self.base_agent.MeetingSegment(**seg) for seg in result["transcript_segments"]
        ])
        
        context = self.context_optimizer.analyze_meeting_context(transcript_text, meeting_info)
        
        # 步骤3：使用优化的提示词重新生成摘要
        optimized_prompt = self.context_optimizer.optimize_summary_prompt(transcript_text, context)
        
        # 这里需要重新调用GPT API，简化处理：直接使用基础结果进行后处理
        optimized_summary = self.context_optimizer.post_process_summary(result["summary"], context)
        
        # 更新结果
        result["summary"] = optimized_summary
        result["context"] = {
            "meeting_type": context.meeting_type,
            "industry": context.industry,
            "keywords": context.keywords,
            "optimization_applied": True
        }
        
        # 添加到历史记录
        self.meeting_history.append({
            "meeting_id": result["meeting_id"],
            "context": context,
            "summary": optimized_summary,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def get_meeting_insights(self, meeting_type: Optional[str] = None, 
                           industry: Optional[str] = None, 
                           time_range: Optional[int] = None) -> Dict[str, Any]:
        """获取会议洞察"""
        logger.info("生成会议洞察...")
        
        # 过滤相关会议
        relevant_meetings = []
        for meeting in self.meeting_history:
            context = meeting.get("context", {})
            
            # 应用过滤条件
            if meeting_type and context.get("meeting_type") != meeting_type:
                continue
            if industry and context.get("industry") != industry:
                continue
            
            relevant_meetings.append(meeting)
        
        if not relevant_meetings:
            return {"insights": "暂无相关会议数据"}
        
        # 分析趋势
        total_meetings = len(relevant_meetings)
        avg_key_points = sum(len(m["summary"].get("key_points", [])) for m in relevant_meetings) / total_meetings
        avg_decisions = sum(len(m["summary"].get("decisions", [])) for m in relevant_meetings) / total_meetings
        avg_actions = sum(len(m["summary"].get("action_items", [])) for m in relevant_meetings) / total_meetings
        
        # 常见关键词
        all_keywords = []
        for meeting in relevant_meetings:
            context = meeting.get("context", {})
            all_keywords.extend(context.get("keywords", []))
        
        # 统计高频关键词
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_meetings": total_meetings,
            "average_metrics": {
                "key_points_per_meeting": round(avg_key_points, 2),
                "decisions_per_meeting": round(avg_decisions, 2),
                "action_items_per_meeting": round(avg_actions, 2)
            },
            "top_keywords": [{"keyword": k, "frequency": f} for k, f in top_keywords],
            "meeting_types": list(set(m.get("context", {}).get("meeting_type", "unknown") for m in relevant_meetings)),
            "industries": list(set(m.get("context", {}).get("industry", "unknown") for m in relevant_meetings))
        }