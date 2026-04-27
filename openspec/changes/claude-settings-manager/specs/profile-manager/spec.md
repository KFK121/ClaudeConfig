## 新增需求

### 需求:Profile 存储
系统必须将每个 Profile 存储为独立的 JSON 文件，放置在 `~/.claude/profiles/` 目录下。文件名必须使用 kebab-case 格式（如 `volcengine-ark.json`）。每个 Profile 文件必须包含 `name`（显示名称）和 `env`（连接配置键值对）两个字段。

#### 场景:Profile 文件格式
- **当** 系统创建一个新 Profile
- **那么** 写入的 JSON 文件必须包含 `name` 和 `env` 字段，`env` 中仅包含连接配置（ANTHROPIC_BASE_URL、ANTHROPIC_AUTH_TOKEN、ANTHROPIC_DEFAULT_OPUS_MODEL、ANTHROPIC_DEFAULT_SONNET_MODEL、ANTHROPIC_DEFAULT_HAIKU_MODEL）

#### 场景:Profile 目录不存在
- **当** 系统首次保存 Profile 且 `~/.claude/profiles/` 目录不存在
- **那么** 系统必须自动创建该目录

### 需求:Profile 下拉选择
系统必须在 UI 顶部提供下拉选择器，列出所有已保存的 Profile。选择一个 Profile 后必须将其 `env` 连接配置加载到表单中。

#### 场景:切换 Profile
- **当** 用户从下拉框选择一个已保存的 Profile
- **那么** 系统必须将该 Profile 的 env 字段值填充到连接配置表单中，偏好开关和插件不受影响

#### 场景:无 Profile 存在
- **当** `~/.claude/profiles/` 目录为空或不存在
- **那么** 下拉框必须显示"无已保存配置"占位文本

### 需求:保存当前配置为 Profile
系统必须允许用户将当前连接配置表单中的值保存为新的 Profile。

#### 场景:保存新 Profile
- **当** 用户点击"保存为 Profile"并输入名称
- **那么** 系统必须将当前连接配置表单中的 5 个字段（BASE_URL、AUTH_TOKEN、三个 MODEL）保存为新的 Profile 文件

#### 场景:Profile 名称重复
- **当** 用户输入的 Profile 名称与已有 Profile 同名
- **那么** 系统必须提示用户确认覆盖

### 需求:更新已有 Profile
系统必须允许用户将当前连接配置覆盖更新到已有 Profile。

#### 场景:更新 Profile
- **当** 用户选择已有 Profile 后修改了表单值并点击"更新当前 Profile"
- **那么** 系统必须用当前表单值覆盖该 Profile 文件

### 需求:删除 Profile
系统必须允许用户删除已保存的 Profile。

#### 场景:删除 Profile
- **当** 用户选择一个 Profile 并点击删除
- **那么** 系统必须显示确认对话框，确认后删除对应的 Profile 文件

#### 场景:取消删除
- **当** 用户在确认对话框中点击取消
- **那么** 系统必须保留该 Profile，不做任何修改

### 需求:Profile 仅保存连接配置
Profile 必须只保存 `env` 中的连接配置字段（ANTHROPIC_BASE_URL、ANTHROPIC_AUTH_TOKEN、三个 MODEL 字段），不保存偏好开关（DISABLE_*）、超时设置（API_TIMEOUT_MS）或插件配置。

#### 场景:加载 Profile 不影响开关
- **当** 用户加载一个 Profile
- **那么** 偏好开关、超时设置、插件配置必须保持当前值不变

#### 场景:保存 Profile 不包含开关
- **当** 用户将当前配置保存为 Profile
- **那么** Profile 文件中禁止包含 DISABLE_* 和 API_TIMEOUT_MS 字段
