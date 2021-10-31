#    dir2segtext-GUI
#    Copyright (C) 2021  Antoni Oliver
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import argparse
import sys
import codecs
import glob
import os
import srx_segmenter

from tkinter import *
from tkinter.ttk import *

import tkinter 
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askdirectory
from tkinter import messagebox

def segmenta(cadena):
    global rules
    global srxlang
    segmenter = srx_segmenter.SrxSegmenter(rules[srxlang],cadena)
    segments=segmenter.extract()
    resposta=[]
    for segment in segments[0]:
        segment=segment.replace("’","'")
        print(segment)
        resposta.append(segment)
    return(resposta)

def select_directory():
    dir = askdirectory(initialdir = ".",mustexist=True, title = "Choose the output directory.")
    E1.delete(0,END)
    E1.insert(0,dir)
    E1.xview_moveto(1)

def select_output_file():
    outfile = asksaveasfilename(initialdir = ".",filetypes =(("text files", ["*.txt"]),("All Files","*.*")),
                           title = "Choose a file to save the segmented text.")
    E2.delete(0,END)
    E2.insert(0,outfile)
    E2.xview_moveto(1)
    
def select_srx_file():
    srxfile = askopenfilename(initialdir = ".",filetypes =(("SRX files", ["*.srx"]),("All Files","*.*")),
                           title = "Choose the SRX file to use.")
    E4.delete(0,END)
    E4.insert(0,inputfile)
    E4.xview_moveto(1)
    
def go():
    global rules
    global srxlang
    dir=E1.get()
    output=E2.get()
    srxfile=E3.get()
    srxlang=E4.get()
    rules = srx_segmenter.parse(srxfile)
    sortida=codecs.open(output,"w",encoding="utf-8")
    for r, d, f in os.walk(dir):
        for file in f:
            fullpath=os.path.join(r, file)
            print(fullpath)
            entrada=codecs.open(fullpath,"r",encoding="utf-8")
            for linia in entrada:
                segments=segmenta(linia)
                for segment in segments:
                    segment=segment.strip()
                    if len(segment)>0:
                        sortida.write(segment+"\n")
            entrada.close()
    sortida.close()
                


top = Tk()
top.title("dir 2 segmented text")

B1=tkinter.Button(top, text = str("Directory"), borderwidth = 1, command=select_directory,width=14).grid(row=0,column=0)
E1 = tkinter.Entry(top, bd = 5, width=50, justify="right")
E1.xview_moveto(1)
E1.grid(row=0,column=1)

B2=tkinter.Button(top, text = str("Output file"), borderwidth = 1, command=select_output_file,width=14).grid(row=1,column=0)
E2 = tkinter.Entry(top, bd = 5, width=50, justify="right")
E2.grid(row=1,column=1)

B3=tkinter.Button(top, text = str("SRX file"), borderwidth = 1, command=select_srx_file,width=14).grid(row=2,column=0)
E3 = tkinter.Entry(top, bd = 5, width=50, justify="right")
E3.grid(row=2,column=1)

L4 = Label(top,text="SRX Lang:").grid(sticky="E",row=3,column=0)
E4 = tkinter.Entry(top, bd = 5, width=15, justify="left")
E4.grid(sticky="W",row=3,column=1)

B5=tkinter.Button(top, text = str("GO!"), borderwidth = 1, command=go,width=14).grid(sticky="W",row=4,column=0)

E3.delete(0,END)
E3.insert(0,"segment.srx")

E4.delete(0,END)
E4.insert(0,"Generic")
   
top.mainloop()
