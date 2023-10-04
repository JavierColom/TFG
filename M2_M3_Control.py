from time import time, sleep
import numpy as np
from PIL import Image
import os
from ardSerial import *
from contextlib import contextmanager
import sys
from roboflow import Roboflow


rf = Roboflow(api_key="RW2uZYa9EZPkDcGWQAaX")
project = rf.workspace("tfg-jzxa8").project("bittle")
model = project.version(1).model

postureTable = postureDict['Bittle']

sit = ['ksit',2]
zero = ['kzero',3]
der = ['kcrR',2]
izq = ['kcrL',2]
cen = ['kcrF',2]

control=True

if __name__ == '__main__':
	try:
		#Conexion serial
		goodPorts = {}
		print(goodPorts)
		connectPort(goodPorts)
		t=threading.Thread(target = keepCheckingPort, args = (goodPorts,))
		t.start()
		parallel = False
		time.sleep(2);
		send(goodPorts, zero)
		
		#Lazo de control
		while(control):
			os.system("sudo libcamera-still --width 512 --height 512 --rotation 180 -o test.jpg - --immediate --nopreview --flush  &> /dev/null")
			t1=time.time()

			#Realizamos inferencia
			prediction=model.predict("test.jpg", confidence=40, overlap=30)
			
			#Convertimos en objeto JSON
			data=prediction.json()

			print(prediction.json()["predictions"])
			print(bool(prediction.json()["predictions"]))

			#Si ha detectado la pelota:
			if bool(prediction.json()["predictions"]):

				#Guardamos dimensiones de la imagen en variables
				width=prediction.json()["image"]["width"]
				height=prediction.json()["image"]["height"]
				
				#Guardamos la coordenada x de la pelota, el ancho y el alto de la caja de detección en variables
				x_value=prediction.json()["predictions"][0]["x"]
				width_value=prediction.json()["predictions"][0]["width"]
				height_value=prediction.json()["predictions"][0]["height"]
					
				print(x_value)
				print(width)
				
				#Calculamos el porcentaje horizontal en el que se encuntra la pelota
				result=int(x_value)/int(width)
				print(result)			

				print(int(height_value)/int(height))	
				
				#Acción de control:
				
				#Si la pelota estan en el primer tercio de la imagen gira a la izquierda
				if result<0.3:
					print("Izquierda")
					send(goodPorts, izq)

				#Si la pelota estan en el segundo tercio de la imagen avanza recto
				elif result> 0.7:
					print("Derecha")
					send(goodPorts, der)

				#Si la pelota estan en el tercer tercio de la imagen gira a la derecha
				elif result>= 0.3 and result<=0.7:
					print("Centro")
					send(goodPorts, cen)
				
				#Si el ancho o el alto de la caja de detección ocupa mas del 25% de la imagen, se sienta y sale del lazo de control
				if (int(height_value)/int(height))>0.25 or (int(width_value)/int(width))>0.25:
					print("Pelota!")
					send(goodPorts, sit)
					sleep(3)
					control=False

			#Si no ha detectado la pelota:
			else:
				print("No ball detected")			
			
			send(goodPorts, "kbalance",1)
			t2=time.time()
			total_time=t2-t1
			print(total_time)
		#Cerrar coneción serial
		closeAllSerial(goodPorts)
		logger.info("finish!")
		os._exit(0)
	
	#Excepción si falla el código
	except Exception as e:
		logger.info("Main Exception")
		closeAllSerial(goodPorts)
		os._exit(0)
		raise e
	
	#Excepción si se interrumpe manualmente CTRL+C
	except KeyboardInterrupt:
		logger.info("Keyboard Interrupt!")
		closeAllSerial(goodPorts)
		os._exit(0)
		raise Exception("Interrupción del teclado detectada")
	
