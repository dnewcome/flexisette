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

# ---- primary T-S params: PUI Audio AS01808AO (18x13mm face-firing micro-speaker) ----
# Fs / Re / power are PUBLISHED; Vas, Qts, Sd, Xmax are ESTIMATES from the cone size pending a
# real DATS / impedance-sweep measurement (the numbers below are provisional, flag accordingly).
P = dict(
    Sd=1.6e-4,    # ~1.6 cm2 effective (18x13mm face)            [estimate]
    Fs=320.0,     # free-air resonance, Hz                        [PUBLISHED]
    Vas=12e-6,    # equivalent compliance volume, m^3 (12 cm3)    [estimate]
    Qts=1.0, Qms=3.0,                                          #  [estimate]
    Re=8.0, Le=0.10e-3,                                        #  [PUBLISHED Z; Le estimate]
    Vb=8e-6,      # sealed back-volume, m^3 (nominal 8 cm3 carved from the insert+interior)
    Sp=9.6e-6, Qp=15.0,    # (port elements unused now -- SEALED design)
    eg=2.83,      # 1 W into 8 ohm -> SPL@1m + excursion
    Xmax=0.35,    # mm peak linear excursion                      [estimate]
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

    rho_c2 = RHO * C * C
    sealed_at = lambda Vb: solve_analytic({**d, 'Cab': Vb / rho_c2}, f, Fb0, vented=False)
    fc_qtc = lambda Vb: (P['Fs'] * np.sqrt(1 + P['Vas'] / Vb), P['Qts'] * np.sqrt(1 + P['Vas'] / Vb))

    # verify the SEALED deck: ngspice vs analytic
    fn, Udn, _ = run_ngspice(make_deck(d, Fb0, vented=False))
    Uda, _, _ = solve_analytic(d, fn, Fb0, vented=False)
    err = np.max(np.abs(np.abs(Udn) - np.abs(Uda)) / (np.abs(Uda) + 1e-30))
    print(f"\n[verify] sealed ngspice vs analytic |Ud| max rel-err = {err*100:.2f}% ({'MATCH' if err<0.02 else 'CHECK'})")

    Vbs = np.array([4, 6, 8, 12, 18]) * 1e-6
    Vnom = P['Vb']
    Ud0, _, _ = sealed_at(Vnom)
    print("\n=== SEALED face-firing design (PUI AS01808AO; Vas/Qts ESTIMATED — measure to confirm) ===")
    for Vb in Vbs:
        fc, qtc = fc_qtc(Vb)
        print(f"  Vb={Vb*1e6:4.0f} cm3 -> Fc={fc:4.0f} Hz, Qtc={qtc:.2f}{'  (peaky/boomy)' if qtc>1.1 else ''}")
    spl_pass = np.median(spl(Ud0, f)[(f > 1500) & (f < 3000)])
    maxexc = np.max(excursion_mm(Ud0, f, P['Sd']))
    clean_W = (P['Xmax'] / maxexc) ** 2
    print(f"  passband SPL ~{spl_pass:.0f} dB@1m | EXCURSION-limited: {maxexc:.2f}mm@1W vs {P['Xmax']}mm Xmax "
          f"-> ~{clean_W*1000:.0f} mW clean (~{spl_pass+10*np.log10(clean_W):.0f} dB@1m)")
    print(f"  Fs 320Hz (real driver) drops the box knee FAR below the 1.1kHz placeholder -> a real low-mid lift")
    print(f"  recommend: carve max back-volume (~10-12cm3) -> Fc ~{fc_qtc(11e-6)[0]:.0f}Hz, Qtc ~{fc_qtc(11e-6)[1]:.2f}"
          f"{' (estimated Qts high -> may be boomy; measure)' if fc_qtc(11e-6)[1]>1.1 else ''}")

    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    cols = plt.cm.viridis(np.linspace(0, .9, len(Vbs)))
    # 1) sealed SPL vs back-volume
    for Vb, c in zip(Vbs, cols):
        Ud, _, _ = sealed_at(Vb)
        ax[0,0].semilogx(f, spl(Ud, f), color=c, lw=1.8, label=f'Vb={Vb*1e6:.0f}cm3 (Fc {fc_qtc(Vb)[0]:.0f}Hz)')
    ax[0,0].set(title='sealed SPL @1m, 1W vs back-volume', xlabel='Hz', ylabel='dB'); ax[0,0].grid(True, which='both', alpha=.3); ax[0,0].legend(fontsize=8)
    # 2) cone excursion at nominal Vb
    ax[0,1].semilogx(f, excursion_mm(Ud0, f, P['Sd']), 'b')
    ax[0,1].axhline(P['Xmax'], color='r', ls=':'); ax[0,1].text(55, P['Xmax']+.02, f"Xmax {P['Xmax']}mm", color='r', fontsize=8)
    ax[0,1].set(title=f'cone excursion @1W (Vb={Vnom*1e6:.0f}cm3)', xlabel='Hz', ylabel='mm peak'); ax[0,1].grid(True, which='both', alpha=.3)
    # 3) Fc & Qtc vs back-volume (the one design knob)
    vv = np.linspace(3, 25, 80) * 1e-6
    ax[1,0].plot(vv*1e6, [fc_qtc(v)[0] for v in vv], 'b-')
    ax[1,0].set(title='sealed Fc & Qtc vs back-volume', xlabel='back-volume (cm3)', ylabel='Fc (Hz)'); ax[1,0].grid(True, alpha=.3)
    a2 = ax[1,0].twinx(); a2.plot(vv*1e6, [fc_qtc(v)[1] for v in vv], 'g--'); a2.axhline(0.7, color='g', ls=':', alpha=.6)
    a2.set_ylabel('Qtc (green)', color='g')
    # 4) sealed electrical |Z| per Vb
    for Vb, c in zip(Vbs, cols):
        _, _, Ze = sealed_at(Vb); ax[1,1].semilogx(f, np.abs(Ze), color=c, lw=1.4)
    ax[1,1].set(title='sealed electrical |Z|', xlabel='Hz', ylabel='ohm'); ax[1,1].grid(True, which='both', alpha=.3)
    for a in (ax[0,0], ax[0,1], ax[1,1]):
        a.set_xlim(50, 5000)
    fig.suptitle('flexisette SEALED face-firing micro-speaker — PUI AS01808AO (Vas/Qts estimated)', fontweight='bold')
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'sealed.png'), dpi=130)
    print(f"\nwrote {os.path.join(HERE,'sealed.png')}")
    open(os.path.join(HERE, 'reflex.cir'), 'w').write(make_deck(d, Fb0, vented=False).replace('{OUT}', 'response.dat'))


if __name__ == "__main__":
    main()
