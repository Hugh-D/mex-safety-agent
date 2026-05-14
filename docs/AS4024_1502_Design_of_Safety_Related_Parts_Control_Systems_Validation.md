# AS 4024.1502 — Design of Safety Related Parts of Control Systems: Validation

---

## 1. Scope

This Standard specifies the procedures and conditions to be followed for the validation by both analysis and testing of the safety functions provided, and the category achieved for the safety-related parts of the control system in compliance with AS 4024.1501, using the design rationale provided by the designer.

This Standard does not give complete validation requirements for programmable electronic systems and therefore can require the use of other standards.

> Note: Requirements for programmable electronic systems, including embedded software, are given in the AS 61508 series.

---

## 2. Objective

The objective of this Standard is to provide designers, manufacturers, suppliers, installers and users of safety related parts of control systems with the means of minimising risks to the health and safety of those working with or otherwise near machinery fitted with safety related parts within their control systems.

---

## 3. Referenced Documents

| Standard | Title |
|---|---|
| AS 1447 | Hot-rolled spring steels |
| AS 4024 | Safety of machinery |
| AS 4024.1201 | General principles — Basic terminology and methodology |
| AS 4024.1202 | General principles — Technical principles |
| AS 4024.1301 | Risk assessment — Principles of risk assessment |
| AS 4024.1501 | Design of safety related parts of control systems — General principles for design |
| AS 4024.1602 | Design of controls, interlocks and guarding — Interlocking devices associated with guards — Principles for design and selection |
| AS 4024.1603 | Design of controls, interlocks and guarding — Prevention of unexpected start up |
| AS 4024.1604 | Design of controls, interlocks and guarding — Emergency stop — Principles for design |
| AS 60204 | Safety of machinery — Electrical equipment of machines |
| AS 60204.1 | Part 1: General requirements (IEC 60204-1 Ed.5 FDIS MOD) |
| AS 60269 | Low-voltage fuses |
| AS 60269.1 | Part 1: General requirements |
| AS 60529 | Degrees of protection provided by enclosures (IP Code) |
| AS 60947 | Low-voltage switchgear and control gear |
| AS 60947.2 | Part 2: Circuit-breakers |
| AS 60947.4.1 | Part 4.1: Contactors and motor-starters — Electromechanical contactors and motor-starters |
| AS 60947.5.1 | Part 5.1: Control circuit devices and switching elements — Electromechanical control circuit devices |
| AS 60947.6.2 | Part 6.2: Multiple function equipment — Control and protective switching devices (or equipment) (CPS) |
| AS 61508 | Functional safety of electrical/electronic/programmable electronic safety-related systems (series) |
| ISO 4079 | Rubber hoses and hose assemblies — Textile reinforced hydraulic types — Specifications |
| ISO 4079-1 | Part 1: Oil-based fluid applications |
| IEC 60664 | Insulation coordination for equipment within low-voltage systems |
| IEC 60664-1 | Part 1: Principles, requirements and tests |
| IEC 60947 | Low-voltage switchgear and control gear |
| IEC 60947-5-3 | Part 5-3: Control circuit devices and switching elements — Requirements for proximity devices with defined behaviour under fault conditions |
| IEC 61558 | Safety of power transformers, power supply units and similar |
| IEC 61558-1 | Part 1: General requirements and tests |

---

## 4. Validation Process

### 4.1 Validation Principles

#### 4.1.1 Purpose

The purpose of the validation process is to confirm the specification and the conformity of the design of the safety-related parts of the control system within the overall safety requirements specification of the machinery.

The validation shall demonstrate that each safety-related part meets the requirements of AS 4024.1501, in particular the specified safety characteristics of the safety functions provided by that part, as set out in the design rationale, and the requirements of the specified category according to AS 4024.1501.

Validation should be carried out by persons who are independent of the design of the safety-related part(s).

> Note: Independent person does not necessarily mean that a third party test is required.

The degree of independence should reflect the safety performance of the safety-related part.

#### 4.1.2 Process

Validation consists of applying analysis (see Clause 5) and, if necessary, executing tests (see Clause 6) in accordance with the validation plan. Figure 1 gives an overview of the validation process. The balance between analysis and testing depends on the technology.

The analysis should be started as early as possible and in parallel with the design process, so that problems can be corrected while they are still relatively easy to correct. It can be necessary for some parts of the analysis to be delayed until the design is well developed.

For large systems, due to the size, complexity or integrated form (with the machinery) of the control system, special arrangements may be made for validation of the safety-related parts of the control system separately before integration including simulation of the appropriate input and output signals, and validation of the effects of integrating safety-related parts into the remainder of the control system within the context of its use in the machine.

**Figure 1 — Overview of the Validation Process**

```
START
  |
  +-- Fault lists (Cl. 4.2, 4.3) ----+
  |                                    |
  +-- Design considerations            v
  |                             Validation plan (Cl. 4.4)
  |                                    |
  +-- Validation principles (Cl. 4.1)  |
                                       v
                               Documents (Cl. 4.5)
                                       |
                               Criteria for fault exclusion
                                       |
                                       v
                               Analysis (Cl. 5)
                                       |
                          Is analysis sufficient?
                         /                        \
                       Yes                         No
                        |                           |
                        |                     Testing (Cl. 6)
                        |                           |
                        |                  Is testing complete?
                        |                          /
                        +<------------------------+
                        |
                  Validation records (Cl. 4.6)
                        |
                       END
```

---

### 4.2 Generic Fault Lists

The validation process involves consideration of behaviour of the safety-related part(s) of the control system for all faults to be considered. The generic fault lists contain:

- (a) the components/elements to be included, e.g. conductors/cables
- (b) the faults to be taken into account, e.g. short circuits between conductors
- (c) the permitted fault exclusions
- (d) a remarks section giving the reasons for the fault exclusions

Only permanent faults are taken into account.

> Note: A basis for fault consideration is given in Appendices A, B, C and D.

---

### 4.3 Specific Fault Lists

A specific product-related fault list shall be generated as a reference document for the validation process of the safety-related part(s). The list can be based on the appropriate generic list(s) found in the Appendices.

Where the specific product-related fault list is based on the generic list(s) it shall state:

- (a) the faults taken from the generic list(s) to be included
- (b) any other relevant faults to be included but not given in the generic list (e.g. common mode faults)
- (c) the faults taken from the generic list(s) that may be excluded and can meet at least the criteria given in the generic list(s)

Under exceptional circumstances, the specific product-related fault list may include any other relevant faults, from the generic list but not permitted for exclusion by the generic list(s), together with a justification and a rationale for its exclusion.

Where this list is not based on the generic list(s) the designer shall give the rationale for fault exclusions.

---

### 4.4 Validation Plan

The validation plan shall identify and describe the requirements for carrying out the validation process of the specified safety functions and their categories.

The validation plan shall also identify the means to be employed to validate the specified safety functions and categories. It shall set out, where appropriate:

- (a) the identity of the specification documents
- (b) the operational and environmental conditions
- (c) the basic safety principles (see Paragraphs A2, B2, C2 and D2)
- (d) the well-tried safety principles (see Paragraphs A3, B3, C3 and D3)
- (e) the well-tried components (see Paragraphs A4 and D4)
- (f) the fault assumptions and fault exclusions to be considered, e.g. from the informative fault lists in Paragraphs A5, B5, C5 and D5
- (g) the analyses and tests to be applied

Safety-related parts which have previously been validated to the same specification need only a reference to that previous validation.

---

### 4.5 Information for Validation

The information required for validation will vary with the technology used, the category(ies) to be demonstrated, the design rationale of the system and the contribution of the safety-related parts of control systems to the reduction of risk. Documents containing sufficient information from the following list shall be included in the validation process to demonstrate the category(ies) and the safety function(s) of the safety-related parts which have been achieved:

- (a) Specification(s) of the expected performance, of the safety functions and categories
- (b) Drawings and specifications, e.g. for mechanical, hydraulic and pneumatic parts, printed circuit boards, assembled boards, internal wiring, enclosure, materials, mounting
- (c) Block diagram(s) with functional description of the blocks
- (d) Circuit diagram(s) including interfaces/connections
- (e) Functional description of the circuit diagram(s)
- (f) Time sequence diagram(s) for switching components, signals relevant for safety
- (g) Description of the relevant characteristics of components previously validated
- (h) For other safety-related parts (excluding those listed in Item (g)): component lists with item designations, rated values, tolerances, relevant operating stresses, type designation, failure rate data and component manufacturer and any other data relevant for safety
- (i) Analysis of all relevant faults (see also Clause 4.2) listed e.g. in Paragraphs A5, B5, C5 and D5, including the justification of any excluded faults
- (j) An analysis of the influence of processed materials

Category specific information shall be provided, as required by Table 2. Additionally, where software is relevant to the safety function(s), the software documentation shall include:

- (i) a specification which is clear and unambiguous and states the safety performance the software is required to achieve
- (ii) evidence that the software is designed to achieve the required safety performance
- (iii) details of tests (in particular test reports) carried out to prove that the required safety performance is achieved

---

### 4.6 Validation Record

Validation by analysis and testing shall be recorded. The record shall demonstrate the validation process for each of the safety requirements. Cross-reference may be made to previous validation records, provided they are properly identified.

For any safety-related part which has failed part of the validation process, the validation record shall describe the part(s) of the validation tests and/or analysis which have been failed.

---

### Table 2 — Documentation Requirements for Categories

| Documentation requirement | B | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Basic safety principles | X | X | X | X | X |
| Expected operating stresses | X | X | X | X | X |
| Influences of processed material | X | X | X | X | X |
| Performance during other relevant external influences | X | X | X | X | X |
| Well-tried components | X | X | — | — | — |
| Well-tried safety principles | — | X | X | X | X |
| The check procedure of the safety function(s) | — | — | X | — | — |
| Checking intervals, when specified | — | — | X | — | — |
| Foreseeable, single faults considered in the design and the detection method used | — | — | X | X | X |
| The common mode failures identified and how prevented | — | — | — | X | X |
| The foreseeable, single faults excluded | — | — | — | X | X |
| The faults to be detected | — | — | — | X | X |
| The variety of accumulations of faults considered in the design | — | — | — | X | X |
| How the safety function is maintained in the case of each of the fault(s) | — | — | — | X | X |
| How the safety function is maintained for each of the combination(s) of faults | — | — | — | — | X |

