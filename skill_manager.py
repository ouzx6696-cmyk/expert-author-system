import os
import json
import yaml
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from style_deconstructor import StyleDeconstructor
from style_compiler import StyleCompiler
from author_agent import AuthorPersonaAgent


class SkillManager:
    """Skill封装与管理系统"""

    def __init__(self, base_dir: str = "skills"):
        """
        初始化Skill管理器
        
        Args:
            base_dir: Skill包存储目录
        """
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        self.deconstructor = StyleDeconstructor()
        self.compiler = StyleCompiler()

    async def create_skill_async(self, author_name: str, corpus_text: str, 
                               source: str = "unknown", llm_client: Any = None) -> str:
        """
        从语料创建一个新的作家Skill包（异步版本，支持真实LLM分析）

        Args:
            author_name: 作家名称
            corpus_text: 训练语料
            source: 语料来源
            llm_client: LLM客户端（可选，用于定性分析）

        Returns:
            Skill包路径
        """
        # 生成Skill包目录名
        safe_author_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_author_name = safe_author_name or "unknown_author"
        skill_dir = os.path.join(self.base_dir, f"skill_{safe_author_name.replace(' ', '_')}")

        if os.path.exists(skill_dir):
            raise ValueError(f"Skill包已存在: {skill_dir}")

        os.makedirs(skill_dir, exist_ok=True)
        os.makedirs(os.path.join(skill_dir, "scene_enhancements"), exist_ok=True)

        # 1. 定量分析
        quantitative = self.deconstructor.analyze_quantitative(corpus_text)

        # 2. 定性分析
        if llm_client:
            try:
                qualitative = await self.deconstructor.analyze_qualitative(corpus_text, llm_client)
            except Exception as e:
                print(f"LLM定性分析失败，使用模拟数据: {e}")
                qualitative = self._build_mock_qualitative(author_name)
        else:
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

    def create_skill(self, author_name: str, corpus_text: str, source: str = "unknown") -> str:
        """
        从语料创建一个新的作家Skill包（同步版本）

        Args:
            author_name: 作家名称
            corpus_text: 训练语料
            source: 语料来源

        Returns:
            Skill包路径
        """
        # 生成Skill包目录名
        safe_author_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_author_name = safe_author_name or "unknown_author"
        skill_dir = os.path.join(self.base_dir, f"skill_{safe_author_name.replace(' ', '_')}")

        if os.path.exists(skill_dir):
            raise ValueError(f"Skill包已存在: {skill_dir}")

        os.makedirs(skill_dir, exist_ok=True)
        os.makedirs(os.path.join(skill_dir, "scene_enhancements"), exist_ok=True)

        # 1. 定量分析
        quantitative = self.deconstructor.analyze_quantitative(corpus_text)

        # 2. 构建模拟定性分析结果
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

    def _save_skill_files(self, skill_dir: str, style_profile: Dict, persona_prompt: str, 
                        corpus_text: str, author_name: str):
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
        """
        加载一个Skill包
        
        Args:
            skill_name: Skill包名称
            
        Returns:
            Skill数据或None
        """
        skill_dir = os.path.join(self.base_dir, skill_name)
        if not os.path.exists(skill_dir):
            return None

        try:
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
        except Exception as e:
            print(f"加载Skill包失败: {e}")
            return None

    def create_agent(self, skill_name: str, llm_client: Any = None) -> Optional[AuthorPersonaAgent]:
        """
        从Skill包创建Agent
        
        Args:
            skill_name: Skill包名称
            llm_client: LLM客户端（可选）
            
        Returns:
            AuthorPersonaAgent 实例或None
        """
        skill = self.load_skill(skill_name)
        if not skill:
            return None

        return AuthorPersonaAgent(skill["style_profile"], skill["persona_prompt"], llm_client)

    def list_skills(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的Skill包
        
        Returns:
            Skill包信息列表
        """
        if not os.path.exists(self.base_dir):
            return []

        skills = []
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            if os.path.isdir(item_path) and item.startswith("skill_"):
                meta_path = os.path.join(item_path, "metadata.yaml")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            metadata = yaml.safe_load(f)
                        skills.append({
                            "name": item,
                            "author_name": metadata.get("author_name", "Unknown"),
                            "version": metadata.get("version", "1.0"),
                            "created_at": metadata.get("created_at")
                        })
                    except Exception as e:
                        print(f"读取Skill元数据失败 {item}: {e}")
        return skills

    def delete_skill(self, skill_name: str) -> bool:
        """
        删除一个Skill包
        
        Args:
            skill_name: Skill包名称
            
        Returns:
            是否删除成功
        """
        skill_dir = os.path.join(self.base_dir, skill_name)
        if os.path.exists(skill_dir):
            try:
                shutil.rmtree(skill_dir)
                return True
            except Exception as e:
                print(f"删除Skill包失败: {e}")
                return False
        return False
        
    def export_skill(self, skill_name: str, output_path: str) -> bool:
        """
        导出Skill包为压缩文件
        
        Args:
            skill_name: Skill包名称
            output_path: 输出文件路径
            
        Returns:
            是否导出成功
        """
        skill_dir = os.path.join(self.base_dir, skill_name)
        if not os.path.exists(skill_dir):
            return False
            
        try:
            # 移除扩展名（如果有），shutil.make_archive会添加
            base_path, _ = os.path.splitext(output_path)
            shutil.make_archive(base_path, 'zip', skill_dir)
            return True
        except Exception as e:
            print(f"导出Skill包失败: {e}")
            return False
            
    def get_skill_stats(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        获取Skill包的统计信息
        
        Args:
            skill_name: Skill包名称
            
        Returns:
            统计信息或None
        """
        skill = self.load_skill(skill_name)
        if not skill:
            return None
            
        stats = skill["style_profile"]["stats"]
        return {
            "author_name": skill["metadata"]["author_name"],
            "created_at": skill["metadata"]["created_at"],
            "total_chars": skill["style_profile"]["corpus_meta"].get("total_chars", 0),
            "avg_sentence_len": stats["syntactic"]["avg_sentence_len"],
            "ttr": stats["lexical"]["ttr"],
            "func_ratio": stats["lexical"]["func_ratio"]
        }
