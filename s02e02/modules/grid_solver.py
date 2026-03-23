class GridSolver:
    _ROTATION_MAP = {12: 3, 3: 6, 6: 9, 9: 12}

    def rotate_cw(self, exits: frozenset) -> frozenset:
        """Rotate exits 90° clockwise: 12→3, 3→6, 6→9, 9→12."""
        return frozenset(self._ROTATION_MAP[e] for e in exits)

    def rotations_needed(self, current: frozenset, desired: frozenset) -> int:
        """Return number of 90° CW rotations (0–3) to reach desired state."""
        state = frozenset(current)
        for i in range(4):
            if state == frozenset(desired):
                return i
            state = self.rotate_cw(state)
        return 0
