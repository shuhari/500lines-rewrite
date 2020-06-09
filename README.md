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
| static analysis |  |
| event-web-framework |  |
| ci | Working... |
| ocr |  |
| templating engine | Done |
| same-origin-policy |  |
| data-store |  |
| In-memory functional database |  |


<a name="english-readme"/>

## Readme in English

This is rewritten of original project [500 Lines or Less](https://github.com/aosabook/500lines) in a In a more modern way:

- Use a new language version, such as Python3 instead of Python2
- Remove some outdated content (e.g CGI) and replace with newer mechanism such as HTTP processing pipeline
- Written in a step-by-step manner, showing actual code for each step, so that the reader can understand it better
- Some projects are developed in a test-driven (TDD) manner

Project relatived articles are published at [My blog](https://shuhari.dev/blog/2020/05/500lines-rewrite-intro).
 
### How to Use

To run the program code, you need

- Python3. Any version higher than Python3.6 should work (but not verified). The development environment is Python3.7.

Code of each project is in a separated directory, naming after [original project](https://github.com/aosabook/500lines). But each step has also its own sub-directory.

For projects that written in Python: open `main.py`, uncomment the Corresponding code and run it.


<a name="chinese-readme"/>

## 中文自述

本项目试图以更加现代化的方式重写 [500 Lines or Less](https://github.com/aosabook/500lines) 项目，并在以下方面有所增强：

- 使用新的语言版本，比如 Python3 取代 Python2
- 去掉部分过时的内容（如 CGI），添加较新的方式如 HTTP 处理管线
- 用循序渐进的方式编写代码，展示每个具体步骤，让读者能够更好地理解
- 部分项目采用测试驱动（TDD）的方式开发。

项目相关的介绍文章发布在 [我的博客](https://shuhari.dev/blog/2020/05/500lines-rewrite-intro).
 
### 如何使用

要运行程序代码，需要

- Python3。理论上任何高于 Python3.6 的版本均可（但未验证）。实际开发环境是 Python3.7

各个项目分别放在不同的目录下，命名方式与 [原项目](https://github.com/aosabook/500lines) 相同，但每个步骤使用独立的目录。

对于用 Python 实现的项目，请访问 `main.py`， 对你关心的项目取消注释并运行。

