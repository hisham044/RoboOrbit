
# arduino_controller.py
import smbus2

class ArduinoController:
    def __init__(self, bus_number=1, arduino_address=0x08):
        self.bus = smbus2.SMBus(bus_number)
        self.arduino_address = arduino_address
        self.command_dict = {
            'stop': 0,
            'move_forward': 1,
            'move_left': 2,
            'move_right': 3,
            'move_backward': 4,
            'camera_up': 5,
            'camera_down': 6,
            'open_delivery': 7,
            'close_delivery': 8,
            'increase_speed': 9,
            'decrease_speed': 10
        }

    def send_command(self, command):
        try:
            cmd_value = self.command_dict.get(command, 0)
            self.bus.write_byte(self.arduino_address, cmd_value)
            print(f"Command {command} sent to Arduino.")
            return True
        except Exception as e:
            print(f"Error sending command to Arduino: {e}")
            return False
