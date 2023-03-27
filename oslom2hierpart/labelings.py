###############################################################################
### COPYRIGHT NOTICE ##########################################################
# labelings.py - Implementation of a command line parser.
# Copyright (C) 2016-2017 Juan I. Perotti
#
# This program/code is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# 
# See http:#www.gnu.org/licenses/gpl.txt for more details.
# 
###############################################################################
# Author       : Juan Ignacio Perotti ( juanignacio.perotti@imtlucca.it )
# Collaborators: one, personal development.
# Project      : Many---this is a general tool.
# Location     : Institute for Advanced Studies Lucca, Piazza S.Francesco, 19, 
#                55100 Lucca LU, Italy.
# Created      : 2016
# Modified     : -- (cleaned up for public consumption)
# 
###############################################################################

import sys
from collections import defaultdict

class Labelings:
    def __init__(self,Nini=0):
        self.N = Nini-1
        self.d = defaultdict(self._new)
    def _new(self):
        self.N += 1
        return self.N
    def __getitem__(self, i):
        return self.d[i]
    def len(self):
        return len(self.d)
    def keys(self):
        return self.d.keys()

class DoubleLabelings:
    def __init__(self):
        self.N = -1
        self.d = defaultdict(self._new)
        self.d_back = []
    def _new(self):
        self.N += 1
        self.d_back.append(self.save)
        return self.N
    def __getitem__(self, i):
        self.save = i
        return self.d[i]
    def len(self):
        return len(self.d)
    def keys(self):
        return self.d.keys()
    def get_back(self,idx):
        return self.d_back[idx]

class Enumerate:
    """
    >>> enum = Enumerate()
    >>> enum[ 'a' ]
    0
    >>>
    >>> enum
    Enumerate{'a'}
    >>>
    >>> enum[ '5' ]
    1
    >>>
    >>> enum
    Enumerate{'a','5'}
    >>>
    >>> enum[100]
    2
    >>>
    >>> enum
    Enumerate{'a','5',100}
    >>>
    >>> enum[100]
    2
    >>>
    >>> enum['5']
    1
    >>>
    >>> len( enum )
    3
    """
    def __init__(self,_enumerate=None):
        if _enumerate is None:
            self._max_i=-1
            self._l2i=defaultdict(self._next_i)
            self._i2l=[]
        else:
            assert isinstance(_enumerate,Enumerate),'ERROR: assert isinstance(_enumerate,Enumerate)'
            self._max_i=_enumerate.get_max_i()
            self._l2i=_enumerate.copy_l2i()
            self._i2l=_enumerate.copy_i2l()
    def len(self):
        return self._max_i+1
    def __len__(self):
        return self.len()
    def _next_i(self):
        self._i2l.append(self._last_l)
        self._max_i+=1
        return self._max_i
    def __getitem__(self,l):
        self._last_l=l
        return self._l2i[l]
    def __contains__(self,l):
        return l in self._l2i
    def __iter__(self):
        for l in self._l2i:
            yield l
    def i2l(self,i):
        assert i>=0 and i<= self._max_i
        return self._i2l[i]
    def l2i(self,l):
        assert l in self._l2i
        return self._l2i[l]
    def list_l(self):
        return self._l2i.keys()
    def copy(self):
        return Enumerate(_enumerate=self)
    def get_max_i(self):
        return self._max_i
    def copy_l2i(self):
        return self._l2i.copy()
    def copy_i2l(self):
        return list(self._i2l)
    def __repr__( self ):
        s = 'Enumerate{'
        sep = ''
        for i in xrange( len( self ) ):
            l = self.i2l( i )
            if isinstance( l , str ):
                ll = "'" + l + "'"
            else:
                ll = str( l )
            #s += sep + '(' + ll + ',' + str( self[ l ] ) + ')'
            s += sep + ll
            sep = ','
        return s + '}'
        
def enumerate_equivalency(enum_1,enum_2):
    try:
        assert isinstance(enum_1,Enumerate)
        assert isinstance(enum_2,Enumerate)
        assert enum_1.len()==enum_2.len(),'ASSERTION ERROR: enum_1.len() != enum_2.len()'
        assert set(enum_1.list_l())==set(enum_2.list_l()),'ASSERTION ERROR: set(enum_1.list_l()) != set(enum_2.list_l())'
        return True
    except:
        return False
         
def enumerate_print(enum,fhw=None):
    assert isinstance(enum,Enumerate)
    if fhw is None:
        fhw=sys.stdout
    for i in xrange(enum.len()):
        print >>fhw,i,enum.i2l(i)

def enumerate_save(enum,fileout):
    assert isinstance(enum,Enumerate)
    fhw=open(fileout,'w')
    enumerate_print(enum,fhw)
    fhw.close()

def enumerate_read(fh):
    enum=Enumerate()
    while True:
        line=fh.readline()
        if not line: break
        i,l=line.split()
        i=int(i)
        assert i==enum[l]
    return enum

def enumerate_load(filein):
    fh=open(filein)
    enum=enumerate_read(fh)
    fh.close()
    return enum

    
# Test code
#----------    

def enumerate_test_1():
    enum=Enumerate()
    print 'A'
    enum['a']
    enum['b']
    enum['c']
    print 'B'
    enumerate_print(enum)
    print 'C'
    enumerate_save(enum,'enum.dat')
    print 'D'
    enum=enumerate_load('enum.dat')
    print 'E'
    enumerate_print(enum)
    
def stop_test():
    raise KeyboardInterrupt         
    
if __name__=='__main__':

    #glog = None

    if 'test' in sys.argv:

        # Run doctest
        #------------
        
        #np.random.seed( 5 )
        import doctest
        print 'doctesting labelings.py ...'
        doctest.testmod()
        print 'doctest success.'        
    
    else:
    
        pass 
