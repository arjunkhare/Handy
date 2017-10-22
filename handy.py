import pandas
import csv
import math
import numpy
import time
import nltk
import random
from nltk.stem.wordnet import WordNetLemmatizer
pi = math.pi



###Count number of unique elements and print###
# un = []
# counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# df = pandas.read_csv("SignData.csv")
# for index, row in df.iterrows():
#   print row["EntryID"], row["Movement"]
#   if(row["Movement"] not in un):
#       un += [row["Movement"]]
#   else:
#       counts[un.index(row["Movement"])] += 1
# print(un)
# print(counts)

###Filter out the elements that are not feasible to be represented with full words###
# movements = pandas.read_csv("freq.csv")
# indices = []
# for index, row in movements.iterrows():
#     print(index)
#     if(row["SignType"] == "AsymmetricalDifferentHandshape" or row["SignType"] == "Other"
#         or row["MajorLocation"] == "Arm" or row["MajorLocation"] == "Other"):
#         indices += [index]
#     if(row["EntryID"].find("_") != -1):
#         indices += [index]
#     if(row["Movement"] == "Other"):
#         indices += [index]
# print(movements.shape)
# movements.drop(movements.index[indices], inplace = True)
# print(movements.shape)
# movements.to_csv("filteredMovements.csv", index = False)

###BEGIN ANGLE COLUMN ADDITION###
#'movements's columns before = ["EntryID", "SignFrequency(M)", "SignType", "SelectedFingers", "Flexion", "MajorLocation", "Movement"]
movements = pandas.read_csv("filteredMovements.csv")
#'movements's columns after = ["EntryID", "SignFrequency(M)", "SignType", "SelectedFingers", "Flexion", "MajorLocation", "Movement",
#                              "iFlexDom", "mFlexDom", "rFlexDom", "pFlexDom", "thumbFlexDom",
#                              "iFlexNonDom", "mFlexNonDom", "rFlexNonDom", "pFlexNonDom", "thumbFlexNonDom",
#                              "xLocAngleDom", "yLocAngleDom",
#                              "xLocAngleNonDom", "yLocAngleNonDom",
#                              "movemXLocAngleF1", "movemYLocAngleF1",
#                              "movemXLocAngleF2", "movemYLocAngleF2",
#                              "movemXLocAngleF3", "movemYLocAngleF3",
#                              "movemXLocAngleF4", "movemYLocAngleF4",
#                              "movemXLocAngleF5", "movemYLocAngleF5",
#                              "movemXLocAngleF6", "movemYLocAngleF6",]
#                               ^^^^I think that movements only apply to dominant hand, but im not sure.

##Parameter Definitions##
#SignType = ['AsymmetricalDifferentHandshape', 'OneHanded', 'AsymmetricalSameHandshape', 'SymmetricalOrAlternating', 'Other']
#                                          -> ['OneHanded', 'AsymmetricalSameHandshape', 'SymmetricalOrAlternating']
#SelectedFingers = ['imrp', 'm', 'i', 'thumb', 'ip', 'p', 'im', 'mrp', 'imr', 'mr']
#Flexion = ['7', '1', '6', '5', '3', '2', '4', 'Crossed', 'Stacked']
#MajorLocation = ['Hand', 'Neutral', 'Head', 'Body', 'Arm', 'Other']
#             -> ['Hand', 'Neutral', 'Head', 'Body']
#Movement =['BackAndForth', 'None', 'Circular', 'Straight', 'Curved', 'Other']
#        ->['BackAndForth', 'None', 'Circular', 'Straight', 'Curved']

##Global Flags##
##Important Mathematical Methods
R = 35  # radius of arm
r_c = 5  # radius of small circle
# Given (y,z) coordinates, closest_point will find the closest point perpendicular to the y-z plane on a sphere centered at (0,0,0)
def closest_point(p):
    y0 = p[0]
    z0 = p[1]
    x = math.sqrt(R**2 - y0**2 - z0**2)
    return [x, y0, z0]

