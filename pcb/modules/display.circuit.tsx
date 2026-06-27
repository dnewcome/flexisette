/**
 * Display module — 0.96" SSD1306 OLED (I2C), mounted BEHIND the board so it
 * glows through the cassette tape-window cutout. The 4-pin header IS the OLED
 * connector AND the bus interface (MCU drives SDA/SCL on the same pins).
 */
import React from "react"
import { JLCPCB } from "../lib/fab"

export const DisplayBlock = ({ name = "display", pcbX = 0, pcbY = 0 }: any) => (
  <subcircuit name={name} pcbX={pcbX} pcbY={pcbY} autorouter="sequential-trace" {...JLCPCB}>
    {/* The 0.96" SSD1306 OLED MODULE as a real placed part, mounted on the BACK so its screen shows
        through the tape-window cutout. Its 4-pin header (GND/VCC/SCL/SDA) solders here; the 27×27mm
        body outline (silkscreen) sits over the window so the drawing reserves/shows where it lives.
        Pads at the chip origin; body offset +14mm up so it centres on the window. */}
    <chip name="OLED" layer="bottom" pcbX={2} pcbY={2}
      pinLabels={{ pin1: "GND", pin2: "VCC", pin3: "SCL", pin4: "SDA" }}
      footprint={
        <footprint>
          <platedhole portHints={["pin1"]} pcbX="-3.81mm" pcbY="0mm" outerDiameter="1.7mm" holeDiameter="1.0mm" shape="circle" />
          <platedhole portHints={["pin2"]} pcbX="-1.27mm" pcbY="0mm" outerDiameter="1.7mm" holeDiameter="1.0mm" shape="circle" />
          <platedhole portHints={["pin3"]} pcbX="1.27mm" pcbY="0mm" outerDiameter="1.7mm" holeDiameter="1.0mm" shape="circle" />
          <platedhole portHints={["pin4"]} pcbX="3.81mm" pcbY="0mm" outerDiameter="1.7mm" holeDiameter="1.0mm" shape="circle" />
          <silkscreenrect pcbX="0mm" pcbY="13mm" width="27mm" height="27mm" />
          <silkscreentext text="OLED 0.96in" pcbX="0mm" pcbY="13mm" fontSize="1.6mm" />
        </footprint>
      } />
    {/* I2C pullups */}
    <resistor name="R1" resistance="4.7k" footprint="0402" pcbX={-3} pcbY={6} />
    <resistor name="R2" resistance="4.7k" footprint="0402" pcbX={3} pcbY={6} />

    <trace from="OLED.GND" to="net.GND" />
    <trace from="OLED.VCC" to="net.V3V3" />
    <trace from="OLED.SCL" to="net.SCL" />
    <trace from="OLED.SDA" to="net.SDA" />
    <trace from="R1.pin1" to="net.SDA" /><trace from="R1.pin2" to="net.V3V3" />
    <trace from="R2.pin1" to="net.SCL" /><trace from="R2.pin2" to="net.V3V3" />

    <copperpour connectsTo="net.GND" layer="bottom" />
  </subcircuit>
)

export default () => (
  <board width="20mm" height="16mm"><DisplayBlock /></board>
)
