"""Classify every entry of PyBaMM 26.9.0.0's Chen2020 parameter set against the
Chen et al. 2020 paper (JES 167 080534, doi:10.1149/1945-7111/ab9050), read in full,
and the per-entry 'Reference' column PyBaMM itself kept in its v22.1 CSVs (dropped
when parameter sets moved to single Python files, PR #2342, v22.10).

provenance_class values (BattINFO parameter-claim vocabulary, plus 'setting'):
  measured    measured in the paper (incl. simple derivations from measured values)
  fitted      fitted or tuned in the paper (OCP fits, EIS/Arrhenius kinetics, trial-and-error tuning)
  literature  literature value (carried over) from another paper or handbook, for another cell or material
  assumed     assumed or placeholder (theory value, zero switch, 'default' in v22.1 with no source)
  setting     setting or operating condition
  unresolved  origin not resolved (none in v0.1)

Run: PYBAMM_DISABLE_TELEMETRY=true python scripts/chen2020_classify.py
Writes data/chen2020_provenance.csv.
"""
import csv, os
from collections import Counter
from pybamm.input.parameters.lithium_ion import Chen2020

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
CLASS = {"M": "measured", "F": "fitted", "B": "literature", "A": "assumed", "S": "setting", "U": "unresolved"}
d = Chen2020.get_parameter_values()
keys = [k for k in d if k not in ("chemistry", "citations")]

SEI_BLOCK = ("SEI partial molar volume", "SEI reaction exchange current density", "SEI resistivity",
         "SEI solvent diffusivity", "Bulk solvent concentration", "SEI open-circuit potential",
         "SEI electron conductivity", "SEI lithium interstitial diffusivity",
         "Lithium interstitial reference concentration", "Initial SEI thickness",
         "EC initial concentration", "EC diffusivity", "SEI kinetic rate constant",
         "Ratio of lithium moles to SEI moles")
