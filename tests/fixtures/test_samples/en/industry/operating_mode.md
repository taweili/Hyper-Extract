# Automated Assembly Line A1 Operating Mode Switching Manual

**Document Number**: OM-2024-001
**Version**: v1.0
**Preparation Date**: February 2024
**Applicable Equipment**: Automated Assembly Line A1

---

## 1. Overview

This document describes the operating modes and mode switching conditions of Automated Assembly Line A1. Operators shall strictly follow this manual for mode switching operations to ensure safe equipment operation.

---

## 2. Operating Modes

Automated Assembly Line A1 supports the following operating modes:

### 2.1 Shutdown Mode

**Mode Description**: Equipment completely stops operation, all systems powered off.

**Applicable Conditions**:
- Production task completed
- Equipment maintenance
- Long-term shutdown

**Load Range**: 0%

### 2.2 Standby Mode

**Mode Description**: Equipment is in hot standby state, main power remains powered, control system ready, can start quickly.

**Applicable Conditions**:
- Pre-production preparation
- Production pause
- Short break

**Load Range**: 5-10%

### 2.3 Manual Debug Mode

**Mode Description**: Equipment is manually controlled by operators, used for equipment debugging, maintenance and fault troubleshooting.

**Applicable Conditions**:
- Equipment debugging
- Maintenance operations
- Fault troubleshooting
- New program testing

**Load Range**: 0-30%

### 2.4 Automatic Operation Mode

**Mode Description**: Equipment automatically runs according to preset program without human intervention.

**Applicable Conditions**:
- Normal production operation
- Mass production

**Load Range**: 30-100%

### 2.5 Emergency Stop Mode

**Mode Description**: Equipment immediately stops all actions, cuts off power source.

**Applicable Conditions**:
- Emergency occurs
- Equipment failure
- Personnel safety threatened

**Load Range**: 0%

---

## 3. Mode Switching

### 3.1 Shutdown Mode → Standby Mode

**Switching Conditions**:
- Close main power switch
- Control system self-test passed

**Switching Steps**:
1. Close main power switch
2. Start auxiliary system
3. Control system self-test
4. Enter standby state

**Switching Time**: Approximately 30 seconds

### 3.2 Standby Mode → Manual Debug Mode

**Switching Conditions**:
- Engage manual handle
- Select manual mode

**Switching Steps**:
1. Engage manual handle
2. Select manual mode on HMI
3. Confirm mode switch
4. Enter manual debug state

**Switching Time**: Approximately 5 seconds

### 3.3 Manual Debug Mode → Standby Mode

**Switching Conditions**:
- Disengage manual handle
- Exit manual mode

**Switching Steps**:
1. Disengage manual handle
2. Select exit manual mode on HMI
3. Confirm exit
4. Return to standby state

**Switching Time**: Approximately 3 seconds

### 3.4 Standby Mode → Automatic Operation Mode

**Switching Conditions**:
- Production task ready
- Materials sufficient
- All subsystems normal
- Press automatic start button

**Switching Steps**:
1. Confirm production task is issued
2. Confirm materials are sufficient
3. Confirm all systems status normal
4. Press automatic start button
5. System loads production program
6. Gradually increase operation speed
7. Enter automatic operation state

**Switching Time**: Approximately 60 seconds

### 3.5 Automatic Operation Mode → Standby Mode

**Switching Conditions**:
- Production task completed
- Press pause button

**Switching Steps**:
1. Press pause button
2. Wait for current process to complete
3. Equipment stops automatic operation
4. Keep power supply
5. Enter standby state

**Switching Time**: Approximately 30 seconds

### 3.6 Automatic Operation Mode → Emergency Stop Mode

**Switching Conditions**:
- Press emergency stop button
- Serious fault detected
- Safety guard opened

**Switching Steps**:
1. Press emergency stop button (or fault triggered)
2. Immediately stop all moving parts
3. Cut off main power
4. Activate alarm device
5. Enter emergency stop state

**Switching Time**: Immediate

### 3.7 Emergency Stop Mode → Standby Mode

**Switching Conditions**:
- Fault cleared
- Site safety confirmed
- Press reset button

**Switching Steps**:
1. Confirm fault is cleared
2. Confirm site is safe
3. Close emergency stop button
4. Press reset button
5. System self-test
6. Enter standby state

**Switching Time**: Approximately 60 seconds

---

## 4. Mode Switching Flowchart

```
                    ┌──────────────┐
                    │  Shutdown   │
                    │    Mode     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   Standby   │
                    │    Mode     │
                    └──────┬───────┘
                           │
            ┌──────────────┴──────────────┐
            │                               │
    ┌──────▼───────┐             ┌───────▼──────┐
    │    Manual    │             │  Automatic   │
    │ Debug Mode   │             │   Mode      │
    └──────┬───────┘             └──────┬───────┘
           │                              │
           └──────────┬───────────────────┘
                      │
               ┌──────▼───────┐
               │ Emergency   │
               │    Stop     │
               │    Mode     │
               └──────────────┘
```

---

## 5. Precautions

1. **Safety First**: Ensure personnel safety during any mode switching
2. **Sequential Execution**: Must follow switching steps in sequence, do not skip steps
3. **Status Confirmation**: Confirm current status meets switching conditions before switching
4. **Exception Handling**: Stop immediately and report if exception occurs during switching

---

## 6. Load and Mode Reference Table

| Mode | Load Range | Description |
|------|-----------|-------------|
| Shutdown Mode | 0% | Completely powered off |
| Standby Mode | 5-10% | Hot standby |
| Manual Debug Mode | 0-30% | Low load debugging |
| Automatic Operation Mode | 30-100% | Normal production |
| Emergency Stop Mode | 0% | Immediate stop |

---

**Prepared by**: Equipment Department
**Reviewed by**: Technical Department
**Approved by**: Production Department
