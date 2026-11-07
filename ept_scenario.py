"""Instanzen: die Handbeispiele und Zufallsinstanzen für App und Messraster."""

import random
from dataclasses import dataclass

import ept_constants as C


@dataclass(frozen=True)
class Instance:
    kisten: tuple         # Quader als (Breite, Tiefe, Höhe) in Lieferreihenfolge, ganzzahlig und positiv
    cap: int = C.CAP      # Kantenlänge eines Behälters

    def __post_init__(self):
        if self.cap <= 0:
            raise ValueError("Kapazität muss positiv sein")
        for t in self.kisten:
            if len(t) != 3 or any((not isinstance(x, int)) or x <= 0 or x > self.cap for x in t):
                raise ValueError(f"Quader {t!r} ungültig (drei ganze Maße, je 1 bis {self.cap})")

    @property
    def n(self) -> int:
        return len(self.kisten)


def beispiel(index: int) -> Instance:
    return Instance(tuple(C.BEISPIELE[index]), C.CAP)


def mess_seed(verteilung: int, n_index: int, j: int) -> int:
    """Fester Seed der j-ten Instanz einer Zelle des Messrasters (Verteilung 0 bis 3, Index der Quaderzahl); stabil über Läufe und Rechner."""
    return 1_000_000 * (verteilung + 1) + 1_000 * (n_index + 1) + j


def zufallsinstanz(verteilung: int, n: int, seed: int, cap: int = C.CAP) -> Instance:
    """n Quader, Breite, Tiefe und Höhe gleichverteilt (ganzzahlig) in den Bereichen der Verteilung."""
    _, _, bereiche = C.VERTEILUNGEN[verteilung]
    rng = random.Random(seed)
    return Instance(tuple(tuple(rng.randint(*bereiche[a]) for a in range(3)) for _ in range(n)), cap)


def quelle_instanz(quelle: int, n: int, seed: int) -> Instance:
    """Instanz der App: Quelle 0 und 1 = Handbeispiele (n und seed ohne Wirkung), 2 bis 5 = Zufallsinstanz der Verteilung quelle - 2."""
    if quelle in C.BEISPIELE:
        return beispiel(quelle)
    return zufallsinstanz(quelle - 2, n, seed)
