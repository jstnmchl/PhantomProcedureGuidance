outputPath = 'C:\\Scans\\'
outputFilename = outputPath + 'slicerIPSAplan.txt'
print(outputFilename)

fileObject = open(outputFilename, 'w')
# write header
fileObject.write("______________________________________________________________________\n \n
                                 IPSA \n
______________________________________________________________________\n \n ")
fileObject.close()