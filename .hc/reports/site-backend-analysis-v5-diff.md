# 依赖分析报告差异对比

**原报告**: `site-backend-analysis-v5.md`
**验证时间**: 2025-12-17

## 📊 验证摘要

| 类别 | 报告数量 | 实际一致 | 实际不一致 |
|------|----------|----------|------------|
| 未被引用的文件 | 50 | 50 ✅ | 0 |
| 未使用的导入 | 71 | ~10 | ~61 ❌ |

---

## 🔴 未被引用的文件

### ✅ 状态：与报告一致

所有 50 个被标记为"未被引用"的文件均已验证存在于文件系统中，与报告一致。

---

## 🟡 未使用的导入

### ❌ 与报告不一致（误报列表）

> ⚠️ 以下导入被报告标记为"未使用"，但经验证**实际被使用**。
> 这表明分析工具可能存在检测问题。

| 文件路径 | 导入项 | 实际状态 | 使用位置 |
|----------|--------|----------|----------|
| `components/SearchTable/ActionButtonsDropdown.tsx` | `type ActionButtonType` | 实际被使用 | 第9行等 |
| `components/SearchTable/DraggableTable.tsx` | `ActionButtonType,` | 实际被使用 | 第19行等 |
| `components/SearchTable/SearchTable.tsx` | `BatchActionType,` | 实际被使用 | 多处引用 |
| `components/SearchTable/SearchTable.tsx` | `type SearchTableRef` | 实际被使用 | 多处引用 |
| `context/UploadContext.tsx` | `TotalProgress,` | 实际被使用 | 第18行 |
| `hooks/useRiskWordDetection/useFormRiskDetection.ts` | `DetectionResult,` | 实际被使用 | 第42行等 |
| `middleware/context.ts` | `generateCacheKey,` | 实际被使用 | 第30行 |
| `middleware/engine.ts` | `MiddlewareEngine,` | 实际被使用 | 第10行 |
| `models/menus/createMenu.dto.ts` | `MenuStatus,` | 实际被使用 | 第20行 |
| `models/menus/updateMenu.dto.ts` | `MenuStatus,` | 实际被使用 | 第21行 |
| `models/users/editRolesStatus.ts` | `type BasicResponseDto` | 实际被使用 | 第9行 extends |
| `pages/login/index.tsx` | `userLoginUrl,` | 实际被使用 | 第72行 |
| `pages/low-code/components/renderDynamicForm/components/FormDate/FormDateRange.tsx` | `STORAGE_FORMAT_MAP,` | 实际被使用 | 第54-55行 |
| `pages/low-code/components/renderDynamicForm/components/FormDate/FormTime.tsx` | `STORAGE_FORMAT_MAP,` | 实际被使用 | 第113行 |
| `pages/low-code/hooks/useDynamicForm.ts` | `type PublishComponentsRef` | 实际被使用 | 第56行、319行 |
| `pages/low-code/newList/index.tsx` | `GetAppModelDataUrl,` | 实际被使用 | 第241行 |
| `pages/member/Management/config/memberTableColumns.tsx` | `AuditStatusTag,` | 实际被使用 | 第82行 |
| `pages/member/Management/hooks/useMemberOperations.ts` | `useMemberBatchDelete,` | 实际被使用 | 第28行 |
| `pages/member/Management/memberTables.tsx` | `type MemberListRequestDto` | 实际被使用 | 第77、97、113行 |
| `pages/member/MemberDetail/index.tsx` | `useMemberPasswordGet,` | 实际被使用 | 第75行 |
| `pages/member/MemberSetting/AutoConvertSettings.tsx` | `type MemberConfigData` | 实际被使用 | 第34行 |
| `pages/member/MemberSetting/SiteRegInfo.tsx` | `useRegisterConfigCreate,` | 实际被使用 | 第55行 |
| `pages/member/context/MemberConfigContext.tsx` | `useFieldConfig,` | 实际被使用 | 第73行 |
| `pages/member/modal/example.tsx` | `CustomerConvertModal,` | 实际被使用 | 第123行 |
| `pages/menu-management/MenuForm.tsx` | `MenuType,` | 实际被使用 | 第77行 |
| `pages/resource-library/components/resourceAttributesDrawer.tsx` | `getAcceptExtensions,` | 实际被使用 | 第240行 |
| `pages/resource-library/components/resourceThumbnail.tsx` | `getPreviewButtonText,` | 实际被使用 | 第49行 |
| `pages/resource-library/enterpriseResource.tsx` | `type SearchTableRef` | 实际被使用 | 第105行 |
| `pages/resource-library/enterpriseResource.tsx` | `SvgIcon` | 实际被使用 | 第790行 |
| `pages/safety/banned/content/index.tsx` | `type SearchTableRef` | 实际被使用 | 值类型使用 |
| `pages/safety/banned/interactive/index.tsx` | `type SearchTableRef` | 实际被使用 | 值类型使用 |
| `pages/seo/components/PlaceholderInputLexical/PlaceholderInputLexical.tsx` | `$createTagNode,` | 实际被使用 | 第418、536行 |
| `pages/seo/components/PlaceholderInputLexical/lexical/TagKeyboardPlugin.tsx` | `$isTagNode` | 实际被使用 | 第51、90等行 |
| `pages/seo/components/VariablePanel/index.tsx` | `VariableItem,` | 实际被使用 | 第45、58、80行 |
| `pages/seo/schema.back/components/MainWorkspace/index.tsx` | `SchemaTagItem,` | 实际被使用 | 第64、66行 |
| `pages/seo/schema.back/constants.ts` | `SchemaTagItem,` | 实际被使用 | 第127等行 |
| `pages/seo/schema/components/SchemaConfigForm/index.tsx` | `SchemaTypeTreeNode,` | 实际被使用 | 第39、49行 |
| `pages/seo/schema/constants.ts` | `SchemaTagItem,` | 实际被使用 | 第127等行 |
| `pages/seo/url-redirect/components/RedirectFormModal/index.tsx` | `useUpdateUrlRedirect,` | 实际被使用 | 第19行 |
| `pages/seo/url-redirect/components/RedirectFormModal/index.tsx` | `HttpStatusCode,` | 实际被使用 | 第87行 |
| `pages/seo/url-setup/components/UrlConfigForm/index.tsx` | `DEFAULT_CHARACTER_ENCODE,` | 实际被使用 | 第120行 |
| `pages/seo/url-setup/index.tsx` | `type` | 误报（实际是 SeoUrlRulesData） | 第17行 |
| `pages/setting/RecycleBin/BusinessRecycleBin/index.tsx` | `ActionButtonType,` | 实际被使用 | 第270行 |
| `pages/setting/RecycleBin/ContentRecycleBin/index.tsx` | `ActionButtonType,` | 实际被使用 | 第270行 |
| `pages/setting/RecycleBin/CustomerRecycleBin/index.tsx` | `ActionButtonType,` | 实际被使用 | 第270行 |
| `pages/setting/RecycleBin/ResourceRecycleBin/index.tsx` | `ActionButtonType,` | 实际被使用 | 第291行 |
| `pages/setting/RecycleBin/ResourceRecycleBin/resourceThumbnail.tsx` | `getPreviewButtonText,` | 实际被使用 | 第49行 |
| `pages/setting/RecycleBin/ResourceRecycleBin/utils.ts` | `BusinessCode` | 实际被使用 | 第1454等行 |
| `pages/setting/Setup/BaseSetting/index.tsx` | `CustomFieldItem,` | 实际被使用 | 第79行 |
| `pages/tag/Management/hooks/useTagData.ts` | `useTagGroupByStatus,` | 实际被使用 | 第71行 |
| `pages/tag/Management/hooks/useTagOperations.ts` | `useTagBatchDelete,` | 实际被使用 | 第297行 |
| `pages/tag/Management/tagTables.tsx` | `TagDeleteResultModal,` | 实际被使用 | 多处 |
| `tools/upload/UploadManager.ts` | `UploadConfig,` | 实际被使用 | 多处 |
| `tools/upload/UploadManager.ts` | `UploadStatus,` | 实际被使用 | 第741行 |
| `tools/upload/UploadManager.ts` | `uploadSingleUrl,` | 实际被使用 | 第334等行 |
| `tools/upload/UploadManager.ts` | `UploadChunkMergeResponseDto,` | 实际被使用 | 第360、843行 |
| `tools/upload/types.ts` | `UploadSingleResponseDto,` | 实际被使用 | 第124行 |
| `utils/menuIconUtils.ts` | `type MenuItem` | 实际被使用 | 第29行 |

