import sys
import pathlib.PurePath
#custom
import modules.iou_table as iou_table

class miou_element:
  def __init__(self, true_idx=-1, comp_idx=-1, true_ty=None, comp_ty=None, intersection_over_union=0.0, confidence=0.0 ):
    self.t_idx = true_idx
    self.c_idx = comp_idx
    self.t_ty  = true_ty
    self.c_ty  = com_ty
    self.iou   = intersection_over_union
    self.conf  = confidence

  def __str__( self ):
    ret  = ''
    ret += str( self.t_idx ) + ','
    ret += str( self.c_idx ) + ','
    ret += str( self.t_ty  ) + ','
    ret += str( self.c_ty  ) + ','
    ret += str( self.iou   ) + ','
    ret += str( self.conf  )
    return ret

class pvr_element:
  def __init__( self, img='', comp_idx=-1, match=-1, conf=0.0, bool_ ):
    self.image = None
    self.name = None
    self.c_idx = comp_idx
    self.t_match_idx = match
    self.is_true = bool_

    self.conf  = None
    self.acctp = None
    self.accfp = None
    self.accfn = None

    self.prec = None
    self.rec  = None

  def __str__( self ):
    ret  = ''
    ret += str( self.image       ) + ','
    ret += str( self.name        ) + ','
    ret += str( self.c_idx       ) + ','
    ret += str( self.t_match_idx ) + ','
    ret += str( self.is_true     ) + ','

    ret += str( self.conf  ) + ','
    ret += str( self.acctp ) + ','
    ret += str( self.accfp ) + ','
    ret += str( self.accfn ) + ','

    ret += str( self.prec ) + ','
    ret += str( self.rec  )
    return ret


class pvr_table:
  
  def __init__(self, iou):
    self.iou_table = iou
    self.meta_ious = []
    #Image, Name (computed), Confidence, T, F, ACCTP, ACCFP, ACCFN, Precision, Recall,
    self.table = None

    self.missed_truths = [] 
    self.true_comps = []


  def _compute_true_positives( self, th, enforce_ty=None ):
    self.meta_ious.sort( key=lambda x: x.iou )
    self.true_comps = []
    self.missed_truths = list(range( 0, self.iou_table.num_true))
    for m_iou in m_ious:
      tmp = pvr_element( 'img_name, todo', meta_iou.c_idx, meta_iou.t_idx, meta_iou.conf )
      iou = m_iou.iou:
        if enforce_ty:
          print('No.')
          sys.exit(1)

        if iou <= th:
          tmp.is_true = False
        else:
          tmp.is_true = True

        missed_truths.remove( meta_iou.t_idx )
        true_comps.append(    meta_iou.c_idx )
        self.table += tmp


    return self.table

  def _update_table( self, th ):
    #sort and update accumulative stuff, prec/rec, etc.
    self._compute_true_positives( th, False )
    self.table.sort( key=lambda x: x.conf )
    cur_acc_tp=0
    cur_acc_fp=0
    cur_acc_fn=self.iou_table.num_true
    for e in self.table:
      e.



    
  def _make_sorted_iou_table( self ):
      #get nonzero elements
      nz_coords = []
      nz_arr = self.iou_table.table.nonzero()
      for idx in range(len(nz_arr[0])):
        nz_coords.append((nz_arr[0][idx-1], nz_arr[1][idx-1]))

      #Fill data
      for t_idx, c_idx in nz_coords:
        self.meta_ious.append([
          t_idx, c_idx,                        #0,1
          self.iou_table.get_true_ty(t_idx),   #2
          self.iou_table.get_comp_ty(c_idx),   #3
          self.iou_table.get_iou(t_idx,c_idx), #4
          self.iou_table.get_conf(c_idx)])     #5



