import os
import re
import sys
import shutil
import argparse
import subprocess
import pathlib 


#Eventually add support to replace the names
# of "epoch_x" with class type?
#Worthwhile to set standard from "epoch_x" 
# to "epoch_x_class" for multiclass detectors.
if __name__ == "__main__":
	imgs = []
	with open('labels.txt') as i:
		for l in i:
			l = l.split('\n')
			imgs += [l[0]]
	print(imgs)
	for i in imgs:
		with open('all.csv') as a:
			with open( (i+'.csv'), 'w') as o:
				for l in a:
					tl = l.split(',')
					if tl[9] == i:
						o.write(l)
		print('  Did: ', i)
	print('Done')
