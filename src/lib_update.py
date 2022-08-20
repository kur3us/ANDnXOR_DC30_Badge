import binascii
import os
import chomper_wifi as wifi
import hashlib
import machine
import time
import ubinascii
import urequests as requests

BASE_URL = 'https://mattdamon.app/'

hostname = "chomper-" + ubinascii.hexlify(machine.unique_id()).decode('utf-8')
wifi.set_hostname(hostname)

_cb = None

def _status_update(msg, error=False):
    if _cb:
        _cb(msg, error)

def manifest_download():
    global BASE_URL
    try:
        res = requests.get(url=BASE_URL+'manifest.txt')
        _status_update("Manifest downloaded")
        return res.text
    except Exception as e:
        print("UPDATE: Unable to download manifest, try again", e)
        _status_update("Manifest failed", True)
        return "ERROR"

def file_download(path, file_name):
    global BASE_URL
    file_url = BASE_URL+'data/'+file_name
    print("DOWNLOADING:", file_url)
    res = requests.get(url=file_url)
    file = open(path, "wb")
    file.write(res.content)
    file.close()
 
def update_file(file_name, hash):
    #Check for existance of file and its hash value against manifest data
    #If missing or invalid, download and update the file
    path = '/'+file_name
    _status_update(file_name)
    print("Checking", path, hash)
    update = False
    exists = False
    try:
        os.stat(path)
        exists = True
    except:
        exists = False

    if exists:
        print(path, "exists")
        digest = hashlib.sha256(open(path,'rb').read()).digest()
        remote_digest = binascii.unhexlify(hash)
        if digest != remote_digest:
            update = True
    else:
        update = True

    if update:
        file_download(path, file_name)
    else:
        print(path, "IS GOOD TO GO")

def update_files(manifest):
    # Parse manifest file
    lines = manifest.split('\n')
    for line in lines:
        tokens = line.split()
        if len(tokens) == 2:
            md5=tokens[0]
            file_name=tokens[1]

            update_file(file_name, md5)

def do_update(cb=None, reboot=True):
    global _cb
    _cb = cb
    wifi._connect()
    _status_update("Connecting...")

    counter = 0
    max = 10
    while not wifi.isconnected():
        counter += 1
        print("...Waiting for connection try", counter, "of", max)
        time.sleep(1)
        if counter >= max:
            print("***UNABLE TO CONNECT TO WIFI FOR UPDATE***")
            return
        
    _status_update("Connected")
    print("Connected")
    manifest = manifest_download()
    update_files(manifest)
    _status_update("Disconnecting")
    wifi._disconnect()

    if reboot:
        _status_update("Rebooting, HODL")
        machine.reset()