---

### ✅ 与报告一致（确认未使用）

以下导入经验证**确实未被使用**，与报告一致：

| 文件路径 | 导入项 | 状态 |
|----------|--------|------|
| `components/RiskWord/components/FormRiskWordDetector/index.tsx` | `DetectedRiskWord,` | ✅ 确认未使用 |
| `hooks/useMemberLevelsData.ts` | `MemberLevel` | ✅ 确认未使用 |
| `models/console/updateModelData.ts` | `CreateAppModelDataStatus` | ✅ 确认未使用 |
| `models/resourceLibrary/moveResource.ts` | `ApiEndpoints` | ✅ 确认未使用 |
| `models/resourceLibrary/resourceExport.ts` | `ApiEndpoints` | ✅ 确认未使用 |
| `models/resourceLibrary/resourceExport.ts` | `ResourceType` | ✅ 确认未使用 |
| `models/resourceLibrary/resourceReplace.ts` | `ApiEndpoints` | ✅ 确认未使用 |
| `models/resourceLibrary/resourceUsingList.ts` | `ApiEndpoints` | ✅ 确认未使用 |
| `models/resourceLibrary/saveUserColumns.ts` | `ApiEndpoints` | ✅ 确认未使用 |
| `models/seo/templateUpdate.ts` | `MemberListRequestDto` | ✅ 确认未使用 |
| `models/seo/templateUpdate.ts` | `SeoTemplateListItemDto` | ✅ 确认未使用 |
| `pages/authorization/index.tsx` | `userGetMenusUrl,` | ✅ 确认未使用 |
| `tools/utils.ts` | `type BasicResponseDto` | ✅ 确认未使用 |

---

## 🔍 问题分析

### 可能的误报原因

1. **类型导入检测问题**: 分析工具可能无法正确识别 `type` 导入的使用情况
2. **解构导入检测问题**: 从解构导入中提取的类型可能未被正确追踪
3. **泛型参数中的使用**: 作为泛型参数使用的类型可能未被检测到
4. **继承/扩展中的使用**: `extends` 或 `implements` 中使用的类型可能被遗漏
5. **JSX 组件使用**: 在 JSX 中直接使用的组件可能未被正确识别

### 建议改进

1. 改进 TypeScript 类型导入的追踪逻辑
2. 增加对 `extends`、泛型参数的使用检测
3. 完善 JSX 组件引用的识别
4. 考虑使用 TypeScript 编译器 API 进行更准确的分析

---

**报告生成时间**: 2025-12-17
