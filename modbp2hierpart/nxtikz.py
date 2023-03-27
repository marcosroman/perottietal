###############################################################################
### COPYRIGHT NOTICE ##########################################################
# nxtikz.py : To plot networkx Graphs using tikz.
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
# Collaborators: None. Personal Development.
# Project      : Many---this is a general tool.
# Location     : Institute for Advanced Studies Lucca, Piazza S.Francesco, 19, 
#                55100 Lucca LU, Italy.
# Created      : 2016
# Modified     : -- (cleaned up for public consumption)
# 
###############################################################################

import sys
import random
import numpy as np
import networkx as nx
import tikz
#import SSD
import clp
import glog
import os

################################################################################
# Styles
################################################################################            

class NodeStyles:
    """
    >>> print 'TODO'
    """
    def __init__( self , seed = None ):
        self._r = random.Random()
        if seed is not None:
            self._r.seed( seed )    
        self._mixer_fill_color   = ( 1. + self._r.random() ) * 2.71828182846
        self._mixer_border_color = ( 1. + self._r.random() ) * 1.41421356237
        self._mixer_shape        = ( 1. + self._r.random() ) * 3.14159265359
        self._color_jet = tikz.ColorJet( seed = seed )
        self._shape_jet = [ 'circle' , 'diamond' , 'regular polygon, regular polygon sides=3' , 'regular polygon, regular polygon sides=4', 'regular polygon, regular polygon sides=5' , 'star, star points=5' ]

    def num_distinct_styles( self ):
        return self.num_distinct_colors() * self.num_distinct_colors() * self.num_distinct_shapes()    

    def num_distinct_colors( self ):
        return self._color_jet.num_colors()

    def num_distinct_shapes( self ):
        return len( self._shape_jet )

    def fill_color( self , i ):
        i = int( i * self._mixer_fill_color ) % self.num_distinct_colors()
        return self._color_jet.color( i )

    def border_color( self , i ):
        i = int( i * self._mixer_border_color ) % self.num_distinct_colors()    
        return self._color_jet.color( i )

    def shape( self , i ):
        i = int( i * self._mixer_shape ) % self.num_distinct_shapes()
        return self._shape_jet[ i ]

################################################################################
# Plotting tools
################################################################################            

def plot_nx_graph( g                              ,
                   filename                = None ,
                   node_position           = None ,
                   node_shape              = None ,
                   node_size               = None ,
                   node_fill_color         = None ,
                   node_border_color       = None ,
                   node_border_width       = None ,
                   node_label              = None ,                   
                   edge_width              = None ,
                   edge_color              = None ,
                   edge_type               = None ,
                   scale_x                 = 10.0 ,
                   scale_y                 = 10.0 ,
                   legends                 = None ,
                   extra_tikz_code_at_head = None ):
    """
    >>> g = load_pairs_into_nxGraph()
    >>> plot_nx_graph( g , 'doctest_nxtikz_karateclub.tex' )
    """
    assert isinstance( g , nx.Graph )
    if node_position is None:
        node_position = nx.spring_layout( g )
    if node_shape is None:
        node_shape = { node : 'circle' for node in g.nodes_iter() }
    if node_size is None:
        node_size = { node : '4mm' for node in g.nodes_iter() }
    if node_fill_color is None:
        node_fill_color = { node : 'red' for node in g.nodes_iter() }
    if node_border_color is None:
        node_border_color = { node : 'black' for node in g.nodes_iter() }
    if node_border_width is None:
        node_border_width = { node : '2pt' for node in g.nodes_iter() }
    if node_label is None:
        node_label = { node : str( node ) for node in g.nodes_iter() }
    if edge_width is None:
        edge_width = { edge : '1pt' for edge in g.edges_iter() }
    if edge_color is None:
        edge_color = { edge : 'gray' for edge in g.edges_iter() }
    if edge_type is None:
        edge_type = { edge : '--' for edge in g.edges_iter() }        
    HEAD=''
    if extra_tikz_code_at_head is not None:
        HEAD = extra_tikz_code_at_head
    LEGENDS=''
    if legends is not None:
        if not isinstance( legends , list ):
            legends = [ ( 2. , -2. ,  legends ) ]
        for x , y , legend in legends:
            LEGENDS += '\\node[draw,text width=4cm] at (' + '{:10.4f}'.format( x ) + ',' + '{:10.4f}'.format( y ) + ') {LLL};\n'.replace( 'LLL' , str( legend ) )
    # Draw the nodes.
    NODES=''
    for n in g.nodes_iter():
        x , y = node_position[ n ]
        x *= scale_x
        y *= scale_y
        NODES += '\\node (' + str( n ) + ') at (' + "{:10.4f}".format( x ) + ',' + "{:10.4f}".format( y ) + ') [draw=' + node_border_color[ n ] +  ',shape=' + node_shape[ n ] + ',fill=' + node_fill_color[ n ]  + ',inner sep=1pt,minimum size=' + node_size[ n ] + ',draw,label=below left:' + node_label[ n ] + '] {};\n'
    # Draw the edges.
    EDGES=''
    for e in g.edges_iter():
        n1 , n2 = e
        EDGES += '\\draw [color=' + edge_color[ e ] + ',line width=' + edge_width[ e ] + ']  (' + node_label[ n1 ] + ') ' + edge_type[ e ] + ' (' + node_label[ n2 ] + '.center);\n'
    # Generate the full .tex
    TEX = tikz_nxtikz_doc.replace( '%LEGENDS' , LEGENDS ).replace( '%NODES' , NODES ).replace( '%EDGES' , EDGES ).replace( '%HEAD' , HEAD )
    # Output...
    if filename is None:
        return TEX
    else:
        with open( filename , 'w' ) as fhw:
            fhw.write( TEX )
        return None
            
