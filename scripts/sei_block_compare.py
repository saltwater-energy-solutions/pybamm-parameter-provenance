"""Compare the shared SEI block (and selected shared constants) across all bundled
PyBaMM lithium-ion parameter sets (PyBaMM 26.9.0.0). Read-only with respect to PyBaMM.

n_SEI_present / n_SEI_match_block count the nine reference values below (the eight
shared constants plus the SEI open-circuit potential 0.4 V).

Run: PYBAMM_DISABLE_TELEMETRY=true python scripts/sei_block_compare.py
Writes data/sei_block_compare.csv.
"""
import csv, os
import pybamm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
EXCLUDE = {"Chayambuka2022", "ECM_Example", "Sulzer2019"}
names = sorted(n for n in pybamm.parameter_sets.keys() if n not in EXCLUDE)

SEI = {
    "SEI partial molar volume [m3.mol-1]": 9.585e-05,
    "SEI resistivity [Ohm.m]": 2e5,
    "SEI kinetic rate constant [m.s-1]": 1e-12,
    "SEI solvent diffusivity [m2.s-1]": 2.5e-22,
    "SEI electron conductivity [S.m-1]": 8.95e-14,
    "SEI lithium interstitial diffusivity [m2.s-1]": 1e-20,
    "Bulk solvent concentration [mol.m-3]": 2636.0,
    "EC diffusivity [m2.s-1]": 2e-18,
    "SEI open-circuit potential [V]": 0.4,
}
EXTRA = [
    "SEI reaction exchange current density [A.m-2]",
    "Initial SEI thickness [m]",
    "Initial inner SEI thickness [m]",
    "Initial outer SEI thickness [m]",
    "Ratio of lithium moles to SEI moles",
    "SEI growth activation energy [J.mol-1]",
    "EC initial concentration in electrolyte [mol.m-3]",
    "Lithium interstitial reference concentration [mol.m-3]",
    "Inner SEI partial molar volume [m3.mol-1]",
    "Outer SEI partial molar volume [m3.mol-1]",
]

def get(pv, k):
    # composite sets prefix phase names
    for kk in (k, "Primary: " + k, "Negative electrode " + k, "Primary: Negative electrode " + k):
        if kk in pv.keys():
            v = pv[kk]
            return v if isinstance(v, (int, float)) else type(v).__name__
    return None

rows = []
for n in names:
    pv = pybamm.ParameterValues(n)
    row = {"set": n, "citations": ";".join(sorted(map(str, pv.get("citations", []) or [])))}
    match = 0
    present = 0
    for k, ref in SEI.items():
        v = get(pv, k)
        row[k] = v
        if v is not None:
            present += 1
            if isinstance(v, float) and abs(v - ref) <= 1e-9 * abs(ref):
                match += 1
    for k in EXTRA:
        row[k] = get(pv, k)
    row["n_SEI_present"] = present
    row["n_SEI_match_block"] = match
    row["n_entries"] = len([k for k in pv.keys()])
    rows.append(row)

fields = ["set", "n_entries", "n_SEI_present", "n_SEI_match_block"] + list(SEI) + EXTRA + ["citations"]
os.makedirs(DATA, exist_ok=True)
out = os.path.join(DATA, "sei_block_compare.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print("pybamm", pybamm.__version__, "sets:", len(names))
for r in rows:
    print(f"{r['set']:36s} entries={r['n_entries']:4d} SEI9 present={r['n_SEI_present']} match={r['n_SEI_match_block']}  "
          f"j0_SEI={r['SEI reaction exchange current density [A.m-2]']} L0={r['Initial SEI thickness [m]']} "
          f"Lin0={r['Initial inner SEI thickness [m]']} z={r['Ratio of lithium moles to SEI moles']} Ea={r['SEI growth activation energy [J.mol-1]']} "
          f"OCP={r['SEI open-circuit potential [V]']} cite={r['citations']}")
print("wrote", os.path.relpath(out, os.path.dirname(HERE)))
