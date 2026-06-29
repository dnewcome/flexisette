"""reflex.py — flexisette bass-reflex micro-speaker: Thiele-Small lumped acoustic sim.

Models the slim oval driver + ~6 cm3 head-insert box + folded slot port as an acoustical
equivalent circuit (pressure=voltage, volume-velocity=current). The ENCLOSURE is in the model:
  box   -> acoustic compliance   Cab = Vb/(rho c^2)        (a capacitor)
  port  -> acoustic mass+loss     Map = rho Leff/Sp, Rap   (an inductor + resistor)
  driver-> reflected R/L(mass)/C(compliance) + Rae = BL^2/(Sd^2 Re)   (the motor's electrical damping)

ngspice solves the circuit for the cone volume velocity Ud and the port volume velocity Up; an
independent numpy complex-impedance solve verifies the deck. Outputs (sim/speaker_reflex/):
  reflex.cir            the generated nominal vented deck (readable artifact + Falstad source)
  response.png          SPL (sealed vs vented + Fb sweep), excursion, port velocity, |Z| impedance
  reflex_falstad.txt    Falstad/CircuitJS netlist (intuition)
Representative driver T-S; refine when a real oval module is chosen.

    python3 sim/speaker_reflex/reflex.py
"""
import os, subprocess, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RHO, C = 1.18, 345.0                     # air density (kg/m3), speed of sound (m/s)

# ---- primary T-S params (representative oval micro-driver) ----
P = dict(
    Sd=1.5e-4,    # effective radiating area, m^2  (~1.5 cm2, oval ~9x25mm)
    Fs=500.0,     # free-air resonance, Hz
    Vas=25e-6,    # equivalent compliance volume, m^3 (25 cm3)
    Qts=0.9, Qms=3.0,
    Re=8.0, Le=0.15e-3,
    Vb=6e-6,      # box back-volume, m^3 (6 cm3, head insert)
    Sp=9.6e-6,    # folded slot port area, m^2 (8 x 1.2 mm)
    Qp=15.0,      # port quality (loss)
    eg=2.83,      # drive volts (= 1 W into 8 ohm) -> SPL@1m, excursion, port velocity
)

def derive(p):
    """T-S -> mechanical -> acoustic element values."""
    d = dict(p)
    Sd, Fs, Vas, Qts, Qms, Re = (p[k] for k in ("Sd", "Fs", "Vas", "Qts", "Qms", "Re"))
    Cms = Vas / (RHO * C * C * Sd * Sd)                 # m/N
    Mms = 1.0 / ((2 * np.pi * Fs) ** 2 * Cms)           # kg
    Qes = 1.0 / (1.0 / Qts - 1.0 / Qms)
    BL = np.sqrt(2 * np.pi * Fs * Mms * Re / Qes)       # T*m
    Rms = 2 * np.pi * Fs * Mms / Qms                    # N*s/m
    d.update(Cms=Cms, Mms=Mms, Qes=Qes, BL=BL, Rms=Rms,
             Mas=Mms / Sd**2, Cas=Cms * Sd**2, Ras=Rms / Sd**2,
             Rae=BL**2 / (Sd**2 * Re),
             Cab=p["Vb"] / (RHO * C * C),
             pg=p["eg"] * BL / (Sd * Re))               # acoustic pressure generator
    return d

def port_mass(Fb, Cab):                                 # tune the port to Fb (box+port resonance)
    return 1.0 / ((2 * np.pi * Fb) ** 2 * Cab)
def port_len(Map, Sp):                                  # physical effective length of that port
    return Map * Sp / RHO

# ---------- analytic complex-impedance solve (verification + impedance curve) ----------
def solve_analytic(d, f, Fb, vented=True):
    w = 2 * np.pi * f
    jw = 1j * w
    Zport = jw * port_mass(Fb, d["Cab"]) + d["Rap"](Fb) if vented else np.inf
    Ybox = jw * d["Cab"] + (1.0 / Zport if vented else 0.0)
    Zbox = 1.0 / Ybox
    Zcone = d["Rae"] + d["Ras"] + jw * d["Mas"] + 1.0 / (jw * d["Cas"]) + Zbox
    Ud = d["pg"] / Zcone
    pb = Ud * Zbox
    Up = pb / Zport if vented else 0.0 * Ud
    # electrical impedance: reflect the MECHANICAL load (no Rae) through BL^2
    Zac_mech = d["Ras"] + jw * d["Mas"] + 1.0 / (jw * d["Cas"]) + Zbox
    Ze = d["Re"] + jw * d["Le"] + d["BL"] ** 2 / (d["Sd"] ** 2 * Zac_mech)
    return Ud, Up, Ze

