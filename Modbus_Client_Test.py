# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 10:19:35 2024

@author: thobson
"""

from pyModbusTCP.client import ModbusClient
from time import sleep

test_client = ModbusClient(host='138.253.19.147', port=1502)

read1 = test_client.read_input_registers(22,2)


sleep(2)

temp_series = [60,100,5,60,150,5,60,200,5,60,20,5]
regs_series = [1280,1281,1282,1283,1284,1285,1286,1287,1288,1289,1290,1291]

register_start = 1279

for i in range (0,len(temp_series)):
    write1 = test_client.write_single_register((i+register_start),temp_series[i])
    print(write1)
    
sleep(0.3)
    
read2 = test_client.read_holding_registers(register_start,len(temp_series))

write2 = test_client.write_multiple_registers(12, temp_series)

print(read1)
print(read2)
