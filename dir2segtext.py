#    dir2segtext
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

def go():
    global dir
    global output
    global srxfile
    global srxlang
    global rules
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
                


if __name__ == "__main__":     
    parser = argparse.ArgumentParser(description='A script segment all the text files in a directory and save in a single file.')
    parser.add_argument("-d", "--dir", dest="dir", type=str, help="The input dir containing the text files to segment.", required=True)
    parser.add_argument("-o", "--output", dest="output", type=str, help="The output file.", required=True)
    parser.add_argument("-s", "--srxfile", dest="srxfile", type=str, help="The SRX file.", required=True)
    parser.add_argument("-l", "--srxlang", dest="srxlang", type=str, help="The SRX language.", required=True)
 
    args = parser.parse_args()
    dir=args.dir
    output=args.output
    srxfile=args.srxfile
    srxlang=args.srxlang
    
    rules = srx_segmenter.parse(srxfile)
    
    go()
