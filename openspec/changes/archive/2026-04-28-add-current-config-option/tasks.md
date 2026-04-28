## 1. 修改前端逻辑

- [x] 1.1 修改 `refreshProfileSelect()`：在下拉框顶部添加"当前配置"选项（value=`__current__`），位于所有 Profile 选项之前
- [x] 1.2 修改 `handleProfileSelect()`：检测选中值为 `__current__` 时，调用 `api.load_settings()` 实时读取 settings.json 并填充连接配置表单
- [x] 1.3 修改 `refreshProfileSelect()`：填充选项后将下拉框默认选中"当前配置"
- [x] 1.4 修改 `handleSave()`：保存成功后，将下拉框选中项设回"当前配置"
