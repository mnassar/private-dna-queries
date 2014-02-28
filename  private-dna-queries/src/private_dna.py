'''
Created on Feb 25, 2014

@author: NASSAR
'''
import argparse
import cloud
import time 
import random
import sys
sys.path.append("paillier-master")
from paillier import generate_keypair, encrypt, decrypt, e_add, e_mul_const,\
    e_add_const
import pickle
acgt="ACGT"
file_="records.txt"
file_e_0="Erecords.txt"
file_e_1="ErecordsQ.txt"
file_d_0="Drecords.txt"
file_d_1="DrecordsQ.txt"

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
    hA = [[0]*m for x in xrange(n)]
    hC = [[0]*m for x in xrange(n)]
    hG = [[0]*m for x in xrange(n)]
    hT = [[0]*m for x in xrange(n)]
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
    pickle.dump("%d %d\n" % (n, m), out_ )
    pickle.dump([hA,hC,hG,hT], out_)
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
    henc = [[0 for y in range(2*m)] for x in range(n)]
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
    pickle.dump("%d %d\n" % (n, m), out_ )
    pickle.dump(henc, out_)
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
    in_ = open(path_+file_, 'rb')
    print pickle.load(in_).strip()
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
            print letter, 
            out_.write(letter)
        print 
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
    in_ = open(path_+file_, 'rb')
    print pickle.load(in_).strip()
    [hA, hC, hG, hT] =pickle.load(in_)
#    for x in hA:
#        print x 
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
    return dres

@timing
def handle_query_1(query, path_, file_e_):
    in_=open(path_+file_e_, 'rb')
    print pickle.load(in_).strip()
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
    return decrypt_query_res_1(res, path_)

@timing
def decrypt_query_res_0(res, path_):
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

@timing 
def handle_query_0(query, path_, file_e_):
    in_=open(path_+file_e_, 'rb')
    print pickle.load(in_).strip()
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
    return decrypt_query_res_0(res, path_)

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
            print line, 
    return rres 
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
                                                    choices=[0,1], type=int)
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
    print "running on cloud"
    path_="/home/picloud/dna-db/"
    if args.gk:
        bitlength=args.gk
        jid=cloud.call(generate_keys, path_, bitlength, _vol="dna-db");
        cloud.join(jid)
        print 'job function took %0.3f ms' % (cloud.info(jid).get(jid).get('runtime')*1000) 
        print cloud.info(jid).get(jid).get('stdout').strip()
        print cloud.result(jid)
    if args.gd:
        n=args.gd[0]
        m=args.gd[1]
        jid=cloud.call(generate_database, path_, file_, n, m, _vol="dna-db"); 
        cloud.join(jid)
        print 'job took %0.3f s' % (cloud.info(jid).get(jid).get('runtime')) 
        print cloud.info(jid).get(jid).get('stdout').strip()
        print cloud.result(jid)
    if args.ed==0: 
        print "encrypt database using binary mode"
        jid=cloud.call(encrypt_database_0, path_, file_, file_e_0, _vol="dna-db")
        cloud.join(jid)
        print 'job took %0.3f s' % (cloud.info(jid).get(jid).get('runtime'))
        print cloud.info(jid).get(jid).get('stdout').strip()
        print cloud.result(jid)
        
    elif args.ed==1: 
        print "encrypt database using quaternary mode"
        jid=cloud.call(encrypt_database_1, path_, file_, file_e_1, _vol="dna-db")
        cloud.join(jid)
        print 'job took %0.3f s' % (cloud.info(jid).get(jid).get('runtime'))
        print cloud.info(jid).get(jid).get('stdout').strip()
        print cloud.result(jid)
    if args.dd==0: 
        print "decrypt database from binary mode"
        jid=cloud.call(decrypt_database_0, path_, file_e_0, file_d_0,  _vol="dna-db")
        cloud.join(jid)
        print 'job took %0.3f s' % (cloud.info(jid).get(jid).get('runtime'))
        print cloud.info(jid).get(jid).get('stdout').strip()
        print cloud.result(jid)
    elif  args.dd==1:
        print "decrypt database from quaternary mode"
        jid=cloud.call(decrypt_database_1, path_, file_e_1, file_d_1,  _vol="dna-db")
        cloud.join(jid)
        print 'job took %0.3f s' % (cloud.info(jid).get(jid).get('runtime'))
        print cloud.info(jid).get(jid).get('stdout').strip()
        print cloud.result(jid)
    if args.gq:
        le=args.gq[0]
        m=args.gq[1]
        print "generate random query" 
        jid=cloud.call(query_generator, le, m, _vol="dna-db")
        cloud.join(jid)
        print 'job took %0.3f s' % (cloud.info(jid).get(jid).get('runtime'))
        print cloud.info(jid).get(jid).get('stdout').strip()
        query = cloud.result(jid)
        print query
        if args.eq==0: 
            print "execute query on binary mode"
            jid=cloud.call(handle_query_0, query, path_, file_e_0, _vol="dna-db")
            cloud.join(jid)
            print 'job took %0.3f ms' % (cloud.info(jid).get(jid).get('runtime')*1000)
            print cloud.info(jid).get(jid).get('stdout').strip()
            res=cloud.result(jid)
            print res.count(0)
        elif args.eq==1: 
            print "execute query on quaternary mode"
            jid=cloud.call(handle_query_1, query, path_, file_e_1, _vol="dna-db")
            cloud.join(jid)
            print 'job took %0.3f ms' % (cloud.info(jid).get(jid).get('runtime')*1000)
            print cloud.info(jid).get(jid).get('stdout').strip()
            res=cloud.result(jid)
            print res.count(0)
        if args.verify: 
            print "verification on clear database"
            jid = cloud.call(handle_query_clear, query, path_, file_, _vol="dna-db")
            cloud.join(jid)
            print 'job took %0.3f ms' % (cloud.info(jid).get(jid).get('runtime')*1000)
            print cloud.info(jid).get(jid).get('stdout').strip()
            print cloud.result(jid)
    if args.eq!=None and args.gq ==None: 
        print "sorry! -eq must be coupled with -gq"         
else: 
    print "running locally"
    path_="dna-db/"
    if args.gk:
        bitlength=args.gk
        print generate_keys(path_, bitlength)
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
        print "generate random query"
        query = query_generator(le,m)
        print query
        if args.eq==0: 
            print "execute query on binary mode"
            res=handle_query_0 (query, path_, file_e_0).count(0)
            print res 
        elif args.eq==1: 
            print "execute query on quaternary mode"
            res=handle_query_1 (query, path_, file_e_1).count(0)
            print res
        if args.verify: 
            print "verification on clear database"
            print handle_query_clear (query, path_, file_)
            
    if args.eq!=None and args.gq ==None: 
        print "sorry! -eq must be coupled with -gq"    
        