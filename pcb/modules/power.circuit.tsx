/**
 * Power module — USB-C 5V -> TP4056 LiPo charger -> AO3401 load-share -> ME6211
 * low-dropout 3V3. VSYS = USB (through Schottky D1) when plugged, else battery
 * (through P-FET Q1, oriented so its body diode can't back-charge the cell).
 * Native USB D+/D- pass through to the MCU. Outputs break out on J_PWR.
 */
import React from "react"
import { JLCPCB } from "../lib/fab"
import { TYPE_C_31_M_12 } from "../imports/TYPE_C_31_M_12"
import { TP4056_42_ESOP8 } from "../imports/TP4056_42_ESOP8"
import { AO3401A } from "../imports/AO3401A"
import { B5819W_SL } from "../imports/B5819W_SL"
import { ME6211C33M5G_N } from "../imports/ME6211C33M5G_N"
import { S2B_PH_SM4_TB_LF__SN_ as JstPH } from "../imports/S2B_PH_SM4_TB_LF__SN_"

export const PowerBlock = ({ name = "power", pcbX = 0, pcbY = 0 }: any) => (
  <subcircuit name={name} pcbX={pcbX} pcbY={pcbY} autorouter="sequential-trace" {...JLCPCB}>
    <TYPE_C_31_M_12 name="USBC" pcbX={-21} pcbY={0} />
    <resistor name="R_CC1" resistance="5.1k" footprint="0402" pcbX={-22} pcbY={4} />
    <resistor name="R_CC2" resistance="5.1k" footprint="0402" pcbX={-19} pcbY={4} />

    {/* charger — stitch the ESOP8 thermal pad (GND) down to the bottom pour */}
    <TP4056_42_ESOP8 name="U_CHG" pcbX={-7} pcbY={0} />
    <via name="GV_CHG" connectsTo="net.GND" fromLayer="top" toLayer="bottom" pcbX={-7} pcbY={0} />
    <resistor name="R_PROG" resistance="2k" footprint="0402" pcbX={-7} pcbY={-5} />
    <capacitor name="C_BAT" capacitance="10uF" footprint="0805" pcbX={-3} pcbY={-5} />
    <JstPH name="J_BAT" pcbX={19} pcbY={5} />

    {/* load share: D1 (USB->SYS), Q1 P-FET (BAT->SYS when USB off) */}
    <B5819W_SL name="D1" pcbX={1} pcbY={5} />
    <AO3401A name="Q1" pcbX={1} pcbY={0} />
    <resistor name="R_G" resistance="100k" footprint="0402" pcbX={1} pcbY={-5} />

    {/* LDO 3V3 */}
    <ME6211C33M5G_N name="U_LDO" pcbX={8} pcbY={0} />
    <capacitor name="C_IN" capacitance="1uF" footprint="0402" pcbX={6} pcbY={4} />
    <capacitor name="C_OUT" capacitance="1uF" footprint="0402" pcbX={11} pcbY={4} />
    <capacitor name="C5" capacitance="22uF" footprint="0805" pcbX={11} pcbY={-4} />

    {/* (breakout header J_PWR removed — V3V3/GND/USB route via named nets to the other blocks) */}

    {/* USB-C: VBUS, GND, shield, CC pulldowns, D+/- (both orientations tied) */}
    <trace from="USBC.A4B9" to="net.VBUS" /><trace from="USBC.B4A9" to="net.VBUS" />
    <trace from="USBC.A1B12" to="net.GND" /><trace from="USBC.B1A12" to="net.GND" />
    <trace from="USBC.EH1" to="net.GND" /><trace from="USBC.EH2" to="net.GND" />
    <trace from="USBC.EH3" to="net.GND" /><trace from="USBC.EH4" to="net.GND" />
    <trace from="USBC.A5" to="R_CC1.pin1" /><trace from="R_CC1.pin2" to="net.GND" />
    <trace from="USBC.B5" to="R_CC2.pin1" /><trace from="R_CC2.pin2" to="net.GND" />
    <trace from="USBC.A6" to="net.USB_DP" /><trace from="USBC.B6" to="net.USB_DP" />
    <trace from="USBC.A7" to="net.USB_DM" /><trace from="USBC.B7" to="net.USB_DM" />

    {/* charger */}
    <trace from="U_CHG.VCC" to="net.VBUS" /><trace from="U_CHG.CE" to="net.VBUS" />
    <trace from="U_CHG.GND" to="net.GND" /><trace from="U_CHG.EP" to="net.GND" />
    <trace from="U_CHG.TEMP" to="net.GND" />
    <trace from="U_CHG.PROG" to="R_PROG.pin1" /><trace from="R_PROG.pin2" to="net.GND" />
    <trace from="U_CHG.BAT" to="net.VBAT" />
    <trace from="C_BAT.pin1" to="net.VBAT" /><trace from="C_BAT.pin2" to="net.GND" />
    <trace from="J_BAT.pin1" to="net.VBAT" /><trace from="J_BAT.pin2" to="net.GND" />

    {/* load share */}
    <trace from="D1.pin1" to="net.VBUS" /><trace from="D1.pin2" to="net.VSYS" />
    <trace from="Q1.S" to="net.VSYS" /><trace from="Q1.D" to="net.VBAT" /><trace from="Q1.G" to="net.VBUS" />
    <trace from="R_G.pin1" to="net.VBUS" /><trace from="R_G.pin2" to="net.GND" />

    {/* LDO */}
    <trace from="U_LDO.VIN" to="net.VSYS" /><trace from="U_LDO.CE" to="net.VSYS" />
    <trace from="U_LDO.VSS" to="net.GND" /><trace from="U_LDO.VOUT" to="net.V3V3" />
    <trace from="C_IN.pin1" to="net.VSYS" /><trace from="C_IN.pin2" to="net.GND" />
    <trace from="C_OUT.pin1" to="net.V3V3" /><trace from="C_OUT.pin2" to="net.GND" />
    <trace from="C5.pin1" to="net.V3V3" /><trace from="C5.pin2" to="net.GND" />

    {/* V3V3/GND/USB are on named nets; the top level bridges them to the mcu/audio/display blocks */}

    <copperpour connectsTo="net.GND" layer="bottom" />
  </subcircuit>
)

export default () => (
  <board width="48mm" height="26mm"><PowerBlock /></board>
)
