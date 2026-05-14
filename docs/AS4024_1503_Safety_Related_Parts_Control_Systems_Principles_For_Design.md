# AS 4024.1503 — Safety-Related Parts of Control Systems: General Principles for Design

> **PARTIAL FILE — Clauses 1–11 and Annexes A–B complete. Remaining annexes to be added.**

---

## 1. Scope

This part of ISO 13849 provides safety requirements and guidance on the principles for the design and integration of safety-related parts of control systems (SRP/CS), including the design of software. For these parts of SRP/CS, it specifies characteristics that include the performance level required for carrying out safety functions. It applies to SRP/CS, regardless of the type of technology and energy used (electrical, hydraulic, pneumatic, mechanical, etc.), for all kinds of machinery.

It does not specify the safety functions or performance levels that are to be used in a particular case.

This part of ISO 13849 provides specific requirements for SRP/CS using programmable electronic system(s).

It does not give specific requirements for the design of products which are parts of SRP/CS. Nevertheless, the principles given, such as categories or performance levels, can be used.

> Note 1: Examples of products which are parts of SRP/CS: relays, solenoid valves, position switches, PLCs, motor control units, two-hand control devices, pressure sensitive equipment. For the design of such products, it is important to refer to the specifically applicable International Standards, e.g. ISO 13851, ISO 13856-1 and ISO 13856-2.
>
> Note 2: For the definition of required performance level, see 3.1.24.
>
> Note 3: The requirements provided in this part of ISO 13849 for programmable electronic systems are compatible with the methodology for the design and development of safety-related electrical, electronic and programmable electronic control systems for machinery given in IEC 62061.
>
> Note 4: For safety-related embedded software for components with PL = e see IEC 61508-3:1998, Clause 7.
>
> Note 5: See also Table 1.

---

## 2. Normative References

| Standard | Title |
|---|---|
| ISO 12100-1:2003 | Safety of machinery — Basic concepts, general principles for design — Part 1: Basic terminology, methodology |
| ISO 12100-2:2003 | Safety of machinery — Basic concepts, general principles for design — Part 2: Technical principles |
| ISO 13849-2:2003 | Safety of machinery — Safety-related parts of control systems — Part 2: Validation |
| ISO 14121 | Safety of machinery — Principles of risk assessment |
| IEC 60050-191:1990 | International electrotechnical vocabulary — Chapter 191: Dependability and quality of service (and amendments) |
| IEC 61508-3:1998 | Functional safety of electrical/electronic/programmable electronic safety-related systems — Part 3: Software requirements (and corrigendum) |
| IEC 61508-4:1998 | Functional safety of electrical/electronic/programmable electronic safety-related systems — Part 4: Definitions and abbreviations (and corrigendum) |

---

## 3. Terms, Definitions, Symbols and Abbreviated Terms

### 3.1 Terms and Definitions

**3.1.1 safety-related part of a control system (SRP/CS)**
Part of a control system that responds to safety-related input signals and generates safety-related output signals.

> Note 1: The combined safety-related parts of a control system start at the point where the safety-related input signals are initiated (including the actuating cam and the roller of the position switch) and end at the output of the power control elements (including the main contacts of a contactor).
> Note 2: If monitoring systems are used for diagnostics, they are also considered as SRP/CS.

**3.1.2 category**
Classification of the safety-related parts of a control system in respect of their resistance to faults and their subsequent behaviour in the fault condition, and which is achieved by the structural arrangement of the parts, fault detection and/or by their reliability.

**3.1.3 fault**
State of an item characterized by the inability to perform a required function, excluding the inability during preventive maintenance or other planned actions, or due to lack of external resources.

> Note 1: A fault is often the result of a failure of the item itself, but may exist without prior failure. [IEC 60050-191:1990, 05-01]
> Note 2: In this part of ISO 13849, "fault" means random fault.

**3.1.4 failure**
Termination of the ability of an item to perform a required function.

> Note 1: After a failure, the item has a fault.
> Note 2: "Failure" is an event, as distinguished from "fault", which is a state.
> Note 3: The concept as defined does not apply to items consisting of software only. [IEC 60050-191:1990, 04-01]
> Note 4: Failures which only affect the availability of the process under control are outside the scope of this part of ISO 13849.

**3.1.5 dangerous failure**
Failure which has the potential to put the SRP/CS in a hazardous or fail-to-function state.

> Note 1: Whether or not the potential is realized can depend on the channel architecture of the system; in redundant systems a dangerous hardware failure is less likely to lead to the overall dangerous or fail-to-function state.
> Note 2: Adapted from IEC 61508-4:1998, definition 3.6.7.

**3.1.6 common cause failure (CCF)**
Failures of different items, resulting from a single event, where these failures are not consequences of each other. [IEC 60050-191-am1:1999, 04-23]

> Note: Common cause failures should not be confused with common mode failures (see ISO 12100-1:2003, 3.34).

**3.1.7 systematic failure**
Failure related in a deterministic way to a certain cause, which can only be eliminated by a modification of the design or of the manufacturing process, operational procedures, documentation or other relevant factors.

> Note 1: Corrective maintenance without modification will not usually eliminate the failure cause.
> Note 2: A systematic failure can be induced by simulating the failure cause. [IEC 60050-191:1990, 04-19]
> Note 3: Examples of causes of systematic failures include human error in: the safety requirements specification; the design, manufacture, installation, operation of the hardware; and the design, implementation, etc., of the software.

**3.1.8 muting**
Temporary automatic suspension of a safety function(s) by the SRP/CS.

**3.1.9 manual reset**
Function within the SRP/CS used to restore manually one or more safety functions before re-starting a machine.

**3.1.10 harm**
Physical injury or damage to health. [ISO 12100-1:2003, 3.5]

**3.1.11 hazard**
Potential source of harm.

> Note 1: A hazard can be qualified in order to define its origin (e.g. mechanical hazard, electrical hazard) or the nature of the potential harm (e.g. electric shock hazard, cutting hazard, toxic hazard, fire hazard).
> Note 2: The hazard envisaged in this definition: either is permanently present during the intended use of the machine; or may appear unexpectedly (e.g. explosion, crushing hazard as a consequence of an unintended/unexpected start-up). [ISO 12100-1:2003, 3.6]

**3.1.12 hazardous situation**
Circumstance in which a person is exposed to at least one hazard, the exposure having immediately or over a long period of time the potential to result in harm. [ISO 12100-1:2003, 3.9]

**3.1.13 risk**
Combination of the probability of occurrence of harm and the severity of that harm. [ISO 12100-1:2003, 3.11]

**3.1.14 residual risk**
Risk remaining after protective measures have been taken. [ISO 12100-1:2003, 3.12]

**3.1.15 risk assessment**
Overall process comprising risk analysis and risk evaluation. [ISO 12100-1:2003, 3.13]

**3.1.16 risk analysis**
Combination of the specification of the limits of the machine, hazard identification and risk estimation. [ISO 12100-1:2003, 3.14]

**3.1.17 risk evaluation**
Judgement, on the basis of risk analysis, of whether risk reduction objectives have been achieved. [ISO 12100-1:2003, 3.16]

**3.1.18 intended use of a machine**
Use of the machine in accordance with the information provided in the instructions for use. [ISO 12100-1:2003, 3.22]

**3.1.19 reasonably foreseeable misuse**
Use of a machine in a way not intended by the designer, but which may result from readily predictable human behaviour. [ISO 12100-1:2003, 3.23]

**3.1.20 safety function**
Function of the machine whose failure can result in an immediate increase of the risk(s). [ISO 12100-1:2003, 3.28]

**3.1.21 monitoring**
Safety function which ensures that a protective measure is initiated if the ability of a component or an element to perform its function is diminished or if the process conditions are changed in such a way that a decrease of the amount of risk reduction is generated.

**3.1.22 programmable electronic system (PES)**
System for control, protection or monitoring dependent for its operation on one or more programmable electronic devices, including all elements of the system such as power supplies, sensors and other input devices, contactors and other output devices.

> Note: Adapted from IEC 61508-4:1998, definition 3.3.2.

**3.1.23 performance level (PL)**
Discrete level used to specify the ability of safety-related parts of control systems to perform a safety function under foreseeable conditions.

> Note: See 4.5.1.

**3.1.24 required performance level (PLr)**
Performance level (PL) applied in order to achieve the required risk reduction for each safety function.

**3.1.25 mean time to dangerous failure (MTTFd)**
Expectation of the mean time to dangerous failure.

> Note: Adapted from IEC 62061:2005, definition 3.2.34.

**3.1.26 diagnostic coverage (DC)**
Measure of the effectiveness of diagnostics, which may be determined as the ratio between the failure rate of detected dangerous failures and the failure rate of total dangerous failures.

> Note 1: Diagnostic coverage can exist for the whole or parts of a safety-related system.
> Note 2: Adapted from IEC 61508-4:1998, definition 3.8.6.

**3.1.27 protective measure**
Measure intended to achieve risk reduction.

> Example 1: Implemented by the designer: inherent design, safeguarding and complementary protective measures, information for use.
> Example 2: Implemented by the user: organization (safe working procedures, supervision, permit-to-work systems), provision and use of additional safeguards, personal protective equipment, training. [ISO 12100-1:2003, 3.18]

**3.1.28 mission time (τM)**
Period of time covering the intended use of an SRP/CS.