################################################################################
# Layouts...
################################################################################

#def gravity_spring_core_layout( G , weight = None , node_sizes = None , spring_constants = None ):
#    """
#    >>>
#    """
#    pass
#    
#class gravity_spring_core_layout_SSD( SSD.AdaptiveStochasticSteepestDescent ):
#    """
#    >>>
#    """
#    def __init__( self , G ):
#        assert isinstance( G , nx.Graph )
#        self._G = G
#        self._x = np.zeros( self.num_nodes() )
#        self._y = np.zeros( self.num_nodes() )        
#        self._E = 0.
#    
#    def num_nodes( self ):
#        self._G.number_of_vertices()
#        
#    def compute_E( self ):
#        """
#        THEORY
#        ------
#        
#            E = sum_ij - r_{ij}^{-2} + K * w_ij * ( r0_ij - r_ij )
#            
#        where
#        
#            r0_ij = max( max_j( z_j ) , z_i )
#            
#        where
#        
#            z_i = size of node i.
#            
#        and
#        
#            w_ij = connection strength between node i and j
#        """
#        pass
#    
#    def N( self ):
#        return 2 * self._G.number_of_vertices()
#        
#    def E( self ):
#        pass
#        
#    def best_E( self ):
#        return self._best_E
#    
#    def update_best_E( self ):
#        self._best_E = self.E()
#    
#    def save_best_x( self ):
#        pass
#            
#    def x_i( self , i ):
#        pass
#        
#    def update_x_i( self , x_i , i ):
#        pass
#        
#    def grad_i_E( self , i ):
#        pass
#     
#    def eps( self ):
#        pass
#     
#    def sqrt_avrg_x_squared( self ):
#        """
#        Should return ( 1/N sum_i x_i^2 )^{1/2}
#        >>>
#        """
#        pass

#    def best_solution( self ):
#        pass            
            
################################################################################
# Extra tools
################################################################################            
       
def load_pairs_into_nxGraph( filein = None , asints = False ):
    """
    >>>
    """
    g = nx.Graph()    
    if filein is None:
        for edge in karate_pairs.split('\n'):
            n1 , n2 = edge.split()
            n1 , n2 = int( n1 ) , int( n2 )
            g.add_edge( n1 , n2 )
    else:
        with open( filein , 'r' ) as fh:
            for edge in fh.readlines():
                n1 , n2 = edge.split()
                if asints:
                    n1 , n2 = int( n1 ) , int( n2 )
                g.add_edge( n1 , n2 )
    return g            
    
