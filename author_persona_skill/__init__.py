"""
作家分身Skill - 主入口模块
兼容各大Agent平台（Dify、Coze等）
"""

import sys
import os

# 添加父目录到路径，以便导入核心模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .skill_main import AuthorPersonaSkill

__version__ = "1.0.0"
__all__ = ["AuthorPersonaSkill"]
