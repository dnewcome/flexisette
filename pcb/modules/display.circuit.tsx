/**
 * Display module — 0.96" SSD1306 OLED (I2C), mounted BEHIND the board so it
 * glows through the cassette tape-window cutout. The 4-pin header IS the OLED
 * connector AND the bus interface (MCU drives SDA/SCL on the same pins).
 */
import React from "react"
import { JLCPCB } from "../lib/fab"

export const DisplayBlock = ({ name = "display", pcbX = 0, pcbY = 0 }: any) => (
  <subcircuit name={name} pcbX={pcbX} pcbY={pcbY} autorouter="sequential-trace" {...JLCPCB}>
    {/* the OLED module plugs in here (GND/VCC/SCL/SDA — the common 4-pin order) */}
    <pinheader name="J_OLED" pinCount={4} footprint="pinrow4" pcbX={0} pcbY={0}
      pinLabels={{ pin1: "GND", pin2: "VCC", pin3: "SCL", pin4: "SDA" }} />
    {/* I2C pullups */}
    <resistor name="R1" resistance="4.7k" footprint="0402" pcbX={-3} pcbY={6} />
    <resistor name="R2" resistance="4.7k" footprint="0402" pcbX={3} pcbY={6} />

    <trace from="J_OLED.GND" to="net.GND" />
    <trace from="J_OLED.VCC" to="net.V3V3" />
    <trace from="J_OLED.SCL" to="net.SCL" />
    <trace from="J_OLED.SDA" to="net.SDA" />
    <trace from="R1.pin1" to="net.SDA" /><trace from="R1.pin2" to="net.V3V3" />
    <trace from="R2.pin1" to="net.SCL" /><trace from="R2.pin2" to="net.V3V3" />

    <copperpour connectsTo="net.GND" layer="bottom" />
  </subcircuit>
)

export default () => (
  <board width="20mm" height="16mm"><DisplayBlock /></board>
)
