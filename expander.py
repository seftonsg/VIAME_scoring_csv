#!/usr/bin/python
########################################
#  Sage Sefton
#  A scoring script for multiple
#  images, by category (wip), human
#  readable outputs, and graphs.
#  2019 06 26
########################################

import os
import re
import sys
import shutil
import argparse
import subprocess
import pathlib 
#Custom imports
import modules.utils      as utils
import modules.preproc    as preproc
import modules.iou_table  as iou_table
import modules.pvr_table  as pvr_table

#init
def get_imgs( directory ):
  """ Function
      get_imgs( directory:pathlib.PurePath) :list
      Given a directory or list file (txt), returns
      a list of the found images.
  """
  img_names = []

  if not directory.suffix:
    for l in os.listdir( directory ):
      l = l.strip().split('.')
      if len( l[0] ) > 0 and l[0][0] == '#':
        continue
      if len( l[0] ) == 0:
        continue
      img_names.append(l[0])
  elif directory.suffix == '.txt':
    with open( directory ) as d:
      for l in d:
        l = l.strip().split('.')
        if len(l[0]) == 0 or l[0][0] == '#':
          continue
        img_names.append(l[0])

  return img_names

#init
def create_subtrack_files( img_names, out_dir, truth_file, comp_file ):
  """ Function
      create_subtrack_files( img_names:list, 
        out_dir   :pathlib.PurePath 
        truth_file:pathlib.PurePath,
        comp_file :pathlib.PurePath
        ) :None
      Given the locations of truth and computed files,
      separates all by images and puts in the respective
      output folders.
  """
  for i in img_names:
    with open( truth_file ) as t:
      #create sub-truth files
      tfile_o = out_dir / ( 'truth_' + i + '.csv')
      with open( tfile_o, 'w' ) as o:
        count = 0
        for l in t:
          #find lines associated with the image
          l = l.strip().split(',')
          name = (l[1].split('.'))[0]
          if name == i:
            l[0] = count
            l[2] = 0
            o.write( utils.ltos_csv(l) + '\n' )#'x'.join(y) adds list y to the end of string x
            count += 1

    with open( comp_file ) as c:
    #create sub-computed files
      cfile_o = out_dir / ( 'computed_' + i + '.csv')
      with open( cfile_o, 'w' ) as o:
        count = 0
        for l in c:
          #find lines associated with the image
          l = l.strip().split(',')
          name = (l[1].split('.'))[0]
          if name == i:
            l[0] = count
            l[2] = 0
            o.write( utils.ltos_csv(l) + '\n' )#'x'.join(y) adds list y to the end of string x
            count += 1

  return None

#init
def move_subtrack_files( img_names, out_dir ):
  """ Function
      move_subtrack_files( img_names:list, dst:pathlib.PurePath ) :None
      Given the images and output directory, moves all subtrack
      (.csv) files to their respective folders.
  """
  #cwd = os.getcwd()
  for i in img_names:
    #truth
    tname = 'truth_'+i+'.csv'
    src = out_dir / tname
    dst = out_dir / i / tname
    preproc.order_coordinates(src, dst)
    os.remove( src )
    #os.rename( src, dst )
    #computed
    cname = 'computed_'+i+'.csv'
    src = out_dir / cname
    dst = out_dir / i / cname
    preproc.order_coordinates(src, dst)
    os.remove( src )
    #os.rename( src, dst )

  return None

#init
def make_dir_tree( img_names, newdir ):
  """ Function
      make_dir_tree( img_names:list, newdir:pathlib.PurePath ) :None
      Creates a new directory with folders for each image,
      all, and results.  If location exists, delete it first.
  """
  if os.path.exists( newdir ):
    #if not shutil.rmtree.avoids_symlink_attacks:
    #  print( 'You are vulnerable to symlink attacks, please upgrade python or remove the output directory manualy.' )
    #  sys.exit( 0 )
    shutil.rmtree( newdir )

  os.mkdir( newdir )
  #os.chdir( newdir )
  for i in img_names:
    os.mkdir( newdir / i )
  os.mkdir( newdir / 'all' )
  os.mkdir( newdir / 'results' )
  #os.chdir( '..' )

  return None

#init 
def copy_vitals( args ):
  """ Function
      copy_vitals( args:?ty ) :None
      Copies all src files to the output dir as
      not to alter the existing ones.
  """
  preproc.order_coordinates(    args.truth, args.output /         args.truth.name)
  preproc.order_coordinates( args.computed, args.output /      args.computed.name)
  preproc.order_coordinates(    args.truth, args.output / 'all' /    'truth_all.csv')
  preproc.order_coordinates( args.computed, args.output / 'all' / 'computed_all.csv')
  #shutil.copyfile(    args.truth, args.output / 'all' /    'truth_all.csv')
  #shutil.copyfile( args.computed, args.output / 'all' / 'computed_all.csv')
  return None

#Main
if __name__ == "__main__":
  parser = argparse.ArgumentParser( description = 'Creates scoring directories by the image, returns COCO metrics.' )

  print('\n')

  # Inputs
  parser.add_argument( '-truth', default=None,
             help='Input filename for groundtruth file.' )
  parser.add_argument( '-computed', default=None,
             help='Input filename for computed tracks file.' )
  parser.add_argument( '-images', default=None, #edit to accept file, or just computed
             help='Input directory or list file for images.')

  # Outputs
  parser.add_argument( '-output', default='exp',
             help='Output directory for expanded folders.')
  parser.add_argument( '-results', default='results',
             help='Results folder name, stored within output dir.')
  # parser.add_argument( '-res_file', default='results.txt',
  #            help='Specify a name for the human-readable results txt file.')
  # parser.add_argument( '-res_csv', default='stats.csv',
  #            help='Specify the csv file with calculated statistics.')
  # parser.add_argument( '-csv_by_file', default=None,
  #            help='If true, CSV files will be created per image, not combined to one file.')

  # Configs?
  #overlap
  #pixel overlap ratio stuff?
  #etc...

  args = parser.parse_args()

  if not args.truth:
    print( 'Error: truths file must be specified' )
    sys.exit( 0 )
  if not args.computed: #note the user could not do this, and instead create annotations manually
    print( 'Error: computed file must be specified' )
    print( '       manual addition of computed tracks not yet supported' )
    sys.exit( 0 )
  if not args.images:
    print( 'Error: images directory or list file must be specified' )
    sys.exit( 0 )

  if os.path.exists(args.output):
    print( 'Warning: Directory already exists and will be overwritten: ', args.output )

  cwd = os.getcwd()

  args.truth    = utils.make_PurePath(    args.truth )
  args.computed = utils.make_PurePath( args.computed )
  args.images   = utils.make_PurePath(   args.images ) 
  args.output   = utils.make_PurePath(   args.output )
  args.results  = args.output / args.results

  #tmp_dir = args.output / '.tmp'
  tmp_dir = utils.make_PurePath('.tmp')
  #print(tmp_dir)
  if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

  #get the names of the images
  img_names = get_imgs( args.images )

  ################################
  #Actually do the math and stuff:
  ################################
  #create directory tree 
  make_dir_tree( img_names, args.output )

  #copy over vital files
  copy_vitals( args )

  #create a new truth file for each image
  create_subtrack_files( img_names, args.output, args.truth, args.computed )
  move_subtrack_files(   img_names, args.output )

  #make and get results by the image
  pvr_table.get_results( img_names, args )

  print( 'Done\n' )
