import streamlit as st
import pickle
import pandas as pd
import requests


movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
st.title('Movies Recommender System')

movies = pd.DataFrame(movies_dict)

selcted_movies_name = st.selectbox(
    'How would you like to be contacted?',
    (movies['title'].values)
)



def fetch_poster(movie_id):
    response = requests.get('')
    data = response.json()
    return "https://image.tmdb.org/t/p/w500"+data['poster_path']




def recommend(movie):
    movie_idx = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_idx]
    movies_list = sorted(list(enumerate(distances)),reverse=True, key=lambda x:x[1])[1:6]
    recommended_movies =[]
    recommended_movies_poster = []
    for i in movies_list:
        movie_id = i[0]
        #featch poster form apis
        recommended_movies.append(movies.iloc[i[0]].title)
        #fetch poster from api
        recommended_movies_poster = fetch_poster(movie_id)
    return recommended_movies




if st.button('Recommend'):
    recommendation = recommend(selcted_movies_name)
    for i in recommendation:
        st.write(i)