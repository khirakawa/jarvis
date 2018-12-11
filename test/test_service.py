import dbus

with open(sys.path[0] + handler.getSdpRecordPath(), "r") as fh:
  self.service_record = fh.read()

bus = dbus.SystemBus()
manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")

opts = {
  "AutoConnect" :	True,
  "Service":
}
