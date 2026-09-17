# purplegold-init

用紫金规范（Purple Gold）初始化你的项目的 AI skill。安装后，AI Agent 可将紫金规范落地到任意项目：复制实例模板、建立 `purplegold/` 与 `紫金产物/` 骨架、生成根模块合金文档并通过校验。

本 skill 为自含包：内置实例模板、脚本与规范版本号，初始化全程离线可用。当前内置规范版本见 `VERSION`。

紫金规范是一套面向"人与 AI 协作"新工程形态的软件工程规范，详见主仓库：[wangfujian762/purplegold](https://github.com/wangfujian762/purplegold)。

## 安装

```bash
npx skills add wangfujian762/purplegold-init
```

或手动安装：把本仓库内容复制到你的 skills 目录下的 `purplegold-init/` 文件夹（如 `~/.agents/skills/purplegold-init/`）。

## 使用

在你的项目根目录（须为或将成为 Git 仓库根）对 AI 说：

> 用紫金规范初始化本项目。

Agent 会读取 `SKILL.md` 并执行初始化流程。初始化完成后，项目中的 AI 将按 `purplegold/RULES.md` 工作。

## 协议

[MIT](LICENSE)
