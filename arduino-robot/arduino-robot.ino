#include <Servo.h>

Servo horizontalServo, verticalServo;

const int horizontalServoPin = 9;  // PWM pin for horizontally rotating servo
const int verticalServoPin = 10;    // PWM pin for vertically rotating servo

int defaultHorizontalAngle = 90;   // Default horizontal angle
int defaultVerticalAngle = 90;     // Default vertical angle

int currentHorizontalAngle = defaultHorizontalAngle; // Current horizontal angle
int currentVerticalAngle = defaultVerticalAngle;     // Current vertical angle

float speed = 0.5; // Default speed (0.0 to 1.0)

void setup() {
  Serial.begin(9600);
  horizontalServo.attach(horizontalServoPin);
  verticalServo.attach(verticalServoPin);
  horizontalServo.write(defaultHorizontalAngle); // Move to default position
  verticalServo.write(defaultVerticalAngle);     // Move to default position
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    parseInput(input);
    
    // Print current status
    Serial.print("currentHorizontalAngle: ");
    Serial.println(currentHorizontalAngle);


    Serial.print("currentVerticalAngle: ");
    Serial.println(currentVerticalAngle);

    // Serial.print("speed: ");
    // Serial.println(speed, 2); // Print speed with 2 decimal places

    // Update the servo positions
    horizontalServo.write(currentHorizontalAngle);
    verticalServo.write(currentVerticalAngle);
  }
}

void parseInput(String input) {
  int commaIndex1 = input.indexOf(',');
  // int commaIndex2 = input.indexOf(',', commaIndex1 + 1);

  // if (commaIndex1 > 0 && commaIndex2 > commaIndex1) {
  if (commaIndex1 > 0) {
    String relativeHorizontalAngleString = input.substring(0, commaIndex1);
    String relativeVerticalAngleString = input.substring(commaIndex1 + 1);
    // String relativeVerticalAngleString = input.substring(commaIndex1 + 1, commaIndex2);
    // String speedString = input.substring(commaIndex2 + 1);

    int relativeHorizontalAngle = relativeHorizontalAngleString.toInt();
    int relativeVerticalAngle = relativeVerticalAngleString.toInt();
    // speed = speedString.toFloat();

    currentHorizontalAngle = constrain(currentHorizontalAngle + relativeHorizontalAngle, 0, 180);
    currentVerticalAngle = constrain(currentVerticalAngle + relativeVerticalAngle, 0, 180);

    // speed = constrain(speed, 0.0, 1.0); // Ensure speed is within 0.0 to 1.0
  }
}
