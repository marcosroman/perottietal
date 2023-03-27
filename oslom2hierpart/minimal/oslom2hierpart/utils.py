def getNneighbors(edgesfilename):
    # open net (.edges) file, so that we can arrange a list of neighbors per node. this will be useful (when there are overlaps [one node belonging to more that one module], we will decide the module for each node calculating a few intersectiones between sets [read on])
    f=open(edgesfilename,"r") # this could be better (with|try|etc), but it's good enough
    lines=f.readlines()
    f.close()
    while(lines[-1]=='\n'): del(lines[-1]) # remove empty lines, if any
    links=[]
    for l in lines:
        links.append(map(int,l.split()))
    del(lines)
    N=max([max(l) for l in links])+1 # +1 since node label are [0:N]
    #neighbors, per node
    neighbors=[[] for i in range(N)]
    while len(links)>0:
        #print("now doing",links)
        i,j=links.pop()
        neighbors[i].append(j)
        neighbors[j].append(i)
    for i in range(N):
        assert neighbors[i]>0

    return N, neighbors

import os,os.path
import glob

# tomamos como input el archivo en cuestion (asi sabemos donde buscar los tp), el numero de label (usando el orden de modbp) y el numero de modulo
# o sea:
# parameters: edgesfilename, layernumber, modulenumber

def getnodesperlayermodule(edgesfilename,layer_index,modulenumber):
    tpfolder=edgesfilename+"_oslo_files"
    assert os.path.exists(tpfolder)
    number_of_tp_files=len(glob.glob(tpfolder+"/tp*"))
    tpfiles=[tpfolder+'/tp']+[tpfolder+'/tp'+str(n) for n in range(1,number_of_tp_files)]
    tpindex=number_of_tp_files-1-layer_index
    tpfilename=tpfiles[tpindex]

    # open file with module information
    f=open(tpfilename,"r")
    lines=f.readlines()
    # these files contan an even number of lines: for each pair, the first line indicates module number (which is ordered, from 0) and the second one shows the list of nodes... so we need to take the second line and jump every two lines
    filteredlines=lines[1::2]
    #listnodespermodule=[]
    #for l in filteredlines:
    l=filteredlines[modulenumber]
    q=l.split(" ")[:-1]
    s=map(int,q) # s is a list of node labels (integers)
    #listnodespermodule.append(s) 
    return s

