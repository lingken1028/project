"""
HX711 Load cell amplifier Python Library
Original source: https://gist.github.com/underdoeg/98a38b54f889fce2b237
Documentation source: https://github.com/aguegu/ardulibs/tree/master/hx711
Adapted by 2017 Jiri Dohnalek

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""


import machine
import time
import sys

class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1

        self.PD_SCK = machine.Pin(pd_sck, machine.Pin.OUT)
        self.DOUT = machine.Pin(dout, machine.Pin.IN)

        self.power_up()
        self.set_gain(gain)

    def set_gain(self, gain=128):
        try:
            if gain == 128:
                self.GAIN = 3
            elif gain == 64:
                self.GAIN = 2
            elif gain == 32:
                self.GAIN = 1
        except:
            self.GAIN = 3  # Sets default GAIN at 128

        self.PD_SCK.off()
        self.read()

    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def get_scale(self):
        return self.SCALE

    def get_offset(self):
        return self.OFFSET

    def read(self):
        while self.DOUT.value():
            pass

        count = 0
        for _ in range(24):
            self.PD_SCK.on()
            count = count << 1
            self.PD_SCK.off()
            if self.DOUT.value():
                count += 1

        self.PD_SCK.on()
        count = count ^ 0x800000
        self.PD_SCK.off()

        for _ in range(self.GAIN):
            self.PD_SCK.on()
            self.PD_SCK.off()

        return count

    def read_average(self, times=16):
        sum = 0
        for _ in range(times):
            sum += self.read()
        return sum / times

    def get_grams(self, times=16):
        value = (self.read_average(times) - self.OFFSET)
        grams = (value / self.SCALE)
        return grams

    def tare(self, times=16):
        sum = self.read_average(times)
        self.set_offset(sum)

    def power_down(self):
        self.PD_SCK.off()
        self.PD_SCK.on()

    def power_up(self):
        self.PD_SCK.off()
