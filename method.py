import cv2
import numpy as np

def loadImage(filename):
        sourceImg = cv2.imread(filename, cv2.IMREAD_COLOR)
        # sourceImg = cv2.imread(filename, 0)
        # print(sourceImg.shape)
        return sourceImg

def resizeImage(sourceImg, destImg_W, destImg_H):
        # scale image if needed
        # get sourceImg W and H
        sourceImg_H = sourceImg.shape[0]
        sourceImg_W = sourceImg.shape[1] 
        if (sourceImg_W != destImg_W or sourceImg_H != destImg_H):
                resultImg = cv2.resize(sourceImg, (destImg_W, destImg_H), cv2.INTER_NEAREST)
                return resultImg
        return sourceImg

"""
JPG quality -> from 0 to 100
"""
def saveImage_JPG(sourceImg, destImg_W, destImg_H, filename, quality):
        resultImg = resizeImage(sourceImg, destImg_W, destImg_H)
        fullFilePath = "%s.jpg" % filename 
        cv2.imwrite(fullFilePath, resultImg, [cv2.IMWRITE_JPEG_QUALITY, quality])

"""
BMP
"""
def saveImage_BMP(sourceImg, destImg_W, destImg_H, filename): 
        resultImg = resizeImage(sourceImg, destImg_W, destImg_H)
        fullFilePath = "%s.bmp" % filename 
        cv2.imwrite(fullFilePath, resultImg)

"""
PNG quality -> from 0 to 9
"""
def saveImage_PNG(sourceImg, destImg_W, destImg_H, filename, compression):
        resultImg = resizeImage(sourceImg, destImg_W, destImg_H)
        fullFilePath = "%s.png" % filename 
        cv2.imwrite(fullFilePath, resultImg, [cv2.IMWRITE_PNG_COMPRESSION, compression])

def createWatermarkImage(markString, Img_W, Img_H):
        # np.uint8(bgImg)
        blank_image = np.zeros((Img_H, Img_W), np.uint8)
        # put text on left top corner
        # set font type
        font = cv2.FONT_HERSHEY_COMPLEX
        # set fontSize basen on imagesize
        fontSize = 0.5
        if Img_H <= 200:
                fontSize = 0.5
        elif Img_H <= 400:
                fontSize = 0.6
        elif Img_H <= 800:
                fontSize = 0.8
        else:
                fontSize = 0.9
        pos_x = 10
        pos_Y = 30
        cv2.putText(blank_image, markString, (pos_x, pos_Y), font, fontSize, (255, 255, 255), 1, cv2.LINE_AA)

        # symmertric
        b_h = blank_image.shape[0]
        b_w = blank_image.shape[1]
        for i in range(0,int(0.5*b_h)):
                for j in range(0,b_w):
                        blank_image[b_h-1-i, b_w-1-j] = blank_image[i,j]

        mapping_H = np.random.permutation(b_h)
        mapping_W = np.random.permutation(b_w)
        return blank_image, mapping_H, mapping_W

def encodeWatermarkImage(waterMarkImg, mapping_H, mapping_W):
        imageH = waterMarkImg.shape[0]
        imageW = waterMarkImg.shape[1]
        encodeWatermarkImage = np.zeros((imageH, imageW))
        for i in range(0,imageH):
                for j in range(0,imageW):
                        encodeWatermarkImage[i,j] = waterMarkImg[mapping_H[i],mapping_W[j]]
        return encodeWatermarkImage

def decodeWatermarkImage(waterMarkImg, mapping_H, mapping_W):
        # revert array
        imageH = waterMarkImg.shape[0]
        imageW = waterMarkImg.shape[1]
        decodeWaterMarkImage = np.zeros((imageH, imageW))
        for i in range(0, imageH):
                for j in range(0, imageW):
                        decodeWaterMarkImage[mapping_H[i], mapping_W[j]] = waterMarkImg[i,j]
        return decodeWaterMarkImage

def addWatermarkImage(sourceImg, waterMarkImg, mapping_H, mapping_W):
        #RGB 
        sourceImg_B = sourceImg[:,:,0]
        sourceImg_G = sourceImg[:,:,1]
        sourceImg_R = sourceImg[:,:,2]
        f_sourceImg_B = cv2.dft(np.float32(sourceImg_B),flags = cv2.DFT_COMPLEX_OUTPUT)
        f_sourceImg_G = cv2.dft(np.float32(sourceImg_G),flags = cv2.DFT_COMPLEX_OUTPUT)
        f_sourceImg_R = cv2.dft(np.float32(sourceImg_R),flags = cv2.DFT_COMPLEX_OUTPUT)
        #watermark
        # encode watermark image 
        encodeImg = encodeWatermarkImage(waterMarkImg, mapping_H, mapping_W)
        encodeImg *= float(4)

        # merge two f_images
        # store watermark int B channel
        f_sourceImg_B[:,:,0] = f_sourceImg_B[:,:,0] + encodeImg
        # f_sourceImg_G[:,:,0] = f_sourceImg_G[:,:,0] + encodeImg
        # f_sourceImg_R[:,:,0] = f_sourceImg_R[:,:,0] + encodeImg

        new_sourceImg_B = cv2.idft(f_sourceImg_B) 
        new_sourceImg_B = cv2.magnitude(new_sourceImg_B[:,:,0],new_sourceImg_B[:,:,1])
        new_sourceImg_G = cv2.idft(f_sourceImg_G) 
        new_sourceImg_G = cv2.magnitude(new_sourceImg_G[:,:,0],new_sourceImg_G[:,:,1])
        new_sourceImg_R = cv2.idft(f_sourceImg_R)
        new_sourceImg_R = cv2.magnitude(new_sourceImg_R[:,:,0],new_sourceImg_R[:,:,1])

        resultImg = np.zeros((sourceImg.shape[0], sourceImg.shape[1], 3))
        resultImg[:,:,0] = new_sourceImg_B
        resultImg[:,:,1] = new_sourceImg_G
        resultImg[:,:,2] = new_sourceImg_R
        # normalize to 0 ~ 255
        resultImg *= 255.0/resultImg.max() 
        resultImg = np.uint8(resultImg)
        return resultImg

"""
input original image and marked image
return watermark Image
"""
def extractWatermark(originalImg, inputImg, mapping_H, mapping_W):
        # original image
        originalImg_B = originalImg[:,:,0]
        originalImg_G = originalImg[:,:,1]
        originalImg_R = originalImg[:,:,2]
        f_originalImg_B = cv2.dft(np.float32(originalImg_B),flags = cv2.DFT_COMPLEX_OUTPUT)
        f_originalImg_G = cv2.dft(np.float32(originalImg_G),flags = cv2.DFT_COMPLEX_OUTPUT)
        f_originalImg_R = cv2.dft(np.float32(originalImg_R),flags = cv2.DFT_COMPLEX_OUTPUT)
        # MarkedImage
        inputImg_B = inputImg[:,:,0]
        inputImg_G = inputImg[:,:,1]
        inputImg_R = inputImg[:,:,2]
        f_inputImg_B = cv2.dft(np.float32(inputImg_B),flags = cv2.DFT_COMPLEX_OUTPUT)
        f_inputImg_G = cv2.dft(np.float32(inputImg_G),flags = cv2.DFT_COMPLEX_OUTPUT)
        f_inputImg_R = cv2.dft(np.float32(inputImg_R),flags = cv2.DFT_COMPLEX_OUTPUT)

        encodeImg_B = f_inputImg_B[:,:,0] - f_originalImg_B[:,:,0]
        # encodeImg_G = f_inputImg_G[:,:,0] - f_originalImg_G[:,:,0]
        # encodeImg_R = f_inputImg_R[:,:,0] - f_originalImg_R[:,:,0]

        decodeImg_B = decodeWatermarkImage(encodeImg_B, mapping_H, mapping_W)
        decodeImg_B *= 0.25
        decodeImg_B *= 255.0/decodeImg_B.max() 
        # decodeImg_B[:,:] = 255
        decodeImg_B[decodeImg_B[:,:]<10] = 0
        decodeImg_B[decodeImg_B[:,:]>=10] = 255
        markedImage = np.uint8(decodeImg_B)


        return markedImage