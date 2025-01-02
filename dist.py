from gpiozero import DistanceSensor
from time import sleep

# Initialize the ultrasonic sensor with the appropriate GPIO pins
ultrasonic = DistanceSensor(echo=17, trigger=4)

# Continuously print the distance
while True:
    print(f"Distance: {ultrasonic.distance * 100:.2f} cm")  # Convert to cm
    sleep(0.1)  # Small delay for readability
