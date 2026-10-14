简体中文 | [English](./README.en.md)

# hardware-design

从想法到《原理图&PCB绘制说明》的硬件设计 Agent Skill，适用于 Claude Code、Codex、WorkBuddy 等支持 SKILL.md 标准的 Agent。

AI 承担调研、方案、选型核算、设计文档撰写与 SVG 拓扑图；原理图和 PCB 由用户在 EDA 软件中绘制，AI 不操作 EDA、不布线。

## 定位

现有硬件类 skill 集中在画图阶段：嘉立创官方提供驱动自家 EDA 的 Skill 家族，KiCad 生态有全流程技能集与 MCP 插件，另有面向已画好原理图的证据审查。画图之前的设计文档写作环节仍无人覆盖，本 skill 补的就是这一段。

| 项目 | 思路 | 与本 skill 的关系 |
| --- | --- | --- |
| [嘉立创官方 easyeda-* skills](https://github.com/easyeda/easyeda-api-skill) | 官方 MCP/Skill 家族：驱动嘉立创 EDA 画图、DRC、格式生成 | 画图阶段的自动化，与本 skill 互补：先文档、后画图 |
| [aklofas/kicad-happy](https://github.com/aklofas/kicad-happy) | KiCad 全流程技能集：原理图分析、PCB 审查、EMC 预合规、SPICE 仿真、选型与制造准备 | 面向 KiCad 生态的审查与仿真，不含画图前的设计文档写作 |
| [oxtaw/pcb-skill](https://github.com/oxtaw/pcb-skill) | 通过 MCP 驱动 EasyEDA Pro 自动画图、下单 | 不依赖 EDA 自动化，覆盖其未涉及的设计文档写作 |
| [ericshang98/hw-review](https://github.com/ericshang98/hw-review) | 对已画好的原理图做逐引脚证据审查 | 在画图之前沉淀设计依据；画完后可配合做网表/布局核对 |

## 工作流

| 阶段 | 内容 | 检查点 |
| --- | --- | --- |
| 0 | 环境与产物组织：python 检查、目录约定 | — |
| 1 | 全网方案搜寻与构思：GitHub、嘉立创开源广场、原厂参考设计、技术社区 | G1：方案确认 |
| 2 | 选型指标表 → 分工选型 → 手册逐颗核对 → EDA 库引脚确认 | G2：选型与引脚双确认 |
| 3 | 撰写《原理图&PCB绘制说明》+ SVG 拓扑图 + 脚本自查 | G3：文档验收 |
| 4 | 可选审查，由用户发起：原理图网表核对 / PCB 器件布局核对 | 差异清单 |

## 安装

```bash
git clone https://github.com/cjf00787/hardware-design-skill.git
cd hardware-design-skill

# Claude Code
cp -r skill/hardware-design ~/.claude/skills/hardware-design
# Codex
cp -r skill/hardware-design ~/.codex/skills/hardware-design
# WorkBuddy
cp -r skill/hardware-design ~/.workbuddy/skills/hardware-design
```

可选依赖：Python 3.6+，自带工具仅使用标准库。

## 用法示例

```text
用户：我想做一个 USB-PD 诱骗器，5~20V/PPS 可调，5A，帮我出设计文档。
AI：（阶段 1）确认 EDA 软件与板厂 → 全网搜寻参考方案并汇成对比表 → 输出一页《设计方案》等待确认。
用户：方案通过。选型交给 AI，手册由我来下载。
AI：（阶段 2）输出选型指标表 → 核对手册并标注页码 → 与用户核对 EDA 库引脚。
AI：（阶段 3）撰写设计文档：系统架构 SVG、模块拓扑图、元器件表、选型计算、PCB 板材与阻抗、BOM，并运行位号一致性检查。
用户：原理图画完了，网表在 netlist.net，请核对。
AI：（阶段 4）重建网络连接，与设计文档逐项对照，输出差异清单。
```

## 仓库结构

```text
skill/hardware-design/
├── SKILL.md                      主流程：设计原则与五个阶段
├── references/
│   ├── design-doc-template.md    《原理图&PCB绘制说明》章节模板与写作要求
│   ├── selection-checklist.md    选型指标方法与核算惯例：耐压、耐流、精度、封装
│   ├── datasheet-workflow.md     手册获取、关键页读法、引脚核对流程
│   ├── pcb-guidance.md           板材知识、载流与阻抗计算方法
│   ├── review-workflow.md        网表审查与器件布局审查流程
│   └── svg-diagram-guide.md      SVG 拓扑图风格规范
└── scripts/
    ├── impedance_calc.py         微带单端/差分阻抗估算
    ├── trace_current.py          IPC-2221 载流与线宽换算
    └── verify_designators.py     位号重复与 BOM 一致性检查
```

SKILL.md 与 references 全部为中文 Markdown，点击文件即可阅读；scripts 是配套的 Python 工具，注释同样为中文。

## 设计原则

1. 文档驱动：AI 不操作 EDA、不布线，原理图与 PCB 由用户绘制。
2. 结论有据：所有参数给出手册页码、实测数据或计算过程，禁止凭记忆填写。
3. 不确定即询问：任何会导致不同电路的分歧点，先问用户再动手。
4. 产物归档：脚本存入 scripts/，规格书存入 datasheets/，设计文档存入 docs/specs/。
5. 审查由用户发起：交付文档时提议一次网表或布局审查，之后不催促、不主动执行。

两条工程边界：板厂的叠层与铜厚参数在项目进行时联网查询当期值，不写入本仓库；中文资料站的 AI 生成规格书只作检索线索，参数以原厂 PDF 为准。

## License

MIT，条款见 [LICENSE](LICENSE)。
