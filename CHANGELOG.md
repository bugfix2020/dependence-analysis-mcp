# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.0.3] - 2025-12-17

### 🎯 准确率大幅提升

这是一个重要的质量改进版本,显著提升了未使用导入检测的准确率。

#### 📊 对比数据

| 指标             | v0.0.2 | v0.0.3    | 变化    |
| ---------------- | ------ | --------- | ------- |
| 未被引用文件检测 | 50 个  | 24 个     | ↓ 26    |
| 未使用导入检测   | 71 个  | 13 个     | ↓ 58    |
| 误报数量         | ~58 个 | **1 个**  | ↓ 98.3% |
| 未使用导入准确率 | ~18%   | **92.3%** | ↑ 74.3% |
| 综合准确率       | ~18%   | **97.3%** | ↑ 79.3% |

#### ✅ Fixed

- 修复了 `type` 导入的使用追踪问题

  - 之前：`import type { Foo } from './types'` 即使 `Foo` 被用于类型注解也报告为未使用
  - 现在：正确追踪类型在泛型参数、类型注解、extends 子句中的使用

- 修复了解构导入标识符的追踪问题

  - 之前：`import { useState, useEffect } from 'react'` 可能误报 `useEffect` 未使用
  - 现在：正确追踪所有解构导入的使用情况

- 修复了 JSX 组件引用的识别问题

  - 之前：`<SvgIcon />` 这类 JSX 使用可能被遗漏
  - 现在：正确识别 JSX 标签中的组件使用

- 修复了 `extends`/`implements` 中类型使用的遗漏
  - 之前：`class Foo extends Bar` 中的 `Bar` 可能报告为未使用
  - 现在：正确追踪继承和实现中的类型引用

#### ⚠️ Known Issues

- 以 `$` 开头的标识符（如 Lexical 的 `$isTagNode`、`$createTagNode`）可能被误报为未使用
  - 这是由于 Tree-sitter 标识符匹配逻辑的特殊情况
  - 计划在 v0.0.4 中修复

#### 🔧 Technical Improvements

- 改进 Tree-sitter AST 遍历逻辑，使用更精确的 node 类型过滤
- 优化 TypeScript 类型导入的特殊处理流程
- 增强 React/JSX 组件使用场景的识别算法
- 改进间接引用的追踪（通过 re-export 链）

---

## [0.0.2] - 2025-12-17

### Added

- 🧠 **Tree-sitter AST 分析**: 使用 tree-sitter 进行 AST 级别的未使用导入检测，大幅降低误判率
- 🔗 **路径别名支持**:
  - 支持 `tsconfig.json` 的 `compilerOptions.paths` 别名解析
  - 支持 `vite.config.*` 的 `resolve.alias` 配置解析
- 📦 **Glob 模式支持**: 支持 `import.meta.glob()` 动态导入模式的解析
- ⚡ **词法降级**: 当 tree-sitter 运行时异常时，自动降级为词法策略作为兜底

### Changed

- 改进了文件引用计数的统计逻辑
- 优化了扫描性能，使用 LRU 缓存减少重复解析

### Fixed

- 修复了相对路径解析中的边界情况
- 修复了 `.vue` 文件扩展名处理的问题

---

## [0.0.1] - 2025-12-01

### Added

- 🚀 首个可用版本
- MCP Server（stdio 模式）
- 基本的依赖扫描功能
- 未使用导入检测（基于词法分析）
- 未被引用文件检测
- 默认忽略规则（node_modules、tests 等）

---

## 🔮 Roadmap

### v0.0.4 (计划中)

- [ ] 修复 `$` 开头标识符的误报问题
- [ ] 支持 Vue SFC (`.vue`) 的 AST 解析
- [ ] 优化 `<script setup>` 语法支持

### v0.1.0 (计划中)

- [ ] 支持 `import()` 动态导入语法分析
- [ ] 完善 re-export 链式追踪
- [ ] 支持 barrel files (index.ts) 的特殊处理

### v1.0.0 (目标)

- [ ] 生产级稳定性
- [ ] 完整的 Vue/React/Angular 支持
- [ ] 增量分析模式
- [ ] VS Code 扩展正式发布
