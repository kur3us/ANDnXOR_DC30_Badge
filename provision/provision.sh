#!/bin/bash
DEV=$1
LOOP=${2:-0}

echo "*************************************************************"
echo "*** AND!XOR DEF CON 30 AUTO PROVISIONER                   ***"
echo "*** Make sure to source esp-idf/export.sh first!          ***"
echo "*************************************************************"

while true; do
   while [ ! -e $DEV ]; do
      timestamp=$(date +%T)
      echo "[$timestamp] Waiting for $DEV to be available"
      sleep 5
   done

   echo "### Provisioning on $DEV ###"

   echo "### Wiping Flash ###"
   esptool.py -p $DEV erase_flash
   echo "### Flashing Micropython ###"
   esptool.py --chip esp32 -p $DEV -b 460800 --before=default_reset --after=hard_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 16MB 0x8000 partition-table.bin 0x1000 bootloader.bin 0x10000 chomper.bin
   echo "### Copying minimum flash files VERY SLOWLY ###"

   # Copy only cross compiled python and docs to watch
   cd ../src

   for i in *.mpy main.py; do
     echo $i `stat -c "%s" $i` bytes
     ampy -p $DEV put $i
   done
   ampy -p $DEV put ../rtfm/docs/index.md rtfm.md

   ampy -p $DEV put ../provision/FIRSTRUN

   echo "### Updating from Firebase ###"
   mpremote connect $DEV run update.py
   mpremote connect $DEV run update.py
   mpremote connect $DEV run update.py

   cd ../provision

   echo "### Rebooting this should take 16 seconds ###"
   mpremote connect $DEV exec "import machine; machine.reset()" > /dev/null &
   sleep 15
   echo "### Watch should be booting ###"
   sleep 5
   echo "### Watch should indicate successful provision ###"

   echo "### Disconnect the watch ###"
   while [ -e $DEV ]; do
      timestamp=$(date +%T)
      echo "[$timestamp] Waiting for $DEV to be disconnected"
      sleep 5
   done
   
   echo "All done. You will see an error in 'serialposix.py' it is normal, OS is cleaning our forked mpremote process from earlier"

   if [[ $LOOP -eq 0 ]]; then
      break
   fi
done
