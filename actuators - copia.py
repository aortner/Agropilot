import RPi.GPIO as GPIO
import time
from pymemcache.client import base
from time import sleep
import threading

class ActuadoresAgropilot:
    def __init__(self):
        self.client = base.Client(('localhost', 11211))
        self.acelerador = 33
        self.kill = 31
        self.fPWM = 50  # Hz (not higher with software PWM)
        self.a = 10.0
        self.b = 2.0
        self.DIR = 35  # Direction GPIO Pin
        self.STEP = 37  # Step GPIO Pin
        self.CW = 1     # Clockwise Rotation
        self.CCW = 0    # Counterclockwise Rotation
        self.SPR = 1600
        self.delay = 60
        self.idelay = 500

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.acelerador, GPIO.OUT)
        self.acelerador_pwm = GPIO.PWM(self.acelerador, self.fPWM)
        self.acelerador_pwm.start(0)
        GPIO.setup(self.kill, GPIO.OUT)
        self.kill_pwm = GPIO.PWM(self.kill, self.fPWM)
        self.kill_pwm.start(0)
        self.client.add('acel', "-1")
        self.client.add('corte', "-1")
        self.client.add('step',"-1")
        self.client.add('dir', "-1")
        GPIO.setup(self.STEP, GPIO.OUT)
        GPIO.setup(self.DIR, GPIO.OUT)
        sleep(1)
        sleep(1)
        t2 = threading.Thread(target=self.runner_child2)
        t2.start()
        

    def setAcelerador(self,direction):
        duty = self.a / 180.0 * float(direction) + self.b
        self.acelerador_pwm.ChangeDutyCycle(duty)


    def cut(self):
        if int(self.client.get('corte'))==0:
            duty = self.a / 180.0 * 0.0 + self.b
            self.kill_pwm.ChangeDutyCycle(duty)
        elif int(self.client.get('corte'))==1:
            duty = self.a / 180.0 * 180.0 + self.b
            kill_pwm.ChangeDutyCycle(duty)

    def crear_giro(self,step,direccion):
        self.client.set('step',str(step))
        self.client.set('dir',str(direccion))
        print("GIRO CREADO")

    def stop(self):
        GPIO.cleanup()

    def runner_child(self):
        while True:
            try:
                self.cut()

                if int(self.client.get('acel')) != -1:
                    self.setAcelerador(int(self.client.get('acel')))
                    self.client.set('acel',"-1")
            except Exception as e:
                print ("Error en servo",repr(e))

    def runner_child2(self):
        while True:
            try:
                if int(self.client.get('step'))>0:
                    print ("GIRO INCIADO",int(self.client.get('dir')),int(self.client.get('step')))
                    GPIO.output(self.DIR, int(self.client.get('dir')))
                    delay2=self.idelay
                    steps=self.client.get('step')
                    for x in range(int(self.client.get('step'))):
                        if delay2>self.delay: 
                            delay2-=1
                        GPIO.output(self.STEP, GPIO.HIGH)
                        sleep(delay2/10000000)
                        GPIO.output(self.STEP, GPIO.LOW)
                        sleep(delay2/10000000)
                    self.client.set('dir',"0")
                    self.client.set('step',"0")
                    print ("GIRO END",int(self.client.get('dir')),int(self.client.get('step')))
            except Exception as e:
                print ("Error en Motor",repr(e))