# Angle --> Point
def angle_to_point(angle):  # angle[0] is depth, angle[1] is relative to surface
    y = R*math.cos(math.radians(angle[0]))
    z = R*math.sin(math.radians(angle[0]))
    x = R*math.cos(math.radians(angle[1]))
    return [x,y,z]

#Defines movement from one major location angle to another
def move_major(a1_0,a2_0,a1_f,a2_f,n):
    a1 = a1_0
    a2 = a2_0
    B = []
    for i in range (0,n):
        a1 += (a1_f-a1_0)/n
        a2 += (a2_f-a2_0)/n
        B.append([a1,a2])
    return B

# Find the decomposed x, z angle between two vectors
def point_to_angle(position):
    x = position[0]
    y = position[1]
    z = position[2]
    if y == 0:
        angle_depth = 90
    else:
        angle_depth = math.degrees(math.atan(z/y))
    if angle_depth != math.degrees(math.asin(z/R)) or angle_depth != math.degrees(math.acos(y/R)):
        angle_depth = -1*angle_depth
    angle_surface = math.degrees(math.asin(x/R))
    return [angle_depth, angle_surface]
    
    
# Generate n ordered pairs on a circle defined by center (x0,y0) and radius
def make_quarter_circle(radius, x0, y0, n):
    # Makes quarter circle
    x = list(numpy.arange(x0 - radius/(4*n),x0-radius,float(-1*radius)/n))
    y = []
    for i in x:
        y.append(math.sqrt((radius**2) - (i-x0)**2) + y0)
    return x,y

def make_full_circle(radius, x0, y0, n):
    # Makes full circle
    c1 = list(numpy.arange(x0 + radius,x0-radius + radius/(4*n),float(-2*radius)/n))
    c2 = list(reversed(c1))
    y = []
    # Make semi circle first
    for i in c1:
        y_val = math.sqrt((radius**2) - (i-x0)**2) + y0
        y.append(y_val)
    for i in c2:
        y_val = -1*math.sqrt((radius**2) - (i-x0)**2) + y0
        y.append(y_val)
    x = numpy.concatenate([c1, c2])
    return x,y

#flags whether both or just the dominant hand will be used
dominantOnly = False

#global values from [0, 1] that define the "closedness" of the fingers
gFFDict = {"1":0.01, "2":0.167, "3":0.333, "4":0.5, "5":0.667, "6":0.833, "7":0.99} #gFFDict = globalFingerFlexionsDict

#list to be used to get index to insert correct finger flexions
fingers = ["i", "m", "r", "p", "t"]

#global values for the tuples of angles to be used for the MajorLocations   For 4th element of list (Body), consider increasing 1st element of tuple (surface)
locationAnglesDom = [[180/4, 180/4], [180/4, 0], [-180/4, 180/4], [180/4, 180/2]]
locationAnglesNonDom = [[180/4, -180/4], [180/4, 0], [-180/4, -180/4], [180/4, -180/2]]

#list to be used to get index to get correct location
locs = ["Hand", "Neutral", "Head", "Body"]

