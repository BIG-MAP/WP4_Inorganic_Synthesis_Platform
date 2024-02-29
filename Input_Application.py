# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 09:24:01 2023

@author: thobson
"""
from __future__ import print_function
import io
from os import path

import numpy as np

import pandas as pd #   Needed for file output

import csv
import requests
import PySimpleGUI as sg
import pyautogui as pag

from datetime import date
from datetime import datetime

from datetime import date

from time import sleep

sg.theme('SystemDefault')   # Defines the theme of the dialog boxes

class Input_App:
    
    def __init__(self):

        print('SOL-GEL Input Application Local v5, BIGMAP WP4, University of Liverpool\n')
        self.Read_Mat_Files()

    def Read_Mat_Files(self):


        mat_file_path = "Materials Information.csv"
        print("Materials information source file: "+mat_file_path)  # States the source file for the materials info table
        
        
        var_file_path = "Default Fixed Variables.csv"
        print("Default fixed variables source file: "+var_file_path)    # States the source file for the 'fixed' variables info table
        
        
        self.Mat_Vals_In = []   # Inititalises an array to contain the material values
        
        mat_file = open(mat_file_path, encoding='utf-8-sig')
        
        with mat_file as csvfile:       # Reads the materials info file row by row and adds the data to the array
            reader = csv.reader(csvfile, delimiter =',')
            for row in reader:
                self.Mat_Vals_In.append(row)    # Instead of a single value, it nests each row as a list of values within the larger list
                
        mat_file.close()    # Close the input file to allow the others to be read
        
        Var_Vals_In = []
        
        var_file = open(var_file_path, encoding='utf-8-sig')
        
        with var_file as csvfile:       # Reads the input file row by row and adds the data to the array
            reader = csv.reader(csvfile, delimiter =',')
            for row in reader:
                Var_Vals_In.append(row)    # Also nests each row as a list of values within the larger list
                
        var_file.close()    # Close the input file, we should now have all the info we need to calculate weights
        
        self.in_path_valid=False
        
        self.tol = '1'   # Default tolerance in %
        self.nmc_mass = Var_Vals_In[0][1]  # Default NMC Mass in g
        self.al_sol_ratio = 1 # Default Al sol gel precursor to NMC ratio in mol%

        self.liq_vol = Var_Vals_In[1][1] # Default total liquid volume in ml
        self.mol_etacac_solid = Var_Vals_In[2][1]    # Default mol ratio EtAcAc:Solid
        self.conc_al_trisec = Var_Vals_In[3][1]   # Default concentration of Al-triSec in mol/L
        self.conc_etacac_al = Var_Vals_In[4][1]   # Default concentration of EtAcAc in Al/IPA
        self.conc_tot = Var_Vals_In[5][1]     # Default total concentration in mol/kg
        self.conc_mol_etacac = Var_Vals_In[6][1]  # Default concentration in mols EtAcAc/kg
        
        self.default_list = [self.nmc_mass, self.al_sol_ratio, self.tol, self.liq_vol, self.mol_etacac_solid, self.conc_al_trisec, self.conc_etacac_al, self.conc_tot, self.conc_mol_etacac]

        self.max_samps = 30  # Max number of samples that can fit on the balance

        self.default_stirr = ""  # The current standard stirrer to be used, with "" meaning no stirrer

        self.Method_ID = "M78"   # ID of the method being used

        self.send_file_path = "C:/Data/XPR_In_Files/"

        self.ext_file_path = "C:/Data/XPR_Out_Files/"




# Note, if you intend to input values manually, put them in as strings




# print("Solid mass = "+str(nmc_mass)+" g, Tolerance = "+str(tol)+" %\n")

#------------------------------------------------------------------------------
#-------------------------- Function Definitions ------------------------------
#------------------------------------------------------------------------------



    def Calc_Weights_All(self,c_dict,vari_paras,Mat_Vals):       # Defines a function that takes the arrays from the input files and calculates weights (note that maths is done on whole columns at a time)
           
        mass_g_NMC = c_dict[vari_paras[1]] # Since this value is fixed a list of the value is made with the same length as the targets list
        
        # print(mass_g_NMC)
        
        nNMC = np.divide(mass_g_NMC,float(Mat_Vals[1][1]))  # Value from mat_vals[1][1] is 2nd value of 2nd row, as counting starts from 0
        # print('nNMC Value: '+str(nNMC))
        
        nAltriSec = np.multiply(np.multiply(c_dict[vari_paras[0]],2),np.divide(nNMC,np.subtract(100,c_dict[vari_paras[0]])))   # Makes new list by applying maths operations to input list
        
        # print('nAl-triSec: '+str(nAltriSec))
        
        nEtAcAc_total = np.multiply(nNMC,c_dict[vari_paras[4]])
        # print('nEtAcAc Total: '+str(nEtAcAc_total))

        mass_g_Al_sol = np.multiply(np.divide(nAltriSec,c_dict[vari_paras[7]]),1000)    # This is a list of the calculated Al sol weights in g
        # print('Mass g Al sol: '+str(mass_g_Al_sol))
        
        nEtAcAc_from_solution = np.multiply(np.divide(mass_g_Al_sol,1000),c_dict[vari_paras[6]])
        # print('nEtAcAc from Solution: '+str(nEtAcAc_from_solution))
        
        mass_EtAcAc_pure = np.multiply((np.subtract(nEtAcAc_total,nEtAcAc_from_solution)),float(Mat_Vals[3][1]))    # This is a list of the calculated pure EtAcAc weights in g
        # print('Mass EtAcAc Pure: '+str(mass_EtAcAc_pure))
        
        vol_EtAcAc = np.divide(mass_EtAcAc_pure,float(Mat_Vals[3][2]))
        # print('Vol EtAcAc: '+str(vol_EtAcAc))
        
        tol_liq_vol = np.multiply(c_dict[vari_paras[3]],mass_g_NMC)
        
        vol_IPA = np.subtract(tol_liq_vol,(np.add(np.divide(vol_EtAcAc,1.2),mass_g_Al_sol)))
        # print('Vol IPA: '+str(vol_IPA))
        
        mass_IPA = np.multiply(vol_IPA,float(Mat_Vals[4][2]))   # This is a list of the calculated IPA weights in g
        # print('Mass IPA: '+str(mass_IPA))
        
        return (mass_g_NMC,mass_g_Al_sol,mass_EtAcAc_pure,mass_IPA)    # Returns lists with the 4 relevant weights
    
    def Start_Dialog(self):
        
       l1 = sg.Text("Enter number of samples",font=('Arial',12))
       box1 = sg.Input('11', enable_events=True,key='-INPUT1-', expand_x=False, justification='left')
       l2 = sg.Text("Min 1, Max 30, Default 11")
       b1 = sg.Button("OK", key='-OK-')
       b2 = sg.Button("Quit", key='-QUIT-')
       
       l3 = sg.Text('Parameter to vary:')
       
       variables = ['Al sol gel precursor mol%','NMC mass g', 'Tolerances in %',\
                    'Total liquid vol per g solid in ml','Mol ratio EtAcAc to solid mol%','Concentration Al-triSec mol/L',\
                        'Conc EtAcAc in Al/IPA','Concentration mol/kg tot','Concentration molEtACAC/kg tot']
           
       vars_list = sg.Combo(variables, default_value=variables[0], font=('Arial', 12),  expand_x=True, enable_events=True,  readonly=True, key='-VARS-') # Creates a menu from which a user can selecr which paramater to vary
       
       self.to_vary = variables[0]  # Default variable parameter is al sol mol%
       
       layout = [[l1],[box1],[l2],[l3],[vars_list],[b1,b2]]
       
       window_samps = sg.Window("Sample Number", layout, size=(350,250)) # Start a dialog box with the layout defined above
       
       I_Vals = []
       d_out = []
       r_dat=[]
       s_name = ''
       appr = False
       fxd_val_lst=[]
       samp_num = 11   # Default number of samples
       param_num = 9   # Number of independent parameters (including one tolerance)
       
       while True:
           event, values = window_samps.read()
           
           if (event == '-VARS-'):     # Allows user to select which independent parameter to vary
               self.to_vary = values['-VARS-']
               print('Parameter to vary: '+str(self.to_vary))
           
           if (event == '-OK-'):
               if (values['-INPUT1-'] != ''):
                   samp_num = int(values['-INPUT1-'])
                   if ((samp_num < 1) or (samp_num > self.max_samps)):
                       sg.popup("Please enter a value between 1 and "+str(self.max_samps))
                   else:
                       I_Vals, d_out, r_dat, s_name, appr, fxd_val_lst = self.Input_Dialog(samp_num,param_num,variables,self.to_vary)
                       if (appr == True):
                           break
               else:
                   sg.popup("Please enter a value between 1 and 30")
           
           if (event == "-QUIT-" or event == sg.WIN_CLOSED):
               break
       
       window_samps.close()


       return(samp_num, I_Vals, d_out, r_dat, s_name, appr, fxd_val_lst)
    
    
    def Input_Dialog(self,s_num,p_num,vrbls,var_param):     # Creates a dialog box for a user to upload target mol% values or enter manually
        
       box_width = 25

       var_num = vrbls.index(var_param)
       
       l0_0 = sg.Text("Name of sample series (will default to series ID if left blank)",font=('Arial',12))
       box0_0 = sg.Input('', size=((box_width*2),None), enable_events=True,key='-INPUT0_0-') 
       
       
       l1 = sg.Text("Select csv file to upload values from col 1: ",font=('Arial',12)) # The test that will appear in the dialog box

       
       l2 = sg.Text(var_param,font=('Arial',12))
       
       l3_1 = sg.Text("Rack reaction temp in C",font=('Arial',12))
       l3_2 = sg.Text("Rack stirring speed in RPM",font=('Arial',12))
       l3_3 = sg.Text("Rack stirring time in mins",font=('Arial',12))
       l3_4 = sg.Text("Calcination temp in C",font=('Arial',12))
       
       box3_1 = sg.Input("80", size=(box_width,None), enable_events=True,key='-INPUT10-')
       box3_2 = sg.Input("450", size=(box_width,None), enable_events=True,key='-INPUT11-')
       box3_3 = sg.Input("30", size=(box_width,None), enable_events=True,key='-INPUT12-')
       box3_4 = sg.Input("400", size=(box_width,None), enable_events=True,key='-INPUT13-')
       
       f3 = sg.Frame("Reaction Stage Parameters",[\
           [l3_1,box3_1],\
               [l3_2,box3_2],\
                   [l3_3,box3_3],\
                       [l3_4,box3_4]],\
                         title_color='black')
       
       samp_boxes = [[l2]]
       
       for i in range (1,(s_num+1)):   # Makes a number of input boxes equal to the number of samples
           samp_boxes.append([sg.Input('0', size=(box_width,None), enable_events=True,key='-INPUT'+str(var_num+1)+'_'+str(i)+'-')])
           
       
       box12 = sg.Input(key = '-FINPUT-')  # Input box for file path to get data from
       
       b1 = sg.Button("Calculate", key='-SUBMIT-')
       b2 = sg.Button("Back", key='-QUIT-')
       b3 = sg.FileBrowse('Browse', key='-BROWSE-')
       b4 = sg.Button("Fill", key = '-FILL-')  # Clickable buttons and their events

       fixd_col_list = [[l1],[box12,b3],[b4],[l0_0],[box0_0]]  # Makes a list for the left-hand column, starting with the fixed elements

       for v in range(0,len(vrbls)):
           if (v != var_num):
               fixd_col_list.append([sg.Text(vrbls[v],font=('Arial',12)),sg.Input(self.default_list[v], size=(box_width,None), enable_events=True,key='-INPUT'+str(v+1)+'-')])
       
       layout = [
                 [sg.Column(fixd_col_list),\
                 sg.Column(samp_boxes),f3,\
                     ],\
                     [b1,b2],\
                 ]     # Define the layout of the dialog box, using the elements above (cannot be used more than once)
           
       if (s_num <= 14):
           win_height = 455
       else:
           win_height = 455 + (25*(s_num-14))  # Scales the size of the dialog box to match the number of samples
           
       window_in = sg.Window("Sol-Gel Process Input", layout, size=(1100,win_height),resizable=True) # Start a dialog box with the layout defined above
       
       Out_Values = []     # Initialise the array which will contain the target values
       data_Check = []      # Initialise the data array containing the masses to be adjusted by the user if needed
       data_new = []        # initialise the array that will be returned by the scan dialog containing any chaneg smade by the user
       process_data = []
       fixed_val_list=[]           # List containing the fixed values defined by the user, to allow for output calculations
       series_name = ''
       approval = False
       
       while True:
           event, values = window_in.read()
       
           if (event == '-FILL-'):     # Once the user has selected an input file with the 'Browse' button, this will fill the input boxes
               if ((path.exists(values['-FINPUT-']) == True) and (values['-FINPUT-'][-4:]=='.csv')):   # Action will only happen if a valid file path is selected
                   choose_file_path = values['-FINPUT-']
                   choose_file = open(choose_file_path, encoding = 'utf-8-sig')    # Opens the selected file
                   
                   with choose_file as csvfile:
                       reader=csv.reader(csvfile, delimiter = ',')
                       
                       i = 0
                       
                       for row in reader:
                           if (i<=(s_num)):
                               if (i>0):
                                   try:
                                       window_in['-INPUT'+str(var_num+1)+'_'+str(i)+'-'].update(row[var_num])    # Fills the column with the variable parameter
                                   except:
                                       sg.popup("Input file does not match the expected import format. Check the correct values have been read in.")
                                       break
                                   if (i == 1):
                                       if (len(row)<13):
                                           sg.popup("Input file does not match the expected import format. Check the correct values have been read in.")
                                       for j in range (1,(len(row)+1)):   # Reads in the 'fixed' values and reaction parameters from the template file
                                           if ((row[j-1] != '') and (j != (var_num+1))):      # Fixed values are only read in if the parameter field is not left blank and the variable parameter is not being read
                                               try:
                                                   window_in['-INPUT'+str(j)+'-'].update(row[j-1]) # Fills the input boxes with the fixed values
                                               except:
                                                   sg.popup("Input file does not match the expected import format. Check the correct values have been read in.")
                                                   break


                               i = i + 1
                   
                   # print(choose_file_path)
                   
                   self.in_path_valid=True
                   
                   choose_file.close()
       
               else:
                   sg.popup('Please select a csv file in a valid path') # If file path is not vaild, this pop-up appears
               
           if event == '-SUBMIT-':
               
               calc_dict ={}   # Dictionary to hold all variables in columns
               
               for k in range (0,len(vrbls)):
                   if (k != var_num):
                       if (values['-INPUT'+str(k+1)+'-'] == ''):   # If the user deletes the values in the box, '0' is read instead
                           calc_dict[vrbls[k]] = [0.0]*s_num
                       else:
                           try:
                               calc_dict[vrbls[k]] = [float(values['-INPUT'+str(k+1)+'-'])]*s_num # Reads the fixed values put in the input boxes
                           except:
                               calc_dict[vrbls[k]] = [0.0]*s_num # If the user attempts to input non-numbers (e.g. text) 0 will input instead
                           
                   elif (k == var_num):
               
                       if len(Out_Values) == 0:
                           for i in range(1,(s_num+1)):
                               try:
                                   Out_Values.append(float(values['-INPUT'+str(var_num+1)+'_'+str(i)+'-']))  # Adds the input values to the list if it is empty
                               except:
                                   Out_Values.append(0.0)  # If float conversion fails (e.g. if user inputs text, 0 will be input instead)
                                   
                       elif len(Out_Values) > 0:
                           Out_Values=[]
                           for j in range (1,(s_num+1)):
                               try:
                                   Out_Values.append(float(values['-INPUT'+str(var_num+1)+'_'+str(i)+'-']))   # Updates the list with current input values if it is not empty
                               except:
                                   Out_Values.append(0.0)   # If float conversion fails (e.g. if user inputs text, 0 will be input instead)
                                   
                       calc_dict[vrbls[var_num]] = Out_Values
                       

               data_Check = self.Calc_Weights_All(calc_dict,vrbls,self.Mat_Vals_In)
                           
               
               series_name=values['-INPUT0_0-']
               
               approval, data_new = self.Scan_Dialog(s_num,series_name,Out_Values,data_Check,calc_dict[vrbls[2]],var_param,approval)     # Opens a second dialog box so users can check the calculated values before submitting

               
               if (len(process_data) == 0):   # Makes a series with the input reaction parameters to send to orbit shaker input file
                   for l in range(10,14):
                       try:
                           process_data.append(values['-INPUT'+str(l)+'-'])
                       except:
                           process_data.append('0')
                           
               elif (len(process_data) > 0):
                   process_data=[]
                   for l in range(10,14):
                       try:
                           process_data.append(values['-INPUT'+str(l)+'-'])
                       except:
                           process_data.append('0')
               
               fixed_val_list=[]           # List containing the fixed values defined by the user, to allow for output calculations
               
               for l in range (0,len(vrbls)):
                   if (l != var_num):
                       sublist=[]
                       sublist.append(vrbls[l])
                       sublist.append(values['-INPUT'+str(l+1)+'-'])
                       fixed_val_list.append(sublist)  # Ensures that each value is associated with its parameter name, as the order will vary
               
               if approval == True:    # If the user clicked 'Submit' on the output window, this window will also close
                   break
              
           if (event == "-QUIT-" or event == sg.WIN_CLOSED):
               break
           
       window_in.close()
       
       print("Fixed values list: "+str(fixed_val_list))
       print("Rack Data: "+str(process_data))

       return(Out_Values,data_new,process_data,series_name,approval,fixed_val_list)  # Returns the array of target values (note, these will be strings, not floats)
    
    def Scan_Dialog(self,samp_no,s_name,Inp_Vals,data_out,Perc_Tol_Out,vrbl,aprvl): # Dialog box where user can edit calculated values and scan sample IDs
        
        is_complete = False
        box_width = 22  # Width of the input boxes
        dec_places = 3  # This is the precision weights need to be in to be usable by the balance
        
        l1 = sg.Text("Process Parameters are shown below, please check/edit values, scan vials and place in positions", font=('Arial',12))
        
        col_list_0=[[sg.Text("No.")]]
        col_list_1=[[sg.Text("SampleID")]]
        col_list_2=[[sg.Text("Mass NMC / g")]]
        col_list_3=[[sg.Text("Tol NMC / % (min 1%)")]]
        col_list_4=[[sg.Text("Mass IPA / g")]]
        col_list_5=[[sg.Text("Tol IPA / % (min 1%)")]]
        col_list_6=[[sg.Text("Mass EtAcAc / g")]]
        col_list_7=[[sg.Text("Tol EtAcAc / % (min 1%)")]]
        col_list_8=[[sg.Text("Mass Al Sol / g")]]
        col_list_9=[[sg.Text("Tol Al Sol / % (min 1%)")]]
        col_list_10=[[sg.Text("Stirrer")]]    # Makes a series of lists (which will form columns) with the the first item the header for each column
        
        for i_0 in range (1,(samp_no+1)): # Makes lists containing input boxes for each column, populated with default values from calculation
            box_0 = sg.Text(str(i_0))
            col_list_0.append([box_0])
            
            box_1 = sg.Input(default_text = "", size=(None,box_width), key="-INPUT_1_"+str(i_0)+"-")
            col_list_1.append([box_1])
            
            box_2 = sg.Input(default_text = str(round(data_out[0][i_0-1],dec_places)), size=(box_width,None), key="-INPUT_2_"+str(i_0)+"-")
            col_list_2.append([box_2])
            
            box_3 = sg.Input(default_text = str(Perc_Tol_Out[i_0-1]), size=(box_width,None), key="-INPUT_3_"+str(i_0)+"-")
            col_list_3.append([box_3])
            
            box_4 = sg.Input(default_text = str(round(data_out[3][i_0-1],dec_places)), size=(box_width,None), key="-INPUT_4_"+str(i_0)+"-")
            col_list_4.append([box_4])
            
            box_5 = sg.Input(default_text = str(Perc_Tol_Out[i_0-1]), size=(box_width,None), key="-INPUT_5_"+str(i_0)+"-")
            col_list_5.append([box_5])
            
            box_6 = sg.Input(default_text = str(round(data_out[2][i_0-1],dec_places)), size=(box_width,None), key="-INPUT_6_"+str(i_0)+"-")
            col_list_6.append([box_6])
            
            box_7 = sg.Input(default_text = str(Perc_Tol_Out[i_0-1]), size=(box_width,None), key="-INPUT_7_"+str(i_0)+"-")
            col_list_7.append([box_7])
            
            box_8 = sg.Input(default_text = str(round(data_out[1][i_0-1],dec_places)), size=(box_width,None), key="-INPUT_8_"+str(i_0)+"-")
            col_list_8.append([box_8])
            
            box_9 = sg.Input(default_text = str(Perc_Tol_Out[i_0-1]), size=(box_width,None), key="-INPUT_9_"+str(i_0)+"-")
            col_list_9.append([box_9])
            
            box_10 = sg.Input(default_text = self.default_stirr, size=(box_width,None), enable_events = True, key="-INPUT_10_"+str(i_0)+"-")
            col_list_10.append([box_10])
            
        b1 = sg.Button('Go Back', key = '-BACK-')
        b2 = sg.Button('Complete', key = '-COMP-')    
            
        layout_scan = [[l1],[sg.Column(col_list_0),sg.Column(col_list_1),sg.Column(col_list_2),\
                             sg.Column(col_list_3),sg.Column(col_list_4),sg.Column(col_list_5),\
                                 sg.Column(col_list_6),sg.Column(col_list_7),sg.Column(col_list_8),\
                                     sg.Column(col_list_9),sg.Column(col_list_10)],[b1,b2]]    # Defines the layout of the dialog with each list converted into a column
        
       
        window_scan = sg.Window(s_name, layout_scan, size = (1750,(100+(30*samp_no))),resizable = True) # Defines dialog box with size scaled to the number of samples
        
        new_dat = []  # A list containing the modified data columns
        
        i_scan = 1  # Used to check whether a sampleID box has been filled
        
        while True:
            
            event, values = window_scan.read(timeout=500)   # The dialog window is opened here, timeout defines how long before cursor moves on form a filled sampleID box
            
            if (event != sg.WIN_CLOSED):    # This is so we don't get an error if the dialog box is closed with the 'X' button
                if ((len(values["-INPUT_1_"+str(i_scan)+"-"]) >= 3) and (i_scan<samp_no)):    # This loop advances the cursor when sampleid is input
                        sleep(0.25)
                        pag.press('tab')
                        i_scan = i_scan + 1

            
            if event == '-COMP-':     # Once values are approved, this window will close
                
                
                nums, sampids, m_NMCs, t_NMCs, m_ipas, t_ipas, m_etacacs, t_etacacs, m_sol_als, t_sol_als, stirrs = [],[],[],[],[],[],[],[],[],[],[]

                
                for i_1 in range(1,(samp_no+1)):
                    nums.append(str(i_1))
                    if (values["-INPUT_1_"+str(i_1)+"-"] == ""):
                        sampids.append(str(i_1))
                    else:
                        sampids.append(values["-INPUT_1_"+str(i_1)+"-"])
                    m_NMCs.append(str(int(round((float(values["-INPUT_2_"+str(i_1)+"-"])*1000),0))))  # User inputs in g but balance reads in mg, with 0 decimal places (rounded otherwise)
                    if (float(values["-INPUT_3_"+str(i_1)+"-"])<1.0):   # Min tol% is 1, so this is used if values input below this
                        t_NMCs.append('1')
                    else:
                        t_NMCs.append(str(int(round(float(values["-INPUT_3_"+str(i_1)+"-"]),0))))    # Rounded to 0 decimal places
                    m_ipas.append(str(int(round((float(values["-INPUT_4_"+str(i_1)+"-"])*1000),0))))
                    if (float(values["-INPUT_5_"+str(i_1)+"-"])<1.0):
                        t_ipas.append('1')
                    else:
                        t_ipas.append(str(int(round(float(values["-INPUT_5_"+str(i_1)+"-"]),0))))
                    m_etacacs.append(str(int(round((float(values["-INPUT_6_"+str(i_1)+"-"])*1000),0))))
                    if (float(values["-INPUT_7_"+str(i_1)+"-"])<1.0):
                        t_etacacs.append('1')
                    else:
                        t_etacacs.append(str(int(round(float(values["-INPUT_7_"+str(i_1)+"-"]),0))))
                    m_sol_als.append(str(int(round((float(values["-INPUT_8_"+str(i_1)+"-"])*1000),0))))
                    if (float(values["-INPUT_9_"+str(i_1)+"-"])<1.0):
                        t_sol_als.append('1')
                    else:
                        t_sol_als.append(str(int(round(float(values["-INPUT_9_"+str(i_1)+"-"]),0))))
                    if (values["-INPUT_10_"+str(i_1)+"-"] == ""):
                        stirrs.append("None")
                    else:
                        stirrs.append(values["-INPUT_10_"+str(i_1)+"-"])
                
                check_id_set = set(sampids) # Makes a list of all the unique values in the sample ID list
                
                if (len(check_id_set) < samp_no):
                    sg.popup("Each sample must have a unique ID, please re-enter")  # Checks whether the number of sample IDs matches the number of samples
                    print("IDs are not all unique, re-enter values")
                    
                else:
                    new_dat = [nums, sampids, m_NMCs, t_NMCs, m_ipas, t_ipas, m_etacacs, t_etacacs, m_sol_als, t_sol_als, stirrs]
                    aprvl = self.Check_Dialog(samp_no,Inp_Vals,new_dat,vrbl)
                
                if (aprvl == True):
                    is_complete = True   # Updates approval value to send to other dialog, and closes this window if user submits values
                    break
            
            if (event == sg.WIN_CLOSED or event == '-BACK-'):   # If the 'Go Back' button is clicked, this dialog closes and returns to input
                break
                
        window_scan.close()
        
        return(is_complete,new_dat) # Sends whether the values have been approved
    
    
    def Check_Dialog(self,samp_n,Inp_Vals,data_Out,vari_pa):
        
        is_accepted = False   # Will update at the end of function if user approves the values
        
        Num_Out = data_Out[0]
        Samp_ID_Out = data_Out[1]
        Mass_NMC_Out = data_Out[2]
        Tol_NMC_Out = data_Out[3]
        Mass_IPA_Out = data_Out[4]
        Tol_IPA_Out = data_Out[5]
        Mass_EtAcAc_Out = data_Out[6]
        Tol_EtAcAc_Out = data_Out[7]
        Mass_Al_Out = data_Out[8]
        Tol_Al_Out = data_Out[9]
        Stirr_Out = data_Out[10]        # Seperates out the columns provided by the input dialog
        
    
        Full_Rows = []
    
    
        for i in range (0,samp_n):      # Places the column elements into rows of an arry which will display as a table table
            Full_Rows.append([Num_Out[i],Inp_Vals[i],\
                              Samp_ID_Out[i],\
                                  Mass_NMC_Out[i],Tol_NMC_Out[i],\
                                      Mass_IPA_Out[i],Tol_IPA_Out[i],\
                                          Mass_EtAcAc_Out[i],Tol_EtAcAc_Out[i],\
                                              Mass_Al_Out[i],Tol_Al_Out[i],\
                                                  Stirr_Out[i]])
    
        l1 = sg.Text("Process Parameters for balance input shown below (note g changed to mg), please check and accept or go back", font=('Arial',12))
    
        header = ['No.',vari_pa,'SampleID','Mass NMC / mg','Tol NMC / %','Mass IPA / mg','Tol IPA / %','Mass EtAcAc / mg','Tol EtAcAc / %', 'Mass Al Sol / mg','Tol Al Sol / %','Stirrer'] # Column headers
    
        b1 = sg.Button('Go Back', key = '-BACK-')
        b2 = sg.Button('Submit', key = '-SUBMIT-')
    
    
        tbl1 = sg.Table(values = Full_Rows,headings = header, auto_size_columns=True, num_rows = len(Inp_Vals), justification='center',key='-TABLE-') # Table to display data
        # Makes a table containing all of the relevant values, to be displayed in the dialog box
    
        layout = [[l1],[tbl1],[b1,b2]]
        
        if (samp_n<=14):
            win_height = 400
        else:
            win_height = 400 + (11*(samp_n-14))
    
        window_out = sg.Window('Series Check', layout, size = (1720,win_height),resizable = True)
    
        while True:
            
            event, values = window_out.read()   # The dialog window is opened here
            
            if event == '-SUBMIT-':     # Once values are approved, this window will close
                is_accepted = True   # Updates approval value to send to other dialog
                self.Target_Vals=Inp_Vals  # Defines target values for process file output
                print("Input values: "+str(Inp_Vals))
                break
            
            if (event == sg.WIN_CLOSED or event == '-BACK-'):   # If the 'Go Back' button is clicked, this dialog closes and returns to input
                break
            
        
                
                
                
        window_out.close()
    
        return(is_accepted) # Sends whether the values have been approved
    
    
    
    
    #------------------------------------------------------------------------------
    #------------------------- Main Loop and File Output --------------------------
    #------------------------------------------------------------------------------
    
    def Run(self):
    
        approval = False
        
        samp_num, Inp_Vals, data_out, r_dat_out, ser_name, approval, fixed_vals_list = self.Start_Dialog() # Runs the first dialog box, where user inputs sample number, which in turn calls other dialog box functions
        
        if approval == True:    # Values will only be sent over the network if the user has confirmed the calculated values
        
            if(ser_name==''):
                ser_name = str(date.today())+'_'+str(datetime.now().strftime('%H%M%S'))
                send_file_name = 'Sample_Series_'+self.Method_ID+'_'+ser_name+'.csv'
            else:
                send_file_name = 'Sample_Series_'+self.Method_ID+'_'+ser_name+'_'+str(date.today())+'.csv'
            
            print('File Created: '+send_file_name+' saved at: '+self.send_file_path)   # File path includes the date and time so they are easy to tell apart
            sg.popup('File Created: '+send_file_name+', saved at: '+self.send_file_path)
            
            print("Sample Series Name: "+ser_name)
            
            out_df ={}
            out_df_ext = {} # Second dictionary to contain the data that won't be fed into LabX, at this time, stirrers, (if used)
            
            headings = ['MethodInternalId','SampleSerieName','NumberOfSubstances','SampleSerieId','SampleId1',\
                        'Substance1','TargetSubstance1','ToleranceSubstance1',\
                            'Substance2','TargetSubstance2','ToleranceSubstance2',\
                                'Substance3','TargetSubstance3','ToleranceSubstance3',\
                                    'Substance4','TargetSubstance4','ToleranceSubstance4',]
                
            substances =["NMC622","IPA Neat","EtAcAc neat","Al Sol"]
                
            
            out_df[headings[0]] = [self.Method_ID]*samp_num
            out_df[headings[1]] = [ser_name]*samp_num
            out_df[headings[2]] = [str(len(substances))]*samp_num
            out_df[headings[3]] = [self.Method_ID+"_"+str(date.today())+'_'+str(datetime.now().strftime('%H%M%S'))]*samp_num
            out_df[headings[4]] = data_out[1]
            out_df[headings[5]] = [substances[0]]*samp_num
            out_df[headings[6]] = data_out[2]
            out_df[headings[7]] = data_out[3]
            out_df[headings[8]] = [substances[1]]*samp_num
            out_df[headings[9]] = data_out[4]
            out_df[headings[10]] = data_out[5]
            out_df[headings[11]] = [substances[2]]*samp_num
            out_df[headings[12]] = data_out[6]
            out_df[headings[13]] = data_out[7]
            out_df[headings[14]] = [substances[3]]*samp_num
            out_df[headings[15]] = data_out[8]
            out_df[headings[16]] = data_out[9]
            
            headings_ext = ['SampleID',str(self.to_vary),'Stirrer','Temp Setpoint','Stirring Speed','Stirring Time','Calcination temp']
            
            for i in range(0,len(fixed_vals_list)): # Adds the headings from the fixed process parameters
                headings_ext.append(fixed_vals_list[i][0])
            
            print("Input values: "+str(Inp_Vals))
        
            out_df_ext[headings_ext[0]] = data_out[1]   # Sample IDs
            
            out_df_ext[headings_ext[1]] = Inp_Vals # Save the target values
            out_df_ext[headings_ext[2]] = data_out[10]  # Stirrers (if used)
            out_df_ext[headings_ext[3]] = r_dat_out[0]  # Temp setpoint
            out_df_ext[headings_ext[4]] = r_dat_out[1]  # Stirring speed
            out_df_ext[headings_ext[5]] = r_dat_out[2]  # Stirring time
            out_df_ext[headings_ext[6]] = r_dat_out[3]  # Calcination temp
        
            for j in range(0,len(fixed_vals_list)): # Adds the values from the fixed process parameters
                out_df_ext[headings_ext[7+j]]=[fixed_vals_list[j][1]]*len(Inp_Vals)
            
            df=pd.DataFrame(out_df,columns=headings)
            
            print("Dataframe:")
            print(df)
            
            send_file = df.to_csv((self.send_file_path+send_file_name),index=False,sep=';',columns=headings) # Makes a new file in the path selected, containing the process parameters
            
            df_ext = pd.DataFrame(out_df_ext,columns=headings_ext)
            
            print("Dataframe extra headings: "+str(headings_ext))
        
            print("Dataframe Extra:")
            print(df_ext)
            
            full_ext_file_path=self.ext_file_path+'Process_'+send_file_name
        
            send_ext_file = df_ext.to_csv(full_ext_file_path,index=True,sep=',',columns=headings_ext) # Makes a new file in the path selected, containing the process parameters

            return full_ext_file_path
        
        else:
            return self.ext_file_path
   
    




