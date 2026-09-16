"""Conservative ordered progress accounting, independent of training reward.

Requires frame-level samples and a validated contiguous cyclic checkpoint map.
Backward travel reduces signed position; revisiting old positions earns nothing.
Invalid jumps invalidate the episode, rather than granting guessed progress.
"""
class Progress:
    def __init__(self, count, checkpoint, lap, race_laps=5):
        if count < 3 or not 0 <= checkpoint < count:
            raise ValueError('Invalid calibrated checkpoint map')
        self.count, self.previous, self.start_lap = count, checkpoint, lap
        self.position = self.maximum = self.valid_laps = 0
        self.race_laps = race_laps
        self.invalid = False

    def update(self, checkpoint, lap, backward=False):
        if self.invalid:
            return 0.0
        if not 0 <= checkpoint < self.count:
            self.invalid = True
            return 0.0
        delta = (checkpoint - self.previous) % self.count
        self.previous = checkpoint
        if delta == self.count - 1:
            delta = -1
        elif delta not in (0, 1):
            self.invalid = True
            return 0.0
        if backward and delta == 1:
            # Conflicting direction evidence: never grant progress.
            self.invalid = True
            return 0.0
        self.position += delta
        old_max = self.maximum
        self.maximum = max(self.maximum, self.position)
        raw_laps = lap - self.start_lap
        candidate = self.position // self.count
        # A full traversal AND game lap evidence are needed. Reset near the
        # finish line cannot turn one checkpoint crossing into a valid lap.
        if raw_laps > self.valid_laps and candidate > self.valid_laps:
            self.valid_laps = min(raw_laps, candidate, self.race_laps)
        return (self.maximum - old_max) / self.count

    @property
    def complete(self):
        return self.valid_laps >= self.race_laps and not self.invalid
