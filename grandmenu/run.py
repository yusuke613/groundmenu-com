#__pycache__の自動作成が鬱陶しいので作成しないように
import sys
sys.dont_write_bytecode=True
from flask import render_template, session, redirect, url_for, flash, request, jsonify
from flaskr import app

# websocketに関するモジュール
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect, send
#modelの読み込み
from flaskr.models import Store, Staff, Menu, Table, Order
#sqlalchemyでfuncを使う(maxやminなどが使えるようになる)
from sqlalchemy import func

from flask_sqlalchemy import SQLAlchemy

#関数群ファイルの読み込み
from flaskr import FlaskAPI

db=SQLAlchemy(app)

# websocketは、socketio.run(app, debug=True)で動くため(本ファイル最下部参照)、run.pyに書く(いい方法があったら書き直す)
# async_mode...よくわからん。
socketio=SocketIO(app, async_mode=None)

# クライアント側と繋がった場合に、注文中のメニューを返す
@socketio.on("cart_information")
def cart_information(msg):
	# 受け取ったMessageを表示
	print(msg)

	# store_id → table_table_number → group_id → room(そのテーブルに座っている人にだけ送るチャットルームみたいなもの)の順に変数を設定していく
	store_id=session['store_id']

	# 店舗の場合はsessionにtable_numberを持っていないので、0を代入
	if 'table_number' not in session:
		session['table_number']=0
	table_number=session['table_number']

	# 決済が完了しているグループのgroup_idをgroup_id_maxとして取得
	group_id_max=db.session.query(func.max(Order.GROUP_ID)).filter_by(STORE_ID=store_id, TABLE_NUMBER=table_number, ORDER_STATUS=7).scalar()
	# group_id_maxに対して+1した数字が現在のgroup_id(group_id_maxがNoneの場合、その店のそのテーブルで注文する初めての客)
	if group_id_max is None:
		group_id=1
	else:
		group_id=group_id_max + 1
	session['group_id']=group_id

	# roomをセッションに持たせる
	session['room']=str(session['store_id']) + "_" + str(session['table_number']) + "_" + str(session['group_id'])
	session['store']=str(session['store_id'])
	room=session['room']
	# roomというチャットスペースみたいなところに入る
	join_room(room)

	# カートの中身を見たいので、order_status=0を設定
	order_status=0
	# カートに入っている商品数を求める(order_statusの値を変更すれば、カートに入っているものや、注文済みのもの、決済が完了したものを見ることができる)
	total_quantity=FlaskAPI.total_quantity(store_id, table_number, group_id, order_status)
	# カートに入っている商品情報を求める(order_statusの値を変更すれば、カートに入っているものや、注文済みのもの、決済が完了したものを見ることができる)
	order_list=FlaskAPI.order_list(store_id, table_number, group_id, order_status)

	# roomのメンバーに情報を送信
	emit("cart_information",{'total_quantity': total_quantity, 'order_list': order_list})

# サーバー側からもコネクトする処理。特に意味無し
@socketio.on('connect')
def server_to_client_connection():
	emit("server_to_client_connection","server has connected", broadcast=True)

