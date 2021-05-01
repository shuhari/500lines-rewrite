# 500 Line or Less (Rewritten)

- [Readme in English](#english-readme)
- [中文自述](#chinese-readme)

## Status

This project is working in progress.

| Project | Origin Article | Blog Article | Status |
|---------|--------|----------------|--------------|
| blockcode |  |  |  |
| ci | [A Continuous Integration System](http://aosabook.org/en/500L/a-continuous-integration-system.html) | [rewrite-ci](https://shuhari.dev/blog/2020/06/500lines-rewrite-ci) | Done |
| cluster |  |
| contingent | [Contingent: A Fully Dynamic Build System](http://aosabook.org/en/500L/contingent-a-fully-dynamic-build-system.html) | [rewrite-contingent](https://shuhari.dev/blog/2021/02/500lines-rewrite-contingent) | Done |
| crawler |  |
| dagoba |  |
| data-store | [DBDB: Dog Bed Database](http://aosabook.org/en/500L/dbdb-dog-bed-database.html) |  | Working |
| editorial |  |
| event-web-framework |  |
| flow-shop |  |
| functionaldb |  |
| image-filters |  |
| interpreter |  [A Python Interpreter Written in Python](http://aosabook.org/en/500L/a-python-interpreter-written-in-python.html) | [rewrite-interpreter](https://shuhari.dev/blog/2020/12/500lines-rewrite-interpreter) | Done |
| modeller |  |
| objmodel | [A Simple Object Model](http://aosabook.org/en/500L/a-simple-object-model.html) | [rewrite-objmodel](https://shuhari.dev/blog/2020/06/500lines-rewrite-objmodel) | Done |
| ocr |  |
| pedometer |  |
| same-origin-policy |  |
| sampler |  |
| spreadsheet |  |
| static analysis | [Static Analysis](http://aosabook.org/en/500L/static-analysis.html) | [rewrite-static-analysis](https://shuhari.dev/blog/2020/07/500lines-rewrite-static-analysis) | Done |
| templating engine | [A Template Engine](http://aosabook.org/en/500L/a-template-engine.html) | [rewrite-template-engine](https://shuhari.dev/blog/2020/05/500lines-rewrite-template-engine) | Done |
| web-server | [A Simple Web Server](http://aosabook.org/en/500L/a-simple-web-server.html) | [rewrite-web-server](https://shuhari.dev/blog/2020/05/500lines-rewrite-web-server) | Done |


<a name="english-readme"/>

## Readme in English

Rewritten of original project [500 Lines or Less](https://github.com/aosabook/500lines) with improvements in the following aspects:

- Code written in `Python2` are rewritten in `Python3`
- Replace some of the outdated content with newer mechanism. For example, HTTP processing pipeline are introduced instead of `CGI`
- Written in a step-by-step manner, showing actual code for each step, so we can see how to make progress
- Some of the projects are developed in a test-driven (TDD) manner

Project relatived articles are published at [My blog](https://shuhari.dev/blog/2020/05/500lines-rewrite-intro), in Chinese language.
 
### How to Use

To run the program code, you need

- `Python3`. Any version higher than `Python3.6` should work (not verified, however). Current development environment is `Python3.8`.

Code of each project is in a separated directory, naming after [the original project](https://github.com/aosabook/500lines). Whitespace or hyphen(`-`) are replaced with underline(`_`) for the sake of references in code. For thosed developed in a step-by-step manner, each step also has its own sub-directory.

To run a projects written in Python: open `main.py` in project root, find the entry point for the project of interest, uncomment it and run.


<a name="chinese-readme" />

## 中文自述

本项目试图以更加现代化的方式重写 [500 Lines or Less](https://github.com/aosabook/500lines) 项目，并在以下方面有所改进：

- 将基于 `Python2` 的项目改写为基于 `Python3`
- 删除部分过时的内容，用更适合现实的机制代替。例如，`CGI` 机制换成了 `HTTP` 处理管线
- 用循序渐进的方式编写代码，展示每个具体步骤，让读者能够更好地理解
- 部分项目采用测试驱动（`TDD`）的方式开发。

项目相关的介绍文章发布在 [作者的博客](https://shuhari.dev/blog/2020/05/500lines-rewrite-intro).
 
### 如何使用

要运行程序代码，需要

- `Python3`。理论上任何高于 Python3.6 的版本均可（但未验证）。目前使用的开发环境是 Python3.8

各个项目分别放在不同的目录下，命名方式遵照原先的名称，为了方便在代码中引用，部分空格或连字符(`-`)用下划线(`_`) 替代。对于使用迭代式开发的项目，每个步骤放在单独的目录下。

对于用 `Python` 实现的项目，请打开项目根目录下的 `main.py`， 找到特定的项目以及步骤编号，取消注释并运行。
