# hylreg Demo 工作区

本仓库为 **demo** 工作区，内含多个子项目。使用 [uv](https://docs.astral.sh/uv/) 管理依赖与工作区。

## 子项目

| 路径 | 说明 |
|------|------|
| [demo/hylreg_hub_manager](demo/hylreg_hub_manager/) | Qt 桌面应用：Git Submodule 中心仓库（hylreg hub）管理与可视化 |

## 环境

- Python 3.12+
- uv

## 使用

**推荐**：进入子项目目录后再安装与运行。

```bash
# 进入子项目
cd demo/hylreg_hub_manager

# 安装依赖并运行
uv sync
uv run python main.py
# 或
uv run hylreg_hub_manager
```

若在仓库根目录操作，可先同步工作区依赖，再指定包运行：

```bash
uv sync
uv run --package hylreg_hub_manager hylreg_hub_manager
```

各子项目详细说明见其目录下的 `README.md`。
