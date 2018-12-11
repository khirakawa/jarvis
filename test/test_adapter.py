#!/usr/bin/python

import dbus

SERVICE_NAME = "org.bluez"
OBJECT_IFACE =  "org.freedesktop.DBus.ObjectManager"
ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
DEVICE_IFACE = SERVICE_NAME + ".Device1"
PROPERTIES_IFACE = "org.freedesktop.DBus.Properties"

bus = dbus.SystemBus()
manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
objects = manager.GetManagedObjects()

for path, ifaces in objects.iteritems():
    adapter = ifaces.get(ADAPTER_IFACE)
    if adapter is None:
        continue
    obj = bus.get_object(SERVICE_NAME, path)
    adapter = dbus.Interface(obj, ADAPTER_IFACE)
    print obj
