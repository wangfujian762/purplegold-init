# purplegold-init

[中文](README.md)

An AI skill that initializes your project with the **Purple Gold (紫金规范)** specification.

Purple Gold is a software engineering specification for the new paradigm of **human–AI collaboration**. Its core idea is **everything is a document**: documents — not code — are the project's primary asset. Even if all code is lost, the project can be quickly rebuilt from its Purple Gold documents.

## The spec at a glance

- **Exoskeleton spec**: the module system of the project. Every module has an ALLOY document (`ALLOY.md`) recording its summary, dependencies, boundary relations, and interface contracts; alignment and validation scripts keep documents and directory structure consistent. Read and maintained by AI.
- **Endoskeleton spec**: how humans and AI drive engineering forward together. The main line is the eight-stage **Spine process** (requirements → feature design → interaction design → UI visual design → architecture & contracts → development planning → development & testing → acceptance); the supporting line is the **Rib specs** (requirements baseline, change records, deployment & operations, effort estimation, and more — thirteen initial specs). Read and maintained by human engineers.
- **Iterator**: versioning and upgrade rules of the spec itself. A project pins its spec version in `purplegold/VERSION`; upgrading = replacing the static rules layer + migrating the dynamic documents layer.

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
