###############################################################################
### COPYRIGHT NOTICE ##########################################################
# glog.py - Module to store global variables.
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
# Collaborators: None, personal development.
# Project      : Many---this is a general tool.
# Location     : Institute for Advanced Studies Lucca, Piazza S.Francesco, 19, 
#                55100 Lucca LU, Italy.
# Created      : 2016
# Modified     : -- (cleaned up for public consumption)
# 
###############################################################################

import sys

# The global log file handler...
glog = sys.stdout

def report_glog( fileout ):
    with open( fileout , 'w' ) as fhw:
        print >> fhw , '# glog' , glog
