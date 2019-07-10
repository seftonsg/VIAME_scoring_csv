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
import modules.utils as utils
import modules.iou_calc as iou_calc

#scoring
def _script_handler( exec_, argv=None ):
  """ Internal Function
      _script_handler( exec_:pathlib.PurePath, argv:list ) :handle.returncode?ty
      TODO: redocument
  """
  # Move to relevant directory
  basedir = os.getcwd()
  os.chdir(exec_.parent)

  tmp_dir = exec_ / '.tmp'
  preproc.order_coordinates(    args.truth, tmp_dir/'tmpt.csv' )
  preproc.order_coordinates( args.computed, tmp_dir/'tmpc.csv')

  iou_calc.get_table( tmp_dir/'tmpt.csv', tmp_dir/'tmpc.csv', tmp_dir/'IoU.csv' )

  
  # Wait to finish
  handle.stdin.write('\n')
  handle.wait()
  if not handle.returncode:
    print('Process: ' + exec_.name + ' completed successfully.')
  else:
    print('Process: ' + exec_.name + ' failed.')

  # Cleanup
  os.chdir(basedir)

  return None

#scoring
def run_scripts( img_names, args ):
  """ _ Function
      run_scripts( img_names:list, args:?ty ) :None
      Give a list of images and terminal args,
      this will make and run all the scoring
      scripts.
      TODO: Rename to 'score()' ?
  """
  
  script_extension = args.script.suffix

  for i in img_names:
    pname = pathlib.PurePath(i + '/score_' + i + script_extension)
    process = args.output / pname
    _script_handler( process )

  pname = pathlib.PurePath('all/score_all' + script_extension)
  process = args.output / pname
  _script_handler( process )

  return None

