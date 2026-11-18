"""Reproduce the simulated phone-battery dataset used in Math 124 Chapter 7.

These 200 synthetic one-hour trials are an arithmetic teaching example.
They are not measurements of an actual phone and do not establish any
phone's battery performance. Each simulated trial keeps the screen on at
a fixed brightness, streams video for part of the hour, and leaves the
screen idle for the remaining time, with other conditions held fixed.

Run this script to replace phone-battery.csv in the same directory.
"""

from pathlib import Path

import numpy as np


def generate_data():
    """Return brightness setting, streaming minutes, and battery used in pp."""
    rng = np.random.default_rng(124)
    s = rng.integers(1, 11, 200) * 10
    t = rng.integers(0, 13, 200) * 5
    s[:4] = [20, 80, 50, 50]
    t[:4] = [10, 10, 50, 30]
    y = np.round(2 + 0.04 * s + 0.15 * t + rng.normal(0, 0.85, 200), 1)
    y[:4] = [4.1, 7.2, 10.8, 9.4]
    return np.column_stack([s, t, y])


def main():
    target = Path(__file__).resolve().with_name("phone-battery.csv")
    np.savetxt(
        target,
        generate_data(),
        fmt="%d,%d,%.1f",
        header="brightness_percent,streaming_minutes,battery_used_pp",
        comments="",
    )


if __name__ == "__main__":
    main()
