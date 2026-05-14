# AS 4024.1501
## Safety of Machinery — Design of Safety-Related Parts of Control Systems: General Principles for Design

---

## 1. Scope

This Standard provides safety requirements and guidance on the principles for designing safety-related parts of control systems (SRP/CS). It specifies categories and describes the characteristics of their safety functions, including programmable systems, for all machinery and related protective devices.

Applies to:
- All safety-related parts of control systems regardless of energy type (electrical, hydraulic, pneumatic, mechanical)
- All machinery applications — professional and non-professional use
- Safety-related parts of control systems used in other technical applications (where appropriate)

> This Standard does not specify which safety functions or categories are to be used in a particular case.

---

## 2. Objective

Enable designers, manufacturers, suppliers, employers, and users of machinery to minimise risks to health and safety by providing technical principles for the design of safety-related parts of control systems.

---

## 3. Referenced Documents

| Standard | Title |
|---|---|
| AS 4024 | Safety of machinery |
| AS 4024.1201 | General principles — Basic terminology and methodology |
| AS 4024.1202 | General principles — Technical principles |
| AS 4024.1301 | Risk assessment — Principles for risk assessment |
| AS 4024.1401 | Ergonomic principles — Design principles — Terminology and general principles |
| AS 4024.1502 | Design of safety-related parts of control systems — Validation |
| AS 4024.1901 | Displays, controls, actuators and signals — General principles for human interactions |
| AS 4024.1902 | Displays, controls, actuators and signals — Displays |
| AS 4024.1903 | Displays, controls, actuators and signals — Control actuators |
| AS 60204 | Safety of machinery — Electrical equipment of machines |
| AS 60204.1 | Part 1: General requirements (IEC 60204-1, Ed.5 FDIS MOD) |
| AS 60529 | Degrees of protection provided by enclosures (IP code) |
| AS 61508 | Functional safety of electrical/electronic/programmable electronic safety-related systems |
| AS/NZS 61000 | Electromagnetic compatibility (EMC) |
| AS/NZS 61000.4.1 | Testing and measurement techniques — Overview of immunity tests |
| IEC 60447 | Basic and safety principles for man-machine interface — Actuating principles |
| IEC 60721 | Classification of environmental conditions |
| IEC 60721-3-0 | Classification of groups of environmental parameters and their severities — Introduction |
| BS EN 1005 | Safety of machinery — Human physical performance |
| BS EN 1005-3 | Recommended force limits for machinery operation |

---

## 4. Definitions

**4.1 Category**
Classification of the safety-related parts of a control system in respect of their resistance to faults and their subsequent behaviour in the fault condition.
> Note: Such behaviour is achieved by the structural arrangement of the parts or by their reliability.

**4.2 Failure**
Termination of the ability of an item to perform a required function.
> Notes: (1) After a failure, the item has a fault. (2) 'Failure' is an event, 'fault' is a state. (3) Does not apply to items consisting of software only. (4) In practice, fault and failure are often used synonymously.

**4.3 Fault**
State of an item characterised by inability to perform a required function, except during preventive maintenance, planned actions, or due to lack of external resources.
> Note: A fault is often the result of a failure of the item itself, but may exist without prior failure.

**4.4 Manual Reset**
Function within the safety-related parts of the control system to manually restore given safety functions before the re-starting of a machine.

**4.5 Muting**
Temporary automatic suspension of a safety function(s) by safety-related parts of the control system to enable the machine (as a system) to achieve a safe state.

**4.6 Safety Function of a Control System**
Function initiated by an input signal and processed by the safety-related parts of the control system to enable the machine (as a system) to achieve a safe state.

**4.7 Safety of Control Systems**
Ability of safety-related parts of a control system to perform their safety function(s) for a given time according to their specified category.

**4.8 Safety-Related Part of a Control System**
Part or subpart(s) of a control system which responds to input signals and generates safety-related output signals.
> Note: The combined safety-related parts of a control system start at the points where the safety-related signals are initiated and end at the output of the power control elements (see AS 4024.1201). This also includes monitoring systems.

---

## 5. General Considerations

### 5.1 Safety Objectives in Design

The safety-related parts of a control system providing safety functions shall be designed and constructed so that the principles of AS 4024.1301 are fully taken into account during:
- All intended use and foreseeable misuse
- When faults occur
- When foreseeable human mistakes are made during intended use of the machine as a whole

### 5.2 General Strategy for Design

From the risk assessment (AS 4024.1301), the designer shall decide the contribution to risk reduction required from each safety-related part of the control system.

> This contribution does not cover the overall risk of the machinery under control — it covers the part of risk reduced by the application of particular safety functions (e.g. stop function initiated by an electrosensitive protective device on a press, or a door-locking function on a washing machine).

The key objective is that the safety-related parts of the control system produce outputs which achieve the risk reduction objectives of AS 4024.1301.

The designer shall declare:
- Which category is being used as the reference point for the design
- The exact points at which the safety-related part(s) start and end
- The design rationale: faults considered, faults excluded, within the design principles and category rationale

