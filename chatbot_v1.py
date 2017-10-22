import cleverbot
cb = cleverbot.Cleverbot('CC526HD-cCoAmjfGia8reYjzKPg', timeout=60)

x = 1
while x > 0:
	text = input("Say to Cleverbot: ")
	try:
	    reply = cb.say(text)
	except cleverbot.CleverbotError as error:
	    print(error)
	else:
	    print(reply)
	finally:
	    cb.close()