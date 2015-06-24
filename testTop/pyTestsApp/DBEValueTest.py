#!/usr/bin/env python
import os
import unittest
import epics
import IOCControl
import GatewayControl
import gwtests
import time

class DBEValueTest(unittest.TestCase):
    '''Test value updates (client using DBE_VALUE flag) through the Gateway'''

    def setUp(self):
        self.iocControl = IOCControl.IOCControl()
        self.gatewayControl = GatewayControl.GatewayControl()
        self.iocControl.startIOC()
        self.gatewayControl.startGateway()
        os.environ["EPICS_CA_AUTO_ADDR_LIST"] = "NO"
        os.environ["EPICS_CA_ADDR_LIST"] = "localhost:{} localhost:{}".format(gwtests.iocPort,gwtests.gwPort)
        epics.ca.initialize_libca()
        self.eventsReceived = 0

    def tearDown(self):
        epics.ca.finalize_libca()
        self.gatewayControl.stop()
        self.iocControl.stop()
        
    def onChange(self, pvname=None, **kws):
        self.eventsReceived += 1
        if gwtests.verbose:
            print pvname, " changed to ", kws['value']
        
    def testValueNoDeadband(self):
        '''DBE_VALUE monitor on an ai - value changes generate events.'''
        # gateway:passive0 is a blank ai record
        pv = epics.PV("gateway:passive0", auto_monitor=epics.dbr.DBE_VALUE)
        pv.add_callback(self.onChange)
        for val in range(10):
            pv.put(val)
            time.sleep(.001)
        time.sleep(.05)
        # We get 11 events: at connection, then at 10 value changes (puts)
        self.assertTrue(self.eventsReceived == 11, 'events expected: 11; events received: ' + str(self.eventsReceived))
