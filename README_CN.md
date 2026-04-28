[English](README.md) | [中文](README_CN.md)

# Claude Settings Manager

<p align="center">
  <strong>一个本地桌面工具，用于管理 Claude Code 配置，支持 Profile 切换</strong>
</p>

---

轻量级桌面应用，基于 Python + pywebview 构建，提供图形界面编辑 `~/.claude/settings.json`。支持将常用 API 配置保存为 Profile，一键切换。

## 功能特性

- **可视化配置编辑** — 通过表单 UI 编辑所有 settings.json 字段，无需手动改 JSON
- **Profile 系统** — 将常用 API 配置保存为命名档，一键切换 API 提供商
- **当前配置** — 始终可查看和回退到当前生效的配置
- **令牌掩码** — Auth Token 默认掩码显示，点击切换明文
- **原子写入** — 通过临时文件 + 重命名写入，防止写入失败时文件损坏
- **保留未知字段** — settings.json 中工具未识别的字段原样保留
- **单实例运行** — 防止多实例同时运行导致文件冲突
- **浅色主题** — 简洁中文界面，技术字段名保持英文

## 技术栈

| 层 | 技术 |
|---|------|
| 后端 | Python 3.12 |
| 桌面窗口 | pywebview (WebView2) |
| 前端 | 纯 HTML / CSS / JS |
| 测试 | pytest (TDD) |
| 打包 | PyInstaller |
| 依赖管理 | uv |

## 项目结构

```
ClaudeConfig/
├── main.pyw              ← 入口（双击启动）
├── app/
│   ├── api.py            ← pywebview js_api 桥接
│   ├── settings.py       ← settings.json 读写
│   └── profiles.py       ← Profile 增删改查
├── ui/
│   ├── index.html        ← 主页面
│   ├── style.css         ← 浅色主题
│   ├── app.js            ← 前端逻辑
│   └── icon.ico          ← 应用图标
├── tests/
│   ├── test_settings.py  ← 设置读写测试
│   └── test_profiles.py  ← Profile 增删改查测试
└── requirements.txt
```

## 快速开始

### 方式一：从源码运行

```bash
pip install pywebview
python main.pyw
```

### 方式二：下载可执行文件

从 [Releases](../../releases) 下载 `ClaudeSettingsManager-v1.0.2.exe`，双击运行。

> **注意：** 需要 Windows 10+ 及 WebView2 运行时（Windows 11 已预装）。

### 从源码打包

```bash
uv venv .venv
uv pip install --python .venv/Scripts/python.exe pywebview pyinstaller

.venv/Scripts/python -m PyInstaller --noconfirm --noconsole --onefile \
  --name "ClaudeSettingsManager" --icon "ui/icon.ico" --add-data "ui;ui" main.pyw
```

## 使用方法

1. 启动应用 — 自动加载当前 settings.json 的值
2. 编辑连接配置（Base URL、Token、模型）和偏好开关
3. 点击 **确认生效** 保存到 settings.json
4. 将常用配置保存为 **Profile** 以便一键切换
5. 重启 Claude Code 使配置生效

## 开发过程

本项目采用结构化的 AI 辅助工作流，结合了多种方法论：

### 使用 OpenSpec 进行需求探索

使用 [OpenSpec](https://github.com/anthropics/openspec) 管理变更生命周期：

1. **探索**（`/opsx:explore`）— 识别核心问题：手动编辑 JSON 切换 API 提供商容易出错。探索 Profile 概念作为解决方案。
2. **提案**（`/opsx:propose`）— 创建正式提案，定义两个能力：`settings-editor` 和 `profile-manager`。
3. **设计**（`design.md`）— 做出关键决策：Python + pywebview、文件式 Profile、js_api 通信、浅色主题 UI。
4. **任务**（`tasks.md`）— 将实现拆分为 10 个可追踪的 TDD 任务。

### 使用 Superpowers 头脑风暴补充细节

使用 **Superpowers 头脑风暴技能** 在实现前细化设计：

- **视觉伴侣** — 在浏览器中渲染 UI 模型，验证布局和配色方案
- **Profile 加载行为** — 明确选择 Profile 后是立即写入还是仅填充表单（决定：填充表单 + 手动保存）
- **UI 决策** — 浅色主题而非暗色、中文界面+英文字段名、白字红底删除按钮

### TDD 模式开发

后端模块采用测试驱动开发：

1. **编写失败测试** → 确认失败 → **编写最小实现** → 确认通过 → **提交**
2. `test_settings.py`：9 个测试覆盖读写、未知字段保留、原子写入、错误处理
3. `test_profiles.py`：10 个测试覆盖 CRUD、字段过滤、重复检测、目录创建

### Subagent 驱动实现

使用 **Superpowers subagent-driven-development** 技能执行实现计划：

- 每个任务派发给独立子代理，附带完整上下文
- 后端任务（settings、profiles）以 TDD 方式运行 pytest 验证
- 前端任务（HTML、CSS、JS）并行执行提高效率
- 集成测试验证完整流程

### Bug 修复与迭代

| 问题 | 根因 | 修复 |
|------|------|------|
| `os.kill(pid, 0)` 在 Windows 上崩溃 | Signal 0 在 Windows 不支持 | 先改用 `ctypes.OpenProcess`，最终改用 `msvcrt.locking` 文件锁 |
| 崩溃后残留锁文件 | PID 检测不可靠（PID 复用导致误判） | 替换为 `msvcrt.locking` 排他文件锁（进程退出自动释放） |
| Profile 下拉框重复点击已选项不生效 | `<select>` 的 change 事件仅在值变化时触发 | 添加"当前配置"选项，实时从文件读取值 |

## 许可证

MIT
