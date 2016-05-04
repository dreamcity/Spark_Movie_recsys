import json
from . import main
from .. import recommendation_engine
 
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
from flask import Flask, current_app,render_template

@main.route("/<int:user_id>/recommend", methods=["GET"])
def user_recommend(user_id):
    recommend_nums = current_app.config['RECOMMEND_NUMS']
    if not recommend_nums:
        recommend_nums = 5
    logger.debug("User %s TOP ratings requested", user_id)
    top_ratings = recommendation_engine.get_top_ratings(user_id,recommend_nums)
    genre_info = current_app.config['GENRE_COLLECTION'].find_one({},{"_id":0})
    recommend_info = []
    for item in top_ratings:
        movie_info = {}
        title = item[0]
        movie = current_app.config['MOVIES_COLLECTION'].find_one({"title":title},{"_id":0})
        movie_info["id"] = movie["id"]
        movie_info["title"] = title
        # movie_info["genre"] = movie["genre"]
        genre_desc = ""
        for x in movie["genre"]:
            desc = genre_info[str(x)]
            genre_desc += desc + "|"
        movie_info["genre"] = genre_desc[:-1]

        movie_info["rec_score"] = item[1]
        movie_info["rank"] = item[2]
        recommend_info.append(movie_info)
    return render_template('recommends.html', user_id=user_id,movies=recommend_info)

    # return json.dumps(top_ratings)

# @main.route("/<int:user_id>/ratings/top/<int:count>", methods=["GET"])
# def top_ratings(user_id, count):
#     logger.debug("User %s TOP ratings requested", user_id)
#     top_ratings = recommendation_engine.get_top_ratings(user_id,count)
#     return json.dumps(top_ratings)
 
@main.route("/<int:user_id>/ratings/<int:movie_id>", methods=["GET"])
def movie_ratings(user_id, movie_id):
    logger.debug("User %s rating requested for movie %s", user_id, movie_id)
    ratings = recommendation_engine.get_ratings_for_movie_ids(user_id, [movie_id])
    return json.dumps(ratings)
 
 
# @main.route("/<int:user_id>/ratings", methods = ["POST"])
# def add_ratings(user_id):
#     # get the ratings from the Flask POST request object
#     ratings_list = request.form.keys()[0].strip().split("\n")
#     ratings_list = map(lambda x: x.split(","), ratings_list)
#     # create a list with the format required by the negine (user_id, movie_id, rating)
#     ratings = map(lambda x: (user_id, int(x[0]), float(x[1])), ratings_list)
#     # add them to the model using then engine API
#     recommendation_engine.add_ratings(ratings)
 
#     return json.dumps(ratings)