# 📚 专家级作者系统 - Author Persona System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

基于大语言模型的提示词工程与Agent架构，构建可复用、高保真的作家风格Skill系统，支持在Dify、Coze等主流Agent平台上直接安装使用！

## ✨ 特性

- 🎯 **深度风格解构** - 定量+定性双通道分析，提取完整风格指纹
- 🤖 **作家分身生成** - 将风格编译为LLM可用的提示词
- ⚙️ **多Agent协作** - 编剧+裁判+润色三Agent协同工作
- 🔄 **迭代优化** - 最多3轮迭代，确保风格相似度
- 🔌 **跨平台兼容** - Dify、Coze等主流Agent平台支持
- 📦 **可复用Skill包** - 一键导出，任意平台安装使用

## 🚀 快速开始

### 方式1：使用Agent平台Skill包（推荐）

直接使用 `author_persona_skill` 目录作为Skill包在Dify或Coze上安装！

```python
# 在Dify平台使用
from author_persona_skill.platforms import DifySkillAdapter
adapter = DifySkillAdapter()
result = adapter.run({
    "action": "complete_workflow",
    "corpus_text": "你的小说语料...",
    "author_name": "作家名称",
    "user_request": "创作需求"
})
```

### 方式2：使用核心模块

```bash
# 安装依赖
pip install -r requirements.txt

# 运行示例
python example.py
```

## 📁 项目结构

```
expert-author-system/
├── 📚 核心模块
│   ├── style_deconstructor.py      # 深度风格解构器
│   ├── style_compiler.py           # 风格编译器
│   ├── author_agent.py             # 多Agent协作系统
│   ├── skill_manager.py            # Skill管理系统
│   └── llm_integration.py          # LLM集成模块
│
├── 📦 Agent平台Skill包（可直接安装使用）
│   └── author_persona_skill/
│       ├── __init__.py
│       ├── skill_main.py           # Skill核心实现
│       ├── api.py                  # 统一API
│       ├── manifest.yaml           # Skill配置
│       ├── README_SKILL.md
│       ├── platforms/              # 平台适配器
│       │   ├── dify_adapter.py     # Dify平台支持
│       │   └── coze_adapter.py     # Coze平台支持
│       └── examples/
│
├── 📖 文档
│   ├── README.md                   # 本文档
│   ├── 使用指南.md                 # 完整使用指南
│   └── example.py                  # 示例代码
│
└── ⚙️ 配置
    ├── requirements.txt
    ├── .env.example
    └── .gitignore
```

## 🎯 核心功能

### 1. 深度风格解构器

- **定量分析**：功能词占比、TTR、句子长度统计、标点密度等
- **定性分析**：作者声音、思维模式、修辞手法、叙事策略等8个维度

### 2. 风格编译器

- 编译完整的作家分身提示词
- 6大场景强化模块（战斗/对话/场景/情感/气势/转场）
- 硬性约束 + 软性约束 + 禁忌短语

### 3. 多Agent协作系统

- **编剧Agent** - 根据风格生成初稿
- **风格裁判Agent** - 评估风格吻合度
- **润色Agent** - 最终打磨优化
- 最多3轮迭代优化

## 🌐 支持的平台

| 平台 | 状态 | 适配器文件 |
|------|------|-----------|
| Dify | ✅ 支持 | `platforms/dify_adapter.py` |
| Coze | ✅ 支持 | `platforms/coze_adapter.py` |
| 自定义平台 | ✅ 支持 | 使用统一API |

## 📊 使用示例

### 完整工作流

```python
from author_persona_skill import AuthorPersonaSkill

# 创建Skill实例
skill = AuthorPersonaSkill()

# 一键完成：从语料到生成
result = skill.complete_workflow(
    corpus_text="夜色如墨，月光透过...",  # 你的小说语料
    author_name="金庸",
    user_request="写一段古城相遇的场景",
    enable_iteration=True
)

# 获取结果
generated_text = result.get("final_text")
style_profile = result.get("style_profile")
persona_prompt = result.get("persona_prompt")
```

## 📝 文档索引

- [使用指南.md](使用指南.md) - 完整使用指南
- [author_persona_skill/README_SKILL.md](author_persona_skill/README_SKILL.md) - Skill包专用文档
- [example.py](example.py) - 核心模块示例
- [author_persona_skill/examples/quick_start.py](author_persona_skill/examples/quick_start.py) - Skill包快速开始

## 🛠️ 技术栈

- **Python 3.8+**
- **jieba** - 中文分词
- **numpy** - 数值计算
- **PyYAML** - 配置文件
- **OpenAI API / DeepSeek API** - 可选，用于LLM调用

## ⚙️ 配置说明

### 环境变量（可选）

```env
# 复制 .env.example 为 .env 并填入配置
OPENAI_API_KEY=your_api_key
DEEPSEEK_API_KEY=your_api_key
```

## 📈 功能对比

| 功能 | 无LLM | 有LLM |
|------|-------|-------|
| 风格分析（定量） | ✅ | ✅ |
| 提示词编译 | ✅ | ✅ |
| 场景强化模块 | ✅ | ✅ |
| 一键生成 | ❌ | ✅ |
| 迭代优化 | ❌ | ✅ |

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**现在就开始创建你的第一个作家分身吧！** ✨
