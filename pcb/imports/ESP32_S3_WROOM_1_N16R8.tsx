import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["GND1"],
  pin2: ["3V3"],
  pin3: ["EN"],
  pin4: ["IO4"],
  pin5: ["IO5"],
  pin6: ["IO6"],
  pin7: ["IO7"],
  pin8: ["IO15"],
  pin9: ["IO16"],
  pin10: ["IO17"],
  pin11: ["IO18"],
  pin12: ["IO8"],
  pin13: ["IO19"],
  pin14: ["IO20"],
  pin15: ["IO3"],
  pin16: ["IO46"],
  pin17: ["IO9"],
  pin18: ["IO10"],
  pin19: ["IO11"],
  pin20: ["IO12"],
  pin21: ["IO13"],
  pin22: ["IO14"],
  pin23: ["IO21"],
  pin24: ["IO47"],
  pin25: ["IO48"],
  pin26: ["IO45"],
  pin27: ["IO0"],
  pin28: ["IO35"],
  pin29: ["IO36"],
  pin30: ["IO37"],
  pin31: ["IO38"],
  pin32: ["IO39"],
  pin33: ["IO40"],
  pin34: ["IO41"],
  pin35: ["IO42"],
  pin36: ["RXD0"],
  pin37: ["TXD0"],
  pin38: ["IO2"],
  pin39: ["IO1"],
  pin40: ["GND2"],
  pin41: ["GND3"],
  pin42: ["pin41_alt1"],
  pin43: ["pin41_alt1"],
  pin44: ["pin41_alt1"],
  pin45: ["pin41_alt1"],
  pin46: ["pin41_alt1"],
  pin47: ["pin41_alt1"],
  pin48: ["pin41_alt1"],
  pin49: ["pin41_alt1"]
} as const

export const ESP32_S3_WROOM_1_N16R8 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C2913202"
  ]
}}
      manufacturerPartNumber="ESP32_S3_WROOM_1_N16R8"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-8.750046mm" pcbY="9.0449527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-8.750046mm" pcbY="7.7749527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-8.750046mm" pcbY="6.5049527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-8.750046mm" pcbY="5.2349527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="-8.750046mm" pcbY="3.9649527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="-8.750046mm" pcbY="2.6949527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="-8.750046mm" pcbY="1.4249527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="-8.750046mm" pcbY="0.1549527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="-8.750046mm" pcbY="-1.1150473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="-8.750046mm" pcbY="-2.3850473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="-8.750046mm" pcbY="-3.6550473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin12"]} pcbX="-8.750046mm" pcbY="-4.9250473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin13"]} pcbX="-8.750046mm" pcbY="-6.1950473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin14"]} pcbX="-8.750046mm" pcbY="-7.4650473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin15"]} pcbX="-6.985mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin16"]} pcbX="-5.715mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin17"]} pcbX="-4.445mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin18"]} pcbX="-3.175mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin19"]} pcbX="-1.905mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin20"]} pcbX="-0.635mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin21"]} pcbX="0.635mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin22"]} pcbX="1.905mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin23"]} pcbX="3.175mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin24"]} pcbX="4.445mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin25"]} pcbX="5.715mm" pcbY="-8.7449533mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin26"]} pcbX="6.985mm" pcbY="-8.7149813mm" width="0.8999982mm" height="1.499997mm" shape="rect" />
