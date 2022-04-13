from depixlib.LoadedImage import *
from depixlib.Rectangle import *
from depixlib.functions import *

import argparse
import logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


usage = '''
	像素化的矩形必须被剪掉，以只包含像素化的矩形。 
	模式搜索图像通常是De Bruijn预期字符序列的截图，
在与原始截图相同的编辑器和文本大小的机器上制作的像素化。
'''

parser = argparse.ArgumentParser(description = usage)
parser.add_argument('-p', '--pixelimage', help = '带有像素矩形的图像路径', required=True)
parser.add_argument('-s', '--searchimage', help = '路径图像与模式搜索', required=True)
parser.add_argument('-a', '--averagetype', help = 'Type of RGB average to use (linear or gammacorrected)',
	default='gammacorrected', choices=['gammacorrected', 'linear'])
parser.add_argument('-b', '--backgroundcolor', help = 'Original editor background color in format r,g,b', default=None)
parser.add_argument('-o', '--outputimage', help = 'Path to output image', nargs='?', default='output.png')
args = parser.parse_args()

pixelatedImagePath = args.pixelimage
searchImagePath = args.searchimage
if args.backgroundcolor != None:
	editorBackgroundColor = tuple([int(x) for x in args.backgroundcolor.split(",")])
else:
	editorBackgroundColor = args.backgroundcolor
averageType = args.averagetype


logging.info("Loading pixelated image from %s" % pixelatedImagePath)
pixelatedImage = LoadedImage(pixelatedImagePath)
unpixelatedOutputImage = pixelatedImage.getCopyOfLoadedPILImage()

logging.info("Loading search image from %s" % searchImagePath)
searchImage = LoadedImage(searchImagePath)


logging.info("Finding color rectangles from pixelated space")
# fill coordinates here if not cut out
pixelatedRectange = Rectangle((0, 0), (pixelatedImage.width-1, pixelatedImage.height-1))


pixelatedSubRectanges = findSameColorSubRectangles(pixelatedImage, pixelatedRectange)
logging.info("Found %s same color rectangles" % len(pixelatedSubRectanges))

pixelatedSubRectanges = removeMootColorRectangles(pixelatedSubRectanges, editorBackgroundColor)
logging.info("%s rectangles left after moot filter" % len(pixelatedSubRectanges))

rectangeSizeOccurences = findRectangleSizeOccurences(pixelatedSubRectanges)
logging.info("Found %s different rectangle sizes" % len(rectangeSizeOccurences))
if len(rectangeSizeOccurences) > max(10, pixelatedRectange.width * pixelatedRectange.height * 0.01):
	logging.warning("Too many variants on block size. Re-pixelating the image might help.")

logging.info("Finding matches in search image")
rectangleMatches = findRectangleMatches(rectangeSizeOccurences, pixelatedSubRectanges, searchImage, averageType)

logging.info("Removing blocks with no matches")
pixelatedSubRectanges = dropEmptyRectangleMatches(rectangleMatches, pixelatedSubRectanges)


logging.info("Splitting single matches and multiple matches")
singleResults, pixelatedSubRectanges = splitSingleMatchAndMultipleMatches(pixelatedSubRectanges, rectangleMatches)

logging.info("[%s straight matches | %s multiple matches]" % (len(singleResults), len(pixelatedSubRectanges)))

logging.info("Trying geometrical matches on single-match squares")
singleResults, pixelatedSubRectanges = findGeometricMatchesForSingleResults(singleResults, pixelatedSubRectanges, rectangleMatches)

logging.info("[%s straight matches | %s multiple matches]" % (len(singleResults), len(pixelatedSubRectanges)))

logging.info("Trying another pass on geometrical matches")
singleResults, pixelatedSubRectanges = findGeometricMatchesForSingleResults(singleResults, pixelatedSubRectanges, rectangleMatches)

logging.info("[%s straight matches | %s multiple matches]" % (len(singleResults), len(pixelatedSubRectanges)))


logging.info("Writing single match results to output")
writeFirstMatchToImage(singleResults, rectangleMatches, searchImage, unpixelatedOutputImage)

logging.info("Writing average results for multiple matches to output")
writeAverageMatchToImage(pixelatedSubRectanges, rectangleMatches, searchImage, unpixelatedOutputImage)

# writeRandomMatchesToImage(pixelatedSubRectanges, rectangleMatches, searchImage, unpixelatedOutputImage)

logging.info("Saving output image to: %s" % args.outputimage)
unpixelatedOutputImage.save(args.outputimage)
