__author__ = 'Anand M'

import argparse, datetime, os


############# parse arguments ########
parser = argparse.ArgumentParser(
    description="wrapper script for STAR aligner. Assumes STAR is installed under path and accessible.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# Positional arguments
parser.add_argument('genomeDir', help='path to genome directory')
parser.add_argument('readFilesIn', help='path/to/read1 [path/to/read2]', nargs='+')

# file reading and multithreading options
parser.add_argument('--runThreadsN', help='Number of threads to use for mapping', default=4, type=int, dest='threads')
parser.add_argument('--outFileNamePrefix',
                    help='output files name prefix (including full or relative path). Can only be defined on the command line.',
                    default='myStar', type=str, dest='prefix')
parser.add_argument('--genomeLoad', help='mode of shared memory usage for the genome files', default='NoSharedMemory',
                    dest='mem', choices=['LoadAndKeep', 'LoadAndRemove', 'LoadAndExit', 'Remove', 'NoSharedMemory'])
parser.add_argument('--twopassMode', help='2-pass mapping mode.', choices=['None', 'Basic'], default='None', type=str,
                    dest='twoPass')
parser.add_argument('--rg', help='read group within quotes "RG\\tID:id\\tSM:sample\\tLB:lib" ',
                    default="@RG\\tID:id\\tSM:sample\\tLB:lib", type=str, dest="rg")


##  Read-Parameters
inputReads = parser.add_argument_group('Read Parameters')

inputReads.add_argument('--readFilesCommand', help='uncomression method to use', default='zcat', dest='zip',
                        choices=['-', 'zcat', 'bzcat'])
inputReads.add_argument('--clip3pNbases',
                        help='number(s) of bases to clip from 3p of each mate. If one value is given, it will be assumed the same for both mates.',
                        dest='clip3', type=int, default=0)
inputReads.add_argument('--clip5pNbases',
                        help='number(s) of bases to clip from 5p of each mate. If one value is given, it will be assumed the same for both mates.',
                        dest='clip5', type=int, default=0)
inputReads.add_argument('--clip3pAdapterSeq',
                        help='adapter sequences to clip from 3p of each mate. If one value is given,it will be assumed the same for both mates.',
                        dest='clipAdapt', type=str, default='-')

# Splice junctions database
junction = parser.add_argument_group('splice junction options')

junction.add_argument('--sjdbGTFfile', help="string: path to the GTF file with annotations", default='-',
                      dest='sjdbGTFfile', type=str)
junction.add_argument('--sjdbGTFchrPrefix',
                      help="string: prefix for chromosome names in a GTF file (e.g. chr for using ENSMEBL annotations with UCSC geneomes)",
                      default='-', dest='sjdbPrefix', type=str)

## Quantification of Annotations
quant = parser.add_argument_group('Quantification of Annotation')

quant.add_argument('--quantMode', default='-', dest='quant', choices=['-', 'TranscriptomeSAM', 'GeneCounts'],
                   help='quantification of SJDB file')

## Output SAM and BAM options

output = parser.add_argument_group('Output: SAM and BAM')

output.add_argument('--outSAMtype', dest='outType', choices=['SAM', 'BAM', 'None'], default='BAM', type=str,
                    help='output type')
output.add_argument('--sortType', dest='sortType', choices=['Unsorted', 'SortedByCoordinate'], default='Unsorted',
                    type=str, help='sort order')
output.add_argument('--outSAMstrandField', dest='strandField', choices=['None', 'intronMotif'], default='intronMotif',
                    type=str, help='sam strand field type')
output.add_argument('--outFilterMultimapNmax', dest='maxAlign', default=10, type=int,
                    help='read alignments will be output only if the read maps fewer than this value,otherwise no alignments will be output')
output.add_argument('--outWigType', dest='outWig', default='None', type=str,choices = ['None', 'bedGraph', 'wiggle'],
                    help="type of signal output, bedGraph or wiggle")
output.add_argument('--outWigStrand', dest='outWigStrand', default='Unstranded', type=str,choices = ['Unstranded', 'Stranded'],
                    help="strandedness of wiggle/bedGraph output")
output.add_argument('--outWigNorm', dest='outWigNorm', default='RPM', type=str,choices = ['RPM', 'None'],
                    help="type of normalization for the signal")

args = parser.parse_args()


# input files
files = ''

if len(args.readFilesIn) <= 2:
    for f in args.readFilesIn:
        files = files + ' ' + f
else:
    print("Please enter paired end files or interleaved single file. More than two input files entered !")
    quit()

# sort type
samsort = args.outType + ' ' + args.sortType

# sam rg
args.rg = str.split(args.rg, '\\t')
dt = str(datetime.date.today().isoformat())
rgattr = ' '.join(args.rg[1:]) + ' ' + 'DT:' + dt

#star command
starCommand = 'STAR --outFileNamePrefix %s --outSAMtype %s ' \
              "--genomeLoad %s --twopassMode %s " \
              "--clip3pNbases %d --clip5pNbases %d --clip3pAdapterSeq %s " \
              "--sjdbGTFfile %s --sjdbGTFchrPrefix %s --quantMode %s --outFilterMultimapNmax %d " \
              "--outSAMstrandField %s --outSAMattrRGline %s --outWigType %s  --outWigStrand %s -outWigNorm %s --runThreadN %d --readFilesCommand %s --genomeDir %s --readFilesIn %s" % (
                  args.prefix, samsort, args.mem, args.twoPass, args.clip3, args.clip5, args.clipAdapt,
                  args.sjdbGTFfile, args.sjdbPrefix, args.quant, args.maxAlign,
                  args.strandField, rgattr, args.outWig, args.outWigStrand, args.outWigNorm ,args.threads, args.zip, args.genomeDir, files)

print("Effective STAR command:\n")
print(starCommand)

print '\n[%s]\tAlignment started. \n' % datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
#os.system(starCommand)
print '[%s]\tAlignment finished. \n' % datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

logFile = 'cat ' + args.prefix + 'Log.final.out'


