#!/usr/bin/env python3
"""
专家级作者系统 - 完整示例
演示如何从语料创建Skill包、加载Skill包、使用Agent生成文本
"""

import json
from skill_manager import SkillManager
from style_deconstructor import StyleDeconstructor
from style_compiler import StyleCompiler
from author_agent import AuthorPersonaAgent, StyleCritic


def demo_create_skill():
    """演示：从语料创建Skill包"""
    print("=" * 60)
    print("步骤1：从语料创建Skill包")
    print("=" * 60)

    # 示例语料（实际项目中应从文件读取真实小说文本）
    sample_corpus = """
    夜色如墨，月光透过树叶的缝隙洒在青石板路上，斑驳陆离。
    她静静地站在古树下，手中握着那柄冰凉的青铜古剑，指节因为用力而泛白。
    风轻轻吹过，撩起她的衣角，也吹来了远方若有若无的笛声。
    "你来了。"一个低沉的声音从树后传来。
    她没有回头，只是微微颔首，"我知道你会来。"
    树影婆娑，那个身影缓缓走出，月光照亮了他坚毅的脸庞。
    "这一天，我等了很久。"他的声音里带着一丝沧桑。
    她终于转过身，四目相对的瞬间，时间仿佛静止了。
    是的，这一天，他们都等了很久。
    远处的山峦在夜色中若隐若现，像是巨兽的脊背。
    山下的小镇已经亮起了灯火，星星点点，温暖而遥远。
    而他们，站在命运的十字路口，前路未知。
    但他们知道，无论前方是什么，他们都会一起面对。
    因为有些东西，比生命更重要。
    比如信仰，比如承诺，比如……爱情。
    夜风渐凉，她握紧了手中的剑，他也握紧了腰间的刀。
    一场对决，即将开始。
    或者，一场新的旅程。
    谁知道呢？
    命运这种东西，从来都不会按照剧本走。
    但这，不正是它最迷人的地方吗？
    """

    manager = SkillManager()

    try:
        # 创建Skill包
        skill_dir = manager.create_skill(
            author_name="示例作家",
            corpus_text=sample_corpus,
            source="示例语料"
        )
        print(f"✓ Skill包创建成功！位置：{skill_dir}")

        # 列出所有Skill包
        skills = manager.list_skills()
        print(f"\n当前可用Skill包：")
        for skill in skills:
            print(f"  - {skill['name']} ({skill['author_name']}, v{skill['version']})")

        return skills[0]['name'] if skills else None

    except Exception as e:
        print(f"✗ 创建Skill包失败：{e}")
        return None


def demo_load_and_analyze(skill_name):
    """演示：加载Skill包并分析"""
    print("\n" + "=" * 60)
    print("步骤2：加载Skill包并分析风格")
    print("=" * 60)

    manager = SkillManager()
    skill = manager.load_skill(skill_name)

    if not skill:
        print("✗ 加载Skill包失败")
        return None

    print(f"✓ Skill包加载成功！")
    print(f"  作家名称：{skill['metadata']['author_name']}")
    print(f"  版本：{skill['metadata']['version']}")
    print(f"  创建时间：{skill['metadata']['created_at']}")

    # 显示量化指标（词汇层、句法层等）
    stats = skill['style_profile']['stats']
    print(f"\n量化风格指标：")
    print(f"  词汇层 - 功能词占比：{stats['lexical']['func_ratio']:.2%}")
    print(f"  词汇层 - 类符/形符比(TTR)：{stats['lexical']['ttr']:.2f}")
    print(f"  句法层 - 平均句子长度：{stats['syntactic']['avg_sentence_len']:.1f}字")
    print(f"  句法层 - 短句爆发率：{stats['syntactic']['short_rate']:.1f}%")

    # 显示定性描述
    profile = skill['style_profile']['profile']
    print(f"\n8维度文学风格分析：")
    print(f"  作者声音：{profile['author_voice']}")
    print(f"  思维模式：{profile['thinking_pattern']}")
    print(f"  句子节奏：{profile['sentence_rhythm']}")

    return skill


