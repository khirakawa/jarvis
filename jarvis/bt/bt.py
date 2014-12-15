#!/usr/bin/python2.7
#Code fixed from http://www.linuxuser.co.uk/tutorials/emulate-a-bluetooth-keyboard-with-the-raspberry-pi

import os
import sys
import bluetooth
from bluetooth import *
import dbus
import time
import evdev
from evdev import *
import json

class Bluetooth:
  P_CTRL = 17
  P_INTR = 19

  HOST = 0
  PORT = 1

  def __init__(self, handler):
    self.handler = handler
    os.system("hciconfig hci0 class " + handler.getClass())
    os.system("hciconfig hci0 name " + handler.getName())
    os.system("hciconfig hci0 piscan")
    self.scontrol = BluetoothSocket(L2CAP)
    self.sinterrupt = BluetoothSocket(L2CAP)
    self.scontrol.bind(("", Bluetooth.P_CTRL))
    self.sinterrupt.bind(("", Bluetooth.P_INTR))
    self.bus = dbus.SystemBus()

    self.manager = dbus.Interface(self.bus.get_object("org.bluez", "/"), "org.bluez.Manager")
    adapter_path = self.manager.DefaultAdapter()
    self.service = dbus.Interface(self.bus.get_object("org.bluez", adapter_path), "org.bluez.Service")

    with open(sys.path[0] + handler.getSdpRecordPath(), "r") as fh:
      self.service_record = fh.read()

  def listen(self):
    self.service_handle = self.service.AddRecord(self.service_record)
    print "Service record added"
    self.scontrol.listen(1) # Limit of 1 connection
    self.sinterrupt.listen(1)
    print "Waiting for a connection"
    self.ccontrol, self.cinfo = self.scontrol.accept()
    print "Got a connection on the control channel from " + self.cinfo[Bluetooth.HOST]
    self.cinterrupt, self.cinfo = self.sinterrupt.accept()
    print "Got a connection on the interrupt channel fro " + self.cinfo[Bluetooth.HOST]

  def send_input(self, ir):
    #  Convert the hex array to a string
    hex_str = ""
    for element in ir:
      if type(element) is list:
        # This is our bit array - convrt it to a single byte represented
        # as a char
        bin_str = ""
        for bit in element:
          bin_str += str(bit)
        hex_str += chr(int(bin_str, 2))
      else:
        # This is a hex value - we can convert it straight to a char
        hex_str += chr(element)
    # Send an input report
    self.cinterrupt.send(hex_str)

  def send(self, message):
    parsedJson = json.loads(message)
    report = self.handler.getReport(parsedJson)
    if report:
      self.send_input(report)
