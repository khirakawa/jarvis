import keymap
import sys

class Keyboard():
  def getClass(self):
    return "0x002540"

  def getName(self):
    return "Jarvis\ Keyboard"

  def getSdpRecordPath(self):
    return "/jarvis/keyboard/sdp_record.xml"

  def getReport(self, json):
    # The structure for an bt keyboard input report (size is 10 bytes)
    report = [
         0xA1, # This is an input report
         0x01, # Report ID
         # Bit array for Modifier keys
         [0,   # Right GUI - (usually the Windows key)
          0,   # Right ALT
          0,   # Right Shift
          0,   # Right Control
          0,   # Left GUI - (again, usually the Windows key)
          0,   # Left ALT
          0,   # Left Shift
          0],   # Left Control
         0x00,  # Vendor reserved
         0x00,  # Rest is space for 6 keys
         0x00,
         0x00,
         0x00,
         0x00,
         0x00 ]

    # Expects json to be in the form of {"pressedKeys": ["KEY_LEFTSHIFT", "KEY_A"]}
    if 'pressedKeys' not in json.keys():
      return

    pressedKeys = json['pressedKeys']
    startIndexForKeys = 4

    for pressedKey in pressedKeys:
      modkey_element = keymap.modkey(pressedKey)
      if modkey_element > 0:
          report[2][modkey_element] = 1
      else:
        # Get the hex keycode of the key
        hex_key = keymap.convert(pressedKey)
        report[startIndexForKeys] = hex_key
        startIndexForKeys += 1
    return report
