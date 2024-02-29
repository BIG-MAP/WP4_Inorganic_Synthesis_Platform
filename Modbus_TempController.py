# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 12:34:05 2024

@author: thobson
"""

from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import re
from time import sleep, localtime

class TempController:
    def __init__(self,ip_addr:str,port_num:int,unit_ID:int,PV_addr_start:int=1,\
                 timer_addr_start:int=10573,total_segs:int=4, prog_addr_start:int=8336,\
                 segnum_addr_start:int=56):
        
        self.ip_addr = ip_addr  # IP address of the temperature controller
        self.port_num = port_num # Port number of the temperature controller (default 502)
        self.unit_ID = unit_ID # Temperature controller unit ID
        
        self.PV_addr_start=PV_addr_start # The start of addresses for parameters to be read (e.g process value - temp)
        self.prog_addr_start=prog_addr_start # The start of addresses for the parameters to be written (e.g setpoint)
        self.timer_addr_start=timer_addr_start # The address for the timer settings (e.g. run, end, hold)
        self.total_segs=total_segs # The number of timer steps e.g. 4 (each with one setpoint, ramp & dwell)
        self.time_0=0
        self.TC_timeout=10
        
        self.t_run_addr=self.timer_addr_start+0
        self.t_reset_addr=self.timer_addr_start+2
        self.t_run_hold_addr=self.timer_addr_start+3
        self.t_run_reset_addr=self.timer_addr_start+4

        self.pow_out_addr=PV_addr_start+3
        self.segnum_addr_start=segnum_addr_start
        
        
        self.temp_client=ModbusClient(host=self.ip_addr,port=self.port_num,timeout=self.TC_timeout)
        
    def __str__(self):
        # print("Executing __str__")
        return f"{self.ip_addr}, {self.port_num}, {self.unit_ID}"
    
    def Test_Comms(self):
        if (self.temp_client.read_holding_registers((self.PV_addr_start),1)==None):
            return False
        else:
            return True

    
    def Log_Timer_Start(self):
        # print("Executing Log_Timer_Start")
        self.time_0=localtime()
        return self.time_0
    
    def Get_Log_Time(self):
        if (self.time_0 != 0):
            return localtime()-self.time_0
        else:
            return 0
    
    def Read_Timer_Stat(self):
        try:
            read_element_list = self.temp_client.read_holding_registers(self.t_run_addr,1)
            t_run_stat=read_element_list[0]
            read_element_list = self.temp_client.read_holding_registers(self.t_reset_addr,1)
            t_reset_stat=read_element_list[0]
            read_element_list = self.temp_client.read_holding_registers(self.t_run_hold_addr,1)
            t_runhold_stat=read_element_list[0]
            read_element_list = self.temp_client.read_holding_registers(self.t_run_reset_addr,1)
            t_runreset_stat=read_element_list[0]

##            print("Run Status: "+str(t_run_stat))
##            print("Reset Status: "+str(t_reset_stat))
            
            if (t_run_stat==1):
                return "Run"
            if (t_reset_stat==1):
                return "Reset"
            if (t_runhold_stat==1):
                print(t_runhold_stat)
                return "Hold"
            if (t_runreset_stat==1):
                print(t_runreset_stat)
                return "Reset"

            
            else:
                return "End"
        
        except(self.temp_client.timeout):
           return ""
    
    def Read_Temp_Meas(self, temp_meas_addr:int=0):
        try:
            read_element_list = self.temp_client.read_holding_registers((self.PV_addr_start+temp_meas_addr),1)
            # print("Read Address Start: "+str(self.read_addr_start))
            # print("Temp Meas. Address: "+str(temp_meas_addr))
            # print("Reading Input Register: "+str(self.read_addr_start+temp_meas_addr))
            if (read_element_list != None):
                return float(read_element_list[0])
            else:
                return None
        except(self.temp_client.timeout):
            return None

    def Read_Power_Out(self):
        pow_out=self.temp_client.read_holding_registers(self.pow_out_addr,1)
        try:
            return str(float(pow_out[0])/10)
        except:
            return "0"
        
    def Read_Segment_Num(self):
        seg_num=self.temp_client.read_holding_registers(self.segnum_addr_start,1)
        try:
            return seg_num[0]
        except:
            return "0"
        
    
    def Read_Prog_Sequence(self):
        read_prog_list=[]
        for i in range(0,self.total_segs):
            seg_addr=self.prog_addr_start+(i*8)
            seg_list=self.temp_client.read_holding_registers(seg_addr,3)
            if (seg_list[0]==1):
                seg_list[2]=float(seg_list[2]/10)
            read_prog_list.append(seg_list)
        return read_prog_list
    
    def Write_Single_Value(self,value_index:int,value:int):
        self.temp_client.write_single_register(value_index, value)
        print("Writing value: "+str(value)+" to address: "+str(value_index))
        sleep(0.1)
        read_val = self.temp_client.read_holding_registers(value_index,1)
        print("Value at address from read: "+str(read_val))
        return read_val
    
    def Set_Seg_Type(self,seg_num:int,val:int):
        print("Seg_num: "+str(seg_num)+", value: "+str(val))
        seg_type_addr=(self.prog_addr_start)+((seg_num-1)*8)
        return self.Write_Single_Value(seg_type_addr, val)
    
    def Set_Single_Dwell(self,dwell_index:int,dwell:int|float):
        dwell_val=int(dwell)
        return self.Write_Single_Value(dwell_index, dwell_val)
    
    def Set_Single_Setpoint(self,SP_index:int,SP:int|float):
        SP_val=int(SP)
        return self.Write_Single_Value(SP_index, SP_val)
    
    def Set_Single_RampRate(self,ramp_index:int,ramp:int|float):
        ramp_val=int(ramp*10)
        return self.Write_Single_Value(ramp_index,ramp_val)
    
    def Set_Single_RampTime(self,ramp_index:int,ramp:int|float):
        ramp_val=int(ramp)
        return self.Write_Single_Value(ramp_index,ramp_val)
    
    def Set_Timer_Sequence(self,temp_segs:list):
        for i in range(0,self.total_segs):
            seg_num=i+1
            self.Set_Seg_Type(seg_num,temp_segs[i][0])
            
            if (temp_segs[i][0]>0):
                if(temp_segs[i][0]!=4):
                    TSP_addr=((self.prog_addr_start)+((seg_num-1)*8))+1
                    TSP_val=self.Set_Single_Setpoint(TSP_addr, temp_segs[i][1])
                    print("Setpoint for segment "+str(seg_num)+" = "+str(TSP_val))
                    
                    if (temp_segs[i][0]==1):
                        RMP_addr=((self.prog_addr_start)+((seg_num-1)*8))+2
                        RMP_val=self.Set_Single_RampRate(RMP_addr, temp_segs[i][2])
                        print("Ramp rate for segment "+str(seg_num)+" = "+str(RMP_val))
                    if (temp_segs[i][0]==2):
                        RMP_addr=((self.prog_addr_start)+((seg_num-1)*8))+2
                        RMP_val=self.Set_Single_RampTime(RMP_addr, temp_segs[i][2])
                        print("Ramp time for segment "+str(seg_num)+" = "+str(RMP_val))
                    if (temp_segs[i][0]==3):
                        DWEL_addr=((self.prog_addr_start)+((seg_num-1)*8))+2
                        DWEL_val=self.Set_Single_Dwell(DWEL_addr, temp_segs[i][2])
                        print("Dwell for segment "+str(seg_num)+" = "+str(DWEL_val))
                        
                elif(temp_segs[i][0]==4):
                    TSP_addr=((self.prog_addr_start)+((seg_num-1)*8))+1
                    TSP_val=self.Set_Single_Setpoint(TSP_addr, temp_segs[i][1])
                    print("Setpoint for step segment "+str(seg_num)+" = "+str(TSP_val))


        return self.Read_Prog_Sequence()
    
    def Run(self):
        run_val=self.Write_Single_Value(self.t_run_addr, 1)
        return run_val
    
    def Reset(self):
        return self.Write_Single_Value(self.t_reset_addr, 1)
    
    def Prog_Run_Hold(self):
        return self.Write_Single_Value(self.t_run_hold_addr, 1)
    
    def Prog_Run_Reset(self):
        return self.Write_Single_Value(self.t_run_reset_addr, 1)
    
    def End(self):
        return self.Write_Single_Value(self.t_run_addr, 0)
        
        

##temp_prog_list = [[1,300,5],[3,300,1],[1,100,5],[1,20,5]]        
##    
##
##my_controller = TempController("138.253.143.222",502,255) 


##print(my_controller)
# print(my_controller.ip_addr)
#print(my_controller.temp_client)
# print(my_controller.Set_Single_Parameter(1, 110))
# print(my_controller.Set_Single_Ramp(1,7))
# print(my_controller.Set_Timer_Sequence(temp_timer_list))
##print("Measured temp: "+str(my_controller.Read_Temp_Meas()))
##my_controller.Set_Timer_Sequence(temp_prog_list)
##print("Program Sequence: "+str(my_controller.Read_Prog_Sequence()))
##print("Timer Status: "+str(my_controller.Read_Timer_Stat()))
# print(my_controller.Run())
# print(my_controller.End())
# #print(my_controller.Read_Temp_Meas())