**Fault-resistance behaviour is a function of:**
- (i) Reliability in respect of performing safety functions
- (ii) Structure (architecture) of the control system
- (iii) Quality of safety-related documentation
- (iv) Completeness of the specification
- (v) Design, manufacture and maintenance
- (vi) Quality and accuracy of software
- (vii) Extent of functional testing
- (viii) Operating characteristics of the machine or part under control

These group into three main characteristics:
- **(A) Hardware reliability** — the level of reliability of components to avoid faults
- **(B) System structure** — the arrangement of components in the safety-related part to avoid, tolerate, or detect faults
- **(C) Non-quantifiable, qualitative aspects** — which affect the behaviour of the safety-related part of a control system

> Reliability and safety are not the same. A system with unreliable components in a redundant structure can be safer than a system with a simpler structure but more reliable components. In applications where consequences of failure are always serious and normally irreversible (e.g. a fault detection, one-cycle fault-tolerant structure), the required safety function after one or two or more faults shall be provided in accordance with the risk assessment.

### 5.3 Process for Selection and Design of Safety Measures

#### 5.3.1 General

This clause sets out a process for selecting safety measures and designing the safety-related parts of the control system. It is important that interfaces between:
- Safety-related parts of the control system
- Non-safety-related parts of the control system
- All other parts of the machine

...are identified. The process is iterative — decisions at any step may affect assumptions made at an earlier step.

#### 5.3.2 Step 1: Hazard Analysis and Risk Assessment

Identify all hazards present at the machine during all modes of operation and at each stage of the machine life cycle, following the guidance in AS 4024.1201 and AS 4024.1301.

Assess the risk from those hazards and decide the appropriate risk reduction for that application.

#### 5.3.3 Step 2: Decide Measures for Risk Reduction by Control Means

Decide the design measures at the machine or provision of safeguards to provide risk reduction. Those parts of the control system which contribute as an integral part of the design measures and/or control of safeguards shall be considered safety-related parts.

> Note: Guidance for selection of an appropriate category is given in Appendix C.

#### 5.3.4 Step 3: Specify Safety Requirements for the Safety-Related Parts

Specify the safety functions to be provided in the control system (see Table 1).

Specify how safety functions will be met and select the category(ies) for each part and combinations of parts within the safety-related parts.

#### 5.3.5 Step 4: Design

Design the safety-related parts according to the specification developed in Step 3 and to the general strategy in Clause 5.2. List the features included in the design which provide the rationale for the category(ies) achieved.

Verify the design at each stage against requirements from the previous stage in the context of the specified safety function(s) and category(ies).

#### 5.3.6 Step 5: Validation

Validate the achieved safety functions and category(ies) against the specification in Step 3. Redesign as necessary (see Clause 9).

Also validate the safety-related parts in conjunction with the entire control system and as part of the machine.

> When programmable electronics are used in the design of safety-related parts of control systems, other detailed procedures are required (see Clause 9.4.2).

### 5.4 Principles for Ergonomic Design

The interface between persons and the safety-related parts of control systems shall be designed and installed so that no one is endangered during all intended use and foreseeable misuse. Ergonomic principles (AS 4024.1201; AS 60204.1; IEC 60447; AS 4024.1401, 4024.1901, 4024.1902, 4024.1903; BS EN 1005-3) should apply.

---

## 6. Characteristics of Safety Functions

### 6.1 General

Table 1 lists typical safety functions and some of their characteristics. The designer shall ensure the requirements of all referenced Standards are satisfied for the selected safety functions. Characteristics shall be adapted for use with different energy sources where necessary.

**TABLE 1 — Standards Giving Requirements for Characteristics of Safety Function**

| Safety Function Characteristic | This Standard | AS 4024.1201 | AS 4024.1202 |
|---|---|---|---|
| Definitions | 4 | 4 | 4 |
| Design principles | 5.2 | — | 5 |
| Ergonomic function | 5.4 | 5.9 | 5.8 |
| Stop function | 6.2 | — | 5.11.3 / 5.11.4 |
| Emergency stop | 6.3 | — | 6.5.2 |
| Manual reset | 6.4 | — | — |
| Start and restart | 6.5 | — | 5.11.4 / 5.11.5 |
| Response time | 6.6 | — | — |
| Safety-related parameters | 6.7 | — | 5.11.9(e) |
| Local control function | 6.8 | — | 5.11.9 / 5.11.11 |
| Muting | 6.9 | — | — |
| Manual suspension of safety functions | 6.10 | — | 5.11.11 |
| Fluctuations, loss and restoration of power sources | 6.11 | — | 5.11.9(e) |
| Programmable electronic systems | — | — | 5.11.8 |
| Unexpected startup | — | — | 5.11.5 |
| Indications and alarms | — | — | 5.8.8 |
| Escape and rescue of trapped persons | — | — | 6.5.3 |
| Pneumatic and hydraulic equipment | — | — | 5.10 |
| Isolation and energy dissipation | — | — | 6.5.4 |
| Control modes and mode selection | — | — | 5.11.9 / 5.11.11 |
| Interfaces/connections | — | — | — |
| Interaction between different SRP/CS | — | — | 5.11.9(e) |

### 6.2 Stop Function

