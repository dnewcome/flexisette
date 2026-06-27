/**
 * MCU module — ESP32-S3-WROOM-1-N16R8 (16MB flash / 8MB PSRAM) + reset/boot +
 * 2 user buttons. Native USB (IO19=D-, IO20=D+) means NO USB-UART bridge — the
 * ROM enumerates as USB-CDC for flashing + audio upload. Buses exit on J_IO.
 *
 *   pin map: I2C SDA=IO8 SCL=IO9 | I2S BCK=IO5 WS=IO6 DIN=IO7 | amp SD=IO4 |
 *            user buttons BTN_A=IO10 BTN_B=IO11 | boot=IO0 reset=EN
 */
import React from "react"
import { JLCPCB } from "../lib/fab"
import { ESP32_S3_WROOM_1_N16R8 } from "../imports/ESP32_S3_WROOM_1_N16R8"
import { TS_1187A_B_A_B as Button } from "../imports/TS_1187A_B_A_B"
import { Decap } from "../lib/place"

const U1 = { x: 0, y: 0 } // module origin in this subcircuit

export const McuBlock = ({ name = "mcu", pcbX = 0, pcbY = 0 }: any) => (
  <subcircuit name={name} pcbX={pcbX} pcbY={pcbY} autorouter="sequential-trace" {...JLCPCB}>
    <ESP32_S3_WROOM_1_N16R8 name="U1" pcbX={0} pcbY={0} />

    {/* 3V3 decoupling — bulk + auto-placed bypass at the real 3V3 pad */}
    <capacitor name="C_BULK" capacitance="22uF" footprint="0805" pcbX={-13} pcbY={9} />
    <Decap name="C1" part="ESP32_S3_WROOM_1_N16R8" ic={U1} pin="3V3" value="100nF" layer="bottom" />

    {/* EN reset: 10k pull-up + 100nF + button to GND */}
    <resistor name="R_EN" resistance="10k" footprint="0402" pcbX={-13} pcbY={5} />
    <capacitor name="C_EN" capacitance="100nF" footprint="0402" pcbX={-13} pcbY={2} />
    <Button name="SW_RST" pcbX={-15} pcbY={-1} />

    {/* IO0 boot strap: 10k pull-up + button to GND */}
    <resistor name="R_BOOT" resistance="10k" footprint="0402" pcbX={-13} pcbY={-5} />
    <Button name="SW_BOOT" pcbX={-15} pcbY={-8} />

    {/* user buttons (play/pause, next) — on the BOTTOM edge, at IO10/IO11 */}
    <Button name="SW_A" pcbX={-4} pcbY={-12} />
    <Button name="SW_B" pcbX={4} pcbY={-12} />

    {/* bus breakout header (right edge) */}
    <pinheader name="J_IO" pinCount={10} footprint="pinrow10" pcbRotation={90} pcbX={15} pcbY={0}
      pinLabels={{
        pin1: "V3V3", pin2: "GND", pin3: "SDA", pin4: "SCL", pin5: "BCK",
        pin6: "WS", pin7: "DIN", pin8: "SD", pin9: "USB_DP", pin10: "USB_DM",
      }} />

    {/* ---- power ---- */}
    <trace from="U1.3V3" to="net.V3V3" />
    <trace from="U1.GND1" to="net.GND" /><trace from="U1.GND2" to="net.GND" />
    <trace from="U1.GND3" to="net.GND" />
    {/* WROOM-1 EPAD (exposed GND/thermal pad under the module): pin41=GND3 above,
        the rest are split paste pads 42-49 — tie them all to GND so the whole pad
        grounds + heat-sinks (the router drops vias to the bottom GND pour). */}
    <trace from="U1.pin42" to="net.GND" /><trace from="U1.pin43" to="net.GND" />
    <trace from="U1.pin44" to="net.GND" /><trace from="U1.pin45" to="net.GND" />
    <trace from="U1.pin46" to="net.GND" /><trace from="U1.pin47" to="net.GND" />
    <trace from="U1.pin48" to="net.GND" /><trace from="U1.pin49" to="net.GND" />
    <trace from="C_BULK.pin1" to="net.V3V3" /><trace from="C_BULK.pin2" to="net.GND" />
    <trace from="C1.pin1" to="net.V3V3" /><trace from="C1.pin2" to="net.GND" />
    <trace from="J_IO.V3V3" to="net.V3V3" /><trace from="J_IO.GND" to="net.GND" />

    {/* ---- reset / boot ---- */}
    <trace from="U1.EN" to="R_EN.pin1" /><trace from="R_EN.pin2" to="net.V3V3" />
    <trace from="U1.EN" to="C_EN.pin1" /><trace from="C_EN.pin2" to="net.GND" />
    <trace from="U1.EN" to="SW_RST.A" /><trace from="SW_RST.C" to="net.GND" />
    <trace from="U1.IO0" to="R_BOOT.pin1" /><trace from="R_BOOT.pin2" to="net.V3V3" />
    <trace from="U1.IO0" to="SW_BOOT.A" /><trace from="SW_BOOT.C" to="net.GND" />

    {/* ---- USB (native) ---- */}
    <trace from="U1.IO20" to="J_IO.USB_DP" /><trace from="U1.IO19" to="J_IO.USB_DM" />

    {/* ---- I2C / I2S / amp-enable buses ---- */}
    <trace from="U1.IO8" to="J_IO.SDA" /><trace from="U1.IO9" to="J_IO.SCL" />
    <trace from="U1.IO5" to="J_IO.BCK" /><trace from="U1.IO6" to="J_IO.WS" />
    <trace from="U1.IO7" to="J_IO.DIN" /><trace from="U1.IO4" to="J_IO.SD" />

    {/* ---- user buttons ---- */}
    <trace from="U1.IO10" to="SW_A.A" /><trace from="SW_A.C" to="net.GND" />
    <trace from="U1.IO11" to="SW_B.A" /><trace from="SW_B.C" to="net.GND" />

    <copperpour connectsTo="net.GND" layer="bottom" />
  </subcircuit>
)

export default () => (
  <board width="40mm" height="40mm"><McuBlock /></board>
)
