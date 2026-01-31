# hylreg_hub_manager

基于 Qt 的桌面应用，用于 [hylreg_hub](https://github.com/.../hylreg_hub) 式 Git Submodule 中心仓库的管理与可视化。  
本仓库为 **demo** 工作区下的子项目，路径：`demo/hylreg_hub_manager`。

## 环境

- Python 3.12+
- uv 管理依赖

## 安装与运行

请在**本目录**下执行：

```bash
cd demo/hylreg_hub_manager   # 若在仓库根目录
uv sync
uv run python main.py
# 或
uv run hylreg_hub_manager
```

## 功能

- 打开本地 hub 仓库根目录
- 查看子模块列表（路径、URL、Commit、状态）
- 添加 / 初始化 / 更新到记录版本 / 更新到远端 / 删除子模块
- 底部输出面板显示 git 命令及结果

详见 [docs/技术设计文档.md](docs/技术设计文档.md)。
