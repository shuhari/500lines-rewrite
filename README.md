# 500 Line or Less (Rewritten)

- [Readme in English](#english-readme)
- [中文自述](#chinese-readme>)

## Status

This project is working in progress.

| Project | Status |
|---------|--------|
| editorial |  |
| byterun |  |
| spreadsheet |  |
| contingent |  |
| object model |  |
| Image Filter app |  |
| flow-shop |  |
| same-origin-policy |  |
| contingent |  |
| dagoba |  |
| Pedometer |  |
| blockcode |  |
| cluster |  |
| Modeller |  |
| same-origin-policy |  |
| web-server | Done |
| crawler |  |
| sampler |  |
| static analysis | Done |
| event-web-framework |  |
| ci | Done |
| ocr |  |
| templating engine | Done |
| same-origin-policy |  |
| data-store |  |
| In-memory functional database |  |


<a name="english-readme"/>

## Readme in English

This is rewritten of original project [500 Lines or Less](https://github.com/aosabook/500lines) with improvements in the following aspects:

- Code written in `PY2` are rewritten in `PY3`
- Remove some outdated content (e.g CGI) and replace with newer mechanism. For example, HTTP processing pipeline are introduced instead of `CGI`
- Written in a step-by-step manner, showing actual code for each step, so we can see how to make progress
- Some projects are developed in a test-driven (TDD) manner

Project relatived articles are published at [My blog](https://shuhari.dev/blog/2020/05/500lines-rewrite-intro), in Chinese language.
 
### How to Use

To run the program code, you need

- `Python3`. Any version higher than `Python3.6` should work (however not verified). The development environment is `Python3.8`.

Code of each project is in a separated directory, naming after [the original project](https://github.com/aosabook/500lines). Some whitespace and `-` character are replaced with `_` for the sake of references in code. Each step has also its own sub-directory.

To run a projects written in Python: open `main.py`, find the entry point for the project of interest, uncomment it and run.


<a name="chinese-readme"/>

## 中文自述

本项目试图以更加现代化的方式重写 [500 Lines or Less](https://github.com/aosabook/500lines) 项目，并在以下方面有所改进：

- 将基于 `PY2` 的项目改写为基于 `PY3`
- 删除部分过时的内容，用更适合现实的机制代替。例如，`CGI` 被 HTTP 处理管线替代
- 用循序渐进的方式编写代码，展示每个具体步骤，让读者能够更好地理解
- 部分项目采用测试驱动（TDD）的方式开发。

项目相关的介绍文章发布在 [作者的博客](https://shuhari.dev/blog/2020/05/500lines-rewrite-intro).
 
### 如何使用

要运行程序代码，需要

- `Python3`。理论上任何高于 Python3.6 的版本均可（但未验证）。实际开发环境是 Python3.8

各个项目分别放在不同的目录下，命名方式遵照原先的名称，为了方便引用，部分空格或 `-` 用 `_` 替代。对于使用迭代式开发的项目，每个步骤放在单独的目录下。

对于用 `Python` 实现的项目，请访问 `main.py`， 找到特定的项目以及步骤编号，取消注释并运行。

