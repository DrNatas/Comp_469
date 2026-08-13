# TOOLS.md - COMP 469 Specific Notes

## Important Links
- AIMA Python Repo: https://github.com/aimacode/aima-python
- Berkeley CS188 Pacman Projects: https://inst.eecs.berkeley.edu/~cs188/ (supplementary source — see Citation Convention below)
- Géron Hands-On ML Book Notebooks: https://github.com/ageron/handson-ml3

## Course Repository Map
This workspace (`openclaw/`) holds the assistant persona/memory only. The
actual course content is a sibling directory, `../Fall 2026/`:

```
Comp_469/
├── openclaw/              # this workspace (persona, memory, Labs/)
│   └── Labs/GenerativePreTraining/
└── Fall 2026/
    ├── L01 … L15/         # weekly lecture slides + speaker notes
    ├── Advanced Topics/   # supplementary/deeper-dive lecture material
    ├── Assessments/       # Canvas quiz .adoc sources + QTI exports (weeks 1-7, 15 only)
    ├── Projects/          # hands-on projects, e.g. Projects/search (Pacman)
    └── Reading/           # AsciiDoc course textbook build + reference PDF
```
Always check `MEMORY.md` for the current, maintained state of this map
(what's built, what's missing) rather than assuming it's unchanged.

## Citation Convention
- AIMA references: "AIMA 4th ed., Ch. X.Y" — confirm the chapter/section
  against the actual text before citing, not just a folder name.
- Papers: author(s), year, venue (e.g. "Radford et al., 2018, ACL").
- Berkeley CS188 material is supplementary/secondary, not the primary
  course text — label it as such when referenced in course materials.

## Lab Setup
- Python 3.10+
- Required packages: numpy, pandas, scikit-learn, matplotlib, torch (or tensorflow)
- Use VS Code + Jupyter extension

## Common Tasks
- Generate new weekly lab → "Create Lab 04 starter notebook"
- Update syllabus schedule → "Revise Week 8 schedule" (note: no syllabus doc exists yet — see MEMORY.md)
- Create rubric → "Make grading rubric for search project"