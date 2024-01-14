#include <Arduino.h>
#include <ESP32Servo.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

// Create a Servo object
Servo myServo;

// Pin connected to the servo motor signal wire 3-black, 5-purple,15-orange,16-yellow
const int servoPin = 12;
int anglePin = 1;

bool motorAttached = true;
// Servo position limits
const int minAngle = 30;
const int maxAngle = 110;

int pos = minAngle; // Current position of the servo
int increment = 1; // Increment value for position change

const int FSR_PIN1 = 13; //black
const int FSR_PIN2 = 5; //purple
const int FSR_PIN3 = 15; //orange
const int FSR_PIN4 = 16; //yellow
TaskHandle_t Task1;
TaskHandle_t Task2;

uint16_t BNO055_SAMPLERATE_DELAY_MS = 200;
const int motor_delay = 20; 

// Check I2C device address and correct line below (by default address is 0x29 or 0x28)
//                                   id, address
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28, &Wire);

void setup() {
  Serial.begin(115200);
  myServo.attach(servoPin); 
  while (!Serial) delay(10); 

  //Serial.println("Orientation Sensor Test"); Serial.println("");

  /* Initialise the sensor */
  if (!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }

  delay(1000);

  //create a task that will be executed in the Task1code() function, with priority 1 and executed on core 0
  xTaskCreatePinnedToCore(
                    Task1code,   /* Task function. */
                    "Task1",     /* name of task. */
                    10000,       /* Stack size of task */
                    NULL,        /* parameter of the task */
                    1,           /* priority of the task */
                    &Task1,      /* Task handle to keep track of created task */
                    0);          /* pin task to core 0 */                  
  delay(500); 

  //create a task that will be executed in the Task2code() function, with priority 1 and executed on core 1
  xTaskCreatePinnedToCore(
                    Task2code,   /* Task function. */
                    "Task2",     /* name of task. */
                    10000,       /* Stack size of task */
                    NULL,        /* parameter of the task */
                    1,           /* priority of the task */
                    &Task2,      /* Task handle to keep track of created task */
                    1);          /* pin task to core 1 high priority */
    delay(500); 
}


void Task1code( void * pvParameters ){
  //Serial.print("Task1 running on core ");
  //Serial.println(xPortGetCoreID());
  for(;;){
  //Serial.println("motorstart");
  if (motorAttached) {
    pos += increment; // Update the position

    if (pos >= maxAngle || pos <= minAngle) {
      increment *= -1; // Reverse the increment to change direction
    }
    myServo.write(pos); // Set the new position of the servo
    }
     delay(motor_delay);
  //   if (Serial.available() > 0) {
  //   char command = Serial.read();
  //   if (command == 'd') {
  //     Serial.print("Received d");
  //     detach_motor();
  //   }
  // }
  }


}


//Task2code: blinks an LED every 700 ms
void Task2code( void * pvParameters ){
  //Serial.print("Task2 running on core ");
  //Serial.println(xPortGetCoreID());

  for(;;){
  unsigned long currentMillis = millis();

  int fsr1 = analogRead(FSR_PIN1);
  int fsr2 = analogRead(FSR_PIN2);
  int fsr3 = analogRead(FSR_PIN3);
  int fsr4 = analogRead(FSR_PIN4);
  int angle = analogRead(anglePin);

  Serial.print(currentMillis);
  Serial.print(",");
  Serial.print(fsr1);
  Serial.print(",");
  Serial.print(fsr2);
  Serial.print(",");
  Serial.print(fsr3);
  Serial.print(",");
  Serial.print(fsr4);
  Serial.print(",");
  Serial.print(angle);
  Serial.print(",");
  
  sensors_event_t orientationData , angVelocityData , linearAccelData, magnetometerData, accelerometerData, gravityData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  bno.getEvent(&angVelocityData, Adafruit_BNO055::VECTOR_GYROSCOPE);
  bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
  bno.getEvent(&magnetometerData, Adafruit_BNO055::VECTOR_MAGNETOMETER);
  bno.getEvent(&accelerometerData, Adafruit_BNO055::VECTOR_ACCELEROMETER);
  bno.getEvent(&gravityData, Adafruit_BNO055::VECTOR_GRAVITY);

  printEvent(&linearAccelData);
  printEvent(&angVelocityData);
  printEvent(&orientationData);
  // printEvent(&magnetometerData);
  printEvent(&accelerometerData);
  // printEvent(&gravityData);

  // int8_t boardTemp = bno.getTemp();
  // Serial.println();
  // Serial.print(F("temperature: "));
  // Serial.println(boardTemp);

  uint8_t system, gyro, accel, mag = 0;
  bno.getCalibration(&system, &gyro, &accel, &mag);
  // Serial.println();
  // Serial.print("Calibration: Sys=");
  // Serial.print(system);
  // Serial.print(" Gyro=");
  // Serial.print(gyro);
  // Serial.print(" Accel=");
  // Serial.print(accel);
  // Serial.print(" Mag=");
  // Serial.println(mag);

  Serial.println();
  delay(BNO055_SAMPLERATE_DELAY_MS);
}
}


void printEvent(sensors_event_t* event) {
  double x = -1000000, y = -1000000 , z = -1000000; //dumb values, easy to spot problem
  if (event->type == SENSOR_TYPE_ACCELEROMETER) {
    //Serial.print("Accl:");
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  }
  else if (event->type == SENSOR_TYPE_ORIENTATION) {
   // Serial.print("Orient:");
    x = event->orientation.x;
    y = event->orientation.y;
    z = event->orientation.z;
    if(x == 0.0){
      //Serial.print("Connecting...");
    bno.begin();
  }
  }
  else if (event->type == SENSOR_TYPE_MAGNETIC_FIELD) {
    //Serial.print("Mag:");
    x = event->magnetic.x;
    y = event->magnetic.y;
    z = event->magnetic.z;
  }

  else if (event->type == SENSOR_TYPE_ROTATION_VECTOR) {
   // Serial.print("Rot:");
    x = event->gyro.x;
    y = event->gyro.y;
    z = event->gyro.z;
  }
  else if (event->type == SENSOR_TYPE_LINEAR_ACCELERATION) {
    //Serial.print("Linear:");
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  }
  else if (event->type == SENSOR_TYPE_GRAVITY) {
    //Serial.print("Gravity:");
    x = event->acceleration.x;
    y = event->acceleration.y;
    z = event->acceleration.z;
  }

  else if (event->type == SENSOR_TYPE_GYROSCOPE) {
    //Serial.print("Gyro:");
    x = event->gyro.x;
    y = event->gyro.y;
    z = event->gyro.z;
  }
  else {
    Serial.print("Unk:");
  }
  
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.print(z);
  if (event->type == SENSOR_TYPE_LINEAR_ACCELERATION)
  {
    Serial.print(",");
  }
    if (event->type == SENSOR_TYPE_GYROSCOPE)
  {
    Serial.print(",");
  }
      if (event->type == SENSOR_TYPE_ORIENTATION)
  {
    Serial.print(",");
  }
  }

  void loop()
{
  // Check for serial input to detach and attach the motor
  if (Serial.available() > 0)
  {
    char command = Serial.read();
    if (command == 'd')
    {
      detach_motor();
    }
    
    if (command == 'a')
    {
      attach_motor();
    }

  }
}

void detach_motor() {
  myServo.detach();
  motorAttached = false;
}

void attach_motor() {
  
  motorAttached = true;
  myServo.attach(servoPin);

}
