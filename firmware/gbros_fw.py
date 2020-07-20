from machine import Pin, I2C, PWM, ADC
import neopixel
import socket
import framebuf
import machine
import time

def run(so):
	pin_in=[]
	oled_width = 1
	oled_heigth = -1
	oled = 0
	adc=0
	send_data=True
	so.settimeout(0.05)
	disp=False
	data=b''
	while(1):
		#so.setsockopt(socket.TCP_NODELAY,1)
		msg=0
		if(send_data):
			for p in pin_in:
				msg += ((not Pin(p, Pin.IN, Pin.PULL_UP).value())<<p)

		try:
			if(send_data):
				so.send(str(msg).encode())
			else:
				so.send(str(adc).encode())
				send_data=True
		except:
			import machine
			machine.reset()

		s=b''
		try:
			s=so.recv(1024)
		except:
			pass
		
		d=s
		if(len(s)==2):
			if( not ( int(s) in pin_in)):
				pin_in.append(int(s))
   
		elif(len(s)==3):
			pin = int(int(s)/10)
			Pin(pin, Pin.OUT).value(int(s)%10)
			if pin in pin_in:
				pin_in.remove(pin)

		if(len(s)==4):
			pin=int(s)
			adc=ADC(pin)
			send_data=False
			if pin in pin_in:
				pin_in.remove(pin)
				
		elif(len(s)==9):
			s=int(s)
			duty=s%10000
			s=int(s/10000)
			freq=s%1000+1
			pin=int(s/1000)
			PWM(Pin(pin), freq=freq, duty=duty)
			if pin in pin_in:
				pin_in.remove(pin)    
					
		elif(len(s)==11):
			s=int(s)
			val=[0,0,0]
			val[2]=(s%1000)
			s=int(s/1000)
			val[1]=(s%1000)
			s=int(s/1000)
			val[0]=(s%1000)
			np = neopixel.NeoPixel(machine.Pin(int(s/1000)), 1)
			np[0]=val
			np.write()
		elif(len(s)==12):
			s=s.decode()
			print(s)
			disp=int(s[-2:])
			s=s[:-2]
			s=int(s)
			oled_heigth=s%1000
			s=int(s/1000)
			oled_width=s%1000
			s=int(s/1000)
			scl=s%100
			sda=int(s/100)
			i2c = I2C(-1, scl=Pin(scl), sda=Pin(sda))
			print(disp, oled_heigth, oled_width, sda, scl)

			if(disp==0):
				from sh1106 import SH1106_I2C
				oled = SH1106_I2C(oled_width, oled_heigth, i2c)
			elif(disp==1):
				from ssd1306 import SSD1306_I2C
				oled = SSD1306_I2C(oled_width, oled_heigth, i2c)
		
		if(len(d)==int(oled_heigth*oled_width)/16):
			disp= not disp
			if(not disp):
				data=data+d
				p=bytearray(data)
				fbuf=framebuf.FrameBuffer(p,oled_width, oled_heigth,framebuf.MONO_HLSB)
				oled.blit(fbuf,0,0)
				oled.show()
			else:
				data=d
		else:
			disp=False
			
		time.sleep(0.01)


	#so.close()

	




