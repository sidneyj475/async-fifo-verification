
from collections import deque


class FIFOScoreboard:
    def __init__(self):
        self.events = []
        self.expected = deque()
        self.writes = 0
        self.reads = 0
        self.errors = []

    def record_write(self, data, timestamp):
        self.events.append(
            (timestamp, 0, "write", data)
        )

    def check_read(self, actual, timestamp):
        self.events.append(
            (timestamp, 1, "read", actual)
        )

    def evaluate(self):
        self.expected.clear()
        self.writes = 0
        self.reads = 0
        self.errors.clear()

        for _, _, kind, data in sorted(self.events):
            if kind == "write":
                self.expected.append(data)
                self.writes += 1
            else:
                if not self.expected:
                    self.errors.append(
                        "Read accepted with empty reference queue"
                    )
                    continue

                expected = self.expected.popleft()
                self.reads += 1

                if data != expected:
                    self.errors.append(
                        f"Read {self.reads}: expected "
                        f"{expected:#04x}, got {data:#04x}"
                    )

    def check_empty(self):
        assert not self.expected, (
            f"{len(self.expected)} unread entries remain"
        )

    def assert_no_errors(self):
        assert not self.errors, "\n".join(self.errors)
