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

    <Decap name="C1" part="ESP32_S3_WROOM_1_N16R8" ic={U1} pin="3V3" value="100nF" layer="bottom" />

    {/* EN reset + IO0 boot pull-ups only (reset/boot BUTTONS dropped — native-USB esptool resets
        over USB-CDC, no manual buttons needed). 4 small parts in a row above the WROOM, clear of the
        top-left screw hole (x>-44) and the WROOM antenna keepout. */}
    <resistor name="R_EN" resistance="10k" footprint="0402" pcbX={-3} pcbY={26} />
    <capacitor name="C_EN" capacitance="100nF" footprint="0402" pcbX={0} pcbY={26} />
    <resistor name="R_BOOT" resistance="10k" footprint="0402" pcbX={3} pcbY={26} />
    <capacitor name="C_BULK" capacitance="22uF" footprint="0805" pcbX={8} pcbY={26} />

    {/* user buttons (play/pause, next) — BELOW the WROOM body */}
    <Button name="SW_A" pcbX={-5} pcbY={-15} />
    <Button name="SW_B" pcbX={5} pcbY={-15} />

    {/* (breakout header J_IO removed — buses route chip-to-chip via named nets; USB programming) */}

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

    {/* ---- reset / boot ---- */}
    <trace from="U1.EN" to="R_EN.pin1" /><trace from="R_EN.pin2" to="net.V3V3" />
    <trace from="U1.EN" to="C_EN.pin1" /><trace from="C_EN.pin2" to="net.GND" />
    <trace from="U1.IO0" to="R_BOOT.pin1" /><trace from="R_BOOT.pin2" to="net.V3V3" />

    {/* ---- buses on GLOBAL named nets (chip pin only; top level bridges block-to-block) ---- */}
    <trace from="U1.IO20" to="net.USB_DP" /><trace from="U1.IO19" to="net.USB_DM" />
    <trace from="U1.IO8" to="net.SDA" /><trace from="U1.IO9" to="net.SCL" />
    <trace from="U1.IO5" to="net.BCK" /><trace from="U1.IO6" to="net.WS" />
    <trace from="U1.IO7" to="net.DIN" /><trace from="U1.IO4" to="net.SD" />

    {/* ---- user buttons ---- */}
    <trace from="U1.IO10" to="SW_A.A" /><trace from="SW_A.C" to="net.GND" />
    <trace from="U1.IO11" to="SW_B.A" /><trace from="SW_B.C" to="net.GND" />

    <copperpour connectsTo="net.GND" layer="bottom" />
  </subcircuit>
)

export default () => (
  <board width="40mm" height="40mm"><McuBlock /></board>
)
