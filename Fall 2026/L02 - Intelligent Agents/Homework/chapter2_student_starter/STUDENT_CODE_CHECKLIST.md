# Student Code Checklist

Complete the `TODO(CH2-...)` markers in `src/autonomous_pacman_agent.py`.

1. Expand `Percept` with current direction, released ghosts, and frightened time.
2. Update `Game.sense_environment()` to populate those sensor fields.
3. Remove dynamic reads of ghosts, frightened mode, and direction from `self.game` inside decision making.
4. Add internal state derived from the percept sequence.
5. Make the internal state influence action selection through a revisit or oscillation term.
6. Replace unexplained utility literals with descriptive named weights.
7. Separate action evaluation from best-action selection.
8. Keep every returned action legal and handle an empty legal-action tuple.
9. Put direction, total utility, food distance, ghost distance, and memory contribution in `last_reason`.
10. Run the contract tests and paired trials.
