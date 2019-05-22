import sqlite3
import datetime
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

sqlite_file = 'texts' # name of sqlite texts file in same directory as script
table_name = 'message' # access the message table, which has message content along with chat handles
column = 'text' # message content

# connect
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

msg = '❤️'
msg2 = '♥'
search = 'HeartChart'

# in handle table:
# id is phone number/email (with +1 on the phone numbers usually)
# ROWID is the handle to the person

print("Please enter the phone number or email of the conversation you want to chart:")
conv_id = sys.stdin.readline()[:-1]
c.execute('SELECT ROWID,id FROM handle WHERE id LIKE "%{mn}%"'.\
        format(mn=conv_id))
handles = c.fetchall()
if len(handles) != 0:
        print("Found", len(handles), "associated handles")
else:
        print("No match found, try again")

print("Would you like to search for hearts? (y/n)")
ans = sys.stdin.readline()[:-1]

rows = []
if ans == 'n':
        print("What would you like to search for?")
        search = sys.stdin.readline()[:-1]

for handle in handles:
        if ans == 'y':
                c.execute('SELECT {cn},date,is_from_me FROM {tn} WHERE ({cn} LIKE "%{mn}%" OR {cn} LIKE "%{mn2}%") AND message.handle_id == {id}'.\
                        format(tn=table_name, cn=column, mn=msg, mn2=msg2, id=handle[0]))
        elif ans == 'n':
                c.execute('SELECT {cn},date,is_from_me FROM {tn} WHERE {cn} LIKE "%{mn}%" AND message.handle_id == {id}'.\
                        format(tn=table_name, cn=column, mn=search, id=handle[0]))
        else:
                print("Please retry with either 'y' or 'n'")

        rows.extend(c.fetchall())

print(len(rows), "matches found")

if len(rows) != 0:
        newDate = time.localtime(rows[0][1] / 1000000000)

        dt = datetime.datetime.fromtimestamp(time.mktime(newDate))
        timedelta = datetime.timedelta(seconds=978307200)
        dt = dt + timedelta

        weekCount17me = np.zeros(53) # 53 because 0 and 52 both possible week values under isocalendar
        weekCount18me = np.zeros(53)
        weekCount17you = np.zeros(53)
        weekCount18you = np.zeros(53)

        for date in rows:
            fDate = time.localtime(date[1] / 1000000000)
            fdt = datetime.datetime.fromtimestamp(time.mktime(fDate))
            ftimedelta = datetime.timedelta(seconds=978307200)
            fdt = fdt + ftimedelta
            yr,weekNum,weekDay = fdt.isocalendar()

            if yr == 2017:
                    if date[2] == 1: #msg was from me
                            weekCount17me[weekNum] += 1
                    else:
                            weekCount17you[weekNum] += 1
            elif yr == 2018:
                    if date[2] == 1:
                            weekCount18me[weekNum] += 1
                    else:
                            weekCount18you[weekNum] += 1

        full_me = np.append(weekCount17me,weekCount18me)
        full_you = np.append(weekCount17you,weekCount18you)
        
        plt.plot(full_me, label='me')
        plt.plot(full_you, label=conv_id)
        plt.title(search)
        plt.ylabel('matching messages') #doesn't propoerly display emoji as axis label, so don't include
        plt.xlabel('weeks')
        plt.legend(loc='upper left')
        plt.show()
        plt.pause(5)
conn.close()