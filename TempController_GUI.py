# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 14:40:46 2024

@author: thobson
"""

# from pyModbusTCP.client import ModbusClient
from Modbus_TempController import TempController
import PySimpleGUI as sg
import csv
from time import time
import pandas as pd
from datetime import date, datetime

# temp_timer_list = [60,100,5,60,150,5,60,200,5,60,20,5]        
    

sg.theme('SystemDefault')

class TC_Dialog:
    
    def __init__(self):
        
        self.text_font_normal = "Arial"
        self.text_size_normal=12
        self.text_font_title = "Arial Bold"
        self.text_size_title=16
        self.text_font_display=self.text_font_title
        self.text_size_display=18
        self.text_colr_display="lime"
        self.bckgrnd_colr_display="black"
        self.bt_txt_colr_off="white"
        self.bt_bkgr_colr_off="navy"
        self.bt_txt_colr_on="navy"
        self.bt_bkgr_colr_on="white"
        self.justif_norm="left"
        
    def Read_CSV_Rows(self,file_path,start_col:int=0,col_no:int=1):
        
        vals_list=[]
        try:
            var_file = open(file_path, encoding='utf-8-sig')
            
            with var_file as csvfile:
                reader=csv.reader(csvfile,delimiter=",")
                
                for row in reader:
                    row_list=[]
                    for i in range(start_col,start_col+col_no):
                        row_list.append(row[i])
                    vals_list.append(row_list)
                    
            var_file.close()
        except:
            print("Invalid file path")
        
        return vals_list
        
    def Tog_On_Off(self,window,status:bool,event,key_on:str,key_off:str):
        
        if ((status==True) and (event==key_off)):
            window[key_on].update(button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off))
            window[key_off].update(button_color=(self.bt_txt_colr_on,self.bt_bkgr_colr_on))
            status=False
        elif ((status==False) and (event==key_on)):
            window[key_on].update(button_color=(self.bt_txt_colr_on,self.bt_bkgr_colr_on))
            window[key_off].update(button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off))
            status=True
            
        return status

class TC_Input_Dialog(TC_Dialog):
    
    def __init__(self,TC_IP="138.253.143.222",TC_port=502,TC_ID=255,\
                 imp_calc_temp_path="C:/Data/XPR_Out_Files/"):
        
        TC_Dialog.__init__(self)
        
        self.window_width=1100
        self.window_height=500
        
        self.log_stat=True
        self.t_end_stat=True
        
        self.TC_IP=TC_IP
        self.TC_port=TC_port
        self.TC_ID=TC_ID
        self.TC_timr_start_addr=10573
        self.TC_prog_start=8336
        self.TC_PV_read_start=1
        self.total_segs=4
        
        self.imp_calc_temp_path=imp_calc_temp_path
        self.imp_dflt_path="Furnace_Defaults.csv"
        self.logs_dflt_path="C:/Data/EPC3016_Out_Files/"
        
    def Create(self):
        
        t_unit="min"
        
        window_title="Input Dialog"
        
        max_tsp=1200.0
        max_rmp=10.0
        max_dwell=99.99
        
        max_tsp_str="Max: "+str(max_tsp)+" C"
        max_rmp_str="Max: "+str(max_rmp)+" C/"+str(t_unit)
        max_dwel_str="Max: "+str(max_dwell)+" "+str(t_unit)
        
        top_ln=sg.Text("Temperature Controller Input Dialog",font=(self.text_font_title,self.text_size_title))
        
        brwse_ln = sg.Text("Select input file (if using)", key='-OUT-',expand_x=True, justification=self.justif_norm)
        brwse_bx = sg.Input(self.imp_calc_temp_path,key = '-FINPUT-')
        brwse_bt = sg.FileBrowse('Browse', key='-INBROWSE-',button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off))
        fill_bt = sg.Button("Fill",key='-FILL-',button_color=self.bt_bkgr_colr_off)
        
        imp_frm=sg.Frame("File Import", [[brwse_ln],[brwse_bx,brwse_bt],[fill_bt]])
        
        series_ln = sg.Text("Process Segments",font=(self.text_font_normal,self.text_size_normal))
        
        ser_frm_lst=[[series_ln],[sg.Text("No.",font=(self.text_font_normal,self.text_size_normal))]]
            
        seg_type_list=["RampRate","RampTime","Dwell","Step","End"]
            
        #timer_maxms = []
        
        
        for i in range(0,self.total_segs):
            row_list=[]
            row_list.append(sg.Text(str(i+1),font=(self.text_font_normal,self.text_size_normal)))
            row_list.append(sg.Combo(seg_type_list,default_value=seg_type_list[0], font=(self.text_font_normal,self.text_size_normal),\
                                     expand_x=True, enable_events=True, readonly=True,size=(10,30),key="-SEGS_"+str(i+1)+"-"))
            row_list.append(sg.Text("TSP (C): ",key="-T_TYPE_"+str(i+1)+"_1-",font=(self.text_font_normal,self.text_size_normal)))
            row_list.append(sg.Input("",size=(None,50),key="-T_INPUT_"+str(i+1)+"_1-"))
            row_list.append(sg.Text("RMP (C/min): ",key="-T_TYPE_"+str(i+1)+"_2-",font=(self.text_font_normal,self.text_size_normal)))
            row_list.append(sg.Input("",size=(None,50),key="-T_INPUT_"+str(i+1)+"_2-"))
            
            ser_frm_lst.append(row_list)
            
            sg.Input()
        
        print("Input list size: "+str(len(ser_frm_lst)))
        # print(ser_frm_lst)  
        
        ser_frm=sg.Frame("Temp Series Inputs", ser_frm_lst)
        
        modbus_param_names=[sg.Text("IP Address:",font=(self.text_font_normal,self.text_size_normal)),\
                            sg.Text("Port:",font=(self.text_font_normal,self.text_size_normal)),\
                            sg.Text("Device ID:",font=(self.text_font_normal,self.text_size_normal)),\
                            sg.Text("Timer Address:",font=(self.text_font_normal,self.text_size_normal)),\
                            sg.Text("Write Registers Start:",font=(self.text_font_normal,self.text_size_normal)),\
                            sg.Text("Read Registers Start:",font=(self.text_font_normal,self.text_size_normal))]
        
        modbus_dflt_params=[self.TC_IP,self.TC_port,self.TC_ID,self.TC_timr_start_addr,\
                            self.TC_prog_start,self.TC_PV_read_start,self.total_segs]
        
        modbus_lst=[]
            
        for k in range(0,len(modbus_param_names)):
            modbus_lst.append([modbus_param_names[k],sg.Input(modbus_dflt_params[k],key="-M_INPUT_"+str(k+1)+"-")])
            
        tst_com_bt=sg.Button("Test Comms",key="-COMTEST-",button_color=self.bt_bkgr_colr_off)
        com_stat_stb=sg.Text("", enable_events=True,key="-COMSTAT-", font = (self.text_font_display, self.text_size_display),\
             text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                 expand_x=True, justification=self.justif_norm)
        
        modbus_lst.append([tst_com_bt,com_stat_stb])
            
        modbus_frm=sg.Frame("Modbus Comms Values", modbus_lst)
        
        timer_end_ln=sg.Text("Stop timer after steps complete?")
        timer_end_y_bt=sg.Button("Yes",key="-T_END_Y-",button_color=(self.bt_txt_colr_on,self.bt_bkgr_colr_on))
        timer_end_n_bt=sg.Button("No",key="-T_END_N-",button_color=self.bt_bkgr_colr_off)
            
        tmr_end_frm=sg.Frame("", [[timer_end_ln],[timer_end_y_bt,timer_end_n_bt]])
        
        logs_ln=sg.Text("Toggle logs on/off",font=(self.text_font_normal,self.text_size_normal))
        logs_on_bt=sg.Button("On",key="-LOGSON-",button_color=(self.bt_txt_colr_on,self.bt_bkgr_colr_on))
        logs_off_bt=sg.Button("Off",key="-LOGSOFF-",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off))
        
        logs_brwse_ln=sg.Text("Select path for logs file")
        logs_brwse_bx=sg.Input(self.logs_dflt_path,key = '-FOUTPUT-')
        logs_brwse_bt=sg.FileBrowse('Browse', key='-OUTBROWSE-',button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off))
        
        logs_frm=sg.Frame("", [[logs_ln],[logs_on_bt,logs_off_bt],[logs_brwse_ln],[logs_brwse_bx,logs_brwse_bt]])
        
        start_bt = sg.Button("Start Process", key='-START-', button_color=self.bt_bkgr_colr_off)
        quit_bt = sg.Button("Quit",key="-QUIT-", button_color=self.bt_bkgr_colr_off)
        
        end_frm=sg.Frame("", [[start_bt,quit_bt]])

        col_left=sg.Column([[imp_frm],[ser_frm],[end_frm,tmr_end_frm]])
        col_right=sg.Column([[modbus_frm],[logs_frm]])
        
        layout = [[top_ln],[col_left,col_right]]
        
        return sg.Window(window_title,layout,size=(self.window_width,self.window_height),resizable=True)
    
    def Update_Segment(self,window,seg_num:int,seg_type:str):
        
        # print("Updating Segment...")
        
        if (seg_type=="RampRate"):
            window["-T_TYPE_"+str(seg_num)+"_1-"].update("TSP (C):",visible=True)
            window["-T_INPUT_"+str(seg_num)+"_1-"].update(visible=True)
            window["-T_TYPE_"+str(seg_num)+"_2-"].update("RMP (C/min):",visible=True)
            window["-T_INPUT_"+str(seg_num)+"_2-"].update(visible=True)
            window["-SEGS_"+str(seg_num)+"-"].update(size=(10,30))

        if (seg_type=="RampTime"):

            window["-T_TYPE_"+str(seg_num)+"_1-"].update("TSP (C):",visible=True)
            window["-T_INPUT_"+str(seg_num)+"_1-"].update(visible=True)
            window["-T_TYPE_"+str(seg_num)+"_2-"].update("RMP (min):",visible=True)
            window["-T_INPUT_"+str(seg_num)+"_2-"].update(visible=True)
            window["-SEGS_"+str(seg_num)+"-"].update(size=(10,30))

        if (seg_type=="Dwell"):

            window["-T_TYPE_"+str(seg_num)+"_1-"].update("TSP (C):",visible=True)
            window["-T_INPUT_"+str(seg_num)+"_1-"].update(visible=True)
            window["-T_TYPE_"+str(seg_num)+"_2-"].update("DWL (hrs):",visible=True)
            window["-T_INPUT_"+str(seg_num)+"_2-"].update(visible=True)
            window["-SEGS_"+str(seg_num)+"-"].update(size=(10,30))

        if (seg_type=="Step"):

            window["-T_TYPE_"+str(seg_num)+"_1-"].update("TSP (C):",visible=True)
            window["-T_INPUT_"+str(seg_num)+"_1-"].update(visible=True)
            window["-T_TYPE_"+str(seg_num)+"_2-"].update("",visible=False)
            window["-T_INPUT_"+str(seg_num)+"_2-"].update(visible=False)
            window["-SEGS_"+str(seg_num)+"-"].update(size=(10,30))

        if (seg_type=="End"):
            window["-T_TYPE_"+str(seg_num)+"_1-"].update("",visible=False)
            window["-T_INPUT_"+str(seg_num)+"_1-"].update(visible=False)
            window["-T_TYPE_"+str(seg_num)+"_2-"].update("",visible=False)
            window["-T_INPUT_"+str(seg_num)+"_2-"].update(visible=False)
            window["-SEGS_"+str(seg_num)+"-"].update(size=(10,30))

    
    def Fill_Default_Inputs(self,window,file_path:str):
        
        fill_vals=TC_Dialog.Read_CSV_Rows(self,file_path,col_no=4)
        
        print("Size of array: "+str(len(fill_vals)))
        
        if (len(fill_vals)==self.total_segs+1) and (len(fill_vals[0])==4):
        
            for seg_num in range(1,len(fill_vals)):
                seg_type=fill_vals[seg_num][1]
                
                if ((seg_type=="End") or (seg_type=="Step") or (seg_type=="Dwell") or (seg_type=="RampRate") or (seg_type=="RampTime")):
                    window["-SEGS_"+str(seg_num)+"-"].update(seg_type)
                    
                    if ((seg_type=="Step") or (seg_type=="Dwell") or (seg_type=="RampRate") or (seg_type=="RampTime")):
                        window["-T_INPUT_"+str(seg_num)+"_1-"].update(fill_vals[seg_num][2])
                        
                        if ((seg_type=="Dwell") or (seg_type=="RampRate") or (seg_type=="RampTime")):
                            window["-T_INPUT_"+str(seg_num)+"_2-"].update(fill_vals[seg_num][3])
                            
                    self.Update_Segment(window, seg_num, seg_type)
                    
                else:
                    print("Type for segment "+str(seg_num)+" not recognised, values not filled")
            
            return fill_vals
        
        else:
            print("Input file not in expected format")
            sg.popup("Input file not in expected format")
      
    def Fill_Top_Temp(self,window,file_path:str):
        try:
            temp_vals=TC_Dialog.Read_CSV_Rows(self,file_path,start_col=7)
            print("Temp vals: "+str(temp_vals))
            print("Temp vals [1]: "+str(temp_vals[1]))
            print("Temp vals [1][0]: "+str(temp_vals[1][0]))
            window["-T_INPUT_1_1-"].update(temp_vals[1][0])
            return temp_vals[1][0]
        except:
            print("Could not read in top temp, check input file. Returning to defaults")
            sg.popup("Could not read in top temp, check input file. Returning to defaults")
    
    def Read_Prog_Boxes(self,values):
        
        inp_vals=[]
        
        for i in range(0,self.total_segs):
            if (values["-SEGS_"+str(i+1)+"-"]=="End"):
                row_vals=[0]
            elif (values["-SEGS_"+str(i+1)+"-"]=="Step"):
                try:
                    TSP_val=float(values["-T_INPUT_"+str(i+1)+"_1-"])
                    row_vals=[4,TSP_val]
                except:
                    print("Could not read in values.")
            else:
                if (values["-SEGS_"+str(i+1)+"-"]=="RampRate"):
                    row_vals=[1]
                if (values["-SEGS_"+str(i+1)+"-"]=="RampTime"):
                    row_vals=[2]
                if (values["-SEGS_"+str(i+1)+"-"]=="Dwell"):
                    row_vals=[3]

                TSP_val=float(values["-T_INPUT_"+str(i+1)+"_1-"])
                val_2=float(values["-T_INPUT_"+str(i+1)+"_2-"])
                row_vals.append(TSP_val)
                row_vals.append(val_2)

                    # print("Could not read in values.")
                
            inp_vals.append(row_vals)
        
        return inp_vals
    
    def Read_Comms_Boxes(self,values):
        
        comm_vals=[]
        
        for i in range(0,6):
            comm_vals.append(values["-M_INPUT_"+str(i+1)+"-"])
    
        return comm_vals
    
    def Start_TC(self,values):
        
        TC_comm_params=self.Read_Comms_Boxes(values)
        print(TC_comm_params)
        
        self.TC_IP=TC_comm_params[0]
        self.TC_port=int(TC_comm_params[1])
        self.TC_ID=int(TC_comm_params[2])
        self.TC_timer_addr=int(TC_comm_params[3])
        self.TC_write_start=int(TC_comm_params[4])
        self.TC_read_start=int(TC_comm_params[5])
        
        controller = TempController(self.TC_IP,self.TC_port,self.TC_ID)
            
        return controller
    
    def Send_Sequence(self,values,controller):
        
        TC_timer_params=self.Read_Prog_Boxes(values)
        print("Timer parameters to send: "+str(TC_timer_params))
        
        TC_sequence=controller.Set_Timer_Sequence(TC_timer_params)
        
        return TC_sequence
        
    def Com_Test_Dialog(self,controller):
        layout=[[sg.Text("Testing comms, please wait.")],[sg.Text("Max. wait approx 10s.")]]
        wait_win=sg.Window("Comms Test",layout=layout,size=(200,100))
        
        while True:
            event, values=wait_win.read(timeout=500)
            comms=controller.Test_Comms()
            break
        wait_win.close()
        
        print("Connection Status: "+str(comms))
        
        return comms
        
    
    def Run_Dialog(self):
        
        TC_window=self.Create()
        
        while True:
            event, values = TC_window.read()
            
            if(event!=None):
                if(event[0:5]=="-SEGS"):
                    self.Update_Segment(TC_window, int(event[6]), values[event])
            
            if(event=="-COMTEST-"):
                my_controller=self.Start_TC(values)
                print(my_controller)
                
                comms_open=self.Com_Test_Dialog(my_controller)
                if (comms_open==True):
                    print("Connected to modbus server")
                    TC_window["-COMSTAT-"].update("Connected")
                elif (comms_open==False):
                    print("No Server connection")
                    TC_window["-COMSTAT-"].update("No Connection")
            
            if ((event=="-LOGSON-") or (event=="-LOGSOFF-")):
                self.log_stat=self.Tog_On_Off(TC_window,self.log_stat,event,"-LOGSON-","-LOGSOFF-")
                
            if ((event=="-T_END_Y-") or (event=="-T_END_N-")):
                self.t_end_stat=self.Tog_On_Off(TC_window,self.t_end_stat,event,"-T_END_Y-","-T_END_N-")
                
            if(event=="-FILL-"):
                print("Default inputs path: "+self.imp_dflt_path)
                fill_sequence=self.Fill_Default_Inputs(TC_window, self.imp_dflt_path)
                top_temp=self.Fill_Top_Temp(TC_window, values["-FINPUT-"])
                
            if(event=="-START-"):
                print(self.Read_Prog_Boxes(values))
                my_controller=self.Start_TC(values)
                
                print(my_controller)
                comms_open=self.Com_Test_Dialog(my_controller)
                if (comms_open==False):
                    sg.popup("Could not establish remote connection, please check communications variables.")
                elif (comms_open==True):
                    sequence_conf=self.Send_Sequence(values,my_controller)
                    print("Sequence Confirmation: "+str(sequence_conf))

                    logs_path=values["-FOUTPUT-"]

                    my_process_dialog=TC_Process_Dialog(my_controller,sequence_conf,self.log_stat,self.t_end_stat,logs_path)
                    my_process_dialog.Run_Dialog()

                    
            
            
            if ((event == "-QUIT-") or (event == sg.WINDOW_CLOSED)):
                break
        
        TC_window.close()
    


class TC_Process_Dialog(TC_Dialog):

    def __init__(self,controller,sequence,l_stat,t_stat,lg_path,total_segs:int=4,lg_period:int|float=60):
        
        TC_Dialog.__init__(self)
        
        self.window_width=400
        self.window_height=850
        self.total_segs=total_segs
        
        self.my_controller=controller
        self.sequence=sequence
        self.log_stat=l_stat
        self.log_path=lg_path
        self.log_period=float(lg_period)
        self.t_end_stat=t_stat

        self.prog_started=False

    def Create(self):

        top_ln=sg.Text("Process Monitor",font=(self.text_font_title,self.text_size_title))

        temp_read_ln=sg.Text("Current Temperature: ", font=(self.text_font_normal,self.text_size_normal))
        temp_read_ds=sg.Text('0', enable_events=True,key='-TMP_DS-',\
                                     font = (self.text_font_display, self.text_size_display),\
                                         text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                             expand_x=True, justification=self.justif_norm)

        pow_read_in=sg.Text("Power Out: ", font=(self.text_font_normal,self.text_size_normal))
        pow_read_ds=sg.Text('', enable_events=True,key='-POW_DS-',\
                                     font = (self.text_font_display, self.text_size_display),\
                                         text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                             expand_x=True, justification=self.justif_norm)
        
        stat_read_in=sg.Text("Timer Status: ", font=(self.text_font_normal,self.text_size_normal))
        stat_read_ds=sg.Text('', enable_events=True,key='-TMR_DS-',\
                                     font = (self.text_font_display, self.text_size_display),\
                                         text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                             expand_x=True, justification=self.justif_norm)

        seg_read_in=sg.Text("Working Segment: ", font=(self.text_font_normal,self.text_size_normal))
        seg_read_ds=sg.Text('', enable_events=True,key='-SEG_DS-',\
                                     font = (self.text_font_display, self.text_size_display),\
                                         text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                             expand_x=True, justification=self.justif_norm)
        
        tmp_read_frm=sg.Frame("",[[temp_read_ln,temp_read_ds],[pow_read_in,pow_read_ds],\
                                  [stat_read_in,stat_read_ds],[seg_read_in,seg_read_ds]],size=(350,200))
            
        prog_param_lst=[]
        prog_ds_lst=[]
        
        for i in range(0,self.total_segs):
            seg_num=i+1
            if (self.sequence[i][0]==0):
                seg_list=[sg.Text("S"+str(seg_num)+":",font=(self.text_font_normal,self.text_size_normal))]
                seg_list.append(sg.Text("End",font=(self.text_font_normal,self.text_size_normal)))
                prog_param_lst.append(seg_list)
                
            if (self.sequence[i][0]==4):
                seg_list=[sg.Text("S"+str(seg_num)+":",font=(self.text_font_normal,self.text_size_normal))]
                seg_list.append(sg.Text("Step",font=(self.text_font_normal,self.text_size_normal)))
                seg_list.append(sg.Text('0 C', enable_events=True,key='-DS_'+str(seg_num)+'_1-',\
                                         font = (self.text_font_display, self.text_size_display),\
                                             text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                                 expand_x=True, justification=self.justif_norm))
                prog_param_lst.append(seg_list)
                
            if (self.sequence[i][0]==1):
                seg_list=[sg.Text("S"+str(seg_num)+":",font=(self.text_font_normal,self.text_size_normal))]
                seg_list.append(sg.Text("RampRate",font=(self.text_font_normal,self.text_size_normal)))
                seg_list.append(sg.Text('0 C', enable_events=True,key='-DS_'+str(seg_num)+'_1-',\
                                         font = (self.text_font_display, self.text_size_display),\
                                             text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                                 expand_x=True, justification=self.justif_norm))
                seg_list.append(sg.Text('0 C/min', enable_events=True,key='-DS_'+str(seg_num)+'_2-',\
                                         font = (self.text_font_display, self.text_size_display),\
                                             text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                                 expand_x=True, justification=self.justif_norm))
                prog_param_lst.append(seg_list)
                
            if (self.sequence[i][0]==2):
                seg_list=[sg.Text("S"+str(seg_num)+":",font=(self.text_font_normal,self.text_size_normal))]
                seg_list.append(sg.Text("RampTime",font=(self.text_font_normal,self.text_size_normal)))
                seg_list.append(sg.Text('0 C', enable_events=True,key='-DS_'+str(seg_num)+'_1-',\
                                         font = (self.text_font_display, self.text_size_display),\
                                             text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                                 expand_x=True, justification=self.justif_norm))
                seg_list.append(sg.Text('0 min', enable_events=True,key='-DS_'+str(seg_num)+'_2-',\
                                         font = (self.text_font_display, self.text_size_display),\
                                             text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                                 expand_x=True, justification=self.justif_norm))
                prog_param_lst.append(seg_list)

            if (self.sequence[i][0]==3):
                seg_list=[sg.Text("S"+str(seg_num)+":",font=(self.text_font_normal,self.text_size_normal))]
                seg_list.append(sg.Text("Dwell",font=(self.text_font_normal,self.text_size_normal)))
                seg_list.append(sg.Text('0 C', enable_events=True,key='-DS_'+str(seg_num)+'_1-',\
                                         font = (self.text_font_display, self.text_size_display),\
                                             text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                                 expand_x=True, justification=self.justif_norm))
                seg_list.append(sg.Text('0 hrs', enable_events=True,key='-DS_'+str(seg_num)+'_2-',\
                                         font = (self.text_font_display, self.text_size_display),\
                                             text_color=self.text_colr_display, background_color=self.bckgrnd_colr_display,\
                                                 expand_x=True, justification=self.justif_norm))
                prog_param_lst.append(seg_list)
                
        prog_ds_frm=sg.Frame("Timer Variables",prog_param_lst,size=(350,50*self.total_segs))
        
        start_bt=sg.Button("Start",key="-START-",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off))
        pause_bt=sg.Button("Pause",key="-PAUSE-",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off))
        reset_bt=sg.Button("Reset",key="-RESET-",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off))
        
        exit_bt=sg.Button("Exit",key="-QUIT-",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off))
        
        tmr_bt_frm=sg.Frame("",[[start_bt,pause_bt,reset_bt],[exit_bt]])
        
        layout=[[top_ln],[prog_ds_frm],[tmp_read_frm],[tmr_bt_frm]]
        
        return sg.Window("Process Monitor",layout,size=(self.window_width,self.window_height))
    
    def Save_Logs(self,lg_dct:dict,lg_head:list):
        
        df_log=pd.DataFrame(lg_dct,columns=lg_head)
        log_file_name = 'Furnace_Logs_'+str(date.today())+'_'+str(datetime.now().strftime('%H%M%S')+'.csv')
        
        log_file = df_log.to_csv((self.log_path+log_file_name),index=False,sep=',',columns=lg_head)

        print('Logs saved at: '+self.log_path+log_file_name)
        sg.popup('Logs saved at: '+self.log_path+log_file_name)
        

    def Update_Sequence(self,window):
        for i in range(0,self.total_segs):
                seg_num=i+1
                if (self.sequence[i][0]!=0):
                    if (self.sequence[i][0]==4):
                        window["-DS_"+str(seg_num)+"_1-"].update(str(self.sequence[i][1])+" C")
                    elif(self.sequence[i][0]==1):
                        window["-DS_"+str(seg_num)+"_1-"].update(str(self.sequence[i][1])+" C")
                        window["-DS_"+str(seg_num)+"_2-"].update(str(self.sequence[i][2])+" C/min")
                    elif(self.sequence[i][0]==2):
                        window["-DS_"+str(seg_num)+"_1-"].update(str(self.sequence[i][1])+" C")
                        window["-DS_"+str(seg_num)+"_2-"].update(str(self.sequence[i][2])+" min")
                    elif(self.sequence[i][0]==3):
                        window["-DS_"+str(seg_num)+"_1-"].update(str(self.sequence[i][1])+" C")
                        window["-DS_"+str(seg_num)+"_2-"].update(str(self.sequence[i][2])+" hrs")
        
    def Run_Dialog(self):
        
        if (self.log_stat==True):
            
            time_0=time()
            j=0
            
            log_dict={}
            log_headings=["Time (s)","Temp (C)","Power (%)","Status","Segment"]


            for i in range(0,len(log_headings)):
                log_dict[log_headings[i]]=[]

        
        TC_window=self.Create()
        
        while True:
            event, values = TC_window.read(timeout=1000)
            
            temp_read=self.my_controller.Read_Temp_Meas()
            TC_window["-TMP_DS-"].update(str(temp_read)+" C")

            pow_read=self.my_controller.Read_Power_Out()
            TC_window["-POW_DS-"].update(str(pow_read)+" %")
            
            stat_read=self.my_controller.Read_Timer_Stat()
            TC_window["-TMR_DS-"].update(stat_read)

            seg_read=self.my_controller.Read_Segment_Num()
            TC_window["-SEG_DS-"].update(seg_read)

            self.Update_Sequence(TC_window)

            # print("Log stat: "+str(self.log_stat)+", Prog stat: "+str(self.prog_started))
            
            
            if ((self.log_stat==True) and (self.prog_started==True)):
                time_elapsed=time()-time_0
                # print("Time elapsed: "+str(time_elapsed))
                if ((time_elapsed/self.log_period)>float(j)):
                    log_dict[log_headings[0]].append(round(time_elapsed,0))
                    log_dict[log_headings[1]].append(temp_read)
                    log_dict[log_headings[2]].append(pow_read)
                    log_dict[log_headings[3]].append(stat_read)
                    log_dict[log_headings[4]].append(seg_read)
                    j=j+1
                    print("Logging...")

            if (event=="-START-"):
                run_val=self.my_controller.Run()
                if (run_val[0]==1):
                    self.prog_started=True
                    time_0=time()

            if (event=="-PAUSE-"):
                pse_val=self.my_controller.Prog_Run_Hold()
                print("Pause value: "+str(pse_val))

            if (event=="-RESET-"):
                if (self.prog_started==False):
                    rst_val=self.my_controller.Reset()
                elif (self.prog_started==True):
                    rst_val=self.my_controller.Reset()
                print("Reset value: "+str(rst_val))
            
            
            
            if ((event == "-QUIT-") or (event == sg.WINDOW_CLOSED)):
                if ((self.log_stat==True) and (self.prog_started==True)):
                    self.Save_Logs(log_dict, log_headings)
                break
        
        TC_window.close()
        
        
        
    
# my_input_dialog=TC_Input_Dialog()
# my_process_dialog=TC_Process_Dialog()

# my_window_1=my_input_dialog.Run_Dialog()
# my_window_2=my_process_dialog.Run_Dialog()


    
    




        
        
        
        
