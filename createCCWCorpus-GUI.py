#    createCCWCorpus-Dir
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

import os

from tkinter import *
from tkinter.ttk import *

import tkinter 
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askdirectory
from tkinter import messagebox

import codecs

import sqlite3
import os
import gzip
import re
from bz2 import BZ2File as bzopen
import codecs
from lxml import etree as et
import sys
import wikipedia


def select_database():
    inputfile = askopenfilename(initialdir = ".",filetypes =(("SQLite files", ["*.sqlite"]),("All Files","*.*")),
                           title = "Choose a database to use.")
    E1.delete(0,END)
    E1.insert(0,inputfile)
    E1.xview_moveto(1)
    
def select_article_list():
    articlelistfile = asksaveasfilename(initialdir = ".",filetypes =(("text files", ["*.txt"]),("All Files","*.*")),
                           title = "Choose a file to save the article list.")
    E8.delete(0,END)
    E8.insert(0,articlelistfile)
    E8.xview_moveto(1)
    
def select_output():
    outputdir = askdirectory(initialdir = ".",mustexist=False, title = "Choose the output directory.")
    E5.delete(0,END)
    E5.insert(0,outputdir)
    E5.xview_moveto(1)


def go():
    global categories
    global categoriesTEMP
    global categoriesAUX
    global todownload
    try:
        categories=[]
        categoriesTEMP=[]
        categoriesAUX=[]
        todownload=[]
        filename=E1.get()
        conn=sqlite3.connect(filename)
        cur = conn.cursor()
        categoria=E2.get()
        level=int(E3.get())
        lang=E4.get()
        for cat in categoria.split(","):
            cat=cat.strip()
            categories.append(cat)
            categoriesTEMP.append(cat)
        while level>0:
            while(len(categoriesTEMP))>0:
                categoria=categoriesTEMP.pop(0)
                cur.execute('SELECT categoryREL from categoryrelations WHERE category=?', (categoria,))
                data=cur.fetchall()
                for d in data:
                    categories.append(d[0])
                    categoriesAUX.append(d[0])
            categoriesTEMP.extend(categoriesAUX)
            categoriesAUX=[]
            level-=1
               
        E6.delete(0,END)
        E6.insert(0,len(categories))

        idents={}
        
        articlelist=E8.get()
        alf=codecs.open(articlelist,"w",encoding="utf-8")

        for category in categories:
            cur.execute('SELECT ident from categories WHERE category=?', (category,))
            data=cur.fetchall()
            for d in data:
                idents[d[0]]=1
                
        idents=idents.keys()
        
        E6.delete(0,END)
        E6.insert(0,len(categories))
        
        todownload=[]
        if not lang=="en":
            for ident in idents:
                cur.execute('SELECT title from langlinks WHERE ident=? and lang=?', (ident,lang))
                data=cur.fetchone()
                if not data==None:
                    todownload.append(data[0])
                    alf.write(data[0]+"\n")
        else:
            for ident in idents:
                cur.execute('SELECT title from titles WHERE ident=?', (str(ident),))
                data=cur.fetchone()
                if not data==None:
                    todownload.append(data[0])
                    alf.write(data[0]+"\n")
                    
        E7.delete(0,END)
        E7.insert(0,len(todownload))
        alf.close()
    except:
        messagebox.showerror("Error", sys.exc_info())
        
def download():
    global categories
    global categoriesTEMP
    global categoriesAUX
    global todownload
    try:
        outdir=E5.get()
        lang=E4.get()
        wikipedia.set_lang(lang)
        for td in todownload:
            outfile=outdir+"/"+td.replace(" ","_").replace("/","-")+".txt"
            
            try:
                sortida=codecs.open(outfile,"w",encoding="utf-8")
                page = wikipedia.page(td)
                sortida.write(page.content+"\n")
            except:
                print("ERROR DOWNLOADING ",outfile,sys.exc_info())
    except:
        messagebox.showerror("Error", sys.exc_info())

categories=[]
categoriesTEMP=[]
categoriesAUX=[]
todownload=[]


top = Tk()
top.title("Create CCW Corpus")

B1=tkinter.Button(top, text = str("Select Database"), borderwidth = 1, command=select_database,width=14).grid(row=0,column=0)
E1 = tkinter.Entry(top, bd = 5, width=50, justify="right")
E1.grid(row=0,column=1)

L2 = Label(top,text="Categories:").grid(sticky="E",row=1,column=0)
E2 = tkinter.Entry(top, bd = 5, width=50, justify="left")
E2.grid(row=1,column=1)

L3 = Label(top,text="Level:").grid(sticky="E",row=2,column=0)
E3 = tkinter.Entry(top, bd = 5, width=3, justify="left")
E3.grid(sticky="W",row=2,column=1)

L4 = Label(top,text="Lang:").grid(sticky="E",row=3,column=0)
E4 = tkinter.Entry(top, bd = 5, width=3, justify="left")
E4.grid(sticky="W",row=3,column=1)

B5=tkinter.Button(top, text = str("Output Dir"), borderwidth = 1, command=select_output,width=14).grid(row=5,column=0)
E5 = tkinter.Entry(top, bd = 5, width=50, justify="right")
E5.xview_moveto(1)
E5.grid(row=5,column=1)

B8=tkinter.Button(top, text = str("Select article list"), borderwidth = 1, command=select_article_list,width=14).grid(row=4,column=0)
E8 = tkinter.Entry(top, bd = 5, width=50, justify="left")
E8.grid(row=4,column=1)

E8.delete(0,END)
E8.insert(0,"article-list.txt")

L6 = Label(top,text="TOTAL CATEGORIES:").grid(sticky="E",row=6,column=0)
E6 = tkinter.Entry(top, bd = 5, width=10, justify="right")
E6.grid(sticky="W",row=6,column=1)

L7 = Label(top,text="TOTAL PAGES:").grid(sticky="E",row=7,column=0)
E7 = tkinter.Entry(top, bd = 5, width=10, justify="right")
E7.grid(sticky="W",row=7,column=1)



B9=tkinter.Button(top, text = str("Calculate"), borderwidth = 1, command=go,width=14).grid(row=8,column=0)

B10=tkinter.Button(top, text = str("Download"), borderwidth = 1, command=download,width=40).grid(row=8,column=1)


E1.delete(0,END)
E1.xview_moveto(1)

E2.delete(0,END)
E2.xview_moveto(1)


    
top.mainloop()
