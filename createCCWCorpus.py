#!/usr/bin/python3
#    createCCWCorpus
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

import sqlite3
import os
import gzip
import re
from bz2 import BZ2File as bzopen
import codecs
from lxml import etree as et
import sys
import wikipedia
import argparse


def go():
    global categoria
    global level
    global articlelist
    categories=[]
    categoriesTEMP=[]

    for cat in categoria.split(","):
        cat=cat.strip()
        categories.append(cat)
        categoriesTEMP.append(cat)
    categoriesAUX=[]
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
           
    print("TOTAL CATEGORIES",len(categories))


    idents={}
    
    alf=codecs.open(articlelist,"w",encoding="utf-8")
    
    for category in categories:
        cur.execute('SELECT ident from categories WHERE category=?', (category,))
        data=cur.fetchall()
        for d in data:
            idents[d[0]]=1
            
    idents=idents.keys()
    

    

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
                print(data[0])
                todownload.append(data[0])
                alf.write(data[0]+"\n")
                
    print("TOTAL PAGES",len(todownload))
    alf.close()
    a=input("Download? (Y/N) ")
    
    if not (a=="Y" or a=="y"):
        sys.exit()
    print("DONWLOADING ",len(todownload))

    wikipedia.set_lang(lang)
    for td in todownload:
        outfile=outdir+"/"+td.replace(" ","_").replace("/","-")+".txt"
        print(outfile)
        
        try:
            sortida=codecs.open(outfile,"w",encoding="utf-8")
            page = wikipedia.page(td)
            sortida.write(page.content+"\n")
        except:
            print("ERROR DOWNLOADING ",outfile,sys.exc_info())
    alf.close()


if __name__ == "__main__":        
    parser = argparse.ArgumentParser(description='Script for the creation of parallel corpora from Wikipedia')
    
    parser.add_argument("-d",'--database', action="store", dest="filename", help='The CCW sqlite database to use.',required=True)

    parser.add_argument("-c",'--categories', action="store", dest="categoria", help='The categories to search for (a category or a list of categories separated by ,',required=True)

    parser.add_argument('--level', action="store", dest="level", type=int, help='The category level depth.',required=True)
    
    parser.add_argument('--lang', action="store", dest="lang", help='The language (two letter ISO code used in Wikipedia.',required=True)
        
    parser.add_argument("-o",'--output', action="store", dest="outdir", help='The name of the sqlite database to be created.',required=True)
    
    parser.add_argument("-a",'--articlelist', action="store", dest="articlelist", help='The name of the text file containing the list of files.',required=False)
        
    args = parser.parse_args()  
    
    filename=args.filename

    conn=sqlite3.connect(filename)
    cur = conn.cursor() 

    categoria=args.categoria
    level=args.level
    lang=args.lang
    outdir=args.outdir
    
    if args.articlelist:
        articlelist=args.articlelist
    else:
        articlelist="article-list.txt"
    
    go()