In addition to the requirements in Table 1:
- A stop function initiated by a protective device shall, as soon as necessary after actuation, put the machine in a safe state. Such a stop shall have priority over a stop for operational reasons.
- When a group of machines works in a coordinated manner, provision shall be made to signal to the supervisory control or other machines that a stop condition exists.

> Note: Such a stop can cause operational problems and a difficult restart (e.g. in arc welding). In some applications this function can be combined with a stop for operational reasons to reduce the temptation to defeat the safety function.

### 6.3 Emergency Stop Function

In addition to the requirements in Table 1:
- When machines work in a coordinated manner, the safety-related parts shall have the facility to signal an emergency stop condition to all parts of the coordinated system.
- Where sections of the coordinated system are clearly separated (e.g. by safeguards or physical position), it is not always necessary to apply an emergency stop to the whole system — only to the particular section identified by the risk assessment.
- After an emergency stop has become effective for a section, a hazard shall not be present at the interfaces of that section with other sections.

### 6.4 Manual Reset

In addition to the requirements in Table 1:
- After a stop command has been initiated by a protective device, the stop condition shall be maintained until the manual reset device is actuated and safe conditions for restarting exist.
- The re-establishment of the safety function by resetting the protective device cancels the stop command. If indicated by the risk assessment, cancellation of the stop command shall be confirmed by a manual, separate, and deliberate action (manual reset).

The manual reset function:
- (i) Shall be provided through a separate and manually operated device within the safety-related parts of the control system
- (ii) Shall only be achieved if all safety functions and protective devices are operative; if not possible the reset shall not be achieved
- (iii) Shall not initiate motion or a hazardous situation by itself
- (iv) Shall be by deliberate action
- (v) Shall prepare the control system for accepting a separate start command
- (vi) Shall only be accepted by actuation of the actuator from its released (OFF) position
- (d) The category of safety-related parts providing manual reset shall be selected so that the inclusion of manual reset does not diminish the safety required of the relevant safety function
- (e) The reset actuator shall be situated outside the danger zone and in a safe position from which there is good visibility to check that no person is within the danger zone

### 6.5 Start and Restart

In addition to the requirements in Table 1:
- A restart shall take place automatically only if a hazardous situation cannot exist. In particular, for control guards, see AS 4024.1201.
- These requirements for start and restart also apply to machines which can be controlled remotely.

### 6.6 Response Time

In addition to the requirements in Table 1, the designer or supplier shall declare the response time when the risk assessment of the safety-related parts of the control system indicates this is necessary (see also Clause 11).

> Note: The response time of the control system is part of the overall response time of the machine. The required overall response time of the machine can influence the design of the safety-related parts (e.g. the need to provide a braking system).

### 6.7 Safety-Related Parameters

In addition to the requirements in Table 1:
- When safety-related parameters (e.g. position, speed, temperature, pressure) deviate from preset limits, the control system shall initiate appropriate measures (e.g. actuation of stopping, warning signal or alarm).
- If errors in manual inputting of safety-related data in programmable electronic systems can lead to a hazardous situation, a data-checking system within the safety-related control system shall be provided (e.g. check of limits, format, or logic input values).

### 6.8 Local Control Function

When a machine is controlled locally (e.g. portable control device or pendant), in addition to Table 1:
- The means for selecting local control shall be situated outside the danger zone.
- It shall not be possible to initiate hazardous conditions from outside the zone of local control.
- Switching between local and external (e.g. remote) control shall not create a hazardous situation.

### 6.9 Muting

Muting shall not result in any person being exposed to hazardous situations. During muting, safe conditions shall be provided by other means.

At the end of muting, all safety functions of the safety-related parts of the control system shall be reinstated.

The category of safety-related parts providing the muting function shall be selected so that the inclusion of muting does not diminish the safety required of the relevant safety function.

In some applications, a signal indicating muting is required.

### 6.10 Manual Suspension of Safety Functions

If it is necessary to manually suspend safety functions (e.g. for set-up, adjustments, maintenance, or repair), in addition to Table 1:
- Effective and secure means shall be provided to prevent manual suspension in those operating modes where it is not allowed.
- Safety functions of the safety-related parts of the control system shall be reinstated before normal operations can be continued.
- Safety-related parts of the control system responsible for manual suspension shall be selected so that the principles of AS 4024.1301 are fully taken into account.

In some applications, a signal indicating manual suspension is required.

### 6.11 Fluctuations, Loss and Restoration of Power Sources

In addition to the requirements in Table 1: when fluctuations in energy levels outside the design operating range occur, including loss of energy supply, the safety-related parts of the control system shall continue to provide or initiate output signal(s) which will enable other parts of the machine system to maintain a safe state.

---

## 7. Categories

### 7.1 General

Safety-related parts of control systems shall be in accordance with one or more of the five categories specified in Clause 7.2. Categories are not intended to be used in any given order or any given hierarchy in respect of safety requirements.

Categories state the required behaviour of safety-related parts of a control system in respect of its resistance to faults based on the strategy described in Clause 5.2.

**Category B** is the basic category. Categories 1–4 progressively increase resistance to faults:
- **Category 1:** Improved resistance to faults — achieved predominantly by selection and application of components
- **Categories 2, 3, 4:** Improved performance in respect of a specified safety function — achieved predominantly by improving the structure of the safety-related part
  - **Category 2:** Periodic checking that the safety function is being performed
  - **Categories 3 and 4:** A single fault will not lead to loss of the safety function
  - **Category 4:** Whenever reasonably practicable as in Category 3, faults will be detected

