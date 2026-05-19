import json
from typing import Dict, Any


class StyleCompiler:
    """风格编译器 - 将风格指纹图谱编译为提示词"""

    def __init__(self):
        self.scene_templates = {
            "battle": """
【战斗场景强化】
- 短句爆发率必须提高30%以上
- 动词密度提升，优先使用动作性强的动词
- 减少抒情描写，增加节奏感
- 适当增加感叹号使用
""",
            "dialogue": """
【对话场景强化】
- 口语化功能词使用增加
- 省略号密度适当提高
- 减少叙述性句子，以对话为主
- 对话更符合角色性格
""",
            "scene": """
【场景描写强化】
- 增加环境细节描绘
- 增强画面感
- 适当使用长句铺陈
- 多用视觉、听觉、触觉等感官描写
""",
            "emotion": """
【情感场景强化】
- 增加心理描写
- 多用意象化表达
- 节奏适当放缓
- 增加比喻和象征
""",
            "momentum": """
【气势场景强化】
- 多用排比和短句堆叠
- 节奏紧凑有力
- 增加气势描写
- 语气助词适当减少
""",
            "transition": """
【转场场景强化】
- 自然流畅的过渡
- 多用动作或环境描写过渡
- 避免生硬的过渡词
- 保持整体节奏
"""
        }

    def compile_persona_prompt(self, style_profile: Dict[str, Any], author_name: str = "作家") -> str:
        """编译主分身提示词"""
        stats = style_profile["stats"]
        profile = style_profile["profile"]

        # 构建统计约束
        stats_constraint = self._build_stats_constraint(stats)

        # 构建叙事软约束
        narrative_constraint = self._build_narrative_constraint(profile)

        # 构建禁忌列表
        taboo_section = self._build_taboo_section(profile)

        # 组合完整提示词
        persona_prompt = f"""【身份注入】你是作家{author_name}的文学分身。你必须完全内化并严格遵循以下风格设定。

【统计约束（硬性）】
{stats_constraint}

【叙事软约束】
{narrative_constraint}

【绝对禁忌】
{taboo_section}

【执行要求】
现在，请以完全符合上述风格的方式回应以下创作任务。你的每个字都必须经受风格审查。"""

        return persona_prompt

    def _build_stats_constraint(self, stats: Dict) -> str:
        """构建统计约束部分"""
        syntactic = stats["syntactic"]
        lexical = stats["lexical"]
        punctuation = stats["punctuation"]["density_per_kilo"]

        # 提取高频功能词
        func_words_combined = "、".join([
            w for w, c in lexical["high_freq_words"][:10]
            if len(w) <= 3
        ])

        # 构建标点约束
        punct_constraints = []
        for p in ["—", "…", "；"]:
            if p in punctuation:
                punct_constraints.append(f"{p} 密度约 {punctuation[p]:.1f} 次/千字")

        constraint_text = f"""- 句子长度：均值 {syntactic['avg_sentence_len']:.1f} 字，短句(<8字)爆发率 {syntactic['short_rate']:.1f}%
- 词汇丰富度（TTR）：维持在 {lexical['ttr']:.2f} 左右
- 功能词占比：{lexical['func_ratio']:.2f}，常用词包括 {func_words_combined}
- 标点偏好：{'；'.join(punct_constraints) if punct_constraints else '保持自然标点使用'}"""

        return constraint_text

    def _build_narrative_constraint(self, profile: Dict) -> str:
        """构建叙事软约束部分"""
        constraints = []

        if "thinking_pattern" in profile:
            constraints.append(f"- 思维推进：{profile['thinking_pattern']}")
        if "sentence_rhythm" in profile:
            constraints.append(f"- 句式节奏：{profile['sentence_rhythm']}")
        if "emotional_arc" in profile:
            constraints.append(f"- 情感弧度：{profile['emotional_arc']}")
        if "author_voice" in profile:
            constraints.append(f"- 文风人格：{profile['author_voice']}")
        if "narrative_strategies" in profile:
            ns = profile["narrative_strategies"]
            if isinstance(ns, dict):
                if "opening" in ns:
                    constraints.append(f"- 开头策略：{ns['opening']}")
                if "transition" in ns:
                    constraints.append(f"- 过渡策略：{ns['transition']}")
                if "ending" in ns:
                    constraints.append(f"- 结尾策略：{ns['ending']}")
        if "rhetoric_devices" in profile:
            rhetorics = profile["rhetoric_devices"]
            if isinstance(rhetorics, list):
                rhetoric_names = [r.get("name", str(r)) for r in rhetorics[:3]]
                constraints.append(f"- 常用修辞：{'、'.join(rhetoric_names)}")

        return "\n".join(constraints)

    def _build_taboo_section(self, profile: Dict) -> str:
        """构建禁忌列表"""
        taboos = []

        # 通用AI味禁忌
        generic_taboos = [
            "总而言之", "综上所述", "值得注意的是", "由此可见",
            "也就是说", "我们可以看到", "从这个角度来看",
            "需要指出的是", "值得一提的是", "必须承认的是"
        ]
        taboos.extend(generic_taboos)

        # 从profile获取特定禁忌
        if "taboo_phrases" in profile:
            if isinstance(profile["taboo_phrases"], list):
                taboos.extend(profile["taboo_phrases"])

        # 去重
        taboos = list(set(taboos))

        taboo_text = f"""- 禁止出现以下短语：{'、'.join(taboos)}
- 禁止段落首句使用连词（"然而""此外"等）
- 禁止任何说教或总结性语句
- 禁止过于规整的三段式结构"""

        return taboo_text

    def get_scene_enhancement(self, scene_type: str) -> str:
        """获取场景强化提示词"""
        return self.scene_templates.get(scene_type, "")

    def compile_complete_prompt(self, style_profile: Dict, author_name: str, scene_type: str = None) -> str:
        """编译完整提示词（含场景强化）"""
        base_prompt = self.compile_persona_prompt(style_profile, author_name)

        if scene_type and scene_type in self.scene_templates:
            enhancement = self.get_scene_enhancement(scene_type)
            return base_prompt + "\n\n" + enhancement

        return base_prompt
