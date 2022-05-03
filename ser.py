import sys
import serial
import time

class pei_serial:

        serial_port = None
        serial_baud = None

        buffer = []

        serial_conn = None

        callback = None

        counter = 0
        stop = False

        init_radio = [  'AT',
                'ATZ',
                'AT+CTOM=0',            # switch to TMO
                'AT+CTSP=1,3,131',      # SDS Type 4
                'AT+CTSP=1,3,130',      # Text Messaging
                'AT+CTSP=2,0,0',        # Voice
                'AT+CTSP=1,2,20',       # SDS Status
                'AT+CTSP=1,3,24',       # SDS Type 4, PID 0 to 127
                'AT+CTSP=1,3,25',       # SDS Type 4, PID 128 to 255
                'AT+CTSP=1,3,3',        # simple GPS
                'AT+CTSP=1,3,10',       # LIP
                'AT+CTSP=1,1,11'        # Group Management
                ]


        def __init__(self, port, baud, callback, logger):
                self.logger = logger
                self.serial_port = port
                self.serial_baud = baud
                self.callback = callback
                self.serial_conn = serial.Serial(port=self.serial_port, baudrate=self.serial_baud)
                self.reset_radio()


        def reset_radio(self):
                self.logger.info("Resetting Radio via PEI...")
                self.buffer = self.init_radio


        def send(self, data):
                self.buffer.append(data)


        def loop(self):
                data = ""
                while True:
                        if self.stop:
                                return
                        if(self.serial_conn.inWaiting() > 0):
                                try:
                                        data = data + self.serial_conn.read(self.serial_conn.inWaiting()).decode('ascii')
                                        if data[len(data)-1:] == '\n':
                                                data = data.replace('\r', '')
                                                data = data.split('\n')
                                                for x in data:
                                                        if x != "":
                                                                self.callback(x)
                                                                self.logger.debug("Serial got: " + x)
                                                data = ""
                                except Exception as e:
                                        self.logger.warning("Could not decode serial PEI message!")
                                        print(str(e))
                        if self.counter > 700:
                                self.buffer.append("AT")
                                self.counter = 0
                        if len(self.buffer)>0:
                                self.logger.debug("Sending serial PEI command: " + self.buffer[0])
                                self.serial_conn.write((self.buffer[0] + '\r\n').encode())
                                if self.buffer[0] == "ATZ":
                                        time.sleep(3)
                                self.buffer.pop(0)
                        self.counter = self.counter + 1
                        time.sleep(0.1)
