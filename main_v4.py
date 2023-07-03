# Photo Mosaic Generator
# Given a image, create a mosaic based of another set of images with a color filter depending the dominant color of the image section.
# Getting the dominant color of the cuadrant and then analyzing the hole set of images to replace the dominant color with the image which
# rgb is closer that the one we are looking.
# Arturo Lopez. April 20, 2022.  email: arlopf95@gmail.com
#-----------------------------------------------------------------------------------------------------------------------------------------
import cv2		  # opencv
import xlsxwriter # To manipulate xlx sheet
import numpy as np

# Resize the image to a int number that we can use
def resizeImage(img, r_h, r_w): 
	width = int(img.shape[1]) # Get width pixels of image
	height = int(img.shape[0]) # Get height pixels of image
	#print(width%r_w, height%r_h)
	width = width - width%r_w
	height = height - height%r_h
	dim = (width, height ) # Resize to have an int numbers of small images
	resizedImg = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
	print("Resized dim = ",dim)
	return resizedImg

# Print the total numbers of images that is going to be used.
def totalImagesUsed(img, r_h, r_w):
	height = int(img.shape[0]) 
	width = int(img.shape[1])
	imgs_vertical = height/r_h
	imgs_horizontal = width/r_w
	total_imgs = (height/r_h)*(width/r_w)
	print("Total images used = ", total_imgs)

# Create an image with grid to easily identify the sections of the target image
def gridImage(img, r_h, r_w):
	height = int(img.shape[0]) 
	width = int(img.shape[1])
	for i in range(0, width, r_w):	 
		cv2.line(img, (i,0), (i, height), (255, 255, 255), 1)
	for i in range(0, height, r_h):
		cv2.line(img, (0,i), (width, i), (255, 255, 255), 1)
	return img

# Take an image and make it square from center, taking care to take the maximum number of pixels
def squareImg(img): 
	width = int(img.shape[1]) # Get width pixels of image
	height = int(img.shape[0]) # Get height pixels of image
	dim = (width, height) 
	if (width > height):
		img = img[0:height, int((width-height)/2):int(width-((width-height)/2))]
	else:
		img = img[int((height-width)/2):int(height-((height-width)/2)), 0:width]
	return img

# Scale images to form the smaller set of images, resize the img to r_h, r_w
def scaleImage(img, r_h, r_w):
	img = cv2.resize(img, (r_h,r_w), interpolation = cv2.INTER_AREA)
	return img

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def color_to_hex(color): # from 255 -> ff
	return '%02x' % color

# Get all the dominant colors from cuadrants of the target image
# Return the image with the dominant colors for each cuadrant and return a list of dominants colors
def getAllDominantsColors(img, r_h, r_w):
	width = int(img.shape[1])
	height = int(img.shape[0])

	# Get the dominant color of the cuadrants
	num_row = height/r_h	# number of rows
	num_col = width/r_w		# number of columns

	# Let´s try to get the sum of rgb of all the pixels in the section and get the average
	bsum = gsum = rsum = 0 # summatory of values
	color = 0
	colorsList = []
	for m in range(0, int(num_row)):
		for n in range(0, int(num_col)):
			bsum = gsum = rsum = 0 
			colorsList.append(color) # Create a list with all the dominants colors of the cuadrants
			for x in range(m*r_h, m*r_h+r_h): # number of column * r_w
				for y in range (n*r_w, n*r_w+r_w):
					b,g,r = (img[x,y])
					bsum += b
					gsum += g
					rsum += r

				# Assigned the dominant color to all the pixels in the kluster getting the sum b,g,r (r,g,b) divided with the number of pixels
				for y in range (n*r_w, n*r_w+r_w):
					(img[x,y]) = round(bsum/(r_w*r_w)), round(gsum/(r_w*r_w)), round(rsum/(r_w*r_w))
					color = rgb_to_hex((int(round(rsum/(r_w*r_w))),int(round(gsum/(r_w*r_w))),int(round(bsum/(r_w*r_w)))))
	colorsList.append(color)
	return img, colorsList

# Return the dominant color in rgb_to_hex of a single image
def getAverageColor(img):
	avg_color_per_row = np.average(img, axis=0)
	avg_color = np.average(avg_color_per_row, axis=0) # blue, green, red
	blue = int(round(avg_color[0]))
	green = int(round(avg_color[1]))
	red = int(round(avg_color[2]))
	color = rgb_to_hex((red, green, blue))
	return color

