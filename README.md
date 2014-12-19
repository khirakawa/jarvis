Jarvis
======

Jarvis helps devs programatically control the Playstation via a Raspberry Pi.  

Potentially useful for:

* Remote control the Playstation for WFH situations.
* Soft controllers
* Test automation


## Setup

### 1. Hardware
You'll first need some hardware:

* [Raspberry Pi](http://www.amazon.com/Raspberry-Complete-Starter-Kit-Model/dp/B00GGM0Y66/ref=sr_1_2?s=electronics&ie=UTF8&qid=1399792409&sr=1-2&keywords=raspberry+pi+kit)
* [Bluetooth dongle](http://www.amazon.com/gp/product/B009ZIILLI/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1)

Instruction for setting up the Raspberry Pi can be found [here](http://www.raspberrypi.org/help/quick-start-guide/).

Plug your Bluetooth dongle into the Pi.

### 2. Bluetooth Setup
Once your Pi is up and running, ssh into the box and run the following commands:

```
sudo apt-get update
sudo apt-get install python-gobject bluez bluez-tools bluez-firmware python-bluez python-dev python-pip
sudo pip install evdev
```

Next, we'll disable some unnecessary Bluetooth plugins. Open `/etc/bluetooth/main.conf` and change:

```
#DisablePlugins = network,input
```

to

```
DisablePlugins = network,input,audio,pnat,sap,serial
```

Restart the Bluetooth service:

```
sudo /etc/init.d/bluetooth restart
```

### 3. Start Jarvis

Clone Jarvis
```
git clone https://github.com/khirakawa/jarvis.git
```

Install dependencies
```
pip install -r requirements.txt
```

Start Jarvis in keyboard mode
```
sudo python jarvis.py
```

### 4. Pair with the Playstation

Go to:

1. Settings
2. Devices
3. Bluetooth Devices

Now wait for `Jarvis Keyboard` to appear in the list.  Once it shows up, pair with it.

### 5. Test it out

Here's a quick way to test out that Jarvis is working correctly via the command line:

```
$ npm install -g ws
$ wscat -c ws://localhost:8888/ws
connected (press CTRL+C to quit)
> {"pressedKeys": ["KEY_PAUSE"]} // PS button
```

If you were successful in navigating back to the content launcher, congrats! Jarvis is ready to kick butt.

## How to use Jarvis

Jarvis runs a web socket server on the Raspberry Pi on port 8888.  Connect to it and send a message in the following format:

`{"pressedKeys": [KEY1, KEY2, KEY3, KEY4, KEY5, KEY6]}`

Where each key is a string.  See `jarvis/keymap.py` for a list of all possible keys.

### Example

Send the word "Hello!" would be:

1. `{"pressedKeys": ["KEY_LEFTSHIFT", "KEY_H"]}`
5. `{"pressedKeys": []}`
2. `{"pressedKeys": ["KEY_E"]}`
5. `{"pressedKeys": []}`
3. `{"pressedKeys": ["KEY_L"]}`
5. `{"pressedKeys": []}`
4. `{"pressedKeys": ["KEY_L"]}`
5. `{"pressedKeys": []}`
5. `{"pressedKeys": ["KEY_O"]}`
5. `{"pressedKeys": []}`
6. `{"pressedKeys": ["KEY_LEFTSHIFT", "KEY_1"]}`
5. `{"pressedKeys": []}`

Send PS Button

1. `{"pressedKeys": ["KEY_PAUSE"]}`
5. `{"pressedKeys": []}`

Send Option Button

1. `{"pressedKeys": ["KEY_SYSRQ"]}`
5. `{"pressedKeys": []}`

Send Share Button

1. `{"pressedKeys": ["KEY_F3"]}`
5. `{"pressedKeys": []}`

## Controller Mappings

- Up - KEY_UP
- Down - KEY_DOWN
- Left - KEY_LEFT
- Right - KEY_RIGHT
- Circle - KEY_ESC
- SQUARE - KEY_F2
- TRIANGLE - KEY_F1
- Cross - KEY_ENTER
- Option - KEY_F3
- Share - KEY_SYSRQ
- PS - KEY_PAUSE

## Limitations

There are some limitations with Jarvis

* Jarvis cannot do anything a Bluetooth keyboard cannot do on the Playstation, including pressing
the L1, L2, L3, R1, R2, R3 buttons.  
* If you logout while paired, your bluetooth connection will be lost.

## Resources

1. http://www.linuxuser.co.uk/tutorials/emulate-a-bluetooth-keyboard-with-the-raspberry-pi
