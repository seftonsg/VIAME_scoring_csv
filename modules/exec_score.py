################################
#  Sage Sefton
#  Functions for Executing VIAME
#  scoring scripts
#  2019 06 26
################################

import re
import subprocess
import os
import pathlib
#Custom
import modules.utils

#scoring
def _make_scripts( img_names, args ):
  """ Internal Function
      _make_scripts( img_names:list, args:?ty ) :None
      Give a list of images and the full set of 
      terminal args.  Makes VIAME scoring_roc-like
      scripts for later use.
  """
  #TODO: not compatable with Matt's scripts, custom script only
  rex_t = re.compile('SET TRUTHS=.*')
  rex_c = re.compile('SET TRACKS=.*')

  # Make for images
  for i in img_names:
    with open(args.script) as s:
      oname = args.output / i / pathlib.PurePath('score_' + i + args.script.suffix)
      with open(oname, 'w' ) as o:
        for l in s:
          if rex_t.match(l):
            l='SET TRUTHS=truth_' + i + '.csv\n'
          if rex_c.match(l):
            l='SET TRACKS=computed_' + i + '.csv\n'
          o.write(l)

  # Make for all
  with open(args.script) as s: 
    oname = args.output / 'all' / pathlib.PurePath('score_all' + args.script.suffix)
    with open(oname, 'w') as o:
      for l in s:
          if rex_t.match(l):
            l='SET TRUTHS=truth_all.csv\n'
          if rex_c.match(l):
            l='SET TRACKS=computed_all.csv\n'
          o.write(l)
  return None

#scoring
def _script_handler( exec_, argv=None ):
  """ Internal Function
      _script_handler( exec_:pathlib.PurePath, argv:list ) :handle.returncode?ty
      Give a script name and arguments, this will run it.
      Written specifically for VIAME scoring_roc scripts.
  """
  # Move to relevant directory
  basedir = os.getcwd()
  os.chdir(exec_.parent)

  # Prepare arguments
  args = [exec_.name]
  if argv:
    args += argv

  # Run the script with Popen
  print( 'Running: ' + str(exec_) )
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
  
  # Wait to finish
  handle.stdin.write('\n')
  handle.wait()
  if not handle.returncode:
    print('Process: ' + exec_.name + ' completed successfully.')
  else:
    print('Process: ' + exec_.name + ' failed.')

  # Cleanup
  os.chdir(basedir)

  return handle.returncode

#scoring
def run_scripts( img_names, args ):
  """ _ Function
      run_scripts( img_names:list, args:?ty ) :None
      Give a list of images and terminal args,
      this will make and run all the scoring
      scripts.
      TODO: Rename to 'score()' ?
  """
  
  _make_scripts( img_names, args )
  
  script_extension = args.script.suffix

  for i in img_names:
    pname = pathlib.PurePath(i + '/score_' + i + script_extension)
    process = args.output / pname
    _script_handler( process )

  pname = pathlib.PurePath('all/score_all' + script_extension)
  process = args.output / pname
  _script_handler( process )

  return None

