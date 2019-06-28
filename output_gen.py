################################
#  Sage Sefton
#  Functions for generating and
#  formatting outputs of the
#  VIAME multi-scorer
#  2019 06 26
################################

import re
import os
import pathlib
import matplotlib.pyplot as plt
#Custom
import utils


#output 
def _print_human_results( score, roc, dst, wipe=False ):
  """ Function
      print_human_results( score:pathlib.PurePath,
        roc:pathlib.PurePath, dst:pathlib.PurePath, 
        wipe:bool 
        ) :None
      Prints a human-readable version of the results files.
      Writes this data to dst.
  """
  #Define a variable for the amount of data printed?
  #Make sure to append, or wipe clean
  #Takes full directory-like objects
  if wipe and os.path.exists( dst ):
    os.remove( dst )

  #Parentheticals are group(1) of re.search(l)
  rex_PD    = re.compile(      'Detection-Pd: (.*)' )
  rex_FA    = re.compile(      'Detection-FA: (.*)' )
  rex_PFA   = re.compile(     'Detection-PFA: (.*)' )
  rex_TrDet = re.compile(   'n-gt-detections: (.*)' )
  rex_CoDet = re.compile( 'n-comp-detections: (.*)' )

  with open( score ) as s:
    for l in s:
      if rex_TrDet.search(l):
        n_detTrue = int(rex_TrDet.search(l).group(1))
      if rex_CoDet.search(l):
        n_detComp = rex_CoDet.search(l).group(1)

      if rex_PD.search(l):
        p_TP = float(rex_PD.search(l).group(1))
      if rex_PFA.search(l):
        p_FP = float(rex_PFA.search(l).group(1))
      #if rex_PTN.search(l):
      #if rex_PFN.search(l):
      
      if rex_FA.search(l):
        n_FA = int(l[16:])

  with open( roc ) as r:
    l = r.read(256).split(';')
    n_TP = l[4][5:]
    n_FP = l[5][5:]
    n_TN = l[6][5:]
    n_FN = l[7][5:]

  with open( dst, 'a' ) as d:
    d.write( '\n' + '-'*40 + '\n' )
    d.write('Data for ' + score.parts[-2] + ':\n' )
    d.write( f'{"  # Computed Detections ":=<30}> {n_detComp:<10}' + '\n')
    d.write( f'{"  # True Detections ":=<30}> {n_detTrue:<10}' + '\n')
    d.write('\n')
    d.write( f'{"  # True  Positives (TP) ":=<30}> {n_TP:<10}' + '\n')
    d.write( f'{"  # False Positives (FP) ":=<30}> {n_FP:<10}' + '\n')
    d.write( f'{"  # True  Negatives (TN) ":=<30}> {n_TN:<10}' + '\n')
    d.write( f'{"  # False Negatives (FN) ":=<30}> {n_FN:<10}' + '\n')
    #d.write( f'{"  # False Positives ":=<30}> {n_FA:<10}' + '\n' )
    d.write('\n')
    d.write( f'{"  P {True Positive} ":=<30}> {p_TP:<10.5f}' + '\n' )
    d.write( f'{"  P {False Positive} ":=<30}> {p_FP:<10.5f}' + '\n' )
      #print("none")
  return None

#CSV
def _make_confidence_name_table( computed ):
  """ Internal Function
      _make_confidence_name_table( 
        computed:pathlib.PurePath 
        ) :list<(float, string)>
      Given a computed-annotations csv file, returns
      a lookup table of confidence and annotation name.
  """
  table = []
  #confidence to #, or to coordinates?
  with open( computed ) as c:
    for l in c:
      l = l.strip().split(',')
      if len(l[0]) > 0 and l[0][0] == '#':
        continue
      if len(l[0]) == 0:
        continue
      entry = [(float(l[10]), l[0])]
      table += entry
  
  return table

