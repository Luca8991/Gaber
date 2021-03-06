import time
import threading
import os
# install opencv: https://stackoverflow.com/a/60201245/5094892
# run python3: LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3
import cv2
from PIL import Image

class Screen(threading.Thread):
    def __init__(self, username, device, router):
        self.device = device
        self.username = username
        self.router = router
        self.counter = 0
        self.started = False
        self.deviceChanged = False
        self.text = ''
        self.ris = ''

    def __startThread(self):
        threading.Thread.__init__(self)
        self.name = self.username+"_screen"
        self.start()
        self.started=True

    def getNotificationMessage(self, device, username=None):

        msg = []

        msg.append([(10, 35), device.getName().replace("_", " ").upper()])
        msg_status = "START STREAM?"
        
        msg.append([(10,50), msg_status])

        return msg
    
    def run(self):

        vidcap = cv2.VideoCapture('src/video/gaber.mp4')
        success,image = vidcap.read()
        count = 0

        old_len = 0

        if self.device:

            self.device.newImg()
            self.device.setText((35,0),"CONSOLE ", 255,self.device.getFonts()[0])
            self.device.setText((1,10),">", 255,self.device.getFonts()[0])
            self.device.sendImg()

        while True:
            if self.device:

                while success:
                    im=Image.fromarray(image)
                    im=im.rotate(90, expand=True)
                    im=im.resize((128,64))
                    im=im.convert('1')
                    self.device.setImg(im)
                    self.device.sendImg()
                    success,image = vidcap.read()
                    count+=1

                '''text = self.router.getText()

                if old_len != len(text) or self.deviceChanged:
                    self.deviceChanged=False
                    old_len = len(text)
                    self.text = text
                    if len(text) != 0:
                        key = text[len(text)-1]
                            
                        if key == '\r':
                            if self.text[:-1] == 'clear':
                                self.ris = ''
                            else:
                                stream = os.popen(self.text[:-1])
                                self.ris = stream.read()
                                stream.close()
                            self.text = ''
                            self.router.setText('')
                        
                    self.device.newImg()
                    self.device.setText((35,0),"CONSOLE ", 255,self.device.getFonts()[0])
                    self.device.setText((1,10),">", 255,self.device.getFonts()[0])
                    self.device.setText((10,10), self.text, 255,self.device.getFonts()[0])
                    self.device.setText((10,20), self.ris, 255,self.device.getFonts()[0])
                    self.device.sendImg()'''
    
    def handleStreaming(self, device):
        if self.device!=device:
            old_device = self.device
            self.__setDevice(device)
            self.deviceChanged = True
            if old_device != 0:
                old_device.resetStreamingUser()
            if not self.started:
                self.__startThread()
    
    def __setDevice(self, device):
        self.device = device