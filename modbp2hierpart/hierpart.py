import sys
from collections import defaultdict
import numpy as np
import random
from operator import itemgetter
import networkx as nx
import itertools
import contextlib
import labelings as lbls
import nxtikz

# Hierarchical Partition
#-----------------------

class NestedPartition:
    """
    >>>
    """
    def __init__( self , elements ):
        if len( elements ) == 0:
            return None
        self._elements = set( elements )
        self._children = set( [] )
        self._ancestor = None

    def __del__( self ):
        self._ancestor = None
        for c in self._children:
            del c
        del self._children
        del self._elements

    def check_consistency( self , assert_not_non_informative_branches = False ):
        """
        >>>
        """
        r = self.root()
        for n in r.DFS():
            assert n.size() > 0 , 'ERROR @ NestedPartition.check_consistency() : the hierarchy contains empty community.' 
            if n.degree() > 0:
                if assert_not_non_informative_branches: 
                    assert n.degree() != 1 , 'ERROR @ NestedPartition.check_consistency() : the hierarchy contains a non-informative branch, i.e. a community with one child community, only.'

                #assert n.elements() == n.children_union() , 'ERROR @ NestedPartition.check_consistency() : the hierarchy contains a community with a set of elements different from the union of the set of elements of its children communities.'
                # Improved version of the previous error message.
                try:
		            assert n.elements() == n.children_union()
                except AssertionError as error:
                    err_message  = "ERROR @ NestedPartition.check_consistency() : the hierarchy contains a community with a set of elements different from the union of the set of elements of its children communities."
                    err_message += "\n n.degree() = " + str( n.degree() )
                    err_message += "\n sorted( [ sorted( c.elements() ) for c in n ]) = " + str( sorted( [ sorted( c.elements() ) for c in n ] ) )
                    err_message += "\n n.elements() = " + str( sorted( n.elements() ) )
                    err_message += "\n n.children_union() = " + str( sorted( n.children_union() ) )
                    error.args += ( err_message , ) # wrap it up in new tuple
                    raise

    def iter_partition( self ):
        """
        >>>
        """
        for c in self:
            yield c.elements()
            
    def iter_elements( self ):
        """
        >>>
        """
        for e in self._elements:
            yield e
            
    def partition( self ):
        """
        >>>
        """
        return [ part for part in self.iter_partition() ]

    def __lshift__( self , nsp ):
        return self.copy()
        
    def copy_node( self ):
        """
        >>>
        """
        return NestedPartition( set( self.elements() ) )
        
    def copy( self ):
        """
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> a1 = k2n[ 'a1' ]
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> cnsp = nsp.copy()
        >>> cnsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> nsp._release_child( a1 )
        >>> nsp
        nsp[[3, 4, 5, 6], [[7], [8, 9]]]
        >>> cnsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        """
        nsp = self.copy_node()
        for c in self:
            st = c.copy()
            nsp._add_child( st )
        return nsp
                          
    def _copy( self , nsp_reference ):
        """
        This special copyier will return the copy, plus a reference to the copy of the node "nsp_reference". The node "nsp_reference" should be a node of the tree of root "self".
        
        >>>
        """
        nsp_to_ret = None
        nsp_copy = self.copy_node()
        #if self._id == nsp_reference._id:
        if self == nsp_reference:        
            nsp_to_ret = nsp_copy
        for c in self:
            st , _nsp = c._copy( nsp_reference )
            if _nsp is not None:
                nsp_to_ret = _nsp
            nsp_copy._add_child( st )
        return nsp_copy , nsp_to_ret
                             
    def _shrink( self ):
        """This function removes are nodes in the tree that are the only son of corresponding parent nodes. The children of each only son take his place. This function is required because, after a merge, or a split, some nodes may end having one and only one child.
        
        >>>
        """
        # Shrink its children.
        for cnsp in self:
            cnsp._shrink()
        # Shrink locally.
        if self.is_leaf():
            return
        if self.degree() == 1:
            child = self._pop_child()
            assert self.degree() == 0
            child_degree = child.degree()
            ch_ch = child._pop_child()
            while ch_ch is not None:
                self._add_child( ch_ch )
                ch_ch = child._pop_child()                
            assert self.degree() == child_degree                             
                             
    def _split_node( self , splitter_set ):
        """
        >>>
        """
        assert isinstance( splitter_set , set )
        e1 = self.elements() - splitter_set
        e2 = self.elements() - e1
        assert len( e1 ) + len( e2 ) == self.size()
        if len( e1 ) == 0:
            nsp1 = None
        else:
            nsp1 = NestedPartition( e1 )
        if len( e2 ) == 0:
            nsp2 = None
        else:
            nsp2 = NestedPartition( e2 )
        return nsp1 , nsp2
            
    def _recursive_split( self , splitter_set ):
        """
        >>>
        """
        nsp1 , nsp2 = self._split_node( splitter_set )
        if nsp1 is None and nsp2 is None:
            assert False
        if self.is_leaf():
            return nsp1 , nsp2
        else:
            for ch in self:
                ch_nsp1 , ch_nsp2 = ch._recursive_split( splitter_set )
                if ch_nsp1 is not None:
                    assert nsp1 is not None
                    nsp1._add_child( ch_nsp1 )
                if ch_nsp2 is not None:
                    assert nsp2 is not None            
                    nsp2._add_child( ch_nsp2 )                    
            return nsp1 , nsp2                 
        
    def split_branch( self , splitter_set ):
        """
        The branch defined by self is split into two. The branches resulting from the split are returned.
        
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> a1 = k2n[ 'a1' ]
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> a1
        ..nsp[[0, 1], [2]]
        >>>
        >>> a1.split_branch( set( [ 1 , 3 , 8 ] ) )
        (nsp[[0], [2]], nsp[1])
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>>
        >>> nsp1 , nsp2 = nsp.split_branch( set( [ 1 , 3 , 8 ] ) )
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> nsp1
        nsp[[4, 5, 6], [[0], [2]], [[7], [9]]]
        >>> nsp2
        nsp[[1], [3], [8]]
        """    
        nsp1 , nsp2 = self._recursive_split( splitter_set )
        if nsp1 is not None:
            nsp1._shrink()
        if nsp2 is not None:
            nsp2._shrink()
        return nsp1 , nsp2
        
    def split_here( self , splitter_set ):
        """
        The tree to which self belong is split at self. More specifically, the tree is modified. The branch spawned by self is deleted and replaced by two new branches, those resulting by the split of that spawned by self.
        
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> a1 = k2n[ 'a1' ]
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> nsp.to_tikz( filename = 'doctest__split_here_1.tex' )
        >>> 
        >>> a1
        ..nsp[[0, 1], [2]]
        >>>
        >>> a1.split_here( set( [ 1 , 3 , 8 ] ) )
        >>> nsp
        nsp[[1], [3, 4, 5, 6], [[0], [2]], [[7], [8, 9]]]
        >>> nsp.to_tikz( filename = 'doctest__split_here_2.tex' )        
        """
        assert not self.is_root()
        ansp = self.ancestor()
        ansp._release_child( self )
        nsp1 , nsp2 = self.split_branch( splitter_set )
        ansp._add_child( nsp1 )
        ansp._add_child( nsp2 )
        del self        
        
    def extend_here( self , splitter_set ):
        assert self.is_leaf()
        nsp = self.copy_node()
        nsp1 , nsp2 = self.split_branch( splitter_set )
        self._add_child( nsp1 )
        self._add_child( nsp2 )        
        
    def merge_branchs( self , nsp1 , nsp2 ):
        """
        Take to branches, nsp1 and nsp2, and creates a new branch by merging them.
        
        >>> k2n = toy()
        >>> sorted( k2n )
        ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'b4', 'root']
        >>> nsp = k2n[ 'root' ]
        >>> a1 = k2n[ 'a1' ]
        >>> a2 = k2n[ 'a2' ]        
        >>>
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> a1
        ..nsp[[0, 1], [2]]
        >>> a2
        ..nsp[3, 4, 5, 6]
        >>>
        >>> mnsp = nsp.merge_branchs( a1 , a2 )
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> mnsp
        nsp[[0, 1], [2], [3, 4, 5, 6]]
        """
        mnsp = NestedPartition( nsp1.elements().union( nsp2.elements() ) )
        if nsp1.is_leaf():
            mnsp._add_child( nsp1.copy() )
        else:
            for c in nsp1:
                mnsp._add_child( c.copy() )
        if nsp2.is_leaf():
            mnsp._add_child( nsp2.copy() )        
        else:
            for c in nsp2:
                mnsp._add_child( c.copy() )
        mnsp._shrink()
        return mnsp
        
    def merge_siblings_here( self , nsp1 , nsp2 ):
        """
        Merges the siblings nsp1 and nsp2 of self, by modifying the tree to which self belongs. nsp1 and nsp2 are deleted in the process, and replaced by the branch that resulted from the merge.
        
        >>> k2n = toy()
        >>> sorted( k2n )
        ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'b4', 'root']
        >>> nsp = k2n[ 'root' ]
        >>> a1 = k2n[ 'a1' ]
        >>> a2 = k2n[ 'a2' ]
        >>>
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> nsp.to_tikz( filename = 'doctest__merge_siblings_here_1.tex' )
        >>> a1
        ..nsp[[0, 1], [2]]
        >>> a2
        ..nsp[3, 4, 5, 6]
        >>>
        >>> nsp.merge_siblings_here( a1 , a2 )
        >>> nsp
        nsp[[[0, 1], [2], [3, 4, 5, 6]], [[7], [8, 9]]]
        >>> nsp.to_tikz( filename = 'doctest__merge_siblings_here_2.tex' )
        """
        assert nsp1.ancestor() == self
        assert nsp2.ancestor() == self
        self._release_child( nsp1 )
        self._release_child( nsp2 )        
        self._add_child( self.merge_branchs( nsp1 , nsp2 ) )
      
    def replace( self , nsp ):
        """Replace self with nsp.
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> a1 = k2n[ 'a1' ]
        >>> a1
        ..nsp[[0, 1], [2]]
        >>> new_a1 = NestedPartition( [0,1,2] )
        >>> a1.replace( new_a1 )
        >>> nsp
        nsp[[0, 1, 2], [3, 4, 5, 6], [[7], [8, 9]]]
        """
        assert self.elements() == nsp.elements()
        assert not self.is_root()
        assert nsp.ancestor() is None
        a = self.ancestor()
        a._release_child( self )
        a._add_child( nsp )
     
    def size( self ):
        return len( self._elements )
        
    def degree( self ):
        return len( self._children )
        
    def is_brother( self , nsp ):
        """
        >>>
        """
        assert isinstance( nsp , NestedPartition )
        self != nsp
        if not ( self.is_root() or nsp.is_root() ):
            return False
        a = self.ancestor()
        return a.is_child( nsp )
        
    def is_child( self , nsp ):
        """
        >>>
        """
        assert isinstance( nsp , NestedPartition )
        return nsp in self._children
        
    def is_root( self ):
        """
        >>>
        """
        return self._ancestor is None
        
    def is_leaf( self ):    
        """
        >>>
        """
        if self.degree() == 0:
            return True
        return False
        
