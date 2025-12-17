# 依赖分析报告

**扫描目录**: `/Users/liuyuxuan/wwwroot/myself/dependence-analysis-mcp/site-backend/src`
**生成时间**: 2025-12-17 16:33:48

## 📊 统计摘要

- **总文件数**: 543
- **被引用文件数**: 519
- **未被引用文件数**: 24
- **未使用的导入数**: 13

## 🔴 未被引用的文件

> ⚠️ 以下文件在项目中没有被其他文件直接或间接引用，请手动确认是否需要保留。
> 入口文件（如 main.tsx, App.tsx）通常不会被其他文件引用，这是正常的。

### 📁 components (1 个文件)

- [ ] `components/I18nDemo.tsx`

### 📁 components/Permission (1 个文件)

- [ ] `components/Permission/index.ts`

### 📁 components/RichTextEditor (2 个文件)

- [ ] `components/RichTextEditor/context/SettingsContext.tsx`
- [ ] `components/RichTextEditor/plugins/ToolbarPlyginType.ts`

### 📁 components/RouteGuard (1 个文件)

- [ ] `components/RouteGuard/index.tsx`

### 📁 components/SearchTable (1 个文件)

- [ ] `components/SearchTable/AddFolderModal.tsx`

### 📁 components/SimplePermissionButton (1 个文件)

- [ ] `components/SimplePermissionButton/index.tsx`

### 📁 constants (1 个文件)

- [ ] `constants/developmentFeatures.ts`

### 📁 models/content (1 个文件)

- [ ] `models/content/categoryModelData.ts`

### 📁 models/seo (6 个文件)

- [ ] `models/seo/redirectCreate.ts`
- [ ] `models/seo/redirectDelete.ts`
- [ ] `models/seo/redirectExportTemplate.ts`
- [ ] `models/seo/redirectImport.ts`
- [ ] `models/seo/redirectList.ts`
- [ ] `models/seo/redirectUpdate.ts`

### 📁 models/users (1 个文件)

- [ ] `models/users/getRolePermissions.ts`

### 📁 pages/seo (1 个文件)

- [ ] `pages/seo/components/PlaceholderInputLexical/lexical/selectionPath.ts`

### 📁 pages/setting (1 个文件)

- [ ] `pages/setting/Setup/Advanced/constants/systemPresets.ts`

### 📁 store (1 个文件)

- [ ] `store/menuUtils.ts`

### 📁 tools (1 个文件)

- [ ] `tools/oauthTokenManager.ts`

### 📁 utils (4 个文件)

- [ ] `utils/buttonPermissionUtils.ts`
- [ ] `utils/memberLevelCache.ts`
- [ ] `utils/menuUtils.ts`
- [ ] `utils/videoRangeCheck.ts`

## 🟡 未使用的导入

> 以下导入语句在文件中没有被使用。

#### `hooks/useMemberLevelsData.ts`

- `MemberLevel` from `@/models/member/memberLevels`

#### `models/console/updateModelData.ts`

- `CreateAppModelDataStatus` from `@/models/console/createModelData`

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

#### `pages/resource-library/enterpriseResource.tsx`

- `SvgIcon` from `@/components/IconFont/SvgIcon`

#### `pages/seo/components/PlaceholderInputLexical/lexical/TagKeyboardPlugin.tsx`

- `$isTagNode` from `../TagNode`

#### `pages/setting/RecycleBin/ResourceRecycleBin/utils.ts`

- `BusinessCode` from `@/constants/businessCode`

## 📈 被引用最多的文件 (Top 20)

| 文件 | 引用次数 |
|------|----------|
| `models/apis.ts` | 177 |
| `hooks/useAxios.tsx` | 118 |
| `models/setting/settingDictionary.ts` | 83 |
| `models/seo/templateUpdate.ts` | 78 |
| `models/seo/appsPages.ts` | 78 |
| `models/seo/templateReset.ts` | 78 |
| `models/seo/urlRules.ts` | 78 |
| `models/seo/advancedSettings.ts` | 78 |
| `models/seo/urlRedirect.ts` | 78 |
| `models/seo/lowcodeLabels.ts` | 78 |
| `models/seo/otherAppVariables.ts` | 78 |
| `models/seo/index.ts` | 78 |
| `models/seo/templateVariables.ts` | 78 |
| `models/seo/metaVariables.ts` | 78 |
| `models/seo/templateList.ts` | 78 |
| `models/seo/redirectBatch.ts` | 78 |
| `models/seo/recommendedVariables.ts` | 78 |
| `models/seo/templateDetail.ts` | 78 |
| `models/resourceLibrary/resourceCapacity.ts` | 78 |
| `models/resourceLibrary/resourceUpdate.ts` | 76 |