finalDict = {}
bigList = [[]]
#Begin Angle Assign
for index, row in movements.iterrows():
    fingerFlexions = ["7", "7", "7", "7", "7"]            #default value for a finger to be reset with 'SelectedFingers'
    signType = row["SignType"]
    if signType == "OneHanded":
        dominantOnly = True

    # Fingers
    selectedFingers = list(row["SelectedFingers"])
    flexion = row["Flexion"]
    for finger in selectedFingers:
        if flexion == 'Crossed' or flexion == 'Stacked':     # set crossed or stacked as minimum closedness (0)
            flexion = '1'
        fingerFlexions[fingers.index(finger)] = str(flexion)
        if finger == "t":                       #simple hack done to check if first letter is t (which represents thumb) and breaks because thumb is only 1 finger
            break                                   #(it can be seen that the thumb is never flexed in combination with other fingers (which is weird?))
    domHandFlexions = fingerFlexions
    nonDomHandFlexions = fingerFlexions
    
    # Elbow
    majorLocation = row["MajorLocation"]
    domLocAngle = locationAnglesDom[locs.index(majorLocation)]
    nonDomLocAngle = locationAnglesNonDom[locs.index(majorLocation)]

    # Movement
    # For straight one-handed movements, adjust depth by a number of deg, pointing towards user.
    # For straight two-handed symmetrical movements, adjust surface by a number of deg, to bring hands closer together.
    # For straight two-handed asymmetrical movements, adjust wrist position such that one hand is pointing up, one hand is pointing to the side.
    # For curved one-handed movements, need to utilize three dimensions: 
    movement = row["Movement"]
    domAngles = [[], [], [], [], [], []]
    nonDomAngles = [[], [], [], [], [], []]
    if movement == 'Straight':
        move = move_major(domLocAngle[0], domLocAngle[1], domLocAngle[0], domLocAngle[1]+30, 1)
        domAngles = [move[0], move[0], move[0], move[0], move[0], move[0]]
        moveN = move_major(nonDomLocAngle[0], nonDomLocAngle[1], nonDomLocAngle[0], nonDomLocAngle[1]+30, 1)
        nonDomAngles = [moveN[0], moveN[0], moveN[0], moveN[0], moveN[0], moveN[0]]
    elif movement == 'BackAndForth':                                                        # Forwards, backwards, back to center
        move1 = move_major(domLocAngle[0], domLocAngle[1], domLocAngle[0], domLocAngle[1]+45, 1)
        move2 = move_major(domLocAngle[0], domLocAngle[1]+45, domLocAngle[0], domLocAngle[1]-45, 1)
        move3 = move_major(domLocAngle[0], domLocAngle[1]-45, domLocAngle[0], domLocAngle[1], 1)
        domAngles = [move1[0], move2[0], move3[0], move3[0], move3[0], move3[0]]
        move1N = move_major(nonDomLocAngle[0], nonDomLocAngle[1], nonDomLocAngle[0], nonDomLocAngle[1]+45, 1)
        move2N = move_major(nonDomLocAngle[0], nonDomLocAngle[1]+45, nonDomLocAngle[0], nonDomLocAngle[1]-45, 1)
        move3N = move_major(nonDomLocAngle[0], nonDomLocAngle[1]-45, nonDomLocAngle[0], nonDomLocAngle[1], 1)
        nonDomAngles = [move1N[0], move2N[0], move3N[0], move3N[0], move3N[0], move3N[0]]
    elif movement == 'Curved':
        [x, y, z] = angle_to_point(domLocAngle)
        if y + 3*r_c > R:
            y -= 3*r_c
        elif y - 3*r_c < -1*R:
            y += 3*r_c
        if z + 3*r_c > R:
            z -= 3*r_c
        elif z - 3*r_c < -1*R:
            z += 3*r_c      
        y1, z1 = make_quarter_circle(r_c,y,z,6)
        domAngles = []
        for i in range(0,len(y1)):
            point = [y1[i], z1[i]]
            [x_c, y_c, z_c] = closest_point(point)
            position = [x_c, y_c, z_c]
            A = point_to_angle(position)
            domAngles.append(A)
        [xN, yN, zN] = angle_to_point(nonDomLocAngle)
        if yN + 3*r_c > R:
            yN -= 3*r_c
        elif yN - 3*r_c < -1*R:
            yN += 3*r_c
        if zN + 3*r_c > R:
            zN -= 3*r_c
        elif zN - 3*r_c < -1*R:
            zN += 3*r_c      
        y1N, z1N = make_quarter_circle(r_c,yN,zN,6)
        nonDomAngles = []
        for i in range(0,len(y1N)):
            point = [y1N[i], z1N[i]]
            [x_c, y_c, z_c] = closest_point(point)
            position = [x_c, y_c, z_c]
            A = point_to_angle(position)
            nonDomAngles.append(A)
    elif movement == 'Circular':
        # full circle
        [x, y, z] = angle_to_point(domLocAngle)
        if y + 3*r_c > R:
            y -= 3*r_c
        elif y - 3*r_c < -1*R:
            y += 3*r_c
        if z + 3*r_c > R:
            z -= 3*r_c
        elif z - 3*r_c < -1*R:
            z += 3*r_c      
        y1, z1 = make_full_circle(r_c,y,z,3)
        domAngles = []
        for i in range(0,len(y1)):
            point = [y1[i], z1[i]]
            [x_c, y_c, z_c] = closest_point(point)
            position = [x_c, y_c, z_c]
            A = point_to_angle(position)
            domAngles.append(A)
        [xN, yN, zN] = angle_to_point(nonDomLocAngle)
        if yN + 3*r_c > R:
            yN -= 3*r_c
        elif yN - 3*r_c < -1*R:
            yN += 3*r_c
        if zN + 3*r_c > R:
            zN -= 3*r_c
        elif zN - 3*r_c < -1*R:
            zN += 3*r_c      
        y1N, z1N = make_full_circle(r_c,yN,zN,3)
        domAngles = []
        for i in range(0,len(y1N)):
            point = [y1N[i], z1N[i]]
            [x_c, y_c, z_c] = closest_point(point)
            position = [x_c, y_c, z_c]
            A = point_to_angle(position)
            nonDomAngles.append(A)
    elif movement == 'None':
        domAngles = [domLocAngle, domLocAngle, domLocAngle, domLocAngle, domLocAngle, domLocAngle]
        nonDomAngles = [nonDomLocAngle, nonDomAngles, nonDomAngles, nonDomAngles, nonDomAngles, nonDomAngles]
    finalList = [domHandFlexions] \
                + [nonDomHandFlexions] \
                + [domLocAngle] \
                + [nonDomLocAngle] \
                + [domAngles] \
                + [nonDomAngles]
    bigList += [finalList]
    finalDict[row["EntryID"]] = finalList
    # print(" ")
    # print(row["EntryID"], finalList)

