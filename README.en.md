# purplegold-init

[中文](README.md)

An AI skill that initializes your project with the **Purple Gold (紫金规范)** specification.

Purple Gold is a software engineering specification for the new paradigm of **human–AI collaboration**. Its core idea is **everything is a document**: documents — not code — are the project's primary asset. Even if all code is lost, the project can be quickly rebuilt from its Purple Gold documents.

## The spec at a glance

### Exoskeleton spec: modules and ALLOY documents

The Exoskeleton spec governs all modules in the engineering tree and their relations; it is read and maintained by AI:

- **Module recognition**: any file or folder playing an independent role is a module. Every folder module has exactly one **ALLOY document** (`ALLOY.md` inside it), created, updated, moved, and deleted together with the module.
- **ALLOY document**: a fixed format with seven required sections — module summary, child-module pointers, internal relations, boundary relations, parent pointer, interface & behavior contracts; internal relations use a strict mermaid subset as the single authoritative representation of dependencies.
- **Dependency rules**: dependencies only between sibling modules, always acyclic; cross-level dependencies are expressed as dependencies between parent modules instead.
- **Script-enforced consistency**: `align.py` aggregates module information into the root module's derived zone (project-wide module index, relation overviews); `validate.py` checks that documented declarations match the actual directory structure — work cannot be wrapped up while checks fail.

### Endoskeleton spec: the Spine process (eight stages)

The Spine process is the main line of a project's design and development work, eight stages in order; stage outputs go to `紫金产物/脊椎产物/`:

| Stage | Focus | Main outputs |
|---|---|---|
| S01 需求确认 | Nail down requirements | Requirements checklist, constraints & non-functional requirements, user roles, glossary |
| S02 功能初步设计 | Features & business flows | Feature list, business flow descriptions, scope statement (optional: use cases) |
| S03 功能交互设计 | Pages & interaction | Page list, page-flow diagram, per-page interaction descriptions, user paths, empty/error states |
| S04 UI 视觉设计 | Visual design | UI design brief (optional), visual drafts, design standards, component list, asset list |
| S05 工程架构与契约 | Technical solution | Tech selection rationale, module architecture, data models, interface & behavior contracts, external services list |
| S06 制定开发计划 | Tasks & schedule | Task breakdown, ordering & milestones, completion criteria, assignment notes |
| S07 开发和测试 | Implementation | Code, engineering test records, deviation records |
| S08 实机测试和验收 | Real-environment acceptance | Test plan, case library, test report (with screenshots), defect list, acceptance checklist |

The Spine process is the project's root driving force: stage outputs may change, but any change triggers a sequential back-flow review of all other stages.

### Endoskeleton spec: the Rib specs (thirteen built-in)

Rib specs are flexible, non-linear rules: executed when their trigger arrives, or enabled on demand by human engineers; instances may trim or add specs. Class A has automatic triggers (AF = ahead of the Spine, outputs feed the Spine process; AB = behind the Spine, registering and maintaining records based on Spine outputs); class M has no automatic trigger and is enabled manually:

| No. | Spec | In one line |
|---|---|---|
| AF01 | 提示词节点 | Record every prompt as a node (index, timestamp, original text, notes) |
| AF02 | 需求基线 | Update the requirements baseline and its change log before anything else whenever input contains requirements — the ultimate source of all requirements |
| AB03 | 项目最新状态 | On any status change, update the three status documents (Spine progress, Rib progress, exoskeleton implementation); latest state only |
| AB04 | 脊椎产物变更记录 | Append a record (with back-flow review conclusion) for every Spine-output change |
| AB05 | 需求追溯表 | Maintain the mapping: requirement → feature → page → module → task → test case |
| AB06 | 美术素材备份 | Back up originals and derived variants of newly referenced art assets, with an asset list |
| M01 | 部署和运维 | Deployment and operations, enabled by human decision |
| M02 | 修复和优化 | Record each fix/optimization session; functional fixes must be retested |
| M03 | 上架 | Store-release management for store-distributed projects (mobile apps, mini programs) |
| M04 | 工作量评估 | Fixed-formula effort estimation for pricing and macro scheduling |
| M05 | 甲方原始文件 | Collect client-provided original files into timestamped folders |
| M06 | 对外文档 | Manage four client-facing documents (MD authoritative, DOCX derived) |
| M07 | 账号密码管理 | Central registry of project accounts and passwords (plaintext; requires a private repo) |

### Iterator: versions and upgrades

A project pins its spec version in `purplegold/VERSION`; upgrading = replacing `purplegold/` with the new instance template and migrating `紫金产物/` per the change record.

## What this skill does

Runs Purple Gold initialization in the current project:

1. Ensures the project root is a Git repository root (`git init` if needed);
2. Copies the bundled instance template, creating `purplegold/` (static rules layer) and `紫金产物/` (dynamic documents skeleton);
3. Writes the spec version, creates the engineering root `project/` and the root-module ALLOY document `project/ALLOY.md`;
4. Adds an entry pointer to `purplegold/RULES.md` in `AGENTS.md`;
5. Runs the alignment and validation scripts — initialization only completes when all checks pass.

This skill is **self-contained**: the instance template, scripts, and spec version (`VERSION`) are bundled, so initialization works fully offline.

Note: the spec documents are written in Chinese; the initialized project's working documents are Chinese as well.

## Install

```bash
npx skills add wangfujian762/purplegold-init
```

Or manually: copy this repository's contents into a `purplegold-init/` folder in your skills directory (e.g. `~/.agents/skills/purplegold-init/`).

## Usage

Prerequisites: `git` available at the project root; Python 3 (for the alignment and validation scripts).

In your project root, tell the AI:

> Initialize this project with the Purple Gold spec (紫金规范).

The agent reads `SKILL.md` and executes the procedure. After initialization, AI agents in the project enter `purplegold/RULES.md` via `AGENTS.md` and work according to the spec; the Spine process starts at stage `S01-需求确认`, and `紫金产物/肋骨产物/AB03-项目最新状态/脊椎流程进展.md` serves as the project's macro todo list.

## Project structure after initialization

```
<project root>/
├── AGENTS.md       # AI entry pointer
├── purplegold/     # Static rules layer: rules, templates, scripts, Spine and Rib specs
├── 紫金产物/        # Dynamic documents layer: documents produced by the project
└── project/        # Engineering root: the module tree, ALLOY documents co-located
    └── ALLOY.md    # Root-module ALLOY document
```

## Learn more

All detailed rules live in the bundled instance template (and, after initialization, in your project):

- `实例模板/purplegold/RULES.md` — the distilled rules: the AI's operating manual (module recognition, ALLOY document format, Spine process, Rib specs, status documents)
- `实例模板/purplegold/脊椎规范/`, `实例模板/purplegold/肋骨规范/` — per-stage and per-process spec documents
- `VERSION` — the Purple Gold spec version bundled in this skill

## Feedback

- Defects and suggestions about the spec: write them in your project's `紫金产物/规范反馈.md` (the instance-to-origin feedback channel), or open an Issue in this repository.

## License

[MIT](LICENSE)
