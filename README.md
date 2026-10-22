# Context-Aware UX Framework (CAUX): presentation

A 36-slide deck presenting the research paper *Designing for intent, not pages: the Context-Aware UX Framework (CAUX)* for modern e-commerce, with team tools and a section on India’s e-commerce and data protection regulations.

## What’s inside

| Path | What it is |
|---|---|
| `index.html` | Full-screen presenter: slides peel away from the bottom-right corner along a transparent fold. Open it in a browser. |
| `deck/deck.json` | Deck index: title, slide order, sections and fonts |
| `deck/slides/*.html` | One file per slide (1920 × 1080). Speaker notes are in each slide’s `<aside>`. |
| `build.py` | Rebuilds `index.html` from the slide files: `python3 build.py` |

## Presenting with `index.html`

| Action | Keys and gestures |
|---|---|
| Next slide | → ↓ Space Enter Page Down, click the right of the screen, or swipe left |
| Previous slide | ← ↑ Page Up Backspace, click the left third, or swipe right |
| First / last slide | Home button or Home key / End key |
| Full screen | F, or the Full screen button |
| Jump to a slide | Add `#12` to the URL |

Controls and the cursor hide after a few seconds without mouse movement. If the viewer’s system asks for reduced motion, slides cross-fade instead of peeling.

## Deck outline

1. **Why a new framework:** the problem, the research gap, the core question
2. **Context:** how e-commerce UX evolved; six business models and their UX priorities
3. **Psychology:** attention, seven truths about how people shop, decision momentum
4. **The framework:** the core principle, seven CAUX principles, feature-visibility map, team ownership, the decision test and page audit
5. **The journey:** seven intent stages, a metric per stage, every touchpoint’s job, checkout isolation, before/after, industry benchmarks
6. **Regulation in India:** timeline, E-Commerce Amendment Rules 2026, DPDP Act and Rules, the 13 banned dark patterns
7. **Conclusion and next steps:** key findings, team workshop, roadmap, sources

## Notes

- The editable version lives as a Claude Slides artifact, which also exports to PowerPoint and PDF. This repository holds a snapshot of its source files; `index.html` is a simplified browser rendering, so icons appear as plain dots and fonts need an internet connection.
- Regulatory content reflects status as of October 2026 and is a design summary, not legal advice. Sources are on the final slide and in the speaker notes.