> Notes:
> 1. The categories mentioned in Table 2 are those given in AS 4024.1501.
> 2. X = documentation is required for the category.
> 3. — = Documentation is not required for the category.

---

## 5. Validation by Analysis

### 5.1 General

The validation of safety-related parts of control systems shall be carried out by analysis. Inputs to the analysis are:

- (a) the hazards identified during analysis at the machine
- (b) the reliability
- (c) the system structure
- (d) the non-quantifiable, qualitative aspects which affect system behaviour
- (e) deterministic arguments

Validation of the safety functions by analysis rather than testing requires the formulation of deterministic arguments. Deterministic arguments differ from other evidence in that they show that the required properties of the system follow logically from a model of the system. Such arguments can be constructed on the basis of simple, well-understood concepts, such as the correctness of a mechanical interlock.

> Note: A deterministic argument is an argument based on qualitative aspects (e.g. quality of manufacture, failure rates, experience of use). This consideration is depending on the application. This and other factors can affect the deterministic arguments.

---

### 5.2 Analysis Techniques

The technique of analysis to be chosen depends upon the goal to be achieved. Two basic types of techniques exist:

- **(a) Top-down (deductive) techniques** — suitable for determining the initiating events that can lead to identified top events, and calculating the probability of top events from the probability of the initiating events. They can also be used to investigate the consequences of identified multiple faults. Examples of top-down techniques are Fault Tree Analysis (FTA — see IEC 61025) and Event Tree Analysis (ETA).

- **(b) Bottom-up (inductive) techniques** — suitable for investigating the consequence of identified single faults. Examples of bottom-up techniques are Failure Modes and Effects Analysis (FMEA — see IEC 60812) and Failure Modes, Effects and Criticality Analysis (FMECA).

More information on analysis methods is given in AS 4024.1301.

---

## 6. Validation by Testing

### 6.1 General

When validation by analysis is not sufficient to demonstrate the achievement of specified safety functions and categories, testing shall be carried out to complete the validation. Testing is always complementary to analysis and is often necessary.

Validation tests shall be planned and implemented in a logical manner. Particular attention shall be paid to the following:

- (a) A test plan shall be produced prior to the starting of the test and shall include:
  - (i) test specifications
  - (ii) expected results of test
  - (iii) chronology of the tests
- (b) Test records shall be produced that include:
  - (i) name of the tester
  - (ii) environmental conditions (see Clause 8)
  - (iii) test procedures and equipment used
  - (iv) results of the test
- (c) The test records shall be compared with the test plan to give assurance that the specified functional and performance targets are achieved

The test sample shall be operated as near as possible to its final operating configuration, i.e. with all peripheral devices and covers attached.

Testing can be applied manually or automatically (e.g. by computer).

Where applied, validation of the safety functions by testing shall be carried out by applying inputs, in various combinations, to the safety-related part of the control system. The corresponding outputs shall be compared to the appropriate specified outputs.

It is recommended that the combination of these inputs be applied systematically to the control system and the machine. An example of this logic is: power-on, start-up, operation, directional changes, restart-up. Where necessary, an expanded range of input data shall be applied to take into account anomalous or unusual situations to see how the safety-related parts of the control system respond. Such combinations of input data shall take into account foreseeable incorrect operation(s).

The objectives of the test will be determined by the environmental conditions for that test. The conditions may be:

- (i) the environmental conditions of intended use
- (ii) conditions at a particular rating
- (iii) a given range of conditions if drift is expected

> Note: The range of conditions which is considered stable and over which the tests are valid should be agreed between the designer and the person(s) responsible for carrying out the tests and should be recorded.

---

### 6.2 Measurement Uncertainty

The uncertainty of measurements during the validation by testing shall be appropriate to the test being carried out. In general, these measurement uncertainties shall be within 5 K for temperature measurements and 5% for the following:

- (a) Time measurements
- (b) Pressure measurements
- (c) Force measurements
- (d) Electrical measurements
- (e) Relative humidity measurements
- (f) Linear measurements

Deviations from these measurement uncertainties shall be justified.

---

### 6.3 Higher Requirements

If, according to the information in the accompanying documents, the control system fulfils higher requirements than the requirements according to this standard, the higher requirements shall apply.

> Note: Such higher requirements can apply if the control system has to withstand particularly adverse service conditions, e.g. rough handling, humidity effects, hydrolysation, ambient temperature variations, effects of chemical agents, corrosion, high strength of electromagnetic fields, for example due to close proximity of transmitters.

---

### 6.4 Number of Test Samples

Unless otherwise specified, the tests shall be made on a single production sample of the safety-related part(s) which should withstand all the relevant tests.

Safety-related part(s) under test shall not be modified during the course of the tests.

Some tests can permanently change the performance of some components. Where the permanent change in the components causes the safety-related part(s) to be outside its design specification a new sample(s) shall be used for subsequent tests.

Where a particular test is destructive and equivalent results can be obtained by testing part of the safety-related part(s) of the control system providing the safety function in isolation, a sample of that part may be used instead of the whole safety-related part(s) for the purpose of obtaining the results of the test. This approach shall only be applied where it has been shown by analysis that testing of the safety-related part(s) is sufficient to demonstrate the safety performance of the whole safety-related part providing the safety function.

---

## 7. Validation of Safety Functions

An important step is the validation of the safety functions provided by the safety-related parts of the control system for complete compliance with their specified characteristics. In the validation process it is important to check for errors and particularly for omissions in the formulated specification, provided with the design rationale.

The aim of validation of the safety functions is to ascertain that the safety-related output signals are correct and logically dependent on the input signals according to the specification. The validation should cover all normal and foreseeable abnormal conditions in static and dynamic simulation.

The specified safety functions (in accordance with AS 4024.1501) shall be validated in all operating modes of the machine. This means that validation shall be carried out to demonstrate correct functionality in different configurations sufficient to ensure that all safety-related outputs are realised over their complete ranges. Tests (e.g. overload tests) may be necessary to validate the specified safety functions; and in response to foreseeable abnormal signal from any input source including power interruption and restoration.

> Note: Where appropriate, combinations of different configurations should be considered.

---

## 8. Validation of Categories

### 8.1 Analysis and Testing of Categories

The validation of categories shall demonstrate that their requirements are fulfilled. Principally, the following methods are applicable:

- (a) An analysis from circuit diagrams (see Clause 5)
- (b) Tests on the actual circuit and fault simulation on actual components, particularly in areas of doubt, regarding performance identified during the analysis (see Clause 6)
- (c) A simulation of control system behaviour, e.g. by means of hardware and/or software models

In some applications it may be necessary to divide the connected safety-related parts into several functional groups and to submit these groups and their interfaces to fault simulation tests.

When carrying out validation by testing, the tests may include as appropriate:

- (i) fault injection tests into a production sample
- (ii) fault injection tests into a hardware model
- (iii) software simulation of faults
- (iv) subsystem failure, e.g. power supplies

The precise instant at which a fault is injected into a system can be critical. The worst case effect of a fault injection should be determined by analysis and, according to this analysis, the fault should be injected at the appropriate critical time.

---

### 8.2 Validation of Category Specifications

#### 8.2.1 Category B

The safety-related parts of control systems to category B shall be validated in accordance with basic safety principles by demonstrating that the specification, design, construction and choice of components are in accordance with AS 4024.1501. This shall be achieved by checking that the safety-related part(s) of control systems are in accordance with its specification as provided in the documents for validation. For the validation of environmental conditions see Clause 6.1.

#### 8.2.2 Category 1

Safety-related parts of control systems to category 1 shall be validated by demonstrating the following:

- (a) They meet the requirements of category B.
- (b) Components are well-tried by meeting at least one of the following conditions:
  - (i) they have been widely used with successful results in similar applications; or
  - (ii) they have been made using principles which demonstrate their suitability and reliability for safety-related applications.
- (c) Well-tried safety principles have been implemented correctly.
- (d) Where newly developed principles have been used then validation shall show:
  - (i) how the expected modes of failure have been avoided; and
  - (ii) how faults have been avoided or their probability has been reduced.

Relevant component standards may be used to demonstrate compliance with this Clause.

#### 8.2.3 Category 2

Safety-related parts of control systems to category 2 shall be validated by demonstrating the following:

- (a) They meet the requirements of category B.
- (b) The well-tried safety principles used (if applicable) meet the requirements of Clause 8.2.2(c).
- (c) The checking equipment detects all relevant faults applied one at a time during the checking process and generates an appropriate control action which:
  - (i) initiates a safe state; or when this is not possible
  - (ii) provides a warning of the hazard.
- (d) The check(s) provided by checking equipment do not introduce an unsafe state.
- (e) The initiation of the check is carried out:
  - (i) at the machine start-up and prior to the initiation of a hazardous situation; and
  - (ii) periodically during operation if the risk assessment and the kind of operations show that it is necessary.

#### 8.2.4 Category 3

Safety-related parts of control systems to category 3 shall be validated by demonstrating the following:

- (a) They meet the requirements of category B.
- (b) The well-tried safety principles (if applicable) meet the requirements of Clause 8.2.2(c).
- (c) A single fault does not lead to the loss of the safety function.
- (d) Single faults (including common mode faults) are detected in accordance with the design rationale.

#### 8.2.5 Category 4

Safety-related parts of control systems to category 4 shall be validated by demonstrating that:

- (a) they meet the requirements of category B
- (b) the well-tried safety principles (if applicable) meet the requirements of Clause 8.2.2(c)
- (c) a single fault (including common mode faults) does not lead to the loss of the safety function
- (d) the single faults are detected at or before the next demand on the safety function
- (e) if it is not possible to meet the requirement at Item (d), an accumulation of faults does not lead to the loss of the safety function(s). The extent of the accumulation of faults considered shall be in accordance with the design rationale.

---

### 8.3 Validation of Combination of Safety-Related Parts

