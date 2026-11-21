"""Metrics for monitoring and alerting (added in Module 10).

A tiny, dependency-free registry that renders the Prometheus text format at GET /metrics.
In a larger system you'd use `prometheus_client` or OpenTelemetry; the concepts are the same:
* counters only go up (requests, errors, messages sent)
* gauges go up and down (oldest unsent approved draft)
* histograms count observations in buckets (request latency) so you can compute percentiles
"""
from __future__ import annotations

import threading
from collections import defaultdict
from typing import Dict, Tuple

BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
Labels = Tuple[Tuple[str, str], ...]


class Registry:
    def __init__(self):
        self._lock = threading.Lock()
        self.counters: Dict[str, Dict[Labels, float]] = defaultdict(lambda: defaultdict(float))
        self.gauges: Dict[str, Dict[Labels, float]] = defaultdict(dict)
        self.histograms: Dict[str, Dict[Labels, list]] = defaultdict(dict)
        self.help: Dict[str, str] = {}

    @staticmethod
    def _labels(labels: Dict[str, str]) -> Labels:
        return tuple(sorted((k, str(v)) for k, v in labels.items()))

    def inc(self, name: str, amount: float = 1, help: str = "", **labels) -> None:
        with self._lock:
            self.help.setdefault(name, help)
            self.counters[name][self._labels(labels)] += amount

    def set(self, name: str, value: float, help: str = "", **labels) -> None:
        with self._lock:
            self.help.setdefault(name, help)
            self.gauges[name][self._labels(labels)] = value

    def observe(self, name: str, value: float, help: str = "", **labels) -> None:
        with self._lock:
            self.help.setdefault(name, help)
            series = self.histograms[name].setdefault(self._labels(labels), [0] * len(BUCKETS) + [0, 0.0])
            for i, bound in enumerate(BUCKETS):
                if value <= bound:
                    series[i] += 1
            series[-2] += 1          # count
            series[-1] += value      # sum

    def value(self, name: str, **labels) -> float:
        key = self._labels(labels)
        return self.counters.get(name, {}).get(key) or self.gauges.get(name, {}).get(key, 0.0)

    def render(self) -> str:
        def fmt(labels: Labels, extra: Tuple[Tuple[str, str], ...] = ()) -> str:
            items = labels + extra
            return "{" + ",".join(f'{k}="{v}"' for k, v in items) + "}" if items else ""

        lines = []
        with self._lock:
            for kind, store in (("counter", self.counters), ("gauge", self.gauges)):
                for name, series in sorted(store.items()):
                    lines += [f"# HELP {name} {self.help.get(name, '')}", f"# TYPE {name} {kind}"]
                    lines += [f"{name}{fmt(labels)} {value:g}" for labels, value in sorted(series.items())]
            for name, series in sorted(self.histograms.items()):
                lines += [f"# HELP {name} {self.help.get(name, '')}", f"# TYPE {name} histogram"]
                for labels, values in sorted(series.items()):
                    for bound, count in zip(BUCKETS, values):
                        lines.append(f"{name}_bucket{fmt(labels, (('le', f'{bound:g}'),))} {count}")
                    lines.append(f"{name}_bucket{fmt(labels, (('le', '+Inf'),))} {values[-2]}")
                    lines.append(f"{name}_count{fmt(labels)} {values[-2]}")
                    lines.append(f"{name}_sum{fmt(labels)} {values[-1]:g}")
        return "\n".join(lines) + "\n"


metrics = Registry()   # one per process