> Direct comparison of fault-resistance behaviour between categories can only be made if one parameter (Clause 5.2) at a time is changed. Higher-numbered categories can only be interpreted as providing greater resistance to faults in comparable circumstances when using similar technology, components of comparable reliability, similar maintenance regimes, and in comparable applications.

### 7.2 Specifications of Categories

#### 7.2.1 Category B

Safety-related parts of control systems shall, as a minimum, be designed, constructed, selected, assembled, and combined in accordance with relevant Standards using basic safety principles for the specific application so they can withstand:
- Expected operating stresses (e.g. force and frequency of braking)
- Influence of the processed material (e.g. resistance of a washing machine to detergents)
- Other relevant external influences (e.g. mechanical vibration, external fields, power supply interruptions or disturbances)

No special measures for safety are applied to parts complying with Category B specifications.

When a fault occurs, it can lead to loss of the safety function. To fulfil AS 4024.1201 requirements, additional measures not provided by the safety-related parts of the control system may be necessary.

#### 7.2.2 Category 1

**7.2.2.1 General**
Requirements of Category B plus: safety-related parts shall be designed and constructed using well-tried components and well-tried safety principles.

**7.2.2.2 Well-Tried Components**
A well-tried component for safety-related application is a component which has been widely used in the past with successful results in similar applications, or made and verified using principles which demonstrate its suitability and reliability for safety-related applications.

In some well-tried components, certain faults can be excluded because the fault rate is known to be very low. Accepting a component as well-tried depends on the application.

> Note: On the level of single electronic components alone, it is not normally possible to achieve Category 1 status.

**7.2.2.3 Well-Tried Safety Principles**

Well-tried safety principles are, for example:
- Avoidance of certain faults (e.g. avoidance of short circuit by separation)
- Reduction of the probability of faults (e.g. over-dimensioning or underrating of components)
- Orientation of the mode of fault (e.g. by ensuring an open circuit when it is vital to remove power in the event of fault)
- Very early detection of faults
- Restriction of the consequences of a fault (e.g. earthing of equipment)

Newly developed components and safety principles may be considered equivalent to 'well-tried' if they fulfil the above-mentioned conditions.

> Notes: (1) The probability of failure in Category 1 is lower than in Category B; consequently loss of the safety function is less likely. (2) When a fault occurs it can lead to loss of the safety function; to fulfil AS 4024.1202, additional measures not provided by the safety-related parts of the control system may be necessary.

#### 7.2.3 Category 2

Requirements of Category B, the use of well-tried safety principles, and:
- Safety-related parts shall be designed so their functions are checked at suitable intervals by the machine control system. The check of safety functions shall be performed:
  - (i) At machine start-up and prior to initiation of any hazardous situation
  - (ii) Periodically during operation, if the risk assessment and kind of operation shows this is necessary

The initiation of the check may be automatic or manual. Any check of safety functions shall either:
- (i) Allow operation if no faults have been detected, or
- (ii) Generate an output which initiates appropriate control action if a fault is detected; whenever possible, this output shall initiate a safe state. When it is not possible to initiate a safe state (e.g. welding of the contact in the final switching device), the output shall provide a warning of the hazard

The check itself shall not lead to a hazardous situation. The checking equipment may be integral with, or separate from, the safety-related parts providing the safety function.

After detection of a fault, a safe state shall be maintained until the fault is cleared.

Category 2 system behaviour allows that:
- (i) The occurrence of a fault can lead to loss of the safety function between checks
- (ii) The loss of safety function is detected by the check

> Notes: (1) In some cases, Category 2 is not applicable because checking of the safety function cannot be applied to all components (e.g. pressure switch or temperature sensor). (2) In general, Category 2 can be achieved with electronic techniques, e.g. in protective equipment and particular control systems.

#### 7.2.4 Category 3

Requirements of Category B, well-tried safety principles, and:
- Safety-related parts shall be designed so that a single fault in any of these parts does not lead to loss of the safety function
- Common-mode faults shall be taken into account when the probability of such a fault occurring is significant
- Whenever reasonably practicable, the single fault shall be detected at or before the next demand upon the safety function

Category 3 system behaviour allows that:
- (i) When a single fault occurs, the safety function is always performed
- (ii) Some but not all faults will be detected
- (iii) Accumulation of undetected faults can lead to loss of the safety function

> Notes: (1) Single fault detection does not mean all faults will be detected; accumulation of undetected faults can lead to an unintended output signal and hazardous situation. Typical practicable measures for fault detection: the connected movement of relay contacts or monitoring of redundant electrical outputs. (2) Designers should give further details on detection of faults if necessary because of technology and application. (3) 'Whenever reasonably practicable' means the required measures for fault detection and the extent to which they are implemented depends mainly upon the consequences of a failure and the probability of the occurrence of this failure within the application. The technology used will influence the possibilities for implementation of fault detection.

#### 7.2.5 Category 4

