import sys
from chomper import Chomper
from flashbdev import bdev
import uos

# Re-mount local storage with larger read and lookahead buffers for faster bling
vfs = uos.VfsLfs2(bdev, readsize=1024, lookahead=4096)
uos.mount(vfs, "/")

def chomper_go():
    # Startup watch
    watch = Chomper()

chomper_go()