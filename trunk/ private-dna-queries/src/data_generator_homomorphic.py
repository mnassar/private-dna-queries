
# the objective of this module is to generate random DNA records 
# of given number and length 
# then to encrypt them one by one using homomorphic encryption 
path_="C:\Users\NASSAR\Documents\DNA_"

acgt="ACGT"

import random
import cloud  
from paillier import *
import pickle
# the keys are locally generated then the public and/or the private can be shared with the cloud  
#    priv, pub = generate_keypair(128)
#    f_priv=open(path_+"\\tests\\priv.txt",'w')
#    f_pub=open(path_+"\\tests\\pub.txt",'w')
#    f_priv.write(pickle.dumps(priv))
#    f_pub.write(pickle.dumps(pub))
#    f_priv.close()
#    f_pub.close()

def generate_database(n,m):
    if cloud.running_on_cloud():
        #run only once 
        #cloud.volume.create("tests","tests")
        file_="tests/records.txt"
    else:
        file_=path_+"\\tests\\records.txt"
    buf= open(file_,'w')
    print n,m 
    for i in range(n):
        seq="" 
        for j in range(m): 
            seq+=acgt[random.randint(0,3)] 
        buf.write(seq+'\n')
        #print seq
    buf.close()
    cloud.bucket.put(file_,"homo/records")
    return 



def encrypt_database(n,m):
    if cloud.running_on_cloud():
        file_="tests/records.txt"
        file_e="tests/E_records.txt"
        buf=open("tests/pub.txt",'r')
        pub=pickle.load(buf)
        buf.close()
        
    else:
        file_=path_+"\\tests\\records.txt"
        file_e=path_+"\\tests\\E_records.txt"
        buf=open(path_+"\\tests\\pub.txt",'r')
        pub=pickle.load(buf)
        buf.close()
    homo = [[0 for y in range(m)] for x in range(n)]
    ibuf = open(file_,'r')
    obuf= open(file_e,'w')
    line=" "
    x=0
    while (line!=""):
        line=ibuf.readline().strip()
        if x==0: 
            print line
        y=0
        for char in line:
            #encrypt 
            homo[x][y]=encrypt(pub,ord(char))
            y+=1
        x+=1
    obuf.write(pickle.dumps(homo))
    obuf.close()
    ibuf.close()
    return file_e

def decrypt_database(n,m):
    file_e="tests/E_records.txt"
    file_o="tests/D_records.txt"
    buf=open(path_+"\\tests\\pub.txt",'r')
    pub=pickle.load(buf)
    buf.close()
    buf=open(path_+"\\tests\\priv.txt",'r') 
    priv=pickle.load(buf)
    buf.close()
    ibuf = open(file_e, 'r')
    obuf =open(file_o, 'w')
    ibuf_=pickle.load(ibuf)
    for x in range(2): 
        for y in range(3): 
            obuf.write("%s %s \n" % (ibuf_[x][y], chr(decrypt(priv,pub, ibuf_[x][y]))) )
    obuf.close()
    cloud.bucket.put(file_o,"homo/D_records")   

# this function is to be run by the cloud
# it computes 4 files for the 4 alphabet letters
# each file contains n*m encryptions of the corresponding letter
#    
def generate_precomputed_encryption(n,m,char, pub):
    file_A=open("tests/"+char+"_enc.txt",'w')
    #file_C=open("tests/C_enc.txt",'w')
    #file_G=open("tests/G_enc.txt",'w')
    #file_T=open("tests/T_enc.txt",'w')
#    buf=open("tests/pub.txt",'r')
#    pub=pickle.load(buf)
#    buf.close()
    for i in range(n*m):
        file_A.write("%s\n"% encrypt(pub,ord(char)))
        #file_C.write("%s\n"% encrypt(pub,ord('C')))
        #file_G.write("%s\n"% encrypt(pub,ord('G')))
        #file_T.write("%s\n"% encrypt(pub,ord('T')))
    file_A.close()
    #file_C.close()
    #file_G.close()
    #file_T.close()
    cloud.bucket.put("tests/"+char+"_enc.txt","homo/"+char+"_enc.txt")
    #cloud.bucket.put("tests/C_enc.txt","homo/C_enc.txt")
    #cloud.bucket.put("tests/G_enc.txt","homo/G_enc.txt")
    #cloud.bucket.put("tests/T_enc.txt","homo/T_enc.txt")
    return 


