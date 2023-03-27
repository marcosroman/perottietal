###############################################################################
### COPYRIGHT NOTICE ##########################################################
# clp.py - Implementation of a command line parser.
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
import os

class CommandLineParser:
    def __init__( self , argv ):
        self._argv = list( argv )
        self._options_to_values = {}
        for arg in self._argv:
            try:
                option , value = arg.split('=')
#                if value in [ 'true' , 'True' ]:
#                    value = True
#                elif value in [ 'false' , 'False' ]:
#                    value = False
#                else:
#                    try:
#                        value = int( value )
#                    except:
#                        try:
#                            value = float( value )
#                        except:
#                            pass
            except:
                option = arg
                value  = True
            self._options_to_values[ option ] = value

    def __getitem__( self , option ):
        if option in self._options_to_values:
            return self._options_to_values[ option ]
        else:
            return None

    def __iter__( self ):
        for option in sorted( self._options_to_values.keys() ):
            yield option , self[ option ]
            
    def letstry( self , option , values = None , as_format = None ):
        if isinstance( values , list ):
            default_value = values[ 0 ]
            allowed_values = set( values )
        else:
            default_value = values
            allowed_values = None
        value = self[ option ]
        if value is None:
            return default_value
        else:
            if allowed_values is not None:
                assert value in allowed_values , 'ERROR : value not in allowed_values; Command Line Parser.'
        if as_format is not None:
            return as_format( value )
        elif value in [ 'true' , 'True' ]:
            value = True
        elif value in [ 'false' , 'False' ]:
            value = False
        else:
            try:
                value = int( value )
            except:
                try:
                    value = float( value )
                except:
                    pass
        return value
        
def decompose_pathfile( pathfile ):
    """
    This works for linux only...
    
    >>> print decompose_pathfile( 'clp.py' )
    ('/home/juan/Workbench/hierpart/hierpart/', 'clp', '.py')
    """
    directory = os.path.dirname( os.path.abspath( pathfile ) )
    if directory is not None:
        if directory[-1] != '/':
            directory += '/'
    filename , extension = os.path.splitext( os.path.basename( os.path.abspath( pathfile ) ) )
    return directory , filename , extension

def replace_last(source_string, replace_what, replace_with):
    head, sep, tail = source_string.rpartition(replace_what)
    return head + replace_with + tail

def replace_extension( pathfile , extension , assert_dot = True ):
    """
    This works for linux only...
    
    >>> replace_extension( 'clp.py' , 'YEA!' )
    'clp.YEA!'
    """
    directory , filename , _extension = decompose_pathfile( pathfile )
    if extension[0] != '.' and assert_dot:
        extension = '.' + extension
    return replace_last( pathfile , _extension , extension )

if __name__ == '__main__':

    clo = CommandLineParser( sys.argv[1:] )
    
    if clo.letstry( 'test' ):
        # Run doctest
        #------------
        
        import doctest
        print 'doctesting clp.py ...'
        doctest.testmod()
        print 'doctest success.'        
        
    else:

        for o , v in clo:
            print o , v
