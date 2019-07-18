import sys
import pathlib
import matplotlib.pyplot as plt
import copy
#custom
import modules.iou_table as iou_table

class miou_element:
  #SPECIAL
  def __init__(self, true_idx=-1, comp_idx=-1, true_ty=None, comp_ty=None, intersection_over_union=0.0, confidence=0.0 ):
    self.t_idx = true_idx
    self.c_idx = comp_idx
    self.t_ty  = true_ty
    self.c_ty  = comp_ty
    self.iou   = intersection_over_union
    self.conf  = confidence

  def __copy__( self ):
    new = type(self)()
    new.t_idx = self.t_idx.copy()
    new.c_idx = self.c_idx.copy()
    new.t_ty  = self.t_ty.copy()
    new.c_ty  = self.c_ty.copy()
    new.iou   = self.iou.copy()
    new.conf  = self.conf.copy()
    return new

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
  #SPECIAL
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

  def __copy__( self ):
    new = type(self)()
    new.image       = copy.copy( self.image )
    new.name        = copy.copy( self.name )
    new.c_idx       = copy.copy(  self.c_idx )
    new.t_match_idx = copy.copy( self.t_match_idx )
    new.is_true     = copy.copy( self.is_true     )

    new.conf  = copy.copy( self.conf  )
    new.iou   = copy.copy( self.iou   )
    new.acctp = copy.copy( self.acctp )
    new.accfp = copy.copy( self.accfp )
    new.accfn = copy.copy( self.accfn )

    new.prec = copy.copy( self.prec )
    new.rec  = copy.copy( self.rec  )

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
  #SPECIAL
  def __init__( self, ious ):
    self.iou_table = ious
    self.meta_ious = []
    self.table = []
    #return self ??? TODO?

  def __copy__( self ):
    new = type(self)(self.iou_table)
    #new.iou_table = copy.copy(self.iou_table)
    new.meta_ious = copy.copy(self.meta_ious)
    new.table     = copy.copy(self.table)
    #new.meta_ious = []
    #new.table = []
    #new._make_meta_ious()
    return new

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
    #used_t = []
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
    self.table.sort( key=lambda x: x.conf )
    self.table = self.table[::-1]
    self.table = self._filter_dupes( self.table )

    self._update_acc_stats()
    self._update_table_pvr( th )
    return None

  def _get_best_precision( self, recth ):
    best_p = 0.0
    for e in self.table:
      if e.rec < recth:
        continue
      else:
        if best_p < e.prec:
          best_p = e.prec
    return best_p

  def _get_COCOsmall( self ):
    new_iou = copy.copy(self.iou_table)
    new_iou.comp_rects = []
    for e in self.iou_table.comp_rects:
      #32 ^ 2
      if e[0].area() < 1024:
        new_iou.comp_rects.append(e)
    new_iou.num_comp = len(new_iou.comp_rects)
    new_iou.run_table()
    return new_iou

  def _get_COCOmedium( self ):
    new_iou = copy.copy(self.iou_table)
    new_iou.comp_rects = []
    for e in self.iou_table.comp_rects:
      #32 ^ = 1024, 96^2 = 8832
      if (1024 <= e[0].area()) and (e[0].area() < 8832):
        new_iou.comp_rects.append(e)
    new_iou.num_comp = len(new_iou.comp_rects)
    new_iou.run_table()
    return new_iou

  def _get_COCOlarge( self ):
    new_iou = copy.copy(self.iou_table)
    new_iou.comp_rects = []
    for e in self.iou_table.comp_rects:
      #96^2 = 8832
      if 8832 <= e[0].area():
        new_iou.comp_rects.append(e)
    new_iou.num_comp = len(new_iou.comp_rects)
    new_iou.run_table()
    return new_iou

  #PUBLIC
  def make_graph( self, save_loc=None, title='' ):
    xs = []
    ys = []
    for i in self.table:
      xs.append( i.rec  )
      ys.append( self._get_best_precision(i.rec))
      #ys.append( i.prec )

    plt.clf()
    plt.plot( xs, ys, 'r' )
    #plt.title()
    plt.ylabel( 'Precision' )
    plt.xlabel( 'Recall'    )
    plt.axis( [0.0,1.0,0.0,1.0] )

    if save_loc:
      plt.savefig( save_loc )
    else:
      plt.show()

    return None

  def get_AP11_short( self, th ):
    self._make_sorted_iou_table( th )
    highest_r = 0
    for i in self.table:
      if i.rec > highest_r:
        highest_r = i.rec
    ap = 0.0
    for i in range(0,11):
      ap += self._get_best_precision( i/10.0 * highest_r )
    ap = ap / 11.0
    return ap

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

  def get_APsm( self, th=0.50 ):
    #small medium large
    #<32   32<96  96<   (area)
    tmp_PVRtable = type(self)(self._get_COCOsmall())
    APsm = tmp_PVRtable.get_AP11( th )
    return APsm

  def get_APmd( self, th=0.50 ):
    #small medium large
    #<32   32<96  96<   (area)
    tmp_PVRtable = type(self)(self._get_COCOmedium())
    APmd = tmp_PVRtable.get_AP11( th )
    return APmd

  def get_APlg( self, th=0.50 ):
    #small medium large
    #<32   32<96  96<   (area)
    tmp_PVRtable = type(self)(self._get_COCOlarge())
    APlg = tmp_PVRtable.get_AP11( th )
    return APlg

  def get_mAP( self ):
    mAP = 0.0
    for i in range(50, 100, 5):
      mAP += self.get_AP11( i/100 )
    mAP = mAP / 10
    return mAP

  def get_num_above_th( self, th ):
    n = 0
    self._make_sorted_iou_table( th )
    for i in self.table:
      if i.is_true:
        n += 1
    return n

  def get_f1( self, th ):
    self._make_sorted_iou_table( th )
    p = self.table[-1].prec
    r = self.table[-1].rec
    if (p+r) == 0:
      return -1.0
    f = (2.0*p*r)/(p+r)
    return f


