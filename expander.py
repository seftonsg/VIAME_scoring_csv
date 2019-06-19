#expander.py

import os
import re
import sys
import shutil
import argparse
import subprocess
import shlex      #shell tokenizer
import time       #for sleep

def get_imgs( directory ):

  img_names = []

  for l in os.listdir(directory):
    l = l.strip().split('.')
    if len( l[0] ) > 0 and l[0][0] == '#':
      continue
    if len( l[0] ) == 0:
      continue
    img_names.append(l[0])

  return img_names

def ltos( l ):
  w=""
  for i in l:
    w += str(i) + ','
  return w[:-1]

def create_subtrack_files( img_names, args ):
  with open( args.truth ) as t:
    for i in img_names:
      #create sub-truth files
      with open( 'truth_' + i + ".csv", 'w' ) as o:
        count = 0
        for l in t:
          #find lines associated with the image
          l = l.strip().split(',')
          name = (l[1].split('.'))[0]
          if name == i:
            l[0] = count
            l[2] = 0
            o.write( ltos(l) + "\n" )#'x'.join(y) adds list y to the end of string x
            count += 1

  with open( args.computed ) as c:
    for i in img_names:
    #create sub-computed files
      with open( 'computed_' + i + ".csv", 'w' ) as o:
        count = 0
        for l in c:
          #find lines associated with the image
          l = l.strip().split(',')
          name = (l[1].split('.'))[0]
          if name == i:
            l[0] = count
            l[2] = 0
            o.write( ltos(l) + "\n" )#'x'.join(y) adds list y to the end of string x
            count += 1

  return None

def move_subtrack_files( img_names, args ):
  
  cwd = os.getcwd()
  for i in img_names:
    #truth
    tname = "truth_"+i+".csv"
    src = cwd + '/' + tname
    dst = cwd + '/' + i + '/' + tname
    os.rename( src, dst )
    #computed
    cname = "computed_"+i+".csv"
    src = cwd + '/' + cname
    dst = cwd + '/' + i + '/' + cname
    os.rename( src, dst )

  return None

def make_dir_tree( img_names, newdir ):
  if os.path.exists( newdir ):
    #if not shutil.rmtree.avoids_symlink_attacks:
    #  print( 'You are vulnerable to symlink attacks, please upgrade python or remove the output directory manualy.' )
    #  sys.exit( 0 )
    shutil.rmtree( newdir )

  os.mkdir( newdir )
  os.chdir( newdir )
  for i in img_names:
    os.mkdir( i )
  os.mkdir( 'all ' )
  os.chdir( '..' )

  return None

def copy_vitals( args ):
  shutil.copyfile(   args.script, args.output +     '/' +        args.script)
  shutil.copyfile(    args.truth, args.output +     '/' +         args.truth)
  shutil.copyfile( args.computed, args.output +     '/' +      args.computed)
  shutil.copyfile(    args.truth, args.output + '/all/' +    'truth_all.csv')
  shutil.copyfile( args.computed, args.output + '/all/' + 'computed_all.csv')
  return None

def make_scripts( img_names, args ):
  #TODO: not compatable with Matt's scripts.  custom script only
  script_extension = args.script.split('.')[-1]
  tre = re.compile('SET TRUTHS=.*')
  cre = re.compile('SET TRACKS=.*')
  for i in img_names:
    with open(args.script) as s:
      os.chdir(i)
      with open('score_' + i + '.' + script_extension, 'w' ) as o:
        for l in s:
          if tre.match(l):
            l='SET TRUTHS=truth_' + i + '.csv\n'
          if cre.match(l):
            l='SET TRACKS=computed_' + i + '.csv\n'
          o.write(l)
      os.chdir( '..' )
  with open(args.script) as s: 
    os.chdir( 'all' )
    with open('score_all.' + script_extension, 'w') as o:
      for l in s:
          if tre.match(l):
            l='SET TRUTHS=truth_' + i + '.csv\n'
          if cre.match(l):
            l='SET TRACKS=computed_' + i + '.csv\n'
          o.write(l)
      os.chdir( '..' )
  return None

def script_handler( args ):
  process_name = args.split(' ')[0]
  print( 'About to run: ' + process_name + ' in ' + os.getcwd())
  handle = subprocess.Popen( args,
                             bufsize            = 1,
                             stdin              = subprocess.PIPE,
                             stdout             = subprocess.PIPE,
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
  script_extension = args.script.split('.')[-1]
  for i in img_names:
    os.chdir(i)
    process_name = 'score_' + i + '.' + script_extension
    args = process_name #shlex.split(process_name + "")
    script_handler( args )
    os.chdir( '..' )

  os.chdir( 'all' )
  process_name = 'score_all.' + script_extension
  args = process_name #shlex.split(process_name + "")
  script_handler( args )
  os.chdir( '..' )

  return None


if __name__ == "__main__":
  parser = argparse.ArgumentParser( description = 'Creates scoring directories by the image' )

  # Inputs
  parser.add_argument( '-truth', default=None,
             help='Input filename for groundtruth file.' )
  parser.add_argument( '-computed', default=None,
             help='Input filename for computed tracks file.' )
  parser.add_argument( '-images', default=None, #edit to accept file, or just computed
             help='Input directory for images.')
  parser.add_argument( '-script', default=None,
             help='The name of the scoring script.  Will not copy otherwise.')

  # Outputs
  parser.add_argument( '-output', default='exp',
             help='Output directory for expanded folders.')

  args = parser.parse_args()

  if not args.truth:
    print( 'Error: truths file must be specified' )
    sys.exit( 0 )
  if not args.computed: #note the user could not do this, and instead create annotations manually
    print( 'Error: computed file must be specified' )
    print( '       manual addition of computed tracks not yet supported' )
    sys.exit( 0 )
  if not args.images:
    print( 'Error: images directory must be specified' )
    sys.exit( 0 )

  if not args.script:
    print( 'Error: a running script must be specified' )
    sys.exit( 0 )
  if args.script and not os.path.exists(args.script): #can I raise an exception here?
    print( 'Error: specified script scoring file does not exist' )
    sys.exit( 0 )

  if os.path.exists(args.output):
    print( 'Warning: directory already exists and will be overwritten' )


  #get the names of the images
  img_names = get_imgs( args.images )

  #create directory tree
  make_dir_tree( img_names, args.output )

  #copy over vital files
  copy_vitals( args )

  #create a new truth file for each image
  os.chdir(args.output)
  create_subtrack_files( img_names, args )
  move_subtrack_files(   img_names, args )

  #make the scripts
  make_scripts( img_names, args )
  run_scripts(  img_names, args )
  os.chdir( '..' )

  print( 'Done' )
  #create a new computed file for each image
  #don't forget the "all" directory
