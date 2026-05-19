import re
import json
import jieba
import numpy as np
from collections import Counter
from typing import Dict, Any, List, Optional


class StyleDeconstructor:
    """深度风格解构器 - 定量与定性双通道分析"""

    def __init__(self):
        self.chinese_func_words = [
            "的", "了", "在", "是", "有", "和", "就", "都", "而", "及",
            "与", "之", "或", "但", "然而", "因此", "所以", "却", "也", "都",
            "忽然", "突然", "缓缓", "慢慢", "轻轻", "渐渐", "终于", "最终"
        ]

    def analyze_quantitative(self, text: str) -> Dict[str, Any]:
        """定量通道：计量风格学分析"""
        if not text or len(text.strip()) == 0:
            raise ValueError("输入文本不能为空")

        if not isinstance(text, str):
            raise TypeError("输入必须是字符串类型")

        sentences = self._split_sentences(text)
        words = list(jieba.cut(text))
        paragraphs = [p for p in text.split('\n') if p.strip()]

        # 词汇层分析
        word_counts = Counter(words)
        total_words = len(words)
        unique_words = len(word_counts)
        ttr = unique_words / max(total_words, 1)

        # 功能词统计
        func_word_count = sum(word_counts.get(w, 0) for w in self.chinese_func_words)
        func_ratio = func_word_count / max(total_words, 1)

        # 高频特色词（TF-IDF风格筛选）
        high_freq_words = sorted(word_counts.items(), key=lambda x: -x[1])[:50]

        # 句法层分析
        sentence_lengths = [len(s) for s in sentences] if sentences else [0]
        avg_sentence_len = float(np.mean(sentence_lengths)) if sentences else 0.0
        std_sentence_len = float(np.std(sentence_lengths)) if sentences else 0.0
        median_sentence_len = float(np.median(sentence_lengths)) if sentences else 0.0

        short_sentences = [s for s in sentence_lengths if s < 8]
        long_sentences = [s for s in sentence_lengths if s > 30]
        short_rate = len(short_sentences) / max(len(sentences), 1) * 100
        long_rate = len(long_sentences) / max(len(sentences), 1) * 100

        # 标点层分析
        punctuation_counts = self._count_punctuation(text)
        total_chars = len(text)
        punct_density = {
            k: float((v / max(total_chars, 1)) * 1000)
            for k, v in punctuation_counts.items()
        }

        # 段落层分析
        avg_paragraph_len = float(np.mean([len(p) for p in paragraphs])) if paragraphs else 0.0
        dialogue_count = self._count_dialogue(text)
        dialogue_ratio = dialogue_count / max(len(sentences), 1)

        return {
            "lexical": {
                "total_words": total_words,
                "unique_words": unique_words,
                "ttr": float(ttr),
                "func_word_count": func_word_count,
                "func_ratio": float(func_ratio),
                "high_freq_words": high_freq_words
            },
            "syntactic": {
                "total_sentences": len(sentences),
                "avg_sentence_len": avg_sentence_len,
                "std_sentence_len": std_sentence_len,
                "median_sentence_len": median_sentence_len,
                "short_rate": float(short_rate),
                "long_rate": float(long_rate)
            },
            "punctuation": {
                "counts": punctuation_counts,
                "density_per_kilo": punct_density
            },
            "paragraph": {
                "total_paragraphs": len(paragraphs),
                "avg_paragraph_len": avg_paragraph_len,
                "dialogue_count": dialogue_count,
                "dialogue_ratio": float(dialogue_ratio)
            }
        }

    def _split_sentences(self, text: str) -> List[str]:
        """按中文标点分割句子"""
        separators = r'[。！？!?]'
        sentences = re.split(separators, text)
        return [s.strip() for s in sentences if s.strip()]

    def _count_punctuation(self, text: str) -> Dict[str, int]:
        """统计标点符号使用"""
        punct_pattern = r'[，。！？；：""''（）【】《》、—…!?;:""\'\'()\[\]<>]'
        puncts = re.findall(punct_pattern, text)
        return dict(Counter(puncts))

    def _count_dialogue(self, text: str) -> int:
        """统计对话数量"""
        dialogue_pattern = r'["“][^"”]*["”]'
        dialogues = re.findall(dialogue_pattern, text)
        return len(dialogues)

    def get_qualitative_prompt(self) -> str:
        """获取定性分析提示词模板"""
        return """你是一位资深文学风格分析师。请仔细阅读以下小说片段，并从下列维度剖析作者的独特风格。
请务必以JSON格式返回结果，不要添加任何额外解释。

文本：
{corpus}

分析维度：
1. author_voice：用一句话概括作者的文风人格。
2. thinking_pattern：思维推进方式（如线性演绎、跳跃拼贴、意识流等）。
3. sentence_rhythm：句式节奏特征（长句铺陈/短句爆发/长短交替等）。
4. lexical_fingerprint：列出至少8个标志性高频词或短语。
5. rhetoric_devices：使用频率最高的3-5种修辞手法，并附简短举例。
6. narrative_strategies：开头、过渡、结尾的常用策略。
7. emotional_arc：常见情感弧度（如"平静→冲突→净化"等）。
8. taboo_phrases：基于文本风格，绝对不能出现的AI味短语（如"总而言之""值得注意的是"）。

输出JSON示例：
{
  "author_voice": "冷峻精准，擅长用工业比喻解构人性",
  "thinking_pattern": "先堆叠细节，再突然给出一句哲学总结",
  "sentence_rhythm": "短句爆发为主，偶尔插入长句营造氛围",
  "lexical_fingerprint": ["铁", "冷", "齿轮", "锈", "烟", "暗", "沉默", "响"],
  "rhetoric_devices": [
    {"name": "比喻", "example": "像生锈的齿轮"},
    {"name": "拟人", "example": "风在低语"}
  ],
  "narrative_strategies": {
    "opening": "从环境细节切入",
    "transition": "用动作代替过渡词",
    "ending": "留白式结尾"
  },
  "emotional_arc": "压抑→爆发→归于平静",
  "taboo_phrases": ["总而言之", "综上所述", "值得注意的是", "由此可见"]
}"""

    def merge_style_profile(self, quantitative: Dict, qualitative: Dict) -> Dict:
        """合并定量与定性分析，生成完整风格指纹"""
        return {
            "version": "1.0",
            "stats": quantitative,
            "profile": qualitative,
            "corpus_meta": {
                "timestamp": None,
                "total_chars": None,
                "source": None
            }
        }

    async def analyze_qualitative(self, text: str, llm_client: Any) -> Dict[str, Any]:
        """
        定性分析（需要LLM支持）
        
        Args:
            text: 分析文本
            llm_client: LLM客户端实例
            
        Returns:
            定性分析结果字典
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("输入文本不能为空")
            
        prompt = self.get_qualitative_prompt().format(corpus=text[:10000])
        system_prompt = "你是一位资深文学风格分析师。"
        
        try:
            result = await llm_client.chat_completion_json(
                system_prompt=system_prompt,
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=2000
            )
            return result
        except Exception as e:
            raise RuntimeError(f"定性分析失败: {str(e)}")
