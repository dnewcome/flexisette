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
import { PowerBlock } from "./modules/power.circuit"
import { McuBlock } from "./modules/mcu.circuit"
import { AudioBlock } from "./modules/audio.circuit"
import { DisplayBlock } from "./modules/display.circuit"

export default () => (
  <board outline={outline} layers={2} autorouter="sequential-trace" {...JLCPCB}>
    {/* OLED window — the SSD1306 glows through here (tape window) */}
    <cutout name="WIN1" shape="rect" width="22.5mm" height="13mm" pcbX="0mm" pcbY="3mm" />

    <DisplayBlock name="display" pcbX={0} pcbY={-11} />
    <McuBlock name="mcu" pcbX={-29} pcbY={-1} />
    <PowerBlock name="power" pcbX={3} pcbY={20} />
    <AudioBlock name="audio" pcbX={31} pcbY={2} />

    {/* ---- power distribution ---- */}
    <trace from=".power .J_PWR .V3V3" to="net.V3V3" />
    <trace from=".mcu .J_IO .V3V3" to="net.V3V3" />
    <trace from=".audio .J_I2S .V3V3" to="net.V3V3" />
    <trace from=".display .J_OLED .VCC" to="net.V3V3" />
    <trace from=".power .J_PWR .GND" to="net.GND" />
    <trace from=".mcu .J_IO .GND" to="net.GND" />
    <trace from=".audio .J_I2S .GND" to="net.GND" />
    <trace from=".display .J_OLED .GND" to="net.GND" />

    {/* ---- USB data: power -> mcu ---- */}
    <trace from=".power .J_PWR .USB_DP" to=".mcu .J_IO .USB_DP" />
    <trace from=".power .J_PWR .USB_DM" to=".mcu .J_IO .USB_DM" />

    {/* ---- I2C: mcu -> display ---- */}
    <trace from=".mcu .J_IO .SDA" to=".display .J_OLED .SDA" />
    <trace from=".mcu .J_IO .SCL" to=".display .J_OLED .SCL" />

    {/* ---- I2S + amp enable: mcu -> audio ---- */}
    <trace from=".mcu .J_IO .BCK" to=".audio .J_I2S .BCK" />
    <trace from=".mcu .J_IO .WS" to=".audio .J_I2S .WS" />
    <trace from=".mcu .J_IO .DIN" to=".audio .J_I2S .DIN" />
    <trace from=".mcu .J_IO .SD" to=".audio .J_I2S .SD" />

    <copperpour connectsTo="net.GND" layer="bottom" />
  </board>
)