Where the safety function is implemented by two or more safety-related parts, validation of the combination (by analysis and, if necessary, by testing) shall be undertaken to establish that the combination achieves the performance specified in the design. Existing recorded validation results of safety-related parts can be taken into account.

---

## 9. Validation of Environmental Requirements

The performance specified in the design for the safety-related parts of the control system shall be validated with respect to the environmental conditions specified for the control system.

Validation shall be carried out by analysis and, if necessary by testing. The extent of the analysis and of the testing will depend upon the safety-related parts, the system in which they are installed, the technology used, and the environmental condition(s) which is being validated. The use of operational reliability data on the system or its components, or the confirmation of compliance to appropriate environmental standards (e.g. for waterproofing or vibration protection) may assist this validation process.

Where applicable validation shall address:

- (a) expected mechanical stresses from shock, vibration or ingress of contaminants
- (b) mechanical durability
- (c) electrical ratings and power supplies
- (d) climatic conditions (temperature and humidity)
- (e) electromagnetic compatibility (immunity)

When testing is necessary to determine compliance with the environmental requirements, the procedures outlined in the relevant Standards shall be followed as far as required for the application.

After the completion of validation by testing, the safety functions shall continue to be in accordance with the specifications for the safety requirements, or the safety-related parts of the control system shall provide output(s) for a safe state.

---

## 10. Validation of Maintenance Requirements

The validation process shall demonstrate that the maintenance requirements as specified in AS 4024.1501 have been implemented.

---

## Appendix A — Validation Tools for Mechanical Systems (Informative)

### A1 Introduction

When mechanical systems are used in conjunction with other technologies, then relevant tables for basic safety and well-tried safety principles should also be taken into account. For further fault exclusions see Clause 4.3.

---

### A2 List of Basic Safety Principles

**Table A1 — Basic Safety Principles**

| Basic safety principle | Remarks |
|---|---|
| Use of suitable materials and adequate manufacturing | Selection of material, manufacturing methods and treatment in relation to, e.g. stress, durability, elasticity, friction, wear, corrosion, temperature. |
| Correct dimensioning and shaping | Consider e.g. stress, strain, fatigue, surface roughness, tolerances, sticking, manufacturing. |
| Proper selection, combination, arrangements, assembly and installation of components/system | Apply manufacturer's application notes, e.g. catalogue sheets, installation instructions, specifications, and use of good engineering practice in similar components/systems. |
| Use of de-energization principle | The safe state is obtained by release of energy. See primary action for stopping in AS 4024.1201. Energy is supplied for starting the movement of a mechanism. See primary action for starting in AS 4024.1202. Consider different modes, e.g. operation mode, maintenance mode. This principle should not be used in special applications, e.g. to keep energy for clamping devices. |
| Proper fastening | For the application of screw locking consider manufacturer's application notes. Overloading can be avoided by applying adequate torque loading technology. |
| Limitation of the generation or transmission of force and similar parameters | Examples are break pin, break plate, torque limiting clutch. |
| Limitation of range of environmental parameters | Examples of parameters are temperature, humidity and pollution at the installation place. See Clause 8 and consider manufacturer's application notes. |
| Limitation of speed and similar parameters | Consider for example the speed, acceleration, deceleration required by the application. |
| Proper reaction time | Consider for example spring relaxation, friction, lubrication, temperature, inertia during acceleration and deceleration, combination of tolerances. |
| Protection against unexpected start-up | Consider unexpected start-up caused by stored energy and after power 'supply' restoration for different modes such as operation mode, maintenance mode etc. Special equipment for release of stored energy may be necessary. Special applications, e.g. to keep energy for clamping devices or ensure a position, need to be considered separately. |
| Simplification | Reduce the number of components in the safety-related system. |
| Separation | Separation of safety-related functions from other functions. |
| Proper lubrication | — |
| Proper prevention of the ingress of fluids and dust | Consider IP rating see AS 60529. |

---

### A3 List of Well-Tried Safety Principles

**Table A2 — Well-Tried Safety Principles**

| Well-tried safety principle | Remarks |
|---|---|
| Use of carefully selected materials and manufacturing | Selection of suitable material, adequate manufacturing methods and treatments related to the application. |
| Use of components with oriented failure mode | The predominant failure mode of a component is known in advance and is always the same, see AS 4024.1202. |
| Over-dimensioning/safety factor | The safety factors are given in standards or by good experience in safety-related applications. |
| Safe position | The moving part of the component is held in one of the possible positions by mechanical means (friction only is not enough). Force is needed for changing the position. |
| Increased OFF force | A safe position/state is obtained by an increased OFF force in relation to ON force. |
| Carefully selection, combination, arrangement, assembly and installation of components/system related to the application | — |
| Carefully selection of fastening related to the application | Avoid relying only on friction. |
| Positive mechanical action | Dependent operation (e.g. parallel operation) between parts is obtained by positive mechanical link(s). Springs and similar 'flexible' elements should not be part of the link(s), see AS 4024.1202. |
| Multiple parts | Reducing the effect of faults by multiplying parts, e.g. where a fault in one spring (of many springs) does not lead to a dangerous condition. |
| Use of well-tried spring | A well-tried spring requires: (a) use of carefully selected materials, manufacturing methods (e.g. presetting and cycling before use) and treatments (e.g. rolling and shot-peening); (b) sufficient guidance of the spring; and (c) sufficient safety factor for fatigue stress (i.e. with high probability a fracture will not occur). Well-tried pressure coil springs may also be designed by: (i) use of carefully selected materials, manufacturing methods and treatments; (ii) sufficient guidance of the spring; (iii) clearance between the turns less than the wire diameter when unloaded; and (iv) sufficient force after a fracture(s) is maintained (i.e. a fracture(s) will not lead to a dangerous condition). |
| Limited range of force and similar parameters | Decide the necessary limitation in relation to the experience and application. Examples for limitations are break pin, break plate, torque limiting clutch. |
| Limited range of speed and similar parameters | Decide the necessary limitation in relation to the experience and application. Examples for limitations are centrifugal governor; safe monitoring of speed or limited displacement. |
| Limited range of environmental parameters | Decide the necessary limitations. Examples on parameters are temperature, humidity and pollution at the installation. See Clause 9 and consider manufacturer's application notes. |
| Limited range of reaction time, limited hysteresis | Decide the necessary limitations. Consider for example spring relaxation, friction, lubrication, temperature, inertia during acceleration and deceleration, combination of tolerances. |

---

### A4 List of Well-Tried Components

Well-tried components for a safety-related application given in Table A3 are based on the application of well-tried safety principles or a standard for their particular applications.

A well-tried component for some applications can be inappropriate for other applications.

**Table A3 — Well-Tried Components**

| Well-tried component | Conditions for 'well-tried' | Standard or specification |
|---|---|---|
| Screw | All factors influencing the screw connection and the application are to be considered. See Table A2. | Mechanical jointing such as screws, nuts, washers, rivets, pins, bolts etc. are standardised. |
| Spring | See Table A2. | Technical specifications for spring steels and other special applications are given in AS 1447. |
| Cam | All factors influencing the cam arrangement (e.g. part of an interlocking device) are to be considered. See Table A2. | See AS 4024.1602. |
| Break-pin (shear-pin) | All factors influencing the application are to be considered. See Table A2. | — |

---

### A5 Fault Lists and Fault Exclusions

#### A5.1 Introduction

The lists express some fault exclusions and their rationale. For further exclusions see Clause 4.3.

The precise instant that the fault occurs can be critical (see Clause 8.1).

#### A5.2 Various Mechanical Devices, Components and Elements

**Table A4 — Mechanical Devices, Components and Elements**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Wear/corrosion | Yes, in the case of carefully selected material, (over)dimensioning, manufacturing process, treatment and proper lubrication, according to the specified life-time (see also Table A2). | See AS 4024.1501. |
| Untightening/loosening | Yes, in the case of carefully selected material, manufacturing process, locking means and treatment, according to the specified life-time (see also Table A2). | — |
| Fracture | Yes, in the case of carefully selected material, (over)dimensioning, manufacturing process, treatment and proper lubrication, according to the specified life-time (see also Table A2). | — |
| Deformation by overstressing | Yes, in the case of carefully selected material, (over)dimensioning, treatment and manufacturing process, according to the specified life-time (see also Table A2). | — |
| Stiffness/sticking | Yes, in the case of carefully selected material, (over)dimensioning, manufacturing process, treatment and proper lubrication, according to the specified life-time (see also Table A2). | — |

> Note: Examples include cam, follower, chain, clutch, brake, shaft, screw, pin, guide and bearing.

#### A5.3 Pressure Coil Springs

**Table A5 — Pressure Coil Springs**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Wear/corrosion | Yes, in the case of the use of well-tried spring(s) and carefully selected fastening(s) (see Table A2). | See AS 4024.1501. |
| Force reduction by setting and fracture | Yes, in the case of the use of well-tried spring(s) and carefully selected fastening(s) (see Table A2). | |
| Stiffness/sticking | Yes, in the case of the use of well-tried spring(s) and carefully selected fastening(s) (see Table A2). | |
| Loosening | Yes, in the case of the use of well-tried spring(s) and carefully selected fastening(s) (see Table A2). | |
| Deformation by overstressing | Yes, in the case of the use of well-tried spring(s) and carefully selected fastening(s) (see Table A2). | |

---

## Appendix B — Validation Tools for Pneumatic Systems (Informative)

### B1 Introduction

When pneumatic systems are used in conjunction with other technologies, then relevant tables for basic safety and well-tried safety principles should also be taken into account. Where pneumatic components are electrically connected/controlled the appropriate fault lists in Appendix D should be considered.

---

### B2 List of Basic Safety Principles

**Table B1 — Basic Safety Principles (Pneumatic)**