**3.1.29 test rate (r't)**
Frequency of automatic tests to detect faults in a SRP/CS; reciprocal value of diagnostic test interval.

**3.1.30 demand rate (r'd)**
Frequency of demands for a safety-related action of the SRP/CS.

**3.1.31 repair rate (r'r)**
Reciprocal value of the period of time between detection of a dangerous failure by either an online test or obvious malfunction of the system and the restart of operation after repair or system/component replacement.

> Note: The repair time does not include the span of time needed for failure-detection.

**3.1.32 machine control system**
System which responds to input signals from parts of machine elements, operators, external control equipment or any combination of these and generates output signals causing the machine to behave in the intended manner.

> Note: The machine control system can use any technology or any combination of different technologies (e.g. electrical/electronic, hydraulic, pneumatic, mechanical).

**3.1.33 safety integrity level (SIL)**
Discrete level (one out of a possible four) for specifying the safety integrity requirements of the safety functions to be allocated to the E/E/PE safety-related systems, where safety integrity level 4 has the highest level of safety integrity and safety integrity level 1 has the lowest. [IEC 61508-4:1998, 3.5.6]

**3.1.34 limited variability language (LVL)**
Type of language that provides the capability of combining predefined, application-specific library functions to implement the safety requirements specifications.

> Note 1: Adapted from IEC 61511-1:2003, definition 3.2.80.1.2.
> Note 2: Typical examples of LVL (ladder logic, function block diagram) are given in IEC 61131-3.
> Note 3: A typical example of a system using LVL: PLC.

**3.1.35 full variability language (FVL)**
Type of language that provides the capability of implementing a wide variety of functions and applications.

> Example: C, C++, Assembler.
> Note 1: Adapted from IEC 61511-1:2003, definition 3.2.80.1.3.
> Note 2: A typical example of systems using FVL: embedded systems.
> Note 3: In the field of machinery, FVL is found in embedded software and rarely in application software.

**3.1.36 application software**
Software specific to the application, implemented by the machine manufacturer, and generally containing logic sequences, limits and expressions that control the appropriate inputs, outputs, calculations and decisions necessary to meet the SRP/CS requirements.

**3.1.37 embedded software (firmware / system software)**
Software that is part of the system supplied by the control manufacturer and which is not accessible for modification by the user of the machinery.

> Note: Embedded software is usually written in FVL.

---

### 3.2 Symbols and Abbreviated Terms

**Table 2 — Symbols and Abbreviated Terms**

| Symbol or abbreviation | Description | Definition or occurrence |
|---|---|---|
| a, b, c, d, e | Denotation of performance levels | Table 3 |
| AOPD | Active optoelectronic protective device (e.g. light barrier) | Annex H |
| B, 1, 2, 3, 4 | Denotation of categories | Table 7 |
| β10d | Number of cycles until 10% of components fail dangerously (pneumatic and electromechanical) | Annex C |
| Cat. | Category | 3.1.2 |
| CC | Current converter | Annex I |
| CCF | Common cause failure | 3.1.6 |
| DC | Diagnostic coverage | 3.1.26 |
| DCavg | Average diagnostic coverage | E.2 |
| F, F1, F2 | Frequency and/or time of exposure to the hazard | A.2.2 |
| FB | Function block | 4.6.3 |
| FVL | Full variability language | 3.1.35 |
| FMEA | Failure modes and effects analysis | 7.2 |
| I, I1, I2 | Input device, e.g. sensor | 6.2 |
| i, j | Index for counting | Annex D |
| I/O | Inputs/outputs | Table E.1 |
| iab, ibc | Interconnecting means | Figure 4 |
| K1A, K1B | Contactors | Annex I |
| L, L1, L2 | Logic | 6.2 |
| LVL | Limited variability language | 3.1.34 |
| M | Motor | Annex I |
| MTTF | Mean time to failure | Annex C |
| MTTFd | Mean time to dangerous failure | 3.1.25 |
| n, N, Ñ | Number of items | 6.3, D.1 |
| Nlow | Number of SRP/CS with PLlow in a combination of SRP/CS | 6.3 |
| O, O1, O2, OTE | Output device, e.g. actuator | 6.2 |
| P, P1, P2 | Possibility of avoiding the hazard | A.2.3 |
| PES | Programmable electronic system | 3.1.22 |
| PL | Performance level | 3.1.23 |
| PLC | Programmable logic controller | Annex I |
| PLlow | Lowest performance level of a SRP/CS in a combination | 6.3 |
| PLr | Required performance level | 3.1.24 |
| r'd | Demand rate | 3.1.30 |
| RS | Rotation sensor | Annex I |
| S, S1, S2 | Severity of injury | A.2.1 |
| SW1A, SW1B, SW2 | Position switches | Annex I |
| SIL | Safety integrity level | Table 4 |
| SRASW | Safety-related application software | 4.6.3 |
| SRESW | Safety-related embedded software | 4.6.2 |
| SRP | Safety-related part | General |
| SRP/CS | Safety-related part of a control system | 3.1.1 |
| TE | Test equipment | 6.2 |
| τM | Mission time | 3.1.28 |

---

## 4. Design Considerations

### 4.1 Safety Objectives in Design

The SRP/CS shall be designed and constructed so that the principles of ISO 12100 and ISO 14121 are fully taken into account (see Figures 1 and 3). All intended use and reasonable foreseeable misuse shall be considered.

---

### 4.2 Strategy for Risk Reduction

#### 4.2.1 General

The strategy for risk reduction at the machine is given in ISO 12100-1:2003, Clause 5. The hazard analysis and risk reduction process for a machine requires that hazards are eliminated or reduced through a hierarchy of measures:

- hazard elimination or risk reduction by design (see ISO 12100-2:2003, Clause 4)
- risk reduction by safeguarding and possibly complementary protective measures (see ISO 12100-2:2003, Clause 5)
- risk reduction by the provision of information for use about the residual risk (see ISO 12100-2:2003, Clause 6)

#### 4.2.2 Contribution to the Risk Reduction by the Control System

The purpose in following the overall design procedure for the machine is to achieve the safety objectives (see 4.1). The design of the SRP/CS to provide the required risk reduction is an integral subset of the overall design procedure for the machine. The SRP/CS provides safety function(s) at a PL which achieves the required risk reduction in providing safety function(s), either as an inherently safe part of the design or as a control for a safeguard or protective device.

For each safety function, the characteristics (see Clause 5) and the required performance level shall be specified and documented in the safety requirements specification.

In this part of ISO 13849 the performance levels are defined in terms of probability of dangerous failure per hour. Five performance levels (a to e) are set out, with defined ranges of probability of a dangerous failure per hour (see Table 3).

**Table 3 — Performance Levels (PL)**

| PL | Average probability of dangerous failure per hour (1/h) |
|---|---|
| a | ≥ 10⁻⁵ to < 10⁻⁴ |
| b | ≥ 3 × 10⁻⁶ to < 10⁻⁵ |
| c | ≥ 10⁻⁶ to < 3 × 10⁻⁶ |
| d | ≥ 10⁻⁷ to < 10⁻⁶ |
| e | ≥ 10⁻⁸ to < 10⁻⁷ |

> Note: Besides the average probability of dangerous failure per hour other measures are also necessary to achieve the PL.

**Figure 1 — Overview of Risk Assessment/Risk Reduction** *(flowchart)*

```
START
  |
  v
Determination of limits of the machinery (ISO 12100-1, 5.2)
  |
  v
Hazard identification (Clause 4 and 5.3)
  |
  v
Risk estimation (5.3)
  |
  v
Risk evaluation (5.3)
  |
Has the risk been adequately reduced?
  |
 No --> Risk reduction process:
         1. by intrinsic design
         2. by safeguards
         3. by information for use (ISO 12100-1:2003, Figure 4)
          |
         Does the protective measure selected depend on a control system?
          |
         Yes --> Iterative process of the design of SRP/CS (see Figure 3)
          |
         No --> Are other hazards generated? --> Yes (loop back) / No --> END
```

> a: Refers to ISO 12100-1:2003. b: Refers to this part of ISO 13849.

**Figure 2 — Overview of the Risk Reduction Process** *(diagram showing risk levels)*

Key:
- R0 = risk before protective measures
- Rr = risk reduction required
- Ra = actual risk reduction achieved
- Solution 1: important part of risk reduction from measures other than SRP/CS; small part from SRP/CS
- Solution 2: important part of risk reduction from SRP/CS; small part from other measures
- 3 = adequately reduced risk
- 4 = inadequately reduced risk

**Figure 3 — Iterative Process for Design of SRP/CS** *(flowchart)*

```
From Figure 1: Identify safety functions to be performed by SRP/CSs
  |
For each safety function: specify required characteristics (Clause 5)
  |
Determine required PLr (see 4.3 and Annex A)
  |
Design and technical realisation: identify SRP/CS parts carrying out the safety function (see 4.4)
  |
Evaluate PL (see 4.5) considering:
  - category (Clause 6)
  - MTTFd (Annexes C and D)
  - DC (Annex E)
  - CCF (Annex F)
  - software (4.6 and Annex J)
  |
Verification: is PL ≥ PLr? (see 4.7)
  |
 Yes --> Validation (Clause 8 / ISO 13849-2): Are all requirements met?
  |
 Yes --> Have all safety functions been analysed? --> Yes --> To Figure 1 (ISO 12100)
```

**Figure 4 — Diagrammatic Presentation of Combination of SRP/CS**

```
1 --> [SRP/CSa] --iab--> [SRP/CSb] --ibc--> [SRP/CSc] --> 2
         [I]               [L]               [O]
```

Key: I = input, L = logic, O = output, 1 = initiation event, 2 = machine actuator

---

### 4.3 Determination of Required Performance Level (PLr)

For each selected safety function to be carried out by a SRP/CS, a required performance level (PLr) shall be determined and documented (see Annex A for guidance). The determination of the required performance level is the result of the risk assessment and refers to the amount of the risk reduction to be carried out by the safety-related parts of the control system (see Figure 2).

The greater the amount of risk reduction required to be provided by the SRP/CS, the higher the PLr shall be.

---

### 4.4 Design of SRP/CS

Part of the risk reduction process is to determine the safety functions of the machine. A safety function may be implemented by one or more SRP/CS, and several safety functions may share one or more SRP/CS. It is also possible that one SRP/CS implements safety functions and standard control functions.

A typical safety function diagrammatic presentation is given in Figure 4 showing a combination of safety-related parts of control systems (SRP/CS) for:
- input (SRP/CSa)
- logic/processing (SRP/CSb)
- output/power control elements (SRP/CSc)
- interconnecting means (iab, ibc) (e.g. electrical, optical)

> Note 1: Within the same machinery it is important to distinguish between different safety functions and their related SRP/CS carrying out a certain safety function.
> Note 2: Designated architectures are given in Clause 6.
> Note 3: All interconnecting means are included in the safety-related parts.

---

### 4.5 Evaluation of the Achieved Performance Level PL and Relationship with SIL

#### 4.5.1 Performance Level PL

For the purposes of this part of ISO 13849, the ability of safety-related parts to perform a safety function is expressed through the determination of the performance level.

For each selected SRP/CS and/or for the combination of SRP/CS that performs a safety function the estimation of PL shall be done.

The PL of the SRP/CS shall be determined by the estimation of the following aspects:
- the MTTFd value for single components (see Annexes C and D)
- the DC (see Annex E)
- the CCF (see Annex F)
- the structure (see Clause 6)
- the behaviour of the safety function under fault condition(s) (see Clause 6)
- safety-related software (see 4.6 and Annex J)
- systematic failure (see Annex G)
- the ability to perform a safety function under expected environmental conditions

These aspects can be grouped under two approaches:
- (a) quantifiable aspects (MTTFd value for single components, DC, CCF, structure)
- (b) non-quantifiable, qualitative aspects which affect the behaviour of the SRP/CS (behaviour under fault conditions, safety-related software, systematic failure and environmental conditions)

Among the quantifiable aspects, the contribution of reliability (e.g. MTTFd, structure) can vary with the technology used.

For a SRP/CS or combination of SRP/CS designed according to the requirements given in Clause 6, the average probability of a dangerous failure could be estimated by means of Figure 5 and the procedure given in Annexes A to H, J and K.

For a SRP/CS which deviates from the designated architectures, a detailed calculation shall be provided to demonstrate the achievement of the required performance level (PLr).

PL a has no correspondence on the SIL scale and is mainly used to reduce the risk of slight, normally reversible injury. PL e corresponding to SIL 3 is defined as the highest level.

**Table 4 — Relationship Between Performance Level (PL) and Safety Integrity Level (SIL)**

| PL | SIL (IEC 61508-1, for information — high/continuous mode of operation) |
|---|---|
| a | No correspondence |
| b | 1 |
| c | 1 |
| d | 2 |
| e | 3 |

Protective measures to reduce the risk shall be applied:
- **Reduce probability of faults** at component level by selection of well-tried components and/or applying well-tried safety principles, to minimise or exclude critical faults (see ISO 13849-2).
- **Improve the structure of the SRP/CS** to avoid the dangerous effect of a fault; some faults may be detected and a redundant and/or monitored structure could be needed.

#### 4.5.2 Mean Time to Dangerous Failure of Each Channel (MTTFd)

The value of the MTTFd of each channel is given in three levels (see Table 5) and shall be taken into account for each channel (e.g. single channel, each channel of a redundant system) individually.

According to MTTFd, a maximum value of 100 years can be taken into account.

**Table 5 — Mean Time to Dangerous Failure of Each Channel (MTTFd)**

| Denotation of each channel | Range of each channel |
|---|---|
| Low | 3 years ≤ MTTFd < 10 years |
| Medium | 10 years ≤ MTTFd < 30 years |
| High | 30 years ≤ MTTFd ≤ 100 years |

> Note 1: The choice of MTTFd ranges is based on failure rates found in the field as state-of-the-art, forming a kind of logarithmic scale fitting to the logarithmic PL scale. An MTTFd value less than 3 years is not expected to be found for real SRP/CS. An MTTFd value greater than 100 years is not acceptable.
> Note 2: The indicated borders are assumed within an accuracy of 5%.

For the estimation of MTTFd of a component, the hierarchical procedure for finding data shall be, in order:
- (a) use manufacturer's data
- (b) use methods in Annexes C and D
- (c) choose ten years

#### 4.5.3 Diagnostic Coverage (DC)

The value of the DC is given in four levels (see Table 6). For the estimation of DC, in most cases, failure mode and effects analysis (FMEA, see IEC 60812) or similar methods can be used. For a simplified approach to estimating DC, see Annex E.

**Table 6 — Diagnostic Coverage (DC)**

| Denotation | Range |
|---|---|
| None | DC < 60% |
| Low | 60% ≤ DC < 90% |
| Medium | 90% ≤ DC < 99% |
| High | 99% ≤ DC |

> Note 1: For SRP/CS consisting of several parts an average value DCavg for DC is used in Figure 5, Clause 6 and E.2.
> Note 2: The choice of DC ranges is based on the key values 60%, 90% and 99% also established in other standards. A DC-value greater than 99% for complex systems is very hard to achieve. The indicated borders are assumed within an accuracy of 5%.

#### 4.5.4 Simplified Procedure for Estimating PL

The PL may be estimated by taking into account all relevant parameters and the appropriate methods for calculation (see 4.5.1).

This clause describes a simplified procedure for estimating the PL of a SRP/CS based on designated architectures. The designated architectures show a logical representation of the system structure for each category.

For the designated architectures, the following typical assumptions are made:
- mission time, 20 years (see Clause 10)
- constant failure rates within the mission time
- for category 2, demand rate ≤ 1/100 test rate
- for category 2, MTTFd,TE larger than half of MTTFd,L

CCF should also be taken into account (for guidance, see Annex F).

**Figure 5 — Relationship Between Categories, DCavg, MTTFd of Each Channel and PL** *(bar graph)*

The graph shows different combinations of category with DCavg (horizontal axis) and MTTFd of each channel (bars representing low, medium and high). For categories 2, 3 and 4, sufficient measures against CCF shall be carried out (see Annex F).

**Table 7 — Simplified Procedure for Evaluating PL Achieved by SRP/CS**

| Category | B | 1 | 2 | 2 | 3 | 3 | 4 |
|---|---|---|---|---|---|---|---|
| DCavg | none | none | low | medium | low | medium | high |
| **MTTFd of each channel** | | | | | | | |
| Low | a | Not covered | a | b | b | c | Not covered |
| Medium | b | Not covered | b | c | c | d | Not covered |
| High | Not covered | c | c | d | d | d | e |

---

### 4.6 Software Safety Requirements

#### 4.6.1 General

All lifecycle activities of safety-related embedded or application software shall primarily consider the avoidance of faults introduced during the software lifecycle (see Figure 6). The main objective is to have readable, understandable, testable and maintainable software.

**Figure 6 — Simplified V-Model of Software Safety Lifecycle**

```
Safety functions specification
  --> Safety-related software specification --> Validation --> Validated software
        |                                           ^
        v                                           |
     System design <------------------------> Integration testing
        |                                           ^
        v                                           |
     Module design <------------------------> Module testing
        |                                           ^
        v                                           |
      Coding -------------------------------------->
```

> Note: Annex J gives more detailed recommendations for lifecycle activities.

#### 4.6.2 Safety-Related Embedded Software (SRESW)

For SRESW for components with PLr a to d, the following basic measures shall be applied:
- software safety lifecycle with verification and validation activities (see Figure 6)
- documentation of specification and design
- modular and structured design and coding
- control of systematic failures (see G.2)
- where using software-based measures for control of random hardware failures, verification of correct implementation
- functional testing, e.g. black box testing
- appropriate software safety lifecycle activities after modifications

For SRESW for components with PLr c or d, the following additional measures shall be applied:
- project management and quality management system comparable to, e.g. IEC 61508 or ISO 9001
- documentation of all relevant activities during software safety lifecycle
- configuration management to identify all configuration items and documents related to a SRESW release
- structured specification with safety requirements and design
- use of suitable programming languages and computer-based tools with confidence from use
- modular and structured programming, separation in non-safety-related software, limited module sizes with fully defined interfaces, use of design and coding standards
- coding verification by walk-through/review with control flow analysis
- extended functional testing, e.g. grey box testing, performance testing or simulation
- impact analysis and appropriate software safety lifecycle activities after modifications

SRESW for components with PLr = e shall comply with IEC 61508-3:1998, Clause 7, appropriate for SIL 3.

> Note 1: For a detailed description of such measures, see e.g. IEC 61508-7:2000.
> Note 2: For SRESW with diversity in design and coding for components used in SRP/CS with category 3 or 4, the effort involved in taking measures to avoid systematic failures can be reduced by reviewing parts of the software only by considering structural aspects instead of checking each line of code.

#### 4.6.3 Safety-Related Application Software (SRASW)

The software safety lifecycle (see Figure 6) also applies to SRASW (see Annex J).

SRASW written in LVL and complying with the following requirements can achieve a PL a to e. If SRASW is written in FVL, the requirements for SRESW shall apply and PL a to e is achievable.

For SRASW for components with PLr from a to e, the following basic measures shall be applied:
- development lifecycle with verification and validation activities (see Figure 6)
- documentation of specification and design
- modular and structured programming
- functional testing
- appropriate development activities after modifications

For SRASW with PLr c to e, the following additional measures (with increasing efficiency: lower effectiveness for PLr c, medium for PLr d, higher for PLr e) are required or recommended:

**(a) Specification** — The safety-related software specification shall be reviewed and shall contain:
1. safety functions with required PL and associated operating modes
2. performance criteria, e.g. reaction times
3. hardware architecture with external signal interfaces
4. detection and control of external failure

**(b) Selection of tools, libraries, languages:**
1. Suitable tools with confidence from use
2. Validated function block (FB) libraries should be used
3. A justified LVL-subset suitable for modular approach should be used; graphical languages (e.g. function block diagram, ladder diagram) are highly recommended

**(c) Software design** shall feature:
1. semi-formal methods to describe data and control flow, e.g. state diagram or program flow chart
2. modular and structured programming predominantly by function blocks deriving from safety-related validated function block libraries
3. function blocks of limited size of coding
4. code execution inside function block which should have one entry and one exit point
5. architecture model of three stages: Inputs → Processing → Outputs (see Figure 7 and Annex J)
6. assignment of a safety output at only one program location
7. use of techniques for detection of external failure and for defensive programming within input, processing and output blocks which lead to safe state

**(d) Where SRASW and non-SRASW are combined in one component:**
1. SRASW and non-SRASW shall be coded in different function blocks with well-defined data links
2. there shall be no logical combination of non-safety-related and safety-related data which could lead to downgrading the integrity of safety-related signals

**(e) Software implementation/coding:**
1. code shall be readable, understandable and testable; symbolic variables shall be used
2. justified or accepted coding guidelines shall be used (see also Annex J)
3. data integrity and plausibility checks available on application layer
4. code should be tested by simulation
5. verification should be by control and data flow analysis for PL = d or e

**(f) Testing:**
1. appropriate validation method is black-box testing of functional behaviour and performance criteria
2. for PL = d or e, test case execution from boundary value analysis is recommended
3. test planning is recommended with completion criteria and required tools
4. I/O testing shall ensure that safety-related signals are correctly used within SRASW

**(g) Documentation:**
1. all lifecycle and modification activities shall be documented
2. documentation shall be complete, available, readable and understandable
3. code documentation shall contain module headers with legal entity, functional and I/O description, version and version of used library function blocks, and sufficient comments

**(h) Verification** — Review, inspection, walkthrough or other appropriate activities.

**(i) Configuration management** — It is highly recommended that procedures and data backup be established to identify and archive documents, software modules, verification/validation results and tool configuration related to a specific SRASW version.

**(j) Modifications** — After modifications of SRASW, impact analysis shall be performed. Access rights to modifications shall be controlled and modification history shall be documented.

**Figure 7 — General Architecture Model of Software**

```
Inputs --> Processing --> Outputs
[Input blocks]  [Processing block]  [Output blocks]
Acquisition of  Processing to       Control of
information     realise safety      actuators by
from safety     functions           safety outputs
sensors
```

#### 4.6.4 Software-Based Parameterization

Software-based parameterization of safety-related parameters shall be considered as a safety-related aspect of SRP/CS design. Parameterization shall be carried out using a dedicated software tool provided by the supplier of the SRP/CS. This tool shall have its own identification (name, version, etc.) and shall prevent unauthorized modification, for example, by use of a password.

The integrity of all data used for parameterization shall be maintained by measures to:
- control the range of valid inputs
- control data corruption before transmission
- control the effects of errors from the parameter transmission process
- control the effects of incomplete parameter transmission
- control the effects of faults and failures of hardware and software of the tool used for parameterization

Confirmation of input parameters to the SRP/CS shall be by either:
- retransmission of the modified parameters to the parameterization tool, or
- other suitable means of confirming the integrity of the parameters

The following verification activities shall be applied for software-based parameterization:
- verification of the correct setting for each safety-related parameter (minimum, maximum and representative values)
- verification that the safety-related parameters are checked for plausibility
- verification that unauthorized modification of safety-related parameters is prevented
- verification that the data/signals for parameterization are generated and processed in such a way that faults cannot lead to a loss of the safety function

---

### 4.7 Verification that Achieved PL Meets PLr

For each individual safety function the PL of the related SRP/CS shall match the required performance level (PLr) determined according to 4.3 (see Figure 3). If this is not the case, an iteration in the process described in Figure 3 is necessary.

The PL of the different SRP/CS which are part of a safety function shall be greater than or equal to the required performance level (PLr) of this safety function.

---

### 4.8 Ergonomic Aspects of Design

The interface between operators and the SRP/CS shall be designed and realized such that no person is endangered during all intended use and reasonable foreseeable misuse of the machine (see also ISO 12100-2, EN 614-1, ISO 9355-1, ISO 9355-2, ISO 9355-3, EN 1005-3, IEC 60204-1:2000 Clause 10, IEC 60447 and IEC 61310).

Ergonomic principles shall be used so that the machine and the control system, including the safety-related parts, are easy to use, and so that the operator is not tempted to act in a hazardous manner.

---

## 5. Safety Functions

### 5.1 Specification of Safety Functions

This clause provides a list and details of safety functions which can be provided by the SRP/CS.

**Table 8 — Some International Standards Applicable to Typical Machine Safety Functions and Certain of Their Characteristics**

| Safety function/characteristic | This part of ISO 13849 | ISO 12100-1:2003 | ISO 12100-2:2003 | For additional information, see: |
|---|---|---|---|---|
| Safety-related stop function initiated by safeguard | 5.2.1 | 3.26.8 | 4.11.3 | IEC 60204-1:2005, 9.2.2, 9.2.5.3, 9.2.5.5 |
| Manual reset function | 5.2.2 | — | — | IEC 60204-1:2005, 9.2.5.3, 9.2.5.4 |
| Start/restart function | 5.2.3 | — | 4.11.3, 4.11.4 | IEC 60204-1:2005, 9.2.1, 9.2.5.1, 9.2.6 |
| Local control function | 5.2.4 | — | 4.11.8, 4.11.10 | IEC 60204-1:2005, 10.1.5 |
| Muting function | 5.2.5 | — | — | — |
| Hold-to-run function | — | — | 4.11.8b | IEC 60204-1:2005, 9.2.6.1 |
| Enabling device function | — | — | — | IEC 60204-1:2005, 9.2.6.3, 10.9 |
| Prevention of unexpected start-up | — | — | 4.11.4 | ISO 14118, IEC 60204-1:2005, 5.4 |
| Escape and rescue of trapped persons | 5.5.3 | — | — | — |
| Isolation and energy dissipation function | — | — | 5.5.4 | ISO 14118, IEC 60204-1:2005, 5.3, 6.3.1 |
| Control modes and mode selection | — | — | 4.11.8, 4.11.10 | IEC 60204-1:2005, 9.2.3, 9.2.4 |
| Interaction between different safety-related parts of control systems | — | — | 4.11.1 (last sentence) | IEC 60204-1:2005, 9.3.4 |
| Monitoring of parameterization of safety-related input values | 4.6.4 | — | — | — |
| Emergency stop function | — | — | 5.5.2 | ISO/IEC 13850, IEC 60204-1:2005, 9.2.5.4 |

> a: Including interlocked guards and limiting devices (e.g. overspeed, overtemperature, overpressure).
> b: Complementary protective measure, see ISO 12100-1:2003.

**Table 9 — Some International Standards Giving Requirements for Certain Safety Functions and Safety-Related Parameters**

| Safety function/safety-related parameter | This part of ISO 13849 | ISO 12100-2:2003 | For additional information, see: |
|---|---|---|---|
| Response time | 5.2.6 | — | ISO 13855:2000, 3.2, A.3, A.4 |
| Safety-related parameter such as speed, temperature or pressure | 5.2.7 | 4.11.8e | IEC 60204-1:2005, 7.1, 9.3.2, 9.3.4 |
| Fluctuations, loss and restoration of power sources | 5.2.8 | 4.11.8e | IEC 60204-1:2005, 4.3, 7.1, 7.5 |
| Indications and alarms | — | 4.8 | ISO 7731, ISO 11428, ISO 11429, IEC 61310-1, IEC 60204-1:2005 10.3/10.4, IEC 61131, IEC 62061 |

When identifying and specifying the safety function(s), the following shall at least be considered:

- (a) results of the risk assessment for each specific hazard or hazardous situation
- (b) machine operating characteristics, including: intended use (including reasonably foreseeable misuse), modes of operation, cycle time, and response time
- (c) emergency operation
- (d) description of the interaction of different working processes and manual activities (repairing, setting, cleaning, trouble shooting, etc.)
- (e) the behaviour of the machine that a safety function is intended to achieve or to prevent
- (f) condition(s) of the machine in which it is to be active or disabled
- (g) the frequency of operation
- (h) priority of those functions that can be simultaneously active and that can cause conflicting action

---

### 5.2 Details of Safety Functions

#### 5.2.1 Safety-Related Stop Function

A safety-related stop function (e.g. initiated by a safeguard) shall, as soon as necessary after actuation, put the machine in a safe state. Such a stop shall have priority over a stop for operational reasons.

When a group of machines are working together in a coordinated manner, provision shall be made for signalling the supervisory control and/or the other machines that such a stop condition exists.

#### 5.2.2 Manual Reset Function

After a stop command has been initiated by a safeguard, the stop condition shall be maintained until safe conditions for restarting exist.

The re-establishment of the safety function by resetting of the safeguard cancels the stop command. If indicated by the risk assessment, this cancellation of the stop command shall be confirmed by a manual, separate and deliberate action (manual reset).

The manual reset function shall:
- be provided through a separate and manually operated device within the SRP/CS
- only be achieved if all safety functions and safeguards are operative
- not initiate motion or a hazardous situation by itself
- be by deliberate action
- enable the control system for accepting a separate start command
- only be accepted by disengaging the actuator from its energized (on) position

The reset actuator shall be situated outside the danger zone and in a safe position from which there is good visibility for checking that no person is within the danger zone.

Where the visibility of the danger zone is not complete, a special reset procedure is required.

#### 5.2.3 Start/Restart Function

A restart shall take place automatically only if a hazardous situation cannot exist. In particular, for interlocking guards with a start function, ISO 12100-2:2003, 5.3.2.5, applies.

These requirements for start and restart shall also apply to machines which can be controlled remotely.

#### 5.2.4 Local Control Function

When a machine is controlled locally, e.g. by a portable control device or pendant:
- the means for selecting local control shall be situated outside the danger zone
- it shall only be possible to initiate hazardous conditions by a local control in a zone defined by the risk assessment
- switching between local and main control shall not create a hazardous situation

#### 5.2.5 Muting Function

Muting shall not result in any person being exposed to hazardous situations. During muting, safe conditions shall be provided by other means.

At the end of muting, all safety functions of the SRP/CS shall be reinstated.

The performance level of safety-related parts providing the muting function shall be selected so that the inclusion of the muting function does not diminish the safety required of the relevant safety function.

#### 5.2.6 Response Time

The response time of the SRP/CS shall be determined when the risk assessment of the SRP/CS indicates that this is necessary (see also Clause 11).

#### 5.2.7 Safety-Related Parameters

When safety-related parameters, e.g. position, speed, temperature or pressure, deviate from present limits the control system shall initiate appropriate measures (e.g. actuation of stopping, warning signal, alarm).

If errors in manual inputting of safety-related data in programmable electronic systems can lead to a hazardous situation, then a data checking system within the safety-related control system shall be provided, e.g. check of limits, format and/or logic input values.

#### 5.2.8 Fluctuations, Loss and Restoration of Power Sources

When fluctuations in energy levels outside the design operating range occur, including loss of energy supply, the SRP/CS shall continue to provide or initiate output signal(s) which will enable other parts of the machine system to maintain a safe state.

---

## 6. Categories and Their Relation to MTTFd of Each Channel, DCavg and CCF

### 6.1 General

The SRP/CS shall be in accordance with the requirements of one or more of the five categories specified in 6.2.

Categories are the basic parameters used to achieve a specific PL. They state the required behaviour of the SRP/CS in respect of its resistance to faults based on the design considerations described in Clause 4.

Category B is the basic category. The occurrence of a fault can lead to the loss of the safety function. In category 1 improved resistance to faults is achieved predominantly by selection and application of components. In categories 2, 3 and 4, improved performance in respect of a specified safety function is achieved predominantly by improving the structure of the SRP/CS.

The selection of a category for a particular SRP/CS depends mainly upon:
- the reduction in risk to be achieved by the safety function
- the required performance level (PLr)
- the technologies used
- the risk arising in the case of a fault(s) in that part
- the possibilities of avoiding a fault(s) in that part (systematic faults)
- the probability of occurrence of a fault(s) in that part and relevant parameters
- the mean time to dangerous failure (MTTFd)
- the diagnostic coverage (DC)
- the common cause failure (CCF) in the case of categories 2, 3 and 4

---

### 6.2 Specifications of Categories

#### 6.2.1 General

Each SRP/CS shall comply with the requirements of the relevant category, see 6.2.3 to 6.2.7.

The designated architectures show not examples but general architectures. Any deviation shall be justified by means of appropriate analytical tools (e.g. Markov modelling, fault tree analysis), such that the system meets the required performance level (PLr).

The lines and arrows in Figures 8 to 12 represent logical interconnecting means and logical possible diagnostic means.

#### 6.2.2 Designated Architectures

The structure of a SRP/CS is a key characteristic having great influence on the PL. Most structures which are present in the machinery field can be mapped to one of the categories. For each category, a typical representation as a safety-related block diagram can be made.

> Note: In some cases arising from a specific technical solution or determined by a type-C standard, the safety-related performance of the SRP/CS can be required only by a category without additional PL.

#### 6.2.3 Category B

The SRP/CS shall, as a minimum, be designed, constructed, selected, assembled and combined in accordance with the relevant standards and using basic safety principles for the specific application to withstand:
- the expected operating stresses, e.g. the reliability with respect to breaking capacity and frequency
- the influence of the processed material, e.g. detergents in a washing machine
- other relevant external influences, e.g. mechanical vibration, electromagnetic interference, power supply interruptions or disturbances

There is no diagnostic coverage (DCavg = none) within category B systems and the MTTFd of each channel can be low to medium. The maximum PL achievable with category B is PL = b.

> Note: When a fault occurs it can lead to the loss of the safety function.

**Figure 8 — Designated Architecture for Category B**

```
I --im--> L --im--> O
```
Key: im = interconnecting means, I = input (e.g. sensor), L = logic, O = output (e.g. main contactor)

#### 6.2.4 Category 1

For category 1, the same requirements as category B apply. In addition:

SRP/CS of category 1 shall be designed and constructed using well-tried components and well-tried safety principles (see ISO 13849-2).

A "well-tried component" for a safety-related application is a component which has been either:
- (a) widely used in the past with successful results in similar applications, or
- (b) made and verified using principles which demonstrate its suitability and reliability for safety-related applications

> Note 1: Complex electronic components (e.g. PLC, microprocessor, application-specific integrated circuit) cannot be considered as well-tried.

The MTTFd of each channel shall be high. The maximum PL achievable with category 1 is PL = c.

> Note 2: There is no diagnostic coverage (DCavg = none) within category 1 systems.
> Note 3: When a fault occurs it can lead to the loss of the safety function. However, the MTTFd of each channel in category 1 is higher than in category B. Consequently, the loss of the safety function is less likely.

**Figure 9 — Designated Architecture for Category 1**

```
I --im--> L --im--> O
```

#### 6.2.5 Category 2

For category 2, the same requirements as category B apply. Well-tried safety principles according to 6.2.4 shall also be followed. In addition:

SRP/CS of category 2 shall be designed so that their function(s) are checked at suitable intervals by the machine control system. The check shall be performed:
- at the machine start-up, and
- prior to the initiation of any hazardous situation, and/or periodically during operation if the risk assessment shows it is necessary

Any check shall either:
- allow operation if no faults have been detected, or
- generate an output which initiates appropriate control action, if a fault is detected

The DCavg of the total SRP/CS including fault-detection shall be low. The MTTFd of each channel shall be low-to-high, depending on the PLr. Measures against CCF shall be applied (see Annex F).

The maximum PL achievable with category 2 is PL = d.

> Note 1: In some cases category 2 is not applicable because the checking of the safety function cannot be applied to all components.
> Note 2: Category 2 system behaviour allows that: the occurrence of a fault can lead to the loss of the safety function between checks; the loss of safety function is detected by the check.

**Figure 10 — Designated Architecture for Category 2**

```
I --im--> L --im--> O
              |          ^
              m          |
              v          |
             TE --im--> OTE
```
Dashed lines represent reasonably practicable fault detection.
Key: m = monitoring, TE = test equipment, OTE = output of TE

#### 6.2.6 Category 3

For category 3, the same requirements as category B apply. Well-tried safety principles according to 6.2.4 shall also be followed. In addition:

SRP/CS of category 3 shall be designed so that a single fault in any of these parts does not lead to the loss of the safety function. Whenever reasonably practicable, the single fault shall be detected at or before the next demand upon the safety function.

The DCavg of the total SRP/CS including fault-detection shall be low. The MTTFd of each of the redundant channels shall be low-to-high, depending on the PLr. Measures against CCF shall be applied (see Annex F).

> Note 3: Category 3 system behaviour allows that: when the single fault occurs the safety function is always performed; some but not all faults will be detected; accumulation of undetected faults can lead to the loss of the safety function.

**Figure 11 — Designated Architecture for Category 3**

```
I1 --im--> L1 --m--> O1
                ^
                c
I2 --im--> L2 --m--> O2
```
Dashed lines represent reasonably practicable fault detection.
Key: c = cross monitoring, I1/I2 = input devices, L1/L2 = logic, O1/O2 = output devices, m = monitoring

#### 6.2.7 Category 4

For category 4, the same requirements as category B apply. Well-tried safety principles according to 6.2.4 shall also be followed. In addition:

SRP/CS of category 4 shall be designed such that:
- a single fault in any of these safety-related parts does not lead to a loss of the safety function, and
- the single fault is detected at or before the next demand upon the safety functions, e.g. immediately, at switch on, or at end of a machine operating cycle

If this detection is not possible, then an accumulation of undetected faults shall not lead to the loss of the safety function.

The DCavg of the total SRP/CS shall be high, including the accumulation of faults. The MTTFd of each of the redundant channels shall be high. Measures against CCF shall be applied (see Annex F).

> Note 1: Category 4 system behaviour allows that: when a single fault occurs the safety function is always performed; the faults will be detected in time; accumulation of undetected faults is taken into account.
> Note 2: The difference between category 3 and category 4 is a higher DCavg in category 4 and a required MTTFd of each channel of "high" only.

**Figure 12 — Designated Architecture for Category 4**

```
I1 --im--> L1 --m--> O1
                ^
                c (solid lines = high DC)
I2 --im--> L2 --m--> O2
```
Key: c = cross monitoring (solid lines represent higher diagnostic coverage than category 3)

---

### Table 10 — Summary of Requirements for Categories

| Category | Summary of requirements | System behaviour | Principle used to achieve safety | MTTFd of each channel | DCavg | CCF |
|---|---|---|---|---|---|---|
| B | SRP/CS and/or their protective equipment, as well as their components, shall be designed, constructed, selected, assembled and combined in accordance with relevant standards so that they can withstand the expected influence. Basic safety principles shall be used. | The occurrence of a fault can lead to the loss of the safety function. | Mainly characterized by selection of components | Low to medium | None | Not relevant |
| 1 | Requirements of B shall apply. Well-tried components and well-tried safety principles shall be used. | The occurrence of a fault can lead to the loss of the safety function but the probability of occurrence is lower than for category B. | Mainly characterized by selection of components | High | None | Not relevant |
| 2 | Requirements of B and the use of well-tried safety principles shall apply. Safety function shall be checked at suitable intervals by the machine control system. | The occurrence of a fault can lead to the loss of the safety function between the checks. The loss of safety function is detected by the check. | Mainly characterized by structure | Low to high | Low to medium | See Annex F |
| 3 | Requirements of B and the use of well-tried safety principles shall apply. Safety-related parts shall be designed so that a single fault does not lead to the loss of the safety function, and whenever reasonably practicable, the single fault shall be detected. | When a single fault occurs, the safety function is always performed. Some, but not all, faults will be detected. Accumulation of undetected faults can lead to the loss of the safety function. | Mainly characterized by structure | Low to high | Low to medium | See Annex F |
| 4 | Requirements of B and the use of well-tried safety principles shall apply. Safety-related parts shall be designed so that a single fault does not lead to loss, and the single fault is detected at or before the next demand. If not possible, an accumulation of undetected faults shall not lead to loss. | When a single fault occurs the safety function is always performed. Detection of accumulated faults reduces probability of loss (high DC). Faults detected in time. | Mainly characterized by structure | High | High including accumulation of faults | See Annex F |

> Note: For full requirements, see Clause 6.

---

### 6.3 Combination of SRP/CS to Achieve Overall PL

A safety function can be realized by a combination of several SRP/CS: input system, signal processing unit, output system. These SRP/CS may be assigned to one and/or different categories. For each SRP/CS used, a category according to 6.2 shall be selected.

For a series alignment of N separate SRP/CS each performing a safety function:
- (a) Identify the lowest PLi; this is PLlow
- (b) Identify the number Nlow ≤ N of SRP/CSi with PLi = PLlow
- (c) Look-up PL in Table 11

**Figure 13 — Combination of SRP/CS to Achieve Overall PL**

```
[SRP/CS1 PL1] --> [SRP/CS2 PL2] --> ... --> [SRP/CSN PLN]
                     SRP/CS PL
```

**Table 11 — Calculation of PL for Series Alignment of SRP/CS**

| PLlow | Nlow | → | PL |
|---|---|---|---|
| a | > 3 | → | None, not allowed |
| a | ≤ 3 | → | a |
| b | > 2 | → | a |
| b | ≤ 2 | → | b |
| c | > 2 | → | b |
| c | ≤ 2 | → | c |
| d | > 3 | → | c |
| d | ≤ 3 | → | d |
| e | > 3 | → | d |
| e | ≤ 3 | → | e |

> Note: The values calculated for this look-up table are based on reliability values at the mid-point for each PL.

---

## 7. Fault Consideration, Fault Exclusion

### 7.1 General

In accordance with the category selected, safety-related parts shall be designed to achieve the required performance level (PLr). The ability to resist faults shall be assessed.

### 7.2 Fault Consideration

ISO 13849-2 lists the important faults and failures for the various technologies. The lists of faults are not exclusive and, if necessary, additional faults shall be considered and listed. For new components not mentioned in ISO 13849-2, a failure mode and effects analysis (FMEA, see IEC 60812) shall be carried out to establish the faults that are to be considered for those components.

In general, the following fault criteria shall be taken into account:
- if, as a consequence of a fault, further components fail, the first fault together with all following faults shall be considered as a single fault
- two or more separate faults having a common cause shall be considered as a single fault (known as a CCF)
- the simultaneous occurrence of two or more faults having separate causes is considered highly unlikely and therefore need not be considered

### 7.3 Fault Exclusion

It is not always possible to evaluate SRP/CS without assuming that certain faults can be excluded. For detailed information on fault exclusions, see ISO 13849-2.

Fault exclusion is a compromise between technical safety requirements and the theoretical possibility of occurrence of a fault. Fault exclusion can be based on:
- the technical improbability of occurrence of some faults
- generally accepted technical experience, independent of the considered application
- technical requirements related to the application and the specific hazard

If faults are excluded, a detailed justification shall be given in the technical documentation.

---

## 8. Validation

The design of the SRP/CS shall be validated (see Figure 3). The validation shall demonstrate that the combination of SRP/CS providing each safety function meets all relevant requirements of this part of ISO 13849.

For details of validation, see ISO 13849-2.

---

## 9. Maintenance

Preventive or corrective maintenance can be necessary to maintain the specified performance of the safety-related parts. Deviations with time from the specified performance can lead to a deterioration in safety or even to a hazardous situation. The information for use of the SRP/CS shall include instructions for the maintenance (including periodic inspection) of the SRP/CS.

The provisions for the maintainability of the safety-related part(s) of a control system shall follow the principles given in ISO 12100-2:2003, 4.7. All information for maintenance shall comply with ISO 12100-2:2003, 6.5.1e.

---

## 10. Technical Documentation

When designing a SRP/CS, its designer shall document at least the following information relevant to the safety-related part:
- safety function(s) provided by the SRP/CS
- the characteristics of each safety function
- the exact points at which the safety-related part(s) start and end
- environmental conditions
- the performance level (PL)
- the category or categories selected
- the parameters relevant to the reliability (MTTFd, DC, CCF and mission time)
- measures against systematic failure
- the technology or technologies used
- all safety-relevant faults considered
- justification for fault exclusions (see ISO 13849-2)
- the design rationale (e.g. faults considered, faults excluded)
- software documentation
- measures against reasonably foreseeable misuse

> Note: In general, this documentation is foreseen as being for the manufacturer's internal purposes and will not be distributed to the machine user.

---

## 11. Information for Use

The principles of ISO 12100-2:2003, 6.5.2, and the applicable sections of other relevant documents (e.g. IEC 60204-1:2005, Clause 17), shall be applied. Information which is important for the safe use of the SRP/CS shall be given to the user. This shall include, but is not limited to:

- the limits of the safety-related parts to the category(ies) selected and any fault exclusions
- the limits of the SRP/CS and any fault exclusions for which, when essential for maintaining the selected category or categories and safety performance, appropriate information (e.g. for modification, maintenance and repair) shall be given to ensure the continued justification of the fault exclusion(s)
- the effects of deviations from the specified performance on the safety function(s)
- clear descriptions of the interfaces to the SRP/CS and protective devices
- response time
- operating limits (including environmental conditions)
- indications and alarms
- muting and suspension of safety functions
- control modes
- maintenance (see Clause 9)
- maintenance check lists
- ease of accessibility and replacing of internal parts
- means for easy and safe trouble shooting
- information explaining the applications for use relevant to the category to which reference is made
- checking test intervals where relevant

Specific information shall be provided on the category or categories and performance level of the SRP/CS, as follows:
- dated reference to this part of ISO 13849 (i.e. "ISO 13849-1:2006")
- the Category, B, 1, 2, 3, or 4
- the performance level, a, b, c, d, or e

> Example: An SRP/CS in accordance with this edition of ISO 13849-1, of Category B and performance level a, would be referred to as: **ISO 13849-1:2006 Category B PL a**

---

## Annex A — Determination of Required Performance Level (PLr) (Informative)

### A.1 Selection of PLr

This annex is concerned with the contribution to the reduction in risk made by the safety-related parts of the control system being considered. The method given here provides only an estimation of risk reduction and is intended as guidance to the designer and standard maker in determining the PLr for each necessary safety function to be carried out by an SRP/CS.

The risk assessment assumes a situation prior to provision of the intended safety function. The severity of injury (denoted by S) is relatively easy to estimate (e.g. laceration, amputation, fatality). For the frequency of occurrence, auxiliary parameters are used to improve the estimation:
- frequency and time of exposure to the hazard (F)
- possibility of avoiding the hazard or limiting the harm (P)

These parameters can be combined, as in Figure A.1, to give a gradation of risk from low to high.

---

### A.2 Guidance for Selecting Parameters S, F and P for the Risk Estimation

#### A.2.1 Severity of Injury S1 and S2

In estimating the risk arising from a failure of a safety function only slight injuries (normally reversible) and serious injuries (normally irreversible) and death are considered.

- **S1**: slight, normally reversible injury (e.g. bruising, lacerations without complications)
- **S2**: serious, normally irreversible injury or death (e.g. amputation, fatality)

#### A.2.2 Frequency and/or Exposure Times to Hazard F1 and F2

F2 should be selected if a person is frequently or continuously exposed to the hazard. The frequency parameter should be chosen according to the frequency and duration of access to the hazard.

- **F1**: seldom-to-less-often and/or exposure time is short
- **F2**: frequent-to-continuous and/or exposure time is long

> Note: In case of no other justification F2 should be chosen if the frequency is higher than once per hour.

Where the demand on the safety function is known by the designer, the frequency and duration of this demand can be chosen instead of the frequency and duration of access to the hazard. In this part of ISO 13849, the frequency of demand on the safety function is assumed to be more than once per year.

#### A.2.3 Possibility of Avoiding the Hazard P1 and P2

- **P1**: possible under specific conditions (e.g. hazard can be directly identified, operation with supervision, experts, slow speed)
- **P2**: scarcely possible (e.g. no chance of avoiding, sudden hazard, non-professionals, high speed)

P1 should only be selected if there is a realistic chance of avoiding an accident or of significantly reducing its effect. P2 should be selected if there is almost no chance of avoiding the hazard.

Aspects which influence the selection of parameter P include:
- operation with or without supervision
- operation by experts or non-professionals
- speed with which the hazard arises (e.g. quickly or slowly)
- possibilities for hazard avoidance (e.g. by escaping)
- practical safety experiences relating to the process

**Figure A.1 — Risk Graph for Determining Required PLr for Safety Function**

```
Starting point (1)
    |
    +--S1 (slight injury)
    |       |
    |       +--F1 --> P1 --> PLr = a
    |       |          P2 --> PLr = b
    |       +--F2 --> P1 --> PLr = b
    |                 P2 --> PLr = c
    |
    +--S2 (serious injury/death)
            |
            +--F1 --> P1 --> PLr = c
            |          P2 --> PLr = d
            +--F2 --> P1 --> PLr = d
                      P2 --> PLr = e
```

Key:
- S: severity of injury (S1 = slight reversible, S2 = serious irreversible or death)
- F: frequency/time of exposure (F1 = seldom/short, F2 = frequent/continuous)
- P: possibility of avoiding (P1 = possible under specific conditions, P2 = scarcely possible)
- L: low contribution to risk reduction
- H: high contribution to risk reduction

---

## Annex B — Block Method and Safety-Related Block Diagram (Informative)

### B.1 Block Method

The simplified approach requires a block-oriented logical representation of the SRP/CS. The SRP/CS should be separated into a small number of blocks according to the following:

- blocks should represent logical units of the SRP/CS related to the execution of the safety function
- different channels belonging to the same safety function should be separated into different blocks — if one block is no longer able to perform its function, the execution of the safety function through the blocks of the other channel should not be affected
- each channel may consist of one or several blocks — three blocks per channel in the designated architectures (input, logic, output) is not an obligatory number, but simply an example
- each hardware unit of the SRP/CS should belong to exactly one block, thus allowing for the calculation of the MTTFd of the block based on the MTTFd of the hardware units belonging to the block (e.g. by failure mode and effects analysis or the parts count method, see Annex D.1)
- hardware units only used for diagnostics and which do not affect the execution of the safety function in the different channels when they fail dangerously may be separated from hardware units necessary for the execution of the safety function in the different channels

> Note: For the purposes of this part of ISO 13849, "blocks" do not correspond to functional blocks or reliability blocks.

### B.2 Safety-Related Block Diagram

The blocks defined by the block method may be used to graphically represent the logical structure of the SRP/CS in a safety-related block diagram. For such a graphical representation, the following may be of guidance:

- the failure of one block in a series alignment of blocks leads to the failure of the whole channel (e.g. if one hardware unit in one channel of the SRP/CS fails dangerously, the whole channel might not be able to execute the safety function any longer)
- only the dangerous failure of all channels in a parallel alignment leads to the loss of the safety function (e.g. a safety function performed by several channels is executed as long as at least one channel has no failure)
- blocks used only for testing purposes and which do not affect the execution of the safety function in the different channels when they fail dangerously may be separated from blocks in the different channels

**Figure B.1 — Example of Safety-Related Block Diagram**

```
+--[ I1 ]------------------------------------------[ O1 ]--+
|                                                            |
+--[ I2 ]--[ L ]--[ O2 ]----------------------------+       |
                                                    |       |
                      [ T ]  (testing device only)  |       |

Channel 1 (top path):   I1 → O1            (series alignment)
Channel 2 (bottom path): I2 → L → O2      (series alignment)
Both channels execute the safety function redundantly (parallel alignment).
T is only used for testing.
```

Key:
- I1, I2: input devices, e.g. sensor
- L: logic
- O1, O2: output devices, e.g. main contactor
- T: testing device

---

## Annex C — Calculating or Evaluating MTTFd Values for Single Components (Informative)

### C.1 General

This annex gives several methods for calculating or evaluating MTTFd values for single components:
- C.2 is based on the respect of good engineering practices for different kinds of components
- C.3 is applicable to hydraulic components
- C.4 provides a means of calculating the MTTFd of pneumatic, mechanical and electromechanical components from B10d (see C.4.1)
- C.5 lists MTTFd values for electrical components

---

### C.2 Good Engineering Practices Method

If the following criteria are met, the MTTFd or B10d value for a component can be estimated according to Table C.1.

a) The components are manufactured according to basic and well-tried safety principles in accordance with ISO 13849-2:2003, or the relevant standard (see Table C.1) for the design of the component (confirmation in the data sheet of the component).

> Note: This information can be found in the data sheet of the component manufacturer.

b) The manufacturer of the component specifies the appropriate application and operating conditions for the user.

c) The design of the SRP/CS fulfils the basic and well-tried safety principles according to ISO 13849-2:2003, for the implementation and operation of the component.

