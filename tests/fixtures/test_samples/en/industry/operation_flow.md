# Automated Assembly Line A1 Startup Operation Procedure

**Procedure Number**: OP-2024-001
**Version**: v2.1
**Preparation Date**: February 2024
**Applicable Equipment**: Automated Assembly Line A1

---

## 1. Scope of Application

This procedure applies to the startup operation of Automated Assembly Line A1, including CNC machining centers, robotic arm systems, material handling systems, and quality inspection stations.

---

## 2. Pre-Startup Checks

### 2.1 Environment Check

| Check Item | Check Content | Status |
|------------|---------------|--------|
| Temperature | Environment temperature should be within 15-30°C | □ |
| Humidity | Relative humidity should be within 40-70% | □ |
| Cleanliness | No debris or water accumulation around equipment | □ |

### 2.2 Equipment Check

| Check Item | Check Content | Status |
|------------|---------------|--------|
| Power Supply | Main power voltage normal, three-phase balanced | □ |
| Air Source | Air pressure maintained at 0.5-0.7MPa | □ |
| Lubrication | All lubrication points have sufficient grease | □ |
| Safety Devices | Emergency stop button, door locks normal | □ |

---

## 3. Startup Procedure

### 3.1 Step 1: Start Auxiliary System

**Operation**: Turn on auxiliary power supply for control cabinet

- Open control cabinet door
- Close auxiliary power switch
- Confirm auxiliary power indicator lights up

**Expected Result**: Auxiliary power normally connected, control panel shows ready status

**Trigger Condition**: Auxiliary power normal

### 3.2 Step 2: Start Hydraulic System

**Operation**: Start hydraulic station

- Press hydraulic station start button
- Wait for hydraulic pressure to rise to set value
- Check hydraulic oil level

**Expected Result**: Hydraulic pressure stable at 3.5MPa, oil level normal

**Trigger Condition**: Hydraulic pressure reaches set value

### 3.3 Step 3: Start Cooling System

**Operation**: Turn on cooling pump

- Turn on cooling pump power switch
- Adjust coolant flow to appropriate value
- Check coolant temperature

**Expected Result**: Cooling system正常运行，进出口温差在5-10°C

**Trigger Condition**: Cooling pump runs without abnormality

### 3.4 Step 4: Start Control System

**Operation**: Start main control system

- Select "Automatic Mode" on HMI
- Click "System Start" button
- Wait for system self-test to complete

**Expected Result**: HMI displays "System Ready", no alarm information

**Trigger Condition**: System self-test passed

### 3.5 Step 5: Activate Servo System

**Operation**: Start servo drive

- Start each axis servo driver in sequence
- Wait for servo system to be ready
- Perform origin reference return

**Expected Result**: Each axis returns to reference origin, position display correct

**Trigger Condition**: Servo system without fault

### 3.6 Step 6: Start Material Handling System

**Operation**: Start conveyor and AGV

- Start conveyor motor
- Activate AGV navigation system
- Set transport path

**Expected Result**: Conveyor runs normally, AGV in position and on standby

**Trigger Condition**: Conveyor runs smoothly

### 3.7 Step 7: Start Robotic System

**Operation**: Activate robotic arm

- Start robotic arm control cabinet
- Load processing program
- Perform robotic arm origin return

**Expected Result**: Each robotic arm joint normal, reaching origin position

**Trigger Condition**: Robotic arm without collision alarm

### 3.8 Step 8: Start Quality Inspection System

**Operation**: Turn on inspection equipment

- Start vision inspection system
- Calibrate inspection parameters
- Load inspection program

**Expected Result**: Inspection system ready, can normally identify workpieces

**Trigger Condition**: Inspection system self-test passed

---

## 4. Full Startup Confirmation

After completing the above steps, perform full confirmation:

| Check Item | Confirmation Content | Result |
|------------|---------------------|--------|
| System Status | All subsystems display "Ready" | □ |
| Communication Status | All equipment communication normal | □ |
| Safety Status | Safety doors closed, emergency stop released | □ |
| Production Mode | Switch to automatic production mode | □ |

---

## 5. Startup Abnormality Handling

### 5.1 Insufficient Hydraulic Pressure

- Check if hydraulic oil is sufficient
- Check if hydraulic pump is normal
- Check for leaks

### 5.2 Cooling System Alarm

- Check coolant level
- Check cooling pump operating status
- Clean cooling filter

### 5.3 Servo System Fault

- Check servo drive alarm code
- Check motor connection
- Perform fault reset

---

## 6. Shutdown Procedure

### 6.1 Normal Shutdown

1. Stop material input
2. Wait for current process to complete
3. Stop each subsystem in sequence
4. Turn off main power

### 6.2 Emergency Shutdown

Press emergency stop button, equipment stops immediately, then follow normal procedure to check before restarting.

---

**Prepared by**: Equipment Department
**Reviewed by**: Technical Department
**Approved by**: Production Department
