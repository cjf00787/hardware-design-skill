[简体中文](./README.md) | English

# hardware-design

A hardware-design Agent Skill that takes an idea to a full "Schematic & PCB Design Specification". Works with Claude Code, Codex, WorkBuddy, and any Agent that supports the SKILL.md standard.

The AI handles research, concept proposals, component-selection calculations, writing the design document, and drawing SVG topology diagrams; schematics and PCB layout are always drawn by the user in their EDA tool — the AI never operates the EDA and never routes.

## Positioning

Existing hardware skills focus on the drawing stage: JLC/嘉立创 ships an official Skill family that drives its own EDA, the KiCad ecosystem has full-flow skill sets and MCP plugins, and there are evidence-driven reviews for finished schematics. The design-document writing stage before drawing is still uncovered — that is the gap this skill fills.

| Project | Approach | Relation to this skill |
| --- | --- | --- |
| [JLC official easyeda-* skills](https://github.com/easyeda/easyeda-api-skill) | Official MCP/Skill family that drives JLC EDA: drawing, DRC, format generation | Automates the drawing stage and complements this skill: document first, then draw |
| [aklofas/kicad-happy](https://github.com/aklofas/kicad-happy) | Full-flow KiCad skill set: schematic analysis, PCB review, EMC pre-compliance, SPICE simulation, sourcing, fab prep | KiCad-focused review and simulation; no pre-drawing design-document writing |
| [oxtaw/pcb-skill](https://github.com/oxtaw/pcb-skill) | Drives EasyEDA Pro via MCP to draw and order automatically | No EDA automation dependency; covers the design-document writing it does not |
| [ericshang98/hw-review](https://github.com/ericshang98/hw-review) | Pin-by-pin evidence review of finished schematics | Settles design rationale before drawing; pairs with it afterwards for netlist/layout checks |

## Workflow

| Phase | Content | Gate |
| --- | --- | --- |
| 0 | Environment and artifact layout: python check, directory conventions | — |
| 1 | Web-wide concept research (GitHub, JLC OSHW hub, vendor reference designs, communities) and proposal | G1: concept sign-off |
| 2 | Selection requirement table → selection split → per-part datasheet verification → EDA library pin confirmation | G2: parts and pins confirmed |
| 3 | Write the Schematic & PCB Design Specification + SVG topology diagrams + script self-checks | G3: document acceptance |
| 4 | Optional reviews, user-initiated: schematic netlist check / PCB placement check | Findings list |

## Installation

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

Optional dependency: Python 3.6+; the bundled tools use only the standard library.

> Note: the skill instructions (SKILL.md and references) are written in Chinese. Deliverables — design documents, proposals, review reports — are written in the language of your conversation.

## Example session

```text
User: I want a USB-PD decoy, 5-20V/PPS adjustable, 5A — write the design document for me.
AI: (Phase 1) confirms EDA tool and fab board house → searches the web for reference designs into a comparison table → outputs a one-page proposal for sign-off.
User: Proposal approved. AI does the selection; I will download the datasheets.
AI: (Phase 2) issues the selection requirement table → verifies datasheets with page citations → confirms EDA library pins with the user.
AI: (Phase 3) writes the design document: system-architecture SVG, module topologies, component tables, selection calculations, PCB material/impedance, BOM — and runs the designator consistency check.
User: Schematic done, netlist is in netlist.net — please verify.
AI: (Phase 4) rebuilds the net connections, compares item by item with the document, and outputs a findings list.
```

## Repository layout

```text
skill/hardware-design/
├── SKILL.md                      main flow: design principles and five phases
├── references/
│   ├── design-doc-template.md    chapter template and writing rules for the design specification
│   ├── selection-checklist.md    selection metrics and calculation conventions
│   ├── datasheet-workflow.md     datasheet sourcing, key-page reading, pin verification
│   ├── pcb-guidance.md           board-material knowledge, current and impedance methods
│   ├── review-workflow.md        netlist review and placement review flows
│   └── svg-diagram-guide.md      SVG topology-diagram style guide
└── scripts/
    ├── impedance_calc.py         microstrip single-ended/differential impedance estimate
    ├── trace_current.py          IPC-2221 current vs trace width
    └── verify_designators.py     designator duplication and BOM consistency check
```

## Design principles

1. Document-driven: the AI never operates the EDA and never routes; schematics and PCB are drawn by the user.
2. Evidence-based: every parameter carries a datasheet page, a measurement, or a worked calculation — never memory.
3. Ask when unsure: any fork that would produce a different circuit is asked about before acting.
4. Archive artifacts: scripts into scripts/, datasheets into datasheets/, documents into docs/specs/.
5. Reviews are user-initiated: the AI proposes the review once at delivery and never pushes.

Two engineering boundaries: fab stackup and copper weights are queried online per project at current values and are not hard-coded in this repository; AI-generated datasheet pages on content farms are leads only — parameters come from vendor PDFs.

## License

MIT — see [LICENSE](LICENSE).