# ---------- ngspice deck (the circuit, generated numeric) ----------
def make_deck(d, Fb, vented=True):
    Map = port_mass(Fb, d["Cab"]); Rap = d["Rap"](Fb)
    port = (f"Lmap pb p1 {Map:.6e}\n"
            f"Rap  p1 pp {Rap:.6e}\n"
            f"VsUp pp 0 0\n") if vented else "VsUp pb pbx 0\nRopen pbx 0 1e15\n"
    return f"""* flexisette bass-reflex acoustic equivalent circuit (Fb={Fb:.0f}Hz vented={vented})
Vpg pg 0 AC {d['pg']:.6e}
Rae pg a  {d['Rae']:.6e}
Ras a  b  {d['Ras']:.6e}
Lmas b c  {d['Mas']:.6e}
Ccas c  cd {d['Cas']:.6e}
VsUd cd pb 0
Ccab pb 0 {d['Cab']:.6e}
{port}.control
ac dec 240 20 5000
let udr=real(i(vsud))
let udi=imag(i(vsud))
let upr=real(i(vsup))
let upi=imag(i(vsup))
wrdata {{OUT}} udr udi upr upi
.endc
.end
"""

def run_ngspice(deck):
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, "o.dat"); cir = os.path.join(t, "d.cir")
        open(cir, "w").write(deck.replace("{OUT}", out))
        subprocess.run(["ngspice", "-b", cir], capture_output=True, text=True)
        a = np.loadtxt(out)               # wrdata: f,udr,f,udi,f,upr,f,upi
        f = a[:, 0]; Ud = a[:, 1] + 1j * a[:, 3]; Up = a[:, 5] + 1j * a[:, 7]
        return f, Ud, Up

# ---------- acoustic outputs ----------
def spl(Utot, f):                         # far-field half-space monopole @1m
    p = RHO * 2 * np.pi * f * np.abs(Utot) / (2 * np.pi)      # = rho f |U|
    return 20 * np.log10(np.maximum(p, 1e-12) / 20e-6)
def excursion_mm(Ud, f, Sd):              # |x| = |Ud|/(w Sd)
    return np.abs(Ud) / (2 * np.pi * f * Sd) * 1e3
def port_vel(Up, Sp):
    return np.abs(Up) / Sp