#    def __eq__( self , nsp ):
#        """
#        >>>
#        CHECK...
#        """
#        assert isinstance( nsp , NestedPartition )
#        if self._id == nsp._id:
#            return True
#        if self.size() != nsp.size():
#            return False
#        if self._elements != nsp._elements:
#            return False
#        H1 = self.node_entropy()
#        H2 = nsp.node_entropy()        
#        jH = self.node_joint_entropy( nsp )
#        if not ( _feq( H1 , H2 ) and _feq( H1 + H2 , 2.0 * jH ) ):
#            return False
#        if not _feq( self.subtree_mutual_information( nsp ) , self.subtree_entropy() ):
#            return False
#        return True
        
    def equivalent( self , nsp ):
        """
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> cnsp = nsp.copy()
        >>> nsp == nsp
        True
        >>> cnsp == nsp
        False
        >>> nsp.equivalent( cnsp )
        True
        """
        assert isinstance( nsp , NestedPartition )    
        if self == nsp:
            return True
        if self.size() != nsp.size():
            return False
        if self._elements != nsp._elements:
            return False
        if abs( self.normalized_hierarchical_mutual_information( nsp , calc_NMI = 'arithmetic' ) - 1. ) > 0.0000001:
            return False
        return True
 
#    def __ne__( self , nsp ):
#        return not self.__eq__( nsp )
        
    def elements( self ):
        return self._elements
        
    def create_children( self , partition , allow_one_child = False ):
        """
        >>>
        """
        assert len( partition ) > 0
        if ( not allow_one_child ) and len( partition ) == 1:
            return self
        if isinstance( partition , dict ):
            assert set([]).union( *partition.values() ) == self.elements()
            for key , part in partition.items():
                nsp = NestedPartition( part )
                partition[ key ] = nsp                
                self._add_child( nsp )
            return partition
        else:
            for part in partition:
                self._add_child( NestedPartition( part ) )
                
    def _add_child( self , nsp ):
        """
        This is an internal function for the incorporation of child communities. It allows the incorporation of one child community at a time. The function "create_children" is the one that should be used by the end user, since it asserts the correct creation of the children communities of a community. Namely, "create_children" asserts that the union of elements of the newly created children equals the set of elements of the parent community "self".

        >>>
        """
        assert isinstance( nsp , NestedPartition )
        assert nsp.elements() <= self._elements
        for c in self:
            assert len( c._elements & nsp.elements() ) == 0 , 'ERROR @ NestedPartition._add_child(...) : Attempting to incorporate a child which share elements with another already incorporated child.'
        nsp._ancestor = self
        self._children.add( nsp )
        
    def _pop_child( self ):
        """
        >>>
        """
        if self.degree() == 0:
            return None
        c = self.random_child()
        self._release_child( c )
        return c
        
    def iter_pop_children( self ):
        """
        >>>
        """
        while self.degree() > 0:
            c = self.random_child()
            self._release_child( c )
            yield c
        
    def _release_child( self , nsp ):
        """
        This does not deleted nsp but it just detach it from self.
        
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> a1 = k2n[ 'a1' ]
        >>> a3 = k2n[ 'a3' ]        
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> nsp._release_child( a3 )
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]]]
        >>> a3
        nsp[[7], [8, 9]]
        >>> a1
        ..nsp[[0, 1], [2]]
        """
        assert isinstance( nsp , NestedPartition )
        assert self.is_child( nsp )
        self._children.remove( nsp )
        nsp._ancestor = None
        
    def random_child( self ):
        """
        >>>
        """
        return random.choice( list( self._children ) )
                
    def random_node( self ):
        """
        >>>
        """
        return random.choice( [ nsp for nsp in self.root().DFS() ] )
              
    def ancestor( self ):
        return self._ancestor
        
    def __iter__( self ):
        """
        >>>
        """
        for c in self._children:
            yield c            
            
    def iter_children( self , sort = False ):
        """
        This is like __iter__() but allows a sorted iteration.
        
        >>>
        """
        if sort:
            for c in sorted( self._children ):
                yield c
        else:
            for c in self._children:
                yield c  
            
    def children_union( self , run_checks = True ):
        """
        run_checks <bool> , default = False : if True, it is checked that the returned union is equal to the set of elements of "self".

        Returns <set> : union of the elements of the children of "self".

        >>>
        """
        union_u = []
        for u in self:
            union_u += u.elements()
        union_u = set( union_u )

        # CHECK
        if run_checks and self.degree() > 0:
            try:
                assert union_u == self.elements()
            except AssertionError as error:
                err_message  = "ERROR @ children_union( self )."
                err_message += "\n v.degree = " + str( self.degree() )
                err_message += "\n union_u = " + str( sorted( union_u ) )
                err_message += "\n v = " + str( sorted( self.elements() ) )
                for u_th , u in enumerate( self ):
                    err_message += "\n u-th = " + str( u_th ) + ", u.elements() = " + str( sorted( u.elements() ) )
                error.args += ( err_message , ) # wrap it up in new tuple
            #raise BaseException

        return union_u
                            
    def node_entropy( self ):
        """
            H(u|v) = sum_{u in C_v} - p(u|v) ln p(u|v)
        
        Here, C_v is the set of children u of v and p(u|v) is the probability that the chosen element is in u given that it is in v.
        
        >>> k2n_toy1 = old_toy_1()
        >>> k2n_toy2 = old_toy_2()
        """
        if self.is_leaf():
            return 0.
        H = 0.
        deno = float( self.size() )
        sum_nume = 0.
        for c in self:
            nume = float( c.size() )
            frac = nume / deno
            H -= _xlnx( frac )
            sum_nume += nume                        
        assert _feq( sum_nume , deno )
        return H
        
    def node_conditional_entropy( self , nsp ):
        """
            H( u1 int. v2 | v1 int. v2 ) = sum_{ u1 in C_v1 } - p( u1 int. v2 | v1 int. v2 ) ln p( u1 int. v2 | v1 int. v2 )
            
        Notice, the summation runs over u1 only---there is no u2.
        
        >>> k2n_toy1 = old_toy_1()
        >>> k2n_toy2 = old_toy_2()        
        """
        if self.is_leaf():
            return 0.
        cH = 0.
        v1 = self.elements()
        v2 = nsp.elements()
        v1Nv2 = v1 & v2
        deno = float( len( v1Nv2 ) )
        if deno == 0.:
            return 0.
        sum_nume = 0.
        for c in self:
            u1 = c.elements()
            u1Nv2 = u1 & v2
            nume = float( len( u1Nv2 ) )
            frac = nume / deno
            cH -= _xlnx( frac )
            sum_nume += nume                        
        assert _feq( sum_nume , deno )
        return cH
    
    def node_conditional_joint_entropy( self , nsp ):
        """
            H( u1 int. u2 | v1 int. v2 ) = sum_{ u1 in C_v1 , u2 in C_v2 } - p( u1 int. u2 | v1 int. v2 ) ln p( u1 int. u2 | v1 int. v2 )
        
        Notice, now the sum runs over u1 and u2.
        
        >>> k2n_toy1 = old_toy_1()
        >>> k2n_toy2 = old_toy_2()        
        """
        cjH = 0.
        if self.is_leaf() or nsp.is_leaf():
            return 0.
        v1 = self.elements()
        v2 = nsp.elements()
        v1Nv2 = v1 & v2
        deno = float( len( v1Nv2 ) )
        if deno == 0.:
            return 0.
        sum_nume = 0.
        for c1 in self:
            u1 = c1.elements()
            for c2 in nsp:
                u2 = c2.elements()
                u1Nu2 = u1 & u2
                nume = float( len( u1Nu2 ) )
                frac = nume / deno
                cjH -= _xlnx( frac )
                sum_nume += nume
        assert _feq( sum_nume , deno )
        return cjH
        
    def node_conditional_mutual_information( self , nsp ):
        """
        MI( u1 ; u2 | v1 int. v2 ) = H( u1 int. v2 | v1 int v2 ) + H( u2 int. v1 | v1 int v2 ) - H( u1 int. u2 | v1 int v2 )
        
        >>> k2n_toy1 = old_toy_1()
        >>> k2n_toy2 = old_toy_2()        
        """
        assert isinstance( nsp , NestedPartition )
        return self.node_conditional_entropy( nsp ) + nsp.node_conditional_entropy( self ) - self.node_conditional_joint_entropy( nsp )
        
    #def subtree_mutual_information( self , nsp ):
    #    """
    #    TODO...
    #    
    #    >>> k2n_toy1 = old_toy_1()
    #    >>> k2n_toy2 = old_toy_2()
    #    >>> root1 = k2n_toy1[ 'root' ]
    #    >>> root2 = k2n_toy2[ 'root' ]
    #    >>> root1
    #    nsp[[['a'], ['b', 'c']], ['d', 'e', 'f']]
    #    >>> root2
    #    nsp[['a'], ['b', 'c'], ['d', 'e', 'f']]
    #    >>>
    #    >>> "%.7f" % root1.subtree_mutual_information( root1 )
    #    '1.3296613'
    #    >>> "%.7f" % root2.subtree_mutual_information( root2 )
    #    '1.0114043'
    #    >>> "%.7f" % root1.subtree_mutual_information( root2 )
    #    '0.6931472'
    #    >>> "%.7f" % root2.subtree_mutual_information( root1 )
    #    '0.6931472'
    #    >>>
    #    >>> 'CHECK...'
    #    >>> 'NOTICE; the values returned by the two last tests do not agree up to full precision. Is it because numerical round? Or is it a bug? Or is it that the SMI is non symmetric? We can check this once we can play with larger hierarchical partitions.'
    #    """
    #    assert isinstance( nsp , NestedPartition )
    #    SMI = self.node_conditional_mutual_information( nsp )
    #    for c1 in self:
    #        for c2 in nsp:
    #            SMI += c1.subtree_mutual_information( c2 )
    #    return SMI
        
    def hierarchical_mutual_information( self , nsp , run_checks = True ):
        """
        HMI( T1 ; T2 ) = ...
        
        CHECKS
        ------
         - Compared with the OLD_hierpart.py --- YES       
        
        >>> k2n_toy1 = old_toy_1()
        >>> k2n_toy2 = old_toy_2()
        >>> root1 = k2n_toy1[ 'root' ]
        >>> root2 = k2n_toy2[ 'root' ]
        >>> root1
        nsp[[['a'], ['b', 'c']], ['d', 'e', 'f']]
        >>> root2
        nsp[['a'], ['b', 'c'], ['d', 'e', 'f']]
        >>>
        >>> # The following numbers are checked with the numbers in the paper and the numbers in ___hierpart.py
        >>> "%.7f" % root1.hierarchical_mutual_information( root1 )
        '1.0114043'
        >>> "%.7f" % root2.hierarchical_mutual_information( root2 )
        '1.0114043'
        >>> "%.7f" % root1.hierarchical_mutual_information( root2 )
        '0.6931472'
        >>> "%.7f" % root2.hierarchical_mutual_information( root1 )
        '0.6931472'
        """
        assert isinstance( nsp , NestedPartition )

        if run_checks:
            self.check_consistency()
            nsp.check_consistency()

        if self.is_leaf( ) or nsp.is_leaf():
            return 0.
        v1 = self.elements()
        v2 = nsp.elements()
        v1Nv2 = v1 & v2
        deno = float( len( v1Nv2 ) )
        if deno == 0.:
            return 0.
        cjH = 0.
        crH = 0.
        sum_nume = 0.
        for c1 in self:
            for c2 in nsp:
                u1 = c1.elements()
                u2 = c2.elements()
                u1Nu2 = u1 & u2
                nume = float( len( u1Nu2 ) )
                frac = nume / deno
                cjH -= _xlnx( frac )
                crH += frac * c1.hierarchical_mutual_information( c2 )
                sum_nume += nume
        try:
            assert _feq( sum_nume , deno )
        except AssertionError as error:
            err_message  = "ERROR @ hierarchical_mutual_information( self , nsp ): assert _feq( sum_nume , deno ) fails for sum_nume = " + str( sum_nume ) + " and deno = " + str( deno ) + "."
            err_message += "\n v1 = " + str( sorted( v1 ) )
            err_message += "\n v2 = " + str( sorted( v2 ) )
            list_u1 = sorted( [ c1.elements() for c1 in self ] )
            list_u2 = sorted( [ c2.elements() for c2 in nsp ] )
            err_message += "\n [ u1 ] = " + str( list_u1 )
            err_message += "\n [ u2 ] = " + str( list_u2 )
            union_u1 = set( [] )
            union_u2 = set( [] )
            for u1 in list_u1:
                for e1 in u1:
                    union_u1.add( e1 )
            for u2 in list_u2:
                for e2 in u2:
                    union_u2.add( e2 )
            err_message += "\n U u1 = " + str( union_u1 )
            err_message += "\n U u2 = " + str( union_u2 )
            error.args += ( err_message , ) # wrap it up in new tuple
            raise                        
        cH1 = self.node_conditional_entropy( nsp )
        cH2 = nsp.node_conditional_entropy( self )
        return cH1 + cH2 - cjH + crH
        
    #def subtree_entropy( self ):
    #    """
    #    TODO...
    #    
    #    >>> k2n_toy1 = old_toy_1()
    #    >>> k2n_toy2 = old_toy_2()        
    #    """
    #    return self.subtree_mutual_information( self )
        
    def hierarchical_entropy( self , run_checks = True ):
        """
        TODO...
        
        >>> k2n_toy1 = old_toy_1()
        >>> k2n_toy2 = old_toy_2()        
        """
        return self.hierarchical_mutual_information( self , run_checks = run_checks )
        
    #def normalized_subtree_mutual_information( self , nsp , calc_NMI = 'arithmetic' ):
    #    """
    #    TODO...
    #    
    #    >>> k2n_toy1 = old_toy_1()
    #    >>> k2n_toy2 = old_toy_2()        
    #    """
    #    if calc_NMI == 'arithmetic':
    #        calc_NMI = _arithmetic_NMI
    #    elif calc_NMI == 'geometric':
    #        calc_NMI = _geometric_NMI
    #    elif calc_NMI == 'max':
    #        calc_NMI = _max_NMI        
    #    assert isinstance( nps , NestedPartition )
    #    SMI1  = self.subtree_entropy()
    #    SMI2  = nsp.subtree_entropy()        
    #    SMI12 = self.subtree_mutual_information( nsp )
    #    return calc_NMI( SMI1 , SMI2 , SMI12 )

    def normalized_hierarchical_mutual_information( self , nsp , calc_NMI = 'arithmetic' , run_checks = True ):
        """
        NHMI( T1 ; T2 ) = ...
        
        CHECKS
        ------
         - Compared with the OLD_hierpart.py --- YES
        
        >>> k2n_toy1 = old_toy_1()
        >>> k2n_toy2 = old_toy_2()        
        """
        if calc_NMI == 'arithmetic':
            calc_NMI = _arithmetic_NMI
        elif calc_NMI == 'geometric':
            calc_NMI = _geometric_NMI
        elif calc_NMI == 'max':
            calc_NMI = _max_NMI
        else:
            assert False , 'ERROR @ NestPartitionm.normalized_hierarchical_mutual_information(...) : "calc_NMI" specifies unknown normalization method.'
        assert isinstance( nsp , NestedPartition )
        HMI1  = self.hierarchical_entropy( run_checks = run_checks )
        HMI2  = nsp.hierarchical_entropy( run_checks = run_checks )
        HMI12 = self.hierarchical_mutual_information( nsp , run_checks = run_checks )
        return calc_NMI( HMI1 , HMI2 , HMI12 )

    #def subtree_variation_information( self , nsp ):
    #    """
    #    TODO...
    #    
    #    >>> k2n_toy1 = old_toy_1()
    #    >>> k2n_toy2 = old_toy_2()        
    #    """
    #    assert isinstance( nsp , NestedPartition )
    #    return self.subtree_entropy() + nsp.subtree_entropy() - 2.0 * self.subtree_mutual_information( nsp )

    #def hierarchical_variation_information( self , nsp ):
    #    """
    #    TODO...
    #    
    #    >>> k2n_toy1 = old_toy_1()
    #    >>> k2n_toy2 = old_toy_2()        
    #    """
    #    assert isinstance( nsp , NestedPartition )
    #    return self.hierarchical_entropy() + nsp.hierarchical_entropy() - 2.0 * self.hierarchical_mutual_information( nsp )

    def root_mutual_information( self , nsp , run_checks = True ):
        """
        Computes the Mutual Information (MI) between the layer-1 partition of T1 and the layer-1 partition of T2.

        root_MI( T1 ; T2 ) = ...
        
        >>> k2n_toy1 = toy()
        >>> k2n_toy2 = toy2()
        >>> k2n_toy3 = toy3()
        >>> root1 = k2n_toy1[ 'root' ]
        >>> root2 = k2n_toy2[ 'root' ]
        >>> root3 = k2n_toy3[ 'root' ]
        >>> root1
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> root2
        nsp[[3, 4, 5, 6], [[0], [1, 2]], [[7], [8, 9]]]
        >>> root3
        nsp[[2, 4, 5, 6], [[0, 1], [3]], [[7], [8, 9]]]
        >>>
        >>> # The following numbers are checked with the numbers in the paper and the numbers in ___hierpart.py
        >>> "%.7f" % root1.root_mutual_information( root1 )
        '1.0889000'
        >>> "%.7f" % root1.root_mutual_information( root2 )
        '1.0889000'
        >>> "%.7f" % root2.root_mutual_information( root2 )
        '1.0889000'
        >>> "%.7f" % root1.root_mutual_information( root3 )
        '0.6730117'
        >>> "%.7f" % root2.root_mutual_information( root3 )
        '0.6730117'
        """
        assert isinstance( nsp , NestedPartition )
        assert( self.is_root() ) , 'ERROR @ root_mutual_information : assert( self.is_root() )'
        assert( nsp.is_root() ) , 'ERROR @ root_mutual_information : assert( nsp.is_root() )'
        if run_checks:
            self.check_consistency()
            nsp.check_consistency()
        S1  = self.node_entropy()
        S2  = nsp.node_entropy()
        S12 = self.node_conditional_joint_entropy( nsp )
        return S1 + S2 - S12

    def root_normalized_mutual_information( self , nsp , calc_NMI = 'arithmetic' , run_checks = True ):
        """
        Computes the Normalized Mutual Information (NMI) between the layer-1 partition of T1 and the layer-1 partition of T2.

        root_NMI( T1 ; T2 ) = ...
        
        >>> k2n_toy1 = toy()
        >>> k2n_toy2 = toy2()
        >>> k2n_toy3 = toy3()
        >>> root1 = k2n_toy1[ 'root' ]
        >>> root2 = k2n_toy2[ 'root' ]
        >>> root3 = k2n_toy3[ 'root' ]
        >>> root1
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> root2
        nsp[[3, 4, 5, 6], [[0], [1, 2]], [[7], [8, 9]]]
        >>> root3
        nsp[[2, 4, 5, 6], [[0, 1], [3]], [[7], [8, 9]]]
        >>>
        >>> # The following numbers are checked with the numbers in the paper and the numbers in ___hierpart.py
        >>> "%.7f" % root1.root_normalized_mutual_information( root1 )
        '1.0000000'
        >>> "%.7f" % root2.root_normalized_mutual_information( root2 )
        '1.0000000'
        >>> "%.7f" % root1.root_normalized_mutual_information( root3 )
        '0.6180656'
        """
        assert isinstance( nsp , NestedPartition )
        assert( self.is_root() ) , 'ERROR @ root_normalized_mutual_information : assert( self.is_root() )'
        assert( nsp.is_root() ) , 'ERROR @ root_normalized_mutual_information : assert( nsp.is_root() )'
        if run_checks:
            self.check_consistency()
            nsp.check_consistency()
        if calc_NMI == 'arithmetic':
            calc_NMI = _arithmetic_NMI
        elif calc_NMI == 'geometric':
            calc_NMI = _geometric_NMI
        elif calc_NMI == 'max':
            calc_NMI = _max_NMI
        else:
            assert False , 'ERROR @ NestPartitionm.root_normalized_mutual_information : "calc_NMI" specifies unknown normalization method.'
        S1  = self.node_entropy()
        S2  = nsp.node_entropy()
        S12 = self.node_conditional_joint_entropy( nsp )
        MI = S1 + S2 - S12 
        return calc_NMI( S1 , S2 , MI )

    def iter_layer_mutual_information( self , nsp , calc_NMI = 'arithmetic' , run_checks = True , verbose = False ):
        """
        This function iterates over the layers of the "self" hierarchy and the "nsp" hierarchy and returns the corresponding layer_mutual_information.
 
        NOTICE: Different branches of a hierarchy may have different depths. Hence, this function iterates until the max depth "L" between both hierarchies and, if during the process a branch has reached its maximum depth at some layer "l" then, the partitions at the subsequent layers "l+1,l+2,...,L" inherits the corresponding "local-structure" of the branch. Namely, if the branch ends in some node "n" then, "virtual" descendants "n_{l+1},n_{l+2},...,n_{L-1}" of one child only are created for the subsequent layers, all of them being equal to "n" and, also, the last descendant "n_L" is also set equal to "n".

        nsp <NestedPartitio> : ...

        calc_NMI <str='arithmetic'> : one of 'arithmetic', 'geometric' or 'max' are the different options that can be specified to indicate the normalization form that is going to be used to compute the NMI at each of the layers.

        run_checks <bool=True> : if True checks are run. Otherwise, checks are avoided. This can be used to speed-up the computations.

        Yields
        ------
        a tuple ( layer_number , MI , NMI ) where:
        layer_number <int> : is the layer,
        MI <float> : is the Mutual Information for the layer and
        NMI <float> : is the Normalized Mutual Information for the layer.
 
        >>> k2n_toy4 = toy4()
        >>> k2n_toy5 = toy5()
        >>> k2n_toy6 = toy6()
        >>> root4 = k2n_toy4[ 'root' ]
        >>> root5 = k2n_toy5[ 'root' ]
        >>> root6 = k2n_toy6[ 'root' ]
        >>> root4
        nsp[[0, 1], [[5, 6], [[2, 3], [4]]], [[7], [8, 9]]]
        >>> root5
        nsp[[0, 1], [[5, 6], [[2], [3, 4]]], [[7, 8], [9]]]
        >>> root6
        nsp[[0, 1], [[2, 3], [[4], [5, 6]]], [[7], [8, 9]]]
        >>>
        >>> for l , mi , nmi in root4.iter_layer_mutual_information( root4 ):
        ...     print l , mi , nmi
        0 0.0 0.0
        1 1.02965301406 1.0
        2 1.55711309806 1.0
        3 1.74806734855 1.0
        >>>
        >>> for l , mi , nmi in root4.iter_layer_mutual_information( root5 ):
        ...     print l , mi , nmi
        0 0.0 0.0
        1 1.02965301406 1.0
        2 1.41848366195 0.910970220285
        3 1.47080847632 0.841391195565
        >>>
        >>> for l , mi , nmi in root4.iter_layer_mutual_information( root6 ):
        ...     print l , mi , nmi
        0 0.0 0.0
        1 1.02965301406 1.0
        2 1.36615884757 0.877366486271
        3 1.74806734855 1.0
        >>>
        >>> k2n_toy1 = toy()
        >>> k2n_toy2 = toy2()
        >>> k2n_toy3 = toy3()
        >>> root1 = k2n_toy1[ 'root' ]
        >>> root2 = k2n_toy2[ 'root' ]
        >>> root3 = k2n_toy3[ 'root' ]
        >>>
        >>> for l , mi , nmi in root1.iter_layer_mutual_information( root2 ):
        ...     print l , mi , nmi
        0 0.0 0.0
        1 1.08889997535 1.0
        2 1.33217904021 0.905746099276
        >>>
        >>> for l , mi , nmi in root1.iter_layer_mutual_information( root3 ):
        ...     print l , mi , nmi
        0 0.0 0.0
        1 0.673011667009 0.618065646292
        2 1.24587441847 0.847067744395
        """
        assert isinstance( nsp , NestedPartition )
        assert( self.is_root() ) , 'ERROR @ root_normalized_mutual_information : assert( self.is_root() )'
        assert( nsp.is_root() ) , 'ERROR @ root_normalized_mutual_information : assert( nsp.is_root() )'

        if calc_NMI == 'arithmetic':
            calc_NMI = _arithmetic_NMI
        elif calc_NMI == 'geometric':
            calc_NMI = _geometric_NMI
        elif calc_NMI == 'max':
            calc_NMI = _max_NMI
        else:
            assert False , 'ERROR @ NestPartitionm.normalized_hierarchical_mutual_information(...) : "calc_NMI" specifies unknown normalization method.'

        def _layer_entropy( list_of_lists_partition ):
            N = 0
            suma = 0
            for l in list_of_lists_partition:
                n = len( l )
                N += n
                suma += _nlnn( n )
            return _ln( N ) - suma / float( N )

        def _layer_joint_entropy( list_of_lists_partition_1 , list_of_lists_partition_2 ):
            N = 0
            suma = 0
            for part_1 in list_of_lists_partition_1:
                for part_2 in list_of_lists_partition_2:
                    n = len( set( part_1 ) & set( part_2 ) )
                    N += n
                    suma += _nlnn( n )
            return _ln( N ) - suma / float( N )

        def _next_layer( nsp_pool ):
            next_nsp_pool = []
            list_of_lists_partition = []
            _continue = False
            for nsp in nsp_pool:
                if nsp.is_leaf():
                    list_of_lists_partition.append( nsp.elements() )
                    next_nsp_pool.append( nsp )
                else:
                    for cnsp in nsp:
                        list_of_lists_partition.append( cnsp.elements() )
                        next_nsp_pool.append( cnsp )
                        _continue = True
            return _continue , next_nsp_pool , list_of_lists_partition

        if run_checks:
            self.check_consistency()
            nsp.check_consistency()

        if verbose:
            print '# self =' , self
            print '# nsp =' , nsp

        nsp_pool_self = [ self.root() ]
        nsp_pool_nsp  = [ nsp.root() ]
        continue_self = True
        continue_nsp  = True
        layer = 0
        yield 0 , 0. , 0.

        while True:
     
            layer += 1

            if continue_self:
                continue_self , nsp_pool_self , child_layer_list_of_lists_partition_self = _next_layer( nsp_pool_self )
                H_self  = _layer_entropy( child_layer_list_of_lists_partition_self )

            if continue_nsp:
                continue_nsp  , nsp_pool_nsp  , child_layer_list_of_lists_partition_nsp  = _next_layer( nsp_pool_nsp )
                H_nsp   = _layer_entropy( child_layer_list_of_lists_partition_nsp )

            if ( continue_self or continue_nsp ):

                H_joint = _layer_joint_entropy( child_layer_list_of_lists_partition_self , child_layer_list_of_lists_partition_nsp )
                MI      = H_self + H_nsp - H_joint 

                layer_MI = MI
                layer_NMI = calc_NMI( H_self , H_nsp , MI )

                if verbose:
                    print '###############################################################'
                    print 'layer =', layer
                    print 'nsp_pool_self =' , nsp_pool_self
                    print 'nsp_pool_nsp =' , nsp_pool_nsp
                    print 'layer_partition_self =' , child_layer_list_of_lists_partition_self 
                    print 'layer_partition_nsp  =' , child_layer_list_of_lists_partition_nsp

                yield layer , layer_MI , layer_NMI

            else:
                break

    def DFS( self , sort = False ):
        """
        >>> nsp = toy()[ 'root' ]
        >>> for l in sorted( [  str( node ) for node in nsp.DFS( sort = True ) ] ):
        ...     print l
        ..nsp[0, 1]
        ..nsp[2]
        ..nsp[3, 4, 5, 6]
        ..nsp[7]
        ..nsp[8, 9]
        ..nsp[[0, 1], [2]]
        ..nsp[[7], [8, 9]]
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        """
        if sort:
            for c in sorted( self , cmp = _nsp_cmp ):
                for cc in c.DFS():
                    yield cc
        else:
            for c in self:
                for cc in c.DFS():
                    yield cc
        yield self
        
    def root( self ):
        """
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> a1 = k2n[ 'a1' ]
        >>> nsp
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        >>> a1
        ..nsp[[0, 1], [2]]
        >>> a1.root()        
        nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
        """
        n = self
        while True:
            if n.is_root():
                return n
            n = n.ancestor()
            
    def newick( self , sort = True ):
        """
        >>>
        """
        if self.is_leaf():
            if sort:
                return sorted( self.elements() )
            return list( self.elements() )
        else:
            if sort:
                return sorted( [ c.newick() for c in self ] )
            return list( [ c.newick() for c in self ] )            
            
    def __repr__( self ):
        """
        >>>
        """
        if self._ancestor is None:
            return 'nsp' + str( self.newick() )
        return '..nsp' + str( self.newick() )
        
    def __str__( self ):
        return self.__repr__()
        
    def enumerate_children( self ):
        """
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> for i , c in nsp.enumerate_children():
        ...     print i , c
        0 ..nsp[[0, 1], [2]]
        1 ..nsp[3, 4, 5, 6]
        2 ..nsp[[7], [8, 9]]
        """
        for i , c in enumerate( sorted( self._children , cmp = _nsp_cmp ) ):
            yield i , c
        
    def iter_leaves_path( self ):
        """
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> for path_elem in nsp.iter_leaves_path():
        ...     print path_elem
        [0, 0, set([0, 1])]
        [0, 1, set([2])]
        [1, set([3, 4, 5, 6])]
        [2, 0, set([7])]
        [2, 1, set([8, 9])]
        """
        if self.is_leaf():
            yield [ self.elements() ]
        else:       
            for i , c in self.enumerate_children():
                for path_elem in c.iter_leaves_path():
                    yield [ i ] + path_elem
        
    def save( self , filename = None ):
        """
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> nsp.save( 'toy.nsp' )
        """
        if not self.is_root( ):
            self.root().save( filename )        
        else:
            #with open( filename , 'w' ) as fhw:
            with smart_streamout( filename ) as fhw:
                for path_elem in self.iter_leaves_path():
                    print >>fhw , ':'.join( [ str( p ) for p in path_elem[:-1] ] ) + ' #%$ ' + ','.join( [ '"' + str(e) + '"' for e in path_elem[-1] ] )
       
    def iter_dendrogram_layout( self , sort = True , _leaves_xpos = None , run_checks = True ):
        """
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> for x , y , _nsp , edge in nsp.iter_dendrogram_layout():
        ...    print x , y , _nsp , edge
        0.0 0.0 ..nsp[0, 1] (..nsp[[0, 1], [2]], ..nsp[0, 1])
        1.0 0.0 ..nsp[2] (..nsp[[0, 1], [2]], ..nsp[2])
        0.5 1.0 ..nsp[[0, 1], [2]] (nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]], ..nsp[[0, 1], [2]])
        2.0 0.0 ..nsp[8, 9] (..nsp[[7], [8, 9]], ..nsp[8, 9])
        3.0 0.0 ..nsp[7] (..nsp[[7], [8, 9]], ..nsp[7])
        2.5 1.0 ..nsp[[7], [8, 9]] (nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]], ..nsp[[7], [8, 9]])
        4.0 0.0 ..nsp[3, 4, 5, 6] (nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]], ..nsp[3, 4, 5, 6])
        1.85714285714 2.0 nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]] None
        """
        if _leaves_xpos is None and run_checks:
            self.check_consistency()
            _leaves_xpos = lbls.Enumerate()
        if self.is_root():
            edge = None
        else:
            edge = ( self.ancestor() , self )
        if self.is_leaf():
            x = float( _leaves_xpos[ self ] )            
            yield x , 0. , self , edge
        else:
            list_x = []
            list_y = []
            for c in self.iter_children( sort = True ):
                for _x , _y , _nsp , _edge in c.iter_dendrogram_layout( sort = sort , _leaves_xpos = _leaves_xpos ):
                    yield _x , _y , _nsp , _edge
                    list_x.append( _x )    
                    list_y.append( _y )
            yield avrg( list_x ) , max( list_y ) + 1. , self , edge
        
    def to_tikz( self             ,
                 filename       = None , 
                 node_sizes     = None ,
                 node_colors    = None ,
                 node_shapes    = None ,
                 node_labels    = None ,                 
                 edge_widths    = None ,                 
                 edge_colors    = None ,
                 scale_x        = 1.0  ,
                 scale_y        = 1.0  , 
                 legends        = ''   ,
                 seed           = 5    ,
                 sort           = True ):
        """
        >>> k2n = toy()
        >>> nsp = k2n[ 'root' ]
        >>> nsp.to_tikz( filename = 'doctest_toyNestedPartitiom.tex' )
        """
        node_styles = nxtikz.NodeStyles( seed = seed )
        
        node_positions = {}
        node_indexes   = {}
        edges          = []
        for i , ( x , y , nsp , edge ) in enumerate( self.iter_dendrogram_layout( sort = True ) ):
            node_positions[ nsp ] = ( x * scale_x , y * scale_y )
            if edge is not None:
                edges.append( edge )
            node_indexes[ nsp ] = i

        if node_sizes is None:
            node_sizes = { nsp : '4mm' for nsp in node_positions.keys() }
        else:
            node_sizes = dict( node_sizes )
        
        if node_colors is None:
            node_colors = {}
            for nsp in node_positions.keys():
                if nsp.is_leaf():
                     color = 'white' # node_styles.fill_color( 0 )
                else:
                     color = node_styles.fill_color( node_indexes[ nsp ] )
                node_colors[ nsp ] = color
        else:
            node_colors = dict( node_colors )
            
        if node_shapes is None:
            node_shapes = {}
            for nsp in node_positions.keys():
                if nsp.is_leaf():
                    shape = 'circle' # node_styles.shape( 0 )          
                else:
                    shape = node_styles.shape( node_indexes[ nsp ] )
                node_shapes[ nsp ] = shape
        else:
            node_shapes = dict( node_shapes )
                        
        if node_labels is None:
            node_labels = {}
            for nsp in node_positions.keys():
                if nsp.is_leaf():
                    node_labels[ nsp ] = '{' + ','.join( str( e ) for e in sorted( nsp.elements() ) ) + '}'
                else:
                    node_labels[ nsp ] = ''
        else:
            node_labels = dict( node_labels )                        

        if edge_colors is None:
            edge_colors = { e : 'black!100' for e in edges }
        else:
            edge_colors = dict( edge_colors )      

        LEGENDS=''
        if legends is not None:
            if legends == '':