rules = [
 # (substring, class code, evidence); codes are mapped to provenance_class names via CLASS
 ("reaction-driven LAM factor", "A", "zero = mechanism off; not in paper"),
 ("SEI growth activation energy", "A", "0 J/mol placeholder; OKane2022 uses 38000"),
 ("current collector thickness", "M", "Table II 16.3/11.7 um, rounded to 16/12"),
 ("Negative electrode thickness", "M", "Table II 85.2 um"),
 ("Positive electrode thickness", "M", "Table II 75.6 um"),
 ("Separator thickness", "M", "Table II ca. 12 um"),
 ("Electrode height", "M", "Table II/VII width 6.5 cm"),
 ("Electrode width", "M", "Table VII length 1.58 m"),
 ("Cell cooling surface area", "M", "derived from measured 21.00 mm x 70.00 mm can (text p.5); not stated in paper (inferred)"),
 ("Cell volume", "M", "derived from measured 21.00 mm x 70.00 mm can; not stated in paper (inferred)"),
 ("Cell thermal expansion coefficient", "B", "not in paper (isothermal model); origin not recorded"),
 ("current collector conductivity", "B", "v22.1 CSV: CRC Handbook (Cu/Al)"),
 ("current collector density", "B", "v22.1 CSV: CRC Handbook"),
 ("current collector specific heat", "B", "v22.1 CSV: CRC Handbook"),
 ("current collector thermal conductivity", "B", "v22.1 CSV: CRC Handbook"),
 ("Nominal cell capacity", "S", "datasheet 5 Ah"),
 ("Current function", "S", "default 1C"),
 ("Contact resistance", "S", "0 default"),
 ("Negative electrode conductivity", "M", "4-point probe 180-250 S/m; 215 used"),
 ("Positive electrode conductivity", "M", "4-point probe 0.174-0.186 S/m; 0.18 used"),
 ("Maximum concentration", "F", "tuned to 1C discharge (Table IX); measured 29583/51765"),
 ("particle diffusivity", "F", "tuned to 1C (Table IX); GITT values 1.74e-15/1.48e-15 are 19x/2.7x lower"),
 ("electrode OCP [V]", "F", "fitted to GITT half-cell pseudo-OCV (eqs 8-9)"),
 ("exchange-current density", "F", "EIS at 50% SOC, Arrhenius fit (Table VI, Fig 16)"),
 ("electrode porosity", "M", "Table II electrolyte volume fraction"),
 ("Separator porosity", "M", "Table II 47%"),
 ("active material volume fraction", "M", "1 - porosity (paper assumes no binder/carbon)"),
 ("particle radius", "M", "Table II/VII mean particle size"),
 ("Bruggeman coefficient (electrolyte)", "A", "theoretical 1.5; paper measured 2.43/2.57/2.91 (Table II)"),
 ("Bruggeman coefficient (electrode)", "A", "0 in 26.9 (was 1.5 'default' in v22.1); not in paper"),
 ("charge transfer coefficient", "A", "symmetric reaction assumed in paper"),
 ("double-layer capacity", "A", "not in paper; no source in v22.1"),
 ("electrode density", "A", "v22.1 CSV: 'default'; not in paper"),
 ("Separator density", "A", "v22.1 CSV: 'default'; not in paper"),
 ("specific heat capacity", "A", "v22.1 CSV: 'default'; not in paper"),
 ("thermal conductivity", "A", "v22.1 CSV: 'default'; not in paper"),
 ("OCP entropic change", "A", "0; not in paper"),
 ("Initial concentration in electrolyte", "A", "paper chose 1 mol/dm3; real cell 'likely up to 1.2'"),
 ("Cation transference number", "B", "Nyman 2008 polynomial evaluated at 1 M by the paper"),
 ("Thermodynamic factor", "A", "ideal electrolyte assumed in paper"),
 ("Electrolyte diffusivity", "B", "Nyman 2008 (EC:EMC 3:7), cited by paper"),
 ("Electrolyte conductivity", "B", "Nyman 2008, cited by paper"),
 ("Total heat transfer coefficient", "A", "v22.1 CSV: 'default'"),
 ("Initial concentration in negative", "S", "0.9014 (measured) x 33133 (tuned)"),
 ("Initial concentration in positive", "S", "0.27 (tuned) x 63104 (tuned)"),
 ("temperature", "S", "25 C operating condition"),
 ("Number of", "S", "single cell"),
 ("voltage cut-off", "S", "2.5/4.2 V test window"),
 ("Open-circuit voltage at", "S", "2.5/4.2 V"),
]
rows = []
for k in keys:
    if any(k.startswith(s) for s in SEI_BLOCK):
        cls, ev = "B", "SEI block: not in paper; v22.1 CSV cites Safari/Single/Ploehn/Yang or 'Guess'"
    else:
        for s, c, e in rules:
            if s in k:
                cls, ev = c, e
                break
        else:
            cls, ev = "U", "unmatched"
    rows.append({"entry": k, "value": d[k] if not callable(d[k]) else d[k].__name__,
                 "provenance_class": CLASS[cls], "evidence": ev})

os.makedirs(DATA, exist_ok=True)
out = os.path.join(DATA, "chen2020_provenance.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["entry", "value", "provenance_class", "evidence"]); w.writeheader(); w.writerows(rows)
c = Counter(r["provenance_class"] for r in rows)
print("entries:", len(rows), dict(sorted(c.items())))
sub = Counter(r["provenance_class"] for r in rows if not r["evidence"].startswith("SEI block") and "LAM" not in r["entry"] and "SEI growth" not in r["entry"])
print("excluding the 17 SEI/LAM degradation entries:", sum(sub.values()), dict(sorted(sub.items())))
for r in rows:
    if r["provenance_class"] == "unresolved": print("UNMATCHED", r)
print("wrote", os.path.relpath(out, os.path.dirname(HERE)))