---

### C.3 Hydraulic Components

If the following criteria are met, the MTTFd value for a single hydraulic component, e.g. valve, can be estimated at 150 years.

a) The hydraulic components are manufactured according to basic and well-tried safety principles in accordance with ISO 13849-2:2003, Tables C.1 and C.2, for the design of the hydraulic component (confirmation in the data sheet of the component).

> Note: This information can be found in the data sheet of the component manufacturer.

b) The manufacturer of the hydraulic component specifies the appropriate application and operating conditions for the user. The SRP/CS manufacturer shall provide information pertaining to his responsibility to apply the basic and well-tried safety principles according to ISO 13849-2:2003, Tables C.1 and C.2, for the implementation and operation of the hydraulic component.

If either a) or b) is not achieved, the MTTFd value for the single hydraulic component has to be given by the manufacturer.

---

**Table C.1 — International Standards Dealing with MTTFd or B10d for Components**

| Component | Basic and well-tried safety principles according to ISO 13849-2:2003 | Other relevant standards | Typical values: MTTFd (years) / B10d (cycles) |
|---|---|---|---|
| Mechanical components | Tables A.1 and A.2 | — | MTTFd = 150 |
| Hydraulic components | Tables C.1 and C.2 | EN 982 | MTTFd = 150 |
| Pneumatic components | Tables B.1 and B.2 | EN 983 | B10d = 20 000 000 |
| Relays and contactor relays with small load (mechanical load) | Tables D.1 and D.2 | EN 50205, IEC 61810, IEC 60947 | B10d = 20 000 000 |
| Relays and contactor relays with maximum load | Tables D.1 and D.2 | EN 50205, IEC 61810, IEC 60947 | B10d = 400 000 |
| Proximity switches with small load (mechanical load) | Tables D.1 and D.2 | IEC 60947, EN 1088 | B10d = 20 000 000 |
| Proximity switches with maximum load | Tables D.1 and D.2 | IEC 60947, EN 1088 | B10d = 400 000 |
| Contactors with small load (mechanical load) | Tables D.1 and D.2 | IEC 60947 | B10d = 20 000 000 |
| Contactors with nominal load | Tables D.1 and D.2 | IEC 60947 | B10d = 2 000 000 |
| Position switches independent of load (a) | Tables D.1 and D.2 | IEC 60947, EN 1088 | B10d = 20 000 000 |
| Position switches (with separate actuator, guard-locking) independent of load (a) | Tables D.1 and D.2 | IEC 60947, EN 1088 | B10d = 2 000 000 |
| Emergency stop devices independent of load (a) | Tables D.1 and D.2 | IEC 60947, ISO 13850 | B10d = 100 000 |
| Emergency stop devices with maximum operational demands (a) | Tables D.1 and D.2 | IEC 60947, ISO 13850 | B10d = 6 050 |
| Push buttons (e.g. enabling switches) independent of load (a) | Tables D.1 and D.2 | IEC 60947 | B10d = 100 000 |