| Basic safety principle | Remarks |
|---|---|
| Use of suitable materials and adequate manufacturing | Selection of material, manufacturing methods and treatment in relation to, e.g. stress, durability, elasticity, friction, wear, corrosion, temperature. |
| Correct dimensioning and shaping | Consider e.g. stress, strain, fatigue, surface roughness, tolerances, manufacturing. |
| Proper selection, combination, arrangements, assembly and installation of components/system | Apply manufacturer's application notes, e.g. catalogue sheets, installation instructions, specifications and use of good engineering practice in similar components/systems. |
| Use of de-energization principle | The safe state is obtained by release of energy to all relevant devices. See primary action for stopping in AS 4024.1202. Energy is supplied for starting the movement of a mechanism. See primary action for starting in AS 4024.1202. Consider different modes, e.g. operation mode, maintenance mode. This principle shall not be used in some applications, e.g. where the loss of pneumatic pressure will create an additional hazard. |
| Proper fastening | For the application of for example screw locking, fittings, gluing, clamp ring, consider manufacturer's application notes. Overloading can be avoided by applying adequate torque loading technology. |
| Pressure limitation | Examples are pressure relief valve, pressure reducing/control valve. |
| Speed limitation/speed reduction | An example is the speed limitation of a piston by a flow valve or a throttle. |
| Sufficient avoidance of contamination of the fluid | Consider filtration and separation of solid particles and water in the fluid. |
| Proper range of switching time | Consider: for example the length of pipework, pressure, exhaust capacity, force, spring tiredness, friction, lubrication, temperature, inertia during acceleration and deceleration, combination of tolerances. |
| Withstanding environmental conditions | Design the equipment so that it is capable of working in all expected environments and in any foreseeable adverse conditions, e.g. temperature, humidity, vibration, pollution. See Clause 9 and consider manufacturer's specification/application notes. |
| Protection against unexpected start-up | Consider unexpected start-up caused by stored energy and after power supply restoration for different modes, e.g. operation mode, maintenance mode. Special equipment for release of stored energy may be necessary. See AS 4024.1603. Special applications (e.g. to keep energy for clamping devices or ensure a position) need to be considered separately. |
| Simplification | Reduce the number of components in the safety-related system. |
| Proper temperature range | To be considered throughout the whole system. |
| Separation | Separation of the safety-related functions from other functions. |

---

### B3 List of Well-Tried Safety Principles

**Table B2 — Well-Tried Safety Principles (Pneumatic)**

| Well-tried safety principle | Remarks |
|---|---|
| Over-dimensioning/safety factor | The safety factor is given in standards or by good experience in safety-related applications. |
| Safe position | The moving part of the component is held in one of the possible positions by mechanical means (friction only is not enough). Force is needed to change the position. |
| Increased OFF force | One solution can be that the area ratio for moving a valve spool to the safe position (OFF position) is significantly larger than for moving the spool to ON position (a safety factor). |
| Valve closed by load pressure | These are generally seat valves, for example poppet valves, ball valves. Consider how to apply the load pressure in order to keep the valve closed even if e.g. the spring closing the valve breaks. |
| Positive mechanical action | The positive mechanical action is used for moving parts inside pneumatic components, see also Table A2. |
| Multiple parts | See Table A2. |
| Use of well-tried spring | See Table A2. |
| Speed limitation/speed reduction by resistance to defined flow | Examples are fixed orifice, fixed throttle. |
| Force limitation/force reduction | This can be achieved by a well-tried pressure relief valve which is for example equipped with a well-tried spring, correctly dimensioned and selected. |
| Appropriate range of working conditions | The limitation of working conditions, e.g. pressure range, flow rate and temperature range should be considered. |
| Proper avoidance of contamination of the fluid | Consider high degree of filtration and separation of solid particles and water in the fluid. |
| Sufficient positive overlapping in piston valves | The positive overlapping ensures the stopping function and prevents non-allowed movements. |
| Limited hysteresis | For example increased friction will increase the hysteresis. Combination of tolerances will also influence the hysteresis. |

---

### B4 List of Well-Tried Components

At the present time no list of well-tried components is given. The status of being well-tried is mainly application specific. Components can be stated as being well-tried if they comply with the description given in AS 4024.1501.

A well-tried component for some applications can be inappropriate for other applications.

---

### B5 Fault Lists and Fault Exclusions

#### B5.1 Introduction

The lists given in Tables B3 to B18 express some fault exclusions and their rationale. For further exclusions see Clause 4.3.

The precise instant that the fault occurs can be critical (Clause 8.1).

#### B5.2 Valves

**Table B3 — Directional Control Valves**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Change of switching times | Yes, in the case of positive mechanical action (see Table A2) of the moving components as long as the actuating force is sufficiently large. | — |
| Non-switching (sticking at end/zero position) or incomplete switching (sticking at random intermediate position) | Yes, in the case of positive mechanical action (see Table A2) of the moving components as long as the actuating force is sufficiently large. | — |
| Spontaneous change of initial switching position (without an input signal) | Yes, in the case of positive mechanical action (see Table A2) of the moving components as long as the holding force is sufficiently large, or Yes, if well-tried springs are used (see Table A2) and if normal installation and operating conditions apply (see remark 1), or Yes, in the case of spool valves with elastic sealing and if normal installation and operating conditions apply (see remark 1). | 1) Normal installation and operating conditions apply when: (a) conditions laid down by manufacturer have been observed; (b) conditions laid down by manufacturer have been observed; (c) weight of the moving component is not acting in an unfavourable sense in terms of safety (e.g. horizontal installation); (d) no special inertial forces affect the moving components; and (e) no extreme vibration and shock stresses occur. |
| Leakage | Yes, in the case of spool type valves with elastic seal in so far as a sufficient positive overlap is present (see remark 2) and if normal conditions of operation apply and an adequate treatment and filtration of the compressed air is provided, or Yes, in the case of seat valves if normal conditions of operation apply (see remark 3) and adequate treatment and filtration of the compressed air is provided. | 2) In the case of spool type valves with elastic seals, the effects due to leakage can usually be excluded. However, a small amount of leakage may occur over a long period of time. 3) Normal conditions of operation apply when the conditions laid down by the manufacturer are being observed. |
| Change in the leakage flow rate over a long period of use | None | — |
| Bursting of the valve housing or breakage of the moving component(s) as well as breakage/fracture of mounting or housing screws | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |
| For servo and proportional valves: pneumatic faults which cause uncontrolled behaviour | Yes, in the case of servo and proportional directional valves if these can be assessed, in terms of technical safety, as conventional directional control valves due to their design and construction. | — |

> Note: If the control functions are realized by a number of single function valves, then a fault analysis should be carried out for each valve. The same procedure should be carried out in the case of piloted valves.

**Table B4 — Stop (Shut-Off) Valves/Non-Return (Check) Valves/Quick-Action Venting Valves/Shuttle Valves, Etc.**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Change of switching times | None | — |
| Non-opening, incomplete opening, non-closure or incomplete closure (sticking at end position or at an arbitrary intermediate position) | Yes, if the guidance system for the moving component(s) is designed in a manner similar to that for a non-controlled ball seat valve without a damping system (see remark 1) and if well-tried springs are used (see Table A2). | 1) For a non-controlled ball seat valve without damping system, the guidance system is generally designed in a manner such that any sticking of the moving component is unlikely. |
| Spontaneous change of initial switching position (without an input signal) | Yes, for normal installation and operating conditions (see remark 2) and if there is sufficient closing force on the basis of the pressures and areas provided. | 2) Normal installation and operating conditions are being met when: (a) conditions laid down by manufacturer are being followed; (b) no special inertial forces affect moving components; and (c) no extreme vibration or shock stresses occur. |
| For shuttle valves: simultaneous closing of both input connections | Yes, if on the basis of the construction and design of the moving component, simultaneous closing is unlikely. | — |
| Leakage | Yes, if normal conditions of operation apply (see remark 3) and there is adequate treatment and filtration of the compressed air. | 3) Normal conditions of operation apply when the conditions laid down by the manufacturer are being observed. |
| Change in the leakage flow rate over a long period of use | None | — |
| Bursting of the valve housing or breakage of the moving component(s) as well as breakage/fracture of mounting or housing screws | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |

**Table B5 — Flow Valves**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Change in flow rate without any change in setting device | Yes, for flow control valves without moving parts (see remark 1), e.g. throttle valves, if normal operating conditions apply (see remark 2) and adequate treatment and filtration of the compressed air is provided. | 1) The setting device is not considered to be a moving part. Changes in flow rate due to changes in pressure differences are physically limited in this type of valve. 2) Normal operating conditions apply when the conditions laid down by the manufacturer are being observed. |
| Change in flow rate in the case of non-adjustable, circular orifices and nozzles | Yes, if the diameter is ≥0.8 mm, normal operating conditions apply (see remark 2) and adequate treatment and filtration of the compressed air is provided. | — |
| For proportional flow valves: change in flow rate due to an unintended change in the set value | None | — |
| Spontaneous change in the setting device | Yes, where there is an effective protection of the setting device adapted to the particular case, based upon technical safety specification(s). | — |
| Unintended loosening (unscrewing) of the operating element(s) of the setting device | Yes, if an effective positive locking device against loosening (unscrewing) is provided. | — |
| Bursting of the valve housing or breakage of the moving component(s) as well as the breakage/fracture of the mounting or housing screws | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |

**Table B6 — Pressure Valves**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Non-opening or insufficient opening (spatially and temporarily) when exceeding set pressure (sticking or sluggish movement of moving component) (see remark 1) | Yes, if: (a) the guidance system for the moving component(s) is similar to the case of a non-controlled ball seat valve without a damping system (see remark 2), e.g. a pressure reducing valve with secondary pressure relief; and (b) the installed springs are well tried springs (see Table A2). | 1) This fault applies only when the pressure valve(s) is used for forced actions, e.g. clamping, and for the control of hazardous movement, e.g. suspension of loads. This fault does not apply to its normal function in hydraulic systems, e.g. pressure limitation, pressure decrease. 2) For a non-controlled ball seat valve the guidance system is generally designed in such a manner that any sticking of the moving component is unlikely. |
| Non-closing or insufficient closing (spatially and temporarily) if pressure drops below set value (sticking or sluggish movement of moving component) (see remark 1) | Yes, if the guidance system for the moving component(s) is similar to the case of a non-controlled ball seat valve without a damping device (see remark 2) and if the installed springs are well-tried (see Table A2). | — |
| Change of pressure control behaviour without changing the setting device (see remark 1) | Yes, for directly actuated pressure limiting valves and pressure switching valves if the installed spring(s) are well-tried (see Table A2). | — |
| For proportional pressure valves: change in pressure control behaviour due to unintended change in the set value (see remark 1) | None | — |
| Spontaneous change in the setting device | Yes, where there is an effective protection of the setting device within the requirements of the application, e.g. lead seals. | — |
| Unintended unscrewing of the operating element of the setting device | Yes, if an effective positive locking device against unscrewing is provided. | — |
| Leakage | Yes, for seat valves, membrane valves and spool valves with elastic sealing in normal operating conditions (see remark 3) and if adequate treatment and filtration of the compressed air is provided. | 3) Normal operating conditions are being met when the conditions laid down by the manufacturer are being followed. |
| Change in leakage flow rate over a long period of use | None | — |
| Bursting of the valve housing or breakage of the moving component(s) as well as breakage/fracture of the mounting or housing screws | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |

#### B5.3 Pipework, Hose Assemblies and Connectors

**Table B7 — Pipework**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Bursting and leakage | Yes, if the dimensioning, choice of materials and fixing are in accordance with good engineering practice (see remark 1). | 1) When using plastic pipes, it is necessary to consider the manufacturer's data, in particular with respect to operational environmental influences, e.g. thermal influences, chemical influences, influences due to radiation. When using steel pipes that have not been treated with a corrosion resistant medium, it is particularly important to provide sufficient drying of the compressed air. |
| Failure at the connector (e.g. tearing off, leakage) | Yes, if using bite type fittings or threaded pipes (i.e. steel fittings, steel pipes) and if dimensioning, choice of materials, manufacture, configuration and fixing are in accordance with good engineering practice. | — |
| Clogging (blockage) | Yes, for pipework in the power circuit. Yes, for the control and measurement pipework if the nominal diameter is >2 mm. | — |
| Kinking of the plastic pipes with a small nominal diameter | Yes, if properly protected and installed, taking into account the relevant manufacturer's data, e.g. minimum bending radius. | — |

**Table B8 — Hose Assemblies**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Bursting, tearing off at the fitting attachment and leakage | Yes, if hose assemblies using hoses manufactured to ISO 4079-1 or similar hoses (see remark 1) with the corresponding hose fittings. | 1) Fault exclusion is not considered when: (a) the intended life time is expired; (b) fatigue behaviour of reinforcement can occur; and (c) external damage is unavoidable. |
| Clogging (blockage) | Yes, for hose assemblies in the power circuit. Yes, for the control and measurement hose assemblies if the nominal diameter is ≥2 mm. | — |

**Table B9 — Connectors**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Bursting, breaking of screws or stripping of threads | Yes, if dimensioning, choice of material, manufacture, configuration and connection to the piping and/or to the fluid technology components are in accordance with good engineering practice. | — |
| Leakage (loss of airtightness) | None (see remark 1). | 1) Due to wear, ageing, deterioration of elasticity, etc. it is not possible to exclude faults over a long period. A sudden major failure of the airtightness is not assumed. |
| Clogging (blockage) | Yes, for applications in the power circuit. Yes, in the case of the control and measurement connectors if the nominal diameter is ≥ mm. | — |

#### B5.4 Pressure Transmitters and Pressure Medium Transducers

**Table B10 — Pressure Transmitters and Pressure Medium Transducers**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Loss or change of air/oil-tightness of pressure chambers | None | — |
| Bursting of the pressure chambers as well as fracture of the attachment or cover screws | Yes, if dimensioning, choice of material, configuration and attachment are in accordance with good engineering practice. | — |

#### B5.5 Compressed Air Treatment

**Table B11 — Filters**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Blockage of the filter element | None | — |
| Rupture or partial rupture of the filter element | Yes, if the filter element is sufficiently resistant to pressure. | — |
| Failure of the dirt indicator or dirt monitor | None | — |
| Bursting of the filter housing or fracture of the cover or connecting elements | Yes, if dimensioning, choice of material, arrangement in the system and fixing are in accordance with good engineering practice. | — |

**Table B12 — Oilers**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Change in the set value (oil volume per unit time) without change to the setting device | None | — |
| Spontaneous change in the setting device | Yes, if effective protection of the setting device is provided, adapted to the particular case. | — |
| Unintended unscrewing of the operating element of the setting device | Yes, if an effective positive locking device against unscrewing is provided. | — |
| Bursting of the housing or fracture of the cover, fixing or connecting elements | Yes, if the dimensioning, choice of materials, arrangement in the system and fixing are in accordance with good engineering practice. | — |

**Table B13 — Silencer**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Blockage (clogging) of the silencer | Yes, if the design and construction of the silencer element fulfils remark 1. | 1) Clogging of the silencer element and/or an increase in the exhaust air back pressure above a certain critical value is unlikely if the silencer has a suitably large diameter and is designed to meet the operating conditions. |

#### B5.6 Accumulators and Pressure Vessels

**Table B14 — Accumulators and Pressure Vessels**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Fracture/bursting of the accumulator/pressure vessel or connectors or stripping of the threads of the fixing screws | Yes, if construction, choice of equipment, choice of materials and arrangement in the system are in accordance with good engineering practice. | — |

#### B5.7 Sensors

**Table B15 — Sensors**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Faulty sensor (see remark 1) | None | 1) Sensors in this table include signal capture, processing and output in particular for pressure, flow rate, temperature, etc. |
| Change of the detection or output characteristics | None | — |

#### B5.8 Information Processing

**Table B16 — Logical Elements**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Faulty logical element (e.g. AND element, OR element, Logic-storage-element) due to, e.g. change in the switching time, failure to switch or incomplete switching | For corresponding fault assumptions and fault exclusions see Tables B3, B4 and B5. | — |

**Table B17 — Time Delay Services**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Faulty time delay device, e.g. pneumatic and pneumatic/mechanical time and counting elements | Yes, for time delay devices without moving components, e.g. fixed resistance, if normal operating conditions (see remark 1) apply and adequate treatment and filtration of the compressed air is provided. | 1) Normal operating conditions are being met when the conditions laid down by the manufacturer are being followed. |
| Change of detection or output characteristics | Yes, for time delay devices without moving components (see remark 1). | — |
| Bursting of the housing or fracture of the cover or fixing elements | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |

**Table B18 — Converters**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Faulty converter (see remark 1) | Yes, for converters without moving components, e.g. reflex nozzle, if normal operating conditions apply (see remark 2) and adequate treatment and filtration of the compressed air is provided. | 1) This covers for example the conversion of a pneumatic signal into an electrical one, the position detection (cylinder switch, reflex nozzle), the amplification of pneumatic signals. 2) Normal operating conditions are being met when the conditions laid down by the manufacturer are being followed. |
| Change of the detection or output characteristics | Yes, for converters without moving components (see remark 2). | — |
| Bursting of the housing or fracture of the cover or fixing elements | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |

---

## Appendix C — Validation Tools for Hydraulic Systems (Informative)

### C1 Introduction

When hydraulic systems are used in conjunction with other technologies, then relevant tables for basic safety and well-tried safety principles should also be taken into account. Where hydraulic components are electrically connected/controlled the appropriate fault lists in Appendix D should be considered.

> Note: Requirements of specific Standards could apply such as pressure equipment.
> Note: Air bubbles and cavitation in the hydraulic fluid should be avoided because they can create additional hazards, e.g. unintended movements.

---

### C2 List of Basic Safety Principles

**Table C1 — Basic Safety Principles (Hydraulic)**

| Basic safety principle | Remarks |
|---|---|
| Use of suitable materials and adequate manufacturing | Selection of material, manufacturing methods and treatment in relation to for example stress, durability, elasticity, friction, wear, corrosion, temperature, hydraulic fluid. |
| Correct dimensioning and shaping | Consider for example stress, strain, fatigue, surface roughness, tolerances, manufacturing. |
| Proper selection, combination, arrangements, assembly and installation of components/system | Apply manufacturer's application notes, e.g. catalogue sheets, installation instructions, specifications, and use of good engineering practice in similar components/systems. |
| Use of de-energisation principle | The safe state is obtained by release of energy to all relevant devices. See primary action for stopping in AS 4024.1202. Energy is supplied for starting the movement of a mechanism. See primary action for starting in AS 4024.1202. Consider different modes, e.g. operation mode, maintenance mode. This principle should not be used in some applications, e.g. where the loss of hydraulic pressure will create an additional hazard. |
| Proper fastening | For the application of for example screw locking, fittings, gluing, clamp ring, consider manufacturer's application notes. Overloading can be avoided by applying adequate torque loading technology. |
| Pressure limitation | Examples are pressure relief valve, pressure reducing/control valve. |
| Speed limitation/speed reduction | An example is the speed limitation of a piston by a flow valve or a throttle. |
| Sufficient avoidance of contamination of the fluid | Consider filtration/separation of solid particles/water in the fluid. Consider also an indication of the need for filter-service. |
| Proper range of switching time | Consider for example the length of pipework, pressure, evacuation relief capacity, spring tiredness, friction, lubrication, temperature/viscosity, inertia during acceleration and deceleration, combination of tolerances. |
| Withstanding environmental conditions | Design the equipment so that it is capable of working in all expected environments and in any foreseeable adverse conditions, e.g. temperature, humidity, vibration, pollution. See Clause 9 and consider manufacturer's specification and application notes. |
| Protection against unexpected start-up | Consider unexpected start-up caused by stored energy and after power supply restoration for different modes, e.g. operation mode, maintenance mode. Special equipment for release of stored energy may be necessary. Special applications, (e.g. keep energy for clamping devices or ensure a position) need to be considered separately. |
| Simplification | Reduce the number of components in the safety-related system. |
| Proper temperature range | To be considered throughout the whole system. |
| Separation | Separation of safety-related functions from other functions. |

---

### C3 List of Well-Tried Safety Principles

**Table C2 — Well-Tried Safety Principles (Hydraulic)**

