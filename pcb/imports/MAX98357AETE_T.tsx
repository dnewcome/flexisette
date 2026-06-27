import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["DIN"],
  pin2: ["GAIN_SLOT"],
  pin3: ["GND1"],
  pin4: ["SD_MODE"],
  pin5: ["pin5"],
  pin6: ["pin6"],
  pin7: ["VDD1"],
  pin8: ["VDD2"],
  pin9: ["OUTP"],
  pin10: ["OUTN"],
  pin11: ["GND2"],
  pin12: ["pin12"],
  pin13: ["pin13"],
  pin14: ["LRCLK"],
  pin15: ["GND3"],
  pin16: ["BCLK"],
  pin17: ["EP"]
} as const

export const MAX98357AETE_T = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C910544"
  ]
}}
      manufacturerPartNumber="MAX98357AETE_T"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-0.748411mm" pcbY="-1.499997mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-0.248539mm" pcbY="-1.499997mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="0.251587mm" pcbY="-1.499997mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="0.751459mm" pcbY="-1.499997mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="1.499997mm" pcbY="-0.747903mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="1.499997mm" pcbY="-0.248031mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="1.499997mm" pcbY="0.252095mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="1.499997mm" pcbY="0.751967mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="0.749935mm" pcbY="1.499997mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="0.250063mm" pcbY="1.499997mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="-0.250063mm" pcbY="1.499997mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin12"]} pcbX="-0.748411mm" pcbY="1.499997mm" width="0.2500122mm" height="0.5999988mm" shape="rect" />
<smtpad portHints={["pin13"]} pcbX="-1.499997mm" pcbY="0.751967mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin14"]} pcbX="-1.499997mm" pcbY="0.252095mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin15"]} pcbX="-1.499997mm" pcbY="-0.248031mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin16"]} pcbX="-1.499997mm" pcbY="-0.747903mm" width="0.5999988mm" height="0.2500122mm" shape="rect" />
<smtpad portHints={["pin17"]} pcbX="0.000127mm" pcbY="-0.000127mm" width="1.499997mm" height="1.499997mm" shape="rect" />
<silkscreenpath route={[{"x":-1.4998954000001277,"y":1.5001494000000548},{"x":-1.4998954000001277,"y":1.1082020000001194}]} />
<silkscreenpath route={[{"x":-1.4998954000001277,"y":-1.1040617999998403},{"x":-1.4998954000001277,"y":-1.4998699999999872}]} />
<silkscreenpath route={[{"x":1.5001239999999143,"y":-1.4998699999999872},{"x":1.5001239999999143,"y":-1.1040617999998403}]} />
<silkscreenpath route={[{"x":1.5001239999999143,"y":1.1082020000001194},{"x":1.5001239999999143,"y":1.5001494000000548}]} />
<silkscreenpath route={[{"x":-1.4998954000001277,"y":1.5001494000000548},{"x":-1.1046206000000893,"y":1.5001494000000548}]} />
<silkscreenpath route={[{"x":1.1061191999998528,"y":1.5001494000000548},{"x":1.5001239999999143,"y":1.5001494000000548}]} />
<silkscreenpath route={[{"x":-1.4998954000001277,"y":-1.4998699999999872},{"x":-1.1046206000000893,"y":-1.4998699999999872}]} />
<silkscreenpath route={[{"x":1.1076431999997567,"y":-1.4998699999999872},{"x":1.5001239999999143,"y":-1.4998699999999872}]} />
<silkscreenpath route={[{"x":-1.23456699999997,"y":-1.8446749999999383},{"x":-1.23641913578615,"y":-1.858743368015439},{"x":-1.241849323151996,"y":-1.8718529999999873},{"x":-1.2504875038019918,"y":-1.8831104961981282},{"x":-1.2617450000001327,"y":-1.891748676848124},{"x":-1.2748546319844536,"y":-1.8971788642137426},{"x":-1.288923000000068,"y":-1.8990309999999226},{"x":-1.3029913680156824,"y":-1.8971788642137426},{"x":-1.316101000000117,"y":-1.891748676848124},{"x":-1.3273584961981442,"y":-1.8831104961981282},{"x":-1.33599667684814,"y":-1.8718529999999873},{"x":-1.3414268642138722,"y":-1.858743368015439},{"x":-1.343279000000166,"y":-1.8446749999999383},{"x":-1.3414268642138722,"y":-1.830606631984324},{"x":-1.33599667684814,"y":-1.817497000000003},{"x":-1.3273584961981442,"y":-1.8062395038018622},{"x":-1.316101000000117,"y":-1.7976013231518664},{"x":-1.3029913680156824,"y":-1.792171135786134},{"x":-1.288923000000068,"y":-1.790318999999954},{"x":-1.2748546319844536,"y":-1.792171135786134},{"x":-1.2617450000001327,"y":-1.7976013231518664},{"x":-1.2504875038019918,"y":-1.8062395038018622},{"x":-1.241849323151996,"y":-1.817497000000003},{"x":-1.23641913578615,"y":-1.830606631984324},{"x":-1.23456699999997,"y":-1.8446749999999383}]} />
<silkscreentext text="{NAME}" pcbX="0.011049mm" pcbY="2.792351mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-2.0423510000000533,"y":2.0423510000000533},{"x":2.064448999999968,"y":2.0423510000000533},{"x":2.064448999999968,"y":-2.16604899999993},{"x":-2.0423510000000533,"y":-2.16604899999993},{"x":-2.0423510000000533,"y":2.0423510000000533}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C910544.obj?uuid=edc2f28e721b49ee8c25b04b981b88c3",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C910544.step?uuid=edc2f28e721b49ee8c25b04b981b88c3",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: -0.000012699999842880061, y: 0, z: -0.01 },
      }}
      {...props}
    />
  )
}