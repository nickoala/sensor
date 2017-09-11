import sys
from sensor.LCD1602 import LCD1602

temperature = sys.argv[1].strip()
humidity = sys.argv[2].strip()

lcd = LCD1602(1, 0x27)

lcd.display('     %s C' % temperature, 1)
lcd.display('     %s %%' % humidity, 2)
