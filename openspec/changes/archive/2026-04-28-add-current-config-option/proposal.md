## 为什么

Profile 下拉框选中某项后再次点击同一项不会触发 change 事件，导致表单不更新。用户无法"重新加载"当前已选中的 Profile 配置。同时缺少一个回到"文件中实际生效值"的操作入口。

## 变更内容

- **修复**：Profile 下拉框增加"当前配置"选项，始终位于最顶部
- **新增**：选择"当前配置"时，从 settings.json 实时读取并填充连接配置表单
- **新增**：点击"确认生效"后，下拉框自动选中"当前配置"
- **新增**：应用启动时，下拉框默认选中"当前配置"

## 能力

### 新增能力
- `current-config-option`: 在 Profile 下拉框中增加"当前配置"选项，从 settings.json 实时读取值填充表单

### 修改能力
- `settings-editor`: Profile 选择行为变更——增加"当前配置"选项作为默认和回退选项

## 影响

- 修改文件：`ui/app.js`（refreshProfileSelect、handleProfileSelect、handleSave 函数）
- 无后端变更
