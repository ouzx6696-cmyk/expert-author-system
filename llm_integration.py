"""
大模型API集成模块
提供统一的接口来调用不同的大模型服务（OpenAI、DeepSeek、Claude等）
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LLMClient:
    """大模型客户端 - 统一接口（支持同步和异步）"""

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
        self.client = None
        self.async_client = None

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
            from openai import OpenAI, AsyncOpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.openai.com/v1"
            )
            self.async_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.openai.com/v1"
            )
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")

    def _init_deepseek(self):
        """初始化DeepSeek客户端（兼容OpenAI格式）"""
        try:
            from openai import OpenAI, AsyncOpenAI
            base_url = self.base_url or "https://api.deepseek.com/v1"
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            self.async_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            if self.model == "gpt-4":
                self.model = "deepseek-chat"
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
        聊天补全（同步版本）

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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM调用失败: {str(e)}")

    async def chat_completion_async(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        聊天补全（异步版本）

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

        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM调用失败: {str(e)}")

    def chat_completion_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天补全，返回JSON格式（同步版本）

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

        return self._parse_json_content(content)

    async def chat_completion_json_async(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天补全，返回JSON格式（异步版本）

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

        content = await self.chat_completion_async(
            json_system_prompt,
            user_prompt,
            temperature,
            max_tokens,
            **kwargs
        )

        return self._parse_json_content(content)

    def _parse_json_content(self, content: str) -> Dict[str, Any]:
        """
        解析JSON内容，处理各种格式问题

        Args:
            content: 可能包含JSON的文本内容

        Returns:
            解析后的字典
        """
        try:
            # 清理可能的Markdown格式
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取第一个大括号对
            try:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    raise ValueError("无法找到有效的JSON对象")
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON解析失败: {e}\n原始内容: {content}")

    def chat_completion_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        带历史记录的聊天补全（同步版本）

        Args:
            messages: 消息历史列表
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            生成的文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM调用失败: {str(e)}")

    async def chat_completion_with_history_async(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        带历史记录的聊天补全（异步版本）

        Args:
            messages: 消息历史列表
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            生成的文本
        """
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM调用失败: {str(e)}")


# 快捷函数
def create_llm_client(provider: str = "openai") -> LLMClient:
    """创建LLM客户端的快捷函数"""
    return LLMClient(provider)


def get_available_providers() -> List[str]:
    """获取可用的模型提供商列表"""
    return ["openai", "deepseek"]
