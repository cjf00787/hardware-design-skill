# hardware-design

从想法到《原理图&PCB绘制说明》的硬件设计 Agent Skill（适用于 Claude Code / Codex / WorkBuddy 等 SKILL.md 标准的 Agent）。

AI 负责**调研、方案、选型核算、设计文档撰写、SVG 拓扑图**；原理图与 PCB **永远由你在 EDA 软件中亲手绘制**——AI 不操作 EDA、不布线。

## 与其他硬件 skill 的差异

| 项目 | 思路 | 本 skill 补的空位 |
| --- | --- | --- |
| [oxtaw/pcb-skill](https://github.com/oxtaw/pcb-skill) | 驱动 EasyEDA Pro（MCP）自动画图、下单 | 不依赖 EDA 自动化；覆盖它没有的"设计文档写作"环节 |
| [ericshang98/hw-review](https://github.com/ericshang98/hw-review) | 对**已画好**的原理图做逐引脚证据审查 | 在画图**之前**把设计依据沉淀成文档；画完后仍可配合做网表/布局核对 |

核心产出是一份**可以照着画图**的设计文档：全网方案调研 → 选型指标表 → 手册逐颗核对（结论标注手册页码）→ EDA 库引脚确认 → 文档（SVG 拓扑图 + 位号唯一元器件表 + 表下选型计算 + 板材/叠层/阻抗 + 全元件 BOM）。

## 工作流

| 阶段 | 内容 | 检查点 |
| --- | --- | --- |
| 0 | 环境与产物组织（python 检查、目录约定） | — |
| 1 | 全网方案搜寻（GitHub / 嘉立创开源广场 / 原厂参考设计 / 社区，不限于固定站点）与构思 | **G1**：方案确认 |
| 2 | 选型指标表 → 分工选型 → 手册逐颗核对（同型号不同厂陷阱）→ EDA 库引脚核对 | **G2**：选型+引脚双确认 |
| 3 | 撰写《原理图&PCB绘制说明》+ SVG 拓扑图 + 脚本自查 | **G3**：文档验收 |
| 4 | 可选审查（**用户发起**）：原理图导出网表核对 / PCB 布局导出核对 | 差异清单 |

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

可选依赖：Python 3.6+（自带 3 个小工具，**仅标准库**，无 pip 依赖）。

## 用法示例

```text
你：我想做一个 USB-PD 诱骗器（5~20V/PPS，5A），帮我出设计文档。
AI：（阶段 1）先问清 EDA 软件/板厂/关键指标 → 全网搜参考方案给你对比 →
    出一页《设计方案》等你确认（G1）
你：方案可以。选型你来查，手册我来下。
AI：（阶段 2）先给《选型指标表》→ 你下载手册到 datasheets/ →
    逐颗核对并标注手册页码 → 请你截图 EDA 库引脚图核对（G2）
AI：（阶段 3）写出设计文档：系统架构 SVG + 各模块拓扑图 + 元器件表 +
    表下计算 + PCB 板材/阻抗 + BOM；跑位号一致性检查（G3）
你：原理图画完了，网表在 netlist.net，帮我核对。
AI：（阶段 4）重建网络连接，与文档逐项对照，出差异清单。
```

## 自带工具（scripts/，仅标准库）

| 工具 | 用途 |
| --- | --- |
| `impedance_calc.py` | 微带单端/差分阻抗估算（IPC-2141 近似） |
| `trace_current.py` | IPC-2221 载流↔线宽换算 |
| `verify_designators.py` | 设计文档位号重复 / 模块表↔BOM 一致性检查 |

```bash
python scripts/impedance_calc.py --H 0.2104 --er 4.5 --W 0.30 --S 0.25 --mode diff
python scripts/trace_current.py width --I 5 --dT 10 --layer ext --cu 1
python scripts/verify_designators.py docs/specs/xxxx-设计文档.md
```

## 设计原则（五红线）

1. **文档驱动**——AI 不操作 EDA、不布线，画图永远是用户。
2. **禁止猜**——所有结论必须有据：手册页码 / 实测 / 写出过程的计算。
3. **不确定直接问**——任何两个答案会导出不同电路的问题都要问。
4. **中间产物归档**——脚本进 `scripts/`，规格书进 `datasheets/`，不散落根目录。
5. **审查用户发起**——AI 只提议，不主动审。

其他要点：板厂叠层/铜厚参数**运行时联网查当期值**（不固化在 skill 里）；中文资料站 AI 生成规格书只作线索；设计文档不写"待办"章节。

## 路线图

- [ ] 常见 EDA 网表/布局格式的解析与自动比对脚本
- [ ] 英文版
- [ ] 更多参考模板（RF、电机驱动等专用模块）

## License

MIT。版权与许可条款见 [LICENSE](LICENSE)。
