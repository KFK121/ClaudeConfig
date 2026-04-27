// ui/app.js — Frontend logic for Claude Settings Manager

// pywebview API bridge (available after page loads)
let api;

// Current full settings data (for preserving unknown fields on save)
let currentSettings = {};

// Profile connection env keys
const CONNECTION_KEYS = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
];

// === Initialization ===

window.addEventListener("pywebviewready", () => {
    api = pywebview.api;
    init();
});

async function init() {
    await loadAndRenderSettings();
    await refreshProfileSelect();
    bindEvents();
}

// === Settings load & render ===

async function loadAndRenderSettings() {
    const resp = await api.load_settings();
    if (!resp.success) {
        showToast(resp.error, "error");
        return;
    }
    currentSettings = resp.data;
    renderSettings(currentSettings);
}

function renderSettings(data) {
    const env = data.env || {};

    // Connection config inputs
    const fields = {
        "f-base-url": "ANTHROPIC_BASE_URL",
        "f-auth-token": "ANTHROPIC_AUTH_TOKEN",
        "f-opus-model": "ANTHROPIC_DEFAULT_OPUS_MODEL",
        "f-sonnet-model": "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "f-haiku-model": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "f-timeout": "API_TIMEOUT_MS",
    };
    for (const [elemId, envKey] of Object.entries(fields)) {
        document.getElementById(elemId).value = env[envKey] || "";
    }

    // Preference switches: checked if value === "1"
    const switches = {
        "f-disable-telemetry": "DISABLE_TELEMETRY",
        "f-disable-error": "DISABLE_ERROR_REPORTING",
        "f-disable-traffic": "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    };
    for (const [elemId, envKey] of Object.entries(switches)) {
        document.getElementById(elemId).checked = env[envKey] === "1";
    }

    // Plugins
    const pluginsContainer = document.getElementById("plugins-container");
    pluginsContainer.innerHTML = "";
    const plugins = data.enabledPlugins || {};
    for (const [name, enabled] of Object.entries(plugins)) {
        const label = document.createElement("label");
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = enabled === true;
        checkbox.dataset.pluginName = name;
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(" " + name));
        pluginsContainer.appendChild(label);
    }

    // Marketplaces
    const mktContainer = document.getElementById("marketplaces-container");
    mktContainer.innerHTML = "";
    const marketplaces = data.extraKnownMarketplaces || {};
    for (const [name, info] of Object.entries(marketplaces)) {
        const div = document.createElement("div");
        div.className = "marketplace-item";
        const repo = info.source ? info.source.repo : "";
        div.innerHTML = `<span class="icon">📦</span><span class="name">${escapeHtml(name)}</span><span class="source">${escapeHtml(repo)}</span>`;
        mktContainer.appendChild(div);
    }
}

// === Collect form values and save ===

function collectFormData() {
    // Start from currentSettings to preserve unknown fields
    const data = JSON.parse(JSON.stringify(currentSettings));
    data.env = data.env || {};

    // Connection config fields
    data.env.ANTHROPIC_BASE_URL = document.getElementById("f-base-url").value;
    data.env.ANTHROPIC_AUTH_TOKEN = document.getElementById("f-auth-token").value;
    data.env.ANTHROPIC_DEFAULT_OPUS_MODEL = document.getElementById("f-opus-model").value;
    data.env.ANTHROPIC_DEFAULT_SONNET_MODEL = document.getElementById("f-sonnet-model").value;
    data.env.ANTHROPIC_DEFAULT_HAIKU_MODEL = document.getElementById("f-haiku-model").value;

    const timeout = document.getElementById("f-timeout").value.trim();
    if (timeout) {
        data.env.API_TIMEOUT_MS = timeout;
    }

    // Preference switches
    const switchMap = {
        "f-disable-telemetry": "DISABLE_TELEMETRY",
        "f-disable-error": "DISABLE_ERROR_REPORTING",
        "f-disable-traffic": "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    };
    for (const [elemId, envKey] of Object.entries(switchMap)) {
        if (document.getElementById(elemId).checked) {
            data.env[envKey] = "1";
        } else {
            delete data.env[envKey];
        }
    }

    // Plugins
    data.enabledPlugins = data.enabledPlugins || {};
    const pluginCheckboxes = document.querySelectorAll("#plugins-container input[type=checkbox]");
    pluginCheckboxes.forEach(cb => {
        const name = cb.dataset.pluginName;
        if (cb.checked) {
            data.enabledPlugins[name] = true;
        } else {
            delete data.enabledPlugins[name];
        }
    });

    return data;
}

async function handleSave() {
    const data = collectFormData();
    const resp = await api.save_settings(data);
    if (resp.success) {
        currentSettings = data;
        showToast("配置已保存", "success");
    } else {
        showToast("保存失败: " + resp.error, "error");
    }
}

// === Profile operations ===

async function refreshProfileSelect() {
    const resp = await api.list_profiles();
    const select = document.getElementById("profile-select");
    // Keep first placeholder option
    select.innerHTML = '<option value="">-- 无已保存配置 --</option>';
    if (resp.success && resp.data.length > 0) {
        resp.data.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.filename;
            opt.textContent = p.name;
            opt.dataset.env = JSON.stringify(p.env);
            select.appendChild(opt);
        });
    }
}

