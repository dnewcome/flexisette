/**
 * Audio module — MAX98357A I2S class-D amp straight into a speaker. No DAC or
 * reconstruction filter: the amp takes I2S directly and drives the speaker BTL.
 * Mono via SD_MODE biased >1.4V (= Left). SD line also breaks out so the MCU can
 * mute/shutdown. Powered from V3V3 (~1W/4ohm); move VDD to VSYS for more volume.
 */
import React from "react"
import { JLCPCB } from "../lib/fab"
import { MAX98357AETE_T } from "../imports/MAX98357AETE_T"
import { S2B_PH_SM4_TB_LF__SN_ as JstPH } from "../imports/S2B_PH_SM4_TB_LF__SN_"

export const AudioBlock = ({ name = "audio", pcbX = 0, pcbY = 0 }: any) => (
  <subcircuit name={name} pcbX={pcbX} pcbY={pcbY} autorouter="sequential-trace" {...JLCPCB}>
    <MAX98357AETE_T name="U2" pcbX={0} pcbY={0} />
    {/* VDD decoupling */}
    <capacitor name="C3" capacitance="10uF" footprint="0805" pcbX={-5} pcbY={4} />
    {/* VDD bypass — right of U2, clear of J_I2S pin6 and the C3 bulk cap */}
    <capacitor name="C2" capacitance="100nF" footprint="0402" pcbX={3} pcbY={4} />
    {/* SD_MODE pulldown — amp off at boot until the MCU drives it high (=Left) */}
    <resistor name="R3" resistance="100k" footprint="0402" pcbX={-5} pcbY={-3} />

    {/* (breakout header J_I2S removed — I2S routes from the MCU via named nets) */}
    {/* speaker out (2-pin JST; pin1/pin2 = contacts) */}
    <JstPH name="J_SPK" pcbX={9} pcbY={0} />

    {/* power */}
    <trace from="U2.VDD1" to="net.V3V3" /><trace from="U2.VDD2" to="net.V3V3" />
    <trace from="U2.GND1" to="net.GND" /><trace from="U2.GND2" to="net.GND" />
    <trace from="U2.GND3" to="net.GND" /><trace from="U2.EP" to="net.GND" />
    <trace from="C3.pin1" to="net.V3V3" /><trace from="C3.pin2" to="net.GND" />
    <trace from="C2.pin1" to="net.V3V3" /><trace from="C2.pin2" to="net.GND" />

    {/* I2S on GLOBAL named nets (chip pin only; top level bridges to the MCU) */}
    <trace from="U2.BCLK" to="net.BCK" /><trace from="U2.LRCLK" to="net.WS" />
    <trace from="U2.DIN" to="net.DIN" />
    {/* SD enable + pulldown (amp SD_MODE on the global net.SD) */}
    <trace from="U2.SD_MODE" to="net.SD" />
    <trace from="R3.pin1" to="net.SD" /><trace from="R3.pin2" to="net.GND" />

    {/* speaker (GAIN_SLOT left floating = 9dB) */}
    <trace from="U2.OUTP" to="J_SPK.pin1" /><trace from="U2.OUTN" to="J_SPK.pin2" />

    <copperpour connectsTo="net.GND" layer="bottom" />
  </subcircuit>
)

export default () => (
  <board width="34mm" height="22mm"><AudioBlock /></board>
)