Requirements of Category B, well-tried safety principles, and:
- Safety-related parts shall be designed so that a single fault in any of these safety-related parts does not lead to loss of the safety function, and the single fault is detected at or before the next demand upon the safety functions (e.g. immediately, at switch-on, or at the end of a machine operating cycle). If this detection is not possible, then an accumulation of faults shall not lead to loss of the safety function.
- If the detection of certain faults is not possible, at least during the next check-up after occurrence of the fault (for reasons of technology or circuit engineering), the occurrence of further faults shall be assumed. In this situation the accumulation of faults shall not lead to loss of the safety function.
- Fault review may be stopped when the probability of further faults is considered sufficiently low. The number of faults in combination which need to be taken into consideration will depend on the technology, structure and application but shall be sufficient to meet the detection criteria. This fault review may be limited to two faults in combination when:
  - (i) Fault rates of the components are low
  - (ii) Faults in combination are largely independent of each other
  - (iii) The interruption of the safety function occurs only when the faults appear in a certain order
- If further faults occur as a result of the first single fault, the first and all consequent faults shall be considered as a single fault.
- Common-mode faults shall be taken into account (e.g. using diversity, special procedures, to identify such faults).

Category 4 system behaviour allows that:
- (i) When faults occur, the safety function is always performed
- (ii) Faults will be detected in time to prevent loss of the safety function

> Notes: (1) In practice, the number of faults to consider will vary considerably — in complex microprocessor circuits, a large number of faults can exist but in an electrohydraulic circuit, three (or even two) faults can be sufficient. (2) For complex circuit structures (e.g. microprocessors), complete redundancies, the review of faults is generally carried out at the structural level, i.e. based on assembly groups.

**TABLE 2 — Summary of Requirements for Categories (see Clause 7)**

| Category | Summary Requirements | System Behaviour | Principles to Achieve Safety |
|---|---|---|---|
| **B** | Safety-related parts shall be designed, constructed, selected, assembled, and combined in accordance with relevant Standards using basic safety principles so they can withstand expected influences. | The occurrence of a fault can lead to loss of the safety function. | Mainly characterised by selection of components |
| **1** | Requirements of B shall apply. Well-tried components and well-tried safety principles shall be used. | The occurrence of a fault can lead to loss of the safety function, but the probability of occurrence is lower than for Category B. | Mainly characterised by selection of components |
| **2** | Requirements of B and well-tried safety principles shall apply. Safety function shall be checked at suitable intervals by the machine control system. | The loss of safety function is detected between the checks. | Mainly characterised by structure |
| **3** | Requirements of B and well-tried safety principles shall apply. Safety-related parts shall be designed so that a single fault in any of these parts does not lead to loss of the safety function, and single faults are detected. | When a single fault occurs, the safety function is always performed. Some but not all faults will be detected. Accumulation of undetected faults can lead to loss of the safety function. | Mainly characterised by structure |
| **4** | Requirements of B and well-tried safety principles shall apply. Safety-related parts shall be designed so that a single fault does not lead to loss of the safety function, and the single fault is detected at or before the next demand upon the safety functions. If detection is not possible, an accumulation of faults shall not lead to loss of the safety function. | When faults occur, the safety function is always performed. The faults will be detected in time to prevent loss of the safety function. | Mainly characterised by structure |

> Notes: (1) Categories are not intended to be used in any given order or in any given hierarchy in respect of safety requirements. (2) The risk assessment will indicate whether the total or partial loss of the safety function(s) arising from faults is acceptable.

### 7.3 Selection and Combination of Safety-Related Parts to Different Categories

Safety functions (Clause 4.6 and Clause 6) are specified by the procedure described in Clause 5.3. Categories shall be selected for all safety-related parts of the control system. A single safety function may be processed by one or more safety-related parts. Similarly several safety functions may be processed by one or more safety-related parts.

When a safety function is carried out by several safety-related parts (e.g. sensors, control unit, power control elements), these parts may be assigned to one category and/or to different categories in combination.

When safety-related parts assigned to the same or different categories are used in combination to fulfil a safety function, an analysis of the combination shall be included in the overall validation required in Step 5 of Clause 5.3.

The selection of a category for a particular safety-related part depends mainly upon:
- (a) The reduction in risk to be achieved by the safety function to which the part contributes
- (b) The probability of occurrence of a fault(s) in that part
- (c) The risk arising in the case of a fault(s) in that part
- (d) The possibilities to avoid a fault(s) in that part
- (e) The technologies used

> Note: Additional information for the selection of categories is given in Appendix C.

---

## 8. Fault Consideration

### 8.1 General

In accordance with the category required, safety-related parts shall be selected on their ability to resist faults (see Clause 5.2). To assess their ability to resist faults, the various modes of failure shall be considered. Certain faults may also be excluded (see Clause 8.2).

Appendix D lists some of the significant faults and failures for various technologies. These lists and the ways in which they shall be validated are further elaborated in AS 4024.1502. The lists in Appendix D and in AS 4024.1502 are not exhaustive — additional faults should be considered and listed.

In such cases, the method of validation shall also be clearly described.

