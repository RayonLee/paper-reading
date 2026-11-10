# paper-reading

把一篇论文变成八种互补视角的学习材料，每个模块有独立文件夹，统一生成可离线打开的 HTML。包含独立的“论文叙事”：用通俗语言讲清作者面对什么问题、为什么这样研究、证据怎样推进论证，以及结论在哪停止。

仓库与技能名称统一为 `paper-reading`，仓库地址为 [RayonLee/paper-reading](https://github.com/RayonLee/paper-reading)。

## 交给其他 AI 使用

把整个 `paper-reading` 文件夹复制给能读取文件、执行 Python 的 AI 工具，然后这样说：

> 请先阅读 paper-reading/SKILL.md，按该流程分析这篇 PDF。用中文生成全部八个模块，使用随附脚本校验并渲染 HTML；给我开始阅读.html 的位置。

支持 Agent Skills 的工具可将整个文件夹放入该工具的技能目录。Codex 可用 `$paper-reading` 显式调用；其他工具的具体安装位置以其文档为准。不支持技能自动发现的 AI 也能直接读取 `SKILL.md` 执行。

只有聊天能力、无法读本地文件或执行脚本的 AI，可以先按 `references/content-format.md` 生成 JSON，再在本机运行渲染命令。脚本固定目录和页面样式，论文解读仍由调用它的 AI 完成，不需要本项目专属 API 密钥。

## 从旧名称迁移

原 `reading-papers` 现更名为 `paper-reading`。安装时将技能文件夹命名为 `paper-reading`，Codex 的调用名称相应改为 `$paper-reading`。已有安装可先备份旧文件夹，再替换为新版本。

主脚本现为 `scripts/paper_reading.py`；旧的 `scripts/reading_papers.py` 保留为兼容命令入口。已生成的学习材料仍可继续阅读和重新渲染。

## 可重复的命令

在 `paper-reading` 文件夹中执行。将示例路径替换成实际路径；路径有空格时保留引号。

```sh
python3 scripts/paper_reading.py init --paper "/path/paper.pdf" --out "/path/paper-study" --title "论文标题"
python3 scripts/paper_reading.py extract --pdf "/path/paper.pdf" --out "/path/paper-study/00_原文与索引/pages.json"
```

初始化需要 PDF 页数：已有 pypdf 或 PyMuPDF 时可自动检测；没有这些库时可查看 PDF 阅读器并为 `init` 加 `--pages 29` 之类的实际页数。`extract` 需要已安装的 pypdf 或 PyMuPDF，也可以换用 AI 环境自己的 PDF 读取工具。提取文本不会自动生成学习报告，扫描件还需 OCR 或视觉读取。

AI 阅读原文、建立证据记录、填写每个模块的 `content.json` 并完成审读后运行：

```sh
python3 scripts/paper_reading.py validate --out "/path/paper-study"
python3 scripts/paper_reading.py render --out "/path/paper-study"
```

只生成叙事等局部内容时，可用 `validate --out "/path/paper-study" --modules 08`；它只校验指定模块，并明确整套尚未完成。

打开输出中的 `开始阅读.html`。修改内容时编辑 JSON，再重复校验与渲染，无须重写页面。浏览器打印功能可另存 PDF。渲染器只用 Python 3.10+ 标准库，页面不依赖 CDN、在线字体、前端构建工具或模型接口。

## 输出与可迁移性

- `00_原文与索引`：原始 PDF、来源校验信息、AI 编写的证据账本和审读记录。
- `01` 至 `08`：各模块的 `content.json`、`学习报告.html`，必要时附表格、图像或补充报告。
- `开始阅读.html`：统一导航。建议顺序为论文叙事 → 快速泛读 → 原文导读 → 方法精读 → 其他视角。

移动或分享结果时复制整篇论文的输出文件夹，以保持本地原文链接完整。技能 ZIP 只包含通用规则、脚本和资源，不包含用户论文或 API 密钥。HTML 中论文页码链接到副本 PDF；公式使用纯文本及可选的核对过的公式图，方便离线阅读。不同浏览器对 PDF 页码跳转支持可能不同，可按标注页码手动定位。

八模块指同一 AI 的八种工作方式，不能据此声称获得八位专家或八个模型的独立验证。自动校验不等于事实核查。文献综述模块默认是单篇文献定位，只有实际检索并记录过程时才报告外部检索结果。

## 本次验收范围

此次用 Anthropic 论文的七份已审读材料测试迁移与统一渲染，保留原逐段导读；另外对论文叙事候选进行了新试读和整合，并让另一任务代理从原PDF实际完成一次仅叙事模块的前向测试。结构测试覆盖5类行为，且已实际检查桌面与手机页面、图片加载和本地链接。具体试读依据、仓库星数采集日期与整合决策见 `references/narrative-sources.md`。这里不声称测试过其他厂商模型或复现了论文原始实验。

2026-11-10 又使用 *Does Virtual Reality Help Property Sales? Empirical Evidence from a Real Estate Platform*（用户提供的2024年版本）从原PDF完成八模块试用。逐段导读含97段正文、13条尾注、24道自测；检查了9个页面的桌面与手机布局、854处本地引用，并有限补核出版社附录B/C/F/G/H/I的有关文本。未重跑原始数据，未完成全附录图像核验，未实测学习者表现或其他模型的效果。论文PDF与个人学习产物不属于本仓库内容。

## 开发检查

```sh
python3 -m unittest discover -s tests -v
```

测试覆盖完整渲染与转义、缺失模块、局部校验、路径边界，以及页码/段落ID/占位符/源文件哈希检查。它们检验工具行为，不能验证论文解读是否正确。

## 来源与授权说明

方法来源和分发边界见 [origins.md](references/origins.md)，叙事模块来源与试读范围见 [narrative-sources.md](references/narrative-sources.md)。`third-party-licenses/` 保留对应来源的许可证。本项目新增的技能说明、脚本与样式采用 [MIT License](LICENSE)。第三方材料保留各自的版权声明与许可证；本项目的 MIT 授权不改变上游项目的许可。
