'''
Created on Apr 8, 2014

@author: NASSAR
ternary storage scheme: 100 010 001 000 
for the 4th letter the query value is computed as E(1-(s1+s2+s3))  
precomputation of E(-k) 
precomputation of E(1)  

'''
import argparse
import cloud
import time 
import random
import sys
from gmpy2 import mpz, invert 
sys.path.append("paillier-master")
from paillier_gmpy2 import generate_keypair, encrypt, decrypt, e_add, e_mul_const,\
    e_add_const
import pickle
acgt="ACGT"
file_="records.txt"
file_e_0="Erecords.txt"
file_e_1="ErecordsQ.txt"
file_d_0="Drecords.txt"
file_d_1="DrecordsQ.txt"
file_pre="pre.txt"

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

@timing
def generate_keys(path_, bitlength): 
    priv, pub = generate_keypair(bitlength)
    f_priv=open(path_+"priv.txt",'wb')
    f_pub=open(path_+"pub.txt",'wb')
    f_priv.write(pickle.dumps(priv))
    f_pub.write(pickle.dumps(pub))
    f_priv.close()
    f_pub.close()
    return "Keys Generated"

@timing
def pre_compute(path_):
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    with open(path_+file_pre, 'w') as out:
        for k in range(1,101): 
            out.write("%s\n"%encrypt(pub, pub.n-k))
        out.close()
@timing
def generate_database(path_, file_, n, m):
    # the database is saved to the volume dna-db and the path specified by file_
    buf=open(path_+file_,'w')
    buf.write("%d %d\n" % (n, m) )
    for i in range(n):
        seq="" 
        for j in range(m): 
            seq+=acgt[random.randint(0,3)] 
        buf.write(seq+'\n')
    buf.close()
    return file_

@timing 
def encrypt_database_1(path_, file_, file_e_): 
    # read the public key from stored file
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()

    in_ = open(path_+file_,'r')
    n,m = in_.readline().split()
    n=int(n)
    m=int(m)
    out_= open(path_+file_e_,'w')
    out_.write("%s %s\n" %(n, 3*m))
    for line in in_:
        y=0
        for char in line.strip():
            if char =='A':
                out_.write("%s\n"%encrypt(pub, 1))
                out_.write("%s\n"%encrypt(pub, 0))
                out_.write("%s\n"%encrypt(pub, 0))
            if char =='C':
                out_.write("%s\n"%encrypt(pub, 0))
                out_.write("%s\n"%encrypt(pub, 1))
                out_.write("%s\n"%encrypt(pub, 0))
            if char =='G':
                out_.write("%s\n"%encrypt(pub, 0))
                out_.write("%s\n"%encrypt(pub, 0))
                out_.write("%s\n"%encrypt(pub, 1))
            if char =='T':
                out_.write("%s\n"%encrypt(pub, 0))
                out_.write("%s\n"%encrypt(pub, 0))
                out_.write("%s\n"%encrypt(pub, 0))
#    for x in hA: 
#        print x 

    out_.close()
    in_.close()
    return file_e_

@timing
def encrypt_database_0(path_, file_, file_e_): # n is the nb of seqs, m is the length of a seq 
    # read the public key from stored file
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    in_ = open(path_+file_,'r')
    n,m = in_.readline().split()
    n=int(n)
    m=int(m)
    x=0
    out_= open(path_+file_e_,'w')
    out_.write("%s %s\n" %(n, 2*m))
    for line in in_:
        #print line 
        for char in line:
            if char =='A':
                #encrypt 00 
                out_.write("%s\n" % encrypt(pub, 0))
                out_.write("%s\n" % encrypt(pub, 0))
            elif char=='C':
                #encrypt 01 
                out_.write("%s\n" % encrypt(pub, 0))
                out_.write("%s\n" % encrypt(pub, 1))
            elif char=='G':
                #encrypt 10 
                out_.write("%s\n" % encrypt(pub, 1))
                out_.write("%s\n" % encrypt(pub, 0))
            elif char=='T':
                #encrypt 11 
                out_.write("%s\n" % encrypt(pub, 1))
                out_.write("%s\n" % encrypt(pub, 1))
    out_.close()
    in_.close()
    return file_e_

@timing
def decrypt_database_0(path_, file_, file_d_):
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    buf=open(path_+"priv.txt",'rb') 
    priv=pickle.load(buf)
    buf.close()
    in_ = open(path_+file_, 'r')
    n, m =in_.readline().split()
    n=int(n)
    m=int(m)/2
    out_ =open(path_+file_d_, 'w')
    for x in range(n): 
        for y in range(0, 2*m, 2): 
            a=decrypt(priv,pub, mpz(in_.readline()))
            b=decrypt(priv,pub, mpz(in_.readline())) 
            letter=''
            if a==0 and b==0:
                letter='A'
            elif a==0 and b==1: 
                letter='C'
            elif a==1 and b==0:
                letter='G'
            elif a==1 and b==1: 
                letter='T'
#            print letter, 
            out_.write(letter)
#        print 
        out_.write("\n")
    out_.close()
    in_.close()
    return file_d_