#CSV
def _make_result_csv( score, roc, dest, dictionary=None, wipe=False ):
  """ Internal Function
      _make_result_csv( score:pathlib.PurePath
        roc :pathlib.PurePath
        dest:pathlib.PurePath
        dictionary:list<float, str>
        wipe:bool
      ) :list
      Given the output files, creates a table of each annotation,
      marks if it's a true or false positive and counts the
      accumulation of TP/FP/TN/FN (though the negatives need 
      some work).  This is mostly a parser of the csv file.
      Returns said table, who's elements are shown below.
  """
  if wipe and os.path.exists( dest ):
    os.remove( dest )

  table = []
  #Image, Name, Confidence, T, F, ACCTP, ACCFP, ACCTN, ACCFN, Precision, Recall

  with open(roc) as r:
    previous = [None] * 11
    for l in r:
      l = l.strip().split(';')
      conf = float(l[0][16:])

      #TODO: convert to enumerated?  dictionary-like?
      entry = [None] * 11
      entry[ 0] = score.parts[-2]
      #entry += [conf]
      entry[ 2] = conf
      entry[ 3] = 0
      entry[ 4] = 0
      entry[ 5] = int(l[4][5:])
      entry[ 6] = int(l[5][5:])
      entry[ 7] = int(l[6][5:])
      entry[ 8] = int(l[7][5:])


      if not previous[0]:
      #Check if TP, FP, etc.
        d_truth = 0
        d_false = 0
      else:
        d_truth = previous[ 5] - entry[ 5]
        d_false = previous[ 6] - entry[ 6]
      while d_truth > 0 or d_false > 0: #or tndiff > 0 or fndiff > 0:
        tmp = entry.copy()
        if d_truth > 0:  #true
          tmp [ 3]  = 1
          tmp [ 5] += d_truth
          tmp [ 8] -= d_truth #decriment FN counter=
          d_truth  -= 1
        elif d_false > 0: #false
          tmp [ 4]  = 1
          tmp [ 6] += d_false
          tmp [ 7] -= d_false #decriment TN counter
          #tmp [7] -= 1
          d_false  -= 1
        table += [tmp]
      previous = entry.copy()

    table = table[::-1]
    #Match the conf levels to the annotation name. Picks largest that is < conf
    #It would be fastest to sort the dictionary list then do a 1:1 match.  No double loop needed
    if dictionary:
        for e in table:
          idx = 0
          best = (0,0)
          for i in range(len(dictionary)):
            if dictionary[i][0] < e[2]:
              if dictionary[i][0] > best[0]:
                best = dictionary[i]
                idx = i
          e[1] = best[1]
          e[2] = best[0]
          del dictionary[idx]
  #  for i in table:
  #    print(i)
  #  print(' Table Len: ' + str(len(table)))
  #  print(' Unused Dict (' + str(len(dictionary)) + '): ')
  #  for i in dictionary:
  #    print(i)
  #  print("\n\n\n")
  return table

#CSV
def _update_tfpn( data, negatives ): #update true and false pos and neg, idk what else to call this function.
  """ Internal Function
      _update_tfpn( data:list, negatives:(int,int) 
      ) :list
      Given a list of annotation objects, this recalculates
      the accumulated TP,FP,TN,FN, and the Precision and
      Recall metrics.  Returns said data list, but if this
      is pass by reference, the return is unecessary.
  """
  TP = 0
  FP = 0
  TN = negatives[0]
  FN = negatives[1]
  for i in data:
    if i[3]:
      TP += 1
      FN -= 1
    elif i[4]:
      FP += 1  
      TN -= 1
    i[ 5] = TP  #ACC TP
    i[ 6] = FP  #ACC FP
    i[ 7] = TN   #TN
    i[ 8] = FN   #FN
    i[ 9] = TP / (TP+FP)#Precision
    i[10] = TP / (TP+FN)#Recall
  return data

#CSV
def _combine_result_csv( data, negatives ):
  """ Internal Function
      _combine_result_csv( data:list, negatives:(int,int)
      ) :list
      Given an unordered list of annotation data, and the
      caps for true/false negatives.  This reorganizes
      the data, updates the accumulated data #s (with
      a helper function), and returns the sorted and 
      recalculated list.
  """
  tupledata = []
  for i in data:
    tupledata += [( i[2], i )]
  tupledata.sort()
  tupledata = tupledata[::-1]
  
  newdat = []
  for i in tupledata:
    newdat += [i[1]]

  newdat = _update_tfpn( newdat, negatives )

  return newdat

#CSV
def _print_csv( data, dest ):
  """ Internal Function
      _print_csv( data:list, dest:pathlib.PurePath ) :None
      Prints the data to the destination after formatting.
      This is its own function.  It uses utils for now,
      but I may remove or alter parts of the data before
      sending them to ltos_csv, hence the function.
  """
  #print('Writing to: ' + str(dest))
  with open(dest, 'w') as d:
    for i in data:
      #remove some parts of i?
      d.write(utils.ltos_csv(i) + '\n')
  return None

