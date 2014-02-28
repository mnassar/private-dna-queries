
# the objective of this module is to generate random DNA records 
# of given number and length 
# then to encrypt them one by one using homomorphic encryption 
 
acgt="ACGT"
 
import random
import cloud 
import time 
from paillier import generate_keypair, encrypt, decrypt, e_add, e_mul_const, e_add_const
import pickle
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

def encrypt_database_1(path_, file_, file_e_, n, m): # n is the nb of seqs, m is the length of a seq 
    # read the public key from stored file
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    
    henc = [[0 for y in range(2*m)] for x in range(n)]
    in_ = open(path_+file_,'r')
    x=0
    for line in in_:
        #print line 
        y=0
        for char in line:
            if char =='A':
                #encrypt 00 
                henc[x][y]=encrypt(pub, 0)
                henc[x][y+1]=encrypt(pub, 0)
                y+=2
            elif char=='C':
                #encrypt 01 
                henc[x][y]=encrypt(pub, 0)
                henc[x][y+1]=encrypt(pub, 1)
                y+=2
            elif char=='G':
                #encrypt 10 
                henc[x][y]=encrypt(pub, 1)
                henc[x][y+1]=encrypt(pub, 0)
                y+=2
            elif char=='T':
                #encrypt 11 
                henc[x][y]=encrypt(pub, 1)
                henc[x][y+1]=encrypt(pub, 1)
                y+=2
        x+=1
    out_= open(path_+file_e_,'wb')
    pickle.dump(henc, out_)
    out_.close()
    in_.close()
    return file_e_

def decrypt_database_1(path_, file_, file_d_):
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    buf=open(path_+"priv.txt",'rb') 
    priv=pickle.load(buf)
    buf.close()
    in_ = open(path_+file_, 'rb')
    henc=pickle.load(in_)
    out_ =open(path_+file_d_, 'w')
    
    for x in range( len(henc)): 
        for y in range(0, len(henc[0]), 2): 
            a=decrypt(priv,pub, henc[x][y])
            b=decrypt(priv,pub, henc[x][y+1]) 
            letter=''
            if a==0 and b==0:
                letter='A'
            elif a==0 and b==1: 
                letter='C'
            elif a==1 and b==0:
                letter='G'
            elif a==1 and b==1: 
                letter='T'
            out_.write(letter)
        out_.write("\n")
    out_.close()
    in_.close()
    return file_d_

def decrypt_query_res_1(res, path_):
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    buf=open(path_+"priv.txt",'rb')
    priv=pickle.load(buf)
    buf.close()
    dres=[0]*len(res)
    for i in range(len(res)): 
        dres[i]=decrypt(priv, pub, res[i])
    return dres.count(0)
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
def handle_query_1(query, path_, file_e_):
    in_=open(path_+file_e_, 'rb')
    henc=pickle.load(in_)
    in_.close()
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
#    buf=open(path_+"priv.txt",'rb')
#    priv=pickle.load(buf)
#    buf.close()
    res=[0]*len(henc)
    i=0
    for seq in henc:
        acc_0=1
        acc_1=1 
        t=0
        for (letter, pos) in query:
#            print letter, pos
#            print decrypt(priv, pub, seq[2*pos]), decrypt(priv, pub, seq[2*pos+1])
#            break
            if letter=='A': 
                acc_0=e_add(pub, acc_0, seq[2*pos])
                acc_0=e_add(pub, acc_0, seq[2*pos+1])
            elif letter=='C':
                acc_0=e_add(pub, acc_0, seq[2*pos])
                acc_1=e_add(pub, acc_1, seq[2*pos+1])
                t+=1
            elif letter=='G':
                acc_1=e_add(pub, acc_1, seq[2*pos])
                acc_0=e_add(pub, acc_0, seq[2*pos+1]) 
                t+=1
            elif letter=='T': 
                acc_1=e_add(pub, acc_1, seq[2*pos])
                acc_1=e_add(pub, acc_1, seq[2*pos+1])
                t+=2
            res[i]=e_add(pub, e_mul_const(pub, acc_0, random.randrange(pub.n)),
                         e_mul_const(pub, 
                                     e_add_const(pub, acc_1,  pub.n-t), 
                                     random.randrange(pub.n)))
        i+=1
    return decrypt_query_res_1(res, path_)
def query_generator(le, m):
    q=[]
    i=0
    while(i<le):
        y= random.randrange(m)
        if not y in q:
            q.append(y)
            i+=1
    for x in range(le):
        q[x]= (acgt[random.randrange(4)], q[x])
#    q.sort(key=lambda x: x[1])
    return q
            
if __name__ == '__main__':
    n=20
    m=30
    qsz=2
    path_="dna-db/"
#    path_="/home/picloud/dna-db/"
    file_="records.txt"
    file_e_="Erecords.txt"
    file_d_="Drecords.txt"
#    bitlength=128
#    jid=cloud.call(generate_keys, path_, bitlength, _vol="dna-db");
#    cloud.join(jid)
#    print cloud.result(jid)

#    jid=cloud.call(generate_database, path_, file_, n, m, _vol="dna-db"); 
#    cloud.join(jid)
#    print cloud.result(jid)

#    jid=cloud.call(encrypt_database_1, path_, file_, file_e_, n, m, _vol="dna-db")
#    cloud.join(jid)
#    print cloud.result(jid)

#    jid=cloud.call(decrypt_database_1, path_, file_e_, file_d_,  _vol="dna-db")
#    cloud.join(jid)
#    print cloud.result(jid)
#    query = [('A',1),  ('C',3)]
#    print query
#    print "run on cloud"
#    jid=cloud.call(handle_query_1, query, path_, file_e_, _vol="dna-db")
#    cloud.join(jid)
#    res=cloud.result(jid)
#    print res
#    print '%0.3f ms' % (cloud.info(jid).get(jid).get('runtime')*1000)

#    start=time.time()
#    print encrypt_database_1(path_, file_, file_e_, n, m)
#    stop=time.time()
#    print '%0.3f ms' % ((stop-start)*1000.0)
#    
    query=query_generator(qsz, m)
    print query 
    print "local processing" 
    path_="dna-db/"
    start=time.time()
    print handle_query_1 (query, path_, file_e_) 
    stop=time.time()
    print '%0.3f ms' % ((stop-start)*1000.0)
    print "local processing on clear"
    start=time.time()
    print handle_query_clear (query, path_, file_)
    stop=time.time()
    print '%0.3f ms' % ((stop-start)*1000.0)
    