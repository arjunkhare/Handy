import pandas
import csv
import math
import numpy
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
R = 35  # radius of arm
r_c = 5  # radius of small circle

#list to be used to get index to insert correct finger flexions
fingers = ["i", "m", "r", "p", "t"]

#global values for the tuples of angles to be used for the MajorLocations   For 4th element of list (Body), consider increasing 1st element of tuple (surface)
locationAnglesDom = [[180/4, 180/4], [180/4, 0], [-180/4, -180/4], [180/4, 180/2]]
locationAnglesNonDom = [[180/4, -180/4], [180/4, 0], [-180/4, 180/4], [180/4, -180/2]]

#list to be used to get index to get correct location
locs = ["Hand", "Neutral", "Head", "Body"]

# Given (y,z) coordinates, closest_point will find the closest point perpendicular to the y-z plane on a sphere centered at (0,0,0)
def closest_point(p):
    y0 = p[0]
    z0 = p[1]
    x = math.sqrt(R**2 - y0**2 - z0**2)
    return [x, y0, z0]

# Angle --> Point
def angle_to_point(angle):  # angle[0] is relative to surface, angle[1] is depth
    y = R*math.cos(math.radians(angle[0]))
    z = R*math.sin(math.radians(angle[0]))
    x = R*math.cos(math.radians(angle[1]))
    
    return [x,y,z]
    
def move_major(a1_0,a2_0,a1_f,a2_f,n):
    a1 = a1_0
    a2 = a2_0
    B = []
    
    for i in range (0,n):
        a1 += (a1_f-a1_0)/n
        a2 += (a2_f-a2_0)/n
        B.append([a1,a2])
    return B

## Calculate the dot product of two vectors
#def dot_product(x,y):
#    result = 0
#    for col in range(0,len(x)):
#        result += x[col]*y[col]
#    return result
#
## Calculate the magnitude of a vector
#def magnitude(x):
#    sum_squares = 0
#    for col in range(0,len(x)):
#        sum_squares += math.pow((x[col]),2)
#    return math.sqrt(sum_squares)

# Find the decomposed x, z angle between two vectors
def point_to_angle(position):
    x = position[0]
    y = position[1]
    z = position[2]
    if y == 0:
        angle_surface = 90
    else:
        angle_surface = math.degrees(math.atan(z/y))
        
    if angle_surface != math.degrees(math.asin(z/R)) or angle_surface != math.degrees(math.acos(y/R)):
        angle_surface = -1*angle_surface
    angle_depth = math.degrees(math.asin(x/R))
        
    return [angle_surface, angle_depth]
    
#    i_uv = [1, 0, 0]   # i unit vector
#    k_uv = [0, 0, 1]   # k unit vector
#
#    angle_surface = math.acos(dot_product(k_uv,position)/magnitude(position))
#    angle_depth = math.acos(dot_product(i_uv,position)/magnitude(position))
#    
#    # Angle is relative to the normal of x-z plane, where the + direction is right, and - direction is left
#    angle_surface = 90 - angle_surface
#    angle_depth = 90 - angle_depth
    
    
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
    
    