function handleProfileSelect() {
    const select = document.getElementById("profile-select");
    const selected = select.options[select.selectedIndex];
    if (!selected || !selected.value) return;

    const profileEnv = JSON.parse(selected.dataset.env);
    // Only fill connection config fields (not switches, timeout, plugins)
    document.getElementById("f-base-url").value = profileEnv.ANTHROPIC_BASE_URL || "";
    document.getElementById("f-auth-token").value = profileEnv.ANTHROPIC_AUTH_TOKEN || "";
    document.getElementById("f-opus-model").value = profileEnv.ANTHROPIC_DEFAULT_OPUS_MODEL || "";
    document.getElementById("f-sonnet-model").value = profileEnv.ANTHROPIC_DEFAULT_SONNET_MODEL || "";
    document.getElementById("f-haiku-model").value = profileEnv.ANTHROPIC_DEFAULT_HAIKU_MODEL || "";
}

function getConnectionEnv() {
    return {
        ANTHROPIC_BASE_URL: document.getElementById("f-base-url").value,
        ANTHROPIC_AUTH_TOKEN: document.getElementById("f-auth-token").value,
        ANTHROPIC_DEFAULT_OPUS_MODEL: document.getElementById("f-opus-model").value,
        ANTHROPIC_DEFAULT_SONNET_MODEL: document.getElementById("f-sonnet-model").value,
        ANTHROPIC_DEFAULT_HAIKU_MODEL: document.getElementById("f-haiku-model").value,
    };
}

async function handleSaveProfile() {
    const name = await showDialog("保存新 Profile", "请输入 Profile 名称：", true);
    if (!name) return;

    const env = getConnectionEnv();
    const resp = await api.save_profile(name, env);
    if (resp.success) {
        showToast("Profile 已保存", "success");
        await refreshProfileSelect();
    } else {
        showToast("保存失败: " + resp.error, "error");
    }
}

async function handleUpdateProfile() {
    const select = document.getElementById("profile-select");
    const filename = select.value;
    if (!filename) {
        showToast("请先选择一个 Profile", "error");
        return;
    }
    const stem = filename.replace(".json", "");
    const env = getConnectionEnv();
    const resp = await api.update_profile(stem, env);
    if (resp.success) {
        showToast("Profile 已更新", "success");
        await refreshProfileSelect();
    } else {
        showToast("更新失败: " + resp.error, "error");
    }
}

async function handleDeleteProfile() {
    const select = document.getElementById("profile-select");
    const filename = select.value;
    if (!filename) {
        showToast("请先选择一个 Profile", "error");
        return;
    }
    const profileName = select.options[select.selectedIndex].textContent;
    const confirmed = await showDialog("删除 Profile", `确认删除 "${profileName}" 吗？此操作不可撤销。`, false);
    if (!confirmed) return;

    const stem = filename.replace(".json", "");
    const resp = await api.delete_profile(stem);
    if (resp.success) {
        showToast("Profile 已删除", "success");
        select.selectedIndex = 0;
        await refreshProfileSelect();
    } else {
        showToast("删除失败: " + resp.error, "error");
    }
}

// === Token toggle ===

function handleToggleToken() {
    const input = document.getElementById("f-auth-token");
    input.type = input.type === "password" ? "text" : "password";
}

// === Timeout validation ===

function handleTimeoutInput(e) {
    e.target.value = e.target.value.replace(/[^\d]/g, "");
}

// === Dialog ===

let dialogResolve = null;

function showDialog(title, message, showInput) {
    return new Promise(resolve => {
        dialogResolve = resolve;
        document.getElementById("dialog-message").textContent = message;
        const inputWrapper = document.querySelector(".dialog-input-wrapper");
        const input = document.getElementById("dialog-input");
        if (showInput) {
            inputWrapper.classList.remove("hidden");
            input.value = "";
        } else {
            inputWrapper.classList.add("hidden");
        }
        document.getElementById("dialog-overlay").classList.remove("hidden");
        if (showInput) input.focus();
    });
}

function handleDialogConfirm() {
    document.getElementById("dialog-overlay").classList.add("hidden");
    const inputWrapper = document.querySelector(".dialog-input-wrapper");
    if (!inputWrapper.classList.contains("hidden")) {
        const val = document.getElementById("dialog-input").value.trim();
        dialogResolve(val || null);
    } else {
        dialogResolve(true);
    }
    dialogResolve = null;
}

function handleDialogCancel() {
    document.getElementById("dialog-overlay").classList.add("hidden");
    dialogResolve(null);
    dialogResolve = null;
}

// === Toast ===

let toastTimer = null;

function showToast(message, type) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = "toast " + type;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        toast.classList.add("hidden");
    }, 2500);
}

// === Utility ===

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// === Event binding ===

function bindEvents() {
    document.getElementById("btn-save").addEventListener("click", handleSave);
    document.getElementById("profile-select").addEventListener("change", handleProfileSelect);
    document.getElementById("btn-save-profile").addEventListener("click", handleSaveProfile);
    document.getElementById("btn-update-profile").addEventListener("click", handleUpdateProfile);
    document.getElementById("btn-delete-profile").addEventListener("click", handleDeleteProfile);
    document.getElementById("btn-toggle-token").addEventListener("click", handleToggleToken);
    document.getElementById("f-timeout").addEventListener("input", handleTimeoutInput);
    document.getElementById("dialog-confirm").addEventListener("click", handleDialogConfirm);
    document.getElementById("dialog-cancel").addEventListener("click", handleDialogCancel);
}