tikz_nxtikz_doc = """%##############################################################################
%## COPYRIGHT NOTICE ##########################################################
% Produced by nxtikz.py .
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

% To include extra packages or things like that.
%HEAD

% To impede the edges overlap with the nodes.
\pgfdeclarelayer{bg}    % declare background layer
\pgfsetlayers{bg,main}  % set the order of the layers (main is the standard layer)

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
            
################################################################################
# Karate Club
################################################################################
# This is the famous Karate Club network 
# [ An Information Flow Model for Conflict and Fission in Small Groups
# Wayne W. Zachary
# Journal of Anthropological Research
# Vol. 33, No. 4 (Winter, 1977), pp. 452-473 ]
# as found in 
# http://tuvalu.santafe.edu/~aaronc/hierarchy/karate.pairs
karate_pairs="""1	2
1	3
1	4
1	5
1	6
1	7
1	8
1	9
1	11
1	12
1	13
1	14
1	18
1	20
1	22
1	32
2	1
2	3
2	4
2	8
2	14
2	18
2	20
2	22
2	31
3	1
3	2
3	4
3	8
3	9
3	10
3	14
3	28
3	29
3	33
4	1
4	2
4	3
4	8
4	13
4	14
5	1
5	7
5	11
6	1
6	7
6	11
6	17
7	1
7	5
7	6
7	17
8	1
8	2
8	3
8	4
9	1
9	3
9	31
9	33
9	34
10	3
10	34
11	1
11	5
11	6
12	1
13	1
13	4
14	1
14	2
14	3
14	4
14	34
15	33
15	34
16	33
16	34
17	6
17	7
18	1
18	2
19	33
19	34
20	1
20	2
20	34
21	33
21	34
22	1
22	2
23	33
24	26
24	28
24	30
24	33
24	34
25	26
25	28
25	32
26	24
26	25
26	32
27	30
27	34
28	3
28	24
28	25
28	34
29	3
29	32
29	34
30	24
30	27
30	33
30	34
31	2
31	9
31	33
31	34
32	1
32	25
32	26
32	29
32	33
32	34
33	3
33	9
33	15
33	16
33	19
33	21
33	23
33	24
33	30
33	31
33	32
33	34
34	9
34	10
34	14
34	15
34	16
34	19
34	20
34	21
34	23
34	24
34	27
34	28
34	29
34	30
34	31
34	32
34	33"""   

################################################################################
# Tests
################################################################################
               
def stop_test():
    raise KeyboardInterrupt         
    
if __name__=='__main__':

    glog.glog = sys.stdout

    clo = clp.CommandLineParser( sys.argv[1:] )

    if clo.letstry( 'test' ):

        # Run doctest
        #------------

        np.random.seed( 5 )
        
        import doctest
        print 'doctesting nxtikz.py ...'
        doctest.testmod()
        print 'doctest success.'        
    
    else:
    
        # Run specific test
        #------------------
 
        pass

        filein    = clo.letstry( 'filein' )
        assert filein is not None
        asints    = clo.letstry( 'asints' , [ False , True ] )
        G = load_pairs_into_nxGraph( filein = filein , asints = asints )
        
        layout    = clo.letstry( 'layout' , [ None , 'spring' , 'spectral' , 'circular' , 'random' , 'shell' ] )
        if layout == 'spring':
            dim        = clo.letstry( 'dim' , 2 )
            k          = clo.letstry( 'k' , None )
            iterations = clo.letstry( 'iterations' , 50 )
            scale      = clo.letstry( 'scale' , 1. )
            node_position = nx.spring_layout( G , dim = dim , k = k , iterations = iterations , scale = scale )
        elif layout == 'spectral':
            dim        = clo.letstry( 'dim' , 2 )
            scale      = clo.letstry( 'scale' , 1. )
            node_position = nx.spectral_layout( G , dim = dim , scale = scale )
        elif layout == 'circular':
            dim        = clo.letstry( 'dim' , 2 )
            scale      = clo.letstry( 'scale' , 1. )
            node_position = nx.circular_layout( G , dim = dim , scale = scale )
        elif layout == 'shell':
            dim        = clo.letstry( 'dim' , 2 )
            scale      = clo.letstry( 'scale' , 1. )
            node_position = nx.shell_layout( G , dim = dim , scale = scale )
        else:
            node_position = None
            
        node_labels = clo.letstry( 'node_labels' , [ True , False ] )
        if node_labels:
            node_label = None
        else:
            node_label = { n : '' for n in G.nodes() }
        
        fileout = clo.letstry( 'fileout' , None )
        if fileout is None:
            filename , extension = os.path.splitext( os.path.basename( os.path.abspath( filein ) ) )
            fileout = filename + '.tex'
        
        plot_nx_graph( G , filename = fileout , node_position = node_position , node_label = node_label )
