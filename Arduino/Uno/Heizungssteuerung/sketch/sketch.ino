/**
  Heizungssteuerung
  mit 4 Zeilen Display
  und Soll-Temperatur-Bedienung

  Copyright (C) 2023, 3x3cut0r

  Veröffentlicht unter der MIT Lizenz.
*/

/** 
 * Includes
 * OneWire.h            -> OneWire by Jim Studt                     v2.3.7
 * DallasTemperature.h  -> DallasTemperature by Miles Burton        v3.9.1
 * LiquidCrystal_I2C.h  -> LiquidCrystal I2C by Frank de Brabander  v1.1.2
 * EEPROM.h             -> EEPROM-Storage by Daniel Porrey          v1.0.1
 */
#include <OneWire.h> // Temperatur Library
#include <DallasTemperature.h> // Temperatur Library für DS18B20
#include <LiquidCrystal_I2C.h> // LCD Library für 20x4 I2C Display
#include <EEPROM.h> // EEPROM um die Solltemperaturen dauerhaft zu speichern

/** 
 * ==================================================
 * Änderbare Variablen
 * ==================================================
 */

/** 
 * 1. Startverzögerung (in Sekunden)
 * die gewartet wird bevor die erste Temperaturanpassung stattfindet
 * Default = 660
 * 
 * Zulässige Werte = 0-65535
 * Maximaler Wert entspricht 18h 12m 15s
 * (wegen Arduino Uno Speicherbegrenzung von 32 bit (unsigned int))
 */
const unsigned int DELAY_BEFORE_START_1 = 660;

/** 
 * 2. Startverzögerung (in Sekunden)
 * die gewartet wird bevor die erste Temperaturanpassung stattfindet
 * Default = 420
 * 
 * Zulässige Werte = 0-65535
 * Maximaler Wert entspricht 18h 12m 15s
 * (wegen Arduino Uno Speicherbegrenzung von 32 bit (unsigned int))
 */
const unsigned int DELAY_BEFORE_START_2 = 420;

/** 
 * Zeit (in Millisekunden)
 * wie lang das Relais beim Einschalten einmalig schaltet
 * Default = 7000
 * 
 * Zulässige Werte = 0-65535
 * Maximaler Wert entspricht 65s 535ms
 * (wegen Arduino Uno Speicherbegrenzung von 32 bit (unsigned int))
 */
const unsigned int INIT_RELAIS_TIME = 7000;

/** 
 * Zeit (in Sekunden)
 * bis zur nächsten Temperaturmessung
 * Default = 120
 * 
 * Zulässige Werte = 0-65535
 * Maximaler Wert entspricht 18h 12m 15s
 * (wegen Arduino Uno Speicherbegrenzung von 32 bit (unsigned int))
 */
const unsigned int UPDATE_TIME = 120; // Sekunden

/** 
 * Zeit (in Millisekunden)
 * wie lang das Relais schaltet
 * Default = 1800
 * 
 * Zulässige Werte = 0-65535
 * Maximaler Wert entspricht 65s 535ms
 * (wegen Arduino Uno Speicherbegrenzung von 32 bit (unsigned int))
 */
const unsigned int RELAIS_TIME = 1800;

/** 
 * Minimale Solltemperatur (in Grad Celsius)
 * Default = 42.0
 * 
 * Zulässige Werte = 0.0 - 120.0
 * Bedingung: nominalMinTemp <= nominalMaxTemp
 */
float nominalMinTemp = 42.0;

/** 
 * Maximale Solltemperatur (in Grad Celsius)
 * Default = 55.0
 * 
 * Zulässige Werte = 0.0 - 120.0
 * Bedingung: nominalMaxTemp >= nominalMinTemp
 */
float nominalMaxTemp = 55.0;

/** 
 * Zeit (in Sekunden)
 * bis die Temperatur erneut aktualisiert werden soll
 * Default = 2
 * 
 * Zulässige Werte = 1 - 60
 */
const unsigned int UPDATE_TEMP_INTERVAL = 2;

