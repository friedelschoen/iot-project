import time, threading

def repeat_timer(sec):
	def wrapper(func):
		def thread():
			while True:
				time.sleep(sec)
				func()

		thd = threading.Thread(target=thread)
		thd.start()

		return func
	return wrapper
