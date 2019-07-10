########################################
#  Sage Sefton
#  Options for calculating IoU and the
#  relevant tables.  To calculate matches
#  over another IoU, 
#  Dynamic programming would possibly
#  be fastest here.
#  2019 07 09
########################################

#scipy
import scipy.sparse
#custom
import modules.utils as utils

ERROR_MARGIN = 10 ** -10

def _area( box ):
  dx = box[2] - box[0]
  dy = box[3] - box[1]
  return abs(dx * dy)

def _between( test, x1, x2 ):
  #WARNING: assumes x1<x2
  return ((x1 < test) and (test < x2)) #or \
       #(test > x1 and test < x2)

def _in_rect( point, rect ):
  """ Internal Function
    _overlap( point:list(2)
          rect_:list(4)
          ):bool
  """
  return _between( point[0], rect[0], rect[2] ) and \
         _between( point[1], rect[1], rect[3] )

def _get_corners_inside( rect_a, rect_b ):
  ret  = [ _in_rect( [rect_a[0], rect_a[1]], rect_b ), #bottom left
           _in_rect( [rect_a[0], rect_a[3]], rect_b ), #top left
           _in_rect( [rect_a[2], rect_a[3]], rect_b ), #top right
           _in_rect( [rect_a[2], rect_a[1]], rect_b )] #bottom right
  num = 0
  for i in ret:
    if i:
      num += 1
  return ret, num

def _calc_iou( rect_a, rect_b ):
  """ Internal Function
    _calc_iou( rect_a:list(4*float)
           rect_b:list(4*float)
    ) :float
    Calculate the IOU (if any) and return it (or None)
  """
  box_i = [None] * 4

  #Determine which corner is within rect_b, if any
  k, s = _get_corners_inside(rect_a, rect_b)
  if s == 1:#point
    if   k == [1, 0, 0, 0]: #point - LL
      box_i  = list(rect_a[ :2])
      box_i += [ rect_b[  2], rect_b[3] ]
    elif k == [0, 1, 0, 0]: #point - UL
      box_i  = [ rect_a[  0], rect_b[1],
                 rect_b[  2], rect_a[3] ]
    elif k == [0, 0, 1, 0]: #point - UR
      box_i  = list(rect_b[ :2]) 
      box_i += [ rect_a[  2], rect_a[3] ]
    elif k == [0, 0, 0, 1]: #point - LR
      box_i  = [ rect_b[  0], rect_a[1], 
                 rect_a[  2], rect_b[3] ]
    else:
      print("Mathematically impossible.")
      print("DEBUG: ", rect_a, rect_b, k, s)
      sys.exit(1)
  elif s == 2: #side
    if   k == [1, 1, 0, 0]: #side - LEFT
      box_i  = list(rect_a[ :2])
      box_i += [ rect_b[  2], rect_b[3] ]
    elif k == [0, 1, 1, 0]: #side - TOP
      box_i  = [ rect_a[  0], rect_b[1] ] 
      box_i += list(rect_a[2: ])
    elif k == [0, 0, 1, 1]: #side - RIGHT
      box_i  = [ rect_b[  0], rect_b[1] ]
      box_i += list(rect_a[2: ])
    elif k == [1, 0, 0, 1]: #side - BOTTOM
      box_i  = list(rect_a[ :2])
      box_i += [ rect_a[  2], rect_b[3] ]
    else:
      print("Mathematically impossible.")
      print("DEBUG: ", rect_a, rect_b, k, s)
      sys.exit(1)
  elif s == 4: #inside
    box_i = rect_a
  elif s == 0: #outside
    k2, s2 = _get_corners_inside(rect_b, rect_a)
    if s2 == 2: #bump (side of b in a)
      if   k2 == [0, 0, 1, 1]: #along left side
        box_i  = [ rect_a[  0], rect_b[1] ]
        box_i += list(rect_b[2: ])
      elif k2 == [1, 0, 0, 1]: #along top side
        box_i  = list(rect_b[ :2])
        box_i += [ rect_b[  2], rect_a[3] ]
      elif k2 == [1, 1, 0, 0]: #along right side
        box_i  = list(rect_b[ :2])
        box_i += [ rect_a[  2], rect_b[3] ] 
      elif k2 == [0, 1, 1, 0]: #along bottom side
        box_i  = [ rect_b[  0], rect_a[1] ]
        box_i += list(rect_b[2: ])
    elif s2 == 4: #encompass
      box_i = rect_b
    else:
      return None
  else:
    print("Mathematically impossible.")
    print("DEBUG: ", rect_a, rect_b, k, s)
    sys.exit(1) #failure
  #calculate areas
  area_a = _area( rect_a )
  area_b = _area( rect_b )
  area_i = _area( box_i )
  area_u = area_a + area_b - area_i
  return float(area_i / area_u)