#                legends += '$\\rm{AIC}(Z|G) = ' + str( self.AIC() ) + '$,\n'
#                legends += '$\ln\mathcal{L}(Z|G) = ' + str( self.ln_L() ) + '$,\n'
#                legends += '$C = ' + str( self.num_internal_nodes() ) + '$\n'
                legends = []
            elif isinstance( legends , str ):
                legends = [ ( 2. , -2. ,  legends ) ]
            for x , y , legend in legends:
                LEGENDS += '\\node[draw,text width=] at (' + '{:10.4f}'.format( x ) + ',' + '{:10.4f}'.format( y ) + ') {LLL};\n'.replace( 'LLL' , str( legend ) )

        # Draw the nodes.
        NODES=''
        for nsp in sorted( node_positions.keys() ):
             x , y = node_positions[ nsp ]
             if nsp.is_leaf():
                 label_position = 'below'    
             else:
                 label_position = 'above right'
             NODES += '\\node (' + str( node_indexes[ nsp ]) + ') at (' + '{:10.4f}'.format( x ) + ',' + '{:10.4f}'.format( y ) + ') [shape=' + node_shapes[ nsp ]+ ',fill=' + node_colors[ nsp ] + ',inner sep=1pt,minimum size=' + node_sizes[ nsp ]+ ',draw,label=' + label_position + ':' + node_labels[ nsp ]+ '] {};\n'

        # Draw the edges.
        def bend( nsp_d , nsp_c , node_positions , reverse = False ):
            x_d = node_positions[ nsp_d ][0]
            x_c = node_positions[ nsp_c ][0]
            if reverse:
                x_d , x_c = x_c , x_d
            if x_d < x_c:
                return 'bend left,'
            if x_d > x_c:
                return 'bend right,'
            return ''
        EDGES=''
        for e in edges:
            nsp_d , nsp_c = e
            EDGES += '\\draw (' + str( node_indexes[ nsp_d ] ) + ') edge[' + bend( nsp_d , nsp_c , node_positions ) + 'color=' + edge_colors[ e ]  + '] (' + str( node_indexes[ nsp_c ] ) + '.center);\n'

        TEX = _tikz_dendrogram_doc.replace( '%LEGENDS' , LEGENDS ).replace( '%NODES' , NODES ).replace( '%EDGES' , EDGES )

        # Output...
        if filename is None:
            return TEX
        else:
            with open( filename , 'w' ) as fhw:
                fhw.write( TEX )         
        
