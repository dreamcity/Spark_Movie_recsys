#!/usr/bin/env python
#-*- coding: utf-8 -*-
# from app import app
from . import main
from flask import Flask,current_app,render_template,request,redirect,url_for
from flask.ext.paginate import Pagination
from pymongo import ASCENDING,DESCENDING
from forms import EditMovieForm
# import datetime

def get_page_items():
    page = int(request.args.get('page', 1))
    per_page = request.args.get('per_page')
    if not per_page:
        per_page = current_app.config.get('PER_PAGE', 10)
    else:
        per_page = int(per_page)

    offset = (page - 1) * per_page
    return page, per_page, offset

@main.route("/movies")
def show_movies():
	total = current_app.config['TOTAL_MOVIES']
	if not total:
		total = current_app.config['MOVIES_COLLECTION'].find().count()
	page, per_page, offset = get_page_items()
	if page * per_page > total:
		movies_info = ""
	else:
		movie_cursor = current_app.config['MOVIES_COLLECTION'].find({},{"_id":0}).skip(offset).limit(per_page)
		genre_info = current_app.config['GENRE_COLLECTION'].find_one({},{"_id":0})
		movies_info= list([])
		for item in movie_cursor:
			item_dict = dict({})
			item_dict["id"] = int(item["id"])
			item_dict["title"] = item["title"]		
			genre_desc = ""
			for x in item["genre"]:
				desc = genre_info[str(x)]
				genre_desc += desc + "|"
			item_dict["genre"] = genre_desc[:-1]
			movies_info.append(item_dict)
	pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap3',record_name="movies_info")
	return render_template('movies.html', total = total,movies=movies_info,page=page,per_page=per_page,pagination=pagination)

@main.route("/movie/<int:movie_id>")
def show_movie_f_id(movie_id):
	movie = current_app.config['MOVIES_COLLECTION'].find_one({"id":movie_id},{"_id":0})
	if not movie:return redirect(url_for('.show_movies'))
	genre_info = current_app.config['GENRE_COLLECTION'].find_one({},{"_id":0})
	movie["genre_desc"] = ""
	for x in movie["genre"]:
		desc = genre_info[str(x)]
		movie["genre_desc"] += desc + "|"
	movie["genre_desc"] = movie["genre_desc"][:-1]

	movie_pattern = {}
	movie_pattern["hot_score"] = current_app.config['RATE_COLLECTION'].find({"movie_id":movie_id}).count()

	movie_pattern["total_rate_nums"] = current_app.config['RATE_COLLECTION'].find().count()

	avg_rate_cursor = current_app.config['RATE_COLLECTION'].aggregate([{"$group":{"_id":"$movie_id","avg":{"$avg":"$rate_score"}}},{"$match":{"_id":movie_id}}])
	avg_rate = ""
	for x in avg_rate_cursor:
		avg_rate = x["avg"]
	movie_pattern["avg_rate"] = avg_rate
	return render_template('movie.html',movie=movie,movie_pattern=movie_pattern)

@main.route("/movie/add")
def add_movie():
	max_id_cursor = current_app.config['MOVIES_COLLECTION'].find({},{"id":1,"_id":0}).sort("id",DESCENDING).limit(1)
	max_id = 0
	for x in max_id_cursor:
		max_id = x["id"]
	movie_max_id = int(max_id) + 1
	return redirect(url_for('.edit_movie',movie_id = movie_max_id))

@main.route("/movie/<int:movie_id>/edit")
def edit_movie(movie_id):
	return redirect(url_for('.update_movie_info',movie_id=movie_id))

@main.route("/edit/movie",methods=['GET', 'POST'])
def update_movie_info():
	movie_id = int(request.args.get('movie_id',0))
	if movie_id :
		form = EditMovieForm()
		if form.validate_on_submit():
			movie_info = {}
			movie_info["title"] = form.title.data
			movie_info["imdb_url"] = form.imdb_url.data
			movie_info["release_time"] = form.release_time.data
			genre = form.genre.data
			genre_code = [0]*19
			genre_list = genre.split("-")
			# print genre_list,genre_code[3]
			for x in genre_list:
				genre_code[int(x)] = 1
			movie_info["genre"] = genre_list
			movie_info["genre_code"] = "".join(str(x) for x in genre_code)
			# print "movie_info",movie_info
			current_app.config['MOVIES_COLLECTION'].update_one({"id":movie_id},{'$set':movie_info},upsert = True)
			return redirect(url_for('.show_movie_f_id',movie_id = movie_id))
		return render_template('edit_movie_form.html',form=form)		
	return redirect(url_for('.show_movie_f_id',movie_id = movie_id))

@main.route("/movie/<int:movie_id>/delete")
def delete_movie(movie_id):
	current_app.config['MOVIES_COLLECTION'].find_one_and_delete({"id":movie_id})
 	return redirect(url_for('.show_movies'))
