from __future__ import print_function
from __future__ import division
# from builtins import input
from BrickPi.Software.BrickPi_Python.BrickPi import *  # import BrickPi.py file to use BrickPi operations


class Lego_Motor():
    """
    PORT_A : rotating plate
    PORT_B : move up & down
    PORT_C : slide front to rear
    """

    def __init__(self):
        BrickPiSetup()
        BrickPi.MotorEnable[PORT_A] = 1
        BrickPi.MotorEnable[PORT_B] = 1
        BrickPi.MotorEnable[PORT_C] = 1


    def Command_Motor(ports, powers):
        for port, power in zip(ports, powers):
            BrickPi.MotorSpeed[port] = power

    def Update_Time(sec):
        ot = time.time()
        while (time.time() - ot < sec):
            BrickPiUpdateValues()

    def Update_Bool(self):
        def is_run():
            return True

        run = True
        while run:
            BrickPiUpdateValues()
            run = is_run()

    def Move_Up(self):
        self.Command_Motor([PORT_A, PORT_B], [50, 50])
        self.Update_Time(1)
        self.Command_Motor([PORT_A, PORT_B], [-50, -50])
        self.Update_Time(1)

    def Main(self):
        while True:
            self.Command_Motor([PORT_A, PORT_B], [50, 50])
            self.Update_Time(1)
            self.Command_Motor([PORT_A, PORT_B], [-50, -50])
            self.Update_Time(1)


if __name__ == '__main__':
    LM = Lego_Motor()
    LM.Main()
