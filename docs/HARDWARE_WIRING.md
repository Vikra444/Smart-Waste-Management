# Hardware Wiring Guide — NEUROX Smart Bin Node

## Components Required (Per Bin Node)

| Component                                 | Quantity | Purpose                       |
| ----------------------------------------- | -------- | ----------------------------- |
| ESP32 Dev Module (38-pin)                 | 1        | Main microcontroller + WiFi |
| HC-SR04 Ultrasonic Sensor                 | 1        | Bin fill level measurement    |
| DHT11 Temperature/Humidity Sensor         | 1        | Environmental monitoring      |
| MQ-2 / MQ-4 Gas Sensor                    | 1        | Methane / smoke / gas detection |
| 18650 Li-Ion Battery + Holder             | 1        | Power supply                  |
| TP4056 Charging Module                    | 1        | Battery management + charging |
| 10kΩ Resistor                             | 3        | Pull-down / voltage divider   |
| 470Ω Resistor                             | 1        | Current limiting              |
| Breadboard / PCB                          | 1        | Circuit assembly              |
| Jumper Wires                              | —        | Connections                   |
| USB-to-Serial Adapter                     | 1        | Firmware flashing             |

---

## Pin Mapping

```
                    ESP32 Dev Module
                  ┌─────────────────┐
              3V3 │ 1           38  │ GND
               EN │ 2           37  │ GND
    [VP] ADC1_0  │ 3 ──────────── 36 │ GPIO23
    [VN] ADC1_3  │ 4           35  │ GPIO22
   GPIO34 ADC1_6 │ 5 ←─ BAT    34  │ GPIO1 (TX0)
   GPIO35 ADC1_7 │ 6 ←─ BAT    33  │ GPIO3 (RX0)
   GPIO32 ADC1_4 │ 7           32  │ GPIO21
   GPIO33 ADC1_5 │ 8           31  │ GND
   GPIO25 DAC1   │ 9           30  │ GPIO19
   GPIO26 DAC2   │ 10          29  │ GPIO18
   GPIO27 TOUCH7 │ 11          28  │ GPIO5
   GPIO14 TOUCH6 │ 12 ──► TRIG 27  │ GPIO17
   GPIO12 TOUCH5 │ 13 ◄── DHT  26  │ GPIO16
         GND     │ 14          25  │ GPIO4
   GPIO13 TOUCH4 │ 15          24  │ GPIO0
         NC      │ 16          23  │ GPIO2
         SD2     │ 17          22  │ GPIO15 ECHO ──►│
         SD3     │ 18          21  │ GPIO8
         CMD     │ 19          20  │ GPIO7
              5V │ 20          19  │ GPIO6
                  └─────────────────┘

  GPIO34 ◄─── MQ Gas Sensor (AOUT)
  GPIO35 ◄─── Battery Voltage Divider
  GPIO14 ───► HC-SR04 TRIG
  GPIO15 ◄─── HC-SR04 ECHO
  GPIO12 ◄─── DHT11 DATA
```

---

## Wiring Diagram

### 1. HC-SR04 Ultrasonic Sensor (Fill Level)

```
HC-SR04          ESP32
─────────        ─────────────
VCC    ──────► 5V (or 3.3V)
GND    ──────► GND
TRIG   ──────► GPIO 14
ECHO   ──────► GPIO 15
```

> **Note:** HC-SR04 outputs 5V on ECHO. Use a **voltage divider** (1kΩ + 2kΩ) to bring it to 3.3V safe for ESP32:
> ```
> ECHO ──[ 1kΩ ]──── GPIO15
>                │
>              [2kΩ]
>                │
>               GND
> ```

### 2. DHT11 Temperature & Humidity

```
DHT11            ESP32
─────────        ─────────────
Pin 1 (VCC) ──► 3.3V
Pin 2 (DATA) ──► GPIO 12  (with 10kΩ pull-up to 3.3V)
Pin 3 (NC)  ──  (not connected)
Pin 4 (GND) ──► GND

Pull-up:
GPIO12 ──[ 10kΩ ]──► 3.3V
```