In general, the following fault criteria shall be taken into account:
- (a) If as a consequence of a fault further components fail, the first fault and all these following faults shall be considered as a single fault.
- (b) Common-mode faults are regarded as a single fault.
- (c) The occurrence at the same time of two independent faults is not considered.

### 8.2 Fault Exclusion

It is impracticable to assess safety-related parts without assuming that certain faults can be excluded. Fault exclusions can be made as a compromise between the technical requirements for safety and the theoretical possibilities of occurrence. This will be influenced by the design, dimensioning, installation, and arrangement of components in the safety-related parts. The designer shall declare, justify, and list all fault exclusions.

Fault exclusion should consider:
- (a) The improbability of the occurrence of certain fault(s)
- (b) Generally accepted technical experience which can be applied independently of the application under consideration
- (c) Technical requirements deriving from the application and the specific risk under consideration
- (d) The harshness of the environment such that fault exclusion for a less harsh environment is not applicable

---

## 9. Validation

### 9.1 General

The purpose of validation is to determine the level of conformity of the safety-related parts of the control system to their specification within the overall safety requirements specification of the machinery. Validation consists of executing tests and applying analysis in accordance with the validation plan (see Clause 9.2).

The design of the safety-related parts of the control system shall be validated. The validation shall demonstrate that each safety-related part meets:
- (a) All the requirements of the specified category (see Clause 7)
- (b) The specified safety characteristics for that part, as set out in the design rationale

The validation of the safety-related parts of control systems should contain:
- (i) Selection of the validation strategy (a validation plan)
- (ii) Management and execution of validation activities (test specifications, testing procedures, analysis procedures)
- (iii) Documentation (auditable reports of all validation activities and decisions)

> Note: Guidance on validation procedures is given in AS 61508.

### 9.2 Validation Plan

The validation plan shall identify the requirements for carrying out all stages of the validation process. The plan should be developed concurrently with the design of the safety-related parts of the control system or can be specified by the relevant machine-specific safety standard.

The plan should include a description of all the requirements for the following:
- (a) Validation by analysis
- (b) Validation by testing:
  - (i) Test of the specified safety functions
  - (ii) Test of the specified categories
  - (iii) Test of dimensioning and compliance to environmental parameters

### 9.3 Validation by Analysis

Analysis is necessary to validate that the reduction in risk has been achieved. Examples of analysis tools: fault lists (see Clause 8), fault tree analysis, failure mode and effects analysis, criticality analysis, and check lists for systematic faults.

### 9.4 Validation by Testing

#### 9.4.1 Test of the Specified Safety Functions

Test the safety functions of the safety-related parts of the control system for complete compliance with their specified characteristics. Check for errors and particularly for omissions when formulating the specification during development of the machine.

The aim is to ascertain that the safety-related output signals are correct and logically dependent on the input signals. The tests should cover all normal and foreseeable abnormal conditions in static and dynamic simulation, as necessary from the risk assessment, to validate the system.

#### 9.4.2 Test of the Specified Categories

Tests shall demonstrate that the requirement is fulfilled. Test procedures shall be chosen on the basis of two criteria: technology and complexity of the control system. The following methods are applicable:
- (a) A theoretical check and behaviour analysis based on circuit diagrams
- (b) Practical tests on the actual circuit, and fault simulation on actual components — particularly in areas of doubt of behaviour identified during the theoretical check and analysis
- (c) A simulation of control system behaviour (e.g. hardware or software models)

In some applications where safety-related parts are connected in a complex manner, it is necessary to divide the connected safety-related parts into several functional groups and to exclusively submit the interfaces to fault-simulation tests.

#### 9.4.3 Test of Dimensioning and Compliance to Environmental Parameters

Tests shall demonstrate that the specified design performance is achieved during all specified operating modes and all specified environmental conditions. Tests should include: tests for expected mechanical structure, electrical ratings, temperature, humidity, vibration, shock loading, electromagnetic compatibility, influence of processed materials.

Relevant standards: AS 60529, AS 60068.1, AS 60204.1, IEC 60721-3-0, AS 61000.4.1.

---

## 10. Validation Report

At the conclusion of the validation process, a safety validation report shall be made summarising the tests and analyses carried out, including the results. The report should specifically identify:
- (a) All items under test
- (b) Personnel responsible for testing
- (c) Test equipment (including details of calibration) and simulation tools
- (d) Analyses and tests carried out
- (e) Problems encountered and how these problems were resolved
- (f) Results

The results shall be documented and retained in an auditable form.

> Note: Compliance with this Clause will assist the manufacturer in completing the technical construction file in respect of the safety-related parts of the control system.

---

## 11. Maintenance

Preventive or corrective maintenance is usually necessary to maintain the specified performance of the safety-related parts. Deviations with time from the specified performance can lead to deterioration in safety or can even lead to a hazardous situation. To identify such deviations, manual periodic inspections are sometimes necessary.

The provisions for the maintainability of the safety-related part(s) of a control system shall follow the principles and all information for maintenance shall comply with AS 4024.1202.

---

## 12. Information to be Provided to the User

