################################
#  Sage Sefton
#  Functions for Executing VIAME
#  scoring functions
#  2019 06 26
################################

import re
import subprocess
import os
#Custom
import utils

def _make_scripts( img_names, args ):
  """ Internal Function
  """
  #TODO: not compatable with Matt's scripts.  custom script only
  script_extension = args.script.name.split('.')[-1]
  rex_t = re.compile('SET TRUTHS=.*')
  rex_c = re.compile('SET TRACKS=.*')
  for i in img_names:
    with open(args.script) as s:
      os.chdir(i)
      oname = args.output / pathlib.PurePath('score_' + i + script_extension)
      with open(oname, 'w' ) as o:
        for l in s:
          if rex_t.match(l):
            l='SET TRUTHS=truth_' + i + '.csv\n'
          if rex_c.match(l):
            l='SET TRACKS=computed_' + i + '.csv\n'
          o.write(l)
  with open(args.script) as s: 
    oname = args.output / pathlib.PurePath('score_all' + script_extension)
    with open(oname, 'w') as o:
      for l in s:
          if rex_t.match(l):
            l='SET TRUTHS=truth_all.csv\n'
          if rex_c.match(l):
            l='SET TRACKS=computed_all.csv\n'
          o.write(l)
  return None

def _script_handler( args ):
  """ Internal Function

  """
  process_name = str(args)
  print( 'About to run: ' + process_name + ' in ' + os.getcwd())
  handle = subprocess.Popen( args,
                             bufsize            = 1,
                             stdin              = subprocess.PIPE,
                             stdout             = subprocess.DEVNULL, 
                             #stdout             = subprocess.PIPE,
                             stderr             = subprocess.STDOUT,
                             universal_newlines = True
                             #text   = True #python 3.7+, uni-NewLine has same effect
                             #encoding = not sure how to use this arg 
                                  )
        
  handle.stdin.write('\n')
  handle.wait()
  print("Done: " + os.getcwd())
  print(handle.returncode)

  return handle.returncode

def run_scripts( img_names, args ):
  """

  """
  _make_scripts( img_names, args )
  script_extension = args.script.suffix
  print('TODO: Purepath on scripts')
  for i in img_names:
    #TODO: does not send purepaths. 
    pname = pathlib.PurePath(i + '/score_' + i + script_extension)
    process = args.output / pname
    args = [process,] #similar to argc/argv
    _script_handler( args )

  #TODO: does not send purepaths. 
  pname = pathlib.PurePath('all/score_all' + script_extension)
  process = args.output / pname
  args = [process,] #similar to argc/argv
  _script_handler( args )

  return None

