# 会议摘要智能体 - 适配器模式实现
"""
适配器模式实现，支持多种AI服务提供商
- OpenAI GPT (默认)
- 本地大模型 (ChatGLM3, Baichuan2等)
- 云服务 (百度文心一言, 阿里通义千问等)
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AIServiceAdapter(ABC):
    """AI服务适配器基类"""
    
    @abstractmethod
    def generate_summary(self, transcript: str, prompt: str) -> Dict[str, Any]:
        """生成摘要"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查服务是否可用"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        pass

class OpenAIAdapter(AIServiceAdapter):
    """OpenAI GPT适配器"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化OpenAI客户端"""
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai
            logger.info(f"OpenAI适配器初始化成功，模型: {self.model}")
        except ImportError:
            logger.error("OpenAI库未安装，请运行: pip install openai")
            raise
    
    def generate_summary(self, transcript: str, prompt: str) -> Dict[str, Any]:
        """使用OpenAI生成摘要"""
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的会议记录分析师。"},
                    {"role": "user", "content": prompt.format(transcript=transcript)}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.error(f"OpenAI响应解析失败: {str(e)}")
            # 降级处理：返回基础结构
            return self._create_fallback_summary(transcript)
        except Exception as e:
            logger.error(f"OpenAI调用失败: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """检查OpenAI服务是否可用"""
        try:
            # 简单测试API调用
            self.client.Model.list()
            return True
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取OpenAI模型信息"""
        return {
            "provider": "OpenAI",
            "model": self.model,
            "type": "cloud",
            "features": ["多语言支持", "上下文理解", "结构化输出"]
        }
    
    def _create_fallback_summary(self, transcript: str) -> Dict[str, Any]:
        """创建降级摘要"""
        lines = transcript.split('\n')[:5]
        return {
            "title": "会议摘要（OpenAI降级版）",
            "overview": f"会议包含{len(lines)}个主要讨论点",
            "key_points": [{"topic": f"讨论点{i+1}", "content": line, "participants": ["未知"], "timestamp": "未知"} 
                          for i, line in enumerate(lines)],
            "decisions": [],
            "action_items": [],
            "risks": [],
            "opportunities": []
        }

class LocalModelAdapter(AIServiceAdapter):
    """本地大模型适配器"""
    
    def __init__(self, model_path: str, model_type: str = "chatglm3"):
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """加载本地模型"""
        try:
            if self.model_type == "chatglm3":
                from transformers import AutoTokenizer, AutoModel
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
                self.model = AutoModel.from_pretrained(self.model_path, trust_remote_code=True, device='cuda')
                self.model = self.model.eval()
                logger.info(f"ChatGLM3模型加载成功: {self.model_path}")
            
            elif self.model_type == "baichuan2":
                from transformers import AutoTokenizer, AutoModelForCausalLM
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_path, trust_remote_code=True, device_map="auto")
                logger.info(f"Baichuan2模型加载成功: {self.model_path}")
            
            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")
                
        except ImportError as e:
            logger.error(f"transformers库未安装或模型加载失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"本地模型加载失败: {str(e)}")
            raise
    
    def generate_summary(self, transcript: str, prompt: str) -> Dict[str, Any]:
        """使用本地模型生成摘要"""
        try:
            full_prompt = prompt.format(transcript=transcript)
            
            if self.model_type == "chatglm3":
                response, history = self.model.chat(self.tokenizer, full_prompt, history=[])
            else:  # baichuan2
                inputs = self.tokenizer(full_prompt, return_tensors="pt")
                inputs = inputs.to("cuda")
                
                with torch.no_grad():
                    outputs = self.model.generate(**inputs, max_length=2048, temperature=0.3)
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # 提取生成的部分（去掉输入）
                response = response[len(full_prompt):]
            
            # 尝试解析JSON
            try:
                # 提取JSON部分（假设模型返回的是JSON字符串）
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
                else:
                    # 如果没有JSON，创建基础结构
                    return self._create_local_fallback_summary(transcript)
            except json.JSONDecodeError:
                return self._create_local_fallback_summary(transcript)
                
        except Exception as e:
            logger.error(f"本地模型生成失败: {str(e)}")
            return self._create_local_fallback_summary(transcript)
    
    def is_available(self) -> bool:
        """检查本地模型是否可用"""
        return self.model is not None and self.tokenizer is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取本地模型信息"""
        return {
            "provider": "Local",
            "model": self.model_type,
            "type": "local",
            "path": self.model_path,
            "features": ["离线运行", "数据安全", "可控性强"]
        }
    
    def _create_local_fallback_summary(self, transcript: str) -> Dict[str, Any]:
        """创建本地模型降级摘要"""
        lines = transcript.split('\n')[:3]
        return {
            "title": "会议摘要（本地模型版）",
            "overview": "基于本地模型生成的会议摘要",
            "key_points": [{"topic": f"要点{i+1}", "content": line, "participants": ["未知"], "timestamp": "未知"} 
                          for i, line in enumerate(lines)],
            "decisions": [],
            "action_items": [],
            "risks": [],
            "opportunities": []
        }

class BaiduAIAdapter(AIServiceAdapter):
    """百度AI适配器"""
    
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self._get_access_token()
    
    def _get_access_token(self):
        """获取百度API访问令牌"""
        try:
            import requests
            url = f"https://aip.baidubce.com/oauth/2.0/token"
            params = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.secret_key
            }
            
            response = requests.post(url, params=params)
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
                logger.info("百度AI适配器初始化成功")
            else:
                raise Exception("获取百度访问令牌失败")
                
        except Exception as e:
            logger.error(f"百度AI初始化失败: {str(e)}")
            raise
    
    def generate_summary(self, transcript: str, prompt: str) -> Dict[str, Any]:
        """使用百度AI生成摘要"""
        try:
            import requests
            
            url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
            headers = {"Content-Type": "application/json"}
            
            data = {
                "messages": [
                    {"role": "user", "content": prompt.format(transcript=transcript)}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(f"{url}?access_token={self.access_token}", 
                                   headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("result", "")
                
                # 尝试解析JSON
                try:
                    return json.loads(content)
                except:
                    return self._create_baidu_fallback_summary(transcript)
            else:
                logger.error(f"百度AI调用失败: {response.status_code}")
                return self._create_baidu_fallback_summary(transcript)
                
        except Exception as e:
            logger.error(f"百度AI生成失败: {str(e)}")
            return self._create_baidu_fallback_summary(transcript)
    
    def is_available(self) -> bool:
        """检查百度AI服务是否可用"""
        return self.access_token is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取百度AI模型信息"""
        return {
            "provider": "Baidu",
            "model": "文心一言",
            "type": "cloud",
            "features": ["中文优化", "本土化", "企业级"]
        }
    
    def _create_baidu_fallback_summary(self, transcript: str) -> Dict[str, Any]:
        """创建百度AI降级摘要"""
        lines = transcript.split('\n')[:4]
        return {
            "title": "会议摘要（百度AI版）",
            "overview": "基于百度文心一言生成的会议摘要",
            "key_points": [{"topic": f"关键讨论{i+1}", "content": line, "participants": ["未知"], "timestamp": "未知"} 
                          for i, line in enumerate(lines)],
            "decisions": [],
            "action_items": [],
            "risks": [],
            "opportunities": []
        }

class AIServiceManager:
    """AI服务管理器"""
    
    def __init__(self):
        self.adapters = {}
        self.current_adapter = None
        self.fallback_order = []
    
    def register_adapter(self, name: str, adapter: AIServiceAdapter):
        """注册适配器"""
        self.adapters[name] = adapter
        logger.info(f"注册AI适配器: {name}")
    
    def set_primary_adapter(self, name: str):
        """设置主适配器"""
        if name in self.adapters:
            self.current_adapter = name
            logger.info(f"设置主适配器: {name}")
        else:
            logger.error(f"适配器不存在: {name}")
            raise ValueError(f"适配器不存在: {name}")
    
    def set_fallback_order(self, order: List[str]):
        """设置降级顺序"""
        self.fallback_order = order
        logger.info(f"设置降级顺序: {order}")
    
    def generate_summary_with_fallback(self, transcript: str, prompt: str) -> Dict[str, Any]:
        """带降级的摘要生成"""
        # 首先尝试当前适配器
        if self.current_adapter and self.current_adapter in self.adapters:
            adapter = self.adapters[self.current_adapter]
            if adapter.is_available():
                try:
                    logger.info(f"使用适配器: {self.current_adapter}")
                    return adapter.generate_summary(transcript, prompt)
                except Exception as e:
                    logger.warning(f"主适配器失败: {str(e)}")
        
        # 尝试降级适配器
        for fallback_name in self.fallback_order:
            if fallback_name in self.adapters:
                adapter = self.adapters[fallback_name]
                if adapter.is_available():
                    try:
                        logger.info(f"使用降级适配器: {fallback_name}")
                        return adapter.generate_summary(transcript, prompt)
                    except Exception as e:
                        logger.warning(f"降级适配器失败: {str(e)}")
                        continue
        
        # 所有适配器都失败，返回错误
        raise RuntimeError("所有AI适配器都不可用")
    
    def get_available_adapters(self) -> Dict[str, Dict[str, Any]]:
        """获取可用适配器信息"""
        info = {}
        for name, adapter in self.adapters.items():
            info[name] = {
                "info": adapter.get_model_info(),
                "available": adapter.is_available()
            }
        return info

# 适配器工厂
def create_ai_service_manager(config: Dict[str, Any]) -> AIServiceManager:
    """创建AI服务管理器"""
    manager = AIServiceManager()
    
    # 注册OpenAI适配器
    if config.get("openai", {}).get("enabled"):
        openai_config = config["openai"]
        openai_adapter = OpenAIAdapter(
            api_key=openai_config["api_key"],
            model=openai_config.get("model", "gpt-3.5-turbo")
        )
        manager.register_adapter("openai", openai_adapter)
    
    # 注册本地模型适配器
    if config.get("local_model", {}).get("enabled"):
        local_config = config["local_model"]
        local_adapter = LocalModelAdapter(
            model_path=local_config["model_path"],
            model_type=local_config.get("type", "chatglm3")
        )
        manager.register_adapter("local_model", local_adapter)
    
    # 注册百度AI适配器
    if config.get("baidu", {}).get("enabled"):
        baidu_config = config["baidu"]
        baidu_adapter = BaiduAIAdapter(
            api_key=baidu_config["api_key"],
            secret_key=baidu_config["secret_key"]
        )
        manager.register_adapter("baidu", baidu_adapter)
    
    # 设置主适配器和降级顺序
    primary = config.get("primary_adapter", "openai")
    fallback_order = config.get("fallback_order", ["local_model", "baidu"])
    
    manager.set_primary_adapter(primary)
    manager.set_fallback_order(fallback_order)
    
    return manager