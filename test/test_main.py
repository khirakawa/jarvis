#!/usr/bin/python2.7

import os
import sys
import bluetooth
from bluetooth import *
import dbus
import time
import evdev
from evdev import *
import keymap


class Bluetooth:
    HOST = "<REMOTEMACHINEMAC>" #<PIMAC>
    #HOST = 0
    PORT = 1

    # Define the ports we'll use
    P_CTRL = 17
    P_INTR = 19

    def __init__(self):
        os.system("hciconfig hci0 class 0x002540")
        os.system("hciconfig hci0 name Jarvis\ Keyboard v2")
        os.system("hciconfig hci0 piscan")

        # Define our two server sockets for communication
        self.scontrol = BluetoothSocket(L2CAP)
        self.sinterrupt = BluetoothSocket(L2CAP)

        # Bind these sockets to a port
        self.scontrol.bind(("", Bluetooth.P_CTRL))
        self.sinterrupt.bind(("", Bluetooth.P_INTR))

        # Set up dbus for advertising the service record
        self.bus = dbus.SystemBus()

        # Set up dbus for advertising the service record
        try:
            self.objManager = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                                          "org.freedesktop.DBus.ObjectManager")
            #print self.manager.GetManagedObjects()["/org/bluez/hci0"]
            self.manager = dbus.Interface(self.bus.get_object("org.bluez", "/org/bluez"),
                                          "org.bluez.ProfileManager1")
            self.hci_props = dbus.Interface(self.bus.get_object("org.bluez", "/org/bluez/hci0"),
                                                                    "org.freedesktop.DBus.Properties")
        except:
            print sys.exc_info()
            sys.exit("[FATAL] Could not set up Bluez5")

        # Read the service record from file
        try:
            fh = open(sys.path[0] + "/sdp_record.xml", "r")
        except:
            sys.exit("[Bluetooth - L.56] Could not open the sdp record. Exiting...")
        self.service_record = fh.read()
        fh.close()
        try:
            opts = { "AutoConnect": 1, "ServiceRecord": self.service_record }

            uuidarray = self.hci_props.Get("org.bluez.Adapter1", "UUIDs")
            for uuids in uuidarray:
                try:
                    self.manager.RegisterProfile("/org/bluez/hci0", uuids, opts)
                except:
                    print uuids

            print "Service Record saved!"
        except:
            print "Service Records saved. Probably already exists"
            #print sys.exc_info()
            #sys.exit("Error updating service record")

        print "Update class again"
        #os.system("hciconfig hci0 class 0x002540")
        #os.system("hciconfig hci0 name Raspberry\ Pi")


    def listen(self):
        # Advertise our service record
        #self.service_handle = self.service.AddRecord(self.service_record)
        #print "[Bluetooth - L.63] Service record added"

        # Start listening on the server sockets
        self.scontrol.listen(1) # Limit of 1 connection
        self.sinterrupt.listen(1)
        print "[Bluetooth - L.68] Waiting for a connection"
        self.ccontrol, self.cinfo = self.scontrol.accept()
        print "[Bluetooth - L.70] Got a connection on the control channel from " + self.cinfo[Bluetooth.HOST]
        self.cinterrupt, self.cinfo = self.sinterrupt.accept()
        print "[Bluetooth - L.72] Got a connection on the interrupt channel from " + self.cinfo[Bluetooth.HOST]

    def python_to_data(self, data):
        if isinstance(data, str):
            data = dbus.String(data)
        elif isinstance(data, bool):
            data = dbus.Boolean(data)
        elif isinstance(data, int):
            data = dbus.Int64(data)
        elif isinstance(data, float):
            data = dbus.Double(data)
        elif isinstance(data, list):
            data = dbus.Array([self.python_to_data(value) for value in data], signature='v')
        elif isinstance(data, dict):
            data = dbus.Dictionary(data, signature='sv')
            for key in data.keys():
                data[key] = self.python_to_data(data[key])
        return data

class Keyboard():
    def __init__(self):
        # The structure for an bt keyboard input report (size is 10 bytes)
        self.state = [
               0xA1, # This is an input report
               0x01, # Usage report = Keyboard
               # Bit array for Modifier keys (D7 being the first element, D0 being last)
               [0,   # Right GUI - (usually the Windows key)
                0,   # Right ALT
                0,   # Right Shift
                0,   # Right Control
                0,   # Left GUI - (again, usually the Windows key)
                0,   # Left ALT
                0,   # Left Shift
                0],  # Left Control
               0x00, # Vendor reserved
               0x00, # Rest is space for 6 keys
               0x00,
               0x00,
               0x00,
               0x00,
               0x00 ]

        # Keep trying to get a keyboard
        have_dev = False
        while have_dev == False:
            try:
                # Try and get a keyboard - should always be event0 as we're only
                # plugging one thing in
                self.dev = InputDevice("/dev/input/event0")
                have_dev = True
            except OSError:
                print "[Keyboard - L.124] - Keyboard not found, waiting 3 seconds and retrying"
                time.sleep(3)

        print "[Keyboard - L.127]Found a keyboard"

    def change_state(self, event):
        evdev_code = ecodes.KEY[event.code]
        modkey_element = keymap.modkey(evdev_code)
        if modkey_element > 0:
            # Need to set one of the modifier bits
            if self.state[2][modkey_element] == 0:
                self.state[2][modkey_element] = 1
            else:
                self.state[2][modkey_element] = 0
        else:
            # Get the hex keycode of the key
            hex_key = keymap.convert(ecodes.KEY[event.code])
            # Loop through elements 4 to 9 of the input report structure
            for i in range (4, 10):
                if self.state[i] == hex_key and event.value == 0:
                    # Code is 0 so we need to depress it
                    self.state[i] = 0x00
                elif self.state[i] == 0x00 and event.value == 1:
                    # If the current space is empty and the key is being pressed
                    self.state[i] = hex_key
                    break

    def event_loop(self, bt):
        for event in self.dev.read_loop():
            # Only bother if we a key and it's an up or down event
            if event.type == ecodes.EV_KEY and event.value < 2:
                    self.change_state(event)
                    bt.send_input(self.state)

if __name__ == "__main__":
    # We can only run as root
    if not os.geteuid() == 0:
        sys.exit("[FATAL] - Only root can run this script (sudo?)")

    bt = Bluetooth()
    bt.listen()
    kb = Keyboard()
    kb.event_loop(bt)
