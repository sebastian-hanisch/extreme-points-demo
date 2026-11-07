"""Exaktes Optimum der 3D-Behälterpackung (Quader ohne Drehung) mit CP-SAT (ortools): nur für Generator und Tests, nie für die App.

Zuordnungsmodell: Jeder Quader liegt in genau einem von B Behältern; Lage ganzzahlig im Behälter; je zwei Quader im selben Behälter sind in mindestens einer der sechs Richtungen getrennt
(einer liegt ganz links, rechts, hinter, vor, unter oder über dem anderen). Behälter werden der Reihe nach benutzt, der erste Quader liegt im ersten Behälter (Symmetrie). Minimiert wird die Zahl
der benutzten Behälter."""


def optimum_cpsat(kisten, cap: int, obergrenze: int, zeitlimit: float = 30.0, arbeiter: int = 2):
    """Kleinste Behälterzahl bis zur Obergrenze (eine gefundene Packung); -1, wenn das Zeitlimit erreicht wird, ohne dass das Optimum bewiesen ist."""
    from ortools.sat.python import cp_model

    n = len(kisten)
    if n == 0:
        return 0
    B = obergrenze
    m = cp_model.CpModel()
    inb = [[m.NewBoolVar(f"i{i}_{b}") for b in range(B)] for i in range(n)]
    for i in range(n):
        m.AddExactlyOne(inb[i])
    pos = [[m.NewIntVar(0, cap - kisten[i][a], f"p{i}_{a}") for a in range(3)] for i in range(n)]
    benutzt = [m.NewBoolVar(f"u{b}") for b in range(B)]
    for i in range(n):
        for b in range(B):
            m.AddImplication(inb[i][b], benutzt[b])
    for b in range(1, B):
        m.AddImplication(benutzt[b], benutzt[b - 1])
    m.Add(inb[0][0] == 1)
    for i in range(n):
        for j in range(i + 1, n):
            gleich = m.NewBoolVar(f"s{i}_{j}")
            for b in range(B):
                m.AddBoolOr([inb[i][b].Not(), inb[j][b].Not(), gleich])
            getrennt = [m.NewBoolVar(f"d{i}_{j}_{k}") for k in range(6)]
            for a in range(3):
                m.Add(pos[i][a] + kisten[i][a] <= pos[j][a]).OnlyEnforceIf(getrennt[2 * a])
                m.Add(pos[j][a] + kisten[j][a] <= pos[i][a]).OnlyEnforceIf(getrennt[2 * a + 1])
            m.AddBoolOr(getrennt + [gleich.Not()])
    m.Minimize(sum(benutzt))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = zeitlimit
    s.parameters.num_workers = arbeiter
    r = s.Solve(m)
    return int(round(s.ObjectiveValue())) if r == cp_model.OPTIMAL else -1
