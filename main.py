import time
import sys
import os
import cv2
import zxing
import pyotp
import base64
import tkinter
import threading

import google_auth_pb2

from tkinter import StringVar

from typing import List, Dict

from urllib.parse import parse_qs, urlparse


def identify_qr_code(image: str):
	"""识别谷歌验证器导出的二维码"""
	reader = zxing.BarCodeReader()
	barcode = reader.decode(image)
	return barcode.parsed


def decode_line(url: str) -> List[Dict[str, str]]:
	"""解码识别出的二维码链接。
	
	Args:
		url: 二维码解码出来的链接，如：`otpauth-migration://offline?data=……`
		
	Returns:
		List[Dict[str, str]]。如：`[{'name': 'OKEx.com', 'secret': 'ABCDWASGLYXIEEFG', 'issuer': 'OKEx.com'}]`
	"""
	parsed_url = urlparse(url)
	params = parse_qs(parsed_url.query)
	data_encoded = params['data'][0]
	data = base64.b64decode(data_encoded)
	payload =google_auth_pb2.MigrationPayload()
	payload.ParseFromString(data)
	otp = payload.otp_parameters
	google_list = []
	for o in otp:
		name = o.name
		secret = str(base64.b32encode(o.secret), 'utf-8').replace('=', '')
		issuer = o.issuer
		google_list.append({"name": name, "secret": secret, "issuer": issuer})
	return google_list


def get_remain():
	ts = int(time.time())
	return 30 - ts % 30


def do_ocr():
	try:
		timestamp = str(int(time.time()))
		if not os.path.exists("./.google_auth"):
			os.makedirs("./.google_auth")
		cap = cv2.VideoCapture(0)
		f, frame = cap.read()
		cv2.imwrite(f"./.google_auth/{timestamp}.png", frame)
		cap.release()
		url = identify_qr_code(f"./.google_auth/{timestamp}.png")
		print(url)
		with open("./.google_auth/url.text", mode="a") as f:
			f.writelines([url])
			f.write('\r\n')
	except:
		pass


google_list = []
try:
	with open("./.google_auth/url.text", mode='r') as f:
		lines = f.readlines()
		for l in lines:
			s = l.rstrip("\n")
			data = decode_line(url=s)[0]
			google_list.append(data)
		google_list = [dict(t) for t in set([tuple(d.items()) for d in google_list])]
except:
	pass


# 主窗口
window = tkinter.Tk()
window.title("garyhertel@foxmail.com")
window.geometry('360x740')
window.update()
window.resizable(False, False)
window.config(background="#ffffff")


# 画布
platform = sys.platform
canvas = tkinter.Canvas(window, bg="white", width=window.winfo_width(), height=window.winfo_height())
label = tkinter.Label(window, text="Google 身份验证器", bg="white", fg="red", justify="left", font=('', 25))
canvas.create_window(70, 10, window=label, anchor=tkinter.NW)
button = tkinter.Button(canvas, text="导入", justify="left", command=do_ocr)
canvas.create_window(160, 45, window=button, anchor=tkinter.NW)


def on_mousewheel(event):
	"""鼠标事件监听"""
	if platform == "darwin":
		canvas.yview_scroll(-1 * event.delta, "units")
	else:
		canvas.yview_scroll(-1 * event.delta / 120, "units")
	
	
canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.pack()


def do_number(code: StringVar, number: StringVar, secret: str):
	"""每秒更新一次显示的验证码"""
	code.set(str(pyotp.TOTP(secret).now())[0: 3] + " " + str(pyotp.TOTP(secret).now())[3: 6])
	number.set(str(get_remain()))
	while True:
		time.sleep(1)
		code.set(str(pyotp.TOTP(secret).now())[0: 3] + " " + str(pyotp.TOTP(secret).now())[3: 6])
		number.set(str(get_remain()) + "  ")


# 第一个label的高度，随后每次增加
location_y = 80
for d in google_list:
	name, secret = f"{d['issuer']} ({d['name']})" if d['issuer'] else d['name'], d["secret"]
	code, number = StringVar(), StringVar()
	label = tkinter.Label(window, text=name, bg="white", fg="black", justify="left", font=('', 15))
	canvas.create_window(10, location_y, window=label, anchor=tkinter.NW)
	label = tkinter.Label(window, textvariable=number, bg="white", fg="green", justify="left", font=('', 25))
	canvas.create_window(295, location_y, window=label, anchor=tkinter.NW)
	location_y += 30
	label = tkinter.Label(window, textvariable=code, bg="white", fg="blue", justify="left", font=('', 20))
	canvas.create_window(10, location_y, window=label, anchor=tkinter.NW)
	location_y += 30
	label = tkinter.Label(window, text="——" * 18, bg="white", fg="gray", justify="left", font=('', 10))
	canvas.create_window(10, location_y, window=label, anchor=tkinter.NW)
	location_y += 30
	threading.Thread(target=do_number, args=(code, number, secret, )).start()


scrollbar = tkinter.Scrollbar(canvas, orient=tkinter.VERTICAL, command=canvas.yview)
scrollbar.place(relx=1, rely=0, relheight=1, anchor=tkinter.NE)
canvas.config(yscrollcommand=scrollbar.set, scrollregion=(0, 0, 0, location_y))

window.mainloop()