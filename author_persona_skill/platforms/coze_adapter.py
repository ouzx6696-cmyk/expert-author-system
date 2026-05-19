"""
作家分身Skill - Coze平台适配器
用于在Coze平台上安装和使用此Skill
"""

import json
from typing import Dict, Any
from ..api import AuthorPersonaAPI


class CozeSkillAdapter:
    """
    Coze平台Skill适配器
    遵循Coze的Plugin规范
    """

    def __init__(self, llm_client=None):
        self.api = AuthorPersonaAPI(llm_client)

    def handle_plugin_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coze Plugin调用处理函数

        Args:
            request: Coze传递的请求数据

        Returns:
            返回给Coze的响应数据
        """
        method = request.get("method", "complete_workflow")
        parameters = request.get("parameters", {})

        # 映射Coze参数到API参数
        params = {
            "corpus_text": parameters.get("corpus_text", ""),
            "author_name": parameters.get("author_name", "作家"),
            "user_request": parameters.get("user_request", ""),
            "enable_iteration": parameters.get("enable_iteration", True),
            "scene_type": parameters.get("scene_type"),
            "persona_prompt": parameters.get("persona_prompt"),
        }

        # 处理style_profile（可能是JSON字符串）
        style_profile_str = parameters.get("style_profile")
        if style_profile_str:
            try:
                params["style_profile"] = json.loads(style_profile_str)
            except:
                params["style_profile"] = None

        # 根据方法分发
        try:
            if method == "analyze_style":
                result = self.api.analyze_style(params["corpus_text"], params["author_name"])
            elif method == "compile_persona":
                result = self.api.compile_persona(
                    params["style_profile"],
                    params["author_name"],
                    params.get("scene_type")
                )
            elif method == "generate_with_persona":
                result = self.api.generate_with_persona(
                    params["persona_prompt"],
                    params["user_request"],
                    params.get("style_profile"),
                    params.get("enable_iteration", False),
                    parameters.get("max_iterations", 3)
                )
            else:  # complete_workflow
                result = self.api.complete_workflow(
                    params["corpus_text"],
                    params["author_name"],
                    params["user_request"],
                    params.get("enable_iteration", True)
                )

            return self._format_coze_output(result)

        except Exception as e:
            return {
                "status": "error",
                "error": {
                    "message": str(e)
                }
            }

    def _format_coze_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换为Coze平台的输出格式

        Args:
            result: API返回的原始结果

        Returns:
            Coze格式的输出
        """
        if not result.get("success"):
            return {
                "status": "error",
                "error": {
                    "message": result.get("error", "未知错误")
                }
            }

        # 成功情况
        output = {
            "status": "success",
            "data": {}
        }

        # 映射数据
        data = output["data"]
        if "final_text" in result:
            data["text"] = result["final_text"]
        if "persona_prompt" in result:
            data["persona_prompt"] = result["persona_prompt"]
        if "style_profile" in result:
            data["style_profile"] = json.dumps(result["style_profile"], ensure_ascii=False)
        if "quantitative_summary" in result:
            data["quantitative_summary"] = result["quantitative_summary"]
        if "qualitative_summary" in result:
            data["qualitative_summary"] = result["qualitative_summary"]
        if "iterations" in result:
            data["iterations"] = result["iterations"]
        if "final_score" in result:
            data["final_score"] = result["final_score"]

        return output


