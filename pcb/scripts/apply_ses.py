#!/usr/bin/env python3
"""apply_ses.py <kicad_pcb> <ses> [out] — write a Freerouting .ses into a KiCad board, headless.

KiCad's own SES import is unusable here (kicad-cli has no specctra; headless
pcbnew.ImportSpecctraSES throws a SWIG error; no xvfb to run the GUI). So we apply
the routes ourselves: rip the existing tracks, then for every wire/via in the SES
create a KiCad track/via — net by (refdes,pad) lookup, geometry by the measured
tscircuit-DSN -> KiCad transform. Result: a fully-routed .kicad_pcb in one command.

Transform (verified consistent across all parts): ses units -> mm = /10000, then
  kicad_x = ses_x + 100 ;  kicad_y = 100 - ses_y   (Specctra Y-flip).
The SES must have tscircuit's "_source_component_N" ids stripped (freeroute.sh does it)
so "Net-(REF-PadN)" carries the real refdes.
"""
import os
import re
import sys

sys.path.insert(0, "/usr/lib/python3/dist-packages")
import pcbnew

PCB = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "index.circuit.kicad_pcb")
SES = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else "build/index.fixed.ses")
OUT = os.path.abspath(sys.argv[3] if len(sys.argv) > 3 else PCB.replace(".kicad_pcb", "_routed.kicad_pcb"))

S = 1 / 10000.0  # SES units -> mm


def tx(x, y):  # SES units -> KiCad mm
    return (x * S + 100.0, 100.0 - y * S)


def mm(v):
    return pcbnew.FromMM(v)


board = pcbnew.LoadBoard(PCB)
LAYER = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}

# (refdes, padname) -> netcode, and netname -> netcode (for named nets)
pad_net = {}
for f in board.GetFootprints():
    ref = f.GetReference()
    for p in f.Pads():
        pad_net[(ref, p.GetPadName())] = p.GetNetCode()
name_net = {n: ni.GetNetCode() for n, ni in board.GetNetInfo().NetsByName().items()}

# rip existing (tscircuit) routing; keep footprints + zones
for t in list(board.GetTracks()):
    board.Remove(t)

ses = open(SES).read()
ses = ses[ses.index("(network_out"):]
blocks = re.split(r'\(net\s+"', ses)[1:]

added_t = added_v = skipped = 0
for blk in blocks:
    name = blk[: blk.index('"')]
    m = re.match(r"Net-\((\w+)-Pad(\w+)\)$", name)
    if m:
        netcode = pad_net.get((m.group(1), m.group(2)))
    else:
        netcode = name_net.get(name)
    if netcode is None:
        skipped += 1
        continue
    for w in re.finditer(r"\(path\s+(F\.Cu|B\.Cu)\s+(\d+)\s+([-\d\s]+?)\)", blk):
        layer = LAYER[w.group(1)]
        width = int(w.group(2)) * S
        nums = [float(v) for v in w.group(3).split()]
        pts = [tx(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        for i in range(len(pts) - 1):
            tr = pcbnew.PCB_TRACK(board)
            tr.SetStart(pcbnew.VECTOR2I(mm(pts[i][0]), mm(pts[i][1])))
            tr.SetEnd(pcbnew.VECTOR2I(mm(pts[i + 1][0]), mm(pts[i + 1][1])))
            tr.SetWidth(mm(width))
            tr.SetLayer(layer)
            tr.SetNetCode(netcode)
            board.Add(tr)
            added_t += 1
    for v in re.finditer(r'\(via\s+"Via\[0-1\]_(\d+):(\d+)_um"\s+(-?\d+)\s+(-?\d+)', blk):
        kx, ky = tx(float(v.group(3)), float(v.group(4)))
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(mm(kx), mm(ky)))
        via.SetWidth(mm(int(v.group(1)) / 1000.0))
        via.SetDrill(mm(int(v.group(2)) / 1000.0))
        via.SetNetCode(netcode)
        board.Add(via)
        added_v += 1

pcbnew.ZONE_FILLER(board).Fill(board.Zones())  # refill GND pours after re-routing
pcbnew.SaveBoard(OUT, board)
open("build/apply_ses_result.txt", "w").write(
    f"injected {added_t} segments + {added_v} vias ({skipped} nets skipped) -> {OUT}\n")
