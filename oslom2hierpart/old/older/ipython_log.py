# IPython log file

f=open("../example.dat","r")
lines=f.readlines()
lines
lines[-1]
while(lines[-1]=='\n'): del(lines[-1])
lines[-1]
lines[0].split()
lines[2].split()
set(lines[2].split())
int(set(lines[2].split()))
map(int,lines[2].split())
links=[]
for l in lines:
    links.append(map(int,l.split()))
    
links
N=1000
neighbors=[[] for i in range(N)]
for i in range(N):
    for l in links:
        node_label=i+1
        if(node_label in l):
            auxlist=list(l)
            del(auxlist[auxlist.index(node_label)])
            neighbors[i].append(auxlist[0])
            
neighbors
get_ipython().magic(u'logstart ')
get_ipython().system(u'vi ipython_log.py')
get_ipython().system(u'cp ipython_log.py edges2neighborlist.py')
get_ipython().magic(u'ls ')
exit()
