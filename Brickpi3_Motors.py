import os, sys, math, glob, re, shutil, time
import brickpi3
import threading
from argparse import ArgumentParser
import logging
import signal

logger = logging.getLogger('LoggingTest')
logger.setLevel(20)
sh = logging.StreamHandler()
logger.addHandler(sh)


class Brickpi3_Motors():
    """
    PORT_B : rotating plate
    PORT_C : move up & down
    PORT_D : slide front to rear
    """
    run = True
    Main_Thread, t_1, t_2 = None, None, None

    def __init__(self):
        print('***** Init {}'.format(__class__.__name__))
        self.BP = brickpi3.BrickPi3()
        self.BP.reset_all()
        self.BP.offset_motor_encoder(self.BP.PORT_B, self.BP.get_motor_encoder(self.BP.PORT_B))
        self.BP.offset_motor_encoder(self.BP.PORT_C, self.BP.get_motor_encoder(self.BP.PORT_C))
        self.BP.offset_motor_encoder(self.BP.PORT_D, self.BP.get_motor_encoder(self.BP.PORT_D))

        logger.log(10, "encoder %6d" % (self.BP.get_motor_encoder(self.BP.PORT_B)))
        logger.log(10, "encoder %6d" % (self.BP.get_motor_encoder(self.BP.PORT_C)))
        logger.log(10, "encoder %6d" % (self.BP.get_motor_encoder(self.BP.PORT_D)))

    def Main(self, cam_index):
        if self.Main_Thread == None:
            self._Catch_KeyboardInterrupt()

        if cam_index == 0:
            [self.t_1, self.t_2] = self._Run_2_Threads(
                [self.move_rotate, self.move_lift],
                [self.BP.PORT_B, self.BP.PORT_C])
        elif cam_index == 2:
            [self.t_1, self.t_2] = self._Run_2_Threads(
                [self.move_rotate, self.move_slide],
                [self.BP.PORT_B, self.BP.PORT_D])
        else:
            raise Exception('***** unexpected cam_index {}'.format(cam_index))

    def _Run_2_Threads(self, methods, ports):
        threads = []
        for method, port in zip(methods, ports):
            logger.log(10, '***** start {}'.format(sys._getframe().f_code.co_name))
            _thread = threading.Thread(target=method, args=(port,))
            # _thread.daemon = True
            _thread.start()
            print('***** thread starts for port no.{}'.format(port))
            # while _thread.is_alive():
            #     _thread.join()
            threads.append(_thread)
        return threads

    def move_rotate(self, port):
        logger.log(10, "encoder %6d" % (self.BP.get_motor_encoder(port)))
        speed = 75  # high tork is needed for small motor at initial movement
        while self.run:
            self.BP.set_motor_power(port, speed)
            logger.log(10, "encoder %6d  speed %6d " % (self.BP.get_motor_encoder(port), speed))
            time.sleep(0.02)
            while speed > 15:
                speed -= 1

    def move_slide(self, port):
        logger.log(10, "encoder %6d" % (self.BP.get_motor_encoder(port)))
        speed = -50  # if speed under 20, cant start because the tork is not enough
        while self.run:
            self.BP.set_motor_power(port, speed)
            logger.log(10, "encoder %6d  speed %6d " % (self.BP.get_motor_encoder(port), speed))
            time.sleep(0.02)
            while speed < -10:
                speed += 1

    def move_lift(self, port):
        speed = 10
        top_deg = 540
        bottom_deg = 5
        # is_lift = True
        while self.run:
            self.BP.set_motor_power(port, speed)
            logger.log(10, "encoder %6d  speed %6d " % (self.BP.get_motor_encoder(port), speed))
            time.sleep(0.2)
            if self.BP.get_motor_encoder(port) >= (top_deg):
                speed = -7
            elif self.BP.get_motor_encoder(port) <= (bottom_deg):
                speed = 10

    def _Catch_KeyboardInterrupt(self):
        def signal_handler(signal, frame):
            print('***** KeyboardInterrupt')
            self.run = False
            self.__del__()

        if self.run:
            signal.signal(signal.SIGINT, signal_handler)


    def __del__(self):
        print('***** BM __del__ called')
        self.run = False
        self.BP.set_motor_power(self.BP.PORT_B, 0)
        self.finalize_motor_pos(self.BP.PORT_C)
        self.finalize_motor_pos(self.BP.PORT_D)
        self.BP.reset_all()
        print('***** {}'.format('BP.reset_all()'))
        # self.t_1.join()
        # self.t_2.join()
        # print('***** threads joined')

    def finalize_motor_pos(self, port):
        def _is_finalized():
            if port == 4:
                return -10 <= self.BP.get_motor_encoder(port) <= 0
            elif port == 8:
                return -10 <= self.BP.get_motor_encoder(port) % 360 <= 0
            else:
                raise Exception('port = {} :arg "port" is not in [3, 4]'.format(port))

        def get_speed():
            if port == 4:
                return -10 if self.BP.get_motor_encoder(port) >= 0 else 10
            elif port == 8:
                return 10 if self.BP.get_motor_encoder(port) >= 0 else -10
            else:
                raise Exception('port = {} :arg "port" is not in [4, 8]'.format(port))

        speed = get_speed()
        logger.log(10, 'port {} encoder {} speed {}'.format(port, self.BP.get_motor_encoder(port), speed))
        while not _is_finalized():
            self.BP.set_motor_power(port, speed)
            logger.log(10, 'port {} encoder {} speed {}'.format(port, self.BP.get_motor_encoder(port), speed))
            speed = get_speed()
        print('***** finalized {}'.format(port))


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument("cam_index", default=0, type=int)
    args = ap.parse_args()
    print('***** use cam_index {}'.format(args.cam_index))

    BM = Brickpi3_Motors()
    BM.Main(args.cam_index)
