/**
  Überschreibt Initialwerte im EEPROM

  Copyright (C) 2022, 3x3cut0r
  Veröffentlicht unter der MIT Lizenz.
*/

/** 
 * Includes
 * LiquidCrystal_I2C.h  -> LiquidCrystal I2C by Frank de Brabander  v1.1.2
 * EEPROM.h             -> EEPROM-Storage by Daniel Porrey          v1.0.1
 */
#include <LiquidCrystal_I2C.h> // LCD Library für 20x4 I2C Display
#include <EEPROM.h> // EEPROM um die Solltemperaturen dauerhaft zu speichern

/** 
 * Minimale Solltemperatur (in Grad Celsius)
 * Default = 43.0
 * 
 * Zulässige Werte = 0.0 - 120.0
 * Bedingung: nominalMinTemp <= nominalMaxTemp
 */
float nominalMinTemp = 43.0;

/** 
 * Maximale Solltemperatur (in Grad Celsius)
 * Default = 55.0
 * 
 * Zulässige Werte = 0.0 - 120.0
 * Bedingung: nominalMaxTemp >= nominalMinTemp
 */
float nominalMaxTemp = 55.0;

/** 
 * Hintergrundbeleuchtung des LCD I2C Displays
 * Default = 1
 * 
 * Zulässige Werte = 0 oder 1
 * 0 = Hintergrundbeleuchtung aus
 * 1 = Hintergrundbeleuchtung an
 */
const int LCD_I2C_BACKLIGHT = 1;

/** 
  ==================================================
  Feste Variablen (bitte nicht ändern!)
  ==================================================
*/

// LCD
LiquidCrystal_I2C lcd(0x27, 20, 4); // I2C_ADDR, LCD_COLUMNS, LCD_LINES

// Temps
const int nominalMinTempAddress = 0; // Speicheradresse (int), im EEPROM der Minimalen Solltemperatur
const int nominalMaxTempAddress = 4; // Speicheradresse (int), im EEPROM der Maximalen Solltemperatur



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
  if (temp > 0 && temp <= 300) {
    return temp;
  } else {
    return 0;
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

void setup() {
  // Init LCD
  lcd.init();
  if (LCD_I2C_BACKLIGHT == 1) {
    lcd.backlight();
  } else {
    lcd.noBacklight();
  }

  // speichere Solltemperatur in EEPROM
  printLCD(0, 0, "write EEPROM:   ....");
  printLCD(2, 0, "Soll (Min):         ");
  printLCD(3, 0, "Soll (Max):         ");
  updateNominalMinTempInEEPROM();
  updateNominalMaxTempInEEPROM();
  delay(2000);

  // lese aus EEPROM
  printLCD(0, 0, "write EEPROM:   DONE");
  float minTemp = getEEPROM(nominalMinTempAddress);
  float maxTemp = getEEPROM(nominalMaxTempAddress);
  int minTempPos = 20 - String(minTemp).length();
  int maxTempPos = 20 - String(maxTemp).length();
  printLCD(2, minTempPos, String(minTemp));
  printLCD(3, maxTempPos, String(maxTemp));
}

void loop() {}