import bma423
import time

class Accelerometer:
    def __init__(self, i2c):
        self.offset = 0

        # Setup accelerometer / step counter
        try:
            self.bma = bma423.BMA423(i2c)
            self.bma.accel_enable = 1
            print("ACCEL: Enabled", self.bma.accel_enable)

            time.sleep_ms(10) # Required to allow feature registers to write

            self.bma.accel_range = 2  # 2G

            self.bma.step_dedect_enabled = 1
            self.bma.feature_enable('step_cntr')

            # NOTE: BMA driver should output it's features register, this is what good output looks like:
            # BMA423: Features: aa0005002d01d47b3b01db7a04003f7bcd6cc3048509c304ece60c460100270019009600a00001000c00f03c00010100030001000e0000180600010043288101

            time.sleep_ms(10) # Allow features to turn on
            print("ACCEL: Step detect status=", self.bma.step_dedect_enabled)

            print("ACCEL: Axes remap:", hex(self.bma.axes_remap))
            self.bma.axes_remap = [1, 0, 0, 0, 2, 1] # Swap X and Y, invert Z, Page 38 of datasheet
            print("ACCEL: Axes remap after swapping/inverting:", hex(self.bma.axes_remap))
            self.bma.feature_enable('tilt')

            # Map interrupts
            self.bma.map_int(0, bma423.BMA423_STEP_CNTR_INT)
            # self.bma.map_int(1, bma423.BMA423_TILT_INT)
            # self.bma.map_int(1, bma423.BMA423_STEP_CNTR_INT)

            # Ensure step watermark is always 1
            print("ACCEL: Step detect watermark=", self.bma.step_watermark)
            if self.bma.step_watermark != 1:
                self.bma.step_watermark = 1
            print("ACCEL: Step detect watermark=", self.bma.step_watermark)                  

            err = self.bma.error_status
            print("ACCEL: Error status:", hex(err))
            if err > 0x00:
                print("ACCEL: Error detected!")

        except Exception as e:
            print("ACCEL: Unable to initialize accelerometer", e)

    def reset_steps(self):
        self.offset += self.bma.step_count

    def step_count(self):
        return self.bma.step_count - self.offset

    def tilted(self):
        xyz = self.bma.read_accel()
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
        # print(f"x,y,z: {x},{y},{z}")
        # print("In range: x {} y {} z {}".format(x in range(-400,-800), y in range(-400, 400), z in range(-900,-600)))
        if x in range(-800,-400) and y in range(-400, 400) and z in range(-900, -600):
            print("TILTED!")
            return True
        return False
