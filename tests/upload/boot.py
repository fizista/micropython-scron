# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)       # turn off vendor O/S debugging messages
#esp.osdebug(0)          # redirect vendor O/S debugging messages to UART(0)