<smtpad portHints={["pin27"]} pcbX="8.750046mm" pcbY="-7.4650473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin28"]} pcbX="8.750046mm" pcbY="-6.1950473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin29"]} pcbX="8.750046mm" pcbY="-4.9250473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin30"]} pcbX="8.750046mm" pcbY="-3.6550473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin31"]} pcbX="8.750046mm" pcbY="-2.3850473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin32"]} pcbX="8.750046mm" pcbY="-1.1150473mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin33"]} pcbX="8.750046mm" pcbY="0.1549527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin34"]} pcbX="8.750046mm" pcbY="1.4249527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin35"]} pcbX="8.750046mm" pcbY="2.6949527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin36"]} pcbX="8.750046mm" pcbY="3.9649527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin37"]} pcbX="8.750046mm" pcbY="5.2349527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin38"]} pcbX="8.750046mm" pcbY="6.5049527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin39"]} pcbX="8.750046mm" pcbY="7.7749527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin40"]} pcbX="8.750046mm" pcbY="9.0449527mm" width="1.499997mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin41"]} pcbX="-0.100076mm" pcbY="-0.0751713mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin42"]} pcbX="-1.500124mm" pcbY="-0.0751713mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin43"]} pcbX="-2.900172mm" pcbY="-0.0751713mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin44"]} pcbX="-2.900172mm" pcbY="2.7249247mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin45"]} pcbX="-1.500124mm" pcbY="2.7249247mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin46"]} pcbX="-0.100076mm" pcbY="2.7249247mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin47"]} pcbX="-0.100076mm" pcbY="1.3248767mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin48"]} pcbX="-2.900172mm" pcbY="1.3248767mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin49"]} pcbX="-1.500124mm" pcbY="1.3248767mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<silkscreenpath route={[{"x":7.297165999999947,"y":10.505351100000212},{"x":7.297165999999947,"y":15.38994890000015},{"x":5.061966000000098,"y":15.38994890000015}]} />
<silkscreenpath route={[{"x":5.265165999999795,"y":10.505351100000212},{"x":5.265165999999795,"y":15.38994890000015},{"x":2.4129999999998972,"y":15.38994890000015},{"x":2.4129999999998972,"y":13.230948900000158},{"x":-0.1270000000000664,"y":13.230948900000158},{"x":-0.1270000000000664,"y":15.38994890000015},{"x":-2.66700000000003,"y":15.38994890000015},{"x":-2.66700000000003,"y":13.230948900000158},{"x":-4.953000000000088,"y":13.230948900000158},{"x":-4.953000000000088,"y":15.38994890000015},{"x":-7.239000000000033,"y":15.38994890000015},{"x":-7.239000000000033,"y":11.706948900000157}]} />
<silkscreenpath route={[{"x":-9.000007400000186,"y":10.505351100000212},{"x":9.016999999999939,"y":10.505351100000212}]} />
<silkscreenpath route={[{"x":9.016999999999939,"y":9.726104500000133},{"x":9.016999999999939,"y":16.53294890000018}]} />
<silkscreenpath route={[{"x":7.666151799999966,"y":-8.994051099999865},{"x":9.016999999999939,"y":-8.994051099999865},{"x":9.016999999999939,"y":-8.14619909999999}]} />
<silkscreenpath route={[{"x":-9.000007400000186,"y":-8.14619909999999},{"x":-9.000007400000186,"y":-8.994051099999865},{"x":-7.66615180000008,"y":-8.994051099999865}]} />
<silkscreenpath route={[{"x":-9.000007400000186,"y":16.544963100000018},{"x":-9.000007400000186,"y":9.726104500000133}]} />
<silkscreenpath route={[{"x":9.000007400000072,"y":16.544963100000018},{"x":-9.000007400000186,"y":16.544963100000018}]} />
<silkscreentext text="{NAME}" pcbX="-0mm" pcbY="17.5633527mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-9.7496000000001,"y":16.813352699999996},{"x":9.749599999999987,"y":16.813352699999996},{"x":9.749599999999987,"y":-9.74704729999985},{"x":-9.7496000000001,"y":-9.74704729999985},{"x":-9.7496000000001,"y":16.813352699999996}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C2913202.obj?uuid=ff306e3ed51d4ebc94ebabcd1b4d8906",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C2913202.step?uuid=ff306e3ed51d4ebc94ebabcd1b4d8906",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: -3.8004924000000644, z: -0.01 },
      }}
      {...props}
    />
  )
}