import re
import os
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
# Required file path
wirelist_path = 'D:\compare\wirelist'
testplan_path = 'D:/compare/testplan'
local_path = 'D:\compare\check_long_wirelist.txt'

f1 = open(wirelist_path, 'r')
wirelist = f1.readlines()
f1.close()
f2 = open(testplan_path, 'r')
testplan = f2.readlines()
f2.close()
allpin = open(local_path, 'w')

#key words to extract the coordinate
start_fun = 'functional'
end_fun = 'end test'
start_digi = 'digital'
end_digi = 'end test'
start_power = 'powered shorts'
end_power = 'end test'
str_allpin = 'wire'

#Logic for obtaining documents
wirelist = [x.strip() for x in wirelist]
wirepins = []
pat = re.compile(start_fun + '(.*?)' + end_fun, re.S)
result_f = pat.findall(wirelist)
pat2 = re.compile(start_digi + '(.*?)' + end_digi, re.S)
result_d = pat2.findall(wirelist)
pat3 = re.compile(start_power + '(.*?)' + end_power, re.S)
result_p = pat3.findall(wirelist)
outfile.write('!Long probe list\nthresold      25\n')
for tplan in testplan:
    if str_allpin in tplan:
        pattern = re.compile('"(.*)"')
        str_re1 = pattern.findall(line)
        ssline = str_re1[0]
        if ssline not in wirepins:
            wirepins.append(ssline)
for long in wirepins:
    markspins = '"%s"' % pins
    markspins = markspins.upper()
    allpin.write('short "GND" to "%s"\n' % markspins)

wirepins.write('Probe list')
# for line in wirelist:
#     if str_allpin in line:
#         pattern = re.compile('"(.*)"')
#         str_re1 = pattern.findall(line)
#         ssline = str_re1[0]
#         if ssline not in wirepins:
#             wirepins.append(ssline)

# for pins in wirepins:
#     markspins = '"%s"' % pins
#     markspins = markspins.upper()
#     allpin.write('node %s\n' % markspins)

#start：test shorts "long_pins"
#end：emd test