| Well-tried safety principle | Remarks |
|---|---|
| Over-dimensioning/safety factor | The safety factor is given in standards or by good experience in safety-related applications. |
| Safe position | The moving part of the component is held in one of the possible positions by mechanical means (friction only is not enough). Force is needed to change the position. |
| Increased OFF force | One solution can be that the area ratio for moving a valve spool to the safe position (OFF position) is significantly larger than for moving the spool to ON position (a safety factor). |
| Valve closed by load pressure | Examples are seat and cartridge valves. Consider how to apply the load pressure in order to keep the valve closed even if, e.g. the spring closing the valve breaks. |
| Positive mechanical action | The positive mechanical action is used for moving parts inside hydraulic components, see also Table A2. |
| Multiple parts | See Table A2. |
| Use of well-tried spring | See Table A2. |
| Speed limitation/speed reduction by resistance to defined flow | Examples are fixed orifice, fixed throttle. |
| Force limitation/force reduction | This can be achieved by a well-tried pressure relief valve which is, e.g. equipped with a well-tried spring, correctly dimensioned and selected. |
| Appropriate range of working conditions | The limitation of working conditions, e.g. pressure range, flow rate and temperature range should be considered. |
| Monitoring of the condition of the fluid | Consider high degree of filtration/separation of solid particles/water in the fluid. Consider also the chemical/physical conditions of the fluid. Consider an indication of the need of filter-service. |
| Sufficient positive overlapping in piston valves | The positive overlapping ensures the stopping function and prevents unallowed movements. |
| Limited hysteresis | For example increased friction will increase the hysteresis. Combination of tolerances will also influence the hysteresis. |

---

### C4 List of Well-Tried Components

At the time no list of well-tried components is given. The status of being well-tried is mainly application specific. Components can be stated as being well-tried if they comply with the description given in AS 4024.1501.

A well-tried component for some applications can be inappropriate for other applications.

---

### C5 Fault Lists and Fault Exclusions

#### C5.1 Introduction

The lists express some fault exclusions and their rationale. For further exclusions see Clause 4.3.

The precise instant that the fault occurs can be critical (see Clause 8.1).

#### C5.2 Valves

**Table C3 — Directional Control Valves (Hydraulic)**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Change of switching times | Yes, in the case of positive mechanical action (see Table A2) of the moving components as long as the actuating force is sufficiently large, or Yes, in respect of the non-opening of a special type of cartridge seat valve, when used with at least one other valve, to control the main flow of the fluid (see remark 1). | 1) Special type of cartridge seat valve is achieved if: (a) the active area for initiating the safety-related switching movement is at least 90% of the total area of the moving component (poppet); (b) the effective control pressure on the active area can be increased up to the maximum operating pressure; (c) the effective control pressure on the area opposite to the active area of the moving component is vented to a very low value compared with the maximum operating pressure; (d) the moving component (poppet) is provided with peripheral balancing grooves; and (e) the pilot valve(s) to this seat valve is designed together in a manifold block without hose assemblies and pipes for the connection of these valves. |
| Non-switching (sticking at end/zero position) or incomplete switching | Yes, in the case of positive mechanical action (see Table A2) of the moving components as long as the actuating force is sufficiently large, or Yes, in respect of the non-opening of a special type of cartridge seat valve, when used with at least one other valve (see remark 1). | — |
| Spontaneous change of initial switching position (without an input signal) | Yes, in the case of positive mechanical action (see Table A2) of the moving components as long as the holding force is sufficiently large, or Yes, if well-tried springs are used (see Table A2) and if normal installation and operating conditions apply (see remark 2), or Yes, in respect of the non-opening of a special type of cartridge seat valve, when used with at least one other valve to control the main flow of the fluid (see remark 1) and if normal installation and operating conditions apply (see remark 2). | 2) Normal installation and operating conditions apply when: (a) conditions laid down by manufacturer are being observed; (b) weight of moving component is not acting in an unfavourable sense in terms of safety, e.g. horizontal installation; (c) no special inertial forces affect the moving components; and (d) no extreme vibration and shock stresses occur. |
| Leakage | Yes, in the case of seat valves, if normal installation and operating conditions apply (see remark 3) and an adequate filtration system is provided. | 3) Normal conditions of operation apply when the conditions laid down by manufacturer are being observed. |
| Change in the leakage flow rate over a long period of use | None | — |
| Bursting of the valve housing or breakage of the moving component(s) as well as breakage/fracture of the mounting or housing screws | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |
| For servo and proportional valves: hydraulic faults which cause uncontrolled behaviour | Yes, in the case of servo and proportional directional valves if these can be assessed, in terms of safety, as conventional directional control valves due to their design and construction. | — |

> Note: If the control functions are realized by a number of single function valves, then a fault analysis should be carried out for each valve. The same procedure should be carried out in the case of piloted valves.

**Table C4 — Stop (Shut-Off) Valves/Non-Return (Check) Valves/Shuttle Valves, Etc. (Hydraulic)**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Change of switching times | None | — |
| Non-opening, incomplete opening, non-closure or incomplete closure (sticking at end position or at an arbitrary intermediate position) | Yes, if the guidance system for the moving component(s) is designed in a manner similar to that for a non-controlled ball seat valve without a damping system (see remark 1) and if well-tried springs are used (see Table A2). | 1) For a non-controlled ball seat valve without damping system, the guidance system is generally designed in a manner such that any sticking of the moving component is unlikely. |
| Spontaneous change of initial switching position (without an input signal) | Yes, for normal installation and operating conditions (see remark 2) and if there is sufficient closing force on the basis of the pressures and areas provided. | 2) Normal installation and operating conditions are being met when: (a) conditions laid down by manufacturer are being followed; (b) no special inertial forces affect the moving components; and (c) no extreme vibration or shock stresses occur. |
| For shuttle valves: simultaneous closing of both input connections | Yes, if on the basis of the construction and design of the moving component, simultaneous closing is unlikely. | — |
| Leakage | Yes, if normal conditions of operation apply (see remark 3) and an adequate filtration system is provided. | 3) Normal conditions of operation apply when the conditions laid down by manufacturer are being observed. |
| Change in the leakage flow rate over a long period of use | None | — |
| Bursting of the valve housing or breakage of the moving component(s) as well as breakage/fracture of the mounting or housing screws | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |

**Table C5 — Flow Valves (Hydraulic)**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Change in the flow rate without change in the setting device | Yes, in the case of flow valves without moving parts (see remark 1), e.g. throttle valves, if normal operating conditions apply (see remark 2) and an adequate filtration system is provided (see remark 3). | 1) The setting device is not considered to be a moving part. Changes in flow rate due to changes in the pressure differences and viscosity are physically limited in this type of valve. 2) Normal operating conditions are being met when the conditions laid down by the manufacturer are being observed. 3) Where a non-return valve is integrated into the flow valve, then in addition, the fault assumptions for non-return valves have to be observed. |
| Change in the flow rate in the case of non-adjustable, circular orifices and nozzles | Yes, if the diameter is ≥ 0.8 mm, normal operating conditions apply (see remark 2) and an adequate filtration system is provided. | — |
| For proportional flow valves: change in the flow rate due to an unintended change in the set value | None | — |
| Spontaneous change in the setting device | Yes, where there is an effective protection of the setting device adapted to the particular case, based upon technical safety specifications. | — |
| Unintended loosening (unscrewing) of the operating element(s) of the setting device | Yes, if an effective positive locking device against loosening (unscrewing) is provided. | — |
| Bursting of the valve housing or breakage of the moving component(s) as well as the breakage/fracture of the mounting or housing screws | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |

**Table C6 — Pressure Valves (Hydraulic)**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Non-opening or insufficient opening (spatially and temporarily) when exceeding the set pressure (sticking or sluggish movement of the moving component) (see remark 1) | Yes, in respect of the non-opening of a special type of cartridge seat valve, when used with at least one other valve, to control the main flow of the fluid (see remark 1 of Table C3), or Yes, if the guidance system for the moving component(s) is similar to the case of a non-controlled ball seat valve without a damping device (see remark 2) and if the installed springs are well-tried (see Table A2). | 1) This fault applies only when the pressure valve(s) is used for forced actions, e.g. clamping, and for the control of hazardous movement, e.g. suspension of loads. This fault does not apply to its normal function in hydraulic systems, e.g. pressure limitation, pressure decrease. 2) For a non-controlled ball seat valve without a damping device the guidance system is generally designed in such a manner that any sticking of the moving component is unlikely. |
| Non-closing or insufficient closing (spatially and temporarily) if pressure drops below the set value (sticking or sluggish movement of the moving component) (see remark 1) | Yes, if the guidance system for the moving component(s) is similar to the case of a non-controlled ball seat valve without a damping device (see remark 2) and if the installed springs are well-tried (see Table A2). | — |
| Change of the pressure control behaviour without changing the setting device (see remark 1) | Yes, for directly actuated pressure relief valves, if the installed spring(s) are well-tried (see Table A2). | — |
| For proportional pressure valves: change in pressure control behaviour due to unintended change in the set value (see remark 1) | None | — |
| Spontaneous change in the setting device | Yes, where there is an effective protection of the setting device adapted to the particular case in relation to technical safety specifications, e.g. lead seals. | — |
| Unintended unscrewing of the operating element of the setting device | Yes, if an effective positive locking device against unscrewing is provided. | — |
| Leakage | Yes, for seat valves if normal conditions of operation apply (see remark 3) and if an adequate filtration system is provided. | 3) Normal conditions of operation apply when the conditions laid down by the manufacturer are being followed. |
| Change of the leakage flow rate over a long period of use | None | — |
| Bursting of the valve housing or breakage of the moving component(s) as well as breakage/fracture of the mounting or housing screws | Yes, if construction, dimensioning and installation are in accordance with good engineering practice. | — |

#### C5.3 Metal Pipework, Hose Assemblies and Connectors

**Table C7 — Metal Pipework**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Bursting and leakage | Yes, if the dimensioning, choice of materials and fixing are in accordance with good engineering practice. | — |
| Failure at the connector (e.g. tearing off, leakage) | Yes, if using welded fittings or welded flanges or flared fittings and if dimensioning, choice of materials, manufacture, configuration and fixing are in accordance with good engineering practice. | — |
| Clogging (blockage) | Yes, for pipework in the power circuit. Yes, for the control and measurement pipework if the nominal diameter is ≥3 mm. | — |

