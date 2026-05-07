# Symbol Library

## Status: COMPLETE

File received: `Elec_Symbols.dxf` (AC1032, 6.7 MB, renamed from "Hugh Complete (2).dxf")
531 user-defined blocks across 34 families. Family map: `family_map.json`

## Requirements

- **Format:** Single DXF file with all blocks defined (preferred) or zipped folder of individual DXF files
- **Naming convention:** V/H prefix (vertical/horizontal) + FAMILY code + variant (e.g., VPB11, HCB1)
- **Required families:** All existing families plus safety-specific symbols:
  - E-stops (mushroom head, key release)
  - Safety relays (Pilz PNOZsigma, SICK Flexi, etc.)
  - Guard interlock switches (Schmersal AZM, Euchner, etc.)
  - Safety contactors
  - Safety PLCs / controllers
  - STO-capable VFDs

## Mapping

Once the library is received, a `family_map.json` file will be created mapping each FAMILY code to the component types used by the drawing parser. Example:

```json
{
  "SW": {"type": "pushbutton_switch", "tag_prefix": "SF"},
  "CB": {"type": "circuit_breaker", "tag_prefix": "QA"},
  "CR": {"type": "control_relay", "tag_prefix": "KF"},
  "SN": {"type": "sensor", "tag_prefix": "BG"}
}
```

## Sample Analysis (from initial DXF submission)

50 blocks across 10 families were identified in the sample file:
- SW (Push buttons/Switches): 8 blocks
- SS (Selector switches): 4 blocks
- CB (Circuit breakers): 8 blocks
- CR (Control relays): 6 blocks
- MS (Motor starters): 4 blocks
- OL (Overloads): 3 blocks
- LT (Pilot lights): 2 blocks
- LS (Limit switches): 6 blocks
- SN (Sensors): 6 blocks
- SV (Solenoid valves): 2 blocks
