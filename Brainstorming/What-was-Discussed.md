# IT Group Project – Defender Robot Brainstorm 
*summerised by Chat GPT*

## Overview
The group discussed the design of a **defensive robot system** (with elements of passing/attacking), focusing on:
- Ball collection and launching
- Sensor selection
- Motor usage
- Communication between components
- Positioning and accuracy strategies

The system mainly consists of **two EV3 robots**:
1. **Movement + Shield Robot**
2. **Shooting/Passing Robot**

---

## Core Design Concept

### Ball Collection & Launching
- Use **two հակ-rotating motors** to suck the ball into a chamber.
- Ball is stored in a **small internal chamber**.
- A separate mechanism launches the ball using:
  - Spinning gears OR
  - A pushing mechanism.

### Ball Handling Ideas
- Ball enters → detected by **colour sensor** → held temporarily → released when needed.
- Two main holding concepts:
  1. **Lid mechanism**
     - Closes after ball enters
     - Opens to release
  2. **Pusher mechanism**
     - Holds ball without lid
     - Pushes ball out when shooting

- Chamber may be slightly **inclined** so ball rolls out when released.

---

## Robot Roles

### 1. Movement + Shield Robot
**Responsibilities:**
- Navigation and positioning
- Aiming (by rotating/positioning itself)
- Defensive blocking (shield)

**Sensors:**
- IR sensor → detects ball / direction
- Colour sensor → detect ball in system
- Gyro sensor → orientation and direction
- (Optional) Touch sensor

**Motors:**
- 2 × Large motors → movement
- 1 × Medium motor → shield control
- (Possible extra motor for lid/blocking mechanism)

---

### 2. Shooting / Passing Robot
**Responsibilities:**
- Intake (suction)
- Holding the ball
- Shooting/passing the ball

**Sensors:**
- Ultrasonic sensor → distance measurement for shot power
- Colour sensor → detect ball presence

**Motors:**
- 1 × Large motor → intake + shooting (same direction system)
- Possibly additional motor for:
  - Catch mechanism
  - Ball control

---

## Communication Strategy

- Robots **communicate between movement and shooting systems**.
- Movement robot determines:
  - Direction of partner robot
  - When to shoot
- Shooting robot:
  - Only calculates **how hard to shoot** (based on distance)

---

## Aiming & Navigation

### Aiming Method
- No adjustable shooter angle
- Robot aims by **physically rotating itself**

### Position Tracking
- Use:
  - **Gyro sensor**
  - **Calculated coordinates (based on movement)**
- Combine both to improve accuracy:
  - Compare expected vs actual movement
  - Correct errors (e.g. slippage)

### Accuracy Strategy
- Move **slowly for better precision**
- Use multiple readings (e.g. gyro averages)

---

## Alternative / Advanced Ideas

### Multi-Robot / Sensor Expansion
- Considered a **third EV3 robot** for:
  - Processing sensor data
  - Central coordination
- Rejected due to:
  - Limited working hardware
  - Complexity

### Ultrasonic Mapping Idea
- Use **4 ultrasonic sensors** to map environment
- Could build a **map of the arena**
- Possibly used for localisation

### Touch Sensor Communication
- Idea to convert multiple sensor outputs into **binary via touch signals**
- Rejected as:
  - Too slow
  - Inefficient

---

## Shield Design

Options discussed:
- Front-mounted shield
- Side-mounted shield
- Back-mounted shield

Considerations:
- Must not block IR sensor
- Possible solutions:
  - Leave gaps
  - Use **transparent LEGO pieces**

---

## Ball Strategy

- System mainly focuses on **passing**, not scoring
- Attack robot (future):
  - Will need to calculate **arc trajectory**
  - More complex than defender

### Passing Logic
- Movement robot aligns direction
- Shooting robot adjusts **power based on distance**

---

## Constraints & Assumptions

- Robots must operate **fully autonomously**
- No manual intervention allowed
- Must start from **known positions**
- Limited number of ports and sensors

---

## Key Challenges Identified

- Accurate positioning (gyro drift, wheel slip)
- Coordinating two robots
- Timing ball intake vs shooting
- Preventing premature ball release
- Sensor limitations (ports, reliability)

---

## Future Work

- Finalise:
  - Sensor allocation
  - Motor assignments
- Build and test:
  - Ball intake mechanism
  - Shooting consistency
- Develop:
  - Position tracking system
  - Communication between robots
- Begin design of **attacking robot**

---

## General Conclusion

- The group developed a **functional high-level design**
- System is complex but feasible
- Next step is **testing and refinement**