# to be called with a finalDict.get("itemname")
def getEncoding(smallerList):
    rightHand = smallerList[0]
    leftHand = smallerList[1]
    rightHandElbow = smallerList[2]
    leftHandElbow = smallerList[3]
    domAngles = smallerList[4]
    nonDomAngles = smallerList[5]
    FOUTPUT_VECTOR = [-1 for i in range(20)]
    FOUTPUT_VECTOR[0] = rightHandElbow[0]
    FOUTPUT_VECTOR[1] = rightHandElbow[1]
    FOUTPUT_VECTOR[2] = 0
    FOUTPUT_VECTOR[3] = 0
    FOUTPUT_VECTOR[4] = 0
    FOUTPUT_VECTOR[5] = leftHandElbow[0]
    FOUTPUT_VECTOR[6] = leftHandElbow[1]
    FOUTPUT_VECTOR[7] = 0
    FOUTPUT_VECTOR[8] = 0
    FOUTPUT_VECTOR[9] = 0
    FOUTPUT_VECTOR[10] = int(float(gFFDict.get(rightHand[4]))*100)
    FOUTPUT_VECTOR[11] = int(float(gFFDict.get(rightHand[0]))*100)
    FOUTPUT_VECTOR[12] = int(float(gFFDict.get(rightHand[1]))*100)
    FOUTPUT_VECTOR[13] = int(float(gFFDict.get(rightHand[2]))*100)
    FOUTPUT_VECTOR[14] = int(float(gFFDict.get(rightHand[3]))*100)
    FOUTPUT_VECTOR[15] = int(float(gFFDict.get(leftHand[4]))*100)
    FOUTPUT_VECTOR[16] = int(float(gFFDict.get(leftHand[0]))*100)
    FOUTPUT_VECTOR[17] = int(float(gFFDict.get(leftHand[1]))*100)
    FOUTPUT_VECTOR[18] = int(float(gFFDict.get(leftHand[2]))*100)
    FOUTPUT_VECTOR[19] = int(float(gFFDict.get(leftHand[3]))*100)
    allLines = []
    line1 = []
    for index in range(len(FOUTPUT_VECTOR)):
        line1 += ["<"+str(FOUTPUT_VECTOR[index])+">"]
    line1 += ["~"]
    allLines.append(line1)
    for index in range(len(domAngles)):
        currLine = []
        FOUTPUT_VECTOR = [-1 for i in range(20)]
        FOUTPUT_VECTOR[0] = domAngles[index][0]
        FOUTPUT_VECTOR[1] = domAngles[index][1]
        FOUTPUT_VECTOR[2] = 0
        FOUTPUT_VECTOR[3] = 0
        FOUTPUT_VECTOR[4] = 0
        FOUTPUT_VECTOR[5] = nonDomAngles[index][0]                                #may change later depends on time
        FOUTPUT_VECTOR[6] = nonDomAngles[index][1]
        FOUTPUT_VECTOR[7] = 0
        FOUTPUT_VECTOR[8] = 0
        FOUTPUT_VECTOR[9] = 0
        FOUTPUT_VECTOR[10] = int(float(gFFDict.get(rightHand[4]))*100)
        FOUTPUT_VECTOR[11] = int(float(gFFDict.get(rightHand[0]))*100)
        FOUTPUT_VECTOR[12] = int(float(gFFDict.get(rightHand[1]))*100)
        FOUTPUT_VECTOR[13] = int(float(gFFDict.get(rightHand[2]))*100)
        FOUTPUT_VECTOR[14] = int(float(gFFDict.get(rightHand[3]))*100)
        FOUTPUT_VECTOR[15] = int(float(gFFDict.get(leftHand[4]))*100)
        FOUTPUT_VECTOR[16] = int(float(gFFDict.get(leftHand[0]))*100)
        FOUTPUT_VECTOR[17] = int(float(gFFDict.get(leftHand[1]))*100)
        FOUTPUT_VECTOR[18] = int(float(gFFDict.get(leftHand[2]))*100)
        FOUTPUT_VECTOR[19] = int(float(gFFDict.get(leftHand[3]))*100)
        for index in range(len(FOUTPUT_VECTOR)):
            currLine += ["<"+str(FOUTPUT_VECTOR[index])+">"]
        currLine += ["~"]
        allLines.append(currLine)
    FOUTPUT_VECTOR = [-1 for i in range(20)]
    FOUTPUT_VECTOR[0] = domAngles[len(domAngles)-1][0]
    FOUTPUT_VECTOR[1] = domAngles[len(domAngles)-1][1]
    FOUTPUT_VECTOR[2] = 0
    FOUTPUT_VECTOR[3] = 0
    FOUTPUT_VECTOR[4] = 0
    FOUTPUT_VECTOR[5] = nonDomAngles[len(nonDomAngles)-1][0]
    FOUTPUT_VECTOR[6] = nonDomAngles[len(nonDomAngles)-1][1]
    FOUTPUT_VECTOR[7] = 0
    FOUTPUT_VECTOR[8] = 0
    FOUTPUT_VECTOR[9] = 0
    FOUTPUT_VECTOR[10] = int(float(gFFDict.get(rightHand[4]))*100)
    FOUTPUT_VECTOR[11] = int(float(gFFDict.get(rightHand[0]))*100)
    FOUTPUT_VECTOR[12] = int(float(gFFDict.get(rightHand[1]))*100)
    FOUTPUT_VECTOR[13] = int(float(gFFDict.get(rightHand[2]))*100)
    FOUTPUT_VECTOR[14] = int(float(gFFDict.get(rightHand[3]))*100)
    FOUTPUT_VECTOR[15] = int(float(gFFDict.get(leftHand[4]))*100)
    FOUTPUT_VECTOR[16] = int(float(gFFDict.get(leftHand[0]))*100)
    FOUTPUT_VECTOR[17] = int(float(gFFDict.get(leftHand[1]))*100)
    FOUTPUT_VECTOR[18] = int(float(gFFDict.get(leftHand[2]))*100)
    FOUTPUT_VECTOR[19] = int(float(gFFDict.get(leftHand[3]))*100)
    line1 = []
    for index in range(len(FOUTPUT_VECTOR)):
        line1 += ["<"+str(FOUTPUT_VECTOR[index])+">"]
    line1 += ["~"]
    for index in range(5):                                              #change 5 to whatever to increase/decrease delay between words
        allLines.append(line1)
    return allLines