> Note 1: B10d is estimated as two times B10 (50% dangerous failure).
> Note 2: "Small load" means, for example, 20% of the rated value (for more information, see EN 13849-2).
> (a) If fault exclusion for direct opening action is possible.

---

### C.4 MTTFd of Pneumatic, Mechanical and Electromechanical Components

#### C.4.1 General

For pneumatic, mechanical and electromechanical components (pneumatic valves, relays, contactors, position switches, cams of position switches, etc.) it may be difficult to calculate the mean time to dangerous failure (MTTFd for components), which is given in years and which is required by this part of ISO 13849. Most of the time, the manufacturers of these kinds of components only give the mean number of cycles until 10% of the components fail dangerously (B10d). This clause gives a method for calculating a MTTFd for components by using B10 or T (lifetime) given by the manufacturer related closely to the application dependent cycles.

If the following criteria are met, the MTTFd value for a single pneumatic, electromechanical or mechanical component can be estimated according to C.4.2.

a) The components are manufactured according to basic safety principles in accordance with ISO 13849-2:2003, Table B.1 or Table D.1, for the design of the component (confirmation in the data sheet of the component).

> Note: This information can be found in the data sheet of the component manufacturer.

b) The components to be used in category 1, 2, 3 or 4 are manufactured according to well-tried safety principles in accordance with ISO 13849-2:2003, Table B.2 or D.2, for the design of the component (confirmation in the data sheet of the component).

