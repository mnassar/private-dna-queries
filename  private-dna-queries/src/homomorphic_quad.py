
# the objective of this module is to generate random DNA records 
# of given number and length 
# then to encrypt them one by one using homomorphic encryption 
 
acgt="ACGT"
 
import random
import time 
import cloud  
from paillier import generate_keypair, encrypt, decrypt, e_add, e_mul_const,\
    e_add_const
import pickle

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap
# the keys are locally generated then the public and/or the private can be shared with the cloud  
def generate_keys(path_, bitlength): 
    priv, pub = generate_keypair(bitlength)
    f_priv=open(path_+"priv.txt",'wb')
    f_pub=open(path_+"pub.txt",'wb')
    f_priv.write(pickle.dumps(priv))
    f_pub.write(pickle.dumps(pub))
    f_priv.close()
    f_pub.close()
    return "Keys Generated"

def generate_database(path_, file_, n, m):
    # the database is saved to the volume dna-db and the path specified by file_
    buf=open(path_+file_,'w')
    for i in range(n):
        seq="" 
        for j in range(m): 
            seq+=acgt[random.randint(0,3)] 
        buf.write(seq+'\n')
    buf.close()
    return file_

def encrypt_database_2(path_, file_, file_e_, n, m): # n is the nb of seqs, m is the length of a seq 
    # read the public key from stored file
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    
    hA = [[0]*m for x in xrange(n)]
    hC = [[0]*m for x in xrange(n)]
    hG = [[0]*m for x in xrange(n)]
    hT = [[0]*m for x in xrange(n)]
    in_ = open(path_+file_,'r')
    x=0
    for line in in_:
        y=0
        for char in line.strip():
            if char =='A':
                hA[x][y]=encrypt(pub, 1)
            else:
                hA[x][y]=encrypt(pub, 0)
            if char =='C':
                hC[x][y]=encrypt(pub, 1)
            else:
                hC[x][y]=encrypt(pub, 0)
            if char =='G':
                hG[x][y]=encrypt(pub, 1)
            else:
                hG[x][y]=encrypt(pub, 0)
            if char =='T':
                hT[x][y]=encrypt(pub, 1)
            else:
                hT[x][y]=encrypt(pub, 0)
            y+=1
        x+=1
#    for x in hA: 
#        print x 
    out_= open(path_+file_e_,'wb')
    pickle.dump([hA,hC,hG,hT], out_)
    out_.close()
    in_.close()
    return file_e_

def decrypt_database_2(path_, file_, file_d_):
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    buf=open(path_+"priv.txt",'rb') 
    priv=pickle.load(buf)
    buf.close()
    in_ = open(path_+file_, 'rb')
    [hA, hC, hG, hT] =pickle.load(in_)
    for x in hA:
        print x 
    out_ =open(path_+file_d_, 'w')
    
    for x in range(len(hA)): 
        for y in range(len(hA[0])): 
            if decrypt(priv,pub, hA[x][y])==1: 
                out_.write('A')
                print 'A',
            elif decrypt(priv,pub, hC[x][y])==1:
                out_.write('C')
                print 'C',
            elif decrypt(priv,pub, hG[x][y])==1:
                out_.write('G')
                print 'G',
            elif decrypt(priv,pub, hT[x][y])==1:
                out_.write('T')
                print 'T',
        out_.write("\n")
        print 
    
    out_.close()
    in_.close()
    return file_d_

def decrypt_query_res_2(res, path_):
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    buf=open(path_+"priv.txt",'rb')
    priv=pickle.load(buf)
    buf.close()
    dres=[0]*len(res)
    for i in range(len(res)): 
        dres[i]=decrypt(priv, pub, res[i])
    return dres
def handle_query_clear(query, path_, file_):
    in_=open(path_+file_, 'r')
    rres=0
    for line in in_: 
        res=0
        for (letter, pos) in query:
            if line[pos]==letter: 
                res+=1 
        if res==len(query): 
            rres+=1
            print line, 
    return rres 
