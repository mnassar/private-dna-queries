#!/usr/bin/env python

from paillier_gmpy2 import *
#from paillier import *

import sys 
import random
import time 

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
        e[i]=encrypt(pub, l[i])
    return e

def test_decrypt(e):
    d=[0]*100
    for i in range(100):
        d[i]=decrypt(priv, pub, e[i]) 
        print d[i], 
    print 
    return d 

def test_e_add(e):
    e_add_tab=[0]*99
    for i in range(99):
        e_add_tab[i]= e_add(pub, e[i], e[i+1])
#        print e_add_tab[i]
#    for x in e_add_tab:
#        print str(x)
    return e_add_tab    

def test_e_add_cnst(e,l):
    e_add_cnst_tab=[0]*100
    for i in range(100):
        e_add_cnst_tab[i]=e_add_const(pub, e[i], l[i])
    return e_add_cnst_tab

def test_e_mul_cnst(e,l):
    e_mul_cnst_tab=[0]*100
    for i in range(100):
        e_mul_cnst_tab[i]=e_mul_const(pub, e[i], l[i])
    return e_mul_cnst_tab

def test(bitlength):    
    global priv, pub 
    print "Generating keypair..."
    time1=time.time()
    priv, pub = generate_keypair(bitlength)
    time2=time.time()    
    print time2-time1
    l=[0]*100
    for i in range(100):
        x=random.randrange(sys.maxint)
        print x,
        l[i]=x
    print
    t_test_encrypt=timing(test_encrypt)
    e= t_test_encrypt(l)
    t_test_decrypt=timing(test_decrypt)
    d= t_test_decrypt(e)
    test=True
    for i in range(100): 
        if l[i]!=d[i]:
            print i, l[i], d[i]
            test=False
            break
    print "test is %s" % test

    
    t_test_e_add=timing(test_e_add)
    e_add_tab=t_test_e_add(e)
    t_test_e_add_cnst=timing(test_e_add_cnst)
    e_add_cnst_tab=t_test_e_add_cnst(e, l)
    t_test_e_mul_cnst=timing(test_e_mul_cnst)
    e_add_mul_tab=t_test_e_mul_cnst(e, l)

if __name__ == '__main__':
    test(1024)

        
    
    x = 3
    print "Encrypting x..."
    cx = encrypt(pub, x)
    print "cx =", cx
    
    y = 5
    print "y =", y
    print "Encrypting y..."
    cy = encrypt(pub, y)
    print "cy =", cy
    
    print "Computing cx + cy..."
    cz = e_add(pub, cx, cy)
    print "cz =", cz
    
    print "Decrypting cz..."
    z = decrypt(priv, pub, cz)
    print "z =", z
    
    print "Computing decrypt((cz + 2) * 3) ..."
    print "result =", decrypt(priv, pub,
                              e_mul_const(pub, e_add_const(pub, cz, 2), 3))
