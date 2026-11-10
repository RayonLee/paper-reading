# 方法来源、版本与整合范围

`reading-papers` 把已有阅读方法的用途分开，再以共用证据记录和统一渲染串联。各模块说明为本次整合重新编写的执行契约，不表示逐一调用了七个外部服务，也不表示完整复刻上游全部功能。来源快照取自本工作区 2026-11-06 下载记录，许可证于 2026-11-10 对照本地文件核查。

| 来源 | 已核查版本或提交 | 本技能采用的工作思路 | 本地许可证情况 |
|---|---|---|---|
| [Imbad0202/academic-research-skills-codex](https://github.com/Imbad0202/academic-research-skills-codex) | 3.24.2；`82725acb393c4410ac6f47634a7f51b40a162fa4` | 问题、设计、证据、贡献与反方解释相互对照；说明实际执行范围 | 根目录与 vendored ARS 许可证均为 CC BY-NC 4.0，版权署名 Cheng-I Wu (2026) |
| [Liangzhen-Chen/literature-guide-read](https://github.com/Liangzhen-Chen/literature-guide-read) | changelog 0.8.0；`f47dbd8a5ca7d5568b60c2d8da53125257f9e2c9` | 稳定分段、原文锚点、逐段解释、公式和图表、回忆题、语义二读、离线 HTML | MIT，literature-guide-read contributors (2026)；其 KaTeX 另有随附许可证 |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) / scientific-critical-thinking | skill 1.5；仓库 `a25cf9ec00e2745d03f8704acf6f6919694ccd9a` | 固定评估对象和单位；先取证再判断；区分偏倚、报告和证据确定性 | MIT，K-Dense Inc. (2025) |
| 同仓库 / literature-review | skill 1.11；同一提交 | 单篇定位与正式综述分开；主题综合、检索记录、研究与报告区分、引用核验 | MIT，K-Dense Inc. (2025) |
| [Zero-stargazer/deep-paper-reading-skill](https://github.com/Zero-stargazer/deep-paper-reading-skill) | 未声明版本号；`1a09e86235f4c64fa6b31a14c285e631ced923da` | 主张证据矩阵、图表审查、导师问题、待核查和组会交接 | MIT，Zero-stargazer (2026) |
| [superiony/Paper-Reading-Skills](https://github.com/superiony/Paper-Reading-Skills) / skimming-reading | 未声明版本号；`f87d235daa6869dd3b5c4a53f2536a26950b9eaf` | 从研究骨架入手决定精读位置 | 所下载完整快照未见许可证，SKILL.md 未含标准 frontmatter |
| 同仓库 / in-depth-reading | 同一提交 | 从方法、公式和实现流程深入理解；按学科适配细节 | 同上；作为阅读思路来源，不打包转发其文本 |

## 分发边界

- 不把 ARS 完整包和未明确许可的阅读清单嵌入本综合包；本地原下载仍是单独来源。ARS 的授权条款不因本技能做了整合而消失，不能将上游原文或脚本重新标为 MIT。
- 若附带 `literature-guide-read` 的脚本、参考文件或资源，保留其原许可证、版权和版本来源；KaTeX 等第三方依赖也保留各自声明。依赖不需要因宿主不同而重写。
- 上游名称用于归因和说明来源，不表示上游作者审阅或背书了本次整合。仓库 star 数用于发现候选，不能当作分析质量、可靠性或学习效果验证。
- 本技能可在不同 AI 宿主中采用相同输入/输出契约与渲染脚本，但不同模型的分析内容仍需各自核查。

## Scientific Agent Skills 的研究引用

Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*. arXiv. [https://doi.org/10.48550/arXiv.2609.00065](https://doi.org/10.48550/arXiv.2609.00065).

于 2026-11-10 查看 [arXiv 记录](https://arxiv.org/abs/2609.00065)：作者如上，记录当前版本为 v2，页面未列出期刊发表记录。引用使用无版本后缀 DOI。该文章说明技能库的结构和文档评估，不能作为本次论文学习效果已获验证的证据。

## 本次整合新增

共享证据记录、八模块固定目录、统一内容数据和离线 HTML 渲染契约、跨模块一致性核查，以及“通俗故事 + 叙事地图 + 证据边界”的论文叙事模块。叙事候选的在线检索、实际试读与采用决定另见本次候选测试记录；这里只列已经核查的原七种方法来源。