import serial
ser = serial.Serial('/dev/tty.usbmodem1411', 9600)

def reset():
    print("resetting all configurations")
    resetArr = [["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                 "~"],
                 ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                 "~"]]
    for instrLine in resetArr:
        for instr in instrLine:
            ser.write(instr)
            print(instr)
        time.sleep(0.50)


def handwave():
    print("handwave hi there!")
    handArr = [["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<20>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<-20>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<20>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<-20>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<20>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<-20>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>", 
                "~"]]
    for instrLine in handArr:
        for instr in instrLine:
            ser.write(instr)
            print(instr)
        time.sleep(0.5)

def queenwave():
    print("queen wave woooooo")
    qunray = [["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<35>",
                "<0>", "<0>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<-35>",
                "<0>", "<0>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<35>",
                "<0>", "<0>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<-35>",
                "<0>", "<0>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<35>",
                "<0>", "<0>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<-35>",
                "<0>", "<0>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>",
                "<20>", "<20>", "<20>", "<20>", 
                "~"],
                ["<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>", 
                "~"]]
    for instrLine in qunray:
        for instr in instrLine:
            ser.write(instr)
            print(instr)
        time.sleep(0.5)


def countdown():
    print("rock papers scissors countdown")
    coArr = [["<0>", "<0>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>", 
                "~"],
                ["<0>", "<-120>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>", 
                "~"],
                ["<0>", "<0>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>", 
                "~"],
                ["<0>", "<-120>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>", 
                "~"],
                ["<0>", "<0>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>", 
                "~"]
            ]
    for instrLine in coArr:
        for instr in instrLine:
            ser.write(instr)
            print(instr)
        time.sleep(0.50)

