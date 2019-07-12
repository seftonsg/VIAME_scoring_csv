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



def _pair_majority( ious, t_tys, c_tys, confs, out, by_class=None ):
  #new name: find matches? uniliniar pairs? 1:1??
  #instead of this... reverse-sort the elements of the array by IOU
  #bin into proper tru/com links 

  #Get all nonzero values
  meta_ious = []
  nz_coords = []
  nz_arr = ious.nonzero()
  for idx in range(len(nz_arr[0])):
    nz_coords.append((nz_arr[0][idx-1], nz_arr[1][idx-1]))

  #Fill data
  for t_idx, c_idx in nz_coords:
    meta_ious.append(
      [t_idx, c_idx,
      t_tys[t_idx], c_tys[c_idx],
      ious[t_idx,c_idx], confs[c_idx]])

  #Multi-sort, starting with least significant
  meta_ious.sort(key=lambda x: x[4]) #iou
  meta_ious.sort(key=lambda x: x[5]) #confidence
  if by_class:
    meta_ious.sort(key=lambda x: x[2]==x[3]) #same class (?)

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


  with open(out, 'w') as o:
    for i in pruned:
      o.write((utils.ltos_csv(i) + '\n'))
  
  unmatched_truths = []
  if by_class:
    print("Not ready yet")
    sys.exit(0)
  else:
    print("none")
  return None










