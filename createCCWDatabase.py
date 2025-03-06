#!/usr/bin/python3
#    createCCWDatabase
#    Copyright (C) 2025  Antoni Oliver
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
import bz2
from bz2 import BZ2File as bzopen
import codecs
from lxml import etree as et
import sys
import argparse


parser = argparse.ArgumentParser(description='Script for the creation of the database for the programs to creata comparable corpora from Wikipedia')
parser.add_argument("-s",'--skoscategories', action="store", dest="skoscategories", help='The skos_categories_en.ttl.bz2 file (from https://downloads.dbpedia.org/).',required=True)

parser.add_argument("-l",'--langlinks', action="store", dest="langlinkssqlgz", help='The langlinks.sql.gz (from https://dumps.wikimedia.org/enwiki/).',required=True)

parser.add_argument("-w",'--wikidump', action="store", dest="wikidump", help='The pages-articles.xml.bz2 (from https://dumps.wikimedia.org/enwiki/).',required=True)
    
parser.add_argument("-o",'--output', action="store", dest="filename", help='The name of the sqlite database to be created.',required=True)
    
args = parser.parse_args()

filename=args.filename
skoscategories=args.skoscategories
langlinkssqlgz=args.langlinkssqlgz
wikidump=args.wikidump
   
#CREATE DATABES

if os.path.exists(filename):
    os.remove(filename)
conn=sqlite3.connect(filename)
cur = conn.cursor() 
cur.execute("CREATE TABLE langlinks (id INTEGER PRIMARY KEY AUTOINCREMENT, ident INTEGER, title TEXT, lang TEXT)")
cur.execute("CREATE INDEX index_langlinks ON langlinks(ident,lang)")

cur.execute("CREATE TABLE categoryrelations (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, categoryREL TEXT)")
cur.execute("CREATE INDEX index_categoryrelations ON categoryrelations(category)")

cur.execute("CREATE TABLE titles (id INTEGER PRIMARY KEY AUTOINCREMENT, ident INTEGER, title TEXT)")
cur.execute("CREATE INDEX index_titles ON titles(ident)")

cur.execute("CREATE TABLE categories (id INTEGER PRIMARY KEY AUTOINCREMENT, ident INTEGER, category TEXT)")
cur.execute("CREATE INDEX index_category ON categories(category)")

cur.execute("CREATE TABLE qualities (id INTEGER PRIMARY KEY AUTOINCREMENT, ident INTEGER, quality TEXT)")
cur.execute("CREATE INDEX index_quality ON qualities(ident)")

cur.execute("CREATE TABLE sizes (id INTEGER PRIMARY KEY AUTOINCREMENT, ident INTEGER, size INTEGER)")
cur.execute("CREATE INDEX index_size ON sizes(ident)")

conn.commit()
'''
#CATEGORY RELATIONS
with bzopen(skoscategories, "r") as textfile:
    cont=0
    for linia in textfile:
        linia=linia.decode("utf-8").strip()
        camps=linia.split(" ")
        catBROA=camps[2].replace("<http://dbpedia.org/resource/Category:","").replace(">","").replace("_"," ")
        catSPEC=camps[0].replace("<http://dbpedia.org/resource/Category:","").replace(">","").replace("_"," ")
        if camps[1]=="<http://www.w3.org/2004/02/skos/core#broader>" or camps[1]=="<http://www.w3.org/2004/02/skos/core#related>":
            cont+=1
            data=[catBROA,catSPEC]
            cur.execute("INSERT OR IGNORE INTO categoryrelations (category,categoryREL) VALUES (?,?)",data)
            if cont==100000:
                print("Commit relations")
                conn.commit()
                cont=0
            
conn.commit()
print("Finished relations")


#LANGLINKS

f=gzip.open(langlinkssqlgz,'rb')

expreg=r"\([0-9]+,'.+?','.+?'\)"

titles={}
langlinks={}
cont=0
for line in f:
    l=line.decode("utf-8",errors="replace")
    ll=re.findall(r'\(.+?\)',l)
    for tripleta in ll:
        tripleta=tripleta.replace("(","").replace(")","")
        camps=tripleta.split(",")
        if len(camps)>2:
            id=camps[0]
            lang=camps[1][1:-1]
            title=camps[2][1:-1]
            data=[id,title,lang]
            cont+=1
            cur.execute("INSERT OR IGNORE INTO langlinks (ident,title,lang) VALUES (?,?,?)",data)
            if cont==100000:
                conn.commit()
                cont=0
                print("Commit langlinks")
                    
print("Finished langlinks")
            
conn.commit()
'''
#WIKIPEDIA
cont=0
text=""
title=""
text=""
FirstID=False
with bz2.BZ2File(wikidump, "r") as xml_file:
    parser = et.iterparse(xml_file, events=("end", "start"))
    FirstID = False
    id, title, text = "", "", ""
    
    for event, elem in parser:
        print(elem.tag)
        if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
            title = elem.text
        if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}id" and not FirstID:
            id = elem.text
            FirstID = True
        if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}text":
            text = elem.text
        if event == "end" and elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}page":
            if id and title and text:
                try:
                    categoriesbrut = re.findall(r"\[\[Category:[^\]]+?\]\]", text)
                    categories = [
                        cat.replace("[[Category:", "").replace("]]", "").strip()
                        for cat in categoriesbrut
                    ]
                    categories.sort()
                    
                    Quality = "Regular"
                    size = len(text)
                    if "{{Featured article}}" in text:
                        Quality = "Featured"
                    elif "{{Good article}}" in text:
                        Quality = "Good"
                    elif "-stub}}" in text:
                        Quality = "Stub"
                    
                    cont += 1
                    
                    cur.execute(
                        "INSERT OR IGNORE INTO titles (ident, title) VALUES (?, ?)",
                        (id, title),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO qualities (ident, Quality) VALUES (?, ?)",
                        (id, Quality),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO sizes (ident, size) VALUES (?, ?)",
                        (id, size),
                    )
                    
                    for cat in categories:
                        cur.execute(
                            "INSERT OR IGNORE INTO categories (ident, category) VALUES (?, ?)",
                            (id, cat),
                        )
                    
                    if cont == 10000:
                        print("Committing to database...")
                        conn.commit()
                        cont = 0
                    
                    # Clear variables to release memory
                    id, title, text = "", "", ""
                    FirstID = False
                    
                except Exception as e:
                    print("ERROR:", e)
                
                # Clear the element to release memory
                elem.clear()
                
    # Final commit after processing all pages
    conn.commit()
print("FINISHED")