# Return a list including all the average colors of the set of pictures
def getAvgColorSet(totalNumberSet):
	colorsListSet = []
	colorsListSet.append(0)
	dirSet = "E:/Projects/photoMosaicGenerator/set_Images_rickandmorty/r_m_"
	for i in range (1, totalNumberSet+1):
		img = cv2.imread(dirSet+ str(i) +".jpg")
		img = squareImg(img)
		colorsListSet.append(getAverageColor(img))
	return colorsListSet


# Select the image from set that has the less different value from the color value we are looking
def selectImageFromSet2(color, colorsListSet, totalNumberSet):
	imgSelected = 1
	diff = 100000000
	for i in range(1, totalNumberSet+1):
		newDiff = abs(int(color, 16) - int(colorsListSet[i], 16))
		if (newDiff < diff):
			diff = newDiff
			imgSelected = i
	img = cv2.imread("E:/Projects/photoMosaicGenerator/set_Images_rickandmorty/r_m_"+ str(imgSelected) +".jpg")
	img = squareImg(img)
	return img


# Create the mosaic of random images, taking care of the size of the images
def createMosaic(colorsList, colorsListSet, r_h, r_w, imgs_horizontal, imgs_vertical, totalNumberSet):
	# Create the first row of Images
	print ("Creating Photo Mosaic")
	print("1/" + str(imgs_vertical) + " LOADING... " + str(int((0/imgs_vertical)*100)) + "%")
	setImg = selectImageFromSet2(colorsList[1], colorsListSet, totalNumberSet)
	setImg = cv2.resize(setImg, (r_h,r_w), interpolation = cv2.INTER_AREA) # Resize the crop image to the size of the smalls pieces of the target image

	setImg2 = selectImageFromSet2(colorsList[2], colorsListSet, totalNumberSet)
	setImg2 = cv2.resize(setImg2, (r_h,r_w), interpolation = cv2.INTER_AREA) # Resize the crop image to the size of the smalls pieces of the target image

	mosaicH1 = np.concatenate((setImg, setImg2), axis = 1) # Concatenate both images to start creating the mosaic
	for i in range (2, int(imgs_horizontal)): # Create first row of images
		setImg = selectImageFromSet2(colorsList[i+1], colorsListSet, totalNumberSet)
		setImg = cv2.resize(setImg, (r_h,r_w), interpolation = cv2.INTER_AREA) # Resize the crop image to the size of the smalls pieces of the target image
		mosaicH1 = np.concatenate((mosaicH1, setImg), axis = 1)

	# Create second row of imgages
	print("2/" + str(imgs_vertical)+ " LOADING... " + str(int((1/imgs_vertical)*100)) + "%")
	setImg = selectImageFromSet2(colorsList[imgs_horizontal+1], colorsListSet, totalNumberSet)
	setImg = cv2.resize(setImg, (r_h,r_w), interpolation = cv2.INTER_AREA) # Resize the crop image to the size of the smalls pieces of the target image

	setImg2 = selectImageFromSet2(colorsList[imgs_horizontal+2], colorsListSet, totalNumberSet)
	setImg2 = cv2.resize(setImg2, (r_h,r_w), interpolation = cv2.INTER_AREA) # Resize the crop image to the size of the smalls pieces of the target image

	mosaicH2 = np.concatenate((setImg, setImg2), axis = 1) # Concatenate both images to start creating the mosaic
	for i in range (2, int(imgs_horizontal)):
		setImg = selectImageFromSet2(colorsList[imgs_horizontal+i+1], colorsListSet, totalNumberSet)
		setImg = cv2.resize(setImg, (r_h,r_w), interpolation = cv2.INTER_AREA) # Resize the crop image to the size of the smalls pieces of the target image
		mosaicH2 = np.concatenate((mosaicH2, setImg), axis = 1)

	# Concatenate the first two rows of mosaic in vertical
	mosaic = np.concatenate((mosaicH1, mosaicH2), axis = 0)
	
	for i in range(2, int(imgs_vertical)):
		print(str(i+1)+ "/" + str(imgs_vertical) + " LOADING... " + str(int((i/imgs_vertical)*100)) + "%")
		setImg = selectImageFromSet2(colorsList[imgs_horizontal*i+1], colorsListSet, totalNumberSet)
		setImg = cv2.resize(setImg, (r_h,r_w), interpolation = cv2.INTER_AREA) # Resize the crop image to the size of the smalls pieces of the target image

		setImg2 = selectImageFromSet2(colorsList[imgs_horizontal*i+2], colorsListSet, totalNumberSet)
		setImg2 = cv2.resize(setImg2, (r_h,r_w), interpolation = cv2.INTER_AREA) # Resize the crop image to the size of the smalls pieces of the target image
		mosaicH = np.concatenate((setImg, setImg2), axis = 1) # Concatenate both images to start creating the mosaic

		for w in range(2, int(imgs_horizontal)):
			setImg = selectImageFromSet2(colorsList[imgs_horizontal*i+w+1], colorsListSet, totalNumberSet)
			setImg = cv2.resize(setImg, (r_h,r_w), interpolation = cv2.INTER_AREA) # Resize the crop image to the size of the smalls pieces of the target image
			mosaicH = np.concatenate((mosaicH, setImg), axis = 1)
		mosaic = np.concatenate((mosaic, mosaicH), axis = 0)
	print("MOSAIC COMPLETE 100%")
	return mosaic