### 3. MQ-2 / MQ-4 Gas Sensor

```
MQ Gas Sensor    ESP32
─────────────    ─────────────
VCC  ──────────► 5V
GND  ──────────► GND
AOUT ──────────► GPIO 34 (ADC1_6) — Analog output
DOUT ──────────  (optional digital threshold, not used)
```

> Gas sensor needs **warm-up time** of ~30 seconds after power-on for stable readings.

### 4. Battery & Power Circuit

```
18650 Battery
     (+) ──► TP4056 B+
     (-) ──► TP4056 B-

TP4056 Output:
     OUT+ ──► ESP32 VIN / 5V pin
     OUT- ──► GND

Battery Voltage Monitoring (Voltage Divider):
Battery(+) ──[ 100kΩ ]──┬──► GPIO 35
                         │
                       [100kΩ]
                         │
                        GND

Battery % Mapping in Firmware:
  ADC 1860 → 0%
  ADC 2600 → 100%
```

---

## Mounting Inside Bin

```
┌────────────────────────────────┐
│         Bin Lid / Top          │
│                                │
│   [HC-SR04] ← Faces downward  │
│      ↓ ↓ (ultrasonic beam)    │
│                                │
│   [MQ Sensor] ← Inside wall   │
│   [DHT11]    ← Inside wall    │
│                                │
│   [ESP32] ← PCB/breadboard    │
│   [Battery] ← Side or bottom  │
│                                │
│         Bin Waste              │
│                                │
└────────────────────────────────┘
```

**Mounting Notes:**
- HC-SR04 must face **straight down** at the center of the bin lid
- Ensure HC-SR04 beam is not blocked — mount to avoid sidewalls
- DHT11 and MQ sensor should be inside the bin but **above the waste level** — usually at 70–80% height from bottom
- Keep ESP32 and battery outside or in a sealed side compartment (waterproof enclosure recommended)

---

## Fill Level Calculation

The HC-SR04 measures **distance from sensor to waste surface**.

```
BIN_HEIGHT_CM = 30  (total inner bin depth)

fill_level = 100 - ((distance / BIN_HEIGHT_CM) * 100)
fill_level = constrain(fill_level, 0, 100)

Example:
  distance = 10cm → fill = 100 - (10/30 * 100) = 67%
  distance = 28cm → fill = 100 - (28/30 * 100) = 7%
  distance = 0cm  → fill = 100% (full)
```

If the sensor returns no echo (`duration == 0`), `fill_level = -1` is sent to the server, which ignores it to prevent false full readings.

---

## Power Consumption (Estimated)

| State | Current Draw |
|-------|-------------|
| ESP32 Active (WiFi TX) | ~240 mA |
| ESP32 Active (WiFi Idle) | ~80 mA |
| DHT11 Reading | ~2.5 mA |
| HC-SR04 Active | ~15 mA |
| MQ Sensor (Heater ON) | ~150 mA |
| **Total Avg (cycle)** | **~200–280 mA** |

**Battery Life Estimate:**
- 3000 mAh 18650 × 1 cell → ~10–15 hours continuous
- For outdoor deployment: use solar panel + TP4056 charging circuit

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Fill level stuck at 100% | HC-SR04 no echo | Check wiring, voltage divider, sensor placement |
| DHT Sensor Error in Serial | Bad wiring or missing pull-up | Add 10kΩ pull-up resistor to DATA pin |
| Gas always 0 | Sensor cold / wrong pin | Wait 30s warm-up; verify AOUT → GPIO34 |
| WiFi won't connect | Wrong SSID/password | Check 2.4GHz band (ESP32 doesn't support 5GHz) |
| HTTP fails (code -1) | Wrong server IP | Verify server IP and port 8000 is accessible |
| OTA not working | Different network | Both laptop and ESP32 must be on same WiFi |
| Battery reads 0% | ADC calibration off | Adjust `1860`/`2600` ADC map values in firmware |