_tikz_dendrogram_doc = """%##############################################################################
%## COPYRIGHT NOTICE ##########################################################
% Produced by dendrogram.py .
% Copyright (C) 2016-2017 Juan I. Perotti
%
% This program/code is free software; you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation; either version 2 of the License, or
% (at your option) any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program; if not, write to the Free Software
% Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
% 
% See http:#www.gnu.org/licenses/gpl.txt for more details.
% 
%##############################################################################
% Author       : Juan Ignacio Perotti ( juanignacio.perotti@imtlucca.it )
% Collaborators: Claudio Juan Tessone, Aaron Clausset and Guido Caldarelli
% Project      : Generalized Hierarchical Random Graphs
% Location     : Institute for Advanced Studies Lucca, Piazza S.Francesco, 19, 
%                55100 Lucca LU, Italy.
% Created      : 1 March 2016
% Modified     : -- (cleaned up for public consumption)
% 
%##############################################################################

% The standalone documentclas fit the page of the pdf to the size of the 
% content.
\documentclass{standalone}

\usepackage[obeyspaces]{url}
\usepackage{tikz}
\usetikzlibrary{shapes}

% If we like to control the size of the page...
%\usepackage[paperwidth=17cm,paperheight=21cm,hmargin=0cm,vmargin=0cm]{geometry}

% To impede the edges overlap with the nodes.
\pgfdeclarelayer{bg}    % declare background layer
\pgfsetlayers{bg,main}  % set the order of the layers (main is the standard layer)

% Define a more convenient macro without @ in its name
\def\gprgb#1#2#3{rgb,255:red,#1;green,#2;blue,#3}

\\begin{document}

\\begin{tikzpicture}

% Put legends if any...
%LEGENDS

% Draw the nodes...
%NODES

% Draw the edges...
\\begin{pgfonlayer}{bg}
%EDGES
\end{pgfonlayer}

\end{tikzpicture}

\end{document}
"""        
        