**Table C8 — Hose Assemblies (Hydraulic)**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Bursting, tearing off at the fitting attachment and leakage | None | — |
| Clogging (blockage) | Yes, for hose assemblies in the power circuit. Yes, for the control and measurement hose assemblies if the nominal diameter is ≥3 mm. | — |

**Table C9 — Connectors (Hydraulic)**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Bursting, breaking of screws or stripping of threads | Yes, if dimensioning, choice of material, manufacture, configuration and connection to the piping and/or to the fluid technology component are in accordance with good engineering practice. | — |
| Leakage (loss of leak-tightness) | None (see remark 1). | 1) Due to wear, ageing, deterioration of elasticity, etc. it is not possible to exclude faults over a long period. A sudden major failure of the leaktightness is not assumed. |
| Clogging (blockage) | Yes, for applications in the power circuit. Yes, in the case of the control and measurement connectors if the nominal diameter is ≥3 mm. | — |

#### C5.4 Filters

**Table C10 — Filters (Hydraulic)**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Blockage of the filter element | None | — |
| Rupture of the filter element | Yes, if the filter element is sufficiently resistant to pressure and an effective bypass valve or an effective monitoring of dirt is provided. | — |
| Failure of the bypass valve | Yes, if the guidance system of the bypass valve is designed in a manner similar to that for a non-controlled ball seat valve without a damping device (see Table C4) and if well-tried springs are used (see Table A2). | — |
| Failure of the dirt indicator or dirt monitor | None | — |
| Bursting of the filter housing or fracture of the cover or connecting elements | Yes, if dimensioning, choice of material, arrangement in the system and fixing are in accordance with good engineering practice. | — |

#### C5.5 Energy Storage

**Table C11 — Energy Storage**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Fracture/bursting of the energy storage vessel or connectors or cover screws as well as stripping of the screw threads | Yes, if construction, choice of equipment, choice of materials and arrangement in the system are in accordance with good engineering practice. | — |
| Leakage at the separating element between the gas and the operating fluid | None | — |
| Failure/breakage of the separating element between the gas and the operating fluid | Yes, in the case of cylinder/piston storage (see remark 1). | 1) A sudden major leakage is not to be considered. |
| Failure of the filling valve on the gas side | Yes, if the filling valve is installed in accordance with good engineering practice and if adequate protection against external influences is provided. | — |

#### C5.6 Sensors

**Table C12 — Sensors (Hydraulic)**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Faulty sensor (see remark 1) | None | 1) Sensors in this table include signal capture, processing and output, in particular for pressure, flow rate, temperature, etc. |
| Change of the detection or output characteristics | None | — |

---

## Appendix D — Validation Tools for Electrical Systems (Informative)

### D1 Introduction

When electrical systems are used in conjunction with other technologies, then relevant tables for basic safety and well-tried safety principles should also be taken into account.

> Notes:
> 1. Electronic components cannot be considered as well-tried.
> 2. The environmental conditions of AS 60204.1 do not apply to the validation process if other environmental conditions are specified.

---

### D2 List of Basic Safety Principles

**Table D1 — Basic Safety Principles (Electrical)**

| Basic safety principle | Remarks |
|---|---|
| Use of suitable materials and adequate manufacturing | Selection of material, manufacturing methods and treatment in relation to for example stress, durability, elasticity, friction, wear, corrosion, temperature, conductivity, dielectric rigidity. |
| Correct dimensioning and shaping | Consider for example stress, strain, fatigue, surface roughness, tolerances, manufacturing. |
| Proper selection, combination, arrangements, assembly and installation of components/system | Apply manufacturer's application notes, e.g. catalogue sheets, installation instructions, specifications, and use of good engineering practice. |
| Correct protective bonding | One side of the control circuit, one terminal of the operating coil of each electromagnetic operated device or one terminal of other electrical device is connected to the protective bonding circuit see IEC 60204-1. |
| Insulation monitoring | Use of isolation monitoring device which either indicates an earth fault or interrupts the circuit automatically after an earth fault IEC 60204-1. |
| Use of de-energization principle | A safe state is obtained by de-energizing all relevant devices, e.g. by using of normally closed (NC) contact for inputs (push-buttons and position switches) and normally open (NO) contact for relays AS 4024.1202. Exceptions may exist in some applications, e.g. where the loss of electrical supply will create an additional hazard. Time delay functions may be necessary to achieve a system safe state AS 60204.1. |
| Transient suppression | Use of a suppression device (RC, diode, varistor) parallel to the load, but not parallel to the contacts. |
| Reduction of response time | Minimise delay in de-energizing of switching components. |
| Compatibility | Use components compatible with the voltages and currents used. |
| Withstanding environmental conditions | Design the equipment so that it is capable of working in all expected environments and in any foreseeable adverse conditions, e.g. temperature, humidity, vibration and electromagnetic interference (EMI) (see Clause 9). |
| Secure fixing of input devices | Secure input devices, e.g. interlocking switches, position switches, limit switches, proximity switches, so that position, alignment and switching tolerance is maintained under all expected conditions, e.g. vibration, normal wear, ingress of foreign bodies, temperature. See AS 4024.1602. |
| Protection against unexpected start-up | Prevent unexpected start-up, e.g. after power supply restoration see AS 4024.1202, AS 4024.1603, AS 60204.1. |
| Protection of the control circuit | The control circuit should be protected in accordance with AS 60204.1. |
| Sequential switching for circuit of serial contacts of redundant signals | To avoid the common mode failure of the welding of both contacts, the switching on and off does not happen simultaneously, so that one contact always switches without current. |

---

### D3 List of Well-Tried Safety Principles

**Table D2 — Well-Tried Safety Principles (Electrical)**

| Well-tried safety principle | Remarks |
|---|---|
| Positive mechanically linked contacts | Use of positively mechanically linked contacts for, e.g. monitoring function AS 4024.1202. |
| Fault avoidance in cables | To avoid short circuit between two adjacent conductors: (a) use cable with shield connected to the protective bonding circuit on each separate conductor; or (b) in flat cables, use of one earthed conductor between each signal conductors. |
| Separation distance | Use of sufficient distance between position terminals, components and wiring to avoid unintended connections. |
| Energy limitation | Use of a capacitor for supplying a finite amount of energy, e.g. in timer application. |
| Limitation of electrical parameters | Limitation in voltage, current, energy or frequency resulting, e.g. in torque limitation, hold-to-run with displacement/time limited, reduced speed, to avoid leading to an unsafe state. |
| No undefined states | Avoid undefined states in the control system. Design and construct the control system so that during normal operation and all expected operating conditions its state, e.g. its output(s) can be predicted. |
| Positive mode actuation | Direct action is transmitted by the shape (and not by the strength) with no elastic elements, e.g. spring between actuator and the contacts see AS 4024.1602. |
| Failure mode orientation | Wherever possible, the device/circuit should fail to the safe state or condition. |
| Oriented failure mode | Oriented failure mode components or systems should be used wherever practicable. |
| Over-dimensioning | Derate components when used in safety circuits, for example by: (a) current passed through switched contacts should be less than half their rated current; (b) the switching frequency of components should be less than half their rated value; and (c) total number of expected switching operation shall be ten times less than the device's electrical durability. Note: Derating can depend on the design rationale. |
| Minimize possibility of faults | Separate safety-related functions from the other functions. |
| Balance complexity/simplicity | Balance should be made between: (a) complexity to reach a better control; and (b) simplify to have a better reliability. |

---

### D4 List of Well-Tried Components

The components listed in Table D3 are considered to be well-tried if they comply with the description given in AS 4024.1501. The standards listed in this table can demonstrate their suitability and reliability for a particular application.

A well-tried component for some applications can be inappropriate for other applications.

**Table D3 — Well-Tried Components (Electrical)**

| Well-tried component | Additional conditions for 'well-tried' | Standard or specification |
|---|---|---|
| Switch with positive mode actuation (direct opening action), e.g. push-button, position switch, cam operated selector switch for mode operation | — | AS 60947.5.1 |
| Emergency stop device | — | AS 4024.1604 |
| Fuse | — | AS 60269.1 |
| Circuit breaker | — | AS 60947.2 |
| Differential circuit breaker/RCD (Residual current detection) | — | AS 60947.2 |
| Main contactor | Only well-tried if: (a) other influences are taken into account, e.g. vibration; (b) failure avoided by appropriate methods, e.g. over-dimensioning (see Table D2); (c) the current to the load is limited by thermal protection device; and (d) the circuits are protected by a protection device against the overloads. | AS 60947.4.1 |
| Control and protective switching device or equipment (CPS) | — | AS 60947.6.2 |
| Auxiliary contactor (e.g. contactor relay) | Only well-tried if: (a) other influences are taken into account, e.g. vibration; (b) positively energized action; (c) failure avoided by appropriate methods, e.g. over-dimensioning (see Table D2); (d) the current in the contacts is limited by fuse or circuit-breaker to avoid the welding of the contacts; and (e) contacts are positively mechanically guided when used for monitoring. | AS 60204.1, AS 60947.5.1 |
| Transformer | — | — |
| Cable | Cabling external to enclosure should be protected against mechanical damage (including e.g. vibration or bending). | AS 60204.1 |
| Plug and socket | — | According to an electrical standard relevant for the intended application. For interlocking, see also AS 4024.1602. |
| Temperature switch | — | For electrical side see AS 60947.5-1. |
| Pressure switch | — | For electrical side see AS 60947.5.1. For pressure side see Appendices B and C. |
| Solenoid for valve | — | — |

---

### D5 Fault Lists and Fault Exclusions

#### D5.1 Introduction

The lists express some fault exclusions and their rationale. For further exclusions see Clause 4.3.

For validation both permanent faults and transient disturbances should be considered.

The precise instant that the fault occurs can be critical (see Clause 7.1).

The harshness of the environment in which safety related parts of the control system are expected to function should be taken into account to ensure that fault exclusions for less harsh environments are not applicable. Harsh operating environments include mining and pharmaceutical industries.

#### D5.2 Conductors and Connectors

