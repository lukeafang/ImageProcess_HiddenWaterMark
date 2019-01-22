#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 15:25:17 2018

@author: lukefang
"""
import os
import sys
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QLineEdit,QComboBox,
                             QPushButton, QFileDialog, QSizePolicy, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt

from method import loadImage, saveImage_JPG, saveImage_BMP, saveImage_PNG, createWatermarkImage, addWatermarkImage, extractWatermark

"""
MainWindow of application
"""
class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        # gobal data

        # source Image
        self.sourceImg = None
        self.sourceImg_W = 0
        self.sourceImg_H = 0

        # waterMark Image
        self.watermarkImg = None
        # mapping function for encode/deconde watermark
        self.mapping_H = 0
        self.mapping_W = 0

        # Image mixed by sourceImg and watermarkImg
        self.markedImg = None

        # extract watermarkImg
        self.extractWatermarkImg = None

        self.display_QImage = None

        self.roiImage = None

        self.initUI()

    def initUI(self):
        self.resize(1250, 700)
        self.setWindowTitle('ImageProcess Application')

        itemW = 30
        itemH = 20
        # item for display image
        self.sourceImg_label = QLabel('source Image', self)
        self.sourceImg_label.setAlignment(Qt.AlignCenter)
        self.sourceImg_label.setStyleSheet(
            'border: gray; border-style:solid; border-width: 1px;')
        self.sourceImg_label.resize(400, 300)
        self.sourceImg_label.move(15, 15)
        self.sourceImg_label.mousePressEvent = self.sourceImageLabel_Clicked
        
        # show size of source image
        self.sourceImgSize_label = QLabel('Size(WxH): ', self)
        self.sourceImgSize_label.resize(itemW+50, itemH)
        tempItemX = 400 + 15 - itemW*6
        tempItemY = 300 + 15
        self.sourceImgSize_label.move(tempItemX, tempItemY)

        self.sourceImgSize_text = QLineEdit('0X0', self)
        self.sourceImgSize_text.resize(itemW*3, itemH)
        self.sourceImgSize_text.setReadOnly(True)
        tempItemX = tempItemX + itemW + 50
        self.sourceImgSize_text.move(tempItemX, tempItemY)        

        self.resultImg1_label = QLabel('result Image 1', self)
        self.resultImg1_label.setAlignment(Qt.AlignCenter)
        self.resultImg1_label.setStyleSheet(
            'border: gray; border-style:solid; border-width: 1px;')
        self.resultImg1_label.resize(400, 300)
        self.resultImg1_label.move(15, 350)
        # show size of result image
        self.resultImgSize_label = QLabel('Size(WxH): ', self)
        self.resultImgSize_label.resize(itemW+50, itemH)
        tempItemX = 400 + 15 - itemW*6
        tempItemY = 650
        self.resultImgSize_label.move(tempItemX, tempItemY)

        self.resultImgSize_text = QLineEdit('0X0', self)
        self.resultImgSize_text.resize(itemW*3, itemH)
        self.resultImgSize_text.setReadOnly(True)
        tempItemX = tempItemX + itemW + 50
        self.resultImgSize_text.move(tempItemX, tempItemY) 

        self.resultImg2_label = QLabel('result Image 2', self)
        self.resultImg2_label.setAlignment(Qt.AlignCenter)
        self.resultImg2_label.setStyleSheet(
            'border: gray; border-style:solid; border-width: 1px;')
        self.resultImg2_label.resize(400, 300)
        self.resultImg2_label.move(425, 350)      

        self.resultImg3_label = QLabel('result Image 3', self)
        self.resultImg3_label.setAlignment(Qt.AlignCenter)
        self.resultImg3_label.setStyleSheet(
            'border: gray; border-style:solid; border-width: 1px;')
        self.resultImg3_label.resize(400, 300)
        self.resultImg3_label.move(835, 350)           

        itemX = 430
        itemY = 15
        # load Image Btn
        self.loadImage_Btn = QPushButton('Load Image', self)
        # set evenet handler
        self.loadImage_Btn.clicked.connect(self.loadImageBtn_Clicked)
        self.loadImage_Btn.move(itemX, itemY)
        itemY += 30

        #Convert Image Btn
        self.convertImage_Btn = QPushButton('Convert Image', self)
        # set evenet handler
        self.convertImage_Btn.clicked.connect(self.convertImageBtn_Clicked)
        self.convertImage_Btn.move(itemX, itemY)
        self.convert_FileName_label = QLabel('File Name:', self)
        self.convert_FileName_label.resize(itemW+40, itemH)
        self.convert_FileName_label.move(itemX+130, itemY+5)
        self.convert_FileName_text = QLineEdit('convert',self)
        self.convert_FileName_text.resize(itemW+60, itemH)
        self.convert_FileName_text.move(itemX+200, itemY+5)
        itemY += 30

        self.convertImage_fixRatio_chk = QCheckBox("Fix Ratio", self)
        self.convertImage_fixRatio_chk.stateChanged.connect(
            self.fixRatioChange)
        self.convertImage_fixRatio_chk.move(itemX, itemY)
        itemY += 30

        itemW = 80
        itemH = 20
        tempItemX = itemX

        self.convert_W_label = QLabel('Convert Width:', self)
        self.convert_W_label.resize(itemW+10, itemH)
        self.convert_W_label.move(tempItemX, itemY)
        tempItemX = tempItemX + itemW + 15
        self.convert_W_text = QLineEdit(self)
        self.convert_W_text.resize(itemW, itemH)
        self.convert_W_text.move(tempItemX, itemY)
        tempItemX = tempItemX + itemW + 10

        self.convert_H_label = QLabel('Convert Height:', self)
        self.convert_H_label.resize(itemW+20, itemH)
        self.convert_H_label.move(tempItemX, itemY)
        tempItemX = tempItemX + itemW + 20
        self.convert_H_text = QLineEdit(self)
        self.convert_H_text.resize(itemW, itemH)
        self.convert_H_text.move(tempItemX, itemY)
        itemY += 30

        # convert file format selectrion
        tempItemX = 430
        itemW = 50
        itemH = 20
        self.convert_format_label = QLabel('Format:', self)
        self.convert_format_label.resize(itemW, itemH)
        self.convert_format_label.move(tempItemX, itemY)

        itemW = 100
        tempItemX = tempItemX + 55
        self.convert_format_cb = QComboBox(self)
        self.convert_format_cb.addItem("jpeg")
        self.convert_format_cb.addItem("bmp")
        self.convert_format_cb.addItem("png")
        self.convert_format_cb.resize(itemW, itemH)
        self.convert_format_cb.move(tempItemX, itemY)
        self.convert_format_cb.currentTextChanged.connect(self.convert_format_cb_changed)
   

        # convert file quality
        tempItemX = tempItemX + itemW + 10
        itemW = 83
        self.convert_fileQuality_label = QLabel('Quality:', self)
        self.convert_fileQuality_label.resize(itemW, itemH)
        self.convert_fileQuality_label.move(tempItemX, itemY)    
        
        tempItemX = tempItemX + itemW + 5
        itemW = 100
        self.convert_fileQuality_cb = QComboBox(self)
        self.convert_fileQuality_cb.addItem("High")
        self.convert_fileQuality_cb.addItem("Medium")
        self.convert_fileQuality_cb.addItem("Low")
        self.convert_fileQuality_cb.resize(itemW, itemH)
        self.convert_fileQuality_cb.move(tempItemX, itemY)
        
        # 
        itemY += 40
        tempItemX = 430
        self.hLine_label = QLabel(self)
        self.hLine_label.setAlignment(Qt.AlignCenter)
        self.hLine_label.setStyleSheet(
            'border: gray; border-style:solid; border-width: 1px;')
        self.hLine_label.resize(400, 1)
        self.hLine_label.move(tempItemX, itemY)   

        #Watermark
        itemY += 20
        tempItemX = 430
        self.watermark_label = QLabel('Watermark:', self)
        self.watermark_label.resize(itemW, itemH)
        self.watermark_label.move(tempItemX, itemY)   
        tempItemX = tempItemX + itemW*0.8
        self.watermark_text = QLineEdit('This is a test.', self)
        self.watermark_text.resize(itemW, itemH)
        self.watermark_text.move(tempItemX, itemY)
        tempItemX += itemW
        #add watermark Btn
        self.createWatermarkBtn = QPushButton('Generate', self)
        # set evenet handler
        self.createWatermarkBtn.clicked.connect(self.createWatermarkBtn_Clicked)
        self.createWatermarkBtn.move(tempItemX, itemY-4)

        itemY += 30
        tempItemX = 430
        self.addWatermarkBtn = QPushButton('Add WaterMark', self)
        self.addWatermarkBtn.clicked.connect(self.addWatermarkBtn_Clicked)
        self.addWatermarkBtn.move(tempItemX, itemY-4)
 
        itemY += 30
        tempItemX = 430
        self.extractWatermarkBtn = QPushButton('Extract WaterMark', self)
        self.extractWatermarkBtn.clicked.connect(self.extractWatermarkBtn_Clicked)
        self.extractWatermarkBtn.move(tempItemX, itemY)

        # cut image
        tempItemX = 840
        itemY = 20
        self.cutImageBtn = QPushButton('Cut Image', self)
        self.cutImageBtn.clicked.connect(self.cutImageBtn_Click)
        self.cutImageBtn.move(tempItemX, itemY-4)

        itemY += 30
        itemW = 80
        itemH = 20
        tempItemX = 850
        self.cutImage_PosX_label = QLabel('Pos X:', self)
        self.cutImage_PosX_label.resize(itemW+10, itemH)
        self.cutImage_PosX_label.move(tempItemX, itemY)
        tempItemX = tempItemX + itemW + 15
        self.cutImage_PosX_text = QLineEdit(self)
        self.cutImage_PosX_text.resize(itemW, itemH)
        self.cutImage_PosX_text.move(tempItemX, itemY)
        tempItemX = tempItemX + itemW + 10

        self.cutImage_PosY_label = QLabel('Pos Y:', self)
        self.cutImage_PosY_label.resize(itemW+20, itemH)
        self.cutImage_PosY_label.move(tempItemX, itemY)
        tempItemX = tempItemX + itemW + 20
        self.cutImage_PosY_text = QLineEdit(self)
        self.cutImage_PosY_text.resize(itemW, itemH)
        self.cutImage_PosY_text.move(tempItemX, itemY)

        itemY += 25
        tempItemX = 850
        self.cutImage_W_label = QLabel('ROI Width:', self)
        self.cutImage_W_label.resize(itemW+10, itemH)
        self.cutImage_W_label.move(tempItemX, itemY)
        tempItemX = tempItemX + itemW + 15
        self.cutImage_W_text = QLineEdit(self)
        self.cutImage_W_text.resize(itemW, itemH)
        self.cutImage_W_text.move(tempItemX, itemY)
        tempItemX = tempItemX + itemW + 10

        self.cutImage_H_label = QLabel('ROI Height:', self)
        self.cutImage_H_label.resize(itemW+20, itemH)
        self.cutImage_H_label.move(tempItemX, itemY)
        tempItemX = tempItemX + itemW + 20
        self.cutImage_H_text = QLineEdit(self)
        self.cutImage_H_text.resize(itemW, itemH)
        self.cutImage_H_text.move(tempItemX, itemY)

        itemY += 30
        tempItemX = 850
        self.roi_image_label = QLabel('ROI Image', self)
        self.roi_image_label.setAlignment(Qt.AlignCenter)
        self.roi_image_label.setStyleSheet(
            'border: gray; border-style:solid; border-width: 1px;')
        self.roi_image_label.resize(200, 150)
        self.roi_image_label.move(tempItemX, itemY)

        itemY += 160
        self.cutImageSaveBtn = QPushButton('Save as', self)
        self.cutImageSaveBtn.clicked.connect(self.cutImageSaveBtn_Clicked)
        self.cutImageSaveBtn.move(tempItemX, itemY-4)  

        itemW = 100
        tempItemX = tempItemX + 80
        self.roi_convert_format_cb = QComboBox(self)
        self.roi_convert_format_cb.addItem("jpeg")
        self.roi_convert_format_cb.addItem("bmp")
        self.roi_convert_format_cb.addItem("png")
        self.roi_convert_format_cb.resize(itemW, itemH)
        self.roi_convert_format_cb.move(tempItemX, itemY + 2)

        itemW = 70
        itemY += 30
        tempItemX = 850
        self.roi_convert_FileName_label = QLabel('File Name:', self)
        self.roi_convert_FileName_label.resize(itemW, itemH)
        self.roi_convert_FileName_label.move(tempItemX, itemY)
        self.roi_convert_FileName_text = QLineEdit('roiImage', self)
        self.roi_convert_FileName_text.resize(itemW, itemH)
        self.roi_convert_FileName_text.move(tempItemX+itemW+5, itemY)


    def keyPressEvent(self, e):    
        if e.key() == Qt.Key_Escape:
            self.close()

    def loadImageBtn_Clicked(self):
        filename, _ = QFileDialog.getOpenFileName(
            None, 'Buscar Imagen', '.', 'Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)')
        if filename:
            # reset other images        
            # # waterMark Image
            self.watermarkImg = None
            # Image mixed by sourceImg and watermarkImg
            self.markedImg = None
            # extract watermarkImg
            self.extractWatermarkImg = None

            self.sourceImg = loadImage(filename)
            self.sourceImg_H = self.sourceImg.shape[0]
            self.sourceImg_W = self.sourceImg.shape[1]
            self.updateUI()
            self.display_QImage = self.displayImage(self.sourceImg, self.sourceImg_label)

    
    def convert_format_cb_changed(self, newText):
        self.convert_fileQuality_label.setVisible(True)
        self.convert_fileQuality_cb.setVisible(True)
        if newText == "bmp":
            self.convert_fileQuality_label.setVisible(False)
            self.convert_fileQuality_cb.setVisible(False)
        elif newText == "png":
            self.convert_fileQuality_label.setText("Compression: ")
        else:
            # jpg
            self.convert_fileQuality_label.setText("Quality: ")
            
        # QMessageBox.about(self, "Title", 'please load a image first.')
        return

    """
    convert openCV Image to QT image and disply on GUI
    """
    def displayImage(self, openCVImg, displayLabel):
        size = openCVImg.shape
        step = openCVImg.size / size[0]

        qformat = QImage.Format_Indexed8
        if len(size) == 3:
            if size[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        displayImg = QImage(openCVImg, size[1], size[0], step, qformat)
        # Swap r and b channel of QImage
        displayImg = displayImg.rgbSwapped()

        qPixMap = QPixmap.fromImage(displayImg)
        label_w = displayLabel.width()
        label_h = displayLabel.height()
        scaledQpixmap = qPixMap.scaled( label_w, label_h, Qt.KeepAspectRatio)
        displayLabel.setPixmap(scaledQpixmap)

        # displayLabel.setPixmap(QPixmap.fromImage(displayImg))
        # displayLabel.setScaledContents(True)
        # displayLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        displayLabel.repaint()
        return displayImg

    def updateUI(self):
        tempStr = "%s X %s" % (self.sourceImg_W , self.sourceImg_H)
        self.sourceImgSize_text.setText(tempStr)
        tempStr = "%s" % self.sourceImg_W
        self.convert_W_text.setText(tempStr)
        tempStr = "%s" % self.sourceImg_H
        self.convert_H_text.setText(tempStr)

        if self.watermarkImg is not None:
            resultImage_H = self.watermarkImg.shape[0]
            resultImage_W = self.watermarkImg.shape[1]     
            tempStr = "%s X %s" % (resultImage_W , resultImage_H)
            self.resultImgSize_text.setText(tempStr)

        return

    def fixRatioChange(self, state):
        if state == Qt.Checked:
            # hide H edit
            self.convert_H_label.setVisible(False)
            self.convert_H_text.setVisible(False)
        else:
            # hide H edit
            self.convert_H_label.setVisible(True)
            self.convert_H_text.setVisible(True)
        return

    """
    convert image to different format and size
    """
    def convertImageBtn_Clicked(self):
        if self.sourceImg is None:
            QMessageBox.about(self, "Title", 'please load a image first.')
            return
        if self.sourceImg_W <= 0:
            QMessageBox.about(self, "Title", 'please load a image first.')
            return
        if self.sourceImg_H <= 0:
            QMessageBox.about(self, "Title", 'please load a image first.')
            return
        # convert file Name
        fileName = self.convert_FileName_text.text()
        if len(fileName) == 0:
            fileName = 'convert'
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/output'
        fullFilePath = dir_path + '/' + fileName
        print(fullFilePath)
        # size of convert file W & H
        convertImg_W = int(self.convert_W_text.text())
        convertImg_H = int(self.convert_H_text.text())
        if convertImg_W <= 0:
            convertImg_W = self.sourceImg_W
        if convertImg_H <= 0:
            convertImg_H = self.sourceImg_H
        # if fixRatio is check, modify convert_W/H based on W
        if self.convertImage_fixRatio_chk.isChecked():
            # sourceImage ratio
            ratio = float(self.sourceImg_H) / float(self.sourceImg_W)
            convertImg_H = int(float(convertImg_W) * ratio)
        
        extension = str(self.convert_format_cb.currentText())
        if extension == 'jpeg':
            # quality, default is 95
            quality = 95
            quality_level = str(self.convert_fileQuality_cb.currentText())
            if quality_level == "High":
                quality = 95
            elif quality_level == "Medium":
                quality = 60
            else:
                # low quality level
                quality = 10
            saveImage_JPG(self.sourceImg, convertImg_W, convertImg_H, fullFilePath, quality)
        elif extension == 'bmp':
            # no quality option
            saveImage_BMP(self.sourceImg, convertImg_W, convertImg_H, fullFilePath)
            # print(extension)
        elif extension == 'png':
            # from 0 - 9, Default value is 3.
            # A higher value means a smaller size and longer compression time
            compression = 3
            compression_level = str(self.convert_fileQuality_cb.currentText())
            if compression_level == "High":
                compression = 8
            elif compression_level == "Medium":
                compression = 3
            else:
                # low quality level
                compression = 1
            saveImage_PNG(self.sourceImg, convertImg_W, convertImg_H, fullFilePath, compression)
        else:
            # unknown extension
            QMessageBox.about(self, "Title", 'Error. unknown extension')
            return
        QMessageBox.about(self, "Message", 'Convert Finished')

    """
    create a watermarkImage base on size of sourceimg
    """
    def createWatermarkBtn_Clicked(self):
        # check sourceImg loaded or not
        if self.sourceImg is None:
            QMessageBox.about(self, "Title", 'please load a image first.')
            return

        markString = self.watermark_text.text()
        self.watermarkImg, self.mapping_H, self.mapping_W = createWatermarkImage(markString, self.sourceImg_W, self.sourceImg_H)
        self.displayImage(self.watermarkImg, self.resultImg1_label)
        self.updateUI()
        return

    """
    mix watermarkimage and sourceImg to generate a new marked image
    """
    def addWatermarkBtn_Clicked(self):
        # check sourceImg loaded or not
        if self.sourceImg is None:
            QMessageBox.about(self, "Title", 'please load a source image first.')
            return
        # check watermark image generated or not
        if self.watermarkImg is None:
            QMessageBox.about(self, "Title", 'please generate a watermark image first.')
            return

        self.markedImg = addWatermarkImage(self.sourceImg, self.watermarkImg, self.mapping_H, self.mapping_W)
        self.displayImage(self.markedImg, self.resultImg2_label)
        # save markedImg
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/output'
        fullFilePath = dir_path + '/' + 'markedImg'
        saveImage_BMP(self.markedImg, self.markedImg.shape[1], self.markedImg.shape[0], fullFilePath)
        return

    def extractWatermarkBtn_Clicked(self):
        # check sourceImg loaded or not
        if self.sourceImg is None:
            QMessageBox.about(self, "Title", 'please load a source image first.')
            return
        # check watermark image generated or not
        if self.watermarkImg is None:
            QMessageBox.about(self, "Title", 'please generate a watermark image first.')
            return
        # check marked image created or not
        if self.markedImg is None:
            QMessageBox.about(self, "Title", 'please generate a marked image first.')
            return            

        self.extractWatermarkImg = extractWatermark(self.sourceImg, self.markedImg, self.mapping_H, self.mapping_W)
        self.displayImage(self.extractWatermarkImg, self.resultImg3_label)
        # save extractwatermarkImage
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/output'
        fullFilePath = dir_path + '/' + 'extractWatermark'
        saveImage_BMP(self.extractWatermarkImg, self.extractWatermarkImg.shape[1], self.extractWatermarkImg.shape[0], fullFilePath)
        return

    def cutImageBtn_Click(self):
        # check sourceImg loaded or not
        if self.sourceImg is None:
            QMessageBox.about(self, "Title", 'please load a source image first.')
            return
        # get roi value
        max_W = int(self.sourceImg.shape[1])
        max_H = int(self.sourceImg.shape[0])
        tempStr = self.cutImage_W_text.text()
        if len(tempStr) <= 0:
            return
        roi_W = int(tempStr)
        tempStr = self.cutImage_H_text.text()
        if len(tempStr) <= 0:
            return
        roi_H = int(tempStr)
        tempStr = self.cutImage_PosX_text.text()
        if len(tempStr) <= 0:
            return       
        posX = int(tempStr)
        tempStr = self.cutImage_PosY_text.text()
        if len(tempStr) <= 0:
            return       
        posY = int(tempStr)

        # check ROI param is correct
        if( (posX+roi_W) >= max_W ):
            QMessageBox.about(self, "Title", 'ROI param error (posX+roi_W) >= max_W')
            return
        if( (posY+roi_H) >= max_H ):
            QMessageBox.about(self, "Title", 'ROI param error (posY+roi_H) >= max_H')
            return

        self.roiImage = np.zeros((roi_H,roi_W,3))
        self.roiImage[:,:,:] = self.sourceImg[posY:(posY+roi_H), posX:(posX+roi_W),:]
        self.roiImage = np.uint8(self.roiImage)
        self.displayImage(self.roiImage, self.roi_image_label)
        
        return

    def cutImageSaveBtn_Clicked(self):
        if self.sourceImg is None:
            QMessageBox.about(self, "Title", 'please load a image first.')
            return
        if self.roiImage is None:
            QMessageBox.about(self, "Title", 'please cut a roi first.')
            return

        # convert file Name
        fileName = self.roi_convert_FileName_text.text()
        if len(fileName) == 0:
            fileName = 'roiImage'
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/output'
        fullFilePath = dir_path + '/' + fileName

        # size of convert file W & H
        roiImage_W = int(self.roiImage.shape[1])
        roiImage_H = int(self.roiImage.shape[0])
        
        extension = str(self.roi_convert_format_cb.currentText())
        if extension == 'jpeg':
            # quality, default is 95
            quality = 95
            saveImage_JPG(self.roiImage, roiImage_W, roiImage_H, fullFilePath, quality)
        elif extension == 'bmp':
            # no quality option
            saveImage_BMP(self.roiImage, roiImage_W, roiImage_H, fullFilePath)
            # print(extension)
        elif extension == 'png':
            # from 0 - 9, Default value is 3.
            # A higher value means a smaller size and longer compression time
            compression = 3
            saveImage_PNG(self.roiImage, roiImage_W, roiImage_H, fullFilePath, compression)
        else:
            # unknown extension
            QMessageBox.about(self, "Title", 'Error. unknown extension')
            return
        QMessageBox.about(self, "Message", 'save Finished')       
        return

    def sourceImageLabel_Clicked(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            tempStr = "click point (%s, %s)" % (x , y)
            print(tempStr)
            if self.display_QImage is not None:
                # c = self.display_QImage.pixel(x,y) 
                # print(c)
                d = self.display_QImage.height()
                pixmap = self.sourceImg_label.pixmap()
                ratio = pixmap.devicePixelRatio()
                # print(ratio)
                # # 
                # # create painter instance with pixmap
                # self.painterInstance = QPainter(pixmap)
                # # set rectangle color and thickness
                # self.penRectangle = QPen(Qt.red)
                # # draw rectangle on painter
                # xPos = 10
                # yPos = 20
                # xLen = 30
                # yLen = 30
                # self.painterInstance.setPen(self.penRectangle)
                # self.painterInstance.drawRect(xPos,yPos,xLen,yLen)
          


if __name__ == "__main__":
    # create output folder
    dir_path = os.path.dirname(os.path.realpath(__file__))
    directory = dir_path + '/output'
    if not os.path.exists(directory):
        os.makedirs(directory)

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
