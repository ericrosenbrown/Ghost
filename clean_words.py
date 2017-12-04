import os

in_path = "./clean.txt"
out_path = "./comma.txt"

try:
	os.remove(out_path)
except OSError:
	pass

f_in = open(in_path,"rb")
f_out = open(out_path,"wb")

content = f_in.read()
contents = content.split("\n")

counter = 0
myword = ""
for word in contents:
	myword += word.lower() + ","
f_out.write(myword)

f_in.close()
f_out.close()