The principles given in AS 4024.1202 and other relevant documents (e.g. AS 60204.1) shall be applied. In particular, information which is important for the safe use of the safety-related parts of the control system shall be provided to the user. This includes but is not limited to:
- (a) The limits of the safety-related parts to the category(ies) selected and any fault exclusions. When fault exclusions are essential in maintaining the selected category(ies) and safety performance, appropriate information (e.g. for modification, maintenance, and repair) is needed to ensure the continued justification of that fault exclusion(s).
- (b) The effects of deviations from the specified performance on the safety function(s)
- (c) Clear descriptions of the interfaces to the safety-related parts of control systems and protective devices
- (d) Response time
- (e) Operating limits (including environmental conditions)
- (f) Indications and alarms
- (g) Muting and suspension of safety functions
- (h) Control modes
- (i) Maintenance (see Clause 11)
- (j) Maintenance checklists
- (k) Ease of accessibility and replacing of internal parts
- (l) Means for easy and safe troubleshooting

---

## Appendix A — Questionnaire for Use During the Design Process
*(Informative)*

**A1 What reaction is required from the safety-related parts of the control system(s) when faults occur?**
- No special action required
- Safe reaction required within a certain time
- Safe reaction immediately required

**A2 In which safety-related part(s) of the control system should faults be assumed?**
- Only in those parts in which (by experience) faults occur relatively often (e.g. peripheral sensors and wiring)
- In auxiliary parts
- In all safety-related parts

**A3 Do both random and systematic faults need to be considered?**

**A4 Which faults should be assumed in the components of the safety-related parts of the control system?**
- Faults only in components which are not well-tried
- Faults in components

**A5 Has the correct reference category been selected in respect of the requirement for detecting faults?**
- Normal requirements for fault detection: all faults which can be detected with relatively simple methods should be detected
- Stringent requirements for fault detection: techniques should be used which enable most of the faults to be detected; if not reasonably practicable, combinations of faults should be assumed (fault accumulation, see Clause 7.2.5)

**A6 What should the next action of the control system be if a fault has been detected?**
- The machine should be brought to a predetermined state as required by the risk assessment
- Further operation of the machine can be permitted until the fault is rectified
- The indication of the fault(s) is sufficient (e.g. warning signal by VDU)

**A7 What is necessary to meet the maintenance requirement?**
- Information on the effects of deviation from design specifications
- Automatic indication of the need for maintenance
- Setting of maintenance intervals
- Setting of component lifetimes
- Provision of diagnostic facilities and test points
- Special precautions for safety during maintenance

**A8 What methods should be used for fault detection?**
- Automatic fault detection, as far as appropriate
- Manual fault detection, e.g. by periodic inspection
- Provision of more than one method

**A9 Has the risk reduction been achieved?**
- Can the risk reduction be achieved more easily with a different combination of risk reduction measures?
- Check that the measures taken do not reduce the ability of the machine to perform its function or generate new, unexpected hazards or problems
- Are the solutions valid for all operating conditions and for all procedures?
- Are these solutions compatible with each other?
- Is the safety specification correct?

**A10 Have ergonomic principles been considered?**
- Are the safety-related parts of the control system, including the protective devices, easy to use?
- Is there safe and easy access to the control system?
- Are warning signals given priority (e.g. highlighted)?

**A11 Have the relationships between safety, reliability, availability, and ergonomics been optimised in such a way that the safety measures will be maintained during the lifetime of the system, and do not tempt personnel to defeat the safety functions?**

---

## Appendix B — Relationship Between Safety, Reliability and Availability for Machinery
*(Informative)*

- **(a) Safety** — the ability of a machine to perform its function, to be transported, installed, adjusted, maintained, dismantled, and disposed of under conditions of intended use without causing injury or damage to health.
- **(b) Reliability** — the ability of a machine or component to perform a required function without failing under specified conditions and for a given period of time.
- **(c) Availability** — the ability of an item to be in a state to perform a required function under given conditions at a given instant of time or over a given time interval, assuming the required external resources are provided.

Safety looks at the causes and consequences of possible accidents. The safety requirements ensure that the system does not reach a hazardous or unsafe state when an event(s) could cause an accident.

From the viewpoint of safety, it does not matter if the system does not serve its purpose, as long as safety requirements are not violated. On the other hand it is possible that the system is highly reliable, but unsafe (e.g. a system with formally verified software but for which a safety-related situation has not been properly specified).

Availability influences safety. The availability of a system implies that the safety-related reliability is performed — otherwise the protective device can be defeated.

The designer is responsible for deciding, for each application, the relationship between availability, reliability, and safety in order to ensure that the reduction in risk is achieved.

---

## Appendix C — Guidance for Selection of Categories
*(Informative)*

### C1 General

This Appendix describes a simplified method based on AS 4024.1301 to select the appropriate categories as reference points for the design of the various safety-related parts of a control system. This guidance should be considered as part of the risk assessment given in AS 4024.1301 and not a substitute for it.

The method provides only an estimation of risk reduction and is intended to guide the designer and standard-maker to a choice of category based on its behaviour in case of a fault. Other influences also contribute to the assessment that adequate safety has been achieved (e.g. component reliability, technology used, or particular application).

**The method:**
- Severity of injury (denoted by **S**) is relatively easy to estimate (e.g. laceration, amputation, fatality)
- For frequency of occurrence, auxiliary parameters improve the estimation:
  - (a) Frequency and duration of exposure to the hazard (**F**)
  - (b) Possibility of avoiding the hazard (**P**)

