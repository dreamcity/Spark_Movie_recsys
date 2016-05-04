#!/usr/bin/env python
#-*- coding: utf-8 -*-
# from app import app
from . import main
from flask import Flask,current_app,render_template,request,redirect,url_for
from flask.ext.paginate import Pagination
from pymongo import ASCENDING,DESCENDING
import time
from forms import EditRateForm,EditUserForm

@main.route("/",methods=["GET"])
def index():
	return render_template('index.html')
	# return render_template('test.html')

@main.route("/users",methods=["GET"])
def show_users():
	total = current_app.config['TOTAL_USERS']
	if not total:
		total = current_app.config['USERS_COLLECTION'].find().count()
	page, per_page, offset = get_page_items()
	if page * per_page > total:
		users_info = ""
	else:
		users_info = current_app.config['USERS_COLLECTION'].find({},{"_id":0}).skip(offset).limit(per_page)
	pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap3',record_name="users_info")
	# return render_template('users.html', users=users_info,page=page,per_page=per_page,pagination=pagination)
	return render_template('users.html', total = total,users=users_info,pagination=pagination)

def get_page_items():
    page = int(request.args.get('page', 1))
    per_page = request.args.get('per_page')
    if not per_page:
        per_page = current_app.config.get('PER_PAGE', 10)
    else:
        per_page = int(per_page)

    offset = (page - 1) * per_page
    return page, per_page, offset

@main.route("/user/<int:user_id>")
def show_user_f_id(user_id):
	user = current_app.config['USERS_COLLECTION'].find_one({"id":user_id},{"_id":0})
	user_pattern = {}
	user_pattern["rate_nums"] = current_app.config['RATE_COLLECTION'].find({"user_id":user_id}).count()
	total_movies = current_app.config['MOVIES_COLLECTION'].find().count()
	user_pattern["unrate_nums"] = total_movies - user_pattern["rate_nums"]
	avg_rate_cursor = current_app.config['RATE_COLLECTION'].aggregate([{"$group":{"_id":"$user_id","avg":{"$avg":"$rate_score"}}},{"$match":{"_id":user_id}}])
	avg_rate = ""
	for x in avg_rate_cursor:
		avg_rate = x["avg"]
	user_pattern["avg_rate"] = avg_rate
	
	first_rate_time_cursor = current_app.config['RATE_COLLECTION'].aggregate([{"$group":{"_id":"$user_id","first_rate":{"$min":"$rate_time"}}},{"$match":{"_id":user_id}}])
	first_rate_time = ""
	for x in first_rate_time_cursor:
		first_rate_time = x["first_rate"]
	user_pattern["first_rate_time"] = first_rate_time

	last_rate_time_cursor = current_app.config['RATE_COLLECTION'].aggregate([{"$group":{"_id":"$user_id","last_rate":{"$max":"$rate_time"}}},{"$match":{"_id":user_id}}])
	last_rate_time = ""
	for x in last_rate_time_cursor:
		last_rate_time = x["last_rate"]
	user_pattern["last_rate_time"] = last_rate_time
	return render_template('user.html',user=user,user_pattern=user_pattern)
@main.route("/user/add")
def add_user():
	max_id_cursor = current_app.config['USERS_COLLECTION'].find({},{"id":1,"_id":0}).sort("id",DESCENDING).limit(1)
	max_id = 0
	for x in max_id_cursor:
		max_id = x["id"]
	user_max_id = int(max_id) + 1
	return redirect(url_for('.edit_user',user_id = user_max_id))
	
@main.route("/user/<int:user_id>/edit")
def edit_user(user_id):
	return redirect(url_for('.update_user_info',user_id=user_id))

@main.route("/edit/user",methods=['GET', 'POST'])
def update_user_info():
	user_id = int(request.args.get('user_id',0))
	if user_id :
		form = EditUserForm()
		if form.validate_on_submit():
			user_info = {}
			user_info["name"] = form.name.data
			user_info["age"] = form.age.data
			user_info["gender"] = form.gender.data
			user_info["occupation"] = form.occupation.data
			current_app.config['USERS_COLLECTION'].update_one({"id":user_id},{'$set':user_info},upsert = True)
			return redirect(url_for('.show_user_f_id',user_id = user_id))
		return render_template('edit_user_form.html',form=form)		
 	return redirect(url_for('.show_user_f_id',user_id = user_id))

@main.route("/user/<int:user_id>/delete")
def delete_user(user_id):
	current_app.config['USERS_COLLECTION'].find_one_and_delete({"id":user_id})
	return redirect(url_for('.show_users'))
 	

