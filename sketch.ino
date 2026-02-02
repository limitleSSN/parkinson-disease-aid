#include <Arduino_Modulino.h>
#include <Arduino_RouterBridge.h>

// Initialize Modulino Modules
ModulinoMovement movement;
ModulinoBuzzer buzzer;
ModulinoKnob knob;
ModulinoThermo thermo;

// Shared variables for Bridge communication
float patient_temp = 0.0;
bool buzzer_on = false;

// --- STEP 1: Define Global Wrapper Functions for Bridge ---
float read_temp() {
  return patient_temp;
}

void control_buzzer(bool state) {
  buzzer_on = state;
}

void setup() {
  // Initialize Modulino hardware
  Modulino.begin();
  movement.begin();
  buzzer.begin();
  knob.begin();
  thermo.begin();
  
  // Initialize RouterBridge communication
  Bridge.begin();

  // Register functions to be accessible from Python
  Bridge.provide("get_temp", read_temp);
  Bridge.provide("set_buzzer", control_buzzer);
}

void loop() {
  // 1. Update Sensors
  movement.update();
  patient_temp = (thermo.getTemperature() * 1.8) + 32; // Convert to Fahrenheit

  // 2. Fall Detection Logic (Movement)
  float x = movement.getX();
  float y = movement.getY();
  float z = movement.getZ();
  float totalAcc = sqrt(x*x + y*y + z*z);

  if (totalAcc > 3.0) {
    buzzer.tone(2000, 500); // Local alert
    Bridge.notify("report_fall", totalAcc); // Remote alert via Bridge
    delay(1000); 
  }

  // 3. Manual Reset/Test (Knob)
  if (knob.isPressed()) {
    buzzer.tone(500, 100);
    Bridge.notify("manual_test", 1);
  }

  // 4. Remote Buzzer Logic (Controlled via Python)
  if (buzzer_on) {
    buzzer.tone(1000, 100);
  } else if (totalAcc <= 3.0) { 
    // Only stop tone if a fall isn't currently being triggered
    buzzer.noTone();
  }

  // 5. Maintenance
  Bridge.update(); // Keep connection alive
  delay(50);       // Balanced delay for responsiveness
}
