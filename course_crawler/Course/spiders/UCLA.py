# -*- coding: utf-8 -*-
import scrapy
import re
import os
import errno

class UclaSpider(scrapy.Spider):
    name = 'UCLA'
    allowed_domains = ['ucla.edu']
    start_urls = ['https://www.registrar.ucla.edu/Academics/Course-Descriptions']

    def parse(self, response):
        area=response.xpath("//div[@class='list-alpha']")
        for item in area:
            #page=item.xpath(".//li/a/text()").extract()
            site=item.xpath(".//li/a/@href").extract()
        for count in range(len(site)):
            yield scrapy.Request('https://www.registrar.ucla.edu'+site[count],callback=self.parse_course)


    def parse_course(self,response):
        # courseList=response.xpath("//div[@class='tab-content']")
        # for course in courseList:
        #     courseName=course.xpath(".//div[@class='media-body']/h3/text()").extract()
        #     yield {'name':courseName}

        areaName=response.xpath("//div[@class='page-header']/h1/span/text()").extract_first()
        targ=['Graduate','Undergraduate']
        if any(s in areaName for s in targ):
            pos=areaName.rfind('(')
            name=areaName[:pos]
            #print name  
        else:
            name=re.sub('\([^(]*\)','',areaName)
        name=re.sub(r'\/','',name)
        #name=(re.sub(regex,'',areaName) for regex in ['\([^()]*\)',r'\\'])
        name=name.rstrip()
        path="./data/"
        self.createFolder(path)
        completeName=os.path.join(path,name+".html")
        
        with open(completeName,'wb') as f:
            f.write(response.body)

    def createFolder(self,directory):
        try:
            os.makedirs(directory)
        except OSError:
            if not os.path.isdir(directory):
                raise      
        return


        
         
        

