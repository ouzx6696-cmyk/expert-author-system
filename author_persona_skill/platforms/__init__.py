"""
作家分身Skill - 平台适配器
支持的平台：Dify, Coze, 自定义平台
"""

from .dify_adapter import DifySkillAdapter, DIFY_MANIFEST
from .coze_adapter import CozeSkillAdapter, COZE_MANIFEST, COZE_MANIFEST_JSON

__all__ = [
    "DifySkillAdapter",
    "DIFY_MANIFEST",
    "CozeSkillAdapter",
    "COZE_MANIFEST",
    "COZE_MANIFEST_JSON",
]
