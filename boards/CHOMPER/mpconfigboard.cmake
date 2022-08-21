# Define the chip variant.
set(IDF_TARGET esp32)

# Set the sdkconfig fragments.
set(SDKCONFIG_DEFAULTS
    ${MICROPY_PORT_DIR}/boards/sdkconfig.base
    ${MICROPY_PORT_DIR}/boards/sdkconfig.ble
    ${MICROPY_PORT_DIR}/boards/sdkconfig.spiram
    ${PROJECT_DIR}/boards/CHOMPER/sdkconfig.board
)

# Set the user C modules to include in the build.
set(USER_C_MODULES
    ${PROJECT_DIR}/lib/chomper/micropython.cmake
    ${PROJECT_DIR}/lib/st7789/micropython.cmake
)

# Set the manifest file for frozen Python code.
set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
