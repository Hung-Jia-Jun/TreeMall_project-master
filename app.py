from flask import Flask,request,redirect
from flask import render_template,Response
import time
import re
import sys
import os
import json
from flask_sqlalchemy import SQLAlchemy
import configparser
import threading
import datetime
import os
from flask_migrate import Migrate
from flask_cors import cross_origin,CORS
import string
import random
config = configparser.ConfigParser()

currentPath = os.path.dirname(os.path.abspath(__file__))

#------------------------------------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class shortURL(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	URL = db.Column(db.String(255))
	MappingURL = db.Column(db.String(255))
  
	def __init__(self,URL,MappingURL):
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
	return render_template('shortURL.html')

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
	regex = "(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
	check_Url = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', _url)
	if len(check_Url) == 0:
		return "URL錯誤，請輸入正確的網址"
	findExistURL = shortURL.query.filter_by(MappingURL=_url).first()
	if findExistURL == None:
		#26^5=11881376個短網址可以配給，以這個Project來說是夠用了
		#剩下就是DB的query latency問題，到時候可以用cluster解決
		randomString = [random.choice(string.ascii_uppercase) for i in range(5)]
		compileURL = ''.join(randomString)
		shortURL_DB = shortURL(URL = compileURL,MappingURL = _url)
		db.session.add(shortURL_DB)
		db.session.commit()
		pass
	else:
		return findExistURL.URL
	return compileURL

@app.route("/<url_key>")
def redirect_to_url(url_key):
    """
    Check the url_key is in DB, redirect to original url.
    """
    url = shortURL.query.filter_by(URL=url_key).first()
    if url is None:
        return False
    return redirect(url.MappingURL)


@app.route("/")
def redirectURL():
	print ("OK")
	pass

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