def handle_query_2(query, path_, file_e_):
    in_=open(path_+file_e_, 'rb')
    [hA,hC,hG,hT]=pickle.load(in_)
    in_.close()
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
#    buf=open(path_+"priv.txt",'rb')
#    priv=pickle.load(buf)
#    buf.close()
    res=[0]*len(hA) #equal to the number of seq 
    for i in range(len(hA)):
        acc=1
        for (letter, pos) in query:
            if letter=='A': 
                acc= e_add(pub, acc, hA[i][pos])
            elif letter=='C':
                acc= e_add(pub, acc, hC[i][pos])
            elif letter=='G':
                acc= e_add(pub, acc, hG[i][pos])
            elif letter=='T':
                acc= e_add(pub, acc, hT[i][pos])
        res[i]=e_mul_const(pub, e_add_const(pub, acc, pub.n-len(query)), random.randrange(pub.n))
    return decrypt_query_res_2(res, path_)
def query_generator(le, m):
    q=[]
    i=0
    while(i<le):
        y= random.randrange(m)
        if not y in q:
            q.append(y)
            i+=1
#    q.sort()
    for x in range(le):
        q[x]= (acgt[random.randrange(4)], q[x])
#    q.sort(key=lambda x: x[1])
    return q
if __name__ == '__main__':
    n=20
    m=30
    qsz=2
  
    file_="records.txt"
    file_e_="ErecordsQ.txt"
    file_d_="DrecordsQ.txt"
    bitlength=64
#    path_="/home/picloud/dna-db/"
#    jid=cloud.call(generate_keys, path_, bitlength, _vol="dna-db");
#    cloud.join(jid)
#    print cloud.result(jid)
#
#    jid=cloud.call(generate_database, path_, file_, n, m, _vol="dna-db"); 
#    cloud.join(jid)
#    print cloud.result(jid)
#    print '%0.3f ms' % (cloud.info(jid).get(jid).get('runtime')*1000) 
#
#    jid=cloud.call(encrypt_database_2, path_, file_, file_e_, n, m, _vol="dna-db")
#    cloud.join(jid)
#    print cloud.result(jid)
#    print '%0.3f ms' % (cloud.info(jid).get(jid).get('runtime')*1000)
    path_="dna-db/"
    start=time.time()
    print generate_keys(path_, bitlength), bitlength 
    stop=time.time()
    print '%0.3f ms' % ((stop-start)*1000.0)
    print "number of seq:", n
    print "len of seq:", m 
    start=time.time()
    print generate_database(path_, file_, n, m) 
    stop=time.time()
    print '%0.3f ms' % ((stop-start)*1000.0) 
    start=time.time()
    print encrypt_database_2(path_, file_, file_e_, n, m)
    stop=time.time()
    print '%0.3f ms' % ((stop-start)*1000.0)
#
#    jid=cloud.call(decrypt_database_2, path_, file_e_, file_d_,  _vol="dna-db")
#    cloud.join(jid)
#    print cloud.result(jid)
#local testing
#    path_="dna-db/"
#    encrypt_database_2(path_, file_, file_e_, n, m)
#    decrypt_database_2(path_, file_e_, file_d_)

#    query = [('A',1),  ('C',3)]
    query=query_generator(qsz, m)
    print query 
    
#    print "run on the cloud" 
#    path_="/home/picloud/dna-db/"
#    jid=cloud.call(handle_query_2, query, path_, file_e_, _vol="dna-db", _type='m1')
#    cloud.join(jid)
#    res=cloud.result(jid)
#    print res.count(0)
#    print '%0.3f ms' % (cloud.info(jid).get(jid).get('runtime')*1000) 
    
    print "run locally"  
    path_="dna-db/"
    start=time.time()
    res=handle_query_2 (query, path_, file_e_)
    stop=time.time()
    print '%0.3f ms' % ((stop-start)*1000.0)
    print res.count(0)  
    print "run locally on clear" 
    start=time.time()
    print handle_query_clear (query, path_, file_)
    stop=time.time()
    print '%0.3f ms' % ((stop-start)*1000.0)