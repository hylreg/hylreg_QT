"""封装 subprocess 调用 git，解析 .gitmodules 与 git submodule status。"""

import configparser
import os
import re
import subprocess
from pathlib import Path

from core.models import SubmoduleInfo, SubmoduleStatus


def _parse_status_prefix(prefix: str) -> SubmoduleStatus:
    """根据 git submodule status 行首符号解析状态。"""
    if not prefix:
        return SubmoduleStatus.INITIALIZED
    if prefix == "-":
        return SubmoduleStatus.UNINITIALIZED
    if prefix == "+":
        return SubmoduleStatus.AHEAD
    if prefix == "U":
        return SubmoduleStatus.MERGE_CONFLICT
    return SubmoduleStatus.INITIALIZED


def parse_gitmodules(repo_root: str) -> list[tuple[str, str]]:
    """
    解析 .gitmodules，返回 [(path, url), ...]。
    repo_root: hub 仓库根目录。
    """
    path = Path(repo_root) / ".gitmodules"
    if not path.exists():
        return []

    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except Exception:
        return []

    result: list[tuple[str, str]] = []
    for section in parser.sections():
        if not section.startswith('submodule "'):
            continue
        # section 形如: submodule "repos/xxx"
        path_key = "path"
        url_key = "url"
        if parser.has_option(section, path_key) and parser.has_option(section, url_key):
            sub_path = parser.get(section, path_key).strip()
            url = parser.get(section, url_key).strip()
            result.append((sub_path, url))
    return result


def run_git_submodule_status(repo_root: str) -> tuple[str, str, int]:
    """
    在 repo_root 下执行 git submodule status。
    返回 (stdout, stderr, returncode)。
    """
    try:
        proc = subprocess.run(
            ["git", "submodule", "status"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (
            proc.stdout or "",
            proc.stderr or "",
            proc.returncode or 0,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        return "", str(e), -1


def parse_submodule_status(stdout: str) -> dict[str, tuple[str, str]]:
    """
    解析 git submodule status 的 stdout。
    每行格式: [ -+|U ] <commit> <path> [ (description) ]
    返回: path -> (commit_hash, prefix)
    """
    result: dict[str, tuple[str, str]] = {}
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # 行首可选: 空格、-、+、U
        prefix = ""
        if line[0] in "-+U ":
            prefix = line[0] if line[0] != " " else ""
            line = line[1:].lstrip()
        parts = line.split(None, 1)
        if len(parts) < 2:
            continue
        commit, rest = parts[0], parts[1]
        # rest 可能是 "path" 或 "path (description)"
        path = rest.split("(", 1)[0].strip()
        result[path] = (commit, prefix)
    return result


def load_submodules(repo_root: str) -> list[SubmoduleInfo]:
    """
    加载子模块列表：合并 .gitmodules 与 git submodule status。
    repo_root: hub 仓库根目录。
    """
    if not repo_root or not (Path(repo_root) / ".git").exists():
        return []

    modules = parse_gitmodules(repo_root)
    stdout, _, code = run_git_submodule_status(repo_root)
    status_map = parse_submodule_status(stdout) if code == 0 else {}

    result: list[SubmoduleInfo] = []
    for path, url in modules:
        commit = ""
        prefix = ""
        status = SubmoduleStatus.UNINITIALIZED
        if path in status_map:
            commit, prefix = status_map[path]
            status = _parse_status_prefix(prefix)
        result.append(
            SubmoduleInfo(
                path=path,
                url=url,
                commit=commit,
                status=status,
                raw_prefix=prefix,
            )
        )
    return result


def run_git(
    repo_root: str,
    args: list[str],
    timeout: int = 120,
) -> tuple[str, str, int]:
    """
    在 repo_root 下执行 git <args>。
    返回 (stdout, stderr, returncode)。
    """
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return (
            proc.stdout or "",
            proc.stderr or "",
            proc.returncode or 0,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        return "", str(e), -1
