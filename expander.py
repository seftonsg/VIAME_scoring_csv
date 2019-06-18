#expander.py

import os
import re
import sys
import shutil
import argparse


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
  return w

def create_tmp_track_files( img_names, filename, prepend='' ):
  with open( filename ) as f:
    for i in img_names:
      #create tmp file
      with open( prepend+i+".csv", 'w' ) as o:
        count = 0
        for l in f:
          #find lines associated with the image
          l = l.strip().split(',')
          name = (l[1].split('.'))[0]
          if name == i:
            l[0] = count
            l[2] = 0
            o.write( ltos(l) + "\n" )#'x'.join(y) adds list y to the end of string x
            count += 1
      #o.close()

    #f.close()
  return None

def make_dir_tree( img_names, newdir ):
  if os.path.exists( newdir ):
    if not rmtree.avoids_symlink_attacks:
      print( 'You are vulnerable to symlink attacks, please upgrade python or remove the output directory manualy.' )
      sys.exit( 0 )
    shutil.rmtree( newdir )

  os.mkdir( newdir )
  os.chdir( newdir )
  for i in img_names:
    os.mkdir( i )
  os.mkdir( 'all ' )
  os.chdir( '..' )

  return None


def copy_vitals( img_names, args ):
  if args.joint:
    shutil.copyfile(args.joint, args.output+args.joint)
  if args.category:
    shutil.copyfile(args.category, args.output+args.category)



  os.chdir(args.output)
  cwd = os.getcwd
  for i in img_names:
    #truths
    fname = "truth_"+i+".csv"
    src = cwd + '/' + fname
    dst = cwd + '/' + i + '/' + fname
    os.rename( src, dst )

  os.chdir( '..' )
  return None



if __name__ == "__main__":
  parser = argparse.ArgumentParser( description = 'Creates scoring directories by the image' )

  # Inputs
  parser.add_argument( '-truth', default=None,
             help='Input filename for groundtruth file.' )
  oarser.add_argument( '-computed', default=None,
             help='Input filename for computed tracks file.' )
  parser.add_argument( '-images', default=None,
             help='Input directory for images.')

  parser.add_argument( '-joint', default=None,
             help='The name of the joint scoring script.  Will not copy otherwise.')
  parser.add_argument( '-category', default=None,
             help='The name of the categorical scoring script.  Will not copy otherwise.')

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
  if args.joint and not os.path.exists(args.joint): #can I raise an exception here?
    print( 'Error: specified joint scoring file does not exist' )
    sys.exit( 0 )
  if args.category and not os.path.exists(args.category):
    print( 'Error: specified categorical scoring file does not exist' )
    sys.exit( 0 )
  if os.path.exists(args.output):
    print( 'Warning: directory already exists and will be overwritten' )


  #get the names of the images
  img_names = get_imgs( args.images )

  #create directory tree
  make_dir_tree( img_names, args.output )

  #create a new truth file for each image
  os.chdir(args.output)
  create_tmp_track_files( img_names, args.truth, 'truth_' )
  create_tmp_track_files( img_names, args.computed, 'computed_' )
  os.chdir( '..' )

  #copy over vital files
  copy_vitals( img_names, args )
  
  print(img_names)
  #create a new computed file for each image
  #don't forget the "all" directory