def _nsp_cmp( nsp1 , nsp2 ):
    for e1 , e2 in zip( sorted( nsp1._elements ) , sorted( nsp2._elements ) ):
        if e1 < e2:
            return -1
        elif e1 > e2:
            return 1
    return 0
        
def load_NestedPartition( filename , nodes_as_int = False , run_checks = True ):
    """
    The .nsp file-format is how a Hierarchical Partition is saved into a file. An example of how a .nsp file looks like is:

    0:0 #%$ "0"
    0:1 #%$ "1","2","3"
    1:0 #%$ "4","5"
    1:1:0 #%$ "6"
    1:1:1 #%$ "7","8","9"

    which corresponds to the tree whose root contains the elemtns "0","1",...,"9" and whose hierarchy is formed by the tree:

    root ---> 0 ---> 0 : "0"
        |      \---> 1 : "1","2","3"
        |
        \---> 1 ---> 0 : "4","5"
               \---> 1 ---> 0 : "6"
                      \---> 1 : "7","8","9"

    filename <str> : the path and filename of the .nsp file that should be loaded.

    node_as_int <bool=False> : If true, all nodes names (i.e. the names of the elements inside the communities of the hierarchical partition) are considered to be integers instead of strings. This option is provided because, for some network packages, nodes are not represented as integers---which is usually computationally faster---but as strings. For safety reasons, the default is set to False.

    check <bool=False> : If True, it checks for consistency.

    >>> nsp = load_NestedPartition( 'toy.nsp' , nodes_as_int = True )
    >>> nsp
    nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
    >>> k2n = toy()
    >>> nsp = k2n[ 'root' ]
    >>> nsp
    nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
    """

    def iter_subpaths( path ):
        """
        This function takes a path, e.g.:

            1:3:2
 
        and yields all possible subpaths, i.e.

            1
            1:3
            1:3:2
 
        """
        _path = path.split(':')
        for i in xrange( len( _path ) ):
            yield ':'.join( _path[:i+1] )

    # Below "sp" stands for "sub-path" and "csp" stands for "children sub-path" and "psp" for "parent sub-path".
    elements = []
    sp_2_elements    = defaultdict( lambda: set([]) )
    sp_2_children_sp = defaultdict( lambda: set([]) )
    with open( filename , 'r' ) as fh:
        for line in fh.readlines():
            path , elements = line.split( ' #%$ ' )
            path = '0:' + path # The root node is added to the path as the prefix "0:". It is omitted in the .nsp file since it is redundant because it is always the same. However, here, in order to allow for the trivial partition of one part with all eleents, we add it explicitly.
            if nodes_as_int:
                elements = set([ int( e ) for e in elements[1:-2].split( '","' ) ])
            else:
                elements = set([ e for e in elements[1:-2].split( '","' ) ])
            # Here the path is iterated over its sub-paths and the sub-paths are correspondingly populated by the network nodes and "linked" as some being the parents/children of the others.
            psp = None
            for sp in iter_subpaths( path ):
                for e in elements:
                    sp_2_elements[ sp ].add( e )
                if psp is not None:
                    sp_2_children_sp[ psp ].add( sp )
                else:
                    pass
                psp = sp

    # Now the one-to-one relation between sub-paths and NestedPartitions is stablished.
    sp_2_nsp = {}
    for sp , elements in sp_2_elements.items():
        sp_2_nsp[ sp ] = NestedPartition( elements )

    # Now, the NestedPartitions are properly linked in order to form the Hierarchical Partition.
    for sp in sp_2_children_sp.keys():
        nsp  = sp_2_nsp[ sp ]
        for csp in sp_2_children_sp[ sp ]:
            cnsp = sp_2_nsp[ csp ]
            nsp._add_child( cnsp )

    root = sp_2_nsp[ '0' ]
    if run_checks:
        root.check_consistency()

    return root

