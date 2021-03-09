# !/user/bin/env Python3
# -*- coding:utf-8 -*-

from tkinter import *
from tkinter import filedialog, dialog
from tkinter.scrolledtext import ScrolledText
import re
import os


#东南西北ESWN
class MainPage(Tk):
    def __init__(self, master=None):
        self.root = master  #定义内部变量root
        self.root.title('Compared pins')
        self.page = Frame(self.root)  #创建Frame
        self.page.pack()
        Label(self.page).grid(row=1, column=0, padx=10)
        self.bt2 = Button(self.page,
                          text='請選擇文件',
                          width=10,
                          height=1,
                          command=self.file).grid(stick=S, padx=50)
        self.scroll = ScrolledText(self.page, width=25, height=5)
        self.scroll.grid(row=2, column=0, padx=8)
        self.scroll_2 = ScrolledText(self.page, width=25, height=5)
        self.scroll_2.grid(row=2, column=1, padx=11)
        self.bt3 = Button(self.page,
                          text='firstcp',
                          width=10,
                          height=1,
                          command=self.compared_file).grid(stick=S, padx=40)
        self.bt4 = Button(self.page,
                          text='lastcp',
                          width=10,
                          height=1,
                          command=self.compared_file_last).grid(stick=S,
                                                                padx=40)

    def file(self):
        filenames = tkinter.filedialog.askopenfilenames()
        if len(filenames) != 0:
            string_filename = ""
            for i in range(0, len(filenames)):
                string_filename += str(filenames[i]) + "\n"
            lb.config(text="您选择的文件是：" + string_filename)
        else:
            lb.config(text="您没有选择任何文件")

    def compared_file(self):
        # Required file path
        fname = 'D:\compare/testplan'
        fname2 = 'D:\compare/wirelist'
        if os.path.isfile(fname):
            testplan = open('D:\compare/testplan', 'r',
                            encoding="utf-8").read()
        else:
            self.scroll.insert(
                'insert', '请确认路径或者文件名是否正确！请将文件放在D:/compare/,\n文件应为testplan\n')
        if os.path.isfile(fname2):
            wirelist = open('D:\compare/wirelist', 'r',
                            encoding="utf-8").read()
        else:
            self.scroll.insert(
                'insert', '请确认路径或者文件名是否正确！请将文件放在D:/compare/,\n文件应为wirelist\n')

        wire = open('D:\compare/wirelist', 'r', encoding="utf-8").readlines()
        wires = [x.strip() for x in wire if x.split()]
        checkpins = open('D:\compare\checkpins.txt', 'w')
        last_list = open('D:\compare\check_long_pins.txt', 'w')
        if testplan and wirelist is not None:
            self.scroll.insert('insert', testplan)
            self.scroll_2.insert('insert', wirelist)
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

            longpins = open('D:\compare\checkpins.txt', 'r',
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
    root.geometry('430x230+30+30')
    app = MainPage(master=root)
    root.mainloop()
