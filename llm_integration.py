"""
大模型API集成模块
提供统一的接口来调用不同的大模型服务（OpenAI、DeepSeek、Claude等）
"""

import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LLMClient:
    """大模型客户端 - 统一接口"""

    def __init__(self, provider: str = "openai"):
        """
        初始化LLM客户端

        Args:
            provider: 模型提供商 ('openai', 'deepseek', 'claude'等)
        """
        self.provider = provider.lower()
        self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY")
        self.base_url = os.getenv(f"{self.provider.upper()}_BASE_URL")
        self.model = os.getenv(f"{self.provider.upper()}_MODEL", "gpt-4")

        if not self.api_key:
            raise ValueError(f"请设置环境变量 {self.provider.upper()}_API_KEY")

        # 根据提供商初始化对应的客户端
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "deepseek":
            self._init_deepseek()
        else:
            raise ValueError(f"不支持的模型提供商: {provider}")

    def _init_openai(self):
        """初始化OpenAI客户端"""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.openai.com/v1"
            )
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")

    def _init_deepseek(self):
        """初始化DeepSeek客户端（兼容OpenAI格式）"""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.deepseek.com/v1"
            )
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")

    def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        聊天补全

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            生成的文本
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.choices[0].message.content

    def chat_completion_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天补全，返回JSON格式

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            解析后的JSON字典
        """
        # 在提示词中强调返回JSON
        json_system_prompt = system_prompt + "\n\n请以严格的JSON格式返回，不要包含任何其他文本或Markdown格式。"

        content = self.chat_completion(
            json_system_prompt,
            user_prompt,
            temperature,
            max_tokens,
            **kwargs
        )

        # 尝试解析JSON
        try:
            # 清理可能的Markdown格式
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {e}\n原始内容: {content}")


# 快捷函数
def create_llm_client(provider: str = "openai") -> LLMClient:
    """创建LLM客户端的快捷函数"""
    return LLMClient(provider)