# Coze平台使用示例配置文件内容（YAML格式）
COZE_MANIFEST = """
# 作家分身Skill - Coze平台配置
# Coze Plugin Manifest

plugin:
  name: "author_persona_skill"
  version: "1.0.0"
  display_name:
    zh-CN: "作家分身Skill"
    en-US: "Author Persona Skill"
  description:
    zh-CN: "基于深度风格解构，创建高保真的作家文学分身，实现专业级文风仿写"
    en-US: "Create high-fidelity author persona for professional style imitation"
  category: "content_creation"
  icon: ""
  homepage: ""

  # 工具定义
  tools:
    - name: "complete_workflow"
      description:
        zh-CN: "完整工作流：从语料到生成的一站式处理"
        en-US: "Complete workflow: one-stop from corpus to generation"
      parameters:
        - name: "corpus_text"
          type: "string"
          required: true
          description:
            zh-CN: "小说原文文本"
            en-US: "Novel text"
        - name: "author_name"
          type: "string"
          required: true
          description:
            zh-CN: "作家名称"
            en-US: "Author name"
        - name: "user_request"
          type: "string"
          required: true
          description:
            zh-CN: "用户创作需求"
            en-US: "User writing request"
        - name: "enable_iteration"
          type: "boolean"
          required: false
          default: true
          description:
            zh-CN: "是否启用迭代优化"
            en-US: "Enable iteration optimization"
      returns:
        - name: "text"
          type: "string"
          description:
            zh-CN: "生成的文本"
            en-US: "Generated text"
        - name: "persona_prompt"
          type: "string"
          description:
            zh-CN: "分身提示词"
            en-US: "Persona prompt"
        - name: "style_profile"
          type: "string"
          description:
            zh-CN: "风格指纹（JSON）"
            en-US: "Style profile (JSON)"

    - name: "analyze_style"
      description:
        zh-CN: "分析小说文本，提取作家风格指纹"
        en-US: "Analyze novel text to extract style fingerprint"
      parameters:
        - name: "corpus_text"
          type: "string"
          required: true
          description:
            zh-CN: "小说原文文本"
            en-US: "Novel text"
        - name: "author_name"
          type: "string"
          required: true
          description:
            zh-CN: "作家名称"
            en-US: "Author name"
      returns:
        - name: "style_profile"
          type: "string"
          description:
            zh-CN: "风格指纹（JSON）"
            en-US: "Style profile (JSON)"

    - name: "compile_persona"
      description:
        zh-CN: "将风格指纹编译为分身提示词"
        en-US: "Compile style profile to persona prompt"
      parameters:
        - name: "style_profile"
          type: "string"
          required: true
          description:
            zh-CN: "风格指纹（JSON字符串）"
            en-US: "Style profile (JSON string)"
        - name: "author_name"
          type: "string"
          required: true
          description:
            zh-CN: "作家名称"
            en-US: "Author name"
        - name: "scene_type"
          type: "string"
          required: false
          description:
            zh-CN: "场景类型（battle/dialogue/scene/emotion/momentum/transition）"
            en-US: "Scene type (battle/dialogue/scene/emotion/momentum/transition)"
      returns:
        - name: "persona_prompt"
          type: "string"
          description:
            zh-CN: "分身提示词"
            en-US: "Persona prompt"

    - name: "generate_with_persona"
      description:
        zh-CN: "使用作家分身进行文本生成"
        en-US: "Generate text using author persona"
      parameters:
        - name: "persona_prompt"
          type: "string"
          required: true
          description:
            zh-CN: "分身提示词"
            en-US: "Persona prompt"
        - name: "user_request"
          type: "string"
          required: true
          description:
            zh-CN: "用户创作需求"
            en-US: "User writing request"
        - name: "style_profile"
          type: "string"
          required: false
          description:
            zh-CN: "风格指纹（JSON，用于裁判评估）"
            en-US: "Style profile (JSON for critic)"
        - name: "enable_iteration"
          type: "boolean"
          required: false
          default: false
          description:
            zh-CN: "是否启用迭代优化"
            en-US: "Enable iteration optimization"
      returns:
        - name: "text"
          type: "string"
          description:
            zh-CN: "生成的文本"
            en-US: "Generated text"
"""


# Coze平台使用示例配置文件内容（JSON格式）
COZE_MANIFEST_JSON = {
    "plugin": {
        "name": "author_persona_skill",
        "version": "1.0.0",
        "display_name": {
            "zh-CN": "作家分身Skill",
            "en-US": "Author Persona Skill"
        },
        "description": {
            "zh-CN": "基于深度风格解构，创建高保真的作家文学分身，实现专业级文风仿写",
            "en-US": "Create high-fidelity author persona for professional style imitation"
        },
        "tools": [
            {
                "name": "complete_workflow",
                "description": {
                    "zh-CN": "完整工作流：从语料到生成的一站式处理",
                    "en-US": "Complete workflow: one-stop from corpus to generation"
                },
                "parameters": [
                    {
                        "name": "corpus_text",
                        "type": "string",
                        "required": True,
                        "description": {
                            "zh-CN": "小说原文文本",
                            "en-US": "Novel text"
                        }
                    },
                    {
                        "name": "author_name",
                        "type": "string",
                        "required": True,
                        "description": {
                            "zh-CN": "作家名称",
                            "en-US": "Author name"
                        }
                    },
                    {
                        "name": "user_request",
                        "type": "string",
                        "required": True,
                        "description": {
                            "zh-CN": "用户创作需求",
                            "en-US": "User writing request"
                        }
                    },
                    {
                        "name": "enable_iteration",
                        "type": "boolean",
                        "required": False,
                        "default": True,
                        "description": {
                            "zh-CN": "是否启用迭代优化",
                            "en-US": "Enable iteration optimization"
                        }
                    }
                ],
                "returns": [
                    {
                        "name": "text",
                        "type": "string",
                        "description": {
                            "zh-CN": "生成的文本",
                            "en-US": "Generated text"
                        }
                    },
                    {
                        "name": "persona_prompt",
                        "type": "string",
                        "description": {
                            "zh-CN": "分身提示词",
                            "en-US": "Persona prompt"
                        }
                    }
                ]
            }
        ]
    }
}
