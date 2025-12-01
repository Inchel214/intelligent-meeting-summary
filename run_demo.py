# 智能会议摘要智能体 - 快速运行脚本
# 安装依赖: pip install openai whisper-python ffmpeg-python

import os
import sys
import json
from datetime import datetime
from meeting_summary_agent import MeetingSummaryAgent

def create_demo_subtitle_file():
    """创建演示字幕文件"""
    demo_subtitle = """[00:00:00] 张总: 各位同事好，今天我们讨论Q1产品规划
[00:00:15] 李经理: 我负责移动端开发，计划新增三个核心功能
[00:00:30] 王总监: 预算方面我们需要控制在500万以内
[00:00:45] 张总: 同意，重点投入AI功能和用户体验优化
[00:01:00] 李经理: 我建议采用React Native框架，可以跨平台开发
[00:01:15] 王总监: 这个方案可行，但需要评估团队学习成本
[00:01:30] 张总: 决策已定，采用React Native，李经理负责技术选型
[00:01:45] 李经理: 我将在下周完成技术方案文档
[00:02:00] 王总监: 预算审批我会在本周五前完成
[00:02:15] 张总: 好的，会议结束，谢谢大家"""
    
    with open("demo_subtitle.txt", "w", encoding="utf-8") as f:
        f.write(demo_subtitle)
    
    return "demo_subtitle.txt"

def create_test_audio_from_subtitle(subtitle_file):
    """从字幕文件创建测试音频（简化版，实际应生成真实音频）"""
    # 这里创建一个很短的静音音频文件作为占位符
    # 实际项目中应该使用真实的会议录音
    
    try:
        import numpy as np
        import wave
        
        # 创建1秒的静音音频
        duration = 1  # 秒
        sample_rate = 16000
        frequency = 440  # A4音符
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(frequency * t * 2 * np.pi)
        
        # 转换为16位整数
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # 保存为WAV文件
        with wave.open("demo_meeting.wav", 'wb') as wav_file:
            wav_file.setnchannels(1)  # 单声道
            wav_file.setsampwidth(2)  # 16位
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print("✓ 创建演示音频文件: demo_meeting.wav")
        return "demo_meeting.wav"
        
    except ImportError:
        print("⚠ numpy未安装，创建虚拟音频文件")
        # 创建一个空文件作为占位符
        with open("demo_meeting.wav", "wb") as f:
            f.write(b"dummy audio file")
        return "demo_meeting.wav"

def main():
    """主函数 - 快速演示"""
    print("🚀 智能会议摘要智能体 Demo")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误: 请设置OPENAI_API_KEY环境变量")
        print("💡 设置方法: export OPENAI_API_KEY='your-api-key'")
        return
    
    try:
        # 创建演示文件
        print("📁 创建演示文件...")
        subtitle_file = create_demo_subtitle_file()
        audio_file = create_test_audio_from_subtitle(subtitle_file)
        
        # 创建智能体
        print("🤖 初始化会议摘要智能体...")
        agent = MeetingSummaryAgent(api_key)
        
        # 处理模式选择
        print("\n📋 选择处理模式:")
        print("1. 使用演示字幕文件（推荐）")
        print("2. 使用真实音频文件")
        
        choice = input("\n请选择 (1-2): ").strip()
        
        if choice == "1":
            # 使用字幕文件直接生成摘要
            print("\n📝 使用演示字幕生成摘要...")
            
            # 读取字幕内容并转换为模拟转录结果
            with open(subtitle_file, "r", encoding="utf-8") as f:
                subtitle_content = f.read()
            
            # 模拟转录结果
            from meeting_summary_agent import MeetingSegment
            segments = []
            
            lines = subtitle_content.strip().split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    # 解析字幕格式 [时间戳] 说话人: 内容
                    if ']' in line and ':' in line:
                        time_part = line.split(']')[0] + ']'
                        speaker_part = line.split(']')[1].strip()
                        if ':' in speaker_part:
                            speaker = speaker_part.split(':')[0].strip()
                            content = speaker_part.split(':', 1)[1].strip()
                            
                            # 模拟时间戳
                            segments.append(MeetingSegment(
                                start_time=f"00:00:{i*15:02d}",
                                end_time=f"00:00:{(i+1)*15:02d}",
                                speaker=speaker,
                                content=content
                            ))
            
            # 生成摘要
            summary = agent.generate_summary(segments)
            
            # 构建结果
            result = {
                "meeting_id": f"demo_meeting_{int(datetime.now().timestamp())}",
                "file_path": subtitle_file,
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
                }
            }
            
        else:
            # 使用真实音频文件
            print(f"\n🎵 处理音频文件: {audio_file}")
            result = agent.process_meeting(audio_file, language="zh")
        
        # 保存结果
        output_file = f"meeting_summary_{result['meeting_id']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 显示结果
        print("\n✅ 会议摘要生成完成！")
        print("=" * 50)
        print(f"📄 摘要标题: {result['summary']['title']}")
        print(f"⏱️ 处理时间: {result['summary']['processing_time']:.2f}秒")
        print(f"📊 转录片段: {len(result['transcript_segments'])}个")
        print(f"🔑 关键点: {len(result['summary']['key_points'])}个")
        print(f"🎯 决策: {len(result['summary']['decisions'])}个")
        print(f"✅ 行动项: {len(result['summary']['action_items'])}个")
        print(f"💯 置信度: {result['summary']['confidence_score']:.2f}")
        
        print(f"\n📁 结果已保存到: {output_file}")
        
        # 显示详细内容
        print("\n📝 会议概述:")
        print(result['summary']['overview'])
        
        if result['summary']['key_points']:
            print("\n🔑 关键讨论点:")
            for i, point in enumerate(result['summary']['key_points'][:3], 1):
                print(f"{i}. {point.get('topic', '未知议题')}: {point.get('content', '')}")
        
        if result['summary']['decisions']:
            print("\n🎯 重要决策:")
            for i, decision in enumerate(result['summary']['decisions'][:3], 1):
                print(f"{i}. {decision.get('content', '')}")
        
        if result['summary']['action_items']:
            print("\n✅ 行动项:")
            for i, action in enumerate(result['summary']['action_items'][:3], 1):
                print(f"{i}. {action.get('task', '')} (负责人: {action.get('assignee', '未知')})")
        
        print("\n🎉 Demo运行完成！")
        
    except Exception as e:
        print(f"\n❌ 运行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()