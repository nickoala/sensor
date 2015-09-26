# coding=utf8

import sys
import time
import traceback
import signal
import telepot
from sensor import *

"""
$ python2.7 indoor.py <token> <user_id>

An indoor climate monitor with 3 sensors and an LCD display.

It also comes with a Telegram bot that can report data periodically.

To know more about Telegram Bot and telepot, go to:
  https://github.com/nickoala/telepot
"""

ds = DS18B20.DS18B20('28-000007355d64')
htu = HTU21D.HTU21D(1, 0x40)
bmp = BMP180.BMP180(1, 0x77)
lcd = LCD1602.LCD1602(1, 0x27)

def read_all():
    return ds.temperature(), htu.humidity(), bmp.pressure()

def lcd_display():
    t, h, p = read_all()
    lcd.display('%.1f C    %.1f%%' % (t.C, h.RH), 1)
    lcd.display('   %.1f hPa' % p.hPa, 2)

def read_send(user_id):
    t, h, p = read_all()
    msg = '{:.1f}°C  {:.1f}%  {:,.1f}hPa'.format(t.C, h.RH, p.hPa)
    bot.sendMessage(user_id, msg)

def handle(msg):
    global last_report, report_interval

    msg_type, from_id, chat_id = telepot.glance(msg)

    if msg_type != 'text':
        return

    if from_id != USER_ID:
        return

    command = msg['text'].strip().lower()

    if command == '/now':
        read_send(from_id)
    elif command == '/1m':
        read_send(from_id)
        last_report = time.time()
        report_interval = 1 * 60
    elif command == '/1h':
        read_send(from_id)
        last_report = time.time()
        report_interval = 1 * 3600
    elif command == '/cancel':
        last_report = None
        report_interval = None
        bot.sendMessage(from_id, "OK")
    else:
        bot.sendMessage(from_id, "I don't understand")


def on_sigterm(signum, frame):
    sys.exit(0)
    # raise SystemExit so the `finally` clause gets executed

signal.signal(signal.SIGTERM, on_sigterm)


TOKEN = sys.argv[1]
USER_ID = long(sys.argv[2])

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)

last_report = None
report_interval = None

try:
    while 1:
        lcd_display()

        # Is it time to report again?
        now = time.time()
        if report_interval is not None and last_report is not None and now - last_report >= report_interval:
            try:
                read_send(USER_ID)
                last_report = now
            except:
                traceback.print_exc()

        time.sleep(0.1)
finally:
    lcd.clear()
