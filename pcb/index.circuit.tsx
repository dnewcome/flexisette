/**
 * flexisette — composed board. Each block is a <subcircuit> that routes in
 * isolation (avoids the monolith choke); only inter-block buses route here.
 * Board outline = the real cassette face; the OLED window is a rect cutout at
 * the cassette's tape window (0, +3). Floorplan by signal flow / keep the
 * window + reels clear: display at the window, mcu left, power bottom, audio right.
 */
import React from "react"
import { JLCPCB } from "./lib/fab"
import outline from "./lib/cassette_outline.json"
import cassetteHoles from "./lib/cassette_holes.json"
import { PowerBlock } from "./modules/power.circuit"
import { McuBlock } from "./modules/mcu.circuit"
import { AudioBlock } from "./modules/audio.circuit"
import { DisplayBlock } from "./modules/display.circuit"

export default () => (
  <board outline={outline} layers={2} autorouter="sequential-trace" {...JLCPCB}>
    {/* Real cassette interior holes recovered from the CAD source (cad/panel._rings(),
        cassette STL) — the tape window (OLED glows through it), 2 reel/drive holes, and
        4 corner screw holes. tscircuit's <cutout> exports each as an Edge.Cuts polygon.
        Points are centered on each hole's bbox (pcbX/pcbY = center), like the rect form. */}
    {cassetteHoles.holes.map((pts, i) => {
      const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1])
      const cx = (Math.min(...xs) + Math.max(...xs)) / 2
      const cy = (Math.min(...ys) + Math.max(...ys)) / 2
      const w = Math.max(...xs) - Math.min(...xs), h = Math.max(...ys) - Math.min(...ys)
      const at = { key: i, pcbX: `${cx}mm`, pcbY: `${cy}mm` }
      if (w > 18) // tape window — rect
        return <cutout {...at} name={`WIN${i}`} shape="rect" width={`${w}mm`} height={`${h}mm`} />
      // reels (~11mm) + corner screw holes (~2.5mm) — round
      return <cutout {...at} name={`${w < 5 ? "SCREW" : "REEL"}${i}`} shape="circle" radius={`${w / 2}mm`} />
    })}

    {/* Spread across the whole board, avoiding window(0,3)/reels(±21,3)/notch(bottom-centre)/screws.
        mcu LEFT end (breakout pulled in to clear the left reel), audio RIGHT end (rotated to fit the
        narrow column), power TOP band, display in the strip just below the window. */}
    <McuBlock name="mcu" pcbX={-40} pcbY={2} />
    <PowerBlock name="power" pcbX={2} pcbY={20} />
    <AudioBlock name="audio" pcbX={24} pcbY={-9} />
    <DisplayBlock name="display" pcbX={-2} pcbY={-12} />

    {/* ---- power + ground: bridge each block to the board V3V3/GND nets (via a known cap/connector
         pin on each — tscircuit scopes net.X per subcircuit, so the cross-block link is explicit) ---- */}
    <trace from=".power .C_OUT .pin1" to="net.V3V3" /><trace from=".power .C_OUT .pin2" to="net.GND" />
    <trace from=".mcu .C_BULK .pin1" to="net.V3V3" /><trace from=".mcu .C_BULK .pin2" to="net.GND" />
    <trace from=".audio .C3 .pin1" to="net.V3V3" /><trace from=".audio .C3 .pin2" to="net.GND" />
    <trace from=".display .J_OLED .VCC" to="net.V3V3" /><trace from=".display .J_OLED .GND" to="net.GND" />

    {/* ---- inter-block signal buses: chip-to-board-net (merge_nets.py reconciles the name fragments) ---- */}
    <trace from=".power .USBC .A6" to="net.USB_DP" /><trace from=".mcu .U1 .IO20" to="net.USB_DP" />
    <trace from=".power .USBC .A7" to="net.USB_DM" /><trace from=".mcu .U1 .IO19" to="net.USB_DM" />
    <trace from=".mcu .U1 .IO8" to="net.SDA" /><trace from=".display .J_OLED .SDA" to="net.SDA" />
    <trace from=".mcu .U1 .IO9" to="net.SCL" /><trace from=".display .J_OLED .SCL" to="net.SCL" />
    <trace from=".mcu .U1 .IO5" to="net.BCK" /><trace from=".audio .U2 .BCLK" to="net.BCK" />
    <trace from=".mcu .U1 .IO6" to="net.WS" /><trace from=".audio .U2 .LRCLK" to="net.WS" />
    <trace from=".mcu .U1 .IO7" to="net.DIN" /><trace from=".audio .U2 .DIN" to="net.DIN" />
    <trace from=".mcu .U1 .IO4" to="net.SD" /><trace from=".audio .U2 .SD_MODE" to="net.SD" />

    <copperpour connectsTo="net.GND" layer="bottom" />
  </board>
)
