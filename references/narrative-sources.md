# 叙事模块的方法来源与试读范围

2026-11-10（Asia/Shanghai）通过 GitHub 连接器发现候选，并用 GitHub REST API 核验公开星数和许可证。数字属于整个仓库，不是单个技能的关注数，也不是质量评价。

| 来源 | 核验星数 | 固定版本 | 许可与采用范围 |
|---|---:|---|---|
| [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) 的 [ml-paper-writing](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/773a52944ba4747a18bd4ae9ade53fff041adcbc/20-ml-paper-writing/ml-paper-writing/SKILL.md) | 14,395 | `773a52944ba4747a18bd4ae9ade53fff041adcbc` | MIT；采用明确主张、支撑证据和读者意义的叙事骨架，及先给熟悉信息再引入新概念的写法 |
| [wshobson/agents](https://github.com/wshobson/agents) 的 [data-storytelling](https://github.com/wshobson/agents/blob/9c61ab243def98f72da12abd41cfcf5bcd91af9d/plugins/business-analytics/skills/data-storytelling/SKILL.md) | 42,369 | `9c61ab243def98f72da12abd41cfcf5bcd91af9d` | MIT；采用情境—张力—发现的顺序及匹配听众语言的原则 |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) 的 [scientific-writing](https://github.com/K-Dense-AI/scientific-agent-skills/blob/2d2065fb4520fa3f3f2bcf61cff26ec8b7eba4b5/skills/scientific-writing/SKILL.md) | 56,616 | `2d2065fb4520fa3f3f2bcf61cff26ec8b7eba4b5` | MIT；比较候选，偏投稿与证据审计，未完整试用或额外引入其投稿流程 |

对 Orchestra 的 What / Why / So What 应作准确理解：What 是主张，Why 是支持主张的证据理由，So What 是意义；研究动机另行解释。reading-papers 的六个叙事问题是在论文学习场景中的适配，不能把上述技能原本用于投稿或商业演示的步骤全部套入。

## 本地应用测试

两份试读使用同一篇用户提供的 Anthropic 论文 *Who’s Aligned to Whom? How AI Agents Shape Experts’ Research Judgment Calls*。同一 AI 系统先分别读取固定版本技能，按其中与叙事相关的条款写出中文说明，再核对原文。没有调用其他模型 API，没有运行第三方代码，没有真实学习者测试，不能称作跨模型验证或泛化性能评测。

试读观察支持有限整合：Orchestra 的骨架使核心主张与证据容易核对；data-storytelling 的组织方式使“专家最后签字”到“中间选择如何形成”的问题更好理解。两者均需改编：不从“最亮眼的数字”代替主要估计；不删除真实不确定性；不把未检验建议写成解决方案；不为制造转折而漏掉不显著结果。

最终模块保留一句话主线、短讲、连贯故事、章节作用表、易误读点和复述题。关键限定跟随对应证据出现。例稿区分 72 个百分点的组间差、86% 的一致率与 82% 的探索性样本内预测，且不把不同案例拼成同一人的经历。

本地研究记录位于原工作区的 `论文阅读Skills/叙事候选测试/`，含公开元数据、下载哈希、两份试读、筛选结论和融合稿。技能运行不依赖该工作区目录，也不依赖联网查这些仓库；方法要求已整理于 [narrative.md](narrative.md)。发布或携带本 skill 时保留对应第三方许可证与来源归属。

这次检索没有找到兼具高星和“单篇论文通俗叙事”专门定位、可以直接无改动使用的方案。两项名字更贴近的 `StatXzy7/paper-storycraft`、`LINBIEXU/warm-paper-story` 核验时均为 0 星；没有把它们包装为高星推荐。后续更新时重新核验来源，不能沿用此处星数当作实时值。
