from cfg import config
from ser import pei_serial

import os
import threading
import signal
import time

class pei_tetra:

        pei_serial = None
        counter = 0
        callerid = 9019999
        call = False
        released = True
        cci = 0

        def __init__(self, logger):
                self.logger = logger
                self.pei_serial = pei_serial(config.get('serial', 'port'), config.get('serial', 'baud'), self.msg, logger)
                self.pei_worker = threading.Thread(target=self.pei_serial.loop)
                self.pei_worker.start()

        def stop(self):
                self.logger.info("Stopping PEI...")
                self.pei_serial.stop = True

        def call_start(self, issi, rpt):
                if str(rpt) != str(config.get('tetra', 'repeater')):
                        if self.released:
                                self.send_serial("AT+CTSDC=0,0,0,1,1,0,1,1,0,0,0")
                                self.send_serial("ATD " + str(config.get('tetra', 'gssi')))
                        else:
                                self.send_serial("AT+CTXD="+str(self.cci)+",0")
                        self.call = True

        def call_end(self):
                time.sleep(1)
                self.send_serial("AT+CUTXC=" + str(self.cci))
                self.call = False

        def send_serial(self, data):
                self.pei_serial.send(data)

        def msg(self, data):
                try:
                        if "+CTXG:" in data and not self.call:
                                # call start
                                os.system("echo O > /tmp/ptt")
                                tmp = data.split(',')
                                self.callerid = int(tmp[len(tmp)-1])
                                self.logger.debug("call start, id: " + str(self.callerid))
                                self.call = True
                                return
                        if "+CDTXC:" in data and self.call:
                                # call stop
                                os.system("echo Z > /tmp/ptt")
                                self.logger.debug("call stop")
                                self.call = False
                                return
                        if "+CTCC:" in data:
                                # cci
                                self.cci = data.split(" ")[1].split(',')[0]
                                self.released = False
                                self.logger.debug("setting CCI to " + str(self.cci))
                                return
                        if "+CTCR:" in data:
                                self.released = True
                                self.call = False
                                self.logger.debug("marking call as released...")
                                return

                except Exception as e:
                        self.logger.warning("Error during PEI validation!")
                        self.logger.warning(str(e))
                        return
                self.logger.debug(data)




if __name__ == '__main__':
        my_pei = pei_tetra()