> Note: This information can be found in the data sheet of the component manufacturer.

c) The manufacturer of the component specifies the appropriate application and operating conditions for the user. The SRP/CS manufacturer shall provide information pertaining to his responsibility to fulfil the basic safety principles according to ISO 13849-2:2003, Table B.1 or D.1, for the implementation and operation of the component. For category 1, 2, 3 or 4, the user has to be informed of his responsibility to fulfil the well-tried safety principles according to ISO 13849-2:2003, Tables B.2 or D.2, for the implementation and operation of the component.

#### C.4.2 Calculation of MTTFd for Components from B10d

The mean number of cycles until 10% of the components fail dangerously (B10d) should be determined by the manufacturer of the component in accordance with relevant product standards for the test methods (e.g. IEC 60957-5-1, ISO 19973, IEC 61810). The dangerous failure modes of the component have to be defined, e.g. sticking at an end position or change of switching times. If not all the components fail dangerously during the tests (e.g. seven components tested, only five fail dangerously), an analysis taking into account the components that were not dangerously failed should be performed.

With B10d and n_op, the mean number of annual operations, MTTFd for components can be calculated as:

```
MTTFd = B10d / (0.1 × n_op)                                          (C.1)
```

where:

```
n_op = (d_op × h_op × 3600 s/h) / t_cycle                            (C.2)
```

with the following assumptions having been made on the application of the component:
- h_op: the mean operation, in hours per day
- d_op: the mean operation, in days per year
- t_cycle: the mean time between the beginning of two successive cycles of the component (e.g. switching of a valve) in seconds per cycle

The operation time of the component is limited to T10d, the mean time until 10% of the components fail dangerously:

```
T10d = B10d / n_op                                                    (C.3)
```

> Note: Explanation of the formulas in C.4.2. B10d, the mean number of cycles till 10% of the components fail dangerously, can be converted to T10d, the mean time until 10% of the components fail dangerously, by using n_op, the mean number of annual operations:
>
> T10d = B10d / n_op                                                  (C.4)

The reliability methods in this part of ISO 13849 assume that the failure of components is distributed exponentially over time: F(t) = 1 – exp(–λdt). For pneumatic and electromechanical components, a Weibull distribution is more likely. But if the operation time of the components is limited to the mean time until 10% of the components fail dangerously (T10d), then a constant dangerous failure rate (λd) over this operation time can be estimated as:

```
λd = 0.1/T10d = 0.1 × n_op / B10d                                    (C.5)
```

Equation (C.5) takes into account that with a constant failure rate, 10% of the components in the assumed application fail after T10d [years], corresponding to B10d [cycles]. To be exact:

```
F(T10d) = 1 – exp(–λd × T10d) = 10%   means   λd = –ln(0.9)/T10d = 0.10 536/T10d ≈ 0.1/T10d     (C.6)
```

With MTTFd = 1/λd for exponential distributions, this yields:

```
MTTFd = T10d / 0.1 = B10d / (0.1 × n_op)                             (C.7)
```

#### C.4.3 Example

For a pneumatic valve, a manufacturer determines a mean value of 60 million cycles as B10d. The valve is used for two shifts each day on 220 operation days a year. The mean time between the beginning of two successive switching of the valve is estimated as 5 s. This yields the following values:

- d_op of 220 days per year
- h_op of 16 h per day
- t_cycle of 5 s per cycle
- B10d of 60 million cycles

With these input data the following quantities can be calculated:

```
n_op = (220 day/year × 16 h/day × 3600 s/h) / (5 s/cycle) = 2.53 × 10^6 cycles/year    (C.8)

T10d = (60 × 10^6 cycles) / (2.53 × 10^6 cycles/year) = 23.7 years                     (C.9)

MTTFd = 23.7 years / 0.1 = 237 years                                                    (C.10)
```

This will give a MTTFd for the component "high" according to Table 5. These assumptions are only valid for a restricted operation time of 23.7 years for the valve.

---

### C.5 MTTFd Data for Electrical Components

#### C.5.1 General

Tables C.2 to C.7 indicate some typical average values of MTTFd for electronic components. The data are extracted from the SN 29500 series database. All data are of general type. Various databases available (see the non-exhaustive list in the Bibliography) which present MTTFd values for various electronic components. If the designer of an SRP/CS has other, reliable, specific data on the components used, then the use of that specific data instead is highly recommended.

The values given in Tables C.2 to C.7 are valid for a temperature of 40 °C, nominal load for current and voltage.

In the MTTF column of the tables, the values from SN 29500 are for generic components for all possible failure modes which are not necessarily dangerous failures. In the MTTFd column, it is typically assumed that not all failures modes lead to a dangerous failure. This depends mainly on the application. A precise way of determining the "typical" MTTFd for components is to carry out an FMEA. Some components, e.g. transistors used as switches, can have short circuits or interruptions as failure. Only one of these two modes can be dangerous; therefore the "remarks" column assumes only 50% dangerous failure, which means that the MTTFd for components is twice the given MTTF value. For use where there is doubt, a worst case MTTFd for components is given in the "worst case" MTTFd column, where the safety margin is 10.

#### C.5.2 Semiconductors

See Tables C.2 and C.3.

**Table C.2 — Transistors (Used as Switches)**

| Transistor | Example | MTTF for components (years) | MTTFd for components — Typical (years) | MTTFd for components — Worst case (years) | Remark |
|---|---|---|---|---|---|
| Bipolar | TO18, TO92, SOT23 | 34 247 | 68 493 | 6 849 | 50% dangerous failure |
| Bipolar, low power | TO5, TO39 | 5 708 | 11 416 | 1 142 | 50% dangerous failure |
| Bipolar, power | TO3, TO220, D-Pack | 1 941 | 3 881 | 388 | 50% dangerous failure |
| FET | Junction MOS | 22 831 | 45 662 | 4 566 | 50% dangerous failure |
| MOS, power | TO3, TO220, D-Pack | 1 142 | 2 283 | 228 | 50% dangerous failure |

**Table C.3 — Diodes, Power Semiconductors and Integrated Circuits**

| Diode | Example | MTTF for components (years) | MTTFd for components — Typical (years) | MTTFd for components — Worst case (years) | Remark |
|---|---|---|---|---|---|
| General purpose | — | 114 155 | 228 311 | 22 831 | 50% dangerous failure |
| Suppressor | — | 15 981 | 31 963 | 3 196 | 50% dangerous failure |
| Zener diode Ptot < 1 W | — | 114 155 | 228 311 | 22 831 | 50% dangerous failure |
| Rectifier diodes | — | 57 078 | 114 155 | 11 416 | 50% dangerous failure |
| Rectifier bridges | — | 11 415 | 22 831 | 2 283 | 50% dangerous failure |
| Thyristors | — | 2 283 | 4 566 | 457 | 50% dangerous failure |
| Triacs, Diacs | — | 1 484 | 2 968 | 297 | 50% dangerous failure |
| Integrated circuits (programmable and non-programmable) | Use manufacturer's data | | | | 50% dangerous failure |

---

### C.6 Passive Components

See Tables C.4 to C.7.

**Table C.4 — Capacitors**

| Capacitor | Example | MTTF for components (years) | MTTFd for components — Typical (years) | MTTFd for components — Worst case (years) | Remark |
|---|---|---|---|---|---|
| Standard, no power | KS, KP, KC, KT, MKT, MKC, MKP, MKU, MP, MKV | 57 078 | 114 155 | 11 416 | 50% dangerous failure |
| Ceramic | — | 22 831 | 45 662 | 4 566 | 50% dangerous failure |
| Aluminium electrolytic — Non-solid electrolyte | — | 22 831 | 45 662 | 4 566 | 50% dangerous failure |
| Aluminium electrolytic — Solid electrolyte | — | 37 671 | 75 342 | 7 534 | 50% dangerous failure |
| Tantalum electrolytic — Non-solid electrolyte | — | 11 415 | 22 831 | 2 283 | 50% dangerous failure |
| Tantalum electrolytic — Solid electrolyte | — | 114 155 | 228 311 | 22 831 | 50% dangerous failure |

**Table C.5 — Resistors**

| Resistor | Example | MTTF for components (years) | MTTFd for components — Typical (years) | MTTFd for components — Worst case (years) | Remark |
|---|---|---|---|---|---|
| Carbon film | — | 114 155 | 228 311 | 22 831 | 50% dangerous failure |
| Metal film | — | 570 776 | 1 141 552 | 114 155 | 50% dangerous failure |
| Metal oxide and wire-wound | — | 22 831 | 45 662 | 4 566 | 50% dangerous failure |
| Variable | — | 3 767 | 7 534 | 753 | 50% dangerous failure |

**Table C.6 — Inductors**

| Inductor | Example | MTTF for components (years) | MTTFd for components — Typical (years) | MTTFd for components — Worst case (years) | Remark |
|---|---|---|---|---|---|
| For MC application | — | 37 671 | 75 342 | 7 534 | 50% dangerous failure |
| Low frequency inductors and transformers | — | 22 831 | 45 662 | 4 566 | 50% dangerous failure |
| Main transformers and transformers for switched modes and power supplies | — | 11 415 | 22 831 | 2 283 | 50% dangerous failure |

**Table C.7 — Optocouplers**

| Optocoupler | Example | MTTF for components (years) | MTTFd for components — Typical (years) | MTTFd for components — Worst case (years) | Remark |
|---|---|---|---|---|---|
| Bipolar output | SFH 610 | 7 648 | 15 296 | 1 530 | 50% dangerous failure |
| FET output | LH 1056 | 2 854 | 5 708 | 571 | 50% dangerous failure |

---

## Annex D — Simplified Method for Estimating MTTFd for Each Channel (Informative)

### D.1 Parts Count Method

Use of the "parts count method" serves to estimate the MTTFd for each channel separately. The MTTFd values of all single components which are part of that channel are used in this calculation.

The general formula is:

```
     S           S
1         1           n_j
----- = Σ ------- = Σ -------                                         (D.1)
MTTFd   i=1 MTTFd_i  j=1 MTTFd_j
```

where:
- MTTFd is for the complete channel
- MTTFd_i, MTTFd_j is the MTTFd of each component which has a contribution to the safety function

The first sum is over each component separately; the second sum is an equivalent, simplified form where all n_j identical components with the same MTTFd_j are grouped together.

The example given in Table D.1 gives a MTTFd of the channel of 21.4 years, which is "medium" according to Table 5.

**Table D.1 — Example of the Parts List of a Circuit Board**

| j | Component | Units n_j | MTTFd_j Worst case (years) | 1/MTTFd_j Worst case (1/year) | n_j/MTTFd_j Worst case (1/year) |
|---|---|---|---|---|---|
| 1 | Transistors, bipolar, low power (see Table C.2) | 2 | 1 142 | 0.000 876 | 0.001 752 |
| 2 | Resistor, carbon film (see Table C.5) | 5 | 22 831 | 0.000 044 | 0.000 219 |
| 3 | Capacitor, standard, no power (see Table C.4) | 4 | 11 416 | 0.000 088 | 0.000 350 |
| 4 | Relay (with small load, see C.2) (B10d = 20 000 000 cycle, n_op = 633 600) | 4 | 315.66 | 0.003 168 | 0.012 672 |
| 5 | Contactor (with nominal load, see C.2) (B10d = 2 000 000 cycle, n_op = 633 600) | 1 | 31.57 | 0.031 676 | 0.031 676 |
| | Σ(n_j/MTTFd_j) | | | | 0.046 669 |
| | **MTTFd = 1 / Σ(n_j/MTTFd_j) [years]** | | | | **21.43** |

