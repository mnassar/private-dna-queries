'''

Created on Jun 3, 2013

@author: NASSAR
'''
#ToDo : Map Reduce 
import cloud 
import cPickle as pickle 
import random
import time
path_="C:\Users\NASSAR\SkyDrive\Documents\DNA"
file_=path_+"\\tests\\records.txt"
acgt="ACGT"

# query size q 
q=1
m=300
n=5000

# generate a random query
query=[]
for i in range(q): 
    r=random.randrange(m)
    c=random.randrange(4)
    query.append((r,c))
query.sort()
print query 

input_=open(file_,'r')
#local query
start=time.time()
matches=0
for line in input_.readlines():
    acc=0
    for (r,c) in query: 
        #print r, c
        char=acgt[c]
        if (line[r]==char):
            acc+=1
    if acc==q: 
        matches+=1
print "local query result ", matches 
stop=time.time()
print "local query time %.2f" % (stop-start)

#remote query 
   

def execute_query(query, share):
    start=time.time()
    if cloud.running_on_cloud():
        #share1=pickle.load(cloud.bucket.getf("share1"))
        #share2=pickle.load(cloud.bucket.getf("share2"))
        share1_file= open ("shares/"+share,'r')
        share1=pickle.load(share1_file)
    else: 
        print " running locally !!"
        share1_file= open (path_+"\\shares\\"+share,'r')
        share1=pickle.load(share1_file)
    stop=time.time()
    time1=stop-start
    start= time.time()
    n=len(share1)
    sums1=[0 for x in range(n)]
    for x in range(n):
        sum_=0
        for (r,c) in query: 
            #print r, c
            sum_+=share1[x][r][c]
        sums1[x]=sum_   
    stop=time.time()
    time2=stop-start 
    start=time.time()   
    cloud.bucket.putf(pickle.dumps(sums1),"results/sums"+share[-1])
    stop=time.time()
    time3=stop-start
    return time1,time2,time3

start=time.time()
jids=cloud.map(execute_query, [query, query], ["share1", "share2"], _type='c2', _vol="shares")
print " submitted job ids", list(jids)
for jid in jids:
    cloud.join(jid)
stop=time.time()
print "overall query time: %.2f s" %(stop-start)
for jid in jids: 
    print " download from volume %.2f, execution %.2f, save to bucket %.2f" % cloud.result(jid)
start=time.time()
sums1=pickle.load(cloud.bucket.getf("results/sums1"))
sums2=pickle.load(cloud.bucket.getf("results/sums2"))
stop=time.time()
print "results download time: %.2f s" %(stop-start)
res=0
for i in range(n): 
    if sums1[i] == sums2[i]:
        res+=1
print res 
if res==matches: 
    print "verification ok" 
    
input_.close()