def write_res( dst, pvrs ):
  with open(dst, 'a') as d:
    mAP  = pvrs.get_mAP (    )
    AP50 = pvrs.get_AP11(0.50)
    AP75 = pvrs.get_AP11(0.75)
    APsm = pvrs.get_APsm(0.00)
    APmd = pvrs.get_APmd(0.00)
    APlg = pvrs.get_APlg(0.00)
    f150 = pvrs.get_f1  (0.50)
    f175 = pvrs.get_f1  (0.75)
    d.write( f'{"  mAP ":=<30}> {mAP:<.5f}'    + '  ( COCO Primary        )\n' )
    d.write( f'{"  AP50 ":=<30}> {AP50:<.5f}'  + '  ( Pascal VOC          )\n' )
    d.write( f'{"  AP75 ":=<30}> {AP75:<.5f}'  + '  ( Strict              )\n' )
    d.write( f'{"  APsm ":=<30}> {APsm:<.5f}'  + '  (         area < 32^2 )\n' )
    d.write( f'{"  APmd ":=<30}> {APmd:<.5f}'  + '  ( 32^2 <= area < 92^2 )\n' )
    d.write( f'{"  APlg ":=<30}> {APlg:<.5f}'  + '  ( 92^2 <= area        )\n' )
    d.write( f'{"  F1-50 ":=<30}> {f150:<.5f}' + '  \n' )
    d.write( f'{"  F1-75 ":=<30}> {f175:<.5f}' + '  \n' )
    d.write( '\n' + '-'*40 + '\n' )
    #print(len(pvrs.table))
  return None

def get_results( img_names, args ):
  """ Function
      get_results( img_names:list args:?ty ) :None
      Produces the results and writes them to the
      results directory (args.output / args.results)
  """ 
  hum_path   = args.results / 'results.txt'
  graph_path = args.results / 'PvR_graph.svg'

  #Do 'all' first

  with open(hum_path, 'w') as d:
    #clean the file
    d.write('\n')
    d.write( '\n' + '-'*40 + '\n' )

  #Do by image
  for i in img_names:
    true_path   = args.output / i / ('truth_' + i + '.csv')
    comp_path   = args.output / i / ('computed_' + i + '.csv')
    ious = iou_table.IoU_table( true_path, comp_path )
    ious.run()
    pvrs = PVRtable(ious)

    with open(hum_path, 'a') as d:
      d.write( 'Metrics for ' + i + ':' + '\n')
    write_res(hum_path, pvrs)

    sub_graph_path = args.output / i / ('PvR_' + i + '.svg')
    pvrs.get_AP11(0.50) #update pvrs to have proper data for graph
    pvrs.make_graph(sub_graph_path)
  
  comp_path  = args.output / 'all' / ('computed_all.csv')
  comp_path  = args.output / 'all' / ('truth_all.csv')
  ious = iou_table.IoU_table( true_path, comp_path )
  ious.run()
  pvrs = PVRtable(ious)

  with open(hum_path, 'a') as d:
    d.write( 'Overall Evaluation Metrics:' + '\n' )
  write_res(hum_path, pvrs)

  pvrs.get_AP11(0.50) #update pvrs to have proper data for graph
  pvrs.make_graph(graph_path)

  return None