def overlapImages(img1, img2, alpha, beta):
	# Now we just need to combine the dominant color (dominant_color) and the mosaic (mosaic).
	overlapImg = cv2.addWeighted(img1, alpha, img2, beta, 0)
	return overlapImg

def main():

	# Read Target Image
	img = cv2.imread("E:/Projects/photoMosaicGenerator/target_rickandmorty_3.jpg")
	#cv2.imshow('Target Image', img) # Display the target image resized

	totalNumberSet = 60 # Number of total images on set

	r_h = 70 # height of small image, change for the desire number of total images
	r_w = 70 # width of small image

	img = resizeImage(img, r_h, r_w) # Resized the target image so we can have an int number of small images, based on r_h and r_w.
	#cv2.imshow('Resize Image', img)
	cv2.imwrite('resized.jpg', img)

	width = int(img.shape[1])
	height = int(img.shape[0])
	imgs_vertical = int(height/r_h)
	imgs_horizontal = int(width/r_w)

	# Print number of total images that are going to be needed.
	totalImagesUsed(img, r_h, r_w) 

	# Get all the dominant colors from cuadrants of the target image
	dominantColor, colorsList = getAllDominantsColors(img, r_h, r_w) 
	#cv2.imshow("Dominant Color", dominantColor)

	colorsListSet = getAvgColorSet(totalNumberSet) # List of the avg color of the images on the set
	
	
	#mosaic = createMosaic(colorsList, r_h, r_w, imgs_horizontal, imgs_vertical, totalNumberSet)
	mosaic = createMosaic(colorsList, colorsListSet, 200, 200, imgs_horizontal, imgs_vertical, totalNumberSet)
	cv2.imwrite('mosaic.jpg', mosaic)

	
	#-----------------------------------------------------------------------------------------------------
	# Testing if the resize of the dominant color does not have any definition issue.
	mosaic = cv2.imread("E:/Projects/photoMosaicGenerator/mosaic.jpg")
	width = int(mosaic.shape[1])
	height = int(mosaic.shape[0])
	dominantColor = cv2.resize(dominantColor, (width, height), interpolation = cv2.INTER_AREA)
	cv2.imwrite('dominantColor.jpg', dominantColor)
	#-----------------------------------------------------------------------------------------------------

	overlapImg = overlapImages(dominantColor, mosaic, 0.5, 0.5)
	cv2.imwrite('overlapImg.jpg', overlapImg)

	overlapImg2 = overlapImages(dominantColor, mosaic, 0.4, 0.6)
	cv2.imwrite('overlapImg2.jpg', overlapImg2)

	overlapImg3 = overlapImages(dominantColor, mosaic, 0.3, 0.7)
	cv2.imwrite('overlapImg3.jpg', overlapImg3)

	overlapImg4 = overlapImages(dominantColor, mosaic, 0.2, 0.8)
	cv2.imwrite('overlapImg4.jpg', overlapImg4)

	overlapImg5 = overlapImages(dominantColor, mosaic, 0.1, 0.9)
	cv2.imwrite('overlapImg5.jpg', overlapImg5)

	# Get a grid image to have a better idea of the sections of the target image
	gridImg = cv2.imread("E:/Projects/photoMosaicGenerator/resized.jpg")
	gridImg = gridImage(gridImg, r_h, r_w)
	#cv2.imshow('Grid Image', gridImg)
	cv2.imwrite('gridImage.jpg', gridImg)
	
	print("Done!")
	cv2.waitKey(0) # Waits until a key is pressed
	cv2.destroyAllWindows() # Destroys the window showing image

main()