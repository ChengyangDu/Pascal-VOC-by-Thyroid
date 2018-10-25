import xml.dom.minidom
import re
import os
import shutil
import scipy.ndimage
import random

def DumpBBoxCore(xmlFilePath, isDevidedByBenign):
    
    dom = xml.dom.minidom.parse(xmlFilePath)
    marks = dom.getElementsByTagName('mark')
    try:
        tirads = dom.getElementsByTagName('tirads')[0].childNodes[0].data
        if isDevidedByBenign:
            if tirads == '2' or tirads == '3':
                tirads = 'benign'
            else:
                tirads = 'malign'
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
                if tirads == 'na':
                    output[image] = {} # no classifications
                else:
                    output[image] = {'minX':minX, 'maxX':maxX, 'minY':minY, 'maxY':maxY, 'tirads':tirads}
        return output

def DumpBBox(dirPath, isDevidedByBenign):
    output = {}
    fileList = os.listdir(dirPath)
    for file in fileList:
        if os.path.basename(file).split('.')[1] == 'xml':
            xmlFilePath = os.path.join(dirPath,file)
            bBox = DumpBBoxCore(xmlFilePath, isDevidedByBenign)

            for i in bBox:
                if bool(bBox[i]): # only valid if there is label
                    imgPath = os.path.join(dirPath, os.path.basename(xmlFilePath).split('.')[0]+'_'+i+'.jpg')
                    output[imgPath] = bBox[i]
    return output

def CreateJPEGImageAndAnnotation(srcDir, outDir, isDevidedByBenign):
    dumpInfo = DumpBBox(srcDir, isDevidedByBenign)
    for img in dumpInfo:
        imgFileName = os.path.basename(img)
        imgFilePath = os.path.join(outDir, 'JPEGImages', imgFileName)
        shutil.copyfile(img, imgFilePath)

        h, w, c = scipy.ndimage.imread(img).shape
        formatStr = '<annotation><folder>VOC2012</folder><filename>' + imgFileName + '</filename><source><database>The VOC2007 Database</database><annotation>PASCAL VOC2007</annotation><image>flickr</image></source><size><width>'+\
                        str(w) + '</width><height>' + str(h) + '</height><depth>' + str(c) + '</depth></size><segmented>0</segmented><object><name>' + str(dumpInfo[img]['tirads']) + '</name><pose>Unspecified</pose><truncated>0</truncated><difficult>0</difficult><bndbox><xmin>' +\
                        str(dumpInfo[img]['minX']) + '</xmin><ymin>' + str(dumpInfo[img]['minY']) + '</ymin><xmax>' + str(dumpInfo[img]['minY']) + '</xmax><ymax>' + str(dumpInfo[img]['maxY']) + '</ymax></bndbox></object></annotation>'
    

        annoFileName = os.path.basename(img).split('.')[0]+'.xml'
        annoFilePath = os.path.join(outDir, 'Annotations', annoFileName)

        with open(annoFilePath, 'w') as f:
            print(formatStr, file = f)


def CreateImageSets(outDir, trainPercent):
    totalXml = os.listdir(os.path.join(outDir, 'Annotations'))
    
    num = len(totalXml)
    list = range(num)
    train = random.sample(range(num), int(num * trainPercent))

    classes = set()
    classDetails = dict()
    for curXml in totalXml:
        dom = xml.dom.minidom.parse(os.path.join(outDir, 'Annotations', curXml))
        annotation = dom.getElementsByTagName('annotation')[0]
        object = annotation.getElementsByTagName('object')[0]
        name = object.getElementsByTagName('name')[0].childNodes[0].data
        classes.update([name])
        classDetails[curXml] = name
    
    for curClass in classes:
        ftrainval = open(os.path.join(outDir, 'ImageSets/Main/', curClass+'_trainval.txt'), 'w')
        ftrain = open( os.path.join(outDir, 'ImageSets/Main/', curClass+'_train.txt'), 'w')
        fval = open(os.path.join(outDir, 'ImageSets/Main/' + curClass+'_val.txt'), 'w')

        for i in list:
            name = totalXml[i][:-4]
            if classDetails[totalXml[i]] == curClass:
                flag = 1
            else:
                flag = -1
            info = name + ' ' + str(flag) + '\n'
            ftrainval.write(info)
            if i in train:
                ftrain.write(info)
            else:
                fval.write(info)

        ftrainval.close()
        ftrain.close()
        fval.close()

def CleanOutputDir(outputDir):
    if os.path.exists(outputDir):
        shutil.rmtree(outputDir)
    os.makedirs(os.path.join(outputDir, 'JPEGImages'))
    os.makedirs(os.path.join(outputDir, 'Annotations'))
    os.makedirs(os.path.join(outputDir, 'ImageSets/Main'))


if __name__=="__main__":

    sourceDir = './imgs'
    outputDir = './output'
    isDevidedByBenign = True

    CleanOutputDir(outputDir)
    CreateJPEGImageAndAnnotation(sourceDir, outputDir, isDevidedByBenign)
    CreateImageSets(outputDir, 0.9)
    