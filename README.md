# AND!XOR DC30 Badge "Chomper"

Please be patient as we add documentation and files for this year's project.

Initial release of python and chomper (micropython) bin file. Provision scripts and our micropython add-ons/source will be available when ready.

# Provisioning (fancy term for flashing) #

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