> Note 1: This method is based on the presumption that a dangerous failure of any component within a channel leads to a dangerous failure of the channel. The MTTFd calculation illustrated by Table D.1 is based upon this.
> Note 2: In this example, the main influence comes from the contactor. The chosen values for MTTFd and B10d for this example are based on Annex C. For the example application d_op = 220 days/year, h_op = 8 h/day and t_cycle = 10 s/cycles is assumed, giving n_op = 633 600 cycles/year. In general, taking manufacturer's values for MTTFd and B10d will lead to a much better result, that is, a higher MTTFd for the channel.

---

### D.2 MTTFd for Different Channels, Symmetrization of MTTFd for Each Channel

The designated architectures of 6.2 assume that for different channels in a redundant SRP/CS the values for MTTFd for each channel are the same. This value per channel should be input for Figure 5.

If the MTTFd of the channels differ, there are two possibilities:
- as a worst case assumption, the lower value should be taken into account
- Equation D.2 can be used as an estimation of a value that can be substituted for MTTFd for each channel:

```
         2  [                      1                  ]
MTTFd = --- [ MTTFdC1 + MTTFdC2 - -------------------]               (D.2)
         3  [                    1/MTTFdC1 + 1/MTTFdC2]
```

where MTTFdC1 and MTTFdC2 are the values for two different redundant channels.

> Example: One channel has an MTTFdC1 = 3 years, the other channel has an MTTFdC2 = 100 years, then the resulting MTTFd = 66 years for each channel. This means a redundant system with 100 years MTTFd in one channel and 3 years MTTFd in the other channel is equal to a system where each channel has a MTTFd of 66 years.

A redundant system with two channels and different MTTFd values for each channel can be substituted by a redundant system with identical MTTFd in each channel by using the above formula. This procedure is necessary for the correct use of Figure 5.

> Note: This method assumes independent parallel channels.

---

## Annex E — Estimates for Diagnostic Coverage (DC) for Functions and Modules (Informative)

### E.1 Examples of Diagnostic Coverage (DC)

See Table E.1.

**Table E.1 — Estimates for Diagnostic Coverage (DC)**

**Input device**

| Measure | DC |
|---|---|
| Cyclic test stimulus by dynamic change of the input signals | 90% |
| Plausibility check, e.g. use of normally open and normally closed mechanically linked contacts | 99% |
| Cross monitoring of inputs without dynamic test | 0% to 99%, depending on how often a signal change is done by the application |
| Cross monitoring of input signals with dynamic test if short circuits are not detectable (for multiple I/O) | 90% |
| Cross monitoring of input signals and intermediate results within the logic (L), and temporal and logical software monitor of the program flow and detection of static faults and short circuits (for multiple I/O) | 99% |
| Indirect monitoring (e.g. monitoring by pressure switch, electrical position monitoring of actuators) | 90% to 99%, depending on the application |
| Direct monitoring (e.g. electrical position monitoring of control valves, monitoring of electromechanical devices by mechanically linked contact elements) | 99% |
| Fault detection by the process | 0% to 99%, depending on the application; this measure alone is not sufficient for the required performance level e |
| Monitoring some characteristics of the sensor (response time, range of analogue signals, e.g. electrical resistance, capacitance) | 60% |

**Logic**

| Measure | DC |
|---|---|
| Indirect monitoring (e.g. monitoring by pressure switch, electrical position monitoring of actuators) | 90% to 99%, depending on the application |
| Direct monitoring (e.g. electrical position monitoring of control valves, monitoring of electromechanical devices by mechanically linked contact elements) | 99% |
| Simple temporal time monitoring of the logic (e.g. timer as watchdog, where trigger points are within the program of the logic) | 60% |
| Temporal and logical monitoring of the logic by the watchdog, where the test equipment does plausibility checks of the behaviour of the logic | 90% |
| Start-up self-tests to detect latent faults in parts of the logic (e.g. program and data memories, input/output ports, interfaces) | 90% (depending on the testing technique) |
| Checking the monitoring device reaction capability (e.g., watchdog) by the main channel at start-up or whenever the safety function is demanded or whenever an external signal demand it, through an input facility | 90% |
| Dynamic principle (all components of the logic are required to change the state ON-OFF-ON when the safety function is demanded), e.g. interlocking circuit implemented by relays | 99% |
| Invariable memory: signature of one word (8 bit) | 90% |
| Invariable memory: signature of double word (16 bit) | 99% |
| Variable memory: RAM-test by use of redundant data e.g. flags, markers, constants, timers and cross comparison of these data | 60% |
| Variable memory: check for readability and write ability of used data memory cells | 60% |
| Variable memory: RAM monitoring with modified Hamming code or RAM self-test (e.g. "galpat" or "Abraham") | 99% |
| Processing unit: self-test by software | 60% to 90% |
| Processing unit: coded processing | 90% to 99% |
| Fault detection by the process | 0% to 99%, depending on the application; this measure alone is not sufficient for the required performance level e |

**Output device**

| Measure | DC |
|---|---|
| Monitoring of outputs by one channel without dynamic test | 0% to 99% depending on how often a signal change is done by the application |
| Cross monitoring of outputs without dynamic test | 0% to 99% depending on how often a signal change is done by the application |
| Cross monitoring of output signals with dynamic test without detection of short circuits (for multiple I/O) | 90% |
| Cross monitoring of output signals and intermediate results within the logic (L) and temporal and logical software monitor of the program flow and detection of static faults and short circuits (for multiple I/O) | 99% |
| Redundant shut-off path with no monitoring of the actuator | 0% |
| Redundant shut-off path with monitoring of one of the actuators either by logic or by test equipment | 90% |
| Redundant shut-off path with monitoring of the actuators by logic and test equipment | 99% |
| Indirect monitoring (e.g. monitoring by pressure switch, electrical position monitoring of actuators) | 90% to 99%, depending on the application |
| Fault detection by the process | 0% to 99%, depending on the application; this measure alone is not sufficient for the required performance level e |
| Direct monitoring (e.g. electrical position monitoring of control valves, monitoring of electromechanical devices by mechanically linked contact elements) | 99% |

> Note 1: For additional references for DC, see e.g. IEC 61508-2:2000, Tables A.2 to A.15.
> Note 2: If medium or high DC is claimed for the logic, at least one measure for variable memory, invariable memory and processing unit with each DC at least 60% has to be applied. There may also be measures that used other than those listed in this table.

---

### E.2 Estimation of Average DC (DCavg)

In many systems, several measures for fault detection might be used. These measures could check different parts of the SRP/CS and have different DC. For an estimation of the PL according to Figure 5 only one, average, DC for the whole SRP/CS performing the safety function is applicable.

DC may be determined as the ratio between the failure rate of detected dangerous failures and the failure rate of total dangerous failures. According to this definition an average diagnostic coverage DCavg is estimated by the following formula:

```
        DC1/MTTFd1 + DC2/MTTFd2 + ... + DCN/MTTFdN
DCavg = ---------------------------------------------                 (E.1)
          1/MTTFd1 + 1/MTTFd2 + ... + 1/MTTFdN
```

Here all components of the SRP/CS without fault exclusion have to be considered and summed up. For each block, the MTTFd and the DC are taken into account. DC in this formula means the ratio of the failure rate of detected dangerous failures of the part (regardless of the measures used to detect the failures) to the failure rate of all dangerous failures of the part. Thus, DC refers to the tested part and not to the testing device. Components without failure detection (e.g. which are not tested) have DC = 0 and contribute only to the denominator of DCavg.

---

## Annex F — Estimates for Common Cause Failure (CCF) (Informative)

### F.1 Requirements for CCF

A comprehensive procedure for measures against CCF for sensors/actuators and separately for control logic is given, for example, in IEC 61508-6:2000, Annex D. Not all measures given therein are applicable to the machinery site. The most important measures are given here.

> Note: In this part of ISO 13849, it is assumed that for redundant systems a β-factor according to IEC 61508-6:2000, Annex D should be less than or equal to 2%.

### F.2 Estimation of Effect of CCF

This quantitative process should be passed for the whole system. Every part of the safety-related parts of the control system should be considered.

Table F.1 lists the measures and contains associated values, based on engineering judgement, which represent the contribution each measure makes in the reduction of common cause failures.

For each listed measure, only the full score or nothing can be claimed. If a measure is only partly fulfilled, the score according to this measure is zero.

Table F.1 gives a quantification of CCF.

**Table F.1 — Scoring Process and Quantification of Measures Against CCF**

| No. | Measure against CCF | Score |
|---|---|---|
| **1** | **Separation / Segregation** | **15** |
| | Physical separation between signal paths: | |
| | — separation in wiring/piping | |
| | — sufficient clearances and creep age distances on printed-circuit boards | |
| **2** | **Diversity** | **20** |
| | Different technologies/design or physical principles are used, for example: | |
| | — first channel programmable electronic and second channel hardwired | |
| | — kind of initiation | |
| | — pressure and temperature | |
| | Measuring of distance and pressure, digital and analog. | |
| | Components of different manufactures. | |
| **3** | **Design / Application / Experience** | |
| | 3.1 Protection against over-voltage, over-pressure, over-current, etc. | **15** |
| | 3.2 Components used are well-tried | **5** |
| **4** | **Assessment / Analysis** | **5** |
| | Are the results of a failure mode and effect analysis taken into account to avoid common-cause-failures in design? | |
| **5** | **Competence / Training** | **5** |
| | Have designers/maintainers been trained to understand the causes and consequences of common cause failures? | |
| **6** | **Environmental** | |
| | 6.1 Prevention of contamination and electromagnetic compatibility (EMC) against CCF in accordance with appropriate standards. Fluidic systems: filtration of the pressure medium, prevention of dirt intake, drainage of compressed air, e.g. in compliance with the component manufacturers' requirements concerning purity of the pressure medium. Electric systems: Has the system been checked for electromagnetic immunity, e.g. as specified in relevant standards against CCF? For combined fluidic and electric systems, both aspects should be considered. | **25** |
| | 6.2 Other influences. Have the requirements for immunity to all relevant environmental influences such as temperature, shock, vibration, humidity (e.g. as specified in relevant standards) been considered? | **10** |
| | **Total** | **[max. achievable 100]** |

| Total score | Measures for avoiding CCF |
|---|---|
| 65 or better | Meets the requirements |
| Less than 65 | Process failed — choose additional measures |

> (a) Where technological measures are not relevant, points attached to this column can be considered in the comprehensive calculation.

---

## Annex G — Systematic Failure (Informative)

### G.1 General

ISO 13849-2 gives a comprehensive list of measures against systematic failure which should be applied, such as basic and well-tried safety principles.

### G.2 Measures for the Control of Systematic Failures

The following measures should be applied.

**Use of de-energization (see ISO 13849-2)**

The safety-related parts of the control system (SRP/CS) should be designed so that with loss of its power supply a safe state of the machine can be achieved or maintained.

**Measures for controlling the effects of voltage breakdown, voltage variations, overvoltage, undervoltage**

SRP/CS behaviour in response to voltage breakdown, voltage variations, overvoltage, and undervoltage conditions should be predetermined so that the SRP/CS can achieve or maintain a safe state of the machine (see also IEC 60204-1 and IEC 61508-7:2000, A.8).

**Measures for controlling or avoiding the effects of the physical environment (for example, temperature, humidity, water, vibration, dust, corrosive substances, electromagnetic interference and its effects)**

SRP/CS behaviour in response to the effects of the physical environment should be predetermined so that the SRP/CS can achieve or maintain a safe state of the machine (see also, for example, IEC 60529, IEC 60204-1).

**Program sequence monitoring shall be used with SRP/CS containing software in order to detect defective program sequences**

A defective program sequence exists if the individual elements of a program (e.g. software modules, subprograms or commands) are processed in the wrong sequence or period of time or if the clock of the processor is faulty (see EN 61508-7:2001, A.9).

**Measures for controlling the effects of errors and other effects arising from any data communication process (see IEC 61508-2:2000, 7.4.8)**

In addition, one or more of the following measures should be applied, taking into account the complexity of the SRP/CS and its PL:
- failure detection by automatic tests
- tests by redundant hardware
- diverse hardware
- operation in the positive mode
- mechanically linked contacts
- direct opening action
- oriented mode of failure
- over-dimensioning by a suitable factor, where the manufacturer can demonstrate that derating will improve reliability — where over-dimensioning is appropriate, an over-dimensioning factor of at least 1.5 should be used

See also ISO 13849-2:2002, D.3.

### G.3 Measures for Avoidance of Systematic Failures

The following measures should be applied.

**Use of suitable materials and adequate manufacturing**

Selection of material, manufacturing methods and treatment in relation to, e.g. stress, durability, elasticity, friction, wear, corrosion, temperature, conductivity, dielectric rigidity.

**Correct dimensioning and shaping**

Consideration of, e.g. stress, strain, fatigue, temperature, surface roughness, tolerances, manufacturing.

**Proper selection, combination, arrangements, assembly and installation of components, including cabling, wiring and any interconnections**

Apply appropriate standards and manufacturer's application notes, e.g. catalogue sheets, installation instructions, specifications, and use of good engineering practice.

**Compatibility**

Use components with compatible operating characteristics.

**Withstanding specified environmental conditions**

Design the SRP/CS so that it is capable of working in all expected environments and in any foreseeable adverse conditions, e.g. temperature, humidity, vibration and electromagnetic interference (EMI) (see ISO 13849-2:2002, D.2).

**Use of components designed to an appropriate standard and having well-defined failure modes**

To reduce the risk of undetected faults by the use of components with specific characteristics (see IEC 61508-7:2000, B.3.3).

In addition, one or more of the following measures should be applied, taking into account the complexity of the SRP/CS and its PL:

**Hardware design review (e.g. by inspection or walk-through)**

To reveal by reviews and analysis discrepancies between the specification and implementation (see IEC 61508-7:2000, B.3.7 and B.3.8).

**Computer-aided design tools capable of simulation or analysis**

Perform the design procedure systematically and include appropriate automatic construction elements that are already available and tested (see IEC 61508-7:2000, B.3.5).

**Simulation**

Perform a systematic and complete inspection of an SRP/CS design in terms of both the functional performance and the correct dimensioning of their components (see IEC 61508-7:2000, B.3.6).

### G.4 Measures for Avoidance of Systematic Failures During SRP/CS Integration

The following measures should be applied during integration of the SRP/CS:
- functional testing
- project management
- documentation

In addition, black-box testing should be applied, taking into account the complexity of the SRP/CS and its PL.

---

## Annex H — Example of Combination of Several Safety-Related Parts of the Control System (Informative)

Figure H.1 is a schematic diagram of the safety-related parts providing one of the functions controlling a machine actuator. This is not a functional/working diagram and is included only to demonstrate the principle of combining categories and technologies in this one function.

The control is provided through electronic control logic and a hydraulic directional valve. The risk is reduced by a AOPD, which detects access to the hazardous situation and prevents start-up of the fluidic actuator when the light beam is interrupted.

The safety-related parts which provide the safety function are: AOPD, electronic control logic, hydraulic directional valve and the interconnecting means.

