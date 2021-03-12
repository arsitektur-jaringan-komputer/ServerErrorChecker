#!/usr/bin/python

import telebot
import difflib
import sys
import os
from inotify_simple import INotify, flags

log = sys.argv[1]
check = log + str(".check")

chatId = sys.argv[2]
bot = telebot.TeleBot(sys.argv[3])

inotify = INotify()
watch_flags = flags.MOVE_SELF | flags.MODIFY


def beda(log, check):
    inotify.add_watch(log, watch_flags)
    try:
        for event in inotify.read(timeout=1):
            if event is not None:
                for flag in flags.from_mask(event.mask):
                    if str(flag) == 'flags.MODIFY':
                        with open(log, "r") as logFile, open(check) as checkFile:
                            loglines = logFile.readlines()
                            checklines = checkFile.readlines()
                            d = difflib.Differ()
                            diff = d.compare(loglines, checklines)
                            perbedaan = "".join(x[2:] for x in diff if x.startswith('- '))
                        if perbedaan != "":
                            try:
                                kirim = 'ERROR TERDETEKSI:\n' + perbedaan
                                bot.send_message(chatId, kirim)
                                with open(check, "a+") as appendFile:
                                    appendFile.write(perbedaan)
                            except:
                                print("Gagal mengirim error")
                        else:
                            pass
                    elif str(flag) == 'flags.MOVE_SELF':
                        with open(check, 'w'):
                            pass
                    elif str(flag) == 'flags.IGNORED':
                        print("warning")
                        bot.send_message(chatId, "Peringatan! file error.log diubah secara manual")
                    else:
                        print(str(flag))
                        bot.send_message(chatId, str(flag))
    except:
        print("error event")
        inotify.rm_watch(log)


i = 1
while 1:
    if i == 1:
        if not os.path.isfile(check):
            f= open(check,"w+")
            f.close()

        with open(log, "r") as logFile, open(check) as checkFile:
            loglines = logFile.readlines()
            checklines = checkFile.readlines()
            d = difflib.Differ()
            diff = d.compare(loglines, checklines)
            perbedaan = "".join(x[2:] for x in diff if x.startswith('- '))
        if perbedaan != "":
            try:
                kirim = 'ERROR TERDETEKSI:\n' + perbedaan
                bot.send_message(chatId, kirim)
                with open(check, "a+") as appendFile:
                    appendFile.write(perbedaan)
            except:
                print("Gagal mengirim error")
        else:
            pass
        i += 1
    beda(log, check)
