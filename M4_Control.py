from time import time, sleep
import numpy as np
from PIL import Image
import os
from ardSerial import *
from contextlib import contextmanager
import sys
from object_detector import detect_object

model_bittle = 'Bittle'
postureTable = postureDict[model_bittle]

sit = ['ksit',2]
zero = ['kzero',1]
balance = ['kbalance',2]
headR = ['m', [1, 30], 1.5]
headL = ['m', [1, -30], 1]
headF = ['m', [1, 0], 1]
back = ['kbk',1]
der = ['kwkR',0.5]
izq = ['kwkL',0.5]
cen = ['kwkF',1]
if __name__ == '__main__':
	try:
		goodPorts = {}
		print(goodPorts)
		connectPort(goodPorts)
		t=threading.Thread(target = keepCheckingPort, args = (goodPorts,))
		t.start()
		parallel = False
		time.sleep(2);
		send(goodPorts, zero)
		control=True
		bal=False
		headDer=True
		headIzq=False
		check=0
		while control:	
			t1=time.time()
			center_x, box_width = detect_object()
			#result = detect_object()  # Llama a la función de detección

			if center_x is not None:  # Si se detectó un objeto
				print(center_x, box_width)
				check=0
				bal=False
				if center_x<0.35:
					print("Izquierda")
					send(goodPorts, izq)
				elif center_x > 0.65:
					print("Derecha")
					send(goodPorts, der)
				elif center_x >= 0.35 and center_x<=0.65:
					print("Centro")
					send(goodPorts, cen)
				elif box_width >= 0.15:
					print("Destino")
					send(goodPorts, sit)
					control=False						
			else:
				print("No ball detected")
				if bal==False:
					send(goodPorts, balance)
					bal=True
				if check is not None:
					if check<1:
						if headDer:
							send(goodPorts, headR)
							headDer=False
							headIzq=True
						else:
							send(goodPorts, headL)
							headIzq=False
							headDer=True
							check=check+1
					else:
						send(goodPorts, back)
						send(goodPorts, balance)
						check=0		
									
			t2=time.time()
			print("TIEMPO DE INFERENCIA: ", t2-t1)
			
		closeAllSerial(goodPorts)
		logger.info("finish!")
		os._exit(0)

	except Exception as e:
		logger.info("Main Exception")
		closeAllSerial(goodPorts)
		os._exit(0)
		raise e
		
	except KeyboardInterrupt:
		logger.info("Keyboard Interrupt!")
		closeAllSerial(goodPorts)
		os._exit(0)
		raise Exception("Interrupción del teclado detectada")
	