These combined safety-related parts provide a stop function as a safety function. As the AOPD is interrupted, the outputs transfer a signal to the electronic control logic, which provides a signal to the hydraulic directional valve to stop the hydraulic flow as the output of the SRP/CS. At the machine, this stops the hazardous movement of the actuator.

This combination of safety-related parts creates a safety function demonstrating the combination of different categories and technologies based on the requirements given in Clause 6. Using the principles given in this part of ISO 13849, the safety-related parts shown in Figure H.2 can be described as follows:

- Category 2, PL = c for the electro-sensitive protective device (light barrier). To reduce the probability of faults this device uses well-tried safety principles.
- Category 3, PL = d for the electronic control logic. To increase the level of safety performance of this electronic control logic, the structure of this SRP/CS is redundant and implements several fault detection measures such that it is able to detect most of single faults.
- Category 1, PL = c for the hydraulic directional valve. The status of being well-tried is mainly application-specific. In this example, the valve is considered to be well-tried. In order to reduce the probability of faults, this device is comprised of well-tried components applied using well-tried safety principles and all application conditions are considered (see 6.2.4).

> Note 1: The position, size and layout of the interconnecting means have also to be taken into account.

This combination leads with PL_low = c and N_low = 2 to an overall performance level of PL = c (see 6.3).

> Note 2: In case of one fault in the category 1 or the category 2 parts of Figure H.2 there may be a loss of the safety function.

**Figure H.1 — Example: Block Diagram Explaining Combination of SRP/CS**

```
+------------------------------------------------------+
|  [Sensors I/F]   [AOPD]                              |
|  SRP/CSa                                             |---> Fa (fluidic actuator)
|  AOPD  Category 2 [Type 2], PL = c                  |
+------------------------------------------------------+
         |
         v
+------------------------------------------------------+
|  [PES]                                               |
|  SRP/CSb                                             |
|  E: Electronic control logic, Category 3, PL = d    |
+------------------------------------------------------+
         |
         v
+------------------------------------------------------+
|  [Hydraulic directional valve  A B / P T]            |
|  SRP/CSc                                             |
|  F: Fluidics, Category 1, PL = c                    |
+------------------------------------------------------+

Key:
AOPD  active optoelectronic protective device (e.g. light barrier)
E     electronic control logic
F     fluidics
Fa    fluidic actuator
H     hazardous movement
```

**Figure H.2 — Substitution of Figure H.1 by Designated Architectures**

```
SRP/CSa (AOPD):                     SRP/CSb (E):                  SRP/CSc (F):
+-------------------+               +------------------------+     +-------------+
|  [I]--[L]--[O]   |               | [I1]--[L1]--[O1]       |     | [I]--[L]--[O]|
| [TE]---[OTE]      |               | [I2]--[L2]--[O2]       |     +-------------+
+-------------------+               +------------------------+

Key:
AOPD  active optoelectronic protective device (e.g. light barrier)
E     electronic control logic
F     fluidics
I, I1, I2   input devices, e.g. sensor
L, L1, L2   logic
O, O1, O2, OTE  output devices, e.g. main contactor
TE    test equipment
```

---

## Annex I — Examples (Informative)

### I.1 General

This annex illustrates the use of the methods given in preceding annexes for identifying safety functions and determining PL. The quantification of two widely used control circuits is given. For the stepwise procedure, see Figure 3.

Two different examples of control circuits, A and B are examined, see Figures I.1 and I.3. Both illustrate the performance of the same safety function of the interlocking of the guard door. The first example is built up as one channel of electromechanical components with high MTTFd values, while the second is made up of two channels — one electromechanical and the other programmable electronic — including tests, but made up of components with lower MTTFd.

### I.2 Safety Function and Required Performance Level (PLr)

For both examples, the safety function of the interlocking of a guard may be chosen as follows.

The dangerous movement will be stopped when the guard door is opened (by de-energizing the power of the electrical motor).

The risk parameters according to the risk graph method (see Figure A.1) are the following:
- severity of injury, S = S2, serious
- frequency and/or exposure time to hazard, F = F1, seldom to less often and/or the exposure time is short
- possibility of avoiding the hazard, P = P1, possible under specific conditions

These decisions lead to a required performance level PLr of c.

Determination of the preferred category: a performance level of c can be achieved typically by very reliable single-channel systems (category 1) or redundant architectures (category 2 or 3) (see Figure 5 and Clause 6).

### I.3 Example A, Single-Channel System

#### I.3.1 Identification of Safety-Related Parts

All components contributing to the safety function are represented in Figure I.1. Functional details not contributing to the safety function of interlocking (such as start and stop switches) are omitted.

**Figure I.1 — Control Circuit A for Performing Safety Function**

```
Guard door
  [o/c switch]
       |
      SW1A (NC door switch)
       |
      K1A (contactor)
       |
      [M] Motor

Key:
o    open
c    close
M    motor
K1A  contactor
SW1A switch (NC)
```

In this example, a door switch has normally closed contacts (but no fault exclusion is justified) and is connected to a contactor able to switch off the power connection to the motor:
- one channel of electromechanical components
- switch SW1A has medium MTTFd
- contactor K1A has low MTTFd

The chosen contactor in this example is a well-tried component when implemented according to ISO 13849-2.

Thus the safety-related parts and their division into channels can be illustrated in a safety-related block diagram as shown in Figure I.2.

**Figure I.2 — Safety-Related Block Diagram Identifying Safety-Related Parts of Example A**

```
+--------+     +--------+
|  SW1A  |---->|  K1A   |
+--------+     +--------+

Key:
K1A   contactor
SW1A  switch
```

#### I.3.2 Quantification of MTTFd for Each Channel, DCavg, Common Cause Failure, Category and PL

The values for MTTFd for each channel, DCavg and common cause failure are assumed to be estimated according to Annexes C, D, E and F, or to be given by the manufacturer. The categories are estimated according to 6.2.

**MTTFd**

The contactor K1A and the switch SW1A contribute to the MTTFd of the one channel. The MTTFd,K1A of 50 years and the MTTFd,SW1A of 20 years are assumed to be given by the manufacturer. The parts count method of D.1 yields for the MTTFd of the one channel:

```
  1         1           1       1        1
----- = --------- + --------- = ------ + ------ = 0.07/years         (I.1)
MTTFd   MTTFd_SW1A  MTTFd_K1A  20 years  50 years
```

which leads to MTTFd = 14.3 years or "medium" for the channel according to 4.5.2, Table 5.

> Note: If no information for K1A were available, a worst case assumption according to C.2 or C.4 could be made.

**DC**

Because no testing is done in control circuit A, the DC = 0 or "none" according to 4.5.3, Table 6.

**Category**

Although the preferred category for this circuit is category 1, the resulting MTTFd of the channel is "medium". This is an argument that only category B is reached by this design.

Input data for Figure 5: MTTFd for each channel is "medium" (14.3 years), DCavg is "none" and category is B.

This may be interpreted as performance level b.

This result does not match the required performance level c according to I.2. The circuit thus has to be redesigned and re-evaluated until performance level c is reached, in order to meet the requirements for risk reduction of the example application of I.2.

### I.4 Example B, Redundant System

#### I.4.1 Identification of Safety-Related Parts

All components contributing to the safety function are represented in Figure I.3. Functional details not contributing to the safety function of interlocking (as start and stopswitches or delayed switching of K1B) are omitted.

**Figure I.3 — Control Circuit B to Perform the Safety Function**

```
Guard door                               L
  [o/c switch]
    |         |
   SW1B      SW2                    K1B (contactor)
   (NC)      (NO)                        |
             |                         SIB (safe impulse blocking) --> CC (current converter)
             PLC                                                          |
             |                         RS (rotation sensor) <-------[M] Motor
             Cs (stop function standard)

Key:
PLC   programmable logic controller
CC    current converter
M     motor
RS    rotation sensor
Cs    stop function (standard)
SIB   safe impulse blocking
K1B   contactor
SW1B  switch (NC)
SW2   switch (NO)
o     open
c     close
```

In this second example two channels providing redundancy are used. The first channel, similarly to that in example A, uses a door switch having direct opening action and which is used in the positive mode of actuation. This door switch is connected to a contactor able to switch off the power connection to the motor. In the second channel additional (programmable) electronic components are used. A second door switch is connected to a programmable logic controller which can control the current converter to switch off the power connection to the motor:
- redundant channels, one electromechanical and the other programmable electronic
- switch SW1B has positive mechanical action of the contacts; SW2 has medium MTTFd
- contactor K1B has medium MTTFd; the chosen contactor in this example is not a well-tried component
- electronic components have medium MTTFd

So the safety-related parts and their division into channels can be illustrated in a safety-related block diagram as shown in Figure I.4.

> Note: With respect to redundant diversity, requirements for software according to 4.6 for the PLC path are not considered relevant.

**Figure I.4 — Block Diagrams Identifying Safety-Related Parts of Example B**

```
Channel 1:  +--------+     +--------+
            |  SW1B  |---->|  K1B   |
            +--------+     +--------+

Channel 2:  +--------+     +--------+     +--------+
            |  SW2   |---->|  PLC   |---->|  CC    |
            +--------+     +--------+     +--------+

Test:       +--------+
            |   RS   |  (tests the current converter)
            +--------+

SW1B and K1B build up the first channel; SW2, PLC and CC build up the second channel.
RS is only used to test the current converter.

Key:
SW1B  interlocking device
K1B   contactor
SW2   switch
PLC   programmable logic controller
CC    current converter
RS    rotation sensor
```

#### I.4.2 Quantification of MTTFd for Each Channel, DCavg, Common Cause Failure, Category and PL

The values for MTTFd for each channel and common cause failure are assumed to be evaluated according to Annexes C, D, E and F, or to be given by the manufacturer. The categories are estimated according to 6.2.

The switch SW1B has a direct opening action and is used in the positive mode of actuation. Therefore, a fault exclusion is made concerning non-opening of a contact and non-actuation of the switch due to mechanical failure (e.g. break of plunger, wear of the actuating cam, maladjustment).

> Note: These assumptions are valid for auxiliary circuit switches according to IEC 60957-5-1:1997, Annex K, and for adequate mechanical fixing and actuation of the switches according to the manufacturer's specification (see also ISO 13849-2).

**MTTFd**

The contactor K1B is the only element contributing to the MTTFd of the one channel. The MTTFd,K1B of 30 years is assumed to be given by the manufacturer. The parts count method of D.1 yields for the MTTFd of the one channel:

```
   1           1
-------- = ---------                                                  (I.2)
MTTFdC1    MTTFd_K1B
```

which leads to MTTFd = 30 years for the channel.

In the second channel SW2, PLC and CC are contributing to MTTFdC2. For these three components as well as for RS a MTTFd of 20 years is assumed to be given by the manufacturer. The parts count method of D.1 yields for the MTTFd of the second channel:

```
    1           1             1             1        1        1       0.15
--------- = ----------- + ----------- + --------- = ------ + ------ + ------ = -----    (I.3)
MTTFd_C2    MTTFd_SW2     MTTFd_PLC     MTTFd_CC    20 yrs   20 yrs   20 yrs   years
```

which leads to MTTFd = 6.7 years for the channel.

Because both channels have different MTTFd, the formula of D.2 can be used to calculate a substitutional value for a single-channel MTTFd of a symmetrical two-channel system. This formula yields MTTFd = 20 years or "medium" for the channel according to 4.5.2, Table 5.

**DC**

In control circuit B, four of the safety-related parts are tested by the PLC: SW2 and K1B are read back by the PLC, the PLC performs self-tests and the CC is read back via RS by the PLC. The calculated DC of every tested part are:

1. DC_SW2 = 60%, "low", due to monitoring of input signals without dynamic test, see Table E.1 (third row of input device part).
2. DC_K1B = 99%, "high", due to normally open and normally closed mechanically linked contacts, see Table E.1 (second row of input device part).
3. DC_PLC = 30%, "none", due to low effectiveness of self-tests (it is assumed that the manufacturer has calculated this value by FMEA).
4. DC_CC = 90%, "medium", due to redundant shut-off path with monitoring of the actuator by control logic, see Table E.1 (sixth row of output device part) — if the PLC monitors a failure of CC, it is able to stop the motion with the safe impulse blocking (additional shut-off path).

For an estimation of the PL, an average DC value (DCavg) is needed as input for Figure 5:

```
DCavg = (DC_SW2/MTTFdSW2 + DC_K1B/MTTFdK1B + DC_PLC/MTTFdPLC + DC_CC/MTTFdCC)
        ------------------------------------------------------------------
        (1/MTTFdSW2 + 1/MTTFdK1B + 1/MTTFdPLC + 1/MTTFdCC)

      = (0.6/20y + 0.99/30y + 0.3/20y + 0.9/20y)     0.123
      = ------------------------------------------ = ------- = 67.1%     (I.4)
        (1/20y + 1/30y + 1/20y + 1/20y)               0.183
```

Thus, the DCavg is "low" according to 4.5.3 and Table 6.

**CCF**

An estimation of the measures against CCF according to F.2 is assumed to have been carried out for control circuit B. Scores are claimed as given in Table I.1.

**Table I.1 — Estimation of the Measures Against CCF for Example B**

| No. | Item | Score for control circuit | Maximum possible score |
|---|---|---|---|
| 1 | Separation/segregation — Physical separation between signal paths | 15 | 15 |
| 2 | Diversity — Different technologies/design or physical principles are used | 20 | 20 |
| 3.1 | Design/application/experience — Protection against overvoltage, overpressure, overcurrent, etc. | None | 15 |
| 3.2 | Components used are well-tried | 5 | 5 |
| 4 | Assessment/analysis — Are the results of a failure mode and effect analysis taken into account to avoid common cause failures in design? | 5 | 5 |
| 5 | Competence/training — Have designers been trained to understand the causes and consequences of common cause failures? | None | 5 |
| 6.1 | Environmental — Prevention of contamination and EMC against CCF in accordance with appropriate standards | 25 | 25 |
| 6.2 | Other influences — Requirements for immunity to all relevant environmental influences (temperature, shock, vibration, humidity) | 10 | 10 |
| | **Total** | **80** | **Max. 100** |

Sufficient measures against CCF require a minimum score of 65. In example B, a score of 80 is sufficient to fulfil the requirements against CCF.

A single fault in any of the parts does not lead to the loss of the safety function. Whenever reasonably practicable the single fault is detected at or before the next demand upon the safety function. The diagnostic coverage (DCavg) is in the range 60% to 90%. The measures against CCF are sufficient. These characteristics are typical for category 3.

Input data for Figure 5: MTTFd for the channel is "medium" (20 years), DCavg is "low" and category is 3.

This may be interpreted as performance level c.

This result matches the required performance level c of I.2. Thus control circuit B meets the requirements for risk reduction of the example application of I.2.

---

## Annex J — Software (Informative)

### J.1 Description of Example

In this annex, exemplary activities for realizing the SRESW of a SRP/CS for PLr = d are presented. The SRP/CS is interfaced with the machine equipment. It ensures:
- the acquisition of information sent by the various sensors
- the processing required to operate the control elements taking into account the safety requirements
- the control of the actuators

The design of the SRESW of this application on function block level is as shown in Figure J.1.

**Figure J.1 — Function Block Level Design of Software Example**

