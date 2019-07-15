################################
#  Sage Sefton
#  Functions for pre-processing
#  2019 07 09
################################
#  This includes:
# -Forcing all detections to be 
#  on one line (not default)
# -Re-naming all detection classes 
#  based on the labels (category
#  scoring only)
# -Fix detection points to be 
#  x1,y1,x2,y2
################################

import modules.utils as utils

#CONVERT
def expand_by_detection( track_file, new_file ):
  """ Util Function
      make_single_lined( track_file  :pathlib.PurePath 
                         new_file    :pathlib.PurePath ):None
      Creates a new file where all detections are placed
      on unique lines, re-enumerated, 
  """
  if track_file == new_file:
    print('Same file')
  return None

def consolidate_classes( track_file, labels_file, new_file ):
  if new_file == track_file:
    print('Same file')
  return None

def order_coordinates( track_file, new_file ):
  with open( track_file ) as t:
    with open( new_file, 'w') as n:
      for l in t: #this seems commonly written, make a util?  Format atoms as proper types?
        l = l.strip().split(',')
        ax = float(l[3])
        ay = float(l[4])
        bx = float(l[5])
        by = float(l[6])
        if (ax > bx): #not in order
          l[3] = bx
          l[5] = ax
        if (ay > by):
          l[4] = by
          l[6] = ay
        n.write( ( utils.ltos_csv(l) + '\n' ) )

  return None

def make_fake_data( track_file, new_file ):
  with open( track_file ) as t:
    with open( new_file, 'w') as n:
      for l in t: #this seems commonly written, make a util?  Format atoms as proper types?
        l = l.strip().split(',')
        ax = float(l[3]) +10
        ay = float(l[4]) +10
        bx = float(l[5]) +10
        by = float(l[6]) +10
        if (ax > bx): #not in order
          l[3] = bx
          l[5] = ax
        if (ay > by):
          l[4] = by
          l[6] = ay
        n.write( ( utils.ltos_csv(l) + '\n' ) )

  return None

def get_avg_dxdy( track_file ):
  xs = 0
  ys = 0
  n = 0
  with open( track_file ) as t:
    for l in t:
      l = l.strip().split(',')
      xs += abs(float(l[5]) - float(l[3]))
      ys += abs(float(l[6]) - float(l[4]))
      n  += 1
  return [(xs/n), (ys/n)]











