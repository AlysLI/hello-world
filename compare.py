import re
# Required file path
testplan = open('D:\compare/testplan', 'r', encoding="utf-8").read()
wirelist = open('D:\compare/wirelist', 'r', encoding="utf-8").read()
wire = open('D:\compare/wirelist', 'r', encoding="utf-8").readlines()
wires = [x.strip() for x in wire if x.split()]
pwr_check = open('D:\compare/pwr_check', 'r', encoding="utf-8").read()
checkpins = open('checkpins.txt', 'w')
last_list2 = open('check_long_pins_org.txt', 'w')
last_list = open('check_long_pins.txt', 'w')

#key words to extract the coordinate
start_fun = 'functional'
start_digi = 'digital'
start_power = 'powered shorts'
power = 'powered analog'
pwr_check = 'pwr_check'
end = "end test"
pattern = re.compile(
    '!.*digital.*?/.*?!|!.*analog.*?/.*?!|!.*mixed.*?/.*?!|!.*looptest 3.*?/.*?',
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
    pattern2 = re.compile('[^\n]*%s[^.]*' % i)
    search = pattern2.findall(endtest)
    for s in search:
        lines = s.split('\n')
        line = [x.strip() for x in lines if x.split()]
        for lin in line:
            if lin in wires:
                wires.remove(lin)
for w in wires:
    checkpins.write('%s\n' % w)
checkpins.close()

longpins = open('checkpins.txt', 'r', encoding="utf-8").read()
re1 = start_fun + '(.*?)' + end
re2 = start_digi + '(.*?)' + end
re3 = start_power + '(.*?)' + end
re4 = pwr_check + '(.*?)' + end
# generic_re是個元組[(.....)]
generic_re = re.compile("(%s|%s)" % (re2, re4), re.S).findall(longpins)
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

for line in wire:
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
    # gpconnect = eval(gpconnect)
    if gpconnect not in wirepins:
        if gpconnect in allpins:
            wirepins.append(gpconnect)

#test 18275s文件長針加入長針清單
l_list2 = []
s_list = []
check_long = open('D:\compare/18275s', 'r', encoding="utf-8").read()
pattern5 = re.compile('Open #1.*[^Message]', re.S)
last = pattern5.findall(check_long)
for s in last:
    lines = s.split('\n')
    line = [x.strip() for x in lines if x.split()]
    for i in line:
        lin = re.compile('[0-9a-zA-Z\_]+').findall(i)
        for l in lin:
            l_list2.append(l)
for i in l_list2:
    i = '"%s"' % i.upper()
    # if i not in wirepins:
    if i in allpins:
        s_list.append(i)
print(s_list)

#test 18275long文件長針加入長針清單
l_list = []
check_long = open('D:\compare/18275long', 'r', encoding="utf-8").read()
pattern5 = re.compile('Short #1.*[^Total]', re.S)
last = pattern5.findall(check_long)
for s in last:
    lines = s.split('\n')
    line = [x.strip() for x in lines if x.split()]
    for i in line:
        lin = re.compile('[0-9a-zA-Z\_]+').findall(i)
        for l in lin:
            l_list.append(l)
for i in l_list:
    i = '"%s"' % i.upper()
    if i not in wirepins:
        if i in allpins:
            wirepins.append(i)

#長針清單
for pins in wirepins:
    if 'GND' not in pins:
        # markspins = '"%s"' % pins
        markspins = pins.upper()
        if not any(longpin in markspins for longpin in s_list):
            last_list.write('short "GND" to %s\n' % markspins)
            longpinslist.append(markspins)

last_list.writelines('\n\n\n!Probe list\nthreshold      1000\n')
short_list = []
for pins in allpins:
    markspins = pins.upper()
    if not any(longpin in markspins for longpin in longpinslist):
        last_list.write('nodes %s\n' % markspins)
        short_list.append(markspins)

last_list.write('\n\n\n!Long probe list\n')
for pins in longpinslist:
    if 'GND' not in pins:
        # markspins = '"%s"' % pins
        markspins = pins.upper()
        last_list.write('nodes %s\n' % markspins)

last_list.close()

with open("check_long_pins.txt", encoding="utf-8", mode="a") as file:
    file.write('nodes "GND"')
with open('check_long_pins.txt', 'r+') as f:
    content = f.read()
    f.seek(0, 0)
    f.write(
        '!Long probe list\n!Total %spcs long probes\n!Total %spcs short probes\nreport netlist, common devices\nthreshold      25\nsettling delay 50.0u\n'
        % (len(longpinslist), len(short_list)) + content)

# ll = open('long.txt', 'w')
# check_long = open('D:\compare/long_probe_Shannon48CR_new.txt',
#                   'r',
#                   encoding="utf-8").readlines()
# check_long = [x.strip() for x in check_long]
# for i in check_long:
#     long = '"%s"' % i
#     if not any(longpin in long for longpin in longpinslist):
#         ll.write('%s\n' % long)
