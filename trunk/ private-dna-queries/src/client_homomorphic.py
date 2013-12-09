
# this module emits aggregate queries to the cloud 
# and contains the query evaluation code to be run at the cloud side
# the cloud has the homomorphically encrypted sequences  
# the decryption of the results are done by the client
# (number of decryption required = number of sequences (n) )

# experiments to do: query time vs. query size vs. database size  
import random
from data_generator_homomorphic import path_
import pickle
from paillier import *
acgt="ACGT"

buf=open(path_+"\\tests\\pub.txt",'r')
pub=pickle.load(buf)
buf.close()

buf=open(path_+"\\tests\\priv.txt",'r') 
priv=pickle.load(buf)
buf.close()

def generate_query(q,m):
    query=[]
    for i in range(q): 
        r=random.randrange(m)
        c=random.randrange(4)
        query.append((r,c))
    query.sort()
    return query 
    
def execute_query(query,n,m):
    file_ae=open(path_+"\\tests\\EA_records.txt",'r')
    homo=pickle.load(file_ae)
    zero_enc=encrypt(pub,0)
    res=n*[zero_enc]
    
    for i in range(n):
        for (a,b) in query:
            r=random.randrange(pub.n)
            v=e_mul_const(pub, e_add(pub, homo[i][a], encrypt(pub,-ord(acgt[b])%pub.n)),r)
            res[i]=e_add(pub, res[i], v)
            
        i+=1
    return res

def verification(res, query, n):
    records = open(path_+"\\tests\\records.txt",'r')
    line=records.readline()
    i=0
    count=0
    fp=n*[0]
    while line!="":
        if decrypt(priv, pub, res[i])==0:
            count+=1
            for (a,b) in query:
                print line[a],
                if line[a]!=acgt[b]:
                    fp[i]=1
            print
        i+=1
        line=records.readline()
    print "count ", count
    print "false positives", fp.count(1) 

import time     
if __name__ == '__main__':
    q=40
    n=200
    m=300
    query=generate_query(q,n)
    for i in range(q):
        index, letter = query [i]
        print index, acgt[letter]
    start=time.time()
    res=execute_query(query,n,m)
    stop=time.time()
    print "query execution time %1.2f s"% (stop-start)
    verification (res, query, n)
    
    