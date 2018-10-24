import xml.dom.minidom
import re
import os

def DumpBBoxCore(xmlFilePath):
    
    dom = xml.dom.minidom.parse(xmlFilePath)
    marks = dom.getElementsByTagName('mark')

    output = {}
    for mark in marks:
        image = mark.getElementsByTagName('image')[0].childNodes[0].data
        try:
            svg = mark.getElementsByTagName('svg')[0].childNodes[0].data
        except:
            output[image] = {}
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
            output[image] = {'minX':minX, 'maxX':maxX, 'minY':minY, 'maxY':maxY}
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


path = './imgs'
print(DumpBBox(path))

    