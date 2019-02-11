# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import json
import sys
import os
import re

path="./CRAWLED_DIR/"
def parse(path):
    outitem={}
    preitem=soup.select("h1")[1].span.text
    preitem=re.sub(r'\/','-',preitem)
    #preitem=preitem.rstrip()
    outitem['subject']=preitem
    container=soup.findAll("li",{"class":"media category-list-item"})
    #print(container)
    data=[]
    for item in container:
        subitem={}
        subitem['course number & title']=item.select("h3")[0].text
        subitem['Number of units']=item.select("p")[0].text
        subitem['Course description']=item.select("p")[1].text
        data.append(subitem)
        #print(course+"\n"+unit+"\n"+description)

    outitem['course']=data

    result="./result/"
    createFolder(result)
    completeName=os.path.join(result,"%s.json" % outitem['subject'])

    with open(completeName,"w") as outfile:
        json.dump(outitem,outfile,indent=2)

def createFolder(directory):
    try:
        os.makedirs(directory)
    except OSError:
        if not os.path.isdir(directory):
            raise      
    return
    
for url in os.listdir(path):
    url=os.path.join(path,url)
    soup=BeautifulSoup(open(url,"r",encoding="utf-8"),"html.parser")
    parse(soup)

