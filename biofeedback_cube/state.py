from collections import deque, defaultdict
import logging
import time

logger = logging.getLogger(__name__)


class MidiNotes:

    def __init__(self, clock):
        self.clock = clock

    notes = defaultdict(deque)
    max_time = 2.0

    def add(self, channel, note, velocity):
        self.notes[channel].append((note, velocity, self.clock.t))

    def bleed(self):
        for channel in self.notes.values():

            while channel and (self.clock.t - channel[0][2]) > self.max_time:
                logger.debug(f'popping {channel[0]}, delta {self.clock.t - channel[0][2]}')
                channel.popleft()


class Clock:
    t = 0.0
    t0 = time.time()
    t1 = time.time()

    def tick(self):
        self.t = time.time() - self.t0


clock = Clock()
midi_notes = MidiNotes(clock)
