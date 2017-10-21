import pandas
import csv
import math
pi = math.pi

###Count number of unique elements and print###
# un = []
# counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# df = pandas.read_csv("SignData.csv")
# for index, row in df.iterrows():
# 	print row["EntryID"], row["Movement"]
# 	if(row["Movement"] not in un):
# 		un += [row["Movement"]]
# 	else:
# 		counts[un.index(row["Movement"])] += 1
# print(un)
# print(counts)

###Filter out the elements that are not feasible to be represented with full words###
# movements = pandas.read_csv("freq.csv")
# indices = []
# for index, row in movements.iterrows():
# 	print(index)
# 	if(row["SignType"] == "AsymmetricalDifferentHandshape" or row["SignType"] == "Other"
# 	   or row["MajorLocation"] == "Arm" or row["MajorLocation"] == "Other"):
# 	    indices += [index]
# print(movements.shape)
# movements.drop(movements.index[indices], inplace = True)
# print(movements.shape)
# movements.to_csv("filteredMovements.csv", index = False)

###BEGIN ANGLE COLUMN ADDITION###
#'movements's columns before = ["EntryID", "SignFrequency(M)", "SignType", "SelectedFingers", "Flexion", "MajorLocation", "Movement"]
movements = pandas.read_csv("filteredMovements.csv")
#'movements's columns after = ["EntryID", "SignFrequency(M)", "SignType", "SelectedFingers", "Flexion", "MajorLocation", "Movement",
#							   "iFlexDom", "mFlexDom", "rFlexDom", "pFlexDom", "thumbFlexDom", "domFlexTime",
#						       "iFlexNonDom", "mFlexNonDom", "rFlexNonDom", "pFlexNonDom", "thumbFlexNonDom", "nonDomFlexTime",
#							   "xLocAngleDom", "yLocAngleDom", "domLocMoveTime",
#							   "xLocAngleNonDom", "yLocAngleNonDom", "nonDomLocMoveTime",
#							   "movemXLocAngle", "movemYLocAngle", "movemTime"]
#								^^^^I think that movements only apply to dominant hand, but im not sure.

##Parameter Definitions##
#SignType = ['AsymmetricalDifferentHandshape', 'OneHanded', 'AsymmetricalSameHandshape', 'SymmetricalOrAlternating', 'Other']
#										   -> ['OneHanded', 'AsymmetricalSameHandshape', 'SymmetricalOrAlternating']
#SelectedFingers = ['imrp', 'm', 'i', 'thumb', 'ip', 'p', 'im', 'mrp', 'imr', 'mr']
#Flexion = ['7', '1', '6', '5', '3', '2', '4', 'Crossed', 'Stacked']
#MajorLocation = ['Hand', 'Neutral', 'Head', 'Body', 'Arm', 'Other']
#			  -> ['Hand', 'Neutral', 'Head', 'Body']
#Movement =['BackAndForth', 'None', 'Circular', 'Straight', 'Curved', 'Other']

##Global Flags##
#flags whether both or just the dominant hand will be used
dominantOnly = False
#global values from [0, 1] that define the "closedness" of the fingers
globalFingerFlexions = [0, 0.167, 0.333, 0.5, 0.667, 0.833, 1, 1, 1]
#list to be used to get index to insert correct finger flexions
fingers = ["i", "m", "r", "p", "t"]
#global values for the tuples of angles to be used for the 'MajorLocation's
locationAnglesDom = [[180/4, -180/4], [180/4, 0], [-180/4, -180/4], [180/4, -180/2]]
locationAnglesNonDom = [[180/4, 180/4], [180/4, 0], [-180/4, 180/4], [180/4, 180/2]]
#list to be used to get index to get correct location
locs = ["Hand", "Neutral", "Head", "Body"]

#Begin Angle Assign
for index, row in movements.iterrows():
	fingerFlexions = [1, 1, 1, 1, 1]			#default value for a finger to be reset with 'SelectedFingers'
	signType = row["SignType"]
	if signType == "OneHanded":
		dominantOnly = True
	selectedFingers = list(row["SelectedFingers"])
	flexion = row["Flexion"]
	for finger in selectedFingers:
		fingerFlexions[fingers.index(finger)] = flexion
		if finger == "t":						#simple hack done to check if first letter is t (which represents thumb) and breaks because thumb is only 1 finger
			break									#(it can be seen that the thumb is never flexed in combination with other fingers (which is weird?))
	domHandFlexions = fingerFlexions
	domHandFlexTime = 0.75						#default number of seconds for fingers to be flexed in (arbitrary and can be changed later)
	nonDomHandFlexions = fingerFlexions
	nonDomHandFlexTime = 0.75					#default number of seconds for fingers to be flexed in (arbitrary and can be changed later)
	majorLocation = row["MajorLocation"]
	domLocAngle = locationAnglesDom[locs.index(majorLocation)]
	domLocMoveTime = 1.0						#default number of seconds for dominant hand to move to 'MajorLocation' (arbitrary and can be changed later)
	nonDomLocAngle = locationAnglesNonDom[locs.index(majorLocation)]
	nonDomLocMoveTime = 1.0						#default number of seconds for nondominant hand to move to 'MajorLocation' (arbitrary and can be changed later)
	###TO DO: get the angles for how movements work i.e. back and forth, curved etc.###
	biglist = domHandFlexions + [domHandFlexTime] \
			+ nonDomHandFlexions + [nonDomHandFlexTime] \
			+ domLocAngle + [domLocMoveTime] \
			+ nonDomLocAngle + [nonDomLocMoveTime]
	print(row["EntryID"], biglist)






































