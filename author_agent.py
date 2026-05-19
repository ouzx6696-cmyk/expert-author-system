import json
from typing import Dict, Any, Tuple, Optional
from style_deconstructor import StyleDeconstructor


class StyleCritic:
    """风格裁判Agent - 独立评估生成文本的风格一致性"""

    def __init__(self, target_style_profile: Dict[str, Any]):
        self.target_stats = target_style_profile["stats"]
        self.deconstructor = StyleDeconstructor()

    def get_critic_prompt(self, generated_text: str) -> str:
        """获取风格裁判提示词"""
        target_stats_json = json.dumps(self._simplify_stats(self.target_stats), ensure_ascii=False, indent=2)

        return f"""你是一位严格的风格审查员。你的任务是将【生成文本】与【目标风格指纹】进行对比，并打分。
目标风格指纹（定量）：
{target_stats_json}

生成文本：
{generated_text}

评估项：
1. 句子长度分布相似度：计算生成文本与目标的平均句长、短句率的偏差，换算为1-10分
2. 功能词占比偏差：对比功能词使用比例，换算为1-10分
3. 标点使用模式吻合度：评估主要标点（逗号、句号、破折号等）的密度吻合度，1-10分
4. 整体韵味主观评分：基于文学感觉的整体风格匹配度，1-10分

请返回JSON格式：
{{
  "scores": {{
    "sentence_length": 8,
    "func_words": 7,
    "punctuation": 9,
    "overall_feel": 8
  }},
  "total_score": 8.0,
  "major_deviations": ["功能词使用略少", "长句比例偏高"],
  "revision_advice": "增加'的、了'等功能词的使用，适当拆分长句"
}}

要求：
- total_score 是四个评分的加权平均（各25%权重）
- 评分要客观严格
- 给出具体的修改建议，最好能指向问题位置"""

    def _simplify_stats(self, stats: Dict) -> Dict:
        """简化统计信息用于提示词"""
        return {
            "avg_sentence_len": stats["syntactic"]["avg_sentence_len"],
            "short_rate": stats["syntactic"]["short_rate"],
            "func_ratio": stats["lexical"]["func_ratio"],
            "punct_density": stats["punctuation"]["density_per_kilo"]
        }

    def evaluate_quantitative(self, text: str) -> Dict[str, float]:
        """定量快速评估（本地计算）"""
        generated_stats = self.deconstructor.analyze_quantitative(text)
        target = self.target_stats

        # 计算各项偏差
        sentence_len_diff = abs(
            generated_stats["syntactic"]["avg_sentence_len"] - target["syntactic"]["avg_sentence_len"]
        )
        sentence_len_score = max(1, 10 - sentence_len_diff * 0.5)

        short_rate_diff = abs(
            generated_stats["syntactic"]["short_rate"] - target["syntactic"]["short_rate"]
        )
        short_rate_score = max(1, 10 - short_rate_diff * 0.15)

        func_ratio_diff = abs(
            generated_stats["lexical"]["func_ratio"] - target["lexical"]["func_ratio"]
        )
        func_ratio_score = max(1, 10 - func_ratio_diff * 30)

        total_score = (sentence_len_score + short_rate_score + func_ratio_score) / 3

        return {
            "sentence_length": sentence_len_score,
            "short_rate": short_rate_score,
            "func_ratio": func_ratio_score,
            "total_score": total_score
        }


class WriterAgent:
    """编剧Agent - 负责生成与修改"""

    def __init__(self, persona_prompt: str):
        self.persona_prompt = persona_prompt

    def get_writer_prompt(self, user_request: str, feedback: Optional[str] = None) -> str:
        """获取编剧Agent提示词"""
        prompt = self.persona_prompt + f"\n\n创作任务：{user_request}"

        if feedback:
            prompt += f"\n\n【风格裁判反馈】：{feedback}\n请根据以上反馈修改文本。"

        return prompt


class PolisherAgent:
    """润色Agent - 最终打磨"""

    def get_polisher_prompt(self, text: str) -> str:
        """获取润色提示词"""
        return f"""请对以下文本进行精细润色，要求：
1. 保持原有的风格和内容完全不变
2. 修正错别字和语句不通顺的地方
3. 优化语句的流畅度
4. 不要增加任何新内容，也不要改变原意

文本：
{text}"""


class AuthorPersonaAgent:
    """作家分身Agent - 完整的多Agent协作系统"""

    def __init__(self, style_profile: Dict[str, Any], persona_prompt: str):
        self.style_profile = style_profile
        self.persona_prompt = persona_prompt

        self.writer = WriterAgent(persona_prompt)
        self.critic = StyleCritic(style_profile)
        self.polisher = PolisherAgent()

        self.max_iterations = 3
        self.score_threshold = 7.5

    def generate(self, user_request: str, scene_type: str = None, enable_iteration: bool = True):
        """
        完整生成流程

        Args:
            user_request: 用户创作请求
            scene_type: 场景类型（可选）
            enable_iteration: 是否启用迭代优化
        """
        iterations = []
        current_text = None
        feedback = None

        # 第一次生成
        writer_prompt = self.writer.get_writer_prompt(user_request, feedback)
        iterations.append({
            "iteration": 0,
            "type": "draft",
            "prompt": writer_prompt
        })

        if not enable_iteration:
            return {
                "final_text": None,
                "iterations": iterations,
                "final_score": None
            }

        # 迭代循环（模拟，实际需调用LLM API）
        for i in range(1, self.max_iterations + 1):
            # 这里需要实际调用LLM生成文本
            # 为演示，先返回框架
            pass

        return {
            "final_text": None,
            "iterations": iterations,
            "final_score": None
        }

    def get_critic_evaluation_prompt(self, generated_text: str) -> str:
        """获取裁判评估提示词"""
        return self.critic.get_critic_prompt(generated_text)

    def get_polisher_prompt(self, text: str) -> str:
        """获取润色提示词"""
        return self.polisher.get_polisher_prompt(text)