Experience has shown that S, F, and P can be combined as in Figure C1 to give a gradation of risk from low to high. This is a qualitative process which gives only an estimation of risk.

In Figure C1, the preferred category is indicated by a large filled circle. In some applications, the designer can deviate to another category (small circle or large unfilled circle). Categories other than preferred can be used (see Clause 7.3) but the intended system behaviour in case of fault(s) should be maintained. Reasons for deviating should be given (e.g. different technologies, well-tried hydraulic/electromechanical components in combination with electrical or electronic systems (Category 3 or 4); when categories with a small circle in Figure C1 are selected, additional measures can be required, e.g. over-dimensioning, use of techniques leading to fault exclusion, or use of dynamic monitoring).

### C2 Guidance for Selecting Parameters S, F and P for Risk Estimation

#### C2.1 Severity of Injury S1 and S2

In estimating risk from fault(s) in the safety-related parts, only slight injuries (normally reversible) and serious injuries (normally irreversible, including death) are considered:
- **S1** — Slight (normally reversible) injury: bruising or lacerations without complications
- **S2** — Serious (normally irreversible) injury, including death: amputation or death

#### C2.2 Frequency or Duration of Exposure to Hazard F1 and F2

A generally valid time period cannot be specified. However:
- **F2** should be selected if a person is frequently or continuously exposed to the hazard (irrelevant whether same or different persons are exposed on successive exposures, e.g. use of lifts). Evaluate duration on the basis of an average value in relation to total period of time in which the equipment is used.
- Example: If it is necessary to reach regularly between tools during cyclic operation, F2 should be selected. If access is only required from time to time, F1 can be selected.

#### C2.3 Possibility of Avoiding the Hazard P

When a hazard arises, it is important to know if it can be recognised and whether it can be avoided before it leads to an accident. Important aspects:
- (a) Operation with or without supervision
- (b) Operation by experts or non-professionals
- (c) Speed with which the hazard arises (quickly or slowly)
- (d) Possibilities for hazard avoidance (e.g. taking flight or intervention of a third party)
- (e) Practical safety experiences relating to the process

**P1** should only be selected if there is a realistic chance of avoiding an accident or significantly reducing its effect. **P2** should be selected if there is almost no chance of avoiding the hazard.

**FIGURE C1 — Possible Selection of Categories for Safety-Related Parts of Control Systems**

Legend:
- **S** Severity of injury: S1 = Slight (normally reversible) / S2 = Serious (normally irreversible, including death)
- **F** Frequency and/or duration of exposure: F1 = Seldom to quite often, and/or short exposure time / F2 = Frequent to continuous and/or long exposure time
- **P** Possibility of avoiding the hazard: P1 = Possible under specific conditions / P2 = Nearly impossible
- ● = Preferred categories for reference points (see Clause 5.2)
- • = Possible categories which may require additional measures (see C1)
- ○ = Measures which can be over-dimensioned for the relevant risk

---

## Appendix D — Examples of Significant Faults and Failures for Various Technologies
*(Informative)*

### D1 Electrical or Electronic Components

Faults and failures to consider:
- (a) Short circuit or open circuit (e.g. earth faults, open circuit of any conductor)
- (b) Short circuit or open circuit in single components (e.g. position switches, control and regulation equipment, machine actuators, relays)
- (c) Non-drop-out or non-pick-up of electromagnetic elements (e.g. contactors, relays, solenoids)
- (d) Non-starting or non-stopping of motors (e.g. servomotors)
- (e) Mechanical blocking of moving elements, loosening or displacing of fixed elements (e.g. position switches)
- (f) Drift beyond tolerance values for analog elements (e.g. resistors, capacitors, transistors)
- (g) Oscillation of (unstable) output signals in integrated components
- (h) Loss of entire or partial function(s) (worst-case behaviour) in complex integrated components (e.g. microprocessors, programmable electronic systems, application-specific integrated circuits)

### D2 Hydraulic and Pneumatic Components

Faults and failures to consider:
- (a) Lack of or incomplete switching of the moving element (e.g. sticking of a valve piston)
- (b) Drift in original control position of the moving element (e.g. directional control valves)
- (c) Leakage and modification of leakage volume flow (e.g. directional control valves)
- (d) Unstable control characteristics in servo-valves and proportional valves
- (e) Loss of pressure or bursting of lines (e.g. hose pipes and at the hose coupling)
- (f) Clogging of filter element (in particular caused by solid substances)
- (g) Abnormal pressure and/or volume flow (e.g. hydraulic pumps, hydraulic motors, compressors, cylinders)
- (h) Failure or abnormal modification of input or output signal characteristics in sensors (e.g. pressure switches)

### D3 Mechanical Components

Faults and failures to consider:
- (a) Spring fracture
- (b) Stiffness or sticking of guide moving components
- (c) Loosening of fixtures (e.g. by vibration)
- (d) Wear (e.g. of runners, latches, rollers)
- (e) Misalignment of parts
- (f) Environmental influences (e.g. corrosion, temperature effects)

---

*End of document — AS 4024.1501*