def _make_table( rects_t, rects_c ):
  table = scipy.sparse.lil_matrix( (len(rects_t), len(rects_c)) )
  print(len(rects_t), ':', len(rects_c))
  for t_idx in range(len(rects_t)-1):
    for c_idx in range(len(rects_c)-1):
      iou = _calc_iou( rects_t[t_idx], rects_c[c_idx] )
      if iou and iou > ERROR_MARGIN:
        table[ t_idx, c_idx ] = iou
  return table

def _pair_majority( ious, t_tys, c_tys, confs, by_class=None ):
  #new name: find matches? uniliniar pairs? 1:1??
  #instead of this... reverse-sort the elements of the array by IOU
  #bin into proper tru/com links 

  #Get all nonzero values
  meta_ious = []
  nz_coords = []
  nz_arr = ious.nonzero()
  for idx in range(len(nz_arr[0])-1):
    nz_coords.append((nz_arr[0][idx], nz_arr[1][idx]))

  #Fill data
  for t_idx, c_idx in nz_coords:
    meta_ious.append(
      [t_idx, c_idx,
      t_tys[t_idx], c_tys[c_idx],
      ious[t_idx,c_idx], confs[c_idx]])

  #Multi-sort, starting with least significant
  meta_ious.sort(key=lambda x: x[5]) #confidence
  if by_class:
    meta_ious.sort(key=lambda x: x[2]==x[3]) #same class (?)
  meta_ious.sort(key=lambda x: x[4]) #iou

  #Create a matrix of matches
  pruned = [] #pairs are defined as (t_idx, c_idx, t_ty, c_ty, IOU, conf)
  used_t_idx = []
  used_c_idx = []
  #go in reverse order as python's sort is low->high
  for meta_iou in meta_ious[::-1]: 
    if ((meta_iou[0] not in used_t_idx) and
        (meta_iou[1] not in used_c_idx)):
        pruned.append(meta_iou)
        used_t_idx.append(meta_iou[0])
        used_c_idx.append(meta_iou[1])


  with open('test.txt', 'w') as o:
    for i in pruned:
      o.write((utils.ltos_csv(i) + '\n'))


  
  
  unmatched_truths = []
  if by_class:
    print("Not ready yet")
    sys.exit(0)
  else:
    print("none")
  return None

def get_table( truth_file, comp_file ):
  #t_data = ([None], '')
  #c_data = ([None], '', 0.0)
  t_tys  = []
  t_rect = []
  c_tys  = []
  c_conf = []
  c_rect = []
  with open(truth_file) as t:
    for i in t:
      i = i.split(',')
      coords  = ( float(i[3]), float(i[4]), float(i[5]), float(i[6]) )
      t_tys  += [ str(i[9]) ]
      t_rect += [ coords    ]
  with open(comp_file) as c:
    for i in c:
      i = i.split(',')
      coords  = ( float(i[3]), float(i[4]), float(i[5]), float(i[6]) )
      c_tys  += [ str(i[9])    ]
      c_conf += [ float(i[10]) ]
      c_rect += [ coords       ]

  table = _make_table( t_rect , c_rect )
  _pair_majority(table, t_tys, c_tys, c_conf, False)


  #datatype:
  #t_ind, t_ty, c_ind, c_ty, IOU, conf)









