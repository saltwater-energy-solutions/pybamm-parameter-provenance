# pybamm-parameter-provenance

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23243371.svg)](https://doi.org/10.5281/zenodo.23243371)

Per-entry provenance for PyBaMM's bundled lithium-ion parameter sets: for each value,
whether it was measured in the cited paper, fitted or tuned there, carried over from
another study (literature value), assumed/default, or a simulation setting.

Status: v0.1 covers Chen2020 (all 92 entries, read against Chen et al. 2020,
JES 167 080534, doi:10.1149/1945-7111/ab9050) and the shared SEI constants across
all 16 lithium-ion sets. It makes no claim about model accuracy. Corrections welcome:
open an issue, and we will update the table and credit you.

Classes follow BattINFO parameter claims (`provenance_class`): measured, fitted,
literature, assumed; plus `setting` for operating conditions.

## Contents

| File | What it is |
|---|---|
| `data/chen2020_provenance.csv` | Each of the 92 `Chen2020` entries in PyBaMM 26.9.0.0: value, `provenance_class`, evidence |
| `data/sei_block_compare.csv` | The SEI constants across the 16 lithium-ion sets (13 carry the same eight shared values) |
| `data/pybamm_v22.1_seis_example_reference.csv` | The SEI rows of PyBaMM's v22.1 `seis/example/parameters.csv`, with its `Reference` column, source URL and retrieval date |
| `scripts/chen2020_classify.py` | Writes `data/chen2020_provenance.csv` |
| `scripts/sei_block_compare.py` | Writes `data/sei_block_compare.csv` |
| `scripts/sei_leverage_analytic.py` | Closed-form ranking of SEI constants (prints only) |

Chen2020 counts (v0.1): measured 18, fitted 8, literature 26, assumed 26, setting 14.

## Reproduce

    python -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt          # pybamm==26.9.0.0, Python 3.12
    PYBAMM_DISABLE_TELEMETRY=true python scripts/sei_block_compare.py
    PYBAMM_DISABLE_TELEMETRY=true python scripts/chen2020_classify.py
    python scripts/sei_leverage_analytic.py

`sei_leverage_analytic.py` is a closed-form ranking of SEI constants, not a PyBaMM
simulation; its numbers are rankings and orders of magnitude, not predictions. Its
U_SEI = 0.8 V case is printed separately and marked non-physical: without SEI-resistance
feedback it exceeds the cell's capacity.

## Sources

PyBaMM v22.1 parameter CSVs (Reference column), PyBaMM 26.9.0.0 parameter files,
Chen et al. 2020 (JES 167 080534), O'Kane et al. 2022 (PCCP 24 7909) SI Table S4.

## Cite

Concept DOI (all versions): https://doi.org/10.5281/zenodo.23243371 · v0.1.0: https://doi.org/10.5281/zenodo.23243372 · see `CITATION.cff`.

## Licence

Code BSD-3-Clause (LICENSE). Tables in data/ CC BY 4.0 (LICENSE-DATA).
Parameter values are reproduced from PyBaMM (BSD-3-Clause) and the cited papers.
