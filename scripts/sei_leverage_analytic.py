"""Analytic leverage of literature-value (carried over) SEI constants on
lithium-inventory loss (LLI) for the LG M50 geometry in PyBaMM's Chen2020 set.

NOT a PyBaMM simulation: it uses the closed forms of PyBaMM's SEI rate laws
(sei_growth.py) at a fixed negative-electrode potential, to rank which constants move
a ~500-cycle LLI most. The outputs are RANKINGS, NOT PREDICTIONS: orders of magnitude
only; a full-model PyBaMM run is needed to confirm any of them.

Assumptions: 500 cycles x 2.5 h of time under SEI growth = 4.5e6 s; isothermal 25 C
(so the Arrhenius factor is 1); graphite potential vs Li held at 0.10 V for the
potential-dependent laws; no SEI-resistance feedback; no cracking, plating or LAM.
Without resistance feedback the reaction-limited rate is exponential in U_sei and
nothing limits it, so the U_sei = 0.8 V case is flagged as non-physical and printed
only to show that sensitivity.

Swap values: D_sol sweep from O'Kane et al. 2022 (PCCP 24 7909, Fig. 1); interstitial
fits to LG M50T ageing data from Li, Kirkaldy, O'Kane et al. (arXiv 2311.05482, Table 3).

Run: python scripts/sei_leverage_analytic.py   (prints to stdout; PyBaMM not needed)
"""
import math
F, R, T = 96485.33, 8.314462, 298.15
f = F / (R * T)
# LG M50 negative electrode, Chen2020 set (PyBaMM 26.9)
eps_am, r_p, L_n, H, W = 0.75, 5.86e-6, 85.2e-6, 0.065, 1.58
A_sei = 3 * eps_am / r_p * L_n * H * W         # m2 of particle surface
t = 500 * 2.5 * 3600.0
dphi = 0.10
Ah_per_mol = F / 3600.0
L0 = 5e-9

def diff_limited(Dc, Vbar, z):
    # dL/dt = Vbar*Dc/(z*L)  ->  L^2 = L0^2 + 2*Vbar*Dc*t/z ; LLI = z*(L-L0)/Vbar per m2
    L = math.sqrt(L0**2 + 2 * Vbar * Dc * t / z)
    return z * (L - L0) / Vbar * A_sei * Ah_per_mol

def reaction_limited(j0, U, alpha=0.5):
    j = j0 * math.exp(-alpha * f * (dphi - U))
    return j * t / F * A_sei * Ah_per_mol

print(f"negative particle surface area {A_sei:.2f} m2; time {t:.2e} s; capacity basis 5.0 Ah")
cases = [
  ("solvent-diffusion, PyBaMM default D_sol=2.5e-22, c=2636, Vbar=9.585e-5, z=2", diff_limited(2.5e-22*2636, 9.585e-5, 2)),
  ("solvent-diffusion, D_sol=2.5e-21 (O'Kane 2022 sweep)", diff_limited(2.5e-21*2636, 9.585e-5, 2)),
  ("solvent-diffusion, D_sol=7.5e-21 (O'Kane 2022 sweep)", diff_limited(7.5e-21*2636, 9.585e-5, 2)),
  ("solvent-diffusion, D_sol=1.25e-20 (O'Kane 2022 sweep)", diff_limited(1.25e-20*2636, 9.585e-5, 2)),
  ("solvent-diffusion, default but z=1 (OKane2022 set)", diff_limited(2.5e-22*2636, 9.585e-5, 1)),
  ("interstitial, PyBaMM default D=1e-20, c0=15, Vbar=9.585e-5", diff_limited(1e-20*15*math.exp(-f*dphi), 9.585e-5, 2)),
  ("interstitial, Li et al. M50T 'SEI only' D=2.36e-18, Vbar=4e-5", diff_limited(2.36e-18*15*math.exp(-f*dphi), 4e-5, 2)),
  ("interstitial, Li et al. M50T '5 coupled' D=9.81e-19, Vbar=5.22e-5", diff_limited(9.81e-19*15*math.exp(-f*dphi), 5.22e-5, 2)),
  ("reaction-limited, j0=1.5e-7, U_sei=0.4 (default)", reaction_limited(1.5e-7, 0.4)),
  ("reaction-limited, j0=1.5e-7, U_sei=0.3", reaction_limited(1.5e-7, 0.3)),
  ("reaction-limited, j0=1.5e-6, U_sei=0.4 (10x j0 only)", reaction_limited(1.5e-6, 0.4)),
  ("reaction-limited, Ramadass2004 set: j0=1.5e-6, U_sei=0.0", reaction_limited(1.5e-6, 0.0)),
]
nonphysical = [
  ("reaction-limited, j0=1.5e-7, U_sei=0.8 (PyBaMM <=v22 outer-SEI OCP)", reaction_limited(1.5e-7, 0.8)),
]
print("RANKINGS, NOT PREDICTIONS: closed-form estimates, orders of magnitude only.")
for name, q in cases:
    print(f"{q:9.4f} Ah  ({100*q/5.0:7.2f} % of 5 Ah)  {name}")
print("NON-PHYSICAL without SEI-resistance feedback (exceeds cell capacity; sensitivity illustration only):")
for name, q in nonphysical:
    print(f"{q:9.4f} Ah  ({100*q/5.0:7.2f} % of 5 Ah)  {name}  [NON-PHYSICAL]")
print("Scaling: diffusion-limited LLI ~ sqrt(z*D*c*t/Vbar) at long times; "
      "reaction-limited LLI ~ j0*exp(alpha*F*U_sei/RT)*t (x%.1f per +0.1 V in U_sei)" % math.exp(0.5*f*0.1))
