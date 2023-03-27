import random

edgesfilename="example.dat"
tpfilename="example.dat_oslo_files/tp1"

# abro archivo que tiene los links... esto voy a usar para generar una lista de vecinos de cada nodo, que va a ser util mas adelante (para definir a que particion corresponde un nodo, en caso de haber overlaps)
f=open(edgesfilename,"r")
lines=f.readlines()
f.close()
while(lines[-1]=='\n'): del(lines[-1]) #saco lineas vacias de abajo
links=[]
for l in lines:
    links.append(map(int,l.split()))
# esto deberia funcionar
N=max([max(l) for l in links])
# lista de vecinos, por nodo (esto voy a usar para calcular intersecciones)
neighbors=[[] for i in range(N)]
for i in range(N):
    for l in links:
        node_label=i+1
        if(node_label in l):
            auxlist=list(l)
            del(auxlist[auxlist.index(node_label)])
            neighbors[i].append(auxlist[0])
    assert neighbors[i]>0

#abrimos archivo con informacion de los modulos
f=open(tpfilename,"r")
lines=f.readlines()
#ignoramos lo que empiece con '#', obtenemos directamente la lista de nodos correspondientes a cada modulo (que, naturalmente, viene ordenada de acuerdo el numero-label del modulo)
filteredlines=lines[1::2]
#listnodespermodule=[] # aca encuentro mi error! me falta agregar el primero modulo, al cual van todos los nodos que no tienen asignados un modulo!
listnodespermodule=[]
for l in filteredlines:
    q=l.split(" ")[:-1]
    s=map(int,q)
    listnodespermodule.append(s) # le agrego la lista correspondiente al modulo determinado por la linea l
listnodespermodule.append([])
# A PARTIR DE AHORA: MEJOR: LOS MODULOS VAN INDEXADOS DESDE EL CERO... DEJO PARA EL FINAL EL MODULO QUE CONTIENE A TODOS LOS QUE NO TIENEN MODULO
# pendiente: verificar y corregir eso

listmodulespernode=[[] for i_node in range(N)]
#for i_module in range(len(listnodespermodule))[:-1]: #omitimos el ultimo, que esta vacio... porque es el que va a contener a todos los nodos que no tienen definido ni siquiera un modulo
for i_module in range(len(listnodespermodule)): 
    for node in listnodespermodule[i_module]:
        i_node=node-1 # porque nuestro conteo es de 0 a N-1
        listmodulespernode[i_node].append(i_module)
        #if len(listmodulespernode[i_node])==0:
        #    listmodulespernode[i_node].append(len(listnodespermodule)-1) # a los que no tienen modulo asignado, les asigno el modulo 0 (asi todos tienen uno)
 
#y aca metemos en la lista los que no tienen modulo... les asignamos el modulo con indice cero
for i_node in range(N):
    #if (len(listnodespermodule)-1) in listmodulespernode[i_node]:
    #    listnodespermodule[0].append(i_node)
    if (listmodulespernode[i_node]==[]):
        listnodespermodule[-1].append(i_node)
        listmodulespernode[i_node].append(len(listnodespermodule)-1)

# ahora es cuando tengo que recorrer la lista
# y para aquellos nodos que tengan mas de un nodo asignado
# hacemos esto de calcular la cantidad de elementos en la interseccion entre sus vecinos y los elementos del nodo en cuestion
# si hay mas de un modulo que arroje el mismo numero, entonces se escoge aleatoriamente
finallistmodulespernode=[]
for i_node in range(N):
    if len(listmodulespernode[i_node])==1:
        finallistmodulespernode.append(listmodulespernode[i_node][0])
    elif len(listmodulespernode[i_node])>1:
        #print 'len(listmodulespernode[',i_node,'=',listmodulespernode[i_node]
        intersecciones=[] # aca vamos a ir guardando las intersecciones, para escoger, para el nodo con indice i_node, el modulo al cual esta mejor conectado (donde tiene mas vecinos)
        for module in listmodulespernode[i_node]:
            i_module=module-1
            #print set(neighbors[i_node])
            size_intersection=len(set(neighbors[i_node]).intersection(set(listnodespermodule[i_module])))
            #print 'size_intersection=',size_intersection
            intersecciones.append(size_intersection)
        max_size_intersection=max(intersecciones) 
        # ahora hacemos la lista de los que tienen ese valor en la interseccion
        #bestmodules_indices=filter(lambda x: intersecciones[]==max_size, listmodulespernode[i_node])
        indices=range(len(listmodulespernode[i_node]))
        bestmodules_indices=filter(lambda x: intersecciones[x]==max_size_intersection, indices)
        if len(bestmodules_indices)==1:
            finallistmodulespernode.append(listmodulespernode[i_node][bestmodules_indices[0]])
        else:
            finallistmodulespernode.append(listmodulespernode[i_node][random.choice(bestmodules_indices)])
    else:
        #print "ERROR, ==0"
        #print 'listmodulespernode[',i_node,']=',listmodulespernode[i_node]
        print "error"
        quit()
    #print i_node,"ok"

for i in range(N):
    print finallistmodulespernode[i]
