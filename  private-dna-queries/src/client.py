'''

Created on Jun 3, 2013

@author: NASSAR
'''
#ToDo : Map Reduce 
import cloud 
import cPickle as pickle 
import random
import time
path_="C:\Users\NASSAR\Documents\DNA_"
file_=path_+"\\tests\\records2.txt"
acgt="ACGT"


# generate a random query
def generate_query(q):
    query=[]
    for i in range(q): 
        r=random.randrange(m)
        c=random.randrange(4)
        query.append((r,acgt[c]))
    query.sort()
    print query 
    return query 

def execute_query_clear(query):
    input_=open(file_,'r')
    #local query
    matches=0
    line=input_.readline()
    while line !="":
        acc=0
        for (r,c) in query: 
        #print r, c
            if (line[r]==c):
                acc+=1
        line=input_.readline()
        if acc==len(query): 
            matches+=1
    print "number of matches", matches 
    return matches
    

#remote query 
#def execute_query(query, share):
#    start=time.time()
#    if cloud.running_on_cloud():
#        #share1=pickle.load(cloud.bucket.getf("share1"))
#        #share2=pickle.load(cloud.bucket.getf("share2"))
#        share1_file= open ("shares/"+share,'r')
#        share1=pickle.load(share1_file)
#    else: 
#        print " running locally !!"
#        share1_file= open (path_+"\\shares\\"+share,'r')
#        share1=pickle.load(share1_file)
#    stop=time.time()
#    time1=stop-start
#    start= time.time()
#    n=len(share1)
#    sums1=[0 for x in range(n)]
#    for x in range(n):
#        sum_=0
#        for (r,c) in query: 
#            #print r, c
#            sum_+=share1[x][r][c]
#        sums1[x]=sum_   
#    stop=time.time()
#    time2=stop-start 
#    start=time.time()   
#    cloud.bucket.putf(pickle.dumps(sums1),"results/sums"+share[-1])
#    stop=time.time()
#    time3=stop-start
#    return time1,time2,time3

#start=time.time()
#jids=cloud.map(execute_query, [query, query], ["share1", "share2"], _type='c2', _vol="shares")
#print " submitted job ids", list(jids)
#for jid in jids:
#    cloud.join(jid)
#stop=time.time()
#print "overall query time: %.2f s" %(stop-start)
#for jid in jids: 
#    print " download from volume %.2f, execution %.2f, save to bucket %.2f" % cloud.result(jid)
#start=time.time()
#sums1=pickle.load(cloud.bucket.getf("results/sums1"))
#sums2=pickle.load(cloud.bucket.getf("results/sums2"))
#stop=time.time()
#print "results download time: %.2f s" %(stop-start)
#res=0
#for i in range(n): 
#    if sums1[i] == sums2[i]:
#        res+=1
#print res 
#if res==matches: 
#    print "verification ok" 
#    
#input_.close()

def execute_query_local(query, share, kernel, n, m):
    random.seed(kernel)
    l=n*[0]
    share_f=open(share,'r')
    share_l=pickle.load(share_f)
    for x in range(n):
        sum_=0
        for (a,b) in query: 
            #print r, c
            sum_+=share_l[x][a][acgt.index(b)]*random.randrange(n*m)
        l[x]=sum_   
    return l 

if __name__ == '__main__':
    # query size q 
    q=20
    m=300
    n=15000
    query = generate_query(q)
    print len(query)
    start=time.time()
    matches=execute_query_clear(query)
    stop=time.time()
    print "query on clear; time %.2f s" % (stop-start)
    kernel = random.randrange(n*m*4)
    
    start=time.time()
    share1= path_+"\\shares\\share1"
    share2=path_+"\\shares\\share2"
    l1=execute_query_local(query, share1, kernel, n, m)
    l2=execute_query_local(query, share2, kernel, n, m)
    count=0
    for i in range(n): 
        if l1[i]==l2[i]: 
            count+=1 
    stop=time.time()
    print count,   
    print "; fp =",  (count-matches)
    print "query on the 2 shares; time %.2f s" % (stop-start)