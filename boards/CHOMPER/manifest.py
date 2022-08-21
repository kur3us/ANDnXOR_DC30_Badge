freeze("$(PORT_DIR)/modules")
# Free libraries
freeze("$(BOARD_DIR)/../../lib/", "axp202c.py")
freeze("$(BOARD_DIR)/../../lib/", "bma423.py")
freeze("$(BOARD_DIR)/../../lib/", "focaltouch.py")
freeze("$(BOARD_DIR)/../../lib/", "font_digital.py")
freeze("$(BOARD_DIR)/../../lib/", "font_digital16.py")
freeze("$(BOARD_DIR)/../../lib/", "font_digital32.py")
freeze("$(BOARD_DIR)/../../lib/", "ntptime.py")
freeze("$(BOARD_DIR)/../../lib/", "pcf8563.py")
freeze("$(BOARD_DIR)/../../lib/", "urequests.py")
freeze("$(BOARD_DIR)/../../lib/", "vga1_8x8.py")
freeze("$(BOARD_DIR)/../../img/", "logo.py")

# Freeze CHOMPER files
# freeze("$(BOARD_DIR)/../../src/", "main.py")
