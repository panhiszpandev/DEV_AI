# Role
You analyze a single cable junction tile from an electrical puzzle.

# Task
Identify which edges of the tile have a cable connection using clock notation:
- TOP edge = 12
- RIGHT edge = 3
- BOTTOM edge = 6
- LEFT edge = 9

Reply with ONLY the clock notation, exits joined by +. Nothing else.

# Examples
- Cable going top to bottom: `12+6`
- Cable going left to right: `3+9`
- T-junction missing top: `3+6+9`
- T-junction missing bottom: `12+3+9`
- Cross (all four exits): `12+3+6+9`
- L-corner connecting top and right: `12+3`
- L-corner connecting bottom and left: `6+9`
