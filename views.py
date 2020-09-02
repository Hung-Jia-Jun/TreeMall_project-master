from flask import Flask,request
from flask import render_template,Response
import time
import sys
import os
import requests
import json
from flask_sqlalchemy import SQLAlchemy
import configparser
import threading
import datetime
import os
from flask_cors import cross_origin,CORS
config = configparser.ConfigParser()

currentPath = os.path.dirname(os.path.abspath(__file__))
config.read(currentPath + '/Config.ini')
DatabaseIP = config.get('Setting','DatabaseIP')
DBusername = config.get('Setting','DBusername')
DBpassword = config.get('Setting','DBpassword')

#------------------------------------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+DBusername+':'+DBpassword+'@'+DatabaseIP+':3306/sensordb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)




class shortURL(db.Model):
	DateTime = db.Column(db.String(255), primary_key=True)
	URL = db.Column(db.String(255))
	MappingURL = db.Column(db.String(255))
  
	def __init__(self, DateTime, URL):
		self.DateTime = DateTime
		self.URL = URL
		self.MappingURL = MappingURL

def ROCYearConvert(orders,shiftYear):
	for order in orders:
		#民國年轉西元年
		datelist = []
		datelist = order["date"].split("/")
		datelist[0] = str(int(datelist[0]) + shiftYear)
		order["date"] = '/'.join(datelist)
	return orders
def sordbyDESC(orders):
	orders = ROCYearConvert(orders,1911)
	#先對所有order的list做排序，之後再依照這個datetime去抓取對應的order
	sortDates = sorted([datetime.datetime.strptime(order["date"], "%Y/%m/%d") for order in orders])
	
	#排序完成的list
	sortedOrder = []
	for dt in sortDates:
		for order in orders:
			if datetime.datetime.strptime(order["date"], "%Y/%m/%d") == dt:
				exist = False
				for sort in sortedOrder:
					if order['name'] == sort['name']:
						exist = True
				if exist == False:
					sortedOrder.append(order)
	#西元年轉民國年
	sortedOrder = ROCYearConvert(sortedOrder,-1911)
	return sortedOrder

@app.route("/shorturl")
def shorturl():
	return render_template('shorturl.html')

@app.route("/index")
def index():
	orederItem = orderList()
	oreders = orederItem.json["orders"]
	progressOrder = []
	completedOrder = []
	for order in oreders:
		if int(order["status"]["code"]) <= 2:
			progressOrder.append(order)
		else:
			completedOrder.append(order)
	progressOrder = sordbyDESC(progressOrder)
	completedOrder = sordbyDESC(completedOrder)
	return render_template('index.html',progressOrder = progressOrder,completedOrder=completedOrder)

#取得用戶輸入的網址
@app.route("/UserShortUrl")
def UserShortUrl():
	_url = request.args.get('url')
	print (_url)
	findExistURL = shortURL.query.filter_by(MappingURL=_url) 
	if findExistURL == None:
		pass
	else:
		return findExistURL.first().URL
	return _url

@app.route("/orderList")
def orderList():
	#依照ID排序
	Orders ="""
				{
					"orders": [
						{
						"name": "Livi優活 抽取式衛生紙(100抽x10包x10串/箱)",
						"logo": "https://static.oopocket.com/store/iconTreemall@3x.png",
						"status": {
							"code": 3,
							"type": "已取消"
						},
						"date": "107/6/12"
						},
						{
						"name": "BALMUDA The Toaster 百慕達烤麵包機-黑色",
						"logo": "https://static.oopocket.com/store/iconTreemall@3x.png",
						"status": {
							"code": 2,
							"type": "已成立"
						},
						"date": "108/7/21"
						},
						{
						"name": "贈-短慧萬用鍋HD2133+三合一濾網「LG樂金」韓國原裝...",
						"logo": "https://static.oopocket.com/store/iconTreemall@3x.png",
						"status": {
							"code": 1,
							"type": "處理中"
						},
						"date": "108/6/2"
						},
						{
						"name": "Apple AirPds 2",
						"logo": "https://static.oopocket.com/store/iconTreemall@3x.png",
						"status": {
							"code": 4,
							"type": "已送達"
						},
						"date": "108/3/02"
						}
					]
				}
			"""
	Orders_json = json.loads(json.dumps(Orders, ensure_ascii=False))
	return Response(response=Orders_json,
                    status=200,
                    mimetype="application/json")

if __name__ == "__main__":
	app.run(host='0.0.0.0',port=8000)