#Begin Angle Assign
for index, row in movements.iterrows():
	fingerFlexions = [1, 1, 1, 1, 1]			#default value for a finger to be reset with 'SelectedFingers'
	signType = row["SignType"]
	if signType == "OneHanded":
		dominantOnly = True
	
	# Fingers
	selectedFingers = list(row["SelectedFingers"])
	flexion = row["Flexion"]
	for finger in selectedFingers:
		if flexion == 'Crossed' or flexion == 'Stacked':     # set crossed or stacked as minimum closedness (0)
			flexion = '0'
		fingerFlexions[fingers.index(finger)] = flexion
		if finger == "t":						#simple hack done to check if first letter is t (which represents thumb) and breaks because thumb is only 1 finger
			break									#(it can be seen that the thumb is never flexed in combination with other fingers (which is weird?))
	domHandFlexions = fingerFlexions

	nonDomHandFlexions = fingerFlexions

	
	# Elbow
	majorLocation = row["MajorLocation"]
	domLocAngle = locationAnglesDom[locs.index(majorLocation)]
	nonDomLocAngle = locationAnglesNonDom[locs.index(majorLocation)]
	
	###TO DO: get the angles for how movements work i.e. back and forth, curved etc.###
	
    
    # Movement
    
    # For straight one-handed movements, adjust depth by a number of deg, pointing towards user.
    # For straight two-handed symmetrical movements, adjust surface by a number of deg, to bring hands closer together.
    # For straight two-handed asymmetrical movements, adjust wrist position such that one hand is pointing up, one hand is pointing to the side.
    
    # For curved one-handed movements, need to utilize three dimensions: 
    
	movement = row["Movement"]

	Angles=[[0,0]]
	if movement == 'Straight':
        	move_major(Angles[-1][0],Angles[-1][1],domLocAngle[0],domLocAngle[1],3)
        	move_major(Angles[-1][0],Angles[-1][0],domLocAngle[0],domLocAngle[1]+10,1)
    
	elif movement == 'BackAndForth':
        	move_major(Angles[-1][0],Angles[-1][1],domLocAngle[0],domLocAngle[1],3)
    # Forwards, backwards, back to center
        	move_major(Angles[-1][0],Angles[-1][1],domLocAngle[0],domLocAngle[1],3)
        	move_major(Angles[-1][0],Angles[-1][1],domLocAngle[0],domLocAngle[1]+15,3)
        	move_major(Angles[-1][0],Angles[-1][1],domLocAngle[0],domLocAngle[1]-15,3)
        	move_major(Angles[-1][0],Angles[-1][1],domLocAngle[0],domLocAngle[1],3)
        
    
	elif movement == 'Curved':
        	[x, y, z] = angle_to_point(domLocAngle)
            # Check to make sure circle is doable
        	if y + 3*r_c > R:
        		y -= 3*r_c
        	elif y - 3*r_c < -1*R:
        		y += 3*r_c
                
        	if z + 3*r_c > R:
        		z -= 3*r_c
        	elif z - 3*r_c < -1*R:
        		z += 3*r_c      
                
        	y1, z1 = make_quarter_circle(r_c,y,z,10)
        	print(y1,z1)
        	Angles = []
        	for i in range(0,len(y1)):
        		point = [y1[i], z1[i]]
        		[x_c, y_c, z_c] = closest_point(point)
        		position = [x_c, y_c, z_c]
        		A = point_to_angle(position)
        		Angles.append(A)
	elif movement == 'Circular':
        # full circle
        	[x, y, z] = angle_to_point(domLocAngle)
            # Check to make sure circle is doable
        	if y + 3*r_c > R:
        		y -= 3*r_c
        	elif y - 3*r_c < -1*R:
        		y += 3*r_c
                
        	if z + 3*r_c > R:
        		z -= 3*r_c
        	elif z - 3*r_c < -1*R:
        		z += 3*r_c      
                
        	y1, z1 = make_full_circle(r_c,y,z,10)
        	Angles = []
        	for i in range(0,len(y1)):
        		point = [y1[i], z1[i]]
        		[x_c, y_c, z_c] = closest_point(point)
        		position = [x_c, y_c, z_c]
        		A = point_to_angle(position)
        		Angles.append(A)

    
    
#	position = closest_point([4,5])
#	print(position)
#	angle = point_to_angle(position)
#	print(angle)
    
    
#    biglist = domHandFlexions + [domHandFlexTime] \
#			+ nonDomHandFlexions + [nonDomHandFlexTime] \
#			+ domLocAngle + [domLocMoveTime] \
#			+ nonDomLocAngle + [nonDomLocMoveTime]
#	print(row["EntryID"], biglist)




































