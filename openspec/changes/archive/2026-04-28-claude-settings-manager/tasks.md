## 1. 项目骨架

- [ ] 1.1 创建项目文件结构：main.pyw 入口、app/ 包（__init__.py、api.py、settings.py、profiles.py）、ui/ 资源（index.html、style.css、app.js）
- [ ] 1.2 创建 requirements.txt，添加 pywebview 依赖
- [ ] 1.3 实现主入口 main.pyw：创建 pywebview 窗口（800x600、标题 "Claude Settings Manager"），注册 js_api，启动事件循环

## 2. 后端：Settings 读写

- [ ] 2.1 实现 app/settings.py：读取 `~/.claude/settings.json`，解析为 Python 字典；文件不存在时返回默认结构
- [ ] 2.2 实现写入逻辑：将修改后的字典格式化写回 settings.json（2 空格缩进），保留未知字段
- [ ] 2.3 实现写入错误处理：捕获权限/IO 异常，返回错误信息

## 3. 后端：Profile 管理

- [ ] 3.1 实现 app/profiles.py：列出 `~/.claude/profiles/` 下所有 .json 文件，解析为 Profile 列表
- [ ] 3.2 实现保存 Profile：将连接配置（BASE_URL、AUTH_TOKEN、三个 MODEL）写入 `~/.claude/profiles/<kebab-name>.json`，自动创建目录
- [ ] 3.3 实现更新 Profile：覆盖已有 Profile 文件
- [ ] 3.4 实现删除 Profile：删除指定 Profile 文件

## 4. 后端：JS API 桥接

- [ ] 4.1 实现 app/api.py：定义 Api 类，使用 pywebview 的 `@expose` 装饰器暴露方法
- [ ] 4.2 暴露 `load_settings()` 方法：调用 settings.py 读取并返回完整配置
- [ ] 4.3 暴露 `save_settings(config)` 方法：调用 settings.py 写入配置
- [ ] 4.4 暴露 `list_profiles()` / `save_profile()` / `update_profile()` / `delete_profile()` 方法：调用 profiles.py 对应方法

## 5. 前端：UI 布局与样式

- [ ] 5.1 实现 index.html：三区布局（连接配置、偏好开关、插件与市场），顶部工具栏含 Profile 下拉和操作按钮
- [ ] 5.2 实现 style.css：简洁现代风格，表单控件对齐，分组卡片式布局，响应式适配

## 6. 前端：交互逻辑

- [ ] 6.1 实现 app.js：页面加载时调用 `load_settings()` 填充表单
- [ ] 6.2 实现保存按钮：收集表单值，调用 `save_settings()`，显示成功/失败提示
- [ ] 6.3 实现 Profile 下拉切换：选择 Profile 后调用加载方法填充连接配置表单（不影响开关和插件）
- [ ] 6.4 实现保存为 Profile：弹出输入框输入名称，调用 `save_profile()`
- [ ] 6.5 实现更新和删除 Profile：更新当前 Profile、删除选中 Profile（含确认对话框）
- [ ] 6.6 实现 Token 掩码切换：默认掩码显示，点击切换明文

## 7. 单实例与健壮性

- [ ] 7.1 实现单实例检测：启动时检查已有实例，若存在则激活其窗口并退出
- [ ] 7.2 实现 API_TIMEOUT_MS 输入校验：仅允许数字输入
- [ ] 7.3 测试完整流程：启动 → 加载配置 → 修改 → 保存 → 验证文件内容正确
