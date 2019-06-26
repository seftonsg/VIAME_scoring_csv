################################
#  Sage Sefton
#  Utility Functions for scoring
#  2019 06 26
################################

import re
import subprocess
import os



def make_scripts( img_names, args ):
  #TODO: not compatable with Matt's scripts.  custom script only
  script_extension = args.script.name.split('.')[-1]
  rex_t = re.compile('SET TRUTHS=.*')
  rex_c = re.compile('SET TRACKS=.*')
  for i in img_names:
    with open(args.script) as s:
      os.chdir(i)
      with open('score_' + i + '.' + script_extension, 'w' ) as o:
        for l in s:
          if rex_t.match(l):
            l='SET TRUTHS=truth_' + i + '.csv\n'
          if rex_c.match(l):
            l='SET TRACKS=computed_' + i + '.csv\n'
          o.write(l)
      os.chdir( '..' )
  with open(args.script) as s: 
    os.chdir( 'all' )
    with open('score_all.' + script_extension, 'w') as o:
      for l in s:
          if rex_t.match(l):
            l='SET TRUTHS=truth_all.csv\n'
          if rex_c.match(l):
            l='SET TRACKS=computed_all.csv\n'
          o.write(l)
      os.chdir( '..' )
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
  script_extension = args.script.suffix
  print('TODO: Purepath on scripts')
  for i in img_names:
    os.chdir(i)
    #TODO: does not send purepaths. 
    process_name = 'score_' + i +  script_extension
    args = process_name #shlex.split(process_name + "")
    _script_handler( args )
    os.chdir( '..' )

  os.chdir( 'all' )
  #TODO: does not send purepaths. 
  process_name = 'score_all' + script_extension
  args = process_name #shlex.split(process_name + "")
  _script_handler( args )
  os.chdir( '..' )

  return None