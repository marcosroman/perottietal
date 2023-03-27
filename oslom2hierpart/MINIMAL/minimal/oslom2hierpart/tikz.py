###############################################################################
### COPYRIGHT NOTICE ##########################################################
# tikz.py : Tools to work with tikz.
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
# Collaborators: None. Personal development.
# Project      : Many---this is a general tool.
# Location     : Institute for Advanced Studies Lucca, Piazza S.Francesco, 19, 
#                55100 Lucca LU, Italy.
# Created      : 2016
# Modified     : -- (cleaned up for public consumption)
# 
###############################################################################

import sys
import numpy as np
import random

tikz_doc = """%##############################################################################
%## COPYRIGHT NOTICE ##########################################################
% Produced by tikz.py .
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
CONTENT
\end{document}
"""

# http://colorbrewer2.org/
_RGB_colors_qualitative_12="""166,206,227
31,120,180
178,223,138
51,160,44
251,154,153
227,26,28
253,191,111
255,127,0
202,178,214
106,61,154
255,255,153
177,89,40"""

_RGB_colors_qualitative_12_extended="""166,206,227
31,120,180
178,223,138
51,160,44
251,154,153
227,26,28
253,191,111
255,127,0
202,178,214
106,61,154
255,255,153
255,0,0
0,255,0
0,0,255
0,255,255
255,0,255
255,255,0"""

class ColorJet:
    """
    >>>
    """
    def __init__( self , RGB_color_pool = _RGB_colors_qualitative_12_extended , seed = 121242 ):
        self._color_pool = []
        for clr in RGB_color_pool.split():
            R , G , B = clr.split(',')
            self._color_pool.append( ( R , G , B ) )            
        self._r = random.Random()
        self._r.seed( seed )
        self._r.shuffle( self._color_pool )

    def num_colors( self ):
        """
        >>> ColorJet().num_colors()
        17
        """
        return len( self._color_pool )

    def color( self , i ): # , porcentage_1 = None , porcentage_2 = None ):
        """
        >>> cj = ColorJet( )
        >>> CONTENT = '''\\\\begin{tikzpicture}\\n''' + '\\n'.join([ "\draw[color=" + cj.color( i ) + "] (0mm," + str(i) + "mm) -- (10mm," + str(i) + "mm);" for i in xrange( cj.num_colors() ) ]) + '''\end{tikzpicture}\\n'''
        >>> with open( 'doctest_tikz__color.tex' , 'w' ) as fhw:
        ...    print >>fhw , tikz_doc.replace( 'CONTENT' , CONTENT )
        """
        R , G , B = self._color_pool[ i % self.num_colors() ]
        return '\gprgb{'+R+'}{'+G+'}{'+B+'}'

    def random_color( self ):
        """
        >>> cj = ColorJet( )
        >>> CONTENT = '''\\\\begin{tikzpicture}\\n''' + '\\n'.join([ "\draw[color=" + cj.random_color() + "] (0mm," + str(i) + "mm) -- (10mm," + str(i) + "mm);" for i in xrange( cj.num_colors() ) ]) + "\\n" + '''\end{tikzpicture}\\n'''
        >>> with open( 'doctest_tikz__random_color.tex' , 'w' ) as fhw:
        ...    print >>fhw , tikz_doc.replace( 'CONTENT' , CONTENT )
        """
        return self.color( self._r.randint( 0 , self.num_colors() ) )
        
    def __iter__( self ):
        """
        >>> for i , rgb in enumerate( ColorJet() ):
        ...     print i , rgb
        0 \gprgb{51}{160}{44}
        1 \gprgb{253}{191}{111}
        2 \gprgb{255}{0}{255}
        3 \gprgb{0}{255}{0}
        4 \gprgb{178}{223}{138}
        5 \gprgb{255}{127}{0}
        6 \gprgb{202}{178}{214}
        7 \gprgb{31}{120}{180}
        8 \gprgb{166}{206}{227}
        9 \gprgb{0}{0}{255}
        10 \gprgb{255}{255}{153}
        11 \gprgb{227}{26}{28}
        12 \gprgb{0}{255}{255}
        13 \gprgb{255}{255}{0}
        14 \gprgb{106}{61}{154}
        15 \gprgb{251}{154}{153}
        16 \gprgb{255}{0}{0}
        """
        for i in xrange( self.num_colors() ):
            yield self.color( i )
        
def stop_test():
    raise KeyboardInterrupt         
    
if __name__=='__main__':

    if 'test' in sys.argv[1:]:

        # Run doctest
        #------------
        import doctest
        print 'doctesting tikz.py ...'
        doctest.testmod()
        print 'doctest success.'        
    
    else:
    
        # Run specific test
        #------------------
 
        pass
          
        #glog = None          
        #glog = open( 'glog.dbg' , 'w' )    