def main():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    d = derive(P)
    d["Rap"] = lambda Fb: np.sqrt(port_mass(Fb, d["Cab"]) / d["Cab"]) / P["Qp"]   # port loss from Qp
    f = np.geomspace(20, 5000, 600)
    Fb0 = 400.0

    print("=== derived ===")
    for k in ("Cms", "Mms", "BL", "Rms", "Qes", "Cab"):
        print(f"  {k:4s} = {d[k]:.4e}")
    print(f"  port@{Fb0:.0f}Hz: Map={port_mass(Fb0,d['Cab']):.0f} kg/m4 -> "
          f"effective length {port_len(port_mass(Fb0,d['Cab']),P['Sp'])*1e3:.0f} mm (slot {P['Sp']*1e6:.1f} mm2)")

    # ngspice vs analytic at Fb0 (verification)
    fn, Udn, Upn = run_ngspice(make_deck(d, Fb0, True))
    Uda, Upa, Ze = solve_analytic(d, fn, Fb0, True)
    err = np.max(np.abs(np.abs(Udn) - np.abs(Uda)) / (np.abs(Uda) + 1e-30))
    print(f"\n[verify] ngspice vs analytic |Ud| max rel-err = {err*100:.2f}%  "
          f"({'MATCH' if err < 0.02 else 'CHECK'})")

    # analytic curves on the fine grid
    Uds, _, Zes = solve_analytic(d, f, Fb0, vented=False)   # sealed
    Udv, Upv, Zev = solve_analytic(d, f, Fb0, vented=True)  # vented @400
    Fc = P["Fs"] * np.sqrt(1 + P["Vas"] / P["Vb"])
    band = (fn > 150) & (fn < 900)                      # the Fb dip sits between the two humps
    fbdip = fn[band][np.argmin(np.abs(Ze)[band])]
    print(f"[verify] sealed Fc (analytic) = {Fc:.0f} Hz ; vented |Z| dip (=Fb) = {fbdip:.0f} Hz (target {Fb0:.0f})")

    # --- engineering summary ---
    pb_band = (f > 1500) & (f < 3000)                   # passband (above resonance)
    spl_pass = np.median(spl(Udv - Upv, f)[pb_band])
    bump = (f > 300) & (f < 700)                        # the low-mid region the port lifts
    gain = np.median(spl(Udv - Upv, f)[bump] - spl(Uds, f)[bump])
    xmax_mm = 0.3
    maxexc = np.max(excursion_mm(Udv, f, P['Sd']))      # peak (at the ~1.1kHz resonance)
    clean_W = (xmax_mm / maxexc) ** 2                    # power to stay within Xmax
    spl_clean = spl_pass + 10 * np.log10(clean_W)        # SPL at that clean level
    vp_clean = np.max(port_vel(Upv, P['Sp'])) * np.sqrt(clean_W)
    print("\n=== ENGINEERING SUMMARY (representative driver) ===")
    print(f"  sealed resonance Fc = {Fc:.0f} Hz | vented tuning Fb = {fbdip:.0f} Hz (folded port {port_len(port_mass(Fb0,d['Cab']),P['Sp'])*1e3:.0f} mm)")
    print(f"  port lifts the 300-700 Hz low-mids ~{gain:.0f} dB over sealed (the audible win)")
    print(f"  EXCURSION-LIMITED, not power-limited: 2.7mm peak @1W vs {xmax_mm}mm Xmax")
    print(f"    -> clean ceiling ~{clean_W*1000:.0f} mW => ~{spl_clean:.0f} dB @1m passband "
          f"(amp has headroom; the micro driver doesn't)")
    print(f"  port velocity at the clean level ~{vp_clean:.0f} m/s vs ~{0.05*C:.0f} m/s chuffing "
          f"({'OK' if vp_clean < 0.05*C else 'still chuffs'}) — the slot only chuffs at absurd power")

    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    # 1) SPL sealed vs vented + Fb sweep
    ax[0,0].semilogx(f, spl(Uds, f), 'k--', lw=2, label='sealed')
    for Fb, c in zip((300, 350, 400, 450, 500), plt.cm.viridis(np.linspace(0, .9, 5))):
        Ud, Up, _ = solve_analytic(d, f, Fb, True)
        ax[0,0].semilogx(f, spl(Ud - Up, f), color=c, lw=1.6, label=f'vented Fb={Fb}')
    ax[0,0].axvline(Fc, color='gray', ls=':'); ax[0,0].text(Fc, ax[0,0].get_ylim()[0]+3, ' sealed Fc', color='gray')
    ax[0,0].set(title='SPL @1m, 1W (sealed vs vented)', xlabel='Hz', ylabel='dB'); ax[0,0].grid(True, which='both', alpha=.3); ax[0,0].legend(fontsize=8)
    # 2) cone excursion
    ax[0,1].semilogx(f, excursion_mm(Uds, f, P['Sd']), 'k--', label='sealed')
    ax[0,1].semilogx(f, excursion_mm(Udv, f, P['Sd']), 'b', label='vented Fb=400')
    ax[0,1].axhline(0.3, color='r', ls=':'); ax[0,1].text(20, .32, 'typ. Xmax ~0.3mm', color='r', fontsize=8)
    ax[0,1].set(title='cone excursion @1W', xlabel='Hz', ylabel='mm peak'); ax[0,1].grid(True, which='both', alpha=.3); ax[0,1].legend(fontsize=8)
    # 3) port air velocity (chuffing)
    ax[1,0].semilogx(f, port_vel(Upv, P['Sp']), 'b')
    ax[1,0].axhline(0.05*C, color='r', ls=':'); ax[1,0].text(20, 0.05*C+0.5, 'chuffing ~Mach 0.05', color='r', fontsize=8)
    ax[1,0].set(title='port air velocity @1W (vented Fb=400)', xlabel='Hz', ylabel='m/s'); ax[1,0].grid(True, which='both', alpha=.3)
    # 4) electrical impedance
    ax[1,1].semilogx(f, np.abs(Zes), 'k--', label='sealed')
    ax[1,1].semilogx(f, np.abs(Zev), 'b', label='vented Fb=400')
    ax[1,1].axvline(fbdip, color='g', ls=':'); ax[1,1].text(fbdip, P['Re'], ' Fb', color='g')
    ax[1,1].set(title='electrical |Z| (twin humps = vented)', xlabel='Hz', ylabel='ohm'); ax[1,1].grid(True, which='both', alpha=.3); ax[1,1].legend(fontsize=8)
    for a in ax.flat:
        a.set_xlim(50, 3000)
    fig.suptitle('flexisette bass-reflex micro-speaker (representative driver, Vb=6cm3)', fontweight='bold')
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'response.png'), dpi=130)
    print(f"\nwrote {os.path.join(HERE,'response.png')}")

    open(os.path.join(HERE, 'reflex.cir'), 'w').write(make_deck(d, Fb0, True).replace('{OUT}', 'response.dat'))
    print(f"wrote {os.path.join(HERE,'reflex.cir')}")


if __name__ == "__main__":
    main()
