"""数据模型：子模块信息。"""

from dataclasses import dataclass
from enum import Enum


class SubmoduleStatus(str, Enum):
    """子模块状态（对应 git submodule status 行首符号）。"""

    UNINITIALIZED = "uninitialized"  # 未初始化（无前缀或 -）
    INITIALIZED = "initialized"  # 已初始化，与记录一致
    MODIFIED = "modified"  # 有未提交修改 (+)
    MERGE_CONFLICT = "merge_conflict"  # 合并冲突 (U)
    AHEAD = "ahead"  # 领先于记录 (+)
    DETACHED = "detached"  # 已检出但与记录不同


@dataclass
class SubmoduleInfo:
    """子模块信息。"""

    path: str
    url: str
    commit: str  # 短 hash 或空
    status: SubmoduleStatus
    raw_prefix: str = ""  # 行首符号：- + U 等，便于显示

    def status_display(self) -> str:
        """用于界面显示的状态文本。"""
        return {
            SubmoduleStatus.UNINITIALIZED: "未初始化",
            SubmoduleStatus.INITIALIZED: "已初始化",
            SubmoduleStatus.MODIFIED: "有修改",
            SubmoduleStatus.MERGE_CONFLICT: "合并冲突",
            SubmoduleStatus.AHEAD: "领先",
            SubmoduleStatus.DETACHED: "已检出",
        }.get(self.status, self.status.value)