#PLOT
def _simplify_data( xs, ys ):
  """ Internal Function
      _simplify_data( xs:list, ys:list) :list, list
      Given the xs and ys for all points, creates a 
      square-like wave that drops only to the next
      highest point.  Calculations are done on an
      inverted list to help find local maxima.
      Note: does not add 0,0 and 1,0.
  """
  nxs  = [xs[-1]]
  nys  = [ys[-1]]
  curr = ys[-1]
  for i in range(len(ys))[::-1]:
    if ys[i] > curr:
      curr = ys[i]
      #add a point level to the old one
      nxs += [xs[i]]
      nys += [nys[-1]]
      #add new highest point
      nxs += [xs[i]]
      nys += [ys[i]]

  nxs += [xs[0]]
  nys += [ys[0]]

  #for i in range(len(nxs)):
  #  print(f'{nxs[i]:.5f}, {nys[i]:.5f}')
  

  return nxs, nys


#PLOT
def _plot_pvr( data, dest=None ):
  """ 
      plot_pvr( data: , dest:pathlib.PurePath ) :None
      Plots the Precision-Recall curve from the data
      and saves the graph to dest.
  """
  xs = []
  ys = []
  #n = []

  for i in data:
    xs += [i[10]]
    ys += [i[ 9]]
    #n += [(i[9],i[10])]
  xs, ys = _simplify_data(xs, ys)
  plt.plot(xs,ys,color='red')
  #plt.plot(n,'rx')
  plt.ylabel('Precision')
  plt.xlabel('Recall')
  #plt.fill([0]+xs+[1],[0]+ys+[0])
  plt.axis([0.0,1.0,0.0,1.0])
  if dest:
    plt.savefig(dest)
  else:
    plt.show()
  return None

#output
def get_results( img_names, args ):
  """ Function
      get_results( img_names:list args:?ty ) :None
      Produces the results and writes them to the
      results directory (args.output / args.results)
  """
  roc_path = args.output / 'all' / 'output_roc.txt'
  sco_path = args.output / 'all' / 'output_score_tracks.txt'
  com_path = args.output / 'all' / 'computed_all.csv'

  hum_path   = args.results / 'results.txt'
  csv_path   = args.results / 'precr.csv'
  graph_path = args.results / 'PvR_graph.svg'

  #Do 'all' first
  #print_human_results( sco_path, roc_path, hum_path, True )
      #1: get human-readable data and print to args.res_file=

  data = []
  for i in img_names:
    roc_path = args.output / i / 'output_roc.txt'
    sco_path = args.output / i / 'output_score_tracks.txt'
    com_path = args.output / i / ('computed_' + i + '.csv')
    _print_human_results( sco_path, roc_path, hum_path )
    dictionary = _make_confidence_name_table( com_path )
    data += _make_result_csv( sco_path, roc_path, csv_path, dictionary )

  roc_path = args.output / 'all' / 'output_roc.txt'
  sco_path = args.output / 'all' / 'output_score_tracks.txt'
  com_path = args.output / 'all' / ('computed_all.csv')
  _print_human_results( sco_path, roc_path, hum_path )
  dictionary = _make_confidence_name_table( com_path )
  tmp = _make_result_csv( sco_path, roc_path, csv_path, dictionary )[0]

  total_TN = tmp[7]
  total_FN = tmp[8]
  #Alter negatives based on the first entry:
  #Note that the first entry of the data list subtracts 1 from
  # one of the negatives (depending on if it's a TP or FP), 
  # so it will always appear one less than the final count of 
  # the positives.
  if tmp[3]:
    total_FN += 1
  elif tmp[4]:
    total_TN += 1

  data = _combine_result_csv( data, (total_TN, total_FN) )
  header = ['Image Name','Annotation Name','Confidence Score','True','False','# True Positives','# False Positives','# True Negatives','# False Negatives','Precision','Recall']
  types = ['str','str','float','bool','bool','int','int','int','int','float','float']
  pretty_data = [header] + [types] + data
  #for i in data:
  #  print(i)

  #TODO: rename the file for csv
  _print_csv( pretty_data,   csv_path )
  _plot_pvr(         data, graph_path )

  return None



