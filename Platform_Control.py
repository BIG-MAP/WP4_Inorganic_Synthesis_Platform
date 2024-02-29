# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 11:06:48 2024

@author: thobson
"""

import PySimpleGUI as sg
from Input_Application import Input_App
from Orbit_Shaker_Control import Heater_Shaker_Controller
import TempController_GUI

sg.theme('SystemDefault')

class Platform_Dialog:
    
    def __init__(self):
        
        self.text_font_normal = "Arial"
        self.text_size_normal=12
        self.text_size_small=8
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
        self.width=600
        self.height=500
        self.button_width=150
        
        self.series_file_path="C:/Data/XPR_Out_Files/"
        
        
    def Create(self):
        
        window_title="Sol-Gel Synthesis Platform"
        title_ln=sg.Text("BIG-MAP WP4: Sol-Gel Synthesis Platform",font=(self.text_font_title,self.text_size_title))
        ack_ln_1=sg.Text("This project has received funding from the European Union’s Horizon 2020 research and innovation programme",\
                          font=(self.text_font_normal,self.text_size_small))
        
        ack_ln_2=sg.Text("under grant agreement No 957189. The project is part of BATTERY 2030+, the large-scale European research",\
                          font=(self.text_font_normal,self.text_size_small))
        
        ack_ln_3= sg.Text("initiative for inventing the sustainable batteries of the future.",\
                          font=(self.text_font_normal,self.text_size_small))
            
        ack_frm=sg.Frame("",[[ack_ln_1],[ack_ln_2],[ack_ln_3]])
        
        banner=sg.Image("BIGMAP_Logo.PNG")
        
        in_app_bt=sg.Button("Dosing Input",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off),\
                            key="-IN_APP-",size=self.button_width,)
        shaker_app_bt=sg.Button("Reaction Stage Control",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off),\
                                key="-SH_APP-",size=self.button_width)
        furn_app_bt=sg.Button("Furnace Control",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off),\
                              key="-FN_APP-",size=self.button_width)
        
        prog_list=[[in_app_bt],[shaker_app_bt],[furn_app_bt]]
        
        prog_frm=sg.Frame("Control Programs", prog_list)
        
        ext_bt=sg.Button("Quit",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off),key="-QUIT-")
        licence_bt=sg.Button("Licence",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off),key="-LCN-")
        
        layout=[[title_ln],[banner],[prog_frm],[ext_bt,licence_bt],[ack_frm]]
        
        return sg.Window(window_title,layout,size=(self.width,self.height),resizable=True,element_justification="c")
    
    def Run_Dialog(self):
        
        main_window=self.Create()
        
        while True:
            event, values = main_window.read()
            
            if(event=="-IN_APP-"):
                my_input_app = Input_App()
                try:
                    self.series_file_path=my_input_app.Run()
                except:
                    print("Error in input app, closing")
                    
            if(event=="-SH_APP-"):
                my_shaker_app = Heater_Shaker_Controller(dflt_in_path=self.series_file_path)
                try:
                    my_shaker_app.Run()
                except:
                    print("Error in heater shaker app, closing")
                    
            if(event=="-FN_APP-"):
                my_furnace_app = TempController_GUI.TC_Input_Dialog(imp_calc_temp_path=self.series_file_path)
                try:
                    my_furnace_app.Run_Dialog()
                except:
                    print("Error in furnace control app, closing")
                 
            if (event=="-LCN-"):
                self.Licence_Dialog()
            
            if ((event == "-QUIT-") or (event == sg.WINDOW_CLOSED)):
                break
        
        main_window.close()
        
    def Licence_Dialog(self):
        
        lines=[""]*17
        
        lines[0]="MIT License"
        lines[1]="Copyright (c) 2023 BIG-MAP"
        lines[2]="Permission is hereby granted, free of charge, to any person obtaining a copy"
        lines[3]="""of this software and associated documentation files (the "Software"), to deal"""
        lines[4]="in the Software without restriction, including without limitation the rights"
        lines[5]="to use, copy, modify, merge, publish, distribute, sublicense, and/or sell"
        lines[6]="copies of the Software, and to permit persons to whom the Software is"
        lines[7]="furnished to do so, subject to the following conditions:"
        lines[8]="The above copyright notice and this permission notice shall be included in all"
        lines[9]="copies or substantial portions of the Software."
        lines[10]="""THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR"""
        lines[11]="IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,"
        lines[12]="FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE"
        lines[13]="AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER"
        lines[14]="LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,"
        lines[15]="OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE"
        lines[16]="SOFTWARE."
        
        ln_layt=[]
        
        for i in range(0,len(lines)):
            ln_layt.append([sg.Text(lines[i],font=(self.text_font_normal,self.text_size_small),key=str(i))])
        
        ext_bt=sg.Button("Close",button_color=(self.bt_txt_colr_off,self.bt_bkgr_colr_off),key="-QUIT-")
        
        layout=[[ln_layt],[ext_bt]]
        
        window=sg.Window("Licence",layout,size=(self.width,self.height),resizable=True,element_justification="c")
        
        while True:
            event, values = window.read()
            
            if ((event == "-QUIT-") or (event == sg.WINDOW_CLOSED)):
                break
        window.close()
        
        
my_dialog=Platform_Dialog()
my_dialog.Run_Dialog()
