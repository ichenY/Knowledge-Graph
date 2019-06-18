import json
from pprint import pprint


with open('Chemical Engineering (CH ENGR) .json') as f:
    pprint(f)
    data = json.load(f)
    des_list = []
    #row = data['course'][0]
    
    #pprint(row['Course description'])

    course = data['course'][:50]
    #pprint(row)
    for description in course:
        course_des = description['Course description']
        des_list.append(course_des)
    with open('test-ucla.txt', 'w') as f_txt:  
        for line in des_list:
            f_txt.write("%s\n" % line)

    

            
    
   
    


