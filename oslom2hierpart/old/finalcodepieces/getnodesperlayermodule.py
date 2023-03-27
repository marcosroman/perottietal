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

