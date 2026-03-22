"""
DeepSeek API服务
用于RAG问答系统和知识图谱的LLM生成

DeepSeek API兼容OpenAI格式，可以直接替换Gemini
"""
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import requests
import json

# 加载环境变量
load_dotenv()

try:
    import openai
except ImportError:
    print("警告: openai库未安装，请运行 pip install openai")
    openai = None


class DeepSeekService:
    """DeepSeek API服务类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com"):
        """
        初始化DeepSeek服务
        
        Args:
            api_key: DeepSeek API密钥，如果为None则从环境变量读取
            base_url: API基础URL，默认https://api.deepseek.com
        """
        if openai is None:
            raise ImportError("openai库未安装，请运行 pip install openai")
        
        # 获取API密钥
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API密钥未设置。请设置环境变量 DEEPSEEK_API_KEY 或在初始化时传入api_key参数"
            )
        
        # 配置OpenAI客户端（DeepSeek兼容OpenAI格式）
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        self.base_url = base_url
    
    def generate_response(
        self,
        query: str,
        context: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        model: str = "deepseek-chat"
    ) -> str:
        """
        生成回答
        
        Args:
            query: 用户问题
            context: 上下文文本列表（从知识库检索到的相关文本）
            system_prompt: 系统提示词（可选）
            temperature: 温度参数，控制随机性（0-1，默认0.7）
            max_tokens: 最大生成token数（可选）
            model: 使用的模型名称，默认deepseek-chat
        
        Returns:
            AI生成的回答
        """
        # 构建提示词
        prompt = self._build_prompt(query, context, system_prompt)
        
        # 构建消息
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # 如果有系统提示词，添加到消息开头
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        try:
            # 调用DeepSeek API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 提取回答文本
            if response and response.choices:
                return response.choices[0].message.content.strip()
            else:
                return "抱歉，我无法生成回答。请稍后重试。"
        
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
    def _build_prompt(
        self,
        query: str,
        context: List[str],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        构建RAG提示词
        
        Args:
            query: 用户问题
            context: 上下文文本列表
            system_prompt: 系统提示词
        
        Returns:
            完整的提示词
        """
        # 默认系统提示词
        default_system_prompt = """你是一个智能助手，基于提供的上下文信息回答用户的问题。
请遵循以下规则：
1. 只基于提供的上下文信息回答问题
2. 如果上下文中没有相关信息，请明确说明
3. 回答要准确、简洁、有帮助
4. 如果上下文信息有多个来源，请综合这些信息
5. 使用中文回答"""
        
        system = system_prompt or default_system_prompt
        
        # 构建上下文文本
        if context:
            context_text = "\n\n".join([
                f"[来源 {i+1}]\n{ctx}"
                for i, ctx in enumerate(context)
            ])
        else:
            context_text = "（无相关上下文信息）"
        
        # 构建完整提示词
        prompt = f"""{system}

上下文信息：
{context_text}

用户问题：{query}

请基于上述上下文信息回答用户的问题："""
        
        return prompt
    
    def generate_stream_response(
        self,
        query: str,
        context: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        model: str = "deepseek-chat"
    ):
        """
        流式生成回答（用于实时显示）
        
        Args:
            query: 用户问题
            context: 上下文文本列表
            system_prompt: 系统提示词
            temperature: 温度参数
            model: 模型名称
        
        Yields:
            回答文本片段
        """
        prompt = self._build_prompt(query, context, system_prompt)
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            yield f"错误: {str(e)}"
    
    def extract_entities_and_relations(self, text: str, model: str = "deepseek-chat") -> List[Dict]:
        """
        从文本中抽取实体和关系（用于知识图谱）
        
        Args:
            text: 输入文本
            model: 使用的模型名称
        
        Returns:
            三元组列表
        """
        prompt = f"""请从以下文本中抽取知识实体和它们之间的关系。

要求：
1. 识别文本中的主要实体（概念、人物、地点、事件等）
2. 识别实体之间的关系（如：属于、包含、导致、位于等）
3. 以三元组形式输出：(实体1, 关系, 实体2)

文本内容：
{text}

请以JSON数组格式输出，每个元素包含：
{{
    "entity1": "实体1名称",
    "relation": "关系类型",
    "entity2": "实体2名称",
    "confidence": 0.9
}}

只输出JSON数组，不要其他文字说明。如果文本中没有明确的实体关系，返回空数组[]。"""
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3  # 降低温度以提高准确性
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # 提取JSON部分
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text
            
            # 解析JSON
            try:
                triples = json.loads(json_str)
                if not isinstance(triples, list):
                    triples = []
            except json.JSONDecodeError:
                triples = []
            
            return triples
        
        except Exception as e:
            print(f"抽取实体和关系失败: {e}")
            return []


# 全局DeepSeek服务实例（懒加载）
_deepseek_service: Optional[DeepSeekService] = None


def get_deepseek_service() -> DeepSeekService:
    """
    获取全局DeepSeek服务实例（单例模式）
    
    Returns:
        DeepSeekService实例
    """
    global _deepseek_service
    if _deepseek_service is None:
        _deepseek_service = DeepSeekService()
    return _deepseek_service