def rock():
    print("rock")
    rockArr = [["<0>", "<-120>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>",
                 "~"],
                 ["<0>", "<-120>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>",
                "<99>", "<99>", "<99>", "<99>",
                 "~"]]
    for instrLine in rockArr:
        for instr in instrLine:
            ser.write(instr)
            print(instr)
        time.sleep(0.50)

def paper():
    print("paper")
    paperArr = [["<0>", "<-120>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                 "~"],
                 ["<0>", "<-120>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                "<1>", "<1>", "<1>", "<1>",
                 "~"]]
    for instrLine in paperArr:
        for instr in instrLine:
            ser.write(instr)
            print(instr)
        time.sleep(0.50)

def scissors():
    print("scissors")
    scisArr = [["<0>", "<-120>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<99>", "<1>",
                "<1>", "<99>", "<99>", "<99>",
                "<1>", "<1>", "<99>", "<99>",
                 "~"],
                ["<0>", "<-120>", "<110>", "<0>",
                "<0>", "<0>", "<0>", "<0>",
                "<0>", "<0>", "<99>", "<1>",
                "<1>", "<99>", "<99>", "<99>",
                "<1>", "<1>", "<99>", "<99>",
                 "~"]]
    for instrLine in scisArr:
        for instr in instrLine:
            ser.write(instr)
            print(instr)
        time.sleep(0.50)

def playRockPaperScissors():
    print("playing rock paper scissors!!")
    countdown()
    a = random.uniform(0, 1)
    if a <= 0.333:
        rock()
    elif a <= 0.667:
        paper()
    elif a <= 1.00:
        scissors()
    time.sleep(5)
    reset()



# print("airplace*****")
# ExecuteWithHandy("yesterday")
# time.sleep(2)
# print("fingerspelling*****")
# ExecuteWithHandy("fingerspelling")
# time.sleep(2)
# print("wander*****")
# ExecuteWithHandy("wander")

def ExecuteWithHandy(instructionID):
    result = getEncoding(finalDict.get(instructionID))
    for instrLine in result:
        for instruction in instrLine:
            ser.write(instruction)
            print(instruction)
        time.sleep(0.25)

def testBreak():
    with open('outputtext.txt', 'r') as myfile:
        data=myfile.read().replace('\n', '')
        wordArr = data.split(" ")
        corrArr = []
        for word in wordArr:
            # lmtzr = WordNetLemmatizer()
            # print(lmtzr.lemmatize('word'))
            if word in finalDict:
                corrArr += [word]
        for finalW in corrArr:
            ExecuteWithHandy(finalW)
            time.sleep(0.10)
        time.sleep(1.0)
        reset()
        print(corrArr)







