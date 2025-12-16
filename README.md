# dependence-analysis-mcp

一个标准 MCP Server（stdio）用于扫描前端/Node 项目里的 ESModule `import ... from ...` 依赖关系，帮助你快速找出：

- ✅ **已引用文件**：被 import 且**确实有使用**（导入但未使用的不计入），并附带 **import 总次数**
- 🧹 **未引用文件**：扫描目录内的源码文件，但从未被其他源码文件引用
- 💤 **已导入但未使用**：存在 `import`，但导入的标识符在文件中未被使用
- 🧪 **实验性（不稳定）**：`__experimentalUnusefulFiles`，对“疑似废弃/临时文件”的推断，极不稳定，仅供参考

> 说明：当前实现返回的文件路径是**绝对路径**。

---

## ✨ 特性

- 🎯 支持 `React / Vue / Angular / Node` 常见代码形态（基于 `.js/.jsx/.ts/.tsx/.vue` 扫描）
- 🧠 AST 级未使用导入检测（`tree-sitter`），大幅降低误判；异常时自动降级为词法策略
- 🔗 路径解析支持：相对路径 + `tsconfig.json` 的 `paths` + `vite.config.*` 的 `resolve.alias`
- 🚫 默认忽略 `node_modules/dist/build/.next/.nuxt/coverage/...` 以及测试/示例/fixtures/mock 等
- 📦 作为 Python 包发布到 PyPI，可直接 `pip install` 使用

---

## 📦 安装

```powershell
pip install dependence-analysis-mcp
```

---

## 🚀 快速开始

启动 MCP server（stdio）：

```powershell
dependence-analysis-mcp
```

然后在你的 MCP 客户端里调用本服务提供的 tool：`run_dependence_analysis`。

---
8
## 🧩 MCP Tool

### `run_dependence_analysis(request)`

#### 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `directory` | `string` | 是 | 要扫描的目录（建议传项目根目录或子目录） |
| `roots` | `string[] \| null` | 否 | 入口文件/目录列表（当前实现暂不强制；后续可通过对话再增强 roots 语义） |
| `includeExtensions` | `string[] \| null` | 否 | 额外/自定义扫描后缀（默认：`.ts/.tsx/.js/.jsx/.vue`） |

#### 返回结构

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `referencedFiles` | `{ path: string; importCount: number }[]` | 已引用文件（排除“导入但未使用”）与 import 总次数 |
| `unreferencedFiles` | `string[]` | 未引用文件（扫描范围内） |
| `unusedImports` | `{ file: string; importSource: string; importedNames: string[] }[]` | 已导入但未使用的 import |
| `__experimentalUnusefulFiles` | `string[]` | 实验性字段：疑似无用文件（非常不稳定，仅供参考） |
| `__experimentalNotice` | `string` | 对实验性字段的明确提示 |
| `warnings` | `string[]` | 解析/降级等告警信息 |

#### 示例输出（节选）

```json
{
  "referencedFiles": [
    { "path": "C:/repo/src/utils/a.ts", "importCount": 3 }
  ],
  "unreferencedFiles": [
    "C:/repo/src/INPUTV2.tsx"
  ],
  "unusedImports": [
    {
      "file": "C:/repo/src/pages/home.tsx",
      "importSource": "@/components/Button",
      "importedNames": ["Button"]
    }
  ],
  "__experimentalUnusefulFiles": [
    "C:/repo/src/INPUTV2.tsx"
  ],
  "__experimentalNotice": "`__experimentalUnusefulFiles` 是实验性属性，非常不稳定，仅供参考。",
  "warnings": []
}
```

---

## 🧷 VS Code 调用（TODO）

目标交互：用户在 VS Code 中执行 `/runDependenceAnalysis`，由 MCP 客户端/扩展将其映射为对本服务 tool `run_dependence_analysis` 的调用。

TODO：补充一个最小可用的 VS Code 侧配置/扩展示例（等你确定所用 MCP 客户端后再落地）。

---

## 🔧 忽略规则（默认）

默认会跳过：

- 目录：`node_modules`、`.git`、`dist`、`build`、`out`、`.next`、`.nuxt`、`.angular`、`coverage`、`.cache`、`.turbo`、`.vercel`
- 测试/示例/辅助目录：`__tests__`、`test(s)`、`e2e`、`cypress`、`__mocks__`、`mocks/mock`、`fixtures/fixture`、`examples/example`、`demo/demos`、`stories`
- 文件：`*.d.ts`、`*.test.*`、`*.spec.*`、`*.stories.*`

---

## ⚠️ 限制与注意事项

- 只统计**本地源码文件**之间的引用：`import React from 'react'` 这类外部依赖会被忽略。
- 当前主要针对 `import ... from ...` + `export ... from ...` 做静态分析；更复杂的动态导入场景可能无法覆盖。
- `__experimentalUnusefulFiles` 为实验性推断字段：不要据此自动删除文件。

---

## 🧪 测试

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

---

## 📂 项目结构

```text
dependence-analysis-mcp/
├── src/dependence_analysis_mcp/  # MCP server + 扫描核心
├── tests/                       # 单元测试
├── pyproject.toml
├── MANIFEST.in
└── README.md
```

---

## 🧰 开发

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

---

## 📦 发布到 PyPI（维护者）

下面是推荐的发布流程（使用 API Token）：

```powershell
python -m pip install -U build twine
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

建议在上传前先：

- 更新 `pyproject.toml` 里的版本号
-（可选）打 git tag（例如 `v0.1.1`）

### 需要 `.gitignore` / “npmignore” 吗？

- `git`：建议加入 `.gitignore`，避免把 `dist/`、`.venv/`、`__pycache__/` 等提交进仓库。
- PyPI 包内容：Python 生态不使用 `.npmignore`。
  - **推荐**使用 `MANIFEST.in` 或在构建工具（hatchling）的配置中明确包含/排除文件。
  - 本项目 wheel 只打包 `src/dependence_analysis_mcp`（见 `pyproject.toml` 的 `packages` 配置），不会把测试等目录打进 wheel。
  - `MANIFEST.in` 主要影响 sdist（源码包）内容，可用于排除 `tests/` 等。

---

## 📝 Changelog

- `0.1.0`：首个可用版本：stdio MCP server + 依赖扫描 + 未使用导入检测 + tsconfig/vite alias 支持。
