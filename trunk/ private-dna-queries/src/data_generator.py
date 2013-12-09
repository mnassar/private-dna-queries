'''
Created on Jun 2, 2013

@author: NASSAR
'''
import cloud
import random 
import time 
import cPickle as pickle 
acgt="ACGT"
path_="C:\Users\NASSAR\Documents\DNA_"
file_=path_+"\\tests\\records2.txt"

#ToDo : Map Reduce 



def share_records(file_): # storage
    share1=[[[0,0,0,0] for y in range(m)] for x in range(n)]
    share2=[[[0,0,0,0] for y in range(m)] for x in range(n)]
    input_=open(file_,'r')
    x=0
    line=" "
    while (line!=""):
        line=input_.readline().strip()
        if x==0: 
            print line
        y=0
        for char in line: 
            for i in range(4):
                #print x,y,i
                a=acgt[i]
                r= random.randrange(100)
                share1[x][y][i]=r
                if char==a:  
                    share2[x][y][i]=r
                else: 
                    r1=random.randrange(100)
                    while r1==r: 
                        r1=random.randrange(100)
                    share2[x][y][i]=r1
            y+=1
        x+=1
    input_.close()
    return share1, share2  
    
def print_store(share1, share2):     
    for x in range(n): 
        for y in range(m): 
            print share1[x][y]
            print share2[x][y]
            print
        print 
            
def generate_database(n,m,file_):
    output = open(file_,'w')
    print n,m 
    for i in range(n):
        seq="" 
        for j in range(m): 
            seq+=acgt[random.randint(0,3)] 
        output.write(seq+'\n')
        #print seq
    output.close()
    
if __name__ == '__main__':
    print time.time()
    #Parameter m : number of characters in a sequence 
    #Parameter n: number of sequences
    
    #import sys
    #n=int(sys.argv[1])
    #m=int(sys.argv[2])
    n=20000
    m=300
    print time.asctime(time.localtime())

    print "number of records", n 
    print "number of char per record", m 
    # generate database
    start=time.time()
    generate_database(n,m,file_)
    stop=time.time()
    print "database generation %.2f s" % (stop-start)
    # share database
    start=time.time() 
    
    #print_store(share1, share2)
    share1, share2= share_records(file_)
   
    #print_store(share1, share2)
#    save shares to cloud (bucket) (no longer used because Volume is better)
#    start=time.time()
#    cloud.bucket.putf(pickle.dumps(share1),"share1")
#    cloud.bucket.putf(pickle.dumps(share2), "share2")
#    stop=time.time()
#    print "saving shares to cloud time %.2f s" % (stop-start)
    
    # save shares to files 
    share1_file= open (path_+"\\shares\\share1",'w')
    share1_file.write(pickle.dumps(share1))
    share1_file.close()
    share2_file= open (path_+"\\shares\\share2",'w')
    share2_file.write(pickle.dumps(share2))
    share2_file.close()
    stop=time.time()
    print "sharing time %.2f s"% (stop-start)     
    print share1[0][0]
    print share2[0][0]
    
    # create a volume (run only once)
    #cloud.volume.create("shares","shares")
#    print "synchronizing ... please wait ..."
#    start=time.time()
#    cloud.volume.sync(path_+"\\shares\\", "shares:")
#    stop=time.time()
#    print "synchronizing volume shares: time %.2f s" % (stop-start) 
#    # read shares from files (for verification) 
#    share1_file= open ("C:\Users\NASSAR\SkyDrive\Documents\DNA\\shares\\share1",'r')
#    share1=pickle.load(share1_file)
#    print share1[0][0]

