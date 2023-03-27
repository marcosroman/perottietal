import argparse

def get_arguments():
    parser=argparse.ArgumentParser()

    parser.add_argument('-o','--output', type=str, required=True,help="nested partition output file (.nsp)")
    parser.add_argument('input',nargs='+', help="list of layer files (to take from modbp to nsp format)")
    args=parser.parse_args()

    outputfile=args.output
    list_inputfiles=args.input

    # list_inputfiles is a list of string. there, each string has the format label.index, where index = 1,2,...,n
    # we need to make sure of two things: that there's just one label
    # and that it is ordered, starting from (index) 1 (if not, we can sort it, no problem, but we make sure they are present from 1 to n)
    labels=[]
    indices=[]
    for fname in list_inputfiles:
        splat=fname.split('.')
        indices.append(int(splat[-1]))
        labels.append(".".join(splat[:-1]))
    indices.sort() # sort in place, just in case
    n=len(indices)
    # here we make sure of those two things above (just one label AND all indices present
    if (len(set(labels))==1 and range(1,n+1)==indices):
        list_inputfiles=[]
        filelabel=labels[0]
        for i in range(1,n+1):
            list_inputfiles.append(filelabel+"."+str(i))
        return outputfile,list_inputfiles
    else:
        print "There's a problem with the input (layer files) list",list_inputfiles
        exit()

