"""
作家分身Skill - 核心实现
提供统一的API接口，兼容各大Agent平台
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

# 导入核心模块
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from style_deconstructor import StyleDeconstructor
from style_compiler import StyleCompiler
from author_agent import AuthorPersonaAgent, StyleCritic


class AuthorPersonaSkill:
    """
    作家分身Skill主类
    提供完整的功能API
    """

    def __init__(self, llm_client=None):
        """
        初始化Skill

        Args:
            llm_client: LLM客户端实例（可选，用于完整功能）
        """
        self.deconstructor = StyleDeconstructor()
        self.compiler = StyleCompiler()
        self.llm_client = llm_client
        self.cache = {}

    def analyze_style(
        self,
        corpus_text: str,
        author_name: str
    ) -> Dict[str, Any]:
        """
        深度分析小说文本，提取作家风格指纹

        Args:
            corpus_text: 小说原文文本
            author_name: 作家名称

        Returns:
            完整的风格指纹数据
        """
        if not corpus_text or len(corpus_text.strip()) < 100:
            raise ValueError("语料文本过短，请至少提供100字以上的文本")

        # 定量分析
        quantitative = self.deconstructor.analyze_quantitative(corpus_text)

        # 定性分析（使用LLM或模拟数据）
        qualitative = self._get_qualitative_analysis(corpus_text, author_name)

        # 合并生成完整风格指纹
        style_profile = self.deconstructor.merge_style_profile(quantitative, qualitative)
        style_profile["corpus_meta"]["timestamp"] = datetime.now().isoformat()
        style_profile["corpus_meta"]["total_chars"] = len(corpus_text)
        style_profile["corpus_meta"]["source"] = "user_upload"
        style_profile["version"] = "1.0.0"
        style_profile["author_name"] = author_name

        # 缓存结果
        cache_key = f"profile_{author_name}"
        self.cache[cache_key] = style_profile

        return {
            "success": True,
            "style_profile": style_profile,
            "quantitative_summary": self._summarize_quantitative(quantitative),
            "qualitative_summary": self._summarize_qualitative(qualitative)
        }

    def _get_qualitative_analysis(
        self,
        corpus_text: str,
        author_name: str
    ) -> Dict[str, Any]:
        """
        获取定性分析结果

        Args:
            corpus_text: 语料文本
            author_name: 作家名称

        Returns:
            定性分析结果
        """
        # 如果有LLM客户端，使用LLM分析
        if self.llm_client:
            try:
                prompt = self.deconstructor.get_qualitative_prompt()
                user_prompt = prompt.format(corpus=corpus_text[:10000])  # 限制长度
                return self.llm_client.chat_completion_json(
                    system_prompt="你是一位资深文学风格分析师。",
                    user_prompt=user_prompt
                )
            except Exception as e:
                print(f"LLM分析失败，使用模拟数据: {e}")

        # 否则使用模拟数据
        return {
            "author_voice": f"{author_name}的独特文风，细腻而富有感染力",
            "thinking_pattern": "线性叙事，层层递进，注重情节发展",
            "sentence_rhythm": "长短句结合，富有节奏感和韵律美",
            "lexical_fingerprint": ["常用词1", "常用词2", "常用词3", "常用词4", "常用词5", "常用词6", "常用词7", "常用词8"],
            "rhetoric_devices": [
                {"name": "比喻", "example": "像...一样"},
                {"name": "拟人", "example": "...在低语"},
                {"name": "排比", "example": "有的...有的...有的..."}
            ],
            "narrative_strategies": {
                "opening": "从环境细节切入，营造氛围",
                "transition": "自然过渡，流畅衔接",
                "ending": "余味悠长，引人深思"
            },
            "emotional_arc": "平静→发展→高潮→平静，情感起伏有致",
            "taboo_phrases": ["总而言之", "综上所述", "值得注意的是", "由此可见", "我们可以看出"]
        }

    def _summarize_quantitative(self, quantitative: Dict) -> Dict:
        """生成定量分析摘要"""
        return {
            "avg_sentence_length": f"{quantitative['syntactic']['avg_sentence_len']:.1f}字",
            "short_sentence_rate": f"{quantitative['syntactic']['short_rate']:.1f}%",
            "function_word_ratio": f"{quantitative['lexical']['func_ratio']:.1%}",
            "vocabulary_richness": f"TTR {quantitative['lexical']['ttr']:.2f}",
            "punctuation_style": "、".join([k for k, v in quantitative['punctuation']['counts'].items() if v > 10][:5])
        }

    def _summarize_qualitative(self, qualitative: Dict) -> Dict:
        """生成定性分析摘要"""
        return {
            "author_voice": qualitative.get("author_voice", ""),
            "thinking_pattern": qualitative.get("thinking_pattern", ""),
            "sentence_rhythm": qualitative.get("sentence_rhythm", ""),
            "key_rhetoric": ", ".join([r.get("name", "") for r in qualitative.get("rhetoric_devices", [])[:3]])
        }

    def compile_persona(
        self,
        style_profile: Dict[str, Any],
        author_name: str,
        scene_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        将风格指纹编译为分身提示词

        Args:
            style_profile: 风格指纹数据
            author_name: 作家名称
            scene_type: 场景类型（可选）

        Returns:
            编译结果
        """
        # 编译主提示词
        persona_prompt = self.compiler.compile_persona_prompt(style_profile, author_name)

        result = {
            "success": True,
            "persona_prompt": persona_prompt,
            "author_name": author_name
        }

        # 如果指定了场景类型，添加场景强化
        if scene_type and scene_type in self.compiler.scene_templates:
            enhancement = self.compiler.get_scene_enhancement(scene_type)
            result["scene_enhancement"] = enhancement
            result["complete_prompt"] = persona_prompt + "\n\n" + enhancement

        # 缓存结果
        cache_key = f"persona_{author_name}"
        self.cache[cache_key] = result

        return result

    def generate_with_persona(
        self,
        persona_prompt: str,
        user_request: str,
        style_profile: Optional[Dict] = None,
        enable_iteration: bool = False,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        使用作家分身进行文本生成

        Args:
            persona_prompt: 分身提示词
            user_request: 用户创作需求
            style_profile: 风格指纹（用于裁判评估）
            enable_iteration: 是否启用迭代优化
            max_iterations: 最大迭代次数

        Returns:
            生成结果
        """
        if not self.llm_client:
            return {
                "success": True,
                "warning": "未配置LLM客户端，返回提示词模板（请配置LLM以启用完整功能）",
                "writer_prompt": persona_prompt + f"\n\n创作任务：{user_request}",
                "final_text": None
            }

        try:
            # 第一次生成
            writer = self._create_writer_agent(persona_prompt)
            draft_text = self.llm_client.chat_completion(
                system_prompt=persona_prompt,
                user_prompt=user_request,
                temperature=0.8
            )

            iterations = [{
                "iteration": 1,
                "text": draft_text,
                "type": "initial"
            }]

            final_text = draft_text
            final_score = None

            # 如果启用迭代且有风格指纹
            if enable_iteration and style_profile:
                agent = AuthorPersonaAgent(style_profile, persona_prompt)
                agent.max_iterations = max_iterations

                for i in range(2, max_iterations + 1):
                    # 裁判评估
                    critic = StyleCritic(style_profile)
                    eval_result = critic.evaluate_quantitative(draft_text)
                    score = eval_result["total_score"]

                    if score >= 7.5:
                        final_score = score
                        break

                    # 根据建议修改
                    revision_prompt = f"当前文本评分: {score}/10\n请根据风格要求修改以下文本:\n{draft_text}"
                    revised_text = self.llm_client.chat_completion(
                        system_prompt=persona_prompt,
                        user_prompt=revision_prompt,
                        temperature=0.7
                    )

                    iterations.append({
                        "iteration": i,
                        "text": revised_text,
                        "score": score,
                        "type": "revision"
                    })

                    draft_text = revised_text
                    final_text = revised_text

            return {
                "success": True,
                "final_text": final_text,
                "iterations": iterations,
                "final_score": final_score,
                "total_iterations": len(iterations)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_text": None
            }

    def _create_writer_agent(self, persona_prompt: str):
        """创建编剧Agent（简化版）"""
        class SimpleWriterAgent:
            def __init__(self, prompt):
                self.persona_prompt = prompt

        return SimpleWriterAgent(persona_prompt)

    def complete_workflow(
        self,
        corpus_text: str,
        author_name: str,
        user_request: str,
        enable_iteration: bool = True
    ) -> Dict[str, Any]:
        """
        完整工作流：从语料到生成的一站式处理

        Args:
            corpus_text: 小说原文文本
            author_name: 作家名称
            user_request: 用户创作需求
            enable_iteration: 是否启用迭代优化

        Returns:
            完整工作流结果
        """
        try:
            # 1. 分析风格
            analyze_result = self.analyze_style(corpus_text, author_name)
            if not analyze_result["success"]:
                return analyze_result

            style_profile = analyze_result["style_profile"]

            # 2. 编译分身
            compile_result = self.compile_persona(style_profile, author_name)
            if not compile_result["success"]:
                return compile_result

            persona_prompt = compile_result["persona_prompt"]

            # 3. 生成文本
            generate_result = self.generate_with_persona(
                persona_prompt=persona_prompt,
                user_request=user_request,
                style_profile=style_profile,
                enable_iteration=enable_iteration
            )

            return {
                "success": True,
                "style_profile": style_profile,
                "persona_prompt": persona_prompt,
                "final_text": generate_result.get("final_text"),
                "iterations": generate_result.get("iterations", []),
                "final_score": generate_result.get("final_score"),
                "quantitative_summary": analyze_result["quantitative_summary"],
                "qualitative_summary": analyze_result["qualitative_summary"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        return self.cache.get(key)

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
