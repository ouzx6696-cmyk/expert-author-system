"""
作家分身Skill - API接口
提供RESTful风格的API接口，便于Agent平台集成
"""

import json
from typing import Dict, Any
from functools import wraps


def api_function(func):
    """API函数装饰器，统一处理返回格式"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, dict) and "success" in result:
                return result
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    return wrapper


class AuthorPersonaAPI:
    """
    作家分身Skill API类
    提供标准的接口供各Agent平台调用
    """

    def __init__(self, llm_client=None):
        from .skill_main import AuthorPersonaSkill
        self.skill = AuthorPersonaSkill(llm_client)

    @api_function
    def analyze_style(self, corpus_text: str, author_name: str) -> Dict[str, Any]:
        """分析风格API"""
        return self.skill.analyze_style(corpus_text, author_name)

    @api_function
    def compile_persona(self, style_profile: Dict, author_name: str, scene_type: str = None) -> Dict[str, Any]:
        """编译分身API"""
        return self.skill.compile_persona(style_profile, author_name, scene_type)

    @api_function
    def generate_with_persona(
        self,
        persona_prompt: str,
        user_request: str,
        style_profile: Dict = None,
        enable_iteration: bool = False,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """生成文本API"""
        return self.skill.generate_with_persona(
            persona_prompt, user_request, style_profile, enable_iteration, max_iterations
        )

    @api_function
    def complete_workflow(
        self,
        corpus_text: str,
        author_name: str,
        user_request: str,
        enable_iteration: bool = True
    ) -> Dict[str, Any]:
        """完整工作流API"""
        return self.skill.complete_workflow(corpus_text, author_name, user_request, enable_iteration)

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一请求处理函数

        Args:
            request: 请求数据，格式:
            {
                "action": "analyze_style|compile_persona|generate_with_persona|complete_workflow",
                "params": {...}
            }

        Returns:
            响应数据
        """
        action = request.get("action")
        params = request.get("params", {})

        action_map = {
            "analyze_style": self.analyze_style,
            "compile_persona": self.compile_persona,
            "generate_with_persona": self.generate_with_persona,
            "complete_workflow": self.complete_workflow
        }

        if action not in action_map:
            return {
                "success": False,
                "error": f"未知的操作: {action}"
            }

        return action_map[action](**params)


# 快捷函数
def create_api(llm_client=None):
    """创建API实例"""
    return AuthorPersonaAPI(llm_client)
