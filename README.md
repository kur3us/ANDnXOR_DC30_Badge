# AND!XOR DC30 Badge "Chomper"

Please be patient as we add documentation and files for this year's project.

Initial release of python and chomper (micropython) bin file. Provision scripts and our micropython add-ons/source will be available when ready.

## Configure Environment ##

You can do all or none of these :). 

- [ ] `sudo adduser $USER dialout` <-- So we can flash and REPL without sudo
- [ ] `sudo apt remove modemmanager` <-- Breaks serial device permissions
- [ ] `sudo apt install build-essential python3-virtualenv python3-freetype ffmpeg picocom` 
- [ ] `sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1` <-- this makes python3 default (optional)
- [ ] `pip3 install adafruit-ampy mpremote cmake` <-- Required for provisioning

## Get the ESP IDF ##

Our Micropython build was against ESP-IDF v4.2. We were not able to get a successful build with later versions, send a PR if you figure this out.

- [ ] `git clone -b v4.2 --recursive https://github.com/espressif/esp-idf.git`
- [ ] `cd esp-idf`
- [ ] `./install.sh` <-- Get local copy of xtensa build tools
- [ ] Delete EC-ACC cert in `~/dev/esp-idf/components/mbedtls/esp_crt_bundle/cacrt_all.pem` if you get a `gen_crt_bundle.py` error later. This should be temporary error until expired cert is fixed. Another option is to use `idf.py menuconfig` in /boards/CHOMPER, traverse to the mbedTLS options, and instead of entire cert store, tick the box to only use recently issued certificates.

## Provisioning (fancy term for flashing) ##

```
cd provision
./provision.sh /dev/ttyACM0
```

Replace `/dev/ttyACM0` with whatever serial device the watch shows up as. The entire process will take several minutes and requires the following wifi to be within range

```
SSID: Matt Damon
PWD: WEmustSAVEhim
```

Wifi is used to copy the large assets, RGB files, etc which is much faster than serial.

## Snackey ##

Since Snackey was part of the project, some details such as walkthroughs will be made available.