@main.route("/user/<int:user_id>/movies")
def show_u_rela_movies(user_id):
	# mode = 0, 未评分的资源
	# mode = 1, 已评分的资源
	# mode = 2, 推荐的资源
	# "/user/<int:user_id>/movies?mode=0"
	# "/user/<int:user_id>/movies?mode=1" the rated movies
	mode = int(request.args.get('mode',0))
	if mode == 1:
		total = current_app.config['RATE_COLLECTION'].find({"user_id":user_id}).count()
		page, per_page, offset = get_page_items()
		pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap3',record_name="User rated movie list")
		movie_rate_cursor = current_app.config['RATE_COLLECTION'].find({"user_id":user_id},{"movie_id":1,"_id":0,"rate_score":1}).skip(offset).limit(per_page).sort("rate_score",DESCENDING)
		genre_info = current_app.config['GENRE_COLLECTION'].find_one({},{"_id":0})	
		movies_info = []
		for item in movie_rate_cursor:
			item_dict = dict({})
			item_dict["movie_id"] = int(item["movie_id"])
			item_dict["rate_score"] = item["rate_score"]
			movie = current_app.config['MOVIES_COLLECTION'].find_one({"id":item_dict["movie_id"]},{"_id":0})
			item_dict["title"] = movie["title"]		
			# item_dict["genre"] = movie["genre"]			
			genre_desc = ""
			for x in movie["genre"]:
				desc = genre_info[str(x)]
				genre_desc += desc + "|"
			item_dict["genre"] = genre_desc[:-1]
			movies_info.append(item_dict)
		return render_template('user_rate_movie.html',mode = 1,user_id = user_id, movies=movies_info,page=page,per_page=per_page,pagination=pagination)
	elif mode == 0:
		total_movies_cursor = current_app.config['MOVIES_COLLECTION'].find({},{"id":1,"_id":0})
		total_movies_list = list([])
		for item in total_movies_cursor:
			total_movies_list.append(item["id"])
		
		total_movies_num = len(total_movies_list)
		page, per_page, offset = get_page_items()
		
		rate_movie_cursor = current_app.config['RATE_COLLECTION'].find({"user_id":user_id},{"movie_id":1,"_id":0,"rate_score":1})
		rate_movie_list = list([])
		for item in rate_movie_cursor:
			rate_movie_list.append(item["movie_id"])
		unrate_movie_list = list(set(total_movies_list)-set(rate_movie_list))
		total = len(unrate_movie_list)
		pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap3',record_name="User not rated movie list")
		unrate_movie_cursor = current_app.config['MOVIES_COLLECTION'].find({"id":{"$in":unrate_movie_list}},{"_id":0}).skip(offset).limit(per_page)
		genre_info = current_app.config['GENRE_COLLECTION'].find_one({},{"_id":0})
		movies_info = []	
		for item in unrate_movie_cursor:
			item_dict = dict({})
			item_dict["movie_id"] = int(item["id"])
			item_dict["title"] = item["title"]		
			genre_desc = ""
			for x in item["genre"]:
				desc = genre_info[str(x)]
				genre_desc += desc + "|"
			item_dict["genre"] = genre_desc[:-1]
			movies_info.append(item_dict)
		return render_template('user_rate_movie.html',mode = 0,user_id = user_id, movies=movies_info,page=page,per_page=per_page,pagination=pagination)
	else:
		pass
	return redirect(url_for('.show_user_f_id',user_id = movie_id))

@main.route("/user/<int:user_id>/movie/<int:movie_id>/delete")
def relieve_rlea_u_movie(user_id,movie_id):
	current_app.config['RATE_COLLECTION'].find_one_and_delete({"user_id":user_id,"movie_id":movie_id})
 	return redirect(url_for('.show_u_rela_movies',user_id = user_id,mode=1))

#/user/rate/movie?operate=edit&user_id=1&movie_id=1
@main.route("/user/rate/movie")
def update_u_rela_movie():
	operate = request.args.get('operate',"show")
	if operate == "edit":
		user_id = request.args.get('user_id',0)
		movie_id = request.args.get('movie_id',0)
		if user_id and movie_id:
			return redirect(url_for('.update_rate',user_id=user_id,movie_id=movie_id))
	elif operate == "delete":
		user_id = request.args.get('user_id',0)
		movie_id = request.args.get('movie_id',0)
		if user_id and movie_id:
			return redirect(url_for('.relieve_rlea_u_movie',user_id=user_id,movie_id=movie_id))
	else:
		pass
		# return redirect(url_for('.show_u_rela_movies',user_id = user_id,mode=1))
	return redirect(url_for('.show_user_f_id',user_id = user_id))

@main.route("/rate")
def show_rate_info():
	user_id = int(request.args.get('user_id',0))
	movie_id = int(request.args.get('movie_id',0))
	if user_id and movie_id:	
		rate_info = current_app.config['RATE_COLLECTION'].find_one({"user_id":user_id,"movie_id":movie_id},{"_id":0})
		if rate_info:
			movie_info = current_app.config['MOVIES_COLLECTION'].find_one({"id":movie_id},{"_id":0,"title":1})
			movie_title = movie_info["title"]
			return render_template('rate.html',rate_info=rate_info,movie_title=movie_title)
	return redirect(url_for('.show_user_f_id',user_id = user_id))

@main.route("/updaterate",methods=['GET', 'POST'])
def update_rate():
	user_id = int(request.args.get('user_id',0))
	movie_id = int(request.args.get('movie_id',0))
	if user_id and movie_id:
		form = EditRateForm()
		if form.validate_on_submit():
			rate_score = int(form.rate_score.data)
			# return "rate_score"+str(rate_score)
			rate_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			current_app.config['RATE_COLLECTION'].update_one({"user_id":user_id,"movie_id":movie_id},{'$set':{"rate_score":rate_score, "rate_time":rate_time}},upsert = True)
			return redirect(url_for('.show_rate_info',user_id = user_id,movie_id = movie_id))
		return render_template('edit_rate_form.html',form=form,user_id=user_id,movie_id=movie_id)		
	return redirect(url_for('.show_user_f_id',user_id = user_id))

