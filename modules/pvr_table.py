import sys
import pathlib
import matplotlib.pyplot as plt
#custom
import modules.iou_table as iou_table

class miou_element:
  def __init__(self, true_idx=-1, comp_idx=-1, true_ty=None, comp_ty=None, intersection_over_union=0.0, confidence=0.0 ):
    self.t_idx = true_idx
    self.c_idx = comp_idx
    self.t_ty  = true_ty
    self.c_ty  = comp_ty
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
  def __init__( self, img='', nm='', comp_idx=-1, match=-1 ):
    self.image = img
    self.name = nm
    self.c_idx = comp_idx
    self.t_match_idx = match
    self.is_true = False

    self.conf  = None
    self.iou   = None
    self.acctp = None
    self.accfp = None
    self.accfn = None

    self.prec = None
    self.rec  = None

  def __str__( self ):
    ret  = ''
    ret += "Image: "   + str( self.image       ) + ','
    ret += "Name: "    + str( self.name        ) + ','
    ret += "c_idx: "   + str( self.c_idx       ) + ','
    ret += "t_match: " + str( self.t_match_idx ) + ','
    ret += "Matched: " + str( self.is_true     ) + ','

    ret += "Conf: " + str( self.conf  ) + ','
    ret += "IoU: "  + str( self.iou   ) + ','
    ret += "TPs: "  + str( self.acctp ) + ','
    ret += "FPs: "  + str( self.accfp ) + ','
    ret += "FNs: "  + str( self.accfn ) + ','

    ret += "Prec: " + str( self.prec ) + ','
    ret += "Rec: "  + str( self.rec  )
    return ret

  def __repr__( self ):
    ret  = ''
    ret += str( self.image       ) + ', '
    ret += str( self.name        ) + ', '
    ret += str( self.c_idx       ) + ', '
    ret += str( self.t_match_idx ) + ', '
    ret += str( self.is_true     ) + ', '

    ret += str( self.conf  ) + ', '
    ret += str( self.iou   ) + ', '
    ret += str( self.acctp ) + ', '
    ret += str( self.accfp ) + ', '
    ret += str( self.accfn ) + ', '

    ret += str( self.prec ) + ', '
    ret += str( self.rec  )
    return ret

class PVRtable:
  
  def __init__( self, ious ):
    self.iou_table = ious
    self.meta_ious = []
    #------Image, Name (computed), Confidence, T, F, ACCTP, ACCFP, ACCFN, Precision, Recall,
    self.table = []

    #self.missed_truths = [] 
    #self.true_comps = []

  #PRIVATE
  def _make_meta_ious( self ): 
    #get nonzero elements
    nz_coords = []
    meta_ious = []
    nz_arr = self.iou_table.table.nonzero()
    for idx in range(len(nz_arr[0])):
      nz_coords.append((nz_arr[0][idx-1], nz_arr[1][idx-1]))

    for t_idx, c_idx in nz_coords:
      tmp = miou_element(
        t_idx, c_idx,                        #0,1
        self.iou_table.get_true_ty(t_idx),   #2
        self.iou_table.get_comp_ty(c_idx),   #3
        self.iou_table.get_iou(t_idx,c_idx), #4
        self.iou_table.get_conf(c_idx))      #5
      meta_ious.append(tmp)
    return(meta_ious)

  def _compute_true_positives( self, th, enforce_ty=None ):
    table = []
    true_comps = []

    #print('Len meta_ious: ', str(len(self.meta_ious)))
    used_comp = []
    for m_iou in self.meta_ious:
      tmp = pvr_element( 'img', 'name-', m_iou.c_idx, m_iou.t_idx )
      iou = m_iou.iou
      if enforce_ty:
        print('No.')
        sys.exit(1)

      if iou >= th:
        tmp.is_true = True

      tmp.conf  = m_iou.conf
      tmp.iou   = iou
      used_comp.append(m_iou.c_idx)

      table.append(tmp)

    for e in range(0, self.iou_table.num_comp):
      if e not in used_comp:
        tmp = pvr_element( 'img', 'name-', e, -1,)
        tmp.iou = 0
        tmp.conf = self.iou_table.comp_rects[e][1]
        table.append(tmp)

    return table

  def _update_acc_stats( self ):
    missed_truths = list(range(0, self.iou_table.num_true))
    #false_pos = list(range(0, self.iou_table.num_comp))
    used_comp = []
    ncomp = self.iou_table.num_comp
    acctp = 0
    accfp = 0
    accfn = len(missed_truths)
    for i in self.table:
      #acctp
      if i.is_true:
        acctp +=  1
        accfn += -1
      #accfp:
      else:
        accfp += 1

      i.acctp = acctp
      i.accfp = accfp
      i.accfn = accfn

  def _update_table_pvr( self, th ):
    #sort and update accumulative stuff, prec/rec, etc.
    for e in self.table:
      e.prec = e.acctp / (e.acctp + e.accfp)
      e.rec  = e.acctp / (e.acctp + e.accfn)

  def _filter_dupes( self, table ):
    ntable = []
    used_c = []
    used_t = []
    for i in table:
      if i.c_idx not in used_c:
        #if i.t_idx not in used_t:
        ntable.append(i)
        used_c.append(i.c_idx)
        #  used_t.append(i.t_matched_idx)
    return ntable
    
  def _make_sorted_iou_table( self, th ):
    #Fill data
    self.meta_ious = self._make_meta_ious()
    self.table = self._compute_true_positives( th, False )

    #self.table.sort(key=lambda x: x.iou)
    

    self.table.sort(key=lambda x: x.conf)
    self.table = self.table[::-1]
    self.table = self._filter_dupes( self.table )
    #for i in self.table:
    #  print(i)
    #sys.exit(0)

    self._update_acc_stats()
    self._update_table_pvr( th )
    # for i in self.table:
    #   print(i.is_true, i.c_idx, i.conf, i.acctp, i.accfp, i.accfn, i.prec, i.rec)

  def _get_best_precision( self, recth ):
    best_p = 0.0
    for e in self.table:
      if e.rec < recth:
        continue
      else:
        if best_p < e.prec:
          best_p = e.prec
    return best_p

  def make_graph( self ):
    xs = []
    ys = []

    for i in self.table:
      xs.append( i.rec  )
      ys.append( self._get_best_precision(i.rec))
      #ys.append( i.prec )

    plt.plot(xs, ys, 'r')
    plt.ylabel( 'Precision' )
    plt.xlabel( 'Recall'    )
    plt.axis([0.0,1.0,0.0,1.0])
    plt.show()
    return None


  #PUBLIC
  def get_AP11( self, th ):
    self._make_sorted_iou_table( th )
    ap = 0.0
    for i in range(0,11):
      ap += self._get_best_precision( i/10.0 )
    ap = ap / 11.0
    return ap

  def get_AP101( self, th ):
    self._make_sorted_iou_table( th )
    ap = 0.0
    for i in range(0,101):
      ap += self._get_best_precision( i/100.0 )
    ap = ap / 101.0
    return ap

  def get_mAP( self ):
    mAP = 0.0
    for i in range(50, 100, 5):
      mAP += self.get_AP11( i/100 )
    mAP = mAP / 10
    return mAP

  def get_num_above_th( self, th ):
    n = 0
    self._make_sorted_iou_table( th )
    #print(self.table)
    for i in self.table:
      #print( i.c_idx, i.t_match_idx, i.is_true )
      if i.is_true:
        n += 1
    return n