def generate_random_hierarchy( num_elements , num_iterations = None , seed = None ):
    """This function generates a random hierarchy. 

    For the developers. Please, uncoment the docstring below to test the function's code. The docstring's test is currently commented since it is not fully deterministic but vary depending on the machine due to differences in the inbuilt random number generator."""
    #>>> nsp = generate_random_hierarchy( 10 , seed = 5 )
    #>>> nsp
    #nsp[[[0, 1, 8], [3, 6]], [[2, 4, 7], [5, 9]]]
    #"""
    #nsp[[1, 8, 9], [[[0, 4, 7], [3]], [[2, 5], [6]]]]
    def generate_random_splitter_set( elements ):
        p = random.random()
        splitter_set = set( [] )
        for e in elements:
            if random.random() < p:
                splitter_set.add( e )
        return splitter_set
    if seed is not None:
        random.seed( seed )
    if num_iterations is None:
        num_iterations = num_elements
    num_elements = int( num_elements )
    assert num_elements > 0
    elements = range( num_elements )
    nsp = NestedPartition( elements )
    for i in xrange( num_iterations ):
        _nsp = nsp.random_node()
        _splitter_set = generate_random_splitter_set( _nsp.elements() )
        if _nsp.size() < 2 or len( _splitter_set ) == 0 or len( _splitter_set ) == _nsp.size():
            continue
        if _nsp.is_leaf():
            _nsp.extend_here( _splitter_set )
        else:
            if _nsp.is_root():
                continue
            _nsp.split_here( _splitter_set )                
    return nsp

