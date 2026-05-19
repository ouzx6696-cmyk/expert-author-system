"""
作家分身Skill - Dify平台适配器
用于在Dify平台上安装和使用此Skill
"""

import json
from typing import Dict, Any
from ..api import AuthorPersonaAPI


class DifySkillAdapter:
    """
    Dify平台Skill适配器
    遵循Dify的Plugin规范
    """

    def __init__(self, llm_client=None):
        self.api = AuthorPersonaAPI(llm_client)

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dify Skill执行入口

        Args:
            inputs: Dify传递的输入数据

        Returns:
            返回给Dify的输出数据
        """
        action = inputs.get("action", "complete_workflow")
        params = {
            "corpus_text": inputs.get("corpus_text", ""),
            "author_name": inputs.get("author_name", "作家"),
            "user_request": inputs.get("user_request", ""),
            "enable_iteration": inputs.get("enable_iteration", True),
            "scene_type": inputs.get("scene_type"),
            "style_profile": inputs.get("style_profile"),
            "persona_prompt": inputs.get("persona_prompt")
        }

        # 清理空参数
        params = {k: v for k, v in params.items() if v is not None}

        # 根据action分发
        if action == "analyze_style":
            result = self.api.analyze_style(params["corpus_text"], params["author_name"])
        elif action == "compile_persona":
            result = self.api.compile_persona(
                params["style_profile"],
                params["author_name"],
                params.get("scene_type")
            )
        elif action == "generate_with_persona":
            result = self.api.generate_with_persona(
                params["persona_prompt"],
                params["user_request"],
                params.get("style_profile"),
                params.get("enable_iteration", False),
                inputs.get("max_iterations", 3)
            )
        else:  # complete_workflow
            result = self.api.complete_workflow(
                params["corpus_text"],
                params["author_name"],
                params["user_request"],
                params.get("enable_iteration", True)
            )

        # 转换为Dify格式
        return self._format_dify_output(result)

    def _format_dify_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换为Dify平台的输出格式

        Args:
            result: API返回的原始结果

        Returns:
            Dify格式的输出
        """
        output = {
            "success": result.get("success", False),
        }

        if result.get("success"):
            # 成功情况
            if "final_text" in result:
                output["text"] = result["final_text"]
            if "persona_prompt" in result:
                output["persona_prompt"] = result["persona_prompt"]
            if "style_profile" in result:
                output["style_profile"] = json.dumps(result["style_profile"], ensure_ascii=False)
            if "quantitative_summary" in result:
                output["quantitative_summary"] = json.dumps(result["quantitative_summary"], ensure_ascii=False)
            if "qualitative_summary" in result:
                output["qualitative_summary"] = json.dumps(result["qualitative_summary"], ensure_ascii=False)
            if "iterations" in result:
                output["iterations"] = json.dumps(result["iterations"], ensure_ascii=False)
        else:
            # 失败情况
            output["error"] = result.get("error", "未知错误")

        return output


