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
                if bool(bBox[i]): # only valid if there is label
                    imgPath = os.path.join(dirPath, os.path.basename(xmlFilePath).split('.')[0]+'_'+i+'.jpg')
                    output[imgPath] = bBox[i]
    return output

def CreateJPEGImageAndAnnotation(srcDir, outDir):
    dumpInfo = DumpBBox(srcDir)
    for img in dumpInfo:
        imgFileName = os.path.basename(img)
        imgFilePath = os.path.join(outDir, 'JPEGImages', imgFileName)
        shutil.copyfile(img, imgFilePath)

        h, w, c = scipy.ndimage.imread(img).shape
        formatStr = '<annotation><folder>VOC2012</folder><filename>' + imgFileName + '</filename><source><database>The VOC2007 Database</database><annotation>PASCAL VOC2007</annotation><image>flickr</image></source><size><width>'+\
                        str(w) + '</width><height>' + str(h) + '</height><depth>' + str(c) + '</depth></size><segmented>1</segmented><object><name>' + str(dumpInfo[img]['tirads']) + '</name><pose>Unspecified</pose><truncated>0</truncated><difficult>0</difficult><bndbox><xmin>' +\
                        str(dumpInfo[img]['minX']) + '</xmin><ymin>' + str(dumpInfo[img]['minY']) + '</ymin><xmax>' + str(dumpInfo[img]['minY']) + '</xmax><ymax>' + str(dumpInfo[img]['maxY']) + '</ymax></bndbox></object></annotation>'
    

        annoFileName = os.path.basename(img).split('.')[0]+'.xml'
        annoFilePath = os.path.join(outDir, 'Annotations', annoFileName)

        with open(annoFilePath, 'w') as f:
            print(formatStr, file = f)













    


if os.path.exists('./output'):
    shutil.rmtree('./output')
os.makedirs('./output/JPEGImages')
os.makedirs('./output/Annotations')

CreateJPEGImageAndAnnotation('./imgs', './output')
    