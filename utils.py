################################
#  Sage Sefton
#  Utility Functions for scoring
#  2019 06 26
################################

import pathlib
  #make_pure_path
import os
  #make_pure_path


def ltos_csv( l ):
  """ Convert a list to a csv-style string
  """
  w=''
  for i in l:
    w += str(i) + ','
  return w[:-1]


def make_pure_path( loc ):
  """ Convert a string to PurePath
      filename -> PP( cwd/filename )
      path     -> PP( path )
  """
  if not loc:
    return None

  if not pathlib.PurePath( loc ).is_absolute():
    return pathlib.PurePath( os.getcwd(), loc )
  else:
    return pathlib.PurePath(loc)