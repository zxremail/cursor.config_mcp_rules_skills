# REA 还原仓库 — 参考

## 推荐目录（模块化）

```text
<git-root>/
├── README.md                 # 产物身份、如何构建（若可）、模块索引
├── .gitignore
├── docs/
│   ├── MODULES.md            # 模块表：职责、依赖、公开 API
│   ├── evidence-index.md     # Evidence ID → 模块/符号 映射
│   └── unknowns.md           # 未决行为；链接 REA Unknown 条目
├── src/
│   ├── <module-a>/           # 一子系统一包
│   │   ├── include/          # C/C++ 可选
│   │   └── ...
│   └── <module-b>/
├── reference/                # 默认整树 ignore（见下）
│   └── decompiled/
│       └── <module-a>/       # REA/Ghidra 原始伪代码快照
└── architecture.html         # 可选；见 rea-architecture-html
```

### 模块命名

| 类型 | 建议 |
|------|------|
| Native `.so` | 按导出簇或源路径字符串聚类：`gpio/`, `i2c/`, `factory/` |
| APK | `app/`, `service/<name>/`, `jni/<lib>/` 与 manifest 组件对应 |
| Managed DLL | 与命名空间或程序集子域一致：`Rigol.PisDao.License/` |
| 共享工具 | `common/`, `platform/` — 禁止复制粘贴三份相同 helper |

### 依赖规则

- `src/` 内 **禁止** 循环依赖；`common` 不得 import 业务模块。
- 跨模块只通过 **公开头文件 / public API 文件**；内部符号加 `static` 或 `internal`。
- 新建模块时更新 `docs/MODULES.md` 一行依赖说明。

## `.gitignore` 基线（复制后按目标增减）

```gitignore
# --- REA / 反编译引擎（可再生、体积大）---
*.gpr
*.rep
*.lock
*.idb
*.i64
*.id0
*.id1
*.id2
*.nam
*.til
ghidra_projects/
.rea/
rea-export/

# --- 原始反编译快照（Git 跟踪清洗后的 src/）---
reference/decompiled/

# --- 二进制与打包证据（默认不跟踪；用户明确要求时再移除对应行）---
*.so
*.dll
*.exe
*.apk
*.aab
*.zip
*.7z
*.bin
export_evidence_bundle/

# --- 构建与 IDE ---
bin/
obj/
build/
out/
.vs/
*.user
*.suo

# --- 日志与临时 ---
*.log
**/log/
*.tmp
*~
```

### 持续优化检查表（每批次勾 mentally）

- [ ] 是否新建了引擎工程目录？→ 加 ignore + commit
- [ ] 是否下载/导出了 >10MB 且非用户要求入库的文件？→ ignore 或放仓外
- [ ] 是否应跟踪 `docs/*.md` 与 `src/**`？→ **不要** ignore
- [ ] 是否误 ignore 了已 commit 文件？→ 改 ignore + `git rm --cached` + 说明 commit

## Commit message

### 合格标题

- `recon(license): 还原 OperID 12/22 分支与 DAO 调用链`
- `chore(gitignore): 忽略 Ghidra .rep 与 rea-export 目录`
- `docs(modules): 拆分 VISA 与 PDM 为独立模块并更新依赖`

### 不合格标题

- `2026-11-06 15:00`
- `update`
- `save decompiled`
- `WIP`
- `auto commit by agent`

### 类型前缀

| 前缀 | 用途 |
|------|------|
| `recon(<module>)` | 新增或实质修改还原源码 |
| `refactor(<module>)` | 仅结构/命名，行为意图不变 |
| `fix(<module>)` | 与 Evidence 对齐修正 |
| `docs` | MODULES / unknowns / evidence-index |
| `chore(gitignore)` | 仅 ignore 或缓存清理策略 |

## 单模块最小交付

1. `src/<module>/` 至少一个公开入口文件 + 实现
2. `docs/evidence-index.md` 中该模块 ≥1 条 Evidence 引用
3. 一条 `recon(<module>): ...` commit
4. working tree 无该模块的未提交已完成文件
