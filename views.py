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
	Data = db.Column(db.String(255))
	MappingData = db.Column(db.String(255))
  
	def __init__(self, DateTime, Data):
		self.DateTime = DateTime
		self.Data = Data
		self.MappingData = MappingData
		

@app.route("/index")
def index():
	orederItem = queryCommandList()
	orederCount = len(orederItem.json["orders"])
	oreders=[]
	for i in range(orederCount):
		oreders.append(i)
	return render_template('index.html',oreders = oreders)

#取得當前指令的列表
@app.route("/orderList")
def queryCommandList():
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
