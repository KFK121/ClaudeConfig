## 为什么

每次切换 Claude Code 的 API 端点、认证令牌或模型映射时，都需要手动编辑 `~/.claude/settings.json`，操作繁琐且容易出错。用户频繁在多个 API 提供商（火山引擎 ARK、Anthropic 官方、DeepSeek 等）之间切换，每次涉及 5+ 个字段的同步修改。需要一个本地桌面工具，双击启动即可通过图形界面快速切换和编辑配置。

## 变更内容

- **新增**：基于 Python + pywebview 的本地桌面配置管理工具
  - 双击启动弹出原生窗口，内嵌 HTML 页面作为 UI
  - 读取并写入 `~/.claude/settings.json`
  - 支持编辑 `env` 中的所有字段（API 端点、令牌、模型、超时、开关）
  - **新增** Profile 系统：将一组完整的 `env` 配置存为命名档，一键加载切换
  - Profile 数据存储在 `~/.claude/profiles/` 目录下
  - 支持编辑 `enabledPlugins` 开关和 `extraKnownMarketplaces`
  - 修改后直接写入文件，用户自行重启 Claude Code 生效

## 功能 (Capabilities)

### 新增功能
- `settings-editor`: 编辑 `~/.claude/settings.json` 的图形界面，包括 env 字段编辑（连接配置 + 偏好开关）、插件开关、市场源管理
- `profile-manager`: Profile 的创建、保存、加载、删除功能，实现配置档一键切换

### 修改功能

（无现有功能被修改）

## 影响

- 新增 Python 依赖：`pywebview`
- 读写文件：`~/.claude/settings.json`、`~/.claude/profiles/*.json`
- 项目结构：新增 Python 应用入口文件、前端 HTML/CSS/JS 资源