**Table D4 — Conductors/Cables**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Short-circuit between any two conductors | Short-circuits between conductors which are: permanently connected (fixed) and protected against external damage, e.g. by cable ducting, armouring, or separate multicore cables, or within an electrical enclosure (see remark 1), or individually shielded with earth connection. | 1) Provided both the conductors and enclosure meet the appropriate requirements (see AS 60204.1). |
| Short-circuit of any conductor to an exposed conductive part or to earth or to the protective bonding conductor | Short circuits between conductor and any exposed conductive part within an electrical enclosure (see remark 1). | — |
| Open-circuit of any conductor | None | — |

**Table D5 — Printed Circuit Boards/Assemblies**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Short-circuit between two adjacent tracks/pads | Short-circuits between adjacent conductors in accordance with remarks 1) to 3). | 1) The creepage distances and clearances are dimensioned at least to IEC 60664-1 with at least pollution degree 2/installation category III. 2) The printed side(s) of the assembled board is covered with an ageing-resistant varnish or a protective layer covering all conductor paths. 3) All enclosures of the safety-related parts of the control system, including those mounted remotely, should provide a degree of protection of at least IP 54 (see AS 60529), when mounted as specified. |
| Open-circuit of any track | None | — |

**Table D6 — Terminal Block**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Short-circuit between adjacent terminals | Short-circuit between adjacent terminals. | The design by itself ensures that short circuit is avoided, e.g. by shaping shrink down plastic tubing over connection point. |
| Open-circuit of individual terminals | None | — |

**Table D7 — Multi-Pin Connector**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Short-circuit between any two adjacent pins | Short-circuit between adjacent pins in accordance with remarks 1) and 2). | 1) By using ferrules or other suitable means for multi-stranded wires. Creepage distances and clearances and all gaps should be dimensioned to at least IEC 60664-1:1992 with installation category III. 2) The assembled board should be mounted in an enclosure of at least IP 54 (see AS 60529) and the printed side(s) of the assembled board is covered with an ageing-resistant varnish or a protective layer covering all conductor paths. |
| Interchanged or incorrectly inserted connector when not prevented by mechanical means | None | — |
| Short-circuit of any conductor (see remark 3) to earth or a conductive part or to the protective conductor | None | 3) The core of the cable is considered as a part of the multi-pin connector. |
| Open-circuit of individual connector pins | None | — |

#### D5.3 Switches

**Table D8 — Electromechanical Position Switch, Manually Operated Switch**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Contact will not close | None | — |
| Contact will not open | Contacts in accordance with AS 60947.5.1 annex K are expected to open. | — |
| Short-circuit between adjacent contacts insulated from each other | Short-circuit can be excluded for switches in accordance with AS 60947.5.1 (see remark 1). | 1) Conductive parts which become loose should not be able to bridge the insulation between contacts. |
| Simultaneous short-circuit between three terminals of change-over contacts | Simultaneous short-circuit can be excluded for switches in accordance with AS 60947.5.1. | — |

> Notes:
> 1. The fault lists for the mechanical aspects are considered in Appendix A.
> 2. Examples include push-button, reset actuator, DIP switch, magnetically operated contacts, reed switch, pressure switch, temperature switch.

**Table D9 — Electromechanical Devices**

| Fault considered | Exclusion | Remarks |
|---|---|---|
| All contacts remain in the energized position when the coil is de-energized (e.g. due to mechanical fault) | None | — |
| All contacts remain in the de-energized position when power is applied (e.g. due to mechanical fault, open circuit of coil) | None | — |
| Contact will not open | None | — |
| Contact will not close | None | — |
| Simultaneous short-circuit between the three terminals of a change-over contact | Simultaneous short-circuit can be excluded if remarks 1) and 2) are fulfilled. | 1) The creepage and clearance distances are dimensioned to at least IEC 60664-1 with at least pollution degree. 2) Installation category III. Conductive parts which become loose cannot bridge the insulation between contacts and the coil. |
| Short-circuit between two pairs of contacts and/or between contacts and coil terminal | Short-circuit can be excluded if remarks 1) and 2) are fulfilled. | — |
| Simultaneous closing of normally open and normally closed contacts | Simultaneous closing of contacts can be excluded if remark 3) is fulfilled. | 3) Positively driven (or mechanically linked) contacts are used. |

> Note: Examples include relay, contactor relays.

**Table D10 — Proximity Switches**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Permanently low resistance at output | None (see remark 1). | 1) See IEC 60947-5-3. |
| Permanently high resistance at output | None (see remark 2). | 2) Fault prevention measures should be described. |
| Interruption in power supply | None | — |
| No operation of switch due to mechanical failure | No operation due to mechanical failure when remark 3) is fulfilled. | 3) All parts of the switch should be sufficiently well fixed. For mechanical aspects see Appendix A. |
| Short-circuit between the three connections of a change-over switch | None | — |

**Table D11 — Solenoid Valves**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Does not energize | None | — |
| Does not de-energize | None | — |

> Note: The fault lists for the mechanical aspects of pneumatic and hydraulic valves are considered in Appendices B and C respectively.

#### D5.4 Discrete Electrical Components

**Table D12 — Transformers**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Open circuit of individual winding | None | — |
| Short-circuit between different windings | Short-circuit between different windings can be excluded if remark 1) is fulfilled. | 1) The requirements of IEC 61558 should be met. Additionally for rated voltages below 500 V the insulation should meet the requirements for a 2500 V a.c. test voltage. Short-circuits in coils and windings need to be avoided by taking appropriate steps, e.g. by: (a) impregnating the coils so as to fill all the cavities between individual coils and the body of the coil and the core; and (b) using winding conductors well within their insulation and high temperature ratings. 2) In the event of a secondary short-circuit heating above a specified operating temperature should not occur. |
| Short-circuit in one winding | Short-circuit in one winding can be excluded if remark 1) is fulfilled. See also the guidance in remark 2). | — |
| Change in effective turns ratio | Change in effective turns ratio can be excluded if remark 1) is fulfilled. See also the guidance in remark 2). | — |

**Table D13 — Inductances**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Open-circuit | None | — |
| Short-circuit | Short-circuit can be excluded if remark 1) is fulfilled. | 1) Coil is single layered, enameled or potted and with axial wire connections and axial mounted. |
| Random change of value (0.5 L_N ≤ L < L_N + tolerance where L_N is the nominal value of inductance) (see remark 2). | None | 2) Depending upon the type of construction other ranges can be considered. |

**Table D14 — Resistors**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Open-circuit | None | — |
| Short-circuit | Short-circuit can be excluded if remark 1) is fulfilled. No exclusions for resistors used in surface-mounting technology. | The resistor is of the film type, or wirewound type with protection to prevent unwinding of wire in the event of breakage, with axial wire connections, axial mounted and varnished. |
| Random change of value (0.5 R_N < R < 2 R_N where R_N is the nominal value of resistance) (see remark 2). | None | 2) Depending upon the type of construction other ranges can be considered. |

**Table D15 — Resistor Networks**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Open-circuit | None | — |
| Short-circuit between any two connections | None | — |
| Short-circuit between any connections | None | — |
| Random change of value (0.5 R_N < R < 2 R_N where R_N is the nominal value of resistance) (see remark 1). | None | 1) Depending upon the type of construction other ranges can be considered. |

**Table D16 — Potentiometers**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Open-circuit of individual connection | None | — |
| Short-circuit between all connections | None | — |
| Short-circuit between any two connections | None | — |
| Random change of value (0.5 R_N < R < 2 R_N where R_N = nominal value of resistance) (see remark 1). | None | 1) Depending upon the type of construction other ranges can be considered. |

**Table D17 — Capacitors**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Open-circuit | None | — |
| Short-circuit | None | — |
| Random change of value (0.5 C_N < C < C_N + tolerance where C_N = nominal value of capacity) (see remark 1). | None | 1) Depending upon the type of construction other ranges can be considered. |
| Changing value tan δ | None | — |

#### D5.5 Electronic Components

**Table D18 — Discrete Semi Conductors**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Open-circuit of any connection | None | — |
| Short-circuit between any two connections | None | — |
| Short-circuit between all connections | None | — |
| Change in characteristics | None | — |

> Note: Examples include diodes, Zener diodes, transistors, triacs, voltage regulators, quartz crystal, phototransistors, light-emitting diodes (LEDS).

**Table D19 — Optocouplers**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Open-circuit of individual connection | None | — |
| Short-circuit between any two input connections | None | — |
| Short-circuit between any two output connections | None | — |
| Short-circuit between any two connections of input and output | Short-circuit between input and output can be excluded if remark 1) is fulfilled. | 1) The creepage distances and clearances should be dimensioned at least to IEC 60664-1 with at least pollution degree 2/installation category III. |

**Table D20 — Non-Programmable Integrated Circuits**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Open-circuit of each individual connection | None | — |
| Short-circuit between any two connections | None | — |
| Stuck-at-fault (i.e. short-circuit to 1 and 0 with isolated input or disconnected output). Static '0' and '1' signal at all inputs and outputs, either individually or simultaneously | None | — |
| Parasitic oscillation of outputs | None | — |
| Changing values (e.g. input/output voltage of analogue devices) | None | — |

> Note: In this Standard, ICs with less than 1000 gates and/or less than 24 pins, operational amplifiers, shift registers and hybrid modules are considered to be non-complex. This definition is arbitrary.

**Table D21 — Programmable and/or Complex Integrated Circuits**

| Fault considered | Fault exclusion | Remarks |
|---|---|---|
| Faults in all or part of the function including software faults | None | — |
| Open-circuit of each individual connection | None | — |
| Short-circuit between any two connections | None | — |
| Stuck-at-fault (i.e. short-circuit to 1 and 0 with isolated input or disconnected output). Static '0' and '1' signal at all inputs and outputs, either individually or simultaneously | None | — |
| Parasitic oscillation of outputs | None | — |
| Changing value, e.g. input/output voltage of analogue devices | None | — |
| Undetected faults in the hardware which go unnoticed because of the complexity of integrated circuit | None | — |

> Note: In this Standard, an IC is considered to be complex if it consists of more than 1000 gates and/or more than 24 pins. This definition is arbitrary. The analysis should identify additional faults which should be considered if they influence the operation of the safety function.

---

*End of AS 4024.1502*