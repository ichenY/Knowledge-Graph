import rltk
import pandas as pd
import csv
import re,sys
# from IPython.display import display

'''
command to run: python match.py <file1> <file2> <output>
'''

file_F = sys.argv[1]
file_Z = sys.argv[2]
output = sys.argv[3]

#file_F = 'fodors.csv'
#file_Z = 'zagats.csv'

tokenizer = rltk.CrfTokenizer()
i = 0
def tokenize_id(t):
    tokens = tokenizer.tokenize(t)
    global i
    i += 1
    t = str(i)
    return t

@rltk.remove_raw_object
class DBFod(rltk.Record):
    @rltk.cached_property
    def id(self):     
        return tokenize_id('')
    
    @rltk.cached_property
    def name(self):
        address = self.raw_object['Address']
        if address[0].isdigit(): #Name contains number
            m = re.match("[\d]+[^\d]*(?=(\s\d+))", address) #match strings before the second number
        else:
            m = re.match("[^\d]*(?=(\s\d+))", address) #match names that doesn't have numeric
            
        if m is None: # the whole address do not contain number
            name = ""
        else: 
            name = m[0]
        
        return set(name.strip().lower().split())
    
    @rltk.cached_property
    def address(self):
        address = self.raw_object['Address']
        if address[0].isdigit(): #Name contains number
            m = re.match("[\d]+[^\d]*(?=(\s\d+))", address) #match strings before the second number
        else:
            m = re.match("[^\d]*(?=(\s\d+))", address) #match names that doesn't have numeric
            
        if m is not None: 
            address = address[m.end(0):]
        
        return address.strip().lower()

    @rltk.cached_property
    def phone(self):
        phone = self.raw_object['Phone'].replace('/','-').replace(' ','')#.replace('and','or').split('or')
#         print(phone.strip()[:15])
        return phone.strip()[:15]

    @rltk.cached_property
    def cuisine(self):
        cs = self.raw_object['Cuisine']
        return cs if cs else ''

ds_fod = rltk.Dataset(rltk.CSVReader(file_F), record_class=DBFod, adapter=rltk.MemoryKeyValueAdapter())
# dFod = [[k+1,dblp.id,dblp.cuisine,dblp.address] for k,dblp in enumerate(ds_fod)]
# print(dFod[506])
# for r_dblp in ds_fod:
#     print(r_dblp.name)



tokenizer = rltk.CrfTokenizer()
i = 0
def tokenize_id(t):
    tokens = tokenizer.tokenize(t)
    global i
    i += 1
    t = str(i)
    return t


@rltk.remove_raw_object
class DBZag(rltk.Record):
    @rltk.cached_property
    def id(self):     
        return tokenize_id('')
    
    @rltk.cached_property
    def name(self):
        address = self.raw_object['Address']
        if address[0].isdigit(): #Name contains number
            m = re.match("[\d]+[^\d]*(?=(\s\d+))", address) #match strings before the second number
        else:
            m = re.match("[^\d]*(?=(\s\d+))", address) #match names that doesn't have numeric
            
        if m is None: # the whole address do not contain number
            name = ""
        else: 
            name = m[0]
        
        return set(name.strip().lower().split())        
        
    @rltk.cached_property
    def address(self):
        address = self.raw_object['Address']
        if address[0].isdigit(): #Name contains number
            m = re.match("[\d]+[^\d]*(?=(\s\d+))", address) #match strings before the second number
        else:
            m = re.match("[^\d]*(?=(\s\d+))", address) #match names that doesn't have numeric
            
        if m is not None: 
            address = address[m.end(0):]

        return address.strip().lower()

    @rltk.cached_property
    def phone(self):
        phone = self.raw_object['Phone'].strip()[:15]
#         print(phone)
        return phone   

    @rltk.cached_property
    def cuisine(self):
        cs = self.raw_object['Cuisine']
        return cs if cs else ''
    

ds_zag = rltk.Dataset(rltk.CSVReader(file_Z), record_class=DBZag, adapter=rltk.MemoryKeyValueAdapter())


def SimilarityScore(record1, record2):
    names = rltk.jaccard_index_similarity(record1.name, record2.name)
    address = rltk.levenshtein_similarity(record1.address, record2.address)
    cuisine = rltk.levenshtein_similarity(record1.cuisine, record2.cuisine)
#     phone = rltk.levenshtein_similarity(record1.phone, record2.phone)
    
    if record1.phone != record2.phone:
        phone = 0.
    else: phone = 1.
    #0.7  0.2 0.1 > 0.8 104
    #0.4 0.4 0.2 >0.59 106
    #0.4 0.4 0.2 >0.53 113
    return 0.4*phone + 0.4*names + 0.2*address


def create_block_reader(ds1: rltk.Dataset, ds2: rltk.Dataset):
    chunkNum = {}
    def blockingFunc(r):
        chunk = sum(int(x) for x in r.phone if x.isdigit()) % 11
        '''
        if chunk in chunkNum:
            chunkNum[chunk] += 1
        else:
            chunkNum[chunk] = 1        
        '''


        return str(chunk)   
    
    bg = rltk.HashBlockGenerator()
    block = bg.generate(
        bg.block(ds1, function_=blockingFunc),
        bg.block(ds2, function_=blockingFunc))
    #print(chunkNum)
    return block

out = []
for r1, r2 in rltk.get_record_pairs(ds_fod, ds_zag, block = create_block_reader(ds_fod, ds_zag)):
    #print(ExtractFeatureFunc(r1,r2))
    if SimilarityScore(r1,r2) > 0.53:
        out.append((file_Z,':',r2.id,file_F,':',r1.id))
        print(r1.id, r2.id)
        print(r1.name, r1.phone, r1.address,SimilarityScore(r1,r2))
        print(r2.name, r2.phone, r2.address)
        
print('number of matched records',len(out))

'''
comparison = {}
def blocking_comparison(k,r):
        chunk = sum(int(x) for x in r.phone if x.isdigit()) % 11
        if chunk in comparison:
            comparison[chunk] += 1
        else:
            comparison[chunk] = 1  
        return comparison
for k,r1 in enumerate(ds_zag):
    blocking(k,r1)

'''

def write_txt():
    with open(output,'w') as f:
        f.write(''.join('%s%s%s\t%s%s%s\n' % x for x in out))
write_txt()