# 送られてくる情報はmenu_id,quantity
@socketio.on("add_to_cart")
def add_to_cart(add_to_cart):
	# try:
		print("メニューIDは" + add_to_cart["menu_id"])
		print("注文数量は" + add_to_cart["order_quantity"])

		store_id=session['store_id']
		table_number=session['table_number']
		group_id=session['group_id']

		menu_id=add_to_cart["menu_id"]
		order_quantity=add_to_cart["order_quantity"]

		# カートに加えられるアイテムが正しいか判定
		store_id==db.session.query(Menu.STORE_ID).filter_by(STORE_ID=store_id, MENU_ID=menu_id).one()

		#order_status=0はかごに入ってる状態を示す
		order_status=0

		# 既にオーダーされている種類であれば数量追加、なければ新規登録
		try:
			existing_order=db.session.query(Order).filter_by(STORE_ID=store_id, TABLE_NUMBER=table_number, GROUP_ID=group_id, ORDER_STATUS=order_status, MENU_ID=menu_id).one()
			existing_order.ORDER_QUANTITY=existing_order.ORDER_QUANTITY + int(order_quantity)
			db.session.commit()
			db.session.close()
		except:
			db.session.add(Order(STORE_ID=store_id, TABLE_NUMBER=table_number, GROUP_ID=group_id, ORDER_STATUS=order_status, MENU_ID=menu_id, ORDER_QUANTITY=order_quantity))
			db.session.commit()
			db.session.close()

		total_quantity=FlaskAPI.total_quantity(store_id, table_number, group_id, order_status)
		order_item=FlaskAPI.order_item(store_id, table_number, group_id, order_status, menu_id)
		print(order_item)
		print(type(order_item))
		room=session['room']
		emit("add_to_cart",{'total_quantity': total_quantity, 'order_item': order_item}, room=room)
	# except:
	# 	room=session['room']
	# 	emit("server_to_client_connection","false", room=room)

@socketio.on("change_cart")
def change_quantity(change_cart):
	try:
		print("注文IDは" + change_cart["order_id"])
		print("注文数量が" + str(change_cart["order_quantity"]) + "になりました")

		store_id=session['store_id']
		table_number=session['table_number']
		group_id=session['group_id']
		order_id=change_cart["order_id"]
		order_quantity=change_cart["order_quantity"]
		order_status=0

		# カートに加えられるアイテムが正しいか判定エラーが出ればexceptに飛ばす
		order_item=db.session.query(Order).\
		filter_by(ORDER_ID=order_id, STORE_ID=store_id).one()
		menu_id=order_item.MENU_ID

		# 注文数量が0の時、カートのステータスをカゴ落ち(1)に変更する
		if order_quantity<=0:
			order_item.ORDER_STATUS=1
		print(order_item)

		# 数量の変更
		order_item.ORDER_QUANTITY=order_quantity
		print(order_item)
		db.session.commit()
		db.session.close()

		total_quantity=FlaskAPI.total_quantity(store_id, table_number, group_id, order_status)
		room=session['room']
		emit("change_cart",{'total_quantity': total_quantity, 'order_id': order_id, 'order_quantity':order_quantity}, room=room)
	except:
		 room=session['room']
		 emit("server_to_client_connection","false", room=room)

@socketio.on("order_submit")
def order_submit():
	print("オーダー決定")
	store_id=session['store_id']
	table_number=session['table_number']
	group_id=session['group_id']
	order_status=2

	db.session.query(Order).filter_by(STORE_ID=store_id, TABLE_NUMBER=table_number, GROUP_ID=group_id, ORDER_STATUS=0).update({Order.ORDER_STATUS: order_status})
	db.session.commit()
	db.session.close()

	order_list=FlaskAPI.order_list(store_id, table_number, group_id, order_status)

	emit("add_to_order",order_list, room=store_id)

# 店舗側がオーダーを確認する仕組み
@socketio.on("show_order")
def show_order(msg):
	# 受け取ったMessageを表示
	print(msg)

	# store_id → table_table_number → group_id → room(そのテーブルに座っている人にだけ送るチャットルームみたいなもの)の順に変数を設定していく
	store_id=session['store_id']
	# roomというチャットスペースみたいなところに入る
	join_room(store_id)

	# カートの中身を見たいので、order_status=0を設定
	order_status=2
	# カートに入っている商品情報を求める(order_statusの値を変更すれば、カートに入っているものや、注文済みのもの、決済が完了したものを見ることができる)
	order_list=FlaskAPI.order_list_all(store_id, order_status)

	# roomのメンバーに情報を送信
	emit("show_order",order_list, room=store_id)

if __name__ == '__main__':
	# app.run(debug=True)
	socketio.run(app, debug=True)
