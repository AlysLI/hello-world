# !/user/bin/env Python3
# -*- coding:utf-8 -*-

from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText
import re
import os
import time


#东南西北ESWN
class MainPage(Tk):
    def __init__(self, master=None):
        self.root = master  #定义内部变量root
        self.root.title('Check Long Probe Program Development')
        self.page = Frame(self.root)  #创建Frame
        self.page.pack()
        self.path = StringVar()
        self.var = StringVar()
        # self.var.set('Start')
        self.entry_1 = Entry(self.page, textvariable=self.path,
                             width=35).grid(row=0, padx=15, pady=10)
        self.bt2 = Button(self.page,
                          text='Find files',
                          width=10,
                          height=1,
                          command=self.file).grid(row=0, column=1, pady=10)
        # self.scroll = ScrolledText(self.page, width=25, height=5)
        # self.scroll.grid(padx=2, pady=20)
        self.bt3 = Button(self.page,
                          text='Part one',
                          width=10,
                          height=1,
                          command=self.compared_file).grid(row=2, column=1)

        self.bt4 = Button(self.page,
                          text='Part two',
                          width=10,
                          height=1,
                          command=self.compared_file_last).grid(row=4,
                                                                column=1)
        self.text_1 = Label(self.page, text='Status:Welecome').grid(row=3,
                                                                    column=0,
                                                                    padx=3)
        self.text_2 = Label(self.page, textvariable=self.var).grid(pady=3,
                                                                   padx=2)
        self.canvas = Canvas(self.page, width=300, height=20, bg='white')
        self.canvas.grid(pady=15, padx=4)

    def file(self):
        self.path_file = askdirectory()
        self.path.set(self.path_file)

    def compared_file(self):
        # Required file path
        fname = self.path_file + '/testplan'
        fname2 = self.path_file + '/wirelist'
        if os.path.isfile(fname):
            testplan = open(fname, 'r', encoding="utf-8").read()
        else:
            self.text_1 = Label(
                self.page,
                text=
                'Status: Please confirm whether the file exists! \nThe file should be testplan'
            ).grid(row=3, column=0, padx=3)
            # self.scroll.insert('insert', '请确认文件是否存在！\n文件应为testplan\n')
        if os.path.isfile(fname2):
            wirelist = open(fname2, 'r', encoding="utf-8").read()
        else:
            self.text_1 = Label(
                self.page,
                text=
                'Status: Please confirm whether the file exists! \nThe file should be wirelist'
            ).grid(row=3, column=0, padx=3)
            # self.scroll.insert('insert', '请确认文件是否存在！\n文件应为wirelist\n')

        wire = open(fname2, 'r', encoding="utf-8").readlines()
        wires = [x.strip() for x in wire if x.split()]
        checkpins = open(self.path_file + '/checkpins.txt', 'w')
        last_list = open(self.path_file + '/check_long_pins_org.txt', 'w')
        try:
            if testplan and wirelist is not None:

                #key words to extract the coordinate
                start_digi = 'digital'
                pwr_check = 'pwr_check'
                end = "end test"
                pattern = re.compile(
                    '!.*digital.*?/.*?!|!.*analog.*?/.*?!|!.*mixed.*?/.*?!',
                    re.M)
                str_re1 = pattern.findall(testplan)
                s2 = []
                for i in str_re1:
                    s1 = i.split('/')[-1].strip('!')
                    s2.append(s1)
                Components = [x.strip() for x in s2]
                str_allpin = 'wire'
                wirepins = []
                allpins = []
                longpinslist = []
                for i in Components:
                    endtest = wirelist.replace('end test', 'end test.')
                    pattern = re.compile('[^\n]*%s[^.]*' % i)
                    search = pattern.findall(endtest)
                    for s in search:
                        lines = s.split('\n')
                        line = [x.strip() for x in lines if x.split()]
                        for lin in line:
                            if lin in wires:
                                wires.remove(lin)
                for w in wires:
                    checkpins.write('%s\n' % w)
                checkpins.close()

                longpins = open(self.path_file + '/checkpins.txt',
                                'r',
                                encoding="utf-8").read()
                shortpins = open(self.path_file + '/checkpins.txt',
                                 'r',
                                 encoding="utf-8").readlines()
                re1 = start_digi + '(.*?)' + end
                re2 = pwr_check + '(.*?)' + end
                # generic_re是個元組[(.....)]
                generic_re = re.compile("(%s|%s)" % (re1, re2),
                                        re.S).findall(longpins)
                # 此處是爲了將元組generic_re轉換爲long_list[]
                long_list = [item for t in generic_re for item in t]
                for line in long_list:
                    lines = line.split('\n')
                    lines = [x.strip() for x in lines if x.split()]  #刪除多於空行
                    for lin in lines:
                        if str_allpin in lin:
                            pattern = re.compile('"(.*)"')
                            str_re1 = pattern.findall(lin)
                            ssline = str_re1[0]
                            sslines = '"%s"' % ssline
                            if sslines not in wirepins:
                                wirepins.append(sslines)

                for line in shortpins:
                    if str_allpin in line:
                        pattern = re.compile('"(.*)"')
                        str_re1 = pattern.findall(line)
                        ssline = str_re1[0]
                        sslines = '"%s"' % ssline
                        if sslines not in allpins:
                            if 'GND' not in sslines:
                                allpins.append(sslines)

                #testplan gpconnect導入長針清單
                pat = re.compile('gpconnect.*"*"').findall(testplan)
                for i in pat:
                    gpconnect = i.split(" ")[1]
                    if gpconnect not in wirepins:
                        if gpconnect in allpins:
                            wirepins.append(gpconnect)
                for pins in wirepins:
                    if 'GND' not in pins:
                        longprobe = pins.upper()
                        last_list.write('short "GND" to %s\n' % longprobe)
                        longpinslist.append(longprobe)

                last_list.writelines(
                    '\n\n\n!Probe list\nthreshold      1000\n')
                short_list = []
                for pin in allpins:
                    shortprobe = pin.upper()
                    if not any(longpin in shortprobe
                               for longpin in longpinslist):
                        last_list.write('nodes %s\n' % shortprobe)
                        short_list.append(shortprobe)

                last_list.write('!Long probe list\n')
                for pins in longpinslist:
                    if 'GND' not in pins:
                        markspins = pins.upper()
                        last_list.write('nodes %s\n' % markspins)

                last_list.close()
                with open(self.path_file + "/check_long_pins_org.txt",
                          encoding="utf-8",
                          mode="a") as file:
                    file.write('nodes "GND"')
                with open(self.path_file + '/check_long_pins_org.txt',
                          'r+') as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write(
                        '!Long probe list\n!Total %spcs long probes\n!Total %spcs short probes\nreport netlist, common devices\nthreshold      25\nsettling delay 50.0u\n'
                        % (len(longpinslist), len(short_list)) + content)

                if os.path.exists(self.path_file + "/checkpins.txt"):
                    os.remove(self.path_file + "/checkpins.txt")
                else:
                    print("The file does not exist")
                #清空进度条
                fill_line = self.canvas.create_rectangle(1.5,
                                                         1.5,
                                                         0,
                                                         23,
                                                         width=0,
                                                         fill="white")

                x = 500  # 未知变量，可更改
                n = 350 / x  # 465是矩形填充满的次数
                # for t in range(x):
                n = 350
                # 以矩形的长度作为变量值更新
                self.canvas.coords(fill_line, (0, 0, n, 60))
                self.page.update()
                time.sleep(0)  # 时间为0，即飞速清空进度条

                # 填充进度条
                fill_line = self.canvas.create_rectangle(1.5,
                                                         1.5,
                                                         0,
                                                         23,
                                                         width=0,
                                                         fill="green")
                x = 200  # 未知变量，可更改
                n = 350 / x  # 200是矩形填充满的次数
                k = 100 / x  # 显示值
                for i in range(x):
                    n = n + 350 / x
                    k = k + 100 / x
                    self.canvas.coords(fill_line, (0, 0, n, 60))
                    if k >= 100:
                        self.var.set("100%")
                    else:
                        self.var.set(str(round(k, 1)) + "%")
                    self.page.update()
                    time.sleep(0.02)  # 控制进度条流动的速度

            else:
                self.text_1 = Label(
                    self.page,
                    text='狀態：请确认路径或者文件名是否正确！\n比對文件应为testplan和wirelist').grid(
                        row=3, column=0, padx=3)
                # self.scroll.insert('insert',
                #                    '请确认路径或者文件名是否正确！\n比對文件应为testplan和wirelist')

        except IOError:
            self.text_1 = Label(
                self.page,
                text='Status:File not found or file comparison failed').grid(
                    row=3, column=0, padx=3)
        else:
            cklong = '/check_long_pins_org.txt'
            self.text_1 = Label(
                self.page,
                text='Status:The content is written successfully,\nFile in %s'
                % self.path_file + cklong).grid(row=3, column=0, padx=3)

    def compared_file_last(self):

        #last compare，目標文件failinformation
        # Required file path
        fname = self.path_file + '/testplan'
        fname2 = self.path_file + '/wirelist'
        failfile = self.path_file + '/failinformation'
        if os.path.isfile(fname):
            testplan = open(fname, 'r', encoding="utf-8").read()
        else:
            self.text_1 = Label(
                self.page,
                text=
                'Status: Please confirm whether the file exists! The file should be testplan'
            ).grid(row=3, column=0, padx=3)
            # self.scroll.insert('insert', '请确认該文件是否存在！\n文件应为testplan\n')
        if os.path.isfile(fname2):
            wirelist = open(fname2, 'r', encoding="utf-8").read()
        else:
            self.text_1 = Label(
                self.page,
                text=
                'Status: Please confirm whether the file exists! The file should be wirelist'
            ).grid(row=3, column=0, padx=3)
            # self.scroll.insert('insert', '请确认該文件是否存在！\n文件应为wirelist\n')

        if os.path.isfile(failfile):
            failinfo = open(failfile, 'r', encoding="utf-8").read()
        else:
            self.text_1 = Label(
                self.page,
                text=
                'Status: Please confirm whether the file exists! The file should be failinformation'
            ).grid(row=3, column=0, padx=3)
            # self.scroll.insert('insert', '请确认該文件是否存在！\n文件应为failinformation\n')
        wire = open(fname2, 'r', encoding="utf-8").readlines()
        wires = [x.strip() for x in wire if x.split()]
        checkpins = open(self.path_file + '/checkpins2.txt', 'w')
        last_list = open(self.path_file + '/check_long_pins.txt', 'w')
        try:
            if testplan and wirelist is not None:
                #key words to extract the coordinate
                start_digi = 'digital'
                pwr_check = 'pwr_check'
                end = "end test"
                pattern = re.compile(
                    '!.*digital.*?/.*?!|!.*analog.*?/.*?!|!.*mixed.*?/.*?!',
                    re.M)
                str_re1 = pattern.findall(testplan)
                s2 = []
                for i in str_re1:
                    s1 = i.split('/')[-1].strip('!')
                    s2.append(s1)
                Components = [x.strip() for x in s2]
                str_allpin = 'wire'
                wirepins = []
                allpins = []
                longpinslist = []
                for i in Components:
                    endtest = wirelist.replace('end test', 'end test.')
                    pattern = re.compile('[^\n]*%s[^.]*' % i)
                    search = pattern.findall(endtest)
                    for s in search:
                        lines = s.split('\n')
                        line = [x.strip() for x in lines if x.split()]
                        for lin in line:
                            if lin in wires:
                                wires.remove(lin)
                for w in wires:
                    checkpins.write('%s\n' % w)
                checkpins.close()

                longpins = open(self.path_file + '/checkpins2.txt',
                                'r',
                                encoding="utf-8").read()
                shortpins = open(self.path_file + '/checkpins2.txt',
                                 'r',
                                 encoding="utf-8").readlines()
                re1 = start_digi + '(.*?)' + end
                re2 = pwr_check + '(.*?)' + end
                # generic_re是個元組[(.....)]
                generic_re = re.compile("(%s|%s)" % (re1, re2),
                                        re.S).findall(longpins)
                # 此處是爲了將元組generic_re轉換爲long_list[]
                long_list = [item for t in generic_re for item in t]
                for line in long_list:
                    lines = line.split('\n')
                    lines = [x.strip() for x in lines if x.split()]  #刪除多於空行
                    for lin in lines:
                        if str_allpin in lin:
                            pattern = re.compile('"(.*)"')
                            str_re1 = pattern.findall(lin)
                            ssline = str_re1[0]
                            sslines = '"%s"' % ssline
                            if sslines not in wirepins:
                                wirepins.append(sslines)

                for line in shortpins:
                    if str_allpin in line:
                        pattern = re.compile('"(.*)"')
                        str_re1 = pattern.findall(line)
                        ssline = str_re1[0]
                        sslines = '"%s"' % ssline
                        if sslines not in allpins:
                            if 'GND' not in sslines:
                                allpins.append(sslines)

                #testplan gpconnect導入長針清單
                pat = re.compile('gpconnect.*"*"').findall(testplan)
                for i in pat:
                    gpconnect = i.split(" ")[1]
                    if gpconnect not in wirepins:
                        if gpconnect in allpins:
                            wirepins.append(gpconnect)

                #添加open fail裏的針點到短針清單，注意Ohm下面有數字的部分
                l_list = []
                pattern5 = re.compile('Open #1.*[^Short #1]', re.S)
                last = pattern5.findall(failinfo)
                for s in last:
                    lines = s.split('\n')
                    line = [x.strip() for x in lines if x.split()]
                    for i in line:
                        lin = re.compile('[0-9a-zA-Z\_]+').findall(i)
                        for j in lin:
                            l_list.append(j)
                for i in l_list:
                    i = '"%s"' % i
                    if i in wirepins:
                        wirepins.remove(i)

                #添加short fail裏的針點到長針清單
                l_list2 = []
                pattern5 = re.compile('Short #1.*[^Total]', re.S)
                last = pattern5.findall(failinfo)
                for s in last:
                    lines = s.split('\n')
                    line = [x.strip() for x in lines if x.split()]
                    for i in line:
                        lin = re.compile('[0-9a-zA-Z\_]+').findall(i)
                        for j in lin:
                            l_list2.append(j)
                for i in l_list2:
                    i = '"%s"' % i
                    if i in allpins:
                        if i not in wirepins:
                            wirepins.append(i)

                for pins in wirepins:
                    if 'GND' not in pins:
                        longprobe = pins.upper()
                        last_list.write('short "GND" to %s\n' % longprobe)
                        longpinslist.append(longprobe)

                last_list.writelines(
                    '\n\n\n!Probe list\nthreshold      1000\n')
                short_list = []
                for pin in allpins:
                    shortprobe = pin.upper()
                    if not any(longpin in shortprobe
                               for longpin in longpinslist):
                        last_list.write('nodes %s\n' % shortprobe)
                        short_list.append(shortprobe)

                last_list.write('!Long probe list\n')
                for pins in longpinslist:
                    if 'GND' not in pins:
                        markspins = pins.upper()
                        last_list.write('nodes %s\n' % markspins)

                last_list.close()
                with open(self.path_file + "/check_long_pins.txt",
                          encoding="utf-8",
                          mode="a") as file:
                    file.write('nodes "GND"')
                with open(self.path_file + '/check_long_pins.txt', 'r+') as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write(
                        '!Long probe list\n!Total %spcs long probes\n!Total %spcs short probes\nreport netlist, common devices\nthreshold      25\nsettling delay 50.0u\n'
                        % (len(longpinslist), len(short_list)) + content)

                if os.path.exists(self.path_file + "/checkpins2.txt"):
                    os.remove(self.path_file + "/checkpins2.txt")
                else:
                    print("The file does not exist")

                #清空进度条
                fill_line = self.canvas.create_rectangle(1.5,
                                                         1.5,
                                                         0,
                                                         23,
                                                         width=0,
                                                         fill="white")

                x = 500  # 未知变量，可更改
                n = 200 / x  # 465是矩形填充满的次数
                # for t in range(x):
                n = 200
                # 以矩形的长度作为变量值更新
                self.canvas.coords(fill_line, (0, 0, n, 60))
                self.page.update()
                time.sleep(0)  # 时间为0，即飞速清空进度条

                # 填充进度条
                fill_line = self.canvas.create_rectangle(1.5,
                                                         1.5,
                                                         0,
                                                         23,
                                                         width=0,
                                                         fill="green")
                x = 200  # 未知变量，可更改
                n = 300 / x  # 200是矩形填充满的次数
                k = 100 / x  # 显示值
                for i in range(x):
                    n = n + 300 / x
                    k = k + 100 / x
                    self.canvas.coords(fill_line, (0, 0, n, 60))
                    if k >= 100:
                        self.var.set("100%")
                    else:
                        self.var.set(str(round(k, 1)) + "%")
                    self.page.update()
                    time.sleep(0.01)  # 控制进度条流动的速度

            else:
                self.text_1 = Label(
                    self.page,
                    text='Status:File not found or file comparison failed'
                ).grid(row=3, column=0, padx=3)
                # self.scroll.insert('insert',
                #                    '请确认路径或者文件名是否正确！\n比對文件应为testplan和wirelist')

        except IOError:
            self.text_1 = Label(
                self.page,
                text='Status:File not found or file comparison failed').grid(
                    row=3, column=0, padx=3)
        else:
            cklong2 = '/check_long_pins.txt'
            self.text_1 = Label(
                self.page,
                text='Status:The last file is written successfully,\nFile in %s'
                % self.path_file + cklong2).grid(row=3, column=0, padx=3)


if __name__ == "__main__":
    root = Tk()
    root.geometry('600x200+30+30')
    app = MainPage(master=root)
    root.mainloop()
