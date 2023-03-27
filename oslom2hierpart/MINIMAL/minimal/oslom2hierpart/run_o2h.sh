#!/bin/bash
oslom2hierpartfolder=./oslom2hierpart
oslom_undir_executable=$oslom2hierpartfolder/oslom_undir
nspfolder=$oslom2hierpartfolder/../../nsps

# the second argument is the destination folder ($2); if it doesnt exist, use the one on parameters 
if [[ $2 != "" ]]; then
	destfolder=$2;
else
	destfolder=$nspfolder
fi

# create destfolder if it doesn't exist
if [[ ! -e $destfolder ]]; then mkdir -p $destfolder; fi

# edgesfile (the argument) 
if [[ $1 != "" ]]; then
	edgesfile=$1
	nspfile=$destfolder/$(echo $(basename $edgesfile) | sed 's/\.edges$/_oslom.nsp/')
	$oslom_undir_executable -f $edgesfile -uw
	python $oslom2hierpartfolder/oslom2modbp.py $edgesfile
	python $oslom2hierpartfolder/modbp2hierpart.py -o $nspfile $edgesfile"_oslom2modbp_files/layer."*
	# replace "> /dev/null &> /dev/null &&" for "\n" (return) in case you want to make OSLOM verbose
else
	echo "Usage: $0 <edges file>"
	exit
fi
