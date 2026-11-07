"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ept_scenario import Instance  # noqa: E402


@pytest.fixture
def mini():
    """Vier Quader (Breite, Tiefe, Höhe) = (4, 4, 2), (2, 5, 8), (7, 5, 2), (4, 8, 2) mit den Nummern 0 bis 3, Behälter 10 mal 10 mal 10, Volumen 32 + 80 + 70 + 64 = 246, Schranke 1.

    Von Hand gerechnet (Details in tests/test_algorithm.py): Extreme Points mit Projektionen brauchen 1 Behälter, ohne Projektionen 2, Schichten 2."""
    return Instance(((4, 4, 2), (2, 5, 8), (7, 5, 2), (4, 8, 2)), 10)