################################################################################       
# Tools
################################################################################

# http://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_streamout( filename = None ):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout
    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()       

def toy():
    """
    >>> k2n = toy()
    >>> k2n[ 'root' ]
    nsp[[3, 4, 5, 6], [[0, 1], [2]], [[7], [8, 9]]]
    """
    partition = {}
    partition[ 'root' ] = NestedPartition( range( 10 ) )
    partition.update( partition[ 'root' ].create_children( { 'a1' : [0,1,2] , 'a2' : [3,4,5,6] , 'a3' : [7,8,9] } ) )
    partition.update( partition[ 'a1' ].create_children( { 'b1' : [0,1] , 'b2' : [2] } ) )
    partition.update( partition[ 'a3' ].create_children( { 'b3' : [7]   , 'b4' : [8,9] } ) )
#    partition.update( partition[ 'b1' ].create_children( { 'c1' : [0]   , 'c2' : [1] } ) )
#    partition.update( partition[ 'b4' ].create_children( { 'c3' : [8]   , 'c4' : [9] } ) )
    return partition

def toy2():
    """
    >>> k2n = toy2()
    >>> k2n[ 'root' ]
    nsp[[3, 4, 5, 6], [[0], [1, 2]], [[7], [8, 9]]]
    """
    partition = {}
    partition[ 'root' ] = NestedPartition( range( 10 ) )
    partition.update( partition[ 'root' ].create_children( { 'a1' : [0,1,2] , 'a2' : [3,4,5,6] , 'a3' : [7,8,9] } ) )
    partition.update( partition[ 'a1' ].create_children( { 'b1' : [0] , 'b2' : [1,2] } ) )
    partition.update( partition[ 'a3' ].create_children( { 'b3' : [7]   , 'b4' : [8,9] } ) )