# this function is to be run locally 
def server_aided_encryption(n,m):
    file_A=open( path_+"\\tests\\A_enc.txt",'r')
    file_C=open(path_+"\\tests\\C_enc.txt",'r')
    file_G=open(path_+"\\tests\\G_enc.txt",'r')
    file_T=open(path_+"\\tests\\T_enc.txt",'r')
    file_= open(path_+"\\tests\\records.txt",'r')
    file_ea= open(path_+"\\tests\\EA_records.txt",'w')
    a=file_A.readline().strip()
    c=file_C.readline().strip()
    g=file_G.readline().strip()
    t=file_T.readline().strip()
    homo = [[0 for y in range(m)] for x in range(n)]
    line=" "
    x=0
    while (line!=""):
        line=file_.readline().strip()
        y=0
        for char in line:
            if char=='A':
                homo[x][y]=long(a)
            elif char=='C':
                homo[x][y]=long(c)
            elif char=='G':
                homo[x][y]=long(g)
            elif char=='T':
                homo[x][y]=long(t)
            y+=1
        x+=1
    file_ea.write(pickle.dumps(homo))
    file_.close()
    file_ea.close()
    file_A.close()
    file_C.close()
    file_G.close()
    file_T.close()
    return path_+"\\tests\\EA_records.txt"

def generate_precomputed_encryption_local((n,m,char)):
    buf=open(path_+"\\tests\\pub.txt",'r')
    pub=pickle.load(buf)
    buf.close()
    file_A=open(path_+"\\tests\\"+char+"_enc.txt",'a')
    for i in range(n*m):
        file_A.write("%s\n"% encrypt(pub,ord(char)))
    file_A.close()
    return

import time     
if __name__ == '__main__':
    n=20
    m=300
    print n,m 
#    from multiprocessing import Pool 
#    start=time.time()
#    pool=Pool(4)
#    pool.map(generate_precomputed_encryption_local, [(n,m,c) for c in ['A','C','G','T']])
#    pool.close()
#    pool.join()
#    stop=time.time()
#    print "locally pre-computing encrypted letters time %d" % (stop-start)

    buf=open(path_+"\\tests\\pub.txt",'r')
    pub=pickle.load(buf)
    buf.close()
#    buf=open(path_+"\\tests\\priv.txt",'r') 
#    priv=pickle.load(buf)
#    buf.close()
#    cloud.volume.sync(path_+"/tests/pub.txt","tests:pub.txt")
    
#    start=time.time()
#    generate_database(n,m)
#    stop=time.time()
#    print "database generation time (local): %d s"%(stop-start)
#    start=time.time()
#    file_e=encrypt_database(n,m)
#    stop=time.time()
#    print "database encryption time (local) %d s"%(stop-start)

    start=time.time()
    jids=cloud.map(generate_precomputed_encryption,4*[n],4*[m],['A','C','G','T'],4*[pub],_vol="tests",_type='f2',_cores=4)
    print jids
    cloud.join(jids)
    stop=time.time()
    print "cloud pre-prepares encrypted letters; time: %d s"%(stop-start)
    
#    # download pre-prepared encryptions 
#    start=time.time()
#    file_A=cloud.bucket.get("homo/A_enc.txt", path_+"\\tests\\A_enc.txt")
#    file_C=cloud.bucket.get("homo/C_enc.txt", path_+"\\tests\\C_enc.txt")
#    file_G=cloud.bucket.get("homo/G_enc.txt", path_+"\\tests\\G_enc.txt")
#    file_T=cloud.bucket.get("homo/T_enc.txt", path_+"\\tests\\T_enc.txt")
#    stop=time.time()
#    print "download pre-prepared encrypted letters; time (connection dependent) %d s"%(stop-start)
    
#    start=time.time()
#    file_ea=server_aided_encryption(n,m)
#    stop=time.time()
#    print "local server-aided encryption %1.2f s"%(stop-start)
#    
#    start=time.time()
#    cloud.volume.sync(path_+"/tests/EA_records.txt","tests:EA_records.txt")
#    stop=time.time()
#    print "synchronizing encrypted database with volume time %d s"%(stop-start)
##  
#    start=time.time()
#    file_e=path_+"\\tests\\E_records.txt"
#    ibuf = open(file_e, 'r')
#    ibuf_=pickle.load(ibuf)
#    for x in range(n): 
#        for y in range(m): 
#            print ibuf_[x][y], chr(decrypt(priv,pub, ibuf_[x][y]))
#        break
    
#    file_ea=path_+"\\tests\\EA_records.txt"
#    ibuf = open(file_ea, 'r')
#    ibuf_=pickle.load(ibuf)
#    for x in range(n): 
#        for y in range(m): 
#            print ibuf_[x][y], chr(decrypt(priv,pub, ibuf_[x][y]))
#        break
  
#def generate_database_cloud:    
#            
#    print "cloud generate database, store to volume tests / records.txt, store to bucket homo / records "
#    pid=cloud.call(generate_database,n,m,_vol="tests")
#    cloud.join(pid)
#    records=cloud.bucket.getf("homo/records")
#    for l in records.readlines():
#        print l.strip();
#    print "cloud encrypt database, store to volume tests / E_records.txt"
#    pid=cloud.call(encrypt_database,n,m,_vol="tests")
#    cloud.join(pid)
#    print "cloud decrypt database, store to volume tests / D_records.txt, store to bucket homo / D_records "
#    pid=cloud.call(decrypt_database,n,m,_vol="tests")
#    cloud.join(pid)
#    D_records=cloud.bucket.getf("homo/D_records")
#    print "retreive results"
#    for l in D_records.readlines():
#        print l.strip();
