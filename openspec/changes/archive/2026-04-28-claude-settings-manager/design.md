## 上下文

用户使用 Claude Code CLI 时，`~/.claude/settings.json` 是核心配置文件，包含 API 连接信息（端点、令牌、模型映射）、功能开关和插件配置。当前只能手动编辑 JSON 文件切换配置，每次切换 API 提供商需要同步修改 5+ 个字段。

现有文件结构：
```
~/.claude/
├── settings.json          ← 主配置（env + plugins + marketplaces）
└── (无其他文件)
```

运行环境：Windows 11，Python 可用，用户使用 PyCharm。

## 目标 / 非目标

**目标：**
- 双击即可启动的桌面工具，弹出原生窗口
- 图形化编辑 `~/.claude/settings.json` 中的所有配置项
- 支持 Profile 系统：保存/加载/删除配置档，一键切换 API 提供商
- Profile 数据持久化存储在 `~/.claude/profiles/` 目录
- 修改直接写入 settings.json，用户自行重启 Claude Code

**非目标：**
- 不支持项目级 `.claude/settings.local.json` 编辑
- 不支持热加载（不自动触发 Claude Code 重启）
- 不做安装包/自动更新
- 不做云端同步
- 不做配置校验（如 API 连通性测试）

## 决策

### 决策 1：Python + pywebview 作为技术栈

**选择**：Python 后端 + pywebview 原生窗口 + 纯 HTML/CSS/JS 前端

**替代方案**：
- tkinter：零依赖但 UI 能力极弱，无法实现现代表单交互
- Electron：功能强大但体积 100MB+，杀鸡用牛刀
- 纯前端 HTML：浏览器安全模型无法直接写本地文件
- Flask + 浏览器：需额外开终端启动服务，不是双击即用

**理由**：pywebview 创建原生窗口（无地址栏），Python 端通过 `js_api` 暴露文件读写方法给前端，启动方式为 `.pyw` 文件双击或 PyInstaller 打包为 `.exe`。前端使用纯 HTML/CSS/JS 无需构建工具，保持零配置。

### 决策 2：Profile 存储格式

**选择**：每个 Profile 一个 JSON 文件，存放在 `~/.claude/profiles/` 目录

**格式**：
```json
{
  "name": "火山引擎 ARK",
  "env": {
    "ANTHROPIC_BASE_URL": "...",
    "ANTHROPIC_AUTH_TOKEN": "...",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "...",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "...",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "..."
  }
}
```

**替代方案**：
- 单个 profiles.json 存储所有 Profile：文件过大时不便管理，无并发安全
- 嵌入到 settings.json 中：污染主配置文件

**理由**：单文件 per Profile 简单直观，易于手动备份/删除，文件名即标识。Profile 只保存 `env` 中的连接配置（端点+令牌+模型），不保存偏好开关——开关跨 Profile 不变。

### 决策 3：前后端通信方式

**选择**：pywebview 的 `js_api` 机制

**替代方案**：
- 本地 HTTP API（Flask）：多一层网络，增加复杂度
- WebSocket：过度工程

**理由**：pywebview 的 `js_api` 允许前端 JS 直接调用 Python 对象的方法，自动处理序列化，无需额外服务层。

### 决策 4：UI 布局

**选择**：单页面三区布局

```
┌──────────────────────────────────────────┐
│  工具栏: [Profile 下拉] [保存] [管理]     │
├──────────────────────────────────────────┤
│                                          │
│  ┌─ 连接配置 ─────────────────────────┐  │
│  │  Base URL / Token / 三个模型       │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌─ 偏好开关 ─────────────────────────┐  │
│  │  遥测 / 错误上报 / 非必要流量       │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌─ 插件与市场 ───────────────────────┐  │
│  │  插件开关 / 市场源列表             │  │
│  └────────────────────────────────────┘  │
│                                          │
└──────────────────────────────────────────┘
```

**替代方案**：多标签页——信息量不大，单页足够，减少导航。

### 决策 5：项目文件结构

```
ClaudeConfig/
├── main.pyw              ← 入口（.pyw 无控制台窗口）
├── app/
│   ├── __init__.py
│   ├── api.py            ← pywebview js_api 暴露的类
│   ├── settings.py       ← settings.json 读写逻辑
│   └── profiles.py       ← Profile 管理逻辑
├── ui/
│   ├── index.html        ← 主页面
│   ├── style.css         ← 样式
│   └── app.js            ← 前端交互逻辑
└── requirements.txt      ← 依赖: pywebview
```

## 风险 / 权衡

- **[风险] pywebview 在 Windows 上依赖 WebView2 运行时** → Windows 11 已预装 Edge WebView2，风险极低。Windows 10 用户可能需手动安装。
- **[风险] 多实例同时运行可能造成文件写入冲突** → 启动时检查已有实例，使用文件锁防止并发写入。
- **[权衡] Profile 只保存 env 连接配置，不保存偏好开关** → 简化 Profile 语义，偏好开关视为全局设置。如后续需求变化可扩展。
- **[风险] settings.json 格式变化导致解析失败** → 读取时做健壮性处理，未知字段原样保留，写入时只修改已知字段。
