#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const char* ssid = "GNXS-2.4G-4B45D0";  // Change to your Wi-Fi SSID
const char* password = "200C864B45D0";  // Change to your Wi-Fi password
const char* serverURL = "http://192.168.1.37:7000/data"; // Change to your computer's IP

LiquidCrystal_I2C lcd(0x26, 16, 2); // LCD I2C address is usually 0x27

void setup() {
    Serial.begin(115200);
    lcd.init();
    lcd.backlight();
    
    lcd.setCursor(0, 0);
    lcd.print("Connecting...");
    WiFi.begin(ssid, password);

    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }

    Serial.println("\nConnected to WiFi");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Connected");

    // Print ESP's IP address on LCD
    lcd.setCursor(0, 1);
    lcd.print(WiFi.localIP().toString());
    delay(3000);
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        WiFiClient client;
        HTTPClient http;

        http.begin(client, serverURL);
        int httpCode = http.GET();

        if (httpCode > 0) {
            String payload = http.getString();
            Serial.println("Server Response: " + payload);

            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("N.o Of plates:");
            lcd.setCursor(0, 1);
            lcd.print(payload.substring(0, 16)); // Display first 16 characters
        } else {
            Serial.println("Error fetching data");
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Error fetching");
            lcd.setCursor(0, 1);
            lcd.print("data");
        }

        http.end();
    } else {
        Serial.println("WiFi Disconnected");
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("WiFi Lost");
    }

    delay(1000); // Check for new messages every second
}
