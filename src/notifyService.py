from PIL   				import Image
import time
import threading
from numpy.random 			import randint

from src.iot_funct.door 		import Door
from src.iot_funct.screen 		import Screen
from src.iot_funct.led			import Led
from src.iot_funct.keyboard 	import Keyboard
from src.iot_funct.console		import Console
#from application import Application

class NotifyService(threading.Thread):
	def __init__(self, app, router):
		threading.Thread.__init__(self)
		self.app=app
		self.router=router
		self.username=self.app.getUsername()
		self.recentDevices=[]
		#self.nearDeavices=[]
		self.device=0
		self.name = self.username+"_notifyService"
		self.appList={
			"door": Door(),
			"screen": Screen(self.username, self.device, self.router),
			"console": Console(self.username, self.device, self.router),
			"keyboard": Keyboard(self.username, self.device, self.router),
			"led": Led()
			} #{"dev.type": IOT_Functions()}
		
		self.notToResetType = ["screen", "keyboard", "console"]
		self.threadType = ["screen", "keyboard", "console"]

	def run(self):
		print(self.app.getUsername()+": notify started")
		while (self.app.isAlive()):
			devs=self.router.listNearDevices(self.username)
			for dev in devs: 
				if((not (dev in self.recentDevices)) and (dev.getStreamingUser()=="")):
					dev.setStreamingUser(self.username)
					self.device=dev

			for dev in self.recentDevices:
				if(not (dev in devs)):
					self.recentDevices.remove(dev)

			if(self.device):
				self.app.startNotify()
				color = list(randint(0,32,3))
				self.app.setNeopixel(color, -1, True)
				self.app.setText((40,0), "NOTIFY", 255,self.app.getFonts()[0], True)
				self.app.setText((10,20), "FOUND", 255,self.app.getFonts()[0], True)

				devType = self.device.getDeviceType()
				
				notifMsg = self.appList[devType].getNotificationMessage(self.device)
				for line in notifMsg:
					self.app.setText(line[0], line[1], 255,self.app.getFonts()[0], True)

				self.app.sendImg(True)
				data=self.app.recvData(True)
				datad_old=data['DOWN']
				datau_old=data['UP']
				datas_old=data['SELECT']
				stop=False
				accepted=False
				startTime = time.time()
				while(not stop):
					data=self.app.recvData(True)
					if (data['DOWN']!=datad_old):
						datad_old=data['DOWN']
						if(datad_old):
							stop=True
							#self.recentDevices.append(dev)
							
					elif (data['UP']!=datau_old):
						datau_old=data['UP']
						if(datau_old):
							stop=True	
							#self.recentDevices.append(dev)
					
					elif(data['SELECT']!=datas_old):
						datas_old=data['SELECT']
						if(datas_old):
							stop=True
							accepted=True

					elif(time.time() - startTime > 30):
						stop = True

				if(accepted):
					if devType in self.threadType:
						self.appList[devType].handleStreaming(self.device)
					else:
						self.appList[devType].run(self.device)

				else:
					self.device.resetStreamingUser()

				self.app.setNeopixel([0, 0, 0], -1, True)
				self.app.stopNotify()
				if not (devType in self.notToResetType):
					self.device.resetStreamingUser()
				self.device=0
			
	def getUsedDevices(self):
		return self.recentDevices

