"""
Gemini API服务
用于RAG问答系统的LLM生成
"""
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    print("警告: google-generativeai未安装，请运行 pip install google-generativeai")
    genai = None


class GeminiService:
    """Gemini API服务类"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        """
        初始化Gemini服务
        
        Args:
            api_key: Gemini API密钥，如果为None则从环境变量读取
            model_name: 使用的模型名称，默认gemini-pro
        """
        if genai is None:
            raise ImportError("google-generativeai未安装，请运行 pip install google-generativeai")
        
        # 获取API密钥
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API密钥未设置。请设置环境变量 GEMINI_API_KEY 或在初始化时传入api_key参数"
            )
        
        # 配置Gemini
        genai.configure(api_key=self.api_key)
        
        # 初始化模型
        self.model_name = model_name
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            raise Exception(f"初始化Gemini模型失败: {str(e)}")
    
    def generate_response(
        self,
        query: str,
        context: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        生成回答
        
        Args:
            query: 用户问题
            context: 上下文文本列表（从知识库检索到的相关文本）
            system_prompt: 系统提示词（可选）
            temperature: 温度参数，控制随机性（0-1，默认0.7）
            max_tokens: 最大生成token数（可选）
        
        Returns:
            AI生成的回答
        """
        # 构建提示词
        prompt = self._build_prompt(query, context, system_prompt)
        
        # 配置生成参数
        generation_config = {
            "temperature": temperature,
        }
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        try:
            # 调用Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # 提取回答文本
            if response and response.text:
                return response.text.strip()
            else:
                return "抱歉，我无法生成回答。请稍后重试。"
        
        except Exception as e:
            raise Exception(f"Gemini API调用失败: {str(e)}")
    
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
        temperature: float = 0.7
    ):
        """
        流式生成回答（用于实时显示）
        
        Args:
            query: 用户问题
            context: 上下文文本列表
            system_prompt: 系统提示词
            temperature: 温度参数
        
        Yields:
            回答文本片段
        """
        prompt = self._build_prompt(query, context, system_prompt)
        
        generation_config = {
            "temperature": temperature,
        }
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            yield f"错误: {str(e)}"


# 全局Gemini服务实例（懒加载）
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """
    获取全局Gemini服务实例（单例模式）
    
    Returns:
        GeminiService实例
    """
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service






