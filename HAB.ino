#include <SPI.h>
#include <WiFi101.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_BME280.h>
#include <Adafruit_GPS.h>

#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;            // your network key Index number (needed only for WEP)

#define VBATPIN A7
#define GPSSerial Serial1

// Connect to the GPS on the hardware port
Adafruit_GPS GPS(&GPSSerial);

// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences
#define GPSECHO false

Adafruit_BMP280 bmp; // I2C
Adafruit_BME280 bme; // I2C

int status = WL_IDLE_STATUS;

int ledEnablePin = 12;
unsigned long lastBeaconnTime = 0;
const unsigned long beaconInterval = 600L * 500L; // delay between updates, in milliseconds (5 minutes)

int photoPin = 0;
int photoValue;

// Initialize the WiFi client library
WiFiClient client;

// server address:
//char server[] = "hab.nfaschool.org";
IPAddress server(192,168,1,60);

unsigned long lastConnectionTime = 0;            // last time you connected to the server, in milliseconds
const unsigned long postingInterval = 600L * 1000L; // delay between updates, in milliseconds (10 minutes)

void setup() {
  pinMode(ledEnablePin, OUTPUT);
  
  // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ); // 1 Hz update rate
  GPS.sendCommand(PGCMD_ANTENNA);
  delay(1000);
  // Ask for firmware version
  GPSSerial.println(PMTK_Q_RELEASE);
  
  //Configure pins for Adafruit ATWINC1500 Feather
  WiFi.setPins(8,7,4,2);

  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  if (!bmp.begin()) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring!"));
    //while (1);
  }
  else {
    Serial.println(F("Found a valid BMP280 sensor!"));
  }
  if (!bme.begin()) {
    Serial.println(F("Could not find a valid BME280 sensor, check wiring!"));
    //while (1);
  }
  else {
    Serial.println(F("Found a valid BME280 sensor!"));
  }

  /* Default settings from datasheet. */
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */

  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }

  // attempt to connect to WiFi network:
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }
  // you're connected now, so print out the status:
  printWiFiStatus();
}

void loop() {
  // if there's incoming data from the net connection.
  // send it out the serial port.  This is for debugging
  // purposes only:
  while (client.available()) {
    char c = client.read();
    Serial.write(c);
  }

  // if the postingInterval has passed since your last connection,
  // then connect again and send data:
  if (millis() - lastConnectionTime > postingInterval) {
    httpRequest();
  }

  // If the beaconInterval has passed, send W1HLO in Morse Code
  if (millis() - lastBeaconTime > beaconInterval) {
    photoValue = analogRead(photoPin);
    lastBeaconTime = millis();
    // if the photo cell detects that it's dark out, flash W1HLO
    if (photoValue < 500) {
      sendBeacon();
    }
  }

}

// This method flashes W1HLO in Morse Code
void sendBeacon() {
  int dit = 200;
  int dah = 500;
  int space = 200;
  int charSpace = 500;
  // W
  digitalWrite(ledEnablePin, HIGH);
  delay(dit);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(charSpace);
  // 1
  digitalWrite(ledEnablePin, HIGH);
  delay(dit);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(charSpace);
  // H
  digitalWrite(ledEnablePin, HIGH);
  delay(dit);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dit);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dit);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dit);
  digitalWrite(ledEnablePin, LOW);
  delay(charSpace);
  // L
  digitalWrite(ledEnablePin, HIGH);
  delay(dit);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dit);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dit);
  digitalWrite(ledEnablePin, LOW);
  delay(charSpace);
  // O
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(space);
  digitalWrite(ledEnablePin, HIGH);
  delay(dah);
  digitalWrite(ledEnablePin, LOW);
  delay(charSpace);
}

// this method makes a HTTP connection to the server:
void httpRequest() {
  // close any connection before send a new request.
  // This will free the socket on the WiFi shield
  client.stop();

  String getRequest = "";
  long temp1;
  long temp2 = 0;
  long pressure;
  long humidity;
  long GPSalt;
  long GPSlat;
  long GPSlong;
  long GPSspeed;
  float volt1 = analogRead(VBATPIN);
  
  float volt2 = 0.0;
  long rssi = WiFi.RSSI();  
  String clientID = "Dr.G";

  volt1 *= 2;    // we divided by 2, so multiply back
  volt1 *= 3.3;  // Multiply by 3.3V, our reference voltage
  volt1 /= 1024; // convert to voltage

  if (bmp.readTemperature()) {
    temp1 = bmp.readTemperature();
  }
  else if (bme.readTemperature()) {
    temp1 = bme.readTemperature();
  }
  else {
    temp1 = 0;
  }

  if (bmp.readPressure()) {
    pressure = bmp.readPressure();
  }
  else if (bme.readPressure()) {
    pressure = bme.readPressure();
  }
  else {
    pressure = 1031.0;
  }

  if (bme.readHumidity()) {
    humidity = bme.readHumidity();
  }
  else {
    humidity = 0;
  }

  if (GPS.fix) {
      Serial.print("Location: ");
      Serial.print(GPS.latitude, 4); Serial.print(GPS.lat);
      Serial.print(", ");
      Serial.print(GPS.longitude, 4); Serial.println(GPS.lon);
      Serial.print("Speed (knots): "); Serial.println(GPS.speed);
      Serial.print("Angle: "); Serial.println(GPS.angle);
      Serial.print("Altitude: "); Serial.println(GPS.altitude);
      Serial.print("Satellites: "); Serial.println((int)GPS.satellites);
      GPSalt = GPS.altitude;
      GPSlat = GPS.lat;
      GPSlong = GPS.lon;
      GPSspeed = GPS.speed;
    }
    else {
      Serial.println("No GPS fix yet.");
      GPSalt = 0.0;
      GPSlat = 0.0;
      GPSlong = 0.0;
      GPSspeed = 0.0;
    }

  // if there's a successful connection:
  if (client.connect(server, 5001)) {
    Serial.println("connecting...");
    // send the HTTP PUT request:
    getRequest = "GET /postData?clientID=" + clientID + "&temp1=" + String(temp1) + "&temp2=" + String(temp2);
    getRequest = getRequest + "&pressure=" + String(pressure) + "&volt1=" + String(volt1) + "&volt2=" + String(volt2);
    getRequest = getRequest + "&signal=" + String(rssi);
    if (GPSalt != 0.0) {
      getRequest = getRequest + "&alt=" + GPSalt;
    }
    if (GPSlat != 0.0) {
      getRequest = getRequest + "&lat=" + GPSlat;
    }
    if (GPSlong != 0.0) {
      getRequest = getRequest + "&long=" + GPSlong;
    }
    if (humidity != 0) {
      getRequest = getRequest + "&humidity=" + humidity;
    }

    getRequest = getRequest + " HTTP/1.1";
    
    client.println(getRequest);
    client.println("Host: 192.168.1.60");
    client.println("User-Agent: ArduinoWiFi/1.1");
    client.println("Connection: close");
    client.println();

    // note the time that the connection was made:
    lastConnectionTime = millis();
  }
  else {
    // if you couldn't make a connection:
    Serial.println("connection failed");
  }
}


void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
