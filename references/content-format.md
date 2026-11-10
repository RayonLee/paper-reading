# 可移植内容格式与命令

脚本 `scripts/reading_papers.py` 使用 Python 3.10+ 标准库渲染，不依赖 Node、特定AI API、CDN或网络。PDF文本提取才需要可选的 pypdf 或 PyMuPDF。CSS存于 `assets/style.css` 并嵌入输出HTML。将整个skill文件夹一起复制；不要只复制脚本。

## 命令

以下相对路径均以当前工作目录为准，`SKILL_DIR`指skill根目录。路径有空格时加引号。

```sh
python3 "SKILL_DIR/scripts/reading_papers.py" init --paper "paper.pdf" --out "新输出目录" --title "论文题名" --pages 29
python3 "SKILL_DIR/scripts/reading_papers.py" extract --pdf "新输出目录/00_原文与索引/source.pdf" --out "新输出目录/00_原文与索引/pages.json"
python3 "SKILL_DIR/scripts/reading_papers.py" render --out "新输出目录"
python3 "SKILL_DIR/scripts/reading_papers.py" validate --out "新输出目录"
```

- `init` 创建8个模块的draft骨架，并复制来源PDF、记录SHA-256与页数。拒绝非空输出目录，避免覆盖笔记。若已有PDF库可省略 `--pages`；无库时须从PDF查看器确认实际物理页数后提供，记录会明确是手工指定。若安装了PDF库且手工页数不一致，命令失败。
- `extract` 可选，不会自动安装依赖。输出逐页文本与来源哈希。空页、公式、图表和阅读顺序需要AI对照PDF核查；脚本不做OCR。命令执行失败时使用当前AI已有的PDF读取工具，不据此假装已读。
- `render` 根据合法的complete内容生成报告和入口；未完成模块明确标记为待完成。旧HTML若对应的数据无效会替换成待完成页，避免误读旧结果。渲染成功不等于整套学习报告完成。
- `validate` 必须8份完整数据都通过才退出0。结构或资料错误退出1/2，并保存 `00_原文与索引/validation_report.json`。会检查页码范围、源哈希、局部资产、已知占位符；**不会判断事实和推理是否正确，也不会证明AI真实读过论文**。
- 局部任务使用 `validate --out "输出目录" --modules 08`，多个模块可写 `--modules 02 08`。只检查所选模块，退出0仅表示该范围通过，报告写入 `validation_selected_report.json`，明确 `validation_scope: selected_modules`、`package_complete: false`。不会覆盖完整校验报告；即使选了全部编号，这条局部命令也不宣称整套完成。无 `--modules` 时仍检查全部8个模块，只有全部通过才标记 `package_complete: true`。
- 对既有输出，只编辑各模块内容并重新render/validate，不重新init。

## content.json

每个模块文件夹都有 `content.json`。文件使用UTF-8。所有显示文本都按**纯文本**处理；不要放HTML标签或依赖Markdown语法。脚本会escape文本防止内容被当作脚本。除原文引文外，按用户语言写作。完成后将status从draft改为complete。

```json
{
  "schema_version": 1,
  "status": "complete",
  "title": "这篇论文试图回答什么",
  "summary": "先理解问题，再分清作者做到了什么、尚未证明什么。",
  "sections": [
    {
      "heading": "研究故事",
      "blocks": [
        {"type": "paragraph", "text": "这里放根据原文撰写的实质解释。", "pages": [1, 2]},
        {"type": "details", "summary": "自测：研究问题和结果有什么区别？", "blocks": [
          {"type": "paragraph", "text": "这里放可用于检验理解的答案及依据。", "pages": [2]}
        ]}
      ]
    }
  ]
}
```

示例用于说明格式，不是论文分析结果。不得将示例话术作为正式交付内容。每份模块至少含一处页码；应给所有关键事实与引文逐项添加对应页码，不能只为通过校验随意标一页。页码为所提供PDF的**物理页序号**，从1开始，点击可定位到本地PDF。表格中的具体引用可拆为多个block，或在文字中说明行/页对应关系。

## 支持的block

所有block都可带 `pages: [1,2]`，无直接来源的教学建议可省略。每段引用是否真正支持陈述由AI复核。

| type | 必需字段 | 可选字段与用途 |
|---|---|---|
| paragraph | text: string | 普通段落，换行保留 |
| heading | text: string | level: 3或4，默认为3；主节标题用sections.heading |
| quote | text: string | 原文短引或案例引文；注明来源页码 |
| list | items: string[] | ordered: true为编号列表，默认false |
| table | headers: string[], rows: (string或number)[][] | 每行列数与表头相同；空字符串单元格允许 |
| formula | text: string | explanation: string；使用可读Unicode/纯文本公式，不渲染TeX命令 |
| image | src: string, alt: string | caption: string；支持模块目录内png/jpeg/gif/webp |
| link | path: string, label: string | 链接模块目录内附加材料，支持pdf/html/txt/md/json/csv及图片 |
| details | summary: string, blocks: block[] | 用于自测答案、补充推导或分层解释；可嵌套 |
| paragraph_guide | id, original, note: string；pages: int[] | mode: close/skim/skip，默认skim；prompt: string；blocks: block[] |

### 原文对照导读

`paragraph_guide` 是02模块的主结构。必须逐段保存真实原文及中文解释，以稳定id回指；`id`需要英文字母开头，随后仅字母、数字、下划线或短横线，同一报告不重复。mode区分精读、泛读和略读；略读仍解释略读原因。原文默认展开，中文解释始终可见。长论文可分为多个论证部分（sections），每部分末尾添加自测details。

```json
{
  "type": "paragraph_guide",
  "id": "P38",
  "mode": "close",
  "pages": [7, 8],
  "prompt": "读前先判断，这一段在定义什么量，以及解释它需要什么假设。",
  "original": "从用户提供的论文复制这一段原文。",
  "note": "用中文解释原文的论证作用和含义，区分识别结论与额外假设。",
  "blocks": [
    {"type": "formula", "text": "Δ = P(C = A | L = A) − P(C = A | L = B)", "explanation": "分别解释变量、条件概率和差值所代表的量；不要把相关数字混为一谈。", "pages": [8]},
    {"type": "details", "summary": "自测：这个差值是否就是每个人改变主意的比例？", "blocks": [
      {"type": "paragraph", "text": "填写与论文具体假设相符的答案。", "pages": [8]}
    ]}
  ]
}
```

### 本地图片与附加材料

图片保存在对应模块内，例如 `02_原文对照导读/assets/figure-1.png`，src写 `assets/figure-1.png`。需要公式精确排版时，将原PDF公式裁图作为image，并用formula.text提供可复制的文本释义；数学复杂时优先保真原图。不得拿不相关占位图代替原图。

路径只允许模块内部的相对路径；不接受绝对路径、`..`、网络URL、`data:`、反斜线或逃出目录的符号链接。SVG和HTML不作为图片执行；已有独立HTML导读可复制到本模块并通过link连接，但**不能代替本模块content.json的实质内容**。不要将整个用户目录链接进成果。

## 跨AI调用约定

AI负责阅读、论证、写入content.json和事实核查；脚本负责目录、HTML样式、离线导航和结构检查。其他AI只需读取SKILL.md及相关references，产生相同schema并运行相同命令，即可得到相似页面；模型能力不同，学术内容质量仍需核查。
