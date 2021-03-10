# !/user/bin/env Python3
# -*- coding:utf-8 -*-

from tkinter import *
from tkinter import filedialog, dialog
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText
import re
import os


#东南西北ESWN
class MainPage(Tk):
    def __init__(self, master=None):
        self.root = master  #定义内部变量root
        self.root.title('Check Long Probe Program Development')
        self.page = Frame(self.root)  #创建Frame
        self.page.pack()
        self.path = StringVar()
        self.entry_1 = Entry(self.page, textvariable=self.path,
                             width=35).grid(row=1, padx=15, pady=10)
        self.bt2 = Button(self.page,
                          text='Find files',
                          width=10,
                          height=1,
                          command=self.file).grid(row=1, column=1, pady=10)
        self.scroll = ScrolledText(self.page, width=25, height=5)
        self.scroll.grid(padx=2, pady=20)
        self.bt3 = Button(self.page,
                          text='firstcompare',
                          width=10,
                          height=1,
                          command=self.compared_file).grid(row=2, column=1)
        self.bt4 = Button(self.page,
                          text='lastcompare',
                          width=10,
                          height=1,
                          command=self.compared_file_last).grid(row=3,
                                                                column=1)

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
            self.scroll.insert('insert', '请确认文件是否正确！\n文件应为testplan\n')
        if os.path.isfile(fname2):
            wirelist = open(fname2, 'r', encoding="utf-8").read()
        else:
            self.scroll.insert('insert', '请确认文件是否正确！\n文件应为wirelist\n')

        wire = open(fname2, 'r', encoding="utf-8").readlines()
        wires = [x.strip() for x in wire if x.split()]
        checkpins = open(self.path_file + '/checkpins.txt', 'w')
        last_list = open(self.path_file + '/check_long_pins.txt', 'w')
        if testplan and wirelist is not None:
            #key words to extract the coordinate
            start_fun = 'functional'
            start_digi = 'digital'
            start_power = 'powered shorts'
            end = "end test"
            pattern = re.compile(
                '!.*digital.*?/.*?!|!.*analog.*?/.*?!|!.*mixed.*?/.*?!', re.M)
            str_re1 = pattern.findall(testplan)
            s2 = []
            for i in str_re1:
                s1 = i.split('/')[-1].strip('!')
                s2.append(s1)
            Components = [x.strip() for x in s2]
            str_allpin = 'wire'
            wirepins = []
            allpins = []

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
            re1 = start_fun + '(.*?)' + end
            re2 = start_digi + '(.*?)' + end
            re3 = start_power + '(.*?)' + end
            # generic_re是個元組[(.....)]
            generic_re = re.compile("(%s|%s|%s)" % (re1, re2, re3),
                                    re.S).findall(longpins)
            # 此處是爲了將元組generic_re轉換爲long_list[]
            long_list = [item for t in generic_re for item in t]
            last_list.write(
                '!Long probe list\nreport netlist, common devices\nthreshold      25\n'
            )
            for line in long_list:
                lines = line.split('\n')
                lines = [x.strip() for x in lines if x.split()]  #刪除多於空行
                for lin in lines:
                    if str_allpin in lin:
                        pattern = re.compile('"(.*)"')
                        str_re1 = pattern.findall(lin)
                        ssline = str_re1[0]
                        if ssline not in wirepins:
                            wirepins.append(ssline)
            for pins in wirepins:
                if 'GND' not in pins:
                    markspins = '"%s"' % pins
                    markspins = markspins.upper()
                    last_list.write('short "GND" to %s\n' % markspins)

            last_list.writelines('\n\n\n!Probe list\nthreshold      1000\n')
            for line in wire:
                if str_allpin in line:
                    pattern = re.compile('"(.*)"')
                    str_re1 = pattern.findall(line)
                    ssline = str_re1[0]
                    sslines = '"%s"' % ssline
                    if sslines not in allpins:
                        allpins.append(sslines)

            for pins in allpins:
                markspins = pins.upper()
                last_list.write('nodes %s\n' % markspins)

            if os.path.exists("D:\compare\checkpins.txt"):
                os.remove("D:\compare\checkpins.txt")
            else:
                print("The file does not exist")
        else:
            self.scroll.insert(
                'insert',
                '请确认路径或者文件名是否正确！请将文件放在D:/compare/,\n文件应为testplan和wirelist')

    def compared_file_last(self):
        print('success')


if __name__ == "__main__":
    root = Tk()
    root.geometry('430x190+30+30')
    app = MainPage(master=root)
    root.mainloop()