# Dify平台使用示例配置文件内容
DIFY_MANIFEST = """
provider:
  name: author_persona_skill
  label:
    en_US: Author Persona Skill
    zh_Hans: 作家分身Skill
  description:
    en_US: Create high-fidelity author persona for professional style imitation
    zh_Hans: 创建高保真的作家文学分身，实现专业级文风仿写
  icon: ""
  icon_background: ""
  help:
    en_US: Upload novel text to create an author persona, then use it for style imitation
    zh_Hans: 上传小说文本创建作家分身，然后使用它进行文风仿写

tools:
  - name: complete_workflow
    label:
      en_US: Complete Workflow
      zh_Hans: 完整工作流
    description:
      en_US: One-stop from corpus to generation
      zh_Hans: 从语料到生成的一站式处理
    parameters:
      - name: corpus_text
        type: string
        required: true
        label:
          en_US: Novel Text
          zh_Hans: 小说文本
        human_description:
          en_US: Paste your novel text here
          zh_Hans: 在此粘贴小说文本
        form: llm
      - name: author_name
        type: string
        required: true
        label:
          en_US: Author Name
          zh_Hans: 作家名称
        human_description:
          en_US: Name of the author
          zh_Hans: 作家名称
        form: form
      - name: user_request
        type: string
        required: true
        label:
          en_US: Writing Request
          zh_Hans: 创作需求
        human_description:
          en_US: Describe what you want to write
          zh_Hans: 描述你想要创作的内容
        form: llm
      - name: enable_iteration
        type: boolean
        required: false
        default: true
        label:
          en_US: Enable Iteration
          zh_Hans: 启用迭代优化
        human_description:
          en_US: Use multi-agent iterative optimization
          zh_Hans: 使用多智能体迭代优化
        form: form
    returns:
      - name: text
        type: string
        label:
          en_US: Generated Text
          zh_Hans: 生成文本
      - name: persona_prompt
        type: string
        label:
          en_US: Persona Prompt
          zh_Hans: 分身提示词
      - name: style_profile
        type: string
        label:
          en_US: Style Profile
          zh_Hans: 风格指纹

  - name: analyze_style
    label:
      en_US: Analyze Style
      zh_Hans: 分析风格
    description:
      en_US: Analyze novel text to extract style fingerprint
      zh_Hans: 分析小说文本，提取风格指纹
    parameters:
      - name: corpus_text
        type: string
        required: true
        label:
          en_US: Novel Text
          zh_Hans: 小说文本
        human_description:
          en_US: Paste your novel text here
          zh_Hans: 在此粘贴小说文本
        form: llm
      - name: author_name
        type: string
        required: true
        label:
          en_US: Author Name
          zh_Hans: 作家名称
        human_description:
          en_US: Name of the author
          zh_Hans: 作家名称
        form: form
    returns:
      - name: style_profile
        type: string
        label:
          en_US: Style Profile
          zh_Hans: 风格指纹

  - name: compile_persona
    label:
      en_US: Compile Persona
      zh_Hans: 编译分身
    description:
      en_US: Compile style profile to persona prompt
      zh_Hans: 将风格指纹编译为分身提示词
    parameters:
      - name: style_profile
        type: string
        required: true
        label:
          en_US: Style Profile
          zh_Hans: 风格指纹
        human_description:
          en_US: JSON string of style profile
          zh_Hans: 风格指纹的JSON字符串
        form: form
      - name: author_name
        type: string
        required: true
        label:
          en_US: Author Name
          zh_Hans: 作家名称
        human_description:
          en_US: Name of the author
          zh_Hans: 作家名称
        form: form
      - name: scene_type
        type: string
        required: false
        label:
          en_US: Scene Type
          zh_Hans: 场景类型
        human_description:
          en_US: battle/dialogue/scene/emotion/momentum/transition
          zh_Hans: 战斗/对话/场景/情感/气势/转场
        form: form
    returns:
      - name: persona_prompt
        type: string
        label:
          en_US: Persona Prompt
          zh_Hans: 分身提示词

  - name: generate_with_persona
    label:
      en_US: Generate with Persona
      zh_Hans: 使用分身生成
    description:
      en_US: Generate text using author persona
      zh_Hans: 使用作家分身生成文本
    parameters:
      - name: persona_prompt
        type: string
        required: true
        label:
          en_US: Persona Prompt
          zh_Hans: 分身提示词
        human_description:
          en_US: Persona prompt string
          zh_Hans: 分身提示词字符串
        form: form
      - name: user_request
        type: string
        required: true
        label:
          en_US: Writing Request
          zh_Hans: 创作需求
        human_description:
          en_US: Describe what you want to write
          zh_Hans: 描述你想要创作的内容
        form: llm
      - name: style_profile
        type: string
        required: false
        label:
          en_US: Style Profile
          zh_Hans: 风格指纹
        human_description:
          en_US: JSON string of style profile for critic
          zh_Hans: 用于裁判评估的风格指纹JSON
        form: form
      - name: enable_iteration
        type: boolean
        required: false
        default: false
        label:
          en_US: Enable Iteration
          zh_Hans: 启用迭代优化
        human_description:
          en_US: Use multi-agent iterative optimization
          zh_Hans: 使用多智能体迭代优化
        form: form
    returns:
      - name: text
        type: string
        label:
          en_US: Generated Text
          zh_Hans: 生成文本
"""
