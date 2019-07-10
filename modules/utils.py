################################
#  Sage Sefton
#  Utility Functions for scoring
#  2019 06 26
################################

import pathlib
  #make_pure_path
import os
  #make_pure_path
import re
  #get_negatives

#GET
#TODO: rename, this name doesn't make sense
def get_negatives( truths, scorefile ):
  """ Util Function
      _get_negatives( truths   :pathlib.PurePath
                      scorefile:pathlib.PurePath 
                    ): (int,int)
  """
  f_negs = get_num_lines(truths)

  #Parentheticals are group(1) of re.search(l)
  rex_FA = re.compile( 'Detection-FA: (.*)' )
  with open(scorefile) as s:
    for l in s:
      if rex_FA.search(l):
        t_negs = int(rex_FA.search(l).group(1))
  
  return t_negs, f_negs

#GET
def get_num_lines( file ):
  """ Util Function
      get_lines( file:pathlib.PurePath): int
      Returns the number of lines of a file.
  """
  i = 0
  with open(file) as f:
    for l in f:
      i += 1

  return i

#CONVERT
def ltos_csv( l ):
  """ Util Function
      ltos_csv( l:list ) :string
      Convert a list to a csv-style string
  """
  w=''
  for i in l:
    w += str(i) + ','
  return w[:-1]

#CONVERT
def make_PurePath( loc ):
  """ Util Function
      make_PurePath( loc:string ) :pathlib.PurePath
      Convert a string to PurePath
      filename -> PP( cwd/filename )
      path     -> PP( path )
  """
  if not loc:
    return None

  if not pathlib.PurePath( loc ).is_absolute():
    return pathlib.PurePath( os.getcwd(), loc )
  else:
    return pathlib.PurePath(loc)