def demo_compile_prompt(skill):
    """演示：编译提示词"""
    print("\n" + "=" * 60)
    print("步骤3：编译作家分身提示词")
    print("=" * 60)

    compiler = StyleCompiler()

    # 编译主提示词
    persona_prompt = compiler.compile_persona_prompt(
        skill['style_profile'],
        skill['metadata']['author_name']
    )

    print(f"✓ 分身提示词编译成功！（前500字符）：")
    print("-" * 60)
    print(persona_prompt[:500] + "..." if len(persona_prompt) > 500 else persona_prompt)
    print("-" * 60)

    # 展示场景强化提示词
    print(f"\n场景强化模块：")
    for scene_type in ['battle', 'dialogue', 'scene']:
        enhancement = compiler.get_scene_enhancement(scene_type)
        print(f"  - {scene_type}: {enhancement[:50]}...")

    return persona_prompt


def demo_agent_workflow(skill):
    """演示：作家分身Agent工作流"""
    print("\n" + "=" * 60)
    print("步骤4：作家分身Agent工作流")
    print("=" * 60)

    # 创建Agent
    agent = AuthorPersonaAgent(skill['style_profile'], skill['persona_prompt'])

    # 用户创作请求
    user_request = "写一段古城相遇的场景，带点悬疑氛围"

    print(f"用户请求：{user_request}")
    print(f"\nAgents准备就绪：")
    print(f"  - 编剧Agent：已加载分身提示词")
    print(f"  - 风格裁判Agent：已加载目标风格指纹")
    print(f"  - 润色Agent：已就绪")
    print(f"\n迭代参数：")
    print(f"  - 最大迭代次数：{agent.max_iterations}")
    print(f"  - 评分阈值：{agent.score_threshold}/10")

    # 获取各Agent的提示词模板
    print(f"\n--- 编剧Agent提示词示例 ---")
    writer_prompt = agent.writer.get_writer_prompt(user_request)
    print(writer_prompt[:300] + "..." if len(writer_prompt) > 300 else writer_prompt)

    print(f"\n--- 风格裁判Agent提示词（需要生成文本） ---")
    print("（需要先生成文本，然后裁判进行评估）")

    # 演示本地评估功能
    print(f"\n--- 本地定量评估功能演示 ---")
    sample_generated_text = """
    古城的青石板路在月光下泛着冷光，她独自走在这条古老的街道上。
    两边的店铺都已打烊，只有偶尔传来的更鼓声打破夜的寂静。
    突然，一个身影从拐角处闪过，她下意识地握紧了手中的香囊。
    """

    critic = StyleCritic(skill['style_profile'])
    evaluation = critic.evaluate_quantitative(sample_generated_text)
    print(f"样本文本评分：")
    print(f"  句子长度评分：{evaluation['sentence_length']:.1f}/10")
    print(f"  短句率评分：{evaluation['short_rate']:.1f}/10")
    print(f"  功能词占比评分：{evaluation['func_ratio']:.1f}/10")
    print(f"  总分：{evaluation['total_score']:.1f}/10")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("专家级作者系统 - 完整演示")
    print("=" * 60)

    # 步骤1：创建Skill包
    skill_name = demo_create_skill()
    if not skill_name:
        return

    # 步骤2：加载并分析
    skill = demo_load_and_analyze(skill_name)
    if not skill:
        return

    # 步骤3：编译提示词
    demo_compile_prompt(skill)

    # 步骤4：Agent工作流
    demo_agent_workflow(skill)

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n下一步：")
    print("  1. 准备真实的小说训练语料")
    print("  2. 集成OpenAI/DeepSeek等大模型API")
    print("  3. 完善定性分析功能")
    print("  4. 开发Web UI界面")


if __name__ == "__main__":
    main()
