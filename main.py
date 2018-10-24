import xml.dom.minidom
import re
import os
import shutil
import scipy.ndimage

def DumpBBoxCore(xmlFilePath):
    
    dom = xml.dom.minidom.parse(xmlFilePath)
    marks = dom.getElementsByTagName('mark')
    try:
        tirads = dom.getElementsByTagName('tirads')[0].childNodes[0].data
    except:
        tirads = 'na'
    finally:
        output = {}
        for mark in marks:
            image = mark.getElementsByTagName('image')[0].childNodes[0].data
            try:
                svg = mark.getElementsByTagName('svg')[0].childNodes[0].data
            except:
                output[image] = {}#no labelling info
            else:
                pattern = re.compile(r"\d+")
                match = pattern.findall(svg)

                for i in range(len(match)):
                    if i == 0:
                        minX = match[0]
                        maxX = match[0]
                    elif i == 1:
                        minY = match[1]
                        maxY = match[1]

                    elif i%2 == 0:
                        if match[i]<minX:
                            minX = match[i]
                        if match[i]>maxX:
                            maxX = match[i]
                    else:
                        if match[i]<minY:
                            minY = match[i]
                        if match[i]>maxY:
                            maxY = match[i] 
                output[image] = {'minX':minX, 'maxX':maxX, 'minY':minY, 'maxY':maxY, 'tirads':tirads}
        return output

def DumpBBox(dirPath):
    output = {}
    fileList = os.listdir(dirPath)
    for file in fileList:
        if os.path.basename(file).split('.')[1] == 'xml':
            xmlFilePath = os.path.join(dirPath,file)
            bBox = DumpBBoxCore(xmlFilePath)

            for i in bBox:
                if bool(bBox[i]):
                    imgPath = os.path.join(dirPath, os.path.basename(xmlFilePath).split('.')[0]+'_'+i+'.jpg')
                    output[imgPath] = bBox[i]
    return output

def CreateJPEGImageAndAnnotation(srcDir, outDir):
    for img in DumpBBox(srcDir):
        outputFile = os.path.join(outDir, 'JPEGImages', os.path.basename(img))
        shutil.copyfile(img, outputFile)

        h, w, c = scipy.ndimage.imread(img).shape

         











    


if os.path.exists('./output'):
    shutil.rmtree('./output')
os.makedirs('./output/JPEGImages')
os.makedirs('./output/Annotations')
path = './imgs'
CreateJPEGImageAndAnnotation(path, './output')
print(DumpBBox(path))

    