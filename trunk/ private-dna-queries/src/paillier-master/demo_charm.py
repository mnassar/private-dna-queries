'''
Created on Feb 25, 2014

@author: NASSAR
'''
from charm.toolbox.integergroup import RSAGroup
from charm.schemes.pkenc.pkenc_paillier99 import Pai99
import random, sys, time  
#from charm.core.math.integer import *
def timing(f, c=0):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        clocktime=time2-time1
        print '%s function took %0.3f ms' % (f.func_name, (clocktime)*1000.0)
        if c==0:
            return ret
        else: 
            return ret, clocktime 
    return wrap

def test_encrypt(l):
    e=[0]*100
    for i in range(100):        
        x=pai.encode(public_key['n'], l[i])
        e[i]=pai.encrypt(public_key, x)
        #print str(e[i])
    return e 
def test_decrypt(e):
    d=[0]*100
    for i in range(100):
        d[i]=pai.decrypt(public_key, secret_key, e[i])
    return d

def test_e_add(e):
    e_add_tab=[0]*99
    for i in range(99):
        e_add_tab[i]= e[i]+ e[i+1]
#        print e_add_tab[i]
#    for x in e_add_tab:
#        print str(x)
    return e_add_tab    

def test_e_add_cnst(e,l):
    e_add_cnst_tab=[0]*100
    for i in range(100):
#        x=pai.encrypt(public_key, l[i])
#        e_add_cnst_tab[i]= e[i] + x
        e_add_cnst_tab[i]= e[i]+ l[i]
    return e_add_cnst_tab

def test_e_mul_cnst(e,l):
    e_mul_cnst_tab=[0]*100
    for i in range(100):
        e_mul_cnst_tab[i]= e[i] * l[i]
    return e_mul_cnst_tab
     
def test(bitlength): 
    global public_key, secret_key, pai 
    time1=time.time()
    group = RSAGroup()
    pai = Pai99(group)
    (public_key, secret_key) = pai.keygen(bitlength) # default is 1024
    time2=time.time()
    print "key generation %.3f ms" % ((time2-time1)*1000)
    l=[0]*100
    for i in range(100):
        x=random.randrange(sys.maxint)
#        print x,
        l[i]=x
    print
    t_test_encrypt=timing(test_encrypt)
    e= t_test_encrypt(l)
#    t_test_decrypt=timing(test_decrypt)
#    d= t_test_decrypt(e)
#    for i in range(100): 
#        print  int(d[i]),
#    print 
#    test=True
#    for i in range(100): 
#        if l[i]!=d[i]:
#            print i, l[i], d[i]
#            test=False
#            break
#    print "test is %s" % test

    
#    t_test_e_add=timing(test_e_add)
#    e_add_tab=t_test_e_add(e)
    t_test_e_add_cnst=timing(test_e_add_cnst)
    e_add_cnst_tab=t_test_e_add_cnst(e, l)
#    t_test_e_mul_cnst=timing(test_e_mul_cnst)
#    e_mul_cnst_tab=t_test_e_mul_cnst(e, l)
#    for i in range(100): 
#        print int(d[i])+l[i], int(pai.decrypt(public_key, secret_key, e_add_cnst_tab[i]))
if __name__ == '__main__':
    test(512)
    
    
#msg_1=12345678987654321
#msg_2=12345761234123409
#msg_3 = msg_1 + msg_2
#msg_1 = pai.encode(public_key['n'], msg_1)
#print msg_1
#msg_2 = pai.encode(public_key['n'], msg_2)
#msg_3 = pai.encode(public_key['n'], msg_3) 
#print msg_3
#cipher_1 = pai.encrypt(public_key, msg_1)
#cipher_2 = pai.encrypt(public_key, msg_2)
#cipher_3 = cipher_1 + cipher_2
#decrypted_msg_3 = pai.decrypt(public_key, secret_key, cipher_3)
#print decrypted_msg_3 == msg_3