#    partition.update( partition[ 'b1' ].create_children( { 'c1' : [0]   , 'c2' : [1] } ) )
#    partition.update( partition[ 'b4' ].create_children( { 'c3' : [8]   , 'c4' : [9] } ) )
    return partition

def toy3():
    """
    >>> k2n = toy3()
    >>> k2n[ 'root' ]
    nsp[[2, 4, 5, 6], [[0, 1], [3]], [[7], [8, 9]]]
    """
    partition = {}
    partition[ 'root' ] = NestedPartition( range( 10 ) )
    partition.update( partition[ 'root' ].create_children( { 'a1' : [0,1,3] , 'a2' : [2,4,5,6] , 'a3' : [7,8,9] } ) )
    partition.update( partition[ 'a1' ].create_children( { 'b1' : [0,1] , 'b2' : [3] } ) )
    partition.update( partition[ 'a3' ].create_children( { 'b3' : [7]   , 'b4' : [8,9] } ) )
#    partition.update( partition[ 'b1' ].create_children( { 'c1' : [0]   , 'c2' : [1] } ) )
#    partition.update( partition[ 'b4' ].create_children( { 'c3' : [8]   , 'c4' : [9] } ) )
    return partition

def toy4():
    """
    >>> k2n = toy4()
    >>> k2n[ 'root' ]
    nsp[[0, 1], [[5, 6], [[2, 3], [4]]], [[7], [8, 9]]]
    """
    partition = {}
    partition[ 'root' ] = NestedPartition( range( 10 ) )
    partition.update( partition[ 'root' ].create_children( { 'a1' : [0,1] , 'a2' : [2,3,4,5,6] , 'a3' : [7,8,9] } ) )
    partition.update( partition[ 'a2' ].create_children( { 'b1' : [2,3,4] , 'b2' : [5,6] } ) )
    partition.update( partition[ 'a3' ].create_children( { 'b3' : [7]   , 'b4' : [8,9] } ) )
    partition.update( partition[ 'b1' ].create_children( { 'c1' : [2,3]   , 'c2' : [4] } ) )
    return partition

def toy5():
    """
    >>> k2n = toy5()
    >>> k2n[ 'root' ]
    nsp[[0, 1], [[5, 6], [[2], [3, 4]]], [[7, 8], [9]]]
    """
    partition = {}
    partition[ 'root' ] = NestedPartition( range( 10 ) )
    partition.update( partition[ 'root' ].create_children( { 'a1' : [0,1] , 'a2' : [2,3,4,5,6] , 'a3' : [7,8,9] } ) )
    partition.update( partition[ 'a2' ].create_children( { 'b1' : [2,3,4] , 'b2' : [5,6] } ) )
    partition.update( partition[ 'a3' ].create_children( { 'b3' : [7,8]   , 'b4' : [9] } ) )
    partition.update( partition[ 'b1' ].create_children( { 'c1' : [2]   , 'c2' : [3,4] } ) )
    return partition

def toy6():
    """
    >>> k2n = toy6()
    >>> k2n[ 'root' ]
    nsp[[0, 1], [[2, 3], [[4], [5, 6]]], [[7], [8, 9]]]
    """
    partition = {}
    partition[ 'root' ] = NestedPartition( range( 10 ) )
    partition.update( partition[ 'root' ].create_children( { 'a1' : [0,1] , 'a2' : [2,3,4,5,6] , 'a3' : [7,8,9] } ) )
    partition.update( partition[ 'a2' ].create_children( { 'b1' : [2,3] , 'b2' : [4,5,6] } ) )
    partition.update( partition[ 'a3' ].create_children( { 'b3' : [7]   , 'b4' : [8,9] } ) )
    partition.update( partition[ 'b2' ].create_children( { 'c1' : [4]   , 'c2' : [5,6] } ) )
    return partition
    
def old_toy_1():    
    """
    >>> k2n_toy1 = old_toy_1()
    >>> k2n_toy1[ 'root' ]
    nsp[[['a'], ['b', 'c']], ['d', 'e', 'f']]
    """
    partition = {}
    partition[ 'root' ] = NestedPartition( [ 'a' , 'b' , 'c' , 'd' , 'e' , 'f' ] )
    partition.update( partition[ 'root' ].create_children( { 'abc' : [ 'a' , 'b' , 'c' ] , 'def' : [ 'd' , 'e', 'f' ] } ) )
    partition.update( partition[ 'abc' ].create_children( { 'a' : [ 'a' ] , 'bc' : [ 'b' , 'c' ] } ) )
    return partition
    
def old_toy_2():    
    """
    >>> k2n_toy2 = old_toy_2()
    >>> k2n_toy2[ 'root' ]
    nsp[['a'], ['b', 'c'], ['d', 'e', 'f']]
    """
    partition = {}
    partition[ 'root' ] = NestedPartition( [ 'a' , 'b' , 'c' , 'd' , 'e' , 'f' ] )
    partition.update( partition[ 'root' ].create_children( { 'a' : [ 'a' ] , 'bc' : [ 'b' , 'c' ] , 'def' : [ 'd' , 'e', 'f' ] } ) )
    return partition
    
def _ln( x ):
    return np.log( x )

def _xlnx( x ):
    assert x >= 0. and x <= 1.
    if x == 0.:
        return 0.
    return x * np.log( x )
    
def _nlnn( n ):
    assert n >= 0.
    if n == 0.:
        return 0.
    return n * np.log( n )

def _feq( x , y , eps = 1.e-10 ):
    if abs( x - y ) < eps:
        return True
    return False
        
def avrg( a ):
    return sum( a ) / float( len( a ) )
        
_newid = itertools.count().next
           
def _merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result           
                
def _arithmetic_NMI( H1 , H2 , H12 ):
    """
    >>>
    """
    suma = H1 + H2
    if suma == 0.:
        return 0.
    return ( 2.0 * H12 ) / suma
                
def _geometric_NMI( H1 , H2 , H12 ):
    """
    >>>
    """
    prod = H1 * H2
    if prod == 0.:
        return 0.
    return H12 / np.sqrt( prod )

def _max_NMI( H1 , H2 , H12 ):
    """
    >>>
    """
    _max = max( H1 , H2 )
    if _max == 0.:
        return 0.
    return H12 / _max

###############################################################################                
# Test code
###############################################################################

def stop_test():
    raise KeyboardInterrupt         
    
if __name__=='__main__':

    import glog
    import clp

    glog.glog = sys.stdout

    clo = clp.CommandLineParser( sys.argv[1:] )

    if clo.letstry( 'test' ):

        glog.glog = open( 'glog.dat' , 'w' )

        seed = 10
        np.random.seed( seed )
        random.seed( seed )

        # Run doctest
        #------------
        import doctest
        print 'doctesting hierpart.py ...'
        doctest.testmod()
        print 'doctest success.'        
    
    else:

        pass    
