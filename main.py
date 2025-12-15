# alterei as linhas 21, 90 e 139 - erro no script: script.js:90:25 e script.js:79:19
from flask import Flask, jsonify, request
import pandas as pd
from demographic_filtering import output
from content_filtering import get_recommendations
from flask import send_from_directory

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

movies_data = pd.read_csv('final.csv')

app = Flask(__name__)

all_movies = movies_data[["original_title","poster_link","release_date","runtime","weighted_rating"]]

user_data = {}

@app.route("/test_db")
def test_db():
    db.collection("test").document("ping").set({"ok": True})
    return {"message": "firestore conectado com sucesso"}

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "liked": [],
            "not_liked": [],
            "did_not_watch": [],#troquei didntwatch por did_not_watch
        }
    return user_data[user_id]

def assign_val():
    m_data = {
        "original_title": all_movies.iloc[0,0],
        "poster_link": all_movies.iloc[0,1],
        "release_date": all_movies.iloc[0,2] or "N/A",
        "duration": all_movies.iloc[0,3],
        "rating":all_movies.iloc[0,4]/2
    }
    return m_data

@app.route("/movies")
def get_movie():
    movie_data = assign_val()

    return jsonify({
        "data": movie_data,
        "status": "success"
    })

@app.route("/like")
def liked_movie():
    global all_movies

    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id obrigatório"}), 400

    movie_data = assign_val()
    user = get_user_data(user_id)  # pega a “caixinha” desse usuário
    user["liked"].append(movie_data)

    print("Gostei (usuário:", user_id, ")", user["liked"])

    all_movies.drop([0], inplace=True)
    all_movies = all_movies.reset_index(drop=True)

    return jsonify({
    "status": "success",
    "movie": movie_data
    })
    
@app.route("/dislike")
def unliked_movie():
    global all_movies
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id obrigatório"}),400

    movie_data=assign_val()
    user = get_user_data(user_id)
    user["not_liked"].append(movie_data)
  
    all_movies.drop([0], inplace=True)
    all_movies=all_movies.reset_index(drop=True)
    
    return jsonify({
    "status": "success",
    "movie": movie_data
    })

@app.route("/did_not_watch")
def did_not_watch_view():
    global all_movies
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id obrigatório"}),400

    movie_data=assign_val()
    user = get_user_data(user_id)
    user["did_not_watch"].append(movie_data)#troquei didntwatch por did_not_watch
    all_movies.drop([0], inplace=True)
    all_movies=all_movies.reset_index(drop=True)
    
    return jsonify({
    "status": "success",
    "movie": movie_data
    })


@app.route('/liked')
def liked():
    #global liked_movies
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id obrigatório"}),400
    user = get_user_data(user_id)

    return jsonify({
       "data":user["liked"],
       "status": "success"
    })
@app.route('/popular_movies')
def popular_movies():
    popular_movies_data = []

    for index, row in output.iterrows():
      _p ={
          "original_title": row['original_title'],
          "poster_link": row['poster_link'],
          "release_date": row["release_date"] or "N/A",
          "duration": row['runtime'],
          "rating": row ['weighted_rating']/2
      } 
      popular_movies_data.append(_p) 

    return jsonify({
       "data":popular_movies_data,
       "status": "success"  
    })

@app.route('/didntwatch')
def didntwatch():
    #global did_not_watch
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id obrigatório"}),400

    user = get_user_data(user_id)
    return jsonify({
       "data":user["did_not_watch"],#troquei not_liked por did_not_watch
       "status": "success"  
    })

@app.route('/recommended_movies')
def recommended_movies():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id obrigatório"}),400

    user = get_user_data(user_id)

    #global liked_movies
    liked_movies = user["liked"]
    recommendations_list = []
    
    for liked_movie in liked_movies:
        output = get_recommendations(liked_movie["original_title"])
        recommendations_list.append(output)
        
    if recommendations_list:
        all_recommended = pd.concat(recommendations_list, ignore_index=True)
    else:
        all_recommended = pd.DataFrame(columns=['original_title', 'poster_link', 'release_date', 'runtime', 'weighted_rating'])    

    all_recommended.drop_duplicates(subset=["original_title"],inplace=True)

    recommended_movie_data=[]

    for index, row in all_recommended.iterrows():
        _p = {
            "original_title": row["original_title"],
            "poster_link":row['poster_link'],
            "release_date":row['release_date'] or "N/A",
            "duration": row['runtime'],
            "rating": row['weighted_rating']/2
        }
        recommended_movie_data.append(_p)

    return jsonify({
        "data":recommended_movie_data,
        "status": "success"
    })

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

if __name__ == "__main__":
  app.run()