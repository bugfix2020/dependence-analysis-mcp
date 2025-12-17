# 依赖分析报告

**扫描目录**: `/Users/liuyuxuan/wwwroot/myself/dependence-analysis-mcp/site-backend/src`
**生成时间**: 2025-12-17 15:39:20

## 📊 统计摘要

- **总文件数**: 543
- **被引用文件数**: 493
- **未被引用文件数**: 50
- **未使用的导入数**: 71

## 🔴 未被引用的文件

> ⚠️ 以下文件在项目中没有被其他文件直接或间接引用，请手动确认是否需要保留。
> 入口文件（如 main.tsx, App.tsx）通常不会被其他文件引用，这是正常的。

### 📁 components (1 个文件)

- [ ] `components/I18nDemo.tsx`

### 📁 components/Permission (1 个文件)

- [ ] `components/Permission/index.ts`

### 📁 components/RichTextEditor (3 个文件)

- [ ] `components/RichTextEditor/context/SettingsContext.tsx`
- [ ] `components/RichTextEditor/plugins/ToolbarPlyginType.ts`
- [ ] `components/RichTextEditor/plugins/utils.ts`

### 📁 components/RouteGuard (1 个文件)

- [ ] `components/RouteGuard/index.tsx`

### 📁 components/SearchTable (1 个文件)

- [ ] `components/SearchTable/AddFolderModal.tsx`

### 📁 components/SimplePermissionButton (1 个文件)

- [ ] `components/SimplePermissionButton/index.tsx`

### 📁 constants (1 个文件)

- [ ] `constants/developmentFeatures.ts`

### 📁 layout (1 个文件)

- [ ] `layout/types.ts`

### 📁 models/content (4 个文件)

- [ ] `models/content/appCategotyModelData.ts`
- [ ] `models/content/categoryModelData.ts`
- [ ] `models/content/index.ts`
- [ ] `models/content/pageModelData.ts`

### 📁 models/member (2 个文件)

- [ ] `models/member/index.ts`
- [ ] `models/member/memberConfig.ts`

### 📁 models/menus (1 个文件)

- [ ] `models/menus/index.ts`

### 📁 models/safety (2 个文件)

- [ ] `models/safety/index.ts`
- [ ] `models/safety/interactiveBanned.ts`

### 📁 models/seo (6 个文件)

- [ ] `models/seo/redirectCreate.ts`
- [ ] `models/seo/redirectDelete.ts`
- [ ] `models/seo/redirectExportTemplate.ts`
- [ ] `models/seo/redirectImport.ts`
- [ ] `models/seo/redirectList.ts`
- [ ] `models/seo/redirectUpdate.ts`

### 📁 models/tag (1 个文件)

- [ ] `models/tag/index.ts`

### 📁 models/users (3 个文件)

- [ ] `models/users/batchRole.ts`
- [ ] `models/users/batchUser.ts`
- [ ] `models/users/getRolePermissions.ts`

### 📁 pages/account-permission (1 个文件)

- [ ] `pages/account-permission/components/RoleDrawe/types.ts`

### 📁 pages/low-code (1 个文件)

- [ ] `pages/low-code/components/renderDynamicForm/components/index.ts`

### 📁 pages/seo (8 个文件)

- [ ] `pages/seo/components/PlaceholderInputLexical/lexical/selectionPath.ts`
- [ ] `pages/seo/components/VariablePanel/adapters.ts`
- [ ] `pages/seo/meta-tags.back/components/SeoConfigForm/seoFieldsSchema.ts`
- [ ] `pages/seo/meta-tags/components/SeoConfigForm/seoFieldsSchema.ts`
- [ ] `pages/seo/schema.back/constants.ts`
- [ ] `pages/seo/schema/constants.ts`
- [ ] `pages/seo/url-redirect/constants.ts`
- [ ] `pages/seo/url-setup/constants.ts`

### 📁 pages/setting (2 个文件)

- [ ] `pages/setting/Setup/Advanced/constants/systemPresets.ts`
- [ ] `pages/setting/Setup/components/fields/index.ts`

### 📁 pages/tag (1 个文件)

- [ ] `pages/tag/components/index.ts`

### 📁 store (1 个文件)

- [ ] `store/menuUtils.ts`

### 📁 tools (1 个文件)

- [ ] `tools/oauthTokenManager.ts`

### 📁 types (1 个文件)

- [ ] `types/member.ts`

### 📁 utils (4 个文件)

- [ ] `utils/buttonPermissionUtils.ts`
- [ ] `utils/memberLevelCache.ts`
- [ ] `utils/menuUtils.ts`
- [ ] `utils/videoRangeCheck.ts`

### 📁 根目录 (1 个文件)

- [ ] `main.tsx`

## 🟡 未使用的导入

> 以下导入语句在文件中没有被使用。

#### `components/RiskWord/components/FormRiskWordDetector/index.tsx`

- `DetectedRiskWord,` from `@/hooks/useRiskWordDetection/types`

#### `components/SearchTable/ActionButtonsDropdown.tsx`

- `type ActionButtonType` from `./types`

#### `components/SearchTable/DraggableTable.tsx`

- `ActionButtonType,` from `./types`

#### `components/SearchTable/SearchTable.tsx`

- `BatchActionType,` from `./types`
- `type SearchTableRef` from `./types`

#### `context/UploadContext.tsx`

- `TotalProgress,` from `@/tools/upload/types`

#### `hooks/useMemberLevelsData.ts`

- `MemberLevel` from `@/models/member/memberLevels`

#### `hooks/useRiskWordDetection/useFormRiskDetection.ts`

- `DetectionResult,` from `./types`

#### `middleware/context.ts`

- `generateCacheKey,` from `./utils`

#### `middleware/engine.ts`

- `MiddlewareEngine,` from `./types`

#### `models/console/updateModelData.ts`

- `CreateAppModelDataStatus` from `@/models/console/createModelData`

#### `models/menus/createMenu.dto.ts`

- `MenuStatus,` from `./getMenusTree.dto`

#### `models/menus/updateMenu.dto.ts`

- `MenuStatus,` from `./getMenusTree.dto`

#### `models/resourceLibrary/moveResource.ts`

- `ApiEndpoints` from `@/models/apis`

#### `models/resourceLibrary/resourceExport.ts`

- `ApiEndpoints` from `@/models/apis`
- `ResourceType` from `@/models/resourceLibrary/types`

#### `models/resourceLibrary/resourceReplace.ts`

- `ApiEndpoints` from `@/models/apis`

#### `models/resourceLibrary/resourceUsingList.ts`

- `ApiEndpoints` from `@/models/apis`

#### `models/resourceLibrary/saveUserColumns.ts`

- `ApiEndpoints` from `@/models/apis`

#### `models/seo/templateUpdate.ts`

- `MemberListRequestDto` from `@/models/member`
- `SeoTemplateListItemDto` from `@/models`

#### `models/users/editRolesStatus.ts`

- `type BasicResponseDto` from `@/models`

#### `pages/authorization/index.tsx`

- `userGetMenusUrl,` from `@/models/users/getMenus`

#### `pages/login/index.tsx`

- `userLoginUrl,` from `@/models`

#### `pages/low-code/components/renderDynamicForm/components/FormDate/FormDateRange.tsx`

- `STORAGE_FORMAT_MAP,` from `./types`

#### `pages/low-code/components/renderDynamicForm/components/FormDate/FormTime.tsx`

- `STORAGE_FORMAT_MAP,` from `./types`

#### `pages/low-code/hooks/useDynamicForm.ts`

- `type PublishComponentsRef` from `../newList/publish-components`

#### `pages/low-code/newList/index.tsx`

- `GetAppModelDataUrl,` from `@/models`

#### `pages/member/Management/config/memberTableColumns.tsx`

- `AuditStatusTag,` from `../../components/tableItemRender`

#### `pages/member/Management/hooks/useMemberOperations.ts`

- `useMemberBatchDelete,` from `@/models/member/memberOperations`

#### `pages/member/Management/memberTables.tsx`

- `type MemberListRequestDto` from `@/models/member/memberList`

#### `pages/member/MemberDetail/index.tsx`

- `useMemberPasswordGet,` from `@/models/member/memberOperations`

#### `pages/member/MemberSetting/AutoConvertSettings.tsx`

- `type MemberConfigData` from `@/models/member/memberConfig`

#### `pages/member/MemberSetting/SiteRegInfo.tsx`

- `useRegisterConfigCreate,` from `@/models/member/memberConfig`

#### `pages/member/context/MemberConfigContext.tsx`

- `useFieldConfig,` from `@/models/member/memberConfig`

#### `pages/member/modal/example.tsx`

- `CustomerConvertModal,` from `./index`

#### `pages/menu-management/MenuForm.tsx`

- `MenuType,` from `@/models/menus`

#### `pages/resource-library/components/resourceAttributesDrawer.tsx`

- `getAcceptExtensions,` from `../utils`

#### `pages/resource-library/components/resourceThumbnail.tsx`

- `getPreviewButtonText,` from `../utils`

#### `pages/resource-library/enterpriseResource.tsx`

- `type SearchTableRef` from `@/components/SearchTable/types`
- `SvgIcon` from `@/components/IconFont/SvgIcon`

#### `pages/safety/banned/content/index.tsx`

- `type SearchTableRef` from `@/components/SearchTable/types`

#### `pages/safety/banned/interactive/index.tsx`

- `type SearchTableRef` from `@/components/SearchTable/types`

#### `pages/seo/components/PlaceholderInputLexical/PlaceholderInputLexical.tsx`

- `$createTagNode,` from `./TagNode`

#### `pages/seo/components/PlaceholderInputLexical/lexical/TagKeyboardPlugin.tsx`

- `$isTagNode` from `../TagNode`

#### `pages/seo/components/VariablePanel/index.tsx`

- `VariableItem,` from `./types`

#### `pages/seo/schema.back/components/MainWorkspace/index.tsx`

- `SchemaTagItem,` from `@/pages/seo/schema/types`

#### `pages/seo/schema.back/constants.ts`

- `SchemaTagItem,` from `./types`

#### `pages/seo/schema/components/SchemaConfigForm/index.tsx`

- `SchemaTypeTreeNode,` from `@/pages/seo/schema/types`

#### `pages/seo/schema/constants.ts`

- `SchemaTagItem,` from `./types`

#### `pages/seo/url-redirect/components/RedirectFormModal/index.tsx`

- `useUpdateUrlRedirect,` from `@/models`
- `HttpStatusCode,` from `../../constants`

#### `pages/seo/url-setup/components/UrlConfigForm/index.tsx`

- `DEFAULT_CHARACTER_ENCODE,` from `../../constants`

#### `pages/seo/url-setup/index.tsx`

- `type` from `@/models`

#### `pages/setting/RecycleBin/BusinessRecycleBin/index.tsx`

- `ActionButtonType,` from `@/components/SearchTable/types`

#### `pages/setting/RecycleBin/ContentRecycleBin/index.tsx`

- `ActionButtonType,` from `@/components/SearchTable/types`

#### `pages/setting/RecycleBin/CustomerRecycleBin/index.tsx`

- `ActionButtonType,` from `@/components/SearchTable/types`

#### `pages/setting/RecycleBin/ResourceRecycleBin/index.tsx`

- `ActionButtonType,` from `@/components/SearchTable/types`

#### `pages/setting/RecycleBin/ResourceRecycleBin/resourceThumbnail.tsx`

- `getPreviewButtonText,` from `./utils`

#### `pages/setting/RecycleBin/ResourceRecycleBin/utils.ts`

- `BusinessCode` from `@/constants/businessCode`

#### `pages/setting/Setup/BaseSetting/index.tsx`

- `CustomFieldItem,` from `./components/CustomGroupCard`

#### `pages/tag/Management/hooks/useTagData.ts`

- `useTagGroupByStatus,` from `@/models/tag/tagList`

#### `pages/tag/Management/hooks/useTagOperations.ts`

- `useTagBatchDelete,` from `@/models/tag/tagOperations`

#### `pages/tag/Management/tagTables.tsx`

- `TagDeleteResultModal,` from `../components`

#### `tools/upload/UploadManager.ts`

- `UploadConfig,` from `@/tools`
- `UploadStatus,` from `@/tools`
- `uploadSingleUrl,` from `@/models`
- `UploadChunkMergeResponseDto,` from `@/models`

#### `tools/upload/types.ts`

- `UploadSingleResponseDto,` from `@/models`

#### `tools/utils.ts`

- `type BasicResponseDto` from `@/models`

#### `utils/menuIconUtils.ts`

- `type MenuItem` from `@/store/menus`

## 📈 被引用最多的文件 (Top 20)

| 文件 | 引用次数 |
|------|----------|
| `models/apis.ts` | 168 |
| `hooks/useAxios.tsx` | 118 |
| `models/setting/settingDictionary.ts` | 74 |
| `models/seo/index.ts` | 69 |
| `models/seo/appsPages.ts` | 69 |
| `models/seo/urlRules.ts` | 69 |
| `models/seo/templateUpdate.ts` | 69 |
| `models/seo/templateVariables.ts` | 69 |
| `models/seo/templateDetail.ts` | 69 |
| `models/seo/templateList.ts` | 69 |
| `models/seo/recommendedVariables.ts` | 69 |
| `models/seo/advancedSettings.ts` | 69 |
| `models/seo/urlRedirect.ts` | 69 |
| `models/seo/metaVariables.ts` | 69 |
| `models/seo/otherAppVariables.ts` | 69 |
| `models/resourceLibrary/resourceCapacity.ts` | 69 |
| `models/seo/templateReset.ts` | 69 |
| `models/seo/lowcodeLabels.ts` | 69 |
| `models/seo/redirectBatch.ts` | 69 |
| `components/IconFont/index.tsx` | 67 |
