import hierpart as hp
import argutils

output_fname,list_filenames=argutils.get_arguments()

# we start from the start 
index_thislayer=0
# and go through all layers
while (index_thislayer < len(list_filenames)):
    # (layer zero, a.k.a. root, is not among the input files)
    filename_nextlayer=list_filenames[index_thislayer]
    with open(filename_nextlayer,'r') as f:
        list_nextlayer=map(int,f.readlines())

    # if we are just getting started, we want to retrieve N (network size),
    # define the nodes list (range(N)), root layer (list of zeros of size N)
    # and create the root partition
    if (index_thislayer == 0):
        N=len(list_nextlayer)
        #print "N=",N
        list_nodes=range(N)
        list_thislayer=[0 for i in range(N)]
        partition={(0,0):hp.NestedPartition(list_nodes)}
    # if not, list_thislayer should be already defined (see below)

    # so now we create dictionaries for 2 consecutive layers (this and next)
    #   whose keys are a tuple: (layerindex,partitionlabel)
    #   and whose associated values are the nodes contained in these partitions
    # for this, we'll be needing the labels:
    thislayer_labels=set(list_thislayer)
    nextlayer_labels=set(list_nextlayer)
    # and some filter functions (they return the list of nodes with a given label)
    filter_thislayer_bylabel = lambda x: filter(lambda y: list_thislayer[y]==x,list_nodes)
    filter_nextlayer_bylabel = lambda x: filter(lambda y: list_nextlayer[y]==x,list_nodes)
    # now we're ready for the dictionaries for the 2 consecutive layers!
    dict_thislayer=dict([((index_thislayer,label),filter_thislayer_bylabel(label)) for label in thislayer_labels])
    dict_nextlayer=dict([((index_thislayer+1,label),filter_nextlayer_bylabel(label)) for label in nextlayer_labels])

    # alright. we'll be doing some more filtering. this time, for each partition (label) in 'thislayer'
    # we want to present it to it's children (in 'nextlayer'). so, we'll be filtering dictionaries 
    for label,elements in dict_thislayer.iteritems():
        filtered_dictionary=dict(filter(lambda x: set(elements).issuperset(x[1]),dict_nextlayer.iteritems()))
        #if (len(filtered_dictionary) > 1): # we don't let them have just one child!
        #print label,elements
        partition.update(partition[label].create_children(filtered_dictionary))

    index_thislayer+=1
    list_thislayer=list_nextlayer

#partition[(0,0)]._shrink()
partition[(0,0)].save(output_fname)


'''
# in case you want to know how it looks like, it's a good idea to not show all node labels
nodes_labels = { cnsp : '' for cnsp in partition[(0,0)].DFS() }
partition[(0,0)].to_tikz('partitiontotikz',node_labels=nodes_labels)
'''
