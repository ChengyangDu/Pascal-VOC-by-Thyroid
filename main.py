import xml.dom.minidom
import re

filePath = "./imgs/81.xml"
dom = xml.dom.minidom.parse(filePath)


marks = dom.getElementsByTagName('mark')

for mark in marks:
    image = mark.getElementsByTagName('image')[0].childNodes[0].data
    svg = mark.getElementsByTagName('svg')[0].childNodes[0].data
    #[{"x": 333, "y": 109
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
    print(minX, maxX, minY, maxY)


        
        

    
    
    