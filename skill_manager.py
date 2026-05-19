import os
import json
import yaml
import shutil
from datetime import datetime
from typing import Dict, Any, Optional
from style_deconstructor import StyleDeconstructor
from style_compiler import StyleCompiler
from author_agent import AuthorPersonaAgent


class SkillManager:
    """Skill封装与管理系统"""

    def __init__(self, base_dir: str = "skills"):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        self.deconstructor = StyleDeconstructor()
        self.compiler = StyleCompiler()

    def create_skill(self, author_name: str, corpus_text: str, source: str = "unknown") -> str:
        """
        从语料创建一个新的作家Skill包

        Args:
            author_name: 作家名称
            corpus_text: 训练语料
            source: 语料来源

        Returns:
            Skill包路径
        """
        # 生成Skill包目录名
        safe_author_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        skill_dir = os.path.join(self.base_dir, f"skill_{safe_author_name.replace(' ', '_')}")

        if os.path.exists(skill_dir):
            raise ValueError(f"Skill包已存在: {skill_dir}")

        os.makedirs(skill_dir)
        os.makedirs(os.path.join(skill_dir, "scene_enhancements"))

        # 1. 定量分析
        quantitative = self.deconstructor.analyze_quantitative(corpus_text)

        # 2. 构建模拟定性分析结果（实际需要调用LLM）
        qualitative = self._build_mock_qualitative(author_name)

        # 3. 合并完整风格图谱
        style_profile = self.deconstructor.merge_style_profile(quantitative, qualitative)
        style_profile["corpus_meta"]["timestamp"] = datetime.now().isoformat()
        style_profile["corpus_meta"]["total_chars"] = len(corpus_text)
        style_profile["corpus_meta"]["source"] = source

        # 4. 编译提示词
        persona_prompt = self.compiler.compile_persona_prompt(style_profile, author_name)

        # 5. 保存所有文件
        self._save_skill_files(skill_dir, style_profile, persona_prompt, corpus_text, author_name)

        return skill_dir

    def _build_mock_qualitative(self, author_name: str) -> Dict[str, Any]:
        """构建模拟的定性分析结果（演示用）"""
        return {
            "author_voice": f"{author_name}的独特文风，细腻而富有感染力",
            "thinking_pattern": "线性叙事，层层递进",
            "sentence_rhythm": "长短句结合，富有节奏感",
            "lexical_fingerprint": ["常用词1", "常用词2", "常用词3", "常用词4", "常用词5", "常用词6", "常用词7", "常用词8"],
            "rhetoric_devices": [
                {"name": "比喻", "example": "示例比喻句"},
                {"name": "拟人", "example": "示例拟人句"}
            ],
            "narrative_strategies": {
                "opening": "开门见山",
                "transition": "自然过渡",
                "ending": "余味悠长"
            },
            "emotional_arc": "平静→发展→高潮→平静",
            "taboo_phrases": ["总而言之", "综上所述"]
        }

    def _save_skill_files(self, skill_dir: str, style_profile: Dict, persona_prompt: str, corpus_text: str, author_name: str):
        """保存Skill包所有文件"""
        # 保存风格指纹
        with open(os.path.join(skill_dir, "author_style.json"), "w", encoding="utf-8") as f:
            json.dump(style_profile, f, ensure_ascii=False, indent=2)

        # 保存分身提示词
        with open(os.path.join(skill_dir, "persona_prompt.txt"), "w", encoding="utf-8") as f:
            f.write(persona_prompt)

        # 保存场景强化提示词
        for scene_type, enhancement in self.compiler.scene_templates.items():
            with open(os.path.join(skill_dir, "scene_enhancements", f"{scene_type}.txt"), "w", encoding="utf-8") as f:
                f.write(enhancement.strip())

        # 保存语料样本
        with open(os.path.join(skill_dir, "corpus_samples.txt"), "w", encoding="utf-8") as f:
            f.write(corpus_text[:5000] + "..." if len(corpus_text) > 5000 else corpus_text)

        # 保存元数据
        metadata = {
            "author_name": author_name,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "source": style_profile["corpus_meta"]["source"]
        }
        with open(os.path.join(skill_dir, "metadata.yaml"), "w", encoding="utf-8") as f:
            yaml.dump(metadata, f, allow_unicode=True)

    def load_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """加载一个Skill包"""
        skill_dir = os.path.join(self.base_dir, skill_name)
        if not os.path.exists(skill_dir):
            return None

        with open(os.path.join(skill_dir, "author_style.json"), "r", encoding="utf-8") as f:
            style_profile = json.load(f)

        with open(os.path.join(skill_dir, "persona_prompt.txt"), "r", encoding="utf-8") as f:
            persona_prompt = f.read()

        with open(os.path.join(skill_dir, "metadata.yaml"), "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        return {
            "style_profile": style_profile,
            "persona_prompt": persona_prompt,
            "metadata": metadata,
            "skill_dir": skill_dir
        }

    def create_agent(self, skill_name: str) -> Optional[AuthorPersonaAgent]:
        """从Skill包创建Agent"""
        skill = self.load_skill(skill_name)
        if not skill:
            return None

        return AuthorPersonaAgent(skill["style_profile"], skill["persona_prompt"])

    def list_skills(self) -> list:
        """列出所有可用的Skill包"""
        if not os.path.exists(self.base_dir):
            return []

        skills = []
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            if os.path.isdir(item_path) and item.startswith("skill_"):
                meta_path = os.path.join(item_path, "metadata.yaml")
                if os.path.exists(meta_path):
                    with open(meta_path, "r", encoding="utf-8") as f:
                        metadata = yaml.safe_load(f)
                    skills.append({
                        "name": item,
                        "author_name": metadata.get("author_name", "Unknown"),
                        "version": metadata.get("version", "1.0"),
                        "created_at": metadata.get("created_at")
                    })
        return skills

    def delete_skill(self, skill_name: str) -> bool:
        """删除一个Skill包"""
        skill_dir = os.path.join(self.base_dir, skill_name)
        if os.path.exists(skill_dir):
            shutil.rmtree(skill_dir)
            return True
        return False
