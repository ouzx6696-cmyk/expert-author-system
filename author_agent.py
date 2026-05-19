import json
from typing import Dict, Any, Tuple, Optional, List
from style_deconstructor import StyleDeconstructor


class StyleCritic:
    """风格裁判Agent - 独立评估生成文本的风格一致性"""

    def __init__(self, target_style_profile: Dict[str, Any]):
        self.target_stats = target_style_profile["stats"]
        self.target_profile = target_style_profile.get("profile", {})
        self.deconstructor = StyleDeconstructor()

    def get_critic_prompt(self, generated_text: str) -> str:
        """获取风格裁判提示词"""
        target_stats_json = json.dumps(self._simplify_stats(self.target_stats), ensure_ascii=False, indent=2)
        
        profile_summary = self._get_profile_summary()

        return f"""你是一位严格的风格审查员。你的任务是将【生成文本】与【目标风格指纹】进行对比，并打分。

目标风格指纹（定量统计）：
{target_stats_json}

目标风格特征（定性描述）：
{profile_summary}

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

    def _get_profile_summary(self) -> str:
        """获取定性风格特征的摘要"""
        summary_parts = []
        if "author_voice" in self.target_profile:
            summary_parts.append(f"- 作者声音：{self.target_profile['author_voice']}")
        if "sentence_rhythm" in self.target_profile:
            summary_parts.append(f"- 句式节奏：{self.target_profile['sentence_rhythm']}")
        if "thinking_pattern" in self.target_profile:
            summary_parts.append(f"- 思维模式：{self.target_profile['thinking_pattern']}")
        return "\n".join(summary_parts) if summary_parts else "（无定性特征描述）"

    def _simplify_stats(self, stats: Dict) -> Dict:
        """简化统计信息用于提示词"""
        return {
            "avg_sentence_len": float(stats["syntactic"]["avg_sentence_len"]),
            "short_rate": float(stats["syntactic"]["short_rate"]),
            "func_ratio": float(stats["lexical"]["func_ratio"]),
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
        sentence_len_score = max(1.0, min(10.0, 10.0 - sentence_len_diff * 0.5))

        short_rate_diff = abs(
            generated_stats["syntactic"]["short_rate"] - target["syntactic"]["short_rate"]
        )
        short_rate_score = max(1.0, min(10.0, 10.0 - short_rate_diff * 0.15))

        func_ratio_diff = abs(
            generated_stats["lexical"]["func_ratio"] - target["lexical"]["func_ratio"]
        )
        func_ratio_score = max(1.0, min(10.0, 10.0 - func_ratio_diff * 30))

        total_score = (sentence_len_score + short_rate_score + func_ratio_score) / 3.0

        return {
            "sentence_length": float(sentence_len_score),
            "short_rate": float(short_rate_score),
            "func_ratio": float(func_ratio_score),
            "total_score": float(total_score)
        }


class WriterAgent:
    """编剧Agent - 负责生成与修改"""

    def __init__(self, persona_prompt: str):
        self.persona_prompt = persona_prompt

    def get_writer_prompt(self, user_request: str, feedback: Optional[str] = None, 
                         previous_text: Optional[str] = None, scene_type: Optional[str] = None) -> str:
        """获取编剧Agent提示词"""
        prompt = self.persona_prompt + f"\n\n创作任务：{user_request}"
        
        if scene_type:
            prompt += f"\n\n场景类型：{scene_type}（请根据场景类型调整文风）"

        if feedback and previous_text:
            prompt += f"\n\n【上次生成的文本】：\n{previous_text}\n\n【风格裁判反馈】：{feedback}\n\n请根据以上反馈修改文本，保持内容核心不变，但优化风格匹配度。"
        elif feedback:
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

    def __init__(self, style_profile: Dict[str, Any], persona_prompt: str, llm_client: Any = None):
        """
        初始化作家分身Agent
        
        Args:
            style_profile: 风格配置文件
            persona_prompt: 分身提示词
            llm_client: LLM客户端（可选，用于实际生成）
        """
        self.style_profile = style_profile
        self.persona_prompt = persona_prompt
        self.llm_client = llm_client

        self.writer = WriterAgent(persona_prompt)
        self.critic = StyleCritic(style_profile)
        self.polisher = PolisherAgent()

        self.max_iterations = 3
        self.score_threshold = 7.5

    async def generate_async(self, user_request: str, scene_type: Optional[str] = None, 
                           enable_iteration: bool = True) -> Dict[str, Any]:
        """
        完整生成流程（异步版本，需要LLM客户端）

        Args:
            user_request: 用户创作请求
            scene_type: 场景类型（可选）
            enable_iteration: 是否启用迭代优化

        Returns:
            包含生成结果的字典
        """
        if not self.llm_client:
            raise ValueError("需要设置LLM客户端才能使用生成功能")

        iterations = []
        current_text = None
        feedback = None
        final_score = None

        # 第一次生成
        writer_prompt = self.writer.get_writer_prompt(user_request, feedback, scene_type=scene_type)
        
        try:
            current_text = await self.llm_client.chat_completion_async(
                system_prompt="你是一位专业作家。",
                user_prompt=writer_prompt,
                temperature=0.8,
                max_tokens=3000
            )
            
            iterations.append({
                "iteration": 0,
                "type": "draft",
                "text": current_text,
                "prompt": writer_prompt
            })

            if enable_iteration:
                # 迭代循环
                for i in range(1, self.max_iterations + 1):
                    # 评估当前文本
                    quant_eval = self.critic.evaluate_quantitative(current_text)
                    
                    # 如果分数达标，停止迭代
                    if quant_eval["total_score"] >= self.score_threshold:
                        break
                    
                    # 使用LLM进行详细评估
                    critic_prompt = self.critic.get_critic_prompt(current_text)
                    try:
                        critic_result = await self.llm_client.chat_completion_json_async(
                            system_prompt="你是一位严格的文学风格评审。",
                            user_prompt=critic_prompt,
                            temperature=0.3,
                            max_tokens=1500
                        )
                        feedback = critic_result.get("revision_advice", "")
                        current_score = critic_result.get("total_score", quant_eval["total_score"])
                    except Exception:
                        # 如果LLM评估失败，使用本地评估
                        feedback = f"风格匹配度分数：{quant_eval['total_score']:.1f}/10，请优化风格。"
                        current_score = quant_eval["total_score"]
                    
                    # 根据反馈修改文本
                    writer_prompt = self.writer.get_writer_prompt(
                        user_request, feedback, current_text, scene_type
                    )
                    
                    revised_text = await self.llm_client.chat_completion_async(
                        system_prompt="你是一位专业作家。",
                        user_prompt=writer_prompt,
                        temperature=0.7,
                        max_tokens=3000
                    )
                    
                    iterations.append({
                        "iteration": i,
                        "type": "revision",
                        "text": revised_text,
                        "score": current_score,
                        "feedback": feedback,
                        "prompt": writer_prompt
                    })
                    
                    current_text = revised_text

            # 最终润色
            polisher_prompt = self.polisher.get_polisher_prompt(current_text)
            final_text = await self.llm_client.chat_completion_async(
                system_prompt="你是一位专业的文字编辑。",
                user_prompt=polisher_prompt,
                temperature=0.3,
                max_tokens=3000
            )
            
            # 最终评估
            final_evaluation = self.critic.evaluate_quantitative(final_text)
            final_score = final_evaluation["total_score"]
            
            return {
                "final_text": final_text,
                "iterations": iterations,
                "final_score": final_score,
                "final_evaluation": final_evaluation
            }
            
        except Exception as e:
            raise RuntimeError(f"生成过程出错: {str(e)}")

    def generate(self, user_request: str, scene_type: Optional[str] = None, 
                enable_iteration: bool = True) -> Dict[str, Any]:
        """
        完整生成流程（同步版本，返回框架，实际生成需要使用异步版本）

        Args:
            user_request: 用户创作请求
            scene_type: 场景类型（可选）
            enable_iteration: 是否启用迭代优化
        """
        iterations = []
        writer_prompt = self.writer.get_writer_prompt(user_request, scene_type=scene_type)
        iterations.append({
            "iteration": 0,
            "type": "draft",
            "prompt": writer_prompt
        })

        return {
            "final_text": None,
            "iterations": iterations,
            "final_score": None,
            "message": "请使用 generate_async() 方法进行实际生成，需要提供LLM客户端"
        }

    def get_critic_evaluation_prompt(self, generated_text: str) -> str:
        """获取裁判评估提示词"""
        return self.critic.get_critic_prompt(generated_text)

    def get_polisher_prompt(self, text: str) -> str:
        """获取润色提示词"""
        return self.polisher.get_polisher_prompt(text)
    
    def evaluate_text(self, text: str) -> Dict[str, float]:
        """评估文本的风格匹配度"""
        return self.critic.evaluate_quantitative(text)