```
Sensors interface:                Processing:            Actuators interface:
+-------------------+             +-------------------+  +--------------------+
| Acquisition        |----------->| Processing        |->| Piloting actuator 1|
| sensor 1           |            | function 1        |  +--------------------+
+-------------------+             +-------------------+
+-------------------+             +-------------------+  +--------------------+
| Acquisition        |------+---->| Processing        |->| Piloting actuator 2|
| sensor 2           |      |     | function 2        |  +--------------------+
+-------------------+       |     +-------------------+
+-------------------+       |                           +--------------------+
| Acquisition        |------+                        -->| Piloting actuator 3|
| sensor 3           |                                  +--------------------+
+-------------------+
+-------------------+
| Acquisition        |
| sensor 4           |
+-------------------+
+-------------------+
| Acquisition        |
| sensor 5           |
+-------------------+
```

---

### J.2 Application of V-Model of Software Safety Lifecycle

Table J.1 presents an exemplary synthesis of activities and documents on application of V-model of software safety lifecycle for a machine control.

**Table J.1 — Activities and Documents Within Software Safety Lifecycle**

| Development activity | Verification activity | Associated documentation |
|---|---|---|
| **Machine aspect:** Identification of the functions involving the SRP/CS | Identification of safety-related functions | "Safety-related specification for machine control" |
| **Architecture aspect:** Definition of the control architecture with sensors and actuators | Comments upon safety characteristics of chosen components | "Definition of the control architecture" |
| **Software specification aspect:** Transcription of machine functions into software functions | Re-reading of the descriptions (see J.3) | "Software descriptions" |
| **Software architecture aspect:** To detail the functions into functional blocks | Definition of critical blocks which are subject of greater review and validation effort | "Function block modelling" |
| **Encoding aspect:** Encoding according to the programming rules (see J.4) | Re-reading of the code. Verification of functions and compliance with rules. | "Encoding comments in the code"; "Encoding re-reading sheets" |
| **Validation aspect:** Making of test scenarios: operation aspect of functions; behaviour-on-failure aspect | Verification of the test covering; Verification of the test results | "Correspondence matrix" which cross-references specification paragraphs and tests; "Test sheets" comprising test scenario and comments upon results achieved |

---

### J.3 Verification of Software Specification

As part of the software safety lifecycle, the verification activity at level of the software specification consists in reading the descriptions so as to verify that all the sensitive points are properly described. The following should be considered when verifying each function:
- limiting the cases of erroneous interpretation of the system specification
- avoiding gaps in specification resulting in an a priori unknown behaviour of the SRP/CS
- precisely defining conditions for activation and de-activation of functions
- precisely guaranteeing that all the possible cases are handled
- consistency tests
- the different parameterizing cases
- the reaction following a failure

---

### J.4 Example of Programming Rules

For the CCF, in general it should be possible to authenticate the program by author, date of loading, version and last type of access. Concerning the programming rules the following rules can be differentiated.

**a) Programming rules at level of the program structure**

The programming should be structured so as to display a consistent and understandable general skeleton allowing the different processings to be easily localized. This implies:

1. use of templates for typical program or function blocks
2. partitioning of the program into segments in order to identify main parts corresponding to "inputs", "processings" and "outputs"
3. comments on each program section in the source of the program to facilitate the updating of the comment in case of modification
4. description of the role a function block has when calling this block
5. that memory location should be used only by one single kind of data type and be marked by unique labels
6. that the working sequence should not depend on variables such as a jump address calculated at runtime of the program, conditional jumps being authorized

**b) Programming rules regarding the use of variables**

- The activation or de-activation of any output should take place only once (centralized conditions).
- The program should be structured such that the equations for updating a variable are centralized.
- Each global variable, input or output, should have a mnemonic name explicit enough and be described by a comment within the source.

**c) Programming rules at level of a function block**

- Preferably use function blocks that have been validated by the supplier of the SRP/CS, checking that the assumed operating conditions for these validated blocks correspond to the conditions of the program.
- The size of the coded block should be limited to the following guideline values:
  - (i) parameters — maximum eight digital and two integer inputs, one output
  - (ii) function code — maximum ten local variables, maximum 20 Boolean equations
- The function blocks should not modify the global variables.
- A digital value should be controlled relative to pre-set benchmarks to ensure the domain of validity.
- A function block should try to detect inconsistencies of variables to be processed.
- The fault code of a block should be accessible to discriminate a fault among others.
- The fault codes and the state of the block after fault detection should be described by comments.
- The resetting of the block or the restoration of a normal state should be described by comments.

---

## Annex K — Numerical Representation of Figure 5 (Informative)

**Table K.1 — Numerical Representation of Figure 5**

Average probability of a dangerous failure per hour (1/h) and corresponding performance level (PL):

| MTTFd for each channel (years) | Cat. B DC_avg = none | PL | Cat. 1 DC_avg = none | PL | Cat. 2 DC_avg = low | PL | Cat. 2 DC_avg = medium | PL | Cat. 3 DC_avg = low | PL | Cat. 3 DC_avg = medium | PL | Cat. 4 DC_avg = high | PL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 3.80 × 10⁻⁵ | a | — | — | 2.58 × 10⁻⁵ | a | 1.99 × 10⁻⁵ | a | 1.26 × 10⁻⁵ | a | 6.09 × 10⁻⁶ | b | — | — |
| 3.3 | 3.46 × 10⁻⁵ | a | — | — | 2.33 × 10⁻⁵ | a | 1.79 × 10⁻⁵ | a | 1.13 × 10⁻⁵ | a | 5.41 × 10⁻⁶ | b | — | — |
| 3.6 | 3.17 × 10⁻⁵ | a | — | — | 2.13 × 10⁻⁵ | a | 1.62 × 10⁻⁵ | a | 1.03 × 10⁻⁵ | a | 4.86 × 10⁻⁶ | b | — | — |
| 3.9 | 2.93 × 10⁻⁵ | a | — | — | 1.95 × 10⁻⁵ | a | 1.48 × 10⁻⁵ | a | 9.37 × 10⁻⁶ | a | 4.40 × 10⁻⁶ | b | — | — |
| 4.3 | 2.65 × 10⁻⁵ | a | — | — | 1.76 × 10⁻⁵ | a | 1.33 × 10⁻⁵ | a | 8.36 × 10⁻⁶ | a | 3.89 × 10⁻⁶ | b | — | — |
| 4.7 | 2.43 × 10⁻⁵ | a | — | — | 1.60 × 10⁻⁵ | a | 1.20 × 10⁻⁵ | a | 7.58 × 10⁻⁶ | a | 3.48 × 10⁻⁶ | b | — | — |
| 5.1 | 2.24 × 10⁻⁵ | a | — | — | 1.47 × 10⁻⁵ | a | 1.10 × 10⁻⁵ | a | 6.91 × 10⁻⁶ | a | 3.15 × 10⁻⁶ | b | — | — |
| 5.6 | 2.04 × 10⁻⁵ | a | — | — | 1.33 × 10⁻⁵ | a | 9.87 × 10⁻⁶ | a | 6.21 × 10⁻⁶ | a | 2.83 × 10⁻⁶ | b | — | — |
| 6.2 | 1.84 × 10⁻⁵ | a | — | — | 1.19 × 10⁻⁵ | a | 8.80 × 10⁻⁶ | a | 5.53 × 10⁻⁶ | a | 2.47 × 10⁻⁶ | b | — | — |
| 6.8 | 1.68 × 10⁻⁵ | a | — | — | 1.08 × 10⁻⁵ | a | 7.93 × 10⁻⁶ | a | 4.98 × 10⁻⁶ | a | 2.20 × 10⁻⁶ | b | — | — |
| 7.5 | 1.52 × 10⁻⁵ | a | — | — | 9.75 × 10⁻⁶ | a | 7.10 × 10⁻⁶ | a | 4.45 × 10⁻⁶ | a | 1.95 × 10⁻⁶ | b | — | — |
| 8.2 | 1.39 × 10⁻⁵ | a | — | — | 8.87 × 10⁻⁶ | a | 6.43 × 10⁻⁶ | a | 4.02 × 10⁻⁶ | a | 1.74 × 10⁻⁶ | b | — | — |
| 9.1 | 1.25 × 10⁻⁵ | a | — | — | 7.94 × 10⁻⁶ | a | 5.71 × 10⁻⁶ | a | 3.57 × 10⁻⁶ | a | 1.53 × 10⁻⁶ | b | — | — |
| 10 | 1.14 × 10⁻⁵ | a | 1.14 × 10⁻⁵ | b | 7.18 × 10⁻⁶ | a | 5.14 × 10⁻⁶ | a | 3.21 × 10⁻⁶ | b | 1.36 × 10⁻⁶ | b | — | — |
| 11 | 1.04 × 10⁻⁵ | a | 1.04 × 10⁻⁵ | b | 6.44 × 10⁻⁶ | b | 4.53 × 10⁻⁶ | b | 2.86 × 10⁻⁶ | b | 1.18 × 10⁻⁶ | b | — | — |
| 12 | 9.51 × 10⁻⁶ | a | 9.51 × 10⁻⁶ | b | 5.84 × 10⁻⁶ | b | 4.04 × 10⁻⁶ | b | 2.49 × 10⁻⁶ | b | 1.04 × 10⁻⁶ | c | — | — |
| 13 | 8.78 × 10⁻⁶ | a | 8.78 × 10⁻⁶ | b | 5.33 × 10⁻⁶ | b | 3.64 × 10⁻⁶ | b | 2.23 × 10⁻⁶ | b | 9.21 × 10⁻⁷ | c | — | — |
| 15 | 7.61 × 10⁻⁶ | b | 7.61 × 10⁻⁶ | b | 4.53 × 10⁻⁶ | b | 3.01 × 10⁻⁶ | b | 1.82 × 10⁻⁶ | b | 7.44 × 10⁻⁷ | c | — | — |
| 16 | 7.13 × 10⁻⁶ | b | 7.13 × 10⁻⁶ | b | 4.21 × 10⁻⁶ | b | 2.77 × 10⁻⁶ | b | 1.67 × 10⁻⁶ | b | 6.76 × 10⁻⁷ | c | — | — |
| 18 | 6.34 × 10⁻⁶ | b | 6.34 × 10⁻⁶ | b | 3.68 × 10⁻⁶ | b | 2.37 × 10⁻⁶ | b | 1.41 × 10⁻⁶ | b | 5.67 × 10⁻⁷ | c | — | — |
| 20 | 5.71 × 10⁻⁶ | b | 5.71 × 10⁻⁶ | b | 3.26 × 10⁻⁶ | b | 2.06 × 10⁻⁶ | c | 1.22 × 10⁻⁶ | b | 4.88 × 10⁻⁷ | c | — | — |
| 22 | 5.19 × 10⁻⁶ | b | 5.19 × 10⁻⁶ | b | 2.93 × 10⁻⁶ | b | 1.82 × 10⁻⁶ | c | 1.07 × 10⁻⁶ | c | 4.21 × 10⁻⁷ | d | — | — |
| 24 | 4.76 × 10⁻⁶ | b | 4.76 × 10⁻⁶ | b | 2.65 × 10⁻⁶ | b | 1.62 × 10⁻⁶ | c | 9.47 × 10⁻⁷ | c | 3.70 × 10⁻⁷ | d | — | — |
| 27 | 4.23 × 10⁻⁶ | b | 4.23 × 10⁻⁶ | b | 2.32 × 10⁻⁶ | b | 1.39 × 10⁻⁶ | c | 8.09 × 10⁻⁷ | c | 3.10 × 10⁻⁷ | d | — | — |
| 30 | 3.80 × 10⁻⁶ | b | 3.80 × 10⁻⁶ | b | 2.06 × 10⁻⁶ | c | 1.21 × 10⁻⁶ | c | 6.94 × 10⁻⁷ | c | 2.65 × 10⁻⁷ | d | 9.54 × 10⁻⁸ | e |
| 33 | 3.46 × 10⁻⁶ | b | 3.46 × 10⁻⁶ | b | 1.85 × 10⁻⁶ | c | 1.06 × 10⁻⁶ | c | 5.94 × 10⁻⁷ | c | 2.30 × 10⁻⁷ | d | 8.57 × 10⁻⁸ | e |
| 36 | 3.17 × 10⁻⁶ | b | 3.17 × 10⁻⁶ | b | 1.67 × 10⁻⁶ | c | 9.39 × 10⁻⁷ | c | 5.17 × 10⁻⁷ | c | 2.01 × 10⁻⁷ | d | 7.11 × 10⁻⁸ | e |
| 39 | 2.93 × 10⁻⁶ | b | 2.93 × 10⁻⁶ | b | 1.53 × 10⁻⁶ | c | 8.40 × 10⁻⁷ | c | 4.53 × 10⁻⁷ | c | 1.78 × 10⁻⁷ | d | 6.37 × 10⁻⁸ | e |
| 43 | 2.65 × 10⁻⁶ | b | 2.65 × 10⁻⁶ | b | 1.37 × 10⁻⁶ | c | 7.34 × 10⁻⁷ | c | 3.87 × 10⁻⁷ | c | 1.54 × 10⁻⁷ | d | 5.76 × 10⁻⁸ | e |
| 47 | 2.43 × 10⁻⁶ | b | 2.43 × 10⁻⁶ | b | 1.24 × 10⁻⁶ | c | 6.49 × 10⁻⁷ | c | 3.35 × 10⁻⁷ | c | 1.34 × 10⁻⁷ | d | 4.73 × 10⁻⁸ | e |
| 56 | 2.04 × 10⁻⁶ | b | 2.04 × 10⁻⁶ | b | 1.13 × 10⁻⁶ | c | 5.80 × 10⁻⁷ | c | 2.93 × 10⁻⁷ | c | 1.19 × 10⁻⁷ | d | 4.22 × 10⁻⁸ | e |
| 62 | 1.84 × 10⁻⁶ | b | 1.84 × 10⁻⁶ | b | 1.02 × 10⁻⁶ | c | 5.12 × 10⁻⁷ | d | 2.49 × 10⁻⁷ | c | 1.03 × 10⁻⁷ | d | 3.80 × 10⁻⁸ | e |
| 68 | 1.68 × 10⁻⁶ | b | 1.68 × 10⁻⁶ | b | 9.17 × 10⁻⁷ | c | 4.43 × 10⁻⁷ | d | 2.13 × 10⁻⁷ | c | 8.84 × 10⁻⁸ | e | 3.41 × 10⁻⁸ | e |
| 75 | 1.52 × 10⁻⁶ | b | 1.52 × 10⁻⁶ | b | 8.17 × 10⁻⁷ | c | 3.90 × 10⁻⁷ | d | 1.84 × 10⁻⁷ | d | 7.68 × 10⁻⁸ | e | 3.08 × 10⁻⁸ | e |
| 82 | 1.39 × 10⁻⁶ | b | 1.39 × 10⁻⁶ | b | 7.61 × 10⁻⁷ | c | 3.01 × 10⁻⁷ | d | 1.57 × 10⁻⁷ | d | 6.62 × 10⁻⁸ | e | 3.08 × 10⁻⁸ | e |
| 91 | 1.25 × 10⁻⁶ | b | 1.25 × 10⁻⁶ | b | 6.61 × 10⁻⁷ | c | 2.61 × 10⁻⁷ | d | 1.35 × 10⁻⁷ | d | 5.79 × 10⁻⁸ | e | 2.74 × 10⁻⁸ | e |
| 100 | 1.14 × 10⁻⁶ | b | 1.14 × 10⁻⁶ | b | 5.28 × 10⁻⁷ | c | 2.29 × 10⁻⁷ | d | 1.01 × 10⁻⁷ | d | 4.29 × 10⁻⁸ | e | 2.47 × 10⁻⁸ | e |

> Note: "—" indicates not covered for that combination of Category and MTTFd range.

---

*End of AS 4024.1503 Reference Document*