/** 
 * Zeit (in Millisekunden)
 * in der eine Temperaturveränderung betrachtet wird
 * Default = 10000
 * 
 * Zulässige Werte = 1000 - 65535
 */
const int TEMP_SAMPLING_INTERVAL = 10000;

/** 
 * Hintergrundbeleuchtung des LCD I2C Displays
 * Default = 1
 * 
 * Zulässige Werte = 0 oder 1
 * 0 = Hintergrundbeleuchtung aus
 * 1 = Hintergrundbeleuchtung an
 */
const unsigned int LCD_I2C_BACKLIGHT = 1;

/**
 * Bit der Sensor-Auflösung
 * Default: 9
 * 
 * Zulässige Werte: 9-12
 * 
 * Bits  Auflösung   Messzeit
 *  9        0,5 °C   93,75 ms
 * 10       0,25 °C  187,50 ms
 * 11      0,125 °C  375,00 ms
 * 12    0,00626 °C  750,00 ms
 */
const unsigned int SENSOR_RESOLUTION_BIT = 9;



/** 
  ==================================================
  Feste Variablen (bitte nicht ändern!)
  ==================================================
*/

// Time
unsigned long previousMillis = 0UL;
unsigned long interval = 1000UL;
unsigned long lastTempMeasurementTime = 0UL; // letzte Temperaturmessung im TEMP_SAMPLING_INTERVAL

// LCD
LiquidCrystal_I2C lcd(0x27, 20, 4); // I2C_ADDR, LCD_COLUMNS, LCD_LINES

// LCD - create new characters
const byte arrowUp[8] = {
  0b00100,
  0b01110,
  0b11111,
  0b00100,
  0b00100,
  0b00100,
  0b00100,
  0b00100
};

const byte arrowDown[8] = {
  0b00100,
  0b00100,
  0b00100,
  0b00100,
  0b00100,
  0b11111,
  0b01110,
  0b00100
};

// Temperatursensor DS18B20
#define ONE_WIRE_BUS 8
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Relais
const int RELAY_OPEN_PIN = 4; // Relais, welches öffnet, wenn es wärmer werden soll
const int RELAY_CLOSE_PIN = 5; // Relais, welches öffnet, wenn es kälter werden soll

// Temps
float currentTemp = 0; // aktuelle Temperatur (in Grad Celsius)
unsigned int updateTime = UPDATE_TIME; // Zeit (in Sekunden), bis zur nächsten Angleichung
int nominalMinTempAddress = 0; // Speicheradresse (int), im EEPROM der Minimalen Solltemperatur
int nominalMaxTempAddress = 4; // Speicheradresse (int), im EEPROM der Maximalen Solltemperatur
float tempAtLastMeasurement = 0; // letzte Temperatur des TEMP_SAMPLING_INTERVALs
enum TempChangeCategory { LOW_TEMP, MEDIUM_TEMP, HIGH_TEMP }; // mögliche Kategorien des letzten Temperaturveränderung
TempChangeCategory tempChangeCat = LOW_TEMP; // Kategorie des letzten TEMP_SAMPLING_INTERVALs

// Temp Thresholds
float tempChangeHighThreshold = 1.0; // gibt hohe Temperaturveränderung des letzten TEMP_SAMPLING_INTERVALs an
// float tempChangeMediumThreshold = 0.3; // gibt niedrigere Temperaturveränderung des letzten TEMP_SAMPLING_INTERVALs an

// Buttons
const int BUTTON_TEMP_UP_PIN = 2; // PIN des Buttons Solltemperatur senken
const int BUTTON_TEMP_DOWN_PIN = 3; // PIN des Buttons Solltemperatur erhöhen
const int BUTTON_TEMP_SWITCH_PIN = 6; // PIN des Buttons Solltemperatur wechseln
const int BUTTON_TEMP_SAVE_PIN = 7; // PIN des Buttons Solltemperatur speichern



/** 
 * ==================================================
 * Funktionen
 * ==================================================
 */

/** 
 * speichert in der übergebenen Adresse (address) einen Wert (value) 
 */
void toEEPROM(int address, float value) {
  EEPROM.put(address, value);
}

/** 
 * liest aus der übergebenen Adresse (address) einen Wert (value) 
 */
float getEEPROM(int address) {
  float temp;
  EEPROM.get(address, temp);
  if (temp > 0 && temp <= 110) {
    return temp;
  } else {
    return 0;
  }
}

/** 
 * liest die minimale Solltemperatur aus dem EEPROM und gibt sie zurück
 */
void readNominalMinTemp() {
  float temp = getEEPROM(nominalMinTempAddress);
  if (temp != 0) {
    nominalMinTemp = temp;
  }
}

/** 
 * liest die maximale Solltemperatur aus dem EEPROM und gibt sie zurück
 */
void readNominalMaxTemp() {
  float temp = getEEPROM(nominalMaxTempAddress);
  if (temp != 0) {
    nominalMaxTemp = temp;
  }
}

/** 
 * aktualisiert die minimale Solltemperatur im EEPROM (falls geändert)
 */
void updateNominalMinTempInEEPROM() {
  toEEPROM(nominalMinTempAddress, nominalMinTemp);
}

/** 
 * aktualisiert die maximale Solltemperatur im EEPROM (falls geändert)
 */
void updateNominalMaxTempInEEPROM() {
  toEEPROM(nominalMaxTempAddress, nominalMaxTemp);
}

/** 
 * druckt (print) den übergebenen text die Zeile (line)
 * an der übergebenen Position (cursor)
 * auf das 4 Zeilen, 20 Zeichen Display
 */
void printLCD(int line, int cursor, String text) {
  lcd.setCursor(cursor, line);
  lcd.print(text);
}

/** 
 * gibt die Kategorie der Temperaturveränderung zurück
 *      >= 1.0 => HIGH
 * 1.0 bis 0.3 => MEDIUM
 * 0.3 bis 0.0 => LOW
 */
TempChangeCategory categorizeTemperatureChange(float tempChange) {
  if (abs(tempChange) >= tempChangeHighThreshold) {
    printLCD(2, 0, "Temperatur      HIGH");
    lcd.setCursor(11, 2);
    lcd.write(byte(tempChange > 0 ? 0 : 1));
    return HIGH_TEMP;
  // } else if (abs(tempChange) >= tempChangeMediumThreshold) {
  //   printLCD(2, 0, "Temperatur    MEDIUM");
  //   lcd.setCursor(11, 2);
  //   lcd.write(byte(tempChange > 0 ? 0 : 1));
  //   return MEDIUM_TEMP;
  } else {
    printLCD(2, 0, "Temperatur       LOW");
    lcd.setCursor(11, 2);
    lcd.write(byte(tempChange > 0 ? 0 : 1));
    return LOW_TEMP;
  }
}

/** 
 * berechnet die relayTime aufgrund der Kategorie der Temperaturänderung
 */
int adjustRelayTimeBasedOnTempCategory(unsigned int relayTime) {
  switch (tempChangeCat) {
    case HIGH_TEMP:
      return relayTime = (unsigned int) (relayTime * 0.5); // Kürzere Öffnungszeit für schnelle Temperaturänderungen
    // case MEDIUM_TEMP:
    //   return relayTime = (unsigned int) (relayTime * 0.75); // Moderate Öffnungszeit
    case LOW_TEMP:
      return relayTime = (unsigned int) (relayTime * 1.0); // Längere Öffnungszeit für langsame Änderungen
  }
}

/** 
 * berechnet die updateTime aufgrund der Kategorie der Temperaturänderung
 */
int adjustUpdateTimeBasedOnTempCategory(unsigned int updateTime) {
  switch (tempChangeCat) {
    case HIGH_TEMP:
      return updateTime = (unsigned int) (updateTime * 0.5); // Temperaturmessung findet sehr oft statt
    // case MEDIUM_TEMP:
    //  return updateTime = (unsigned int) (updateTime * 0.75); // Temperaturmessung findet öfter statt
    case LOW_TEMP:
      return updateTime = (unsigned int) (updateTime * 1.0); // Temperaturmessung findet normal statt
  }
}

/** 
 * liest die Temperatur vom Thermostat und gibt sie als float zurück
 */
float getTemp() {
  sensors.requestTemperatures(); // Send the command for all devices on the bus to perform a temperature conversion:
  float tempC = sensors.getTempCByIndex(0); // the index 0 refers to the first device
  return tempC;
}

/** 
 * aktualisiert die aktuelle Temperatur auf dem Display
 */
void updateTemp() {
  currentTemp = getTemp();
  String currentTempString = String(currentTemp, 1) + " \337C";
  int tempPos = 20 - currentTempString.length();
  printLCD(0, 0, "Aktuell:            ");
  printLCD(0, tempPos, currentTempString);
}

/** 
 * aktualisiert die Solltemperatur auf dem Display
 */
void printNominalTemp() {
  printLCD(1, 0, "Soll:               ");
  if (nominalMinTemp < 0) { nominalMinTemp = 0.0; }
  if (nominalMinTemp > 120.0) { nominalMinTemp = 120.0; }
  if (nominalMaxTemp < 0) { nominalMaxTemp = 0.0; }
  if (nominalMaxTemp > 120.0) { nominalMaxTemp = 120.0; }
  if (nominalMaxTemp < nominalMinTemp) { nominalMaxTemp = nominalMinTemp; }
  String nominalTemp = String(nominalMinTemp, 1) + " - " + String(nominalMaxTemp, 1) + " \337C";
  int tempPos = 20 - nominalTemp.length();
  printLCD(1, tempPos, nominalTemp);
}

/** 
 * schaltet das Relais (relayPin)
 * über die übergebene Zeit (relayTime)
 */
void setRelais(int relayPin, int relayTime) {
  // schalte nur, wenn die Temperatur ausgelesen werden kann
  if (currentTemp >= 0 && currentTemp <= 150) {
    if (relayPin == RELAY_OPEN_PIN) {
      printLCD(3, 0, "\357ffne Ventil     >>>");
    } else if (relayPin == RELAY_CLOSE_PIN) {
      printLCD(3, 0, "schlie\342e Ventil: <<<");
    }
    digitalWrite(relayPin, HIGH);
    delay(relayTime);
    digitalWrite(relayPin, LOW);
  } else {
    printLCD(3, 0, "Fehler: Temp Fehler!");
    delay(RELAIS_TIME);
  } 
}

/** 
 * schaltet das jeweilige Relais abhängig von der Solltemperatur 
 */
void openRelais(int relayTime) {
  if (currentTemp < nominalMinTemp) {
    // erhöhe Temperatur
    setRelais(RELAY_OPEN_PIN, relayTime);
  } else if (currentTemp > nominalMaxTemp) {
    // verringere Temperatur
    setRelais(RELAY_CLOSE_PIN, relayTime);
  } else {
    printLCD(3, 0, "Soll Temp erreicht !");
  }
}

/** 
 * erhöht oder verringert die Solltemperatur
 */
void updateNominalTemp(int buttonPin) {
  int buttonLong = 0;
  float rate = 0.1;
  while (digitalRead(buttonPin) == LOW) {
      if (buttonPin == BUTTON_TEMP_UP_PIN) {
        if (rate >= 3) {
          printLCD(2, 0, "TempUp Pressed   +++");
        } else if (rate >= 0.5) {
          printLCD(2, 0, "TempUp Pressed    ++");
        } else {
          printLCD(2, 0, "TempUp Pressed     +");
        }
        nominalMinTemp = nominalMinTemp + rate;
        nominalMaxTemp = nominalMaxTemp + rate;
      } else if (buttonPin == BUTTON_TEMP_DOWN_PIN) {
        if (rate >= 3) {
          printLCD(2, 0, "TempDown Pressed ---");
        } else if (rate >= 0.5) {
          printLCD(2, 0, "TempDown Pressed  --");
        } else {
          printLCD(2, 0, "TempDown Pressed   -");
        }
        nominalMinTemp = nominalMinTemp - rate;
        nominalMaxTemp = nominalMaxTemp - rate;
      }
      printNominalTemp();
      delay(500);
      buttonLong = buttonLong + 1;
      if (buttonLong == 5) {
        rate = 1;
      } else if (buttonLong == 10) {
        rate = 1; // rate = 5 -> war zu schnell
      }
  }
  // printLCD(2, 0, "                    ");
}

/** 
 * wechselt die Speicheradressen für die Solltemperaturen
 */
void switchNominalTemp(int buttonPin) {
    if (buttonPin == BUTTON_TEMP_SWITCH_PIN && digitalRead(buttonPin) == LOW) {
        nominalMinTempAddress = nominalMinTempAddress + 8; // 0 + 8 = 8
        nominalMaxTempAddress = nominalMaxTempAddress + 8; // 4 + 8 = 12
        if (nominalMinTempAddress > 8) { nominalMinTempAddress = 0; }
        if (nominalMaxTempAddress > 12) { nominalMaxTempAddress = 4; }
        String minTemp = String(nominalMinTempAddress);
        String maxTemp = String(nominalMaxTempAddress);
        int minTempPos = 17 - minTemp.length();
        int maxTempPos = 20 - maxTemp.length();
        printLCD(2, 0, "Switch Pressed      ");
        printLCD(2, minTempPos, minTemp);
        printLCD(2, maxTempPos, maxTemp);
        delay(2000);
    }
}

/** 
 * speichert die Solltemperaturen im EEPROM
 */
void saveNominalTemp(int buttonPin) {
    if (buttonPin == BUTTON_TEMP_SAVE_PIN && digitalRead(buttonPin) == LOW) {
        // update nominalTemp
        updateNominalMinTempInEEPROM();
        updateNominalMaxTempInEEPROM();
        printLCD(2, 0, "Save Temps to EEPROM");
        delay(2000);
    }
}

/** 
 * prüft ob ein TempButton oder SwitchButton gedrückt ist und
 * ändert entsprechend die Solltemperatur oder wechselt die Speicheradressen
 */
void checkButtons() {
  updateNominalTemp(BUTTON_TEMP_UP_PIN);
  updateNominalTemp(BUTTON_TEMP_DOWN_PIN);
  switchNominalTemp(BUTTON_TEMP_SWITCH_PIN);
  saveNominalTemp(BUTTON_TEMP_SAVE_PIN);
}

/** 
 * warte die übergebene Zeit (seconds) vor dem Start
 */
void waitStart(unsigned int secs) {
  int counter = secs;
  while (counter >= 0) {
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis > interval) {

      // prüfe ob Button gedrückt
      checkButtons();

      // aktualisiere Temperatur alle 5 Sekunden
      if (updateTime % UPDATE_TEMP_INTERVAL == 0) {
        updateTemp();
      }

      secs = counter;
      String statusWait = "STARTE IN:          ";
      String time = "";

      // int years = (int) (secs / (60*60*24*365));
      // secs     -= years       * (60*60*24*365);
      // int days  = (int) (secs / (60*60*24));
      // secs     -= days 	      * (60*60*24);
      int hours = (int) (secs / (60*60));
      secs     -= hours       * (60*60);
      int mins  = (int) (secs / (60));
      secs     -= mins        * (60);

      if (hours > 0) { time = time + hours + "h "; }
      time = time + mins  + "m " + secs  + "s"; 

      int empty = 20 - time.length();
      printLCD(3, 0, statusWait);
      printLCD(3, empty, time);

      counter = counter - 1;
      previousMillis = currentMillis;
    }
  }
}

/** 
 * aktualisiert die Uhrzeit des Timers auf dem Display
 */
void updateTimer(unsigned int secs) {
  String statusWait = "WARTE:              ";
  String time = "";

  // int years = (int) (secs / (60*60*24*365));
  // secs     -= years       * (60*60*24*365);
  // int days  = (int) (secs / (60*60*24));
  // secs     -= days 	      * (60*60*24);
  int hours = (int) (secs / (60*60));
  secs     -= hours       * (60*60);
  int mins  = (int) (secs / (60));
  secs     -= mins        * (60);

  if (hours > 0) { time = time + hours + "h "; }
  time = time + mins  + "m " + secs  + "s"; 

  int empty = 20 - time.length();
  printLCD(3, 0, statusWait);
  printLCD(3, empty, time);
}



/** 
 * ==================================================
 * initialisiert alle Bauteile
 * ==================================================
 */
void setup() {

  // Init LCD
  lcd.init();
  if (LCD_I2C_BACKLIGHT == 1) {
    lcd.backlight();
  } else {
    lcd.noBacklight();
  }

  // init special character
  lcd.createChar(0, arrowUp);
  lcd.createChar(1, arrowDown);

  // Init Serial
  Serial.begin(115200);

  // Init Temperatursensor
  sensors.begin();

  // Init Sensor Auflösung
  sensors.setResolution(SENSOR_RESOLUTION_BIT);

  // Init Relais
  digitalWrite(RELAY_OPEN_PIN, LOW);
  pinMode(RELAY_OPEN_PIN, OUTPUT);
  digitalWrite(RELAY_CLOSE_PIN, LOW);
  pinMode(RELAY_CLOSE_PIN, OUTPUT);

  // Init Buttons
  pinMode(BUTTON_TEMP_UP_PIN, INPUT_PULLUP); 
  pinMode(BUTTON_TEMP_DOWN_PIN, INPUT_PULLUP); 
  pinMode(BUTTON_TEMP_SWITCH_PIN, INPUT_PULLUP);
  pinMode(BUTTON_TEMP_SAVE_PIN, INPUT_PULLUP);

  // aktualisiere aktuelle Temperatur
  updateTemp();
  tempAtLastMeasurement = getTemp();

  // setze Solltemperatur
  readNominalMinTemp();
  readNominalMaxTemp();
  printNominalTemp();

  // Startverzögerung
  waitStart(DELAY_BEFORE_START_1); // warte auf Start 1
  setRelais(RELAY_CLOSE_PIN, INIT_RELAIS_TIME); // öffne Ventil initial
  waitStart(DELAY_BEFORE_START_2); // warte auf Start 2

  // öffne Ventil
  openRelais(RELAIS_TIME);
}



/** 
 * ==================================================
 * Schleife des Hauptprogramms
 * ==================================================
 */
void loop() {
  unsigned long currentMillis = millis();

  // Kategorie der Temperaturveränderung ermitteln und setzen
  if (currentMillis - lastTempMeasurementTime >= TEMP_SAMPLING_INTERVAL) {
    float currentTemp = getTemp();
    float tempChange = currentTemp - tempAtLastMeasurement;
    tempChangeCat = categorizeTemperatureChange(tempChange);

    // aktualisiere letzte gemessene Temperatur
    tempAtLastMeasurement = currentTemp;

    // aktualisiere lastTempMeasurementTime
    lastTempMeasurementTime = currentMillis;
  }

  // Hauptprogramm
  if (currentMillis - previousMillis > interval) {
    
    // aktualisiere Timer
    if (updateTime >= 0) {
      updateTimer(updateTime);
      updateTime--;
    }

    // prüfe ob Button gedrückt
    checkButtons();

    // aktualisiere Temperatur alle 2 Sekunden
    if (updateTime % UPDATE_TEMP_INTERVAL == 0) {
      updateTemp();
    }

    if (updateTime == 0) {
      // öffne Ventil
      openRelais(RELAIS_TIME);

      // reset Timer und berücksichtige Temperaturveränderung
      // updateTime = adjustUpdateTimeBasedOnTempCategory(UPDATE_TIME);
      updateTime = UPDATE_TIME;
      if (currentTemp >= 60) {
        updateTime *= 0.5;
      }

      // update nominalTemp
      updateNominalMinTempInEEPROM();
      updateNominalMaxTempInEEPROM();
    }

    // aktualisiere previousMillis
    previousMillis = currentMillis;
  }
}
