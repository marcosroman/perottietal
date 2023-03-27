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
        i,j=links.pop()
        neighbors[i].append(j)
        neighbors[j].append(i)
    for i in range(N):
        assert neighbors[i]>0

    return N, neighbors

