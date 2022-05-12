code = '9939a3'

if len(code) != 6 or not code[0:4].isnumeric() or not code[4:6].isalpha():
	print('invalid')
