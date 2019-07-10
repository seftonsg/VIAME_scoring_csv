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

def order_coordinates( track_file, labels_file, new_file ):
  return None