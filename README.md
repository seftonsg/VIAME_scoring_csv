# VIAME Score CSV

This is a command-line application that calculates COCO and PASCAL style metrics given a set of true and computed annotations.  Currently, the program only supports CSV files formatted the way VIAME accepts and produces them.  Other detection file formats may be supported in the future.

## Roadmap  
I intend to update this program in my spare time.  These are the improvements I would like to make, in no particular order:
 * Conversion to C++
 * habcam and mouss support
 * graphics for example dummy tests

## Usage  
This scoring tool requires three pieces of information: 
 1. A file of the true (known) "detections" (called "true annotations")
 2. A file of the computed detections
 3. A directory containing the test-set images  
   ___OR___  
   A file listing the names of those images  

### Arguments  
All input arguments are required.  The output arguments are mostly for user organization and ease-of-use.  
__Note:__ This program supports python PurePath. Any argument _except for_ `-results` can be a:
 - filename
 - relative path
 - full path

#### Inputs  
|     COMMAND |                                   DESCRIPTION |
|-------------|-----------------------------------------------|
|    `-truth` |      Input filename for true detections file. |
| `-computed` |  Input filename for computed detections file. |
|   `-images` |      Input directory or list file for images. |

\* `-images` can take a directory of images ___OR___ a file listing the names of those images

#### Outputs  
|     COMMAND |                                   DESCRIPTION |
|-------------|-----------------------------------------------|
|   `-output` |                Path for the output directory. |
|  `-results` | Name of the results folder in the output dir. |

## Interpretation  



**This program was written as part of an internship provided by the Ernest F. Hollings Scholarship**  
**Written by:** Sage Sefton  
**Advised by:** George "Randy" Cutter  
**Special thanks:** Beth Jaime, Matt Dawkins, and the Hollings Scholarship team