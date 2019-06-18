from bs4 import BeautifulSoup
import json,os,glob,sys

'''
command to run: python extract.py ./webpages ./output.jsonld


'''

head = sys.argv[1]
#root = os.path.join(sys.argv[1] +'./*.html')
#print(root)
index = './webpages/index.json'

#url = './webpages/page1.html'
#soup = BeautifulSoup(open(url,'r',encoding='utf-8'),'html.parser')
data,data['@context'],nodes = {},{},[]
data['@context']['og'] = 'http://ogp.me/ns#'
data['@context']['og:url'] = {"@type":"@id"}
data['@context']['og:image'] = {"@type":"@id"}

for url in glob.glob(head+'/*.html'):
    #print(123)
    soup = BeautifulSoup(open(url,'r',encoding='utf-8'),'html.parser')
    title,site_name,description,url_og,type_og,image,rating,rating_scale = '','','','','','','',''
    for tag in soup.find_all('meta'):
        if tag.get('property') == 'og:title':
            title = tag.get('content')
            print(title)
        elif tag.get('property') == 'og:site_name':
            site_name = tag.get('content')
        elif tag.get('property') == 'og:description':
            description = tag.get('content')
        elif tag.get('property') == 'og:url':
            url_og = tag.get('content')
        elif tag.get('property') == 'og:type':
            type_og = tag.get('content')
        elif tag.get('property') == 'og:image':
            image = tag.get('content')
        elif tag.get('property') == 'og:rating':
            rating = tag.get('content')
        elif tag.get('property') == 'og:rating_scale':
            rating_scale = tag.get('content')

    filekey = os.path.basename(url)
    print(filekey)
    def getid(index):
        with open(index,'r') as f:
            data = json.load(f)
            fileid = data[filekey]
            return fileid
        
    fileid = getid(index)
    #print(fileid)
    data_g = {}
    data_g['@id'] = fileid
    if title: data_g['og:title'] = title 
    if site_name: data_g['og:site_name'] = site_name
    if description: data_g['og:description'] = description
    if url_og: data_g['og:url'] = url_og
    if type_og: data_g['og:type'] = type_og
    if image: data_g['og:image'] = image
    if rating: data_g['og:rating'] = rating
    if rating_scale: data_g['og:rating_scale'] = rating_scale
    nodes.append(data_g)

data['@graph'] = nodes   

    #data.append(meta2json())
#print(data)
    
with open(sys.argv[2], 'w') as outfile:
    json.dump(data, outfile,indent=2)
