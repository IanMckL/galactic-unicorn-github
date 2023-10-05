# Galactic Github
![image](./gg_logo.png)

## A galactic gallery of your cosmic contributions
Galactic github is a micropython plugin for the Pimoroni Galactic Unicorn LED matrix.
It displays your github contributions.

![image](./gg_example.png)

## Requirements
1. [Pico W Smart LED Matrix – Galactic Unicorn (53x11 – 583 pixels)](https://shop.pimoroni.com/products/space-unicorns?variant=40842033561683)
2. A github account
3. A github personal access token
4. 2.4GHz WiFi connection

## Installation
1. Clone this repository
2. Open the ```main.py``` file in your IDE of choice. Find the following parameters and replace them with your own information:
    * ```GITHUB_USERNAME```  <-- Github account  github username
    * ```GITHUB_TOKEN``` <-- Github personal access token
    * ```WIFI_SSID``` <-- 2.4GHz WiFi SSID
    * ```WIFI_PASSWORD``` <--2.4GHz WiFi password
3. Connect to the Galactic Unicorn's onboard Raspberry Pi Pico W via USB
4. Copy ```main.py``` into the root directory of the Pico W.

## Usage
1. Connect Pico W to power 
2. Wait for the Pico W to connect to WiFi and fetch your github contributions
3. Voila! You should see your github contributions displayed on the Galactic Unicorn LED matrix.

## Troubleshooting
Connect to the Pico W via USB and view the console output 

## Known Issues

### Pico W Connection Issues
The onboard wifi can be a bit finicky. If you're having trouble connecting, try unplugging and waiting a few minutes before attempting again. Socket memory leaks in the ```urequests``` package is a known issue. 

#### Resolution:
1. Connect Pico W to Thonny and reset by typing machine.reset() in the REPL console.
2. Unplug Pico W and wait a few minutes before attempting to connect again.

## Future Improvements
 - [x] Ping github API every 60 seconds to update contributions. Currently unavailable due to memory leaks in the ```urequests``` package's json parser.
 - [ ] Persistent state storage
 - [ ] Play a sound and display celebratory message when new contributions are detected
 - [ ] Create a 3D printed stand and wall mount for the Galactic Unicorn