@timing
def decrypt_database_1(path_, file_, file_d_):
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
    buf=open(path_+"priv.txt",'rb') 
    priv=pickle.load(buf)
    buf.close()
    in_ = open(path_+file_, 'r')
    n, m =in_.readline().split()
    n=int(n)
    m=int(m)/3
#    for x in hA:
#        print x 
    out_ =open(path_+file_d_, 'w')
    for x in range(n): 
        for y in range(m): 
            # we stop as soon as we find a 1 
            if decrypt(priv, pub, mpz(in_.readline()))==1:
                out_.write('A')
                in_.readline() 
                in_.readline()
#                print 'A',
            elif decrypt(priv, pub, mpz(in_.readline()))==1:
                out_.write('C')
                in_.readline()
#                print 'C',
            elif decrypt(priv, pub, mpz(in_.readline()))==1:
                out_.write('G')
#                print 'G',
            else:# decrypt(priv, pub, mpz(in_.readline()))==1:
                out_.write('T')
#                print 'T',
        out_.write("\n")
#        print 
    
    out_.close()
    in_.close()
    return file_d_

@timing 
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

@timing 
def decrypt_query_res(res, path_):
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

@timing
def handle_query_1(query, path_, file_e_):
    in_=open(path_+file_e_, 'r')
    n, m =in_.readline().split()
    n=int(n)
    m=int(m)/3
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
#    buf=open(path_+"priv.txt",'rb')
#    priv=pickle.load(buf)
#    buf.close()
#    print query 
    query.sort(key=lambda x: x[1])
#    print query
    res=[0]*n #equal to the number of seq 
    significant_time_=[0]*n
#    counter=0
    cnst_1_= encrypt(pub, 1)
    with open(path_+file_pre, 'r') as pre_: 
            cnst= mpz(pre_.readlines()[len(query)-1])
            pre_.close()
    for i in range(n):
        acc=1
        old_pos=0
        for (letter, pos) in query:
            for j in range(old_pos, pos):
                in_.readline()
                in_.readline()
                in_.readline()
            
#                counter+=4
#            print counter
            old_pos=pos+1
            s1_=mpz(in_.readline())
            s2_=mpz(in_.readline())
            s3_=mpz(in_.readline())
            if letter=='A': 
                st_=time.time()
                acc= e_add(pub, acc, s1_)
                significant_time_[i]+=time.time()-st_
            elif letter=='C':
                st_=time.time()
                acc= e_add(pub, acc, s2_)
                significant_time_[i]+=time.time()-st_
            elif letter=='G':
                st_=time.time()
                acc= e_add(pub, acc, s3_)
                significant_time_[i]+=time.time()-st_
            elif letter=='T':
                st_=time.time()
                acc= e_add(pub, acc, e_add(pub, cnst_1_, invert(e_add(pub,e_add(pub, s1_, s2_),s3_), pub.n_sq)))
                significant_time_[i]+=time.time()-st_
#            counter+=4
#            print counter 
        for j in range(3*pos+3, 3*m):
            in_.readline()
#            counter+=1
#        print counter
        st_=time.time()
        res[i]=e_mul_const(pub, e_add(pub, acc, cnst), random.randrange(pub.n))
        significant_time_[i]+=time.time()-st_
        #print significant_time_[i]
    in_.close()
    sg=sum(significant_time_)
    print "sum significant query time = %f s" % (sg)
    return decrypt_query_res(res, path_), sg



@timing 
def handle_query_0(query, path_, file_e_):
    in_=open(path_+file_e_, 'r')
    n, m =in_.readline().split()
    n=int(n)
    m=int(m)/2 
    buf=open(path_+"pub.txt",'rb')
    pub=pickle.load(buf)
    buf.close()
#    buf=open(path_+"priv.txt",'rb')
#    priv=pickle.load(buf)
#    buf.close()
    res=[0]*n
    significant_time_=[0]*n
    query.sort(key=lambda x: x[1])
    i=0
    ltrs=map(lambda x:x[0], query)
    t=ltrs.count('T')*2+ltrs.count('C')+ltrs.count('G')
    with open(path_+file_pre, 'r') as pre_: 
            cnst= mpz(pre_.readlines()[t-1])
            pre_.close()
    for seq in range(n):
        acc_0=1
        acc_1=1 
        old_pos=0
        
        for (letter, pos) in query:
#            print letter, pos
#            print decrypt(priv, pub, seq[2*pos]), decrypt(priv, pub, seq[2*pos+1])
#            break
            for j in range(old_pos, pos): 
                in_.readline()
                in_.readline()
            old_pos=pos+1
            
            if letter=='A': 
                st_=time.time()
                acc_0=e_add(pub, acc_0, mpz(in_.readline()))
                acc_0=e_add(pub, acc_0, mpz(in_.readline()))
                significant_time_[i]+=time.time()-st_
            elif letter=='C':
                st_=time.time()
                acc_0=e_add(pub, acc_0, mpz(in_.readline()))
                acc_1=e_add(pub, acc_1, mpz(in_.readline()))
                significant_time_[i]+=time.time()-st_
            elif letter=='G':
                st_=time.time()
                acc_1=e_add(pub, acc_1, mpz(in_.readline()))
                acc_0=e_add(pub, acc_0, mpz(in_.readline()))
                significant_time_[i]+=time.time()-st_ 
            elif letter=='T': 
                st_=time.time()
                acc_1=e_add(pub, acc_1, mpz(in_.readline()))
                acc_1=e_add(pub, acc_1, mpz(in_.readline()))
                significant_time_[i]+=time.time()-st_
        st_=time.time()
        res[i]=e_add(pub, e_mul_const(pub, acc_0, random.randrange(pub.n)),
                         e_mul_const(pub, 
                                     e_add(pub, acc_1, cnst), 
                                     random.randrange(pub.n)))
        significant_time_[i]+=time.time()-st_
        i+=1
        for j in range(2*pos+2, 2*m):
            in_.readline()
    
    in_.close()
    sg=sum(significant_time_)
    print "sum significant query time = %f s" % (sg)
    return decrypt_query_res(res, path_), sg 

@timing
def handle_query_clear(query, path_, file_):
    in_=open(path_+file_, 'r')
    rres=0
    print in_.readline().strip()
    for line in in_: 
        res=0
        for (letter, pos) in query:
            if line[pos]==letter: 
                res+=1 
        if res==len(query): 
            rres+=1
#            print line, 
    return rres 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process counting queries over encrypted DNA database')
    parser.add_argument('-pi',  help='run on picloud', action="store_true")
    parser.add_argument('-gk', metavar='bitlength',  help='generate key pair, store on pub.txt and priv.txt', type=int)
    parser.add_argument('-gd', nargs=2, metavar=('n', 'm'), help='generate random database, n is number of sequences, m is number of letters per sequence, store to records.txt', type=int)
    parser.add_argument('-ed',  help='encrypt database: (0) binary mode, store in Erecords.txt \
                                                        (1) quaternary mode, store in ErecordsQ.txt'
                                                        , choices=[0,1], type= int)
    parser.add_argument('-dd',  help='decrypt database: (0) binary mode, decrypts from Erecords.txt \
                                                        (1) quaternary mode, decrypts from ErecordsQ.txt ', 
                                                        choices=[0,1], type=int)
    parser.add_argument('-gq', nargs=2, metavar=('l', 'm'),  help='generate random query of l positions among m', type=int)
    parser.add_argument('-eq',  help='execute query: (0) on binary mode, using Erecords.txt \
                                                        (1) on quaternary mode, using ErecordsQ.txt ', 
                                                        choices=[0,1,2], type=int)
    parser.add_argument('-v', '--verify',  help='run query on plain-text database', action="store_true")
    parser.add_argument('-s', '--sync',  help='(0) synchronize cloud\'s folder to local folder and exit; \
                (1) synchronize local folder to cloud\'s folder and exit', type=int, choices=[0,1])
    args = parser.parse_args()
    
    if args.sync==0:
        print "synchronize cloud\'s folder to local folder and exit;"
        cloud.volume.sync('dna-db:', './dna-db')
        exit()
    elif args.sync==1:
        print "synchronize local folder to cloud\'s folder and exit;"
        cloud.volume.sync('./dna-db', 'dna-db:')
        exit()
    if args.pi: 
        print "code for cloud not ready for private_dna_pre "
      
    else: 
        print "running locally"
        path_="dna-db-ter/"
        if args.gk:
            bitlength=args.gk
            print generate_keys(path_, bitlength)
            pre_compute(path_) # must be recomputed for each new key 
        if args.gd: 
            n=args.gd[0]
            m=args.gd[1]
            print generate_database(path_, file_, n, m) 
        if args.ed==0: 
            print "encrypt database using binary mode"
            print encrypt_database_0(path_, file_, file_e_0)
        elif args.ed==1: 
            print "encrypt database using quaternary mode"
            print encrypt_database_1(path_, file_, file_e_1)
        if args.dd==0: 
            print "decrypt database from binary mode"
            decrypt_database_0(path_, file_e_0, file_d_0)
        elif  args.dd==1:
            print "decrypt database from quaternary mode"
            decrypt_database_1(path_, file_e_1, file_d_1)
        if args.gq:
            le=args.gq[0] 
            m=args.gq[1] 
            print "generate random query %d over %d" %(le, m)
            query = query_generator(le,m)
#            print query
            if args.eq==0: 
                print "execute query on binary mode"
                res, sg0=handle_query_0 (query, path_, file_e_0)
                print res 
            elif args.eq==1: 
                print "execute query on quaternary mode"
                res, sg1=handle_query_1 (query, path_, file_e_1)
                print res
            elif args.eq==2:
                print "execute query on binary mode"
                res, sg0=handle_query_0 (query, path_, file_e_0)
                print res
                print "execute query on quaternary mode"
                res, sg1=handle_query_1 (query, path_, file_e_1)
                print res
                print "gain ratio = %f" % (sg0/sg1)
                
            if args.verify: 
                print "verification on clear database"
                print handle_query_clear (query, path_, file_)
                
        if args.eq!=None and args.gq ==None: 
            print "sorry! -eq must be coupled with -gq"    
        