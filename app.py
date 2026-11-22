import os
import pickle
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

with (APP_DIR / "movie_dict.pkl").open("rb") as movie_file:
    movies = pd.DataFrame(pickle.load(movie_file))

with (APP_DIR / "similarity.pkl").open("rb") as similarity_file:
    similarity = pickle.load(similarity_file)


def get_tmdb_credentials():
    bearer_token = os.getenv("TMDB_BEARER_TOKEN", "").strip()
    api_key = os.getenv("TMDB_API_KEY", "").strip()

    secrets_files = (
        APP_DIR / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml",
    )
    if any(path.is_file() for path in secrets_files):
        bearer_token = bearer_token or str(
            st.secrets.get("TMDB_BEARER_TOKEN", "")
        ).strip()
        api_key = api_key or str(st.secrets.get("TMDB_API_KEY", "")).strip()

    return bearer_token, api_key


def fetch_poster(movie_id, session, bearer_token, api_key):
    headers = {}
    params = {}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    elif api_key:
        params["api_key"] = api_key

    response = session.get(
        f"{TMDB_MOVIE_URL}/{int(movie_id)}",
        headers=headers,
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    poster_path = response.json().get("poster_path")
    if not poster_path:
        return None
    return f"{TMDB_IMAGE_URL}{poster_path}"


def recommend(movie_title):
    matching_indices = movies.index[movies["title"] == movie_title]
    if matching_indices.empty:
        raise ValueError(f"Movie not found: {movie_title}")

    movie_index = matching_indices[0]
    distances = similarity[movie_index]
    recommended_indices = sorted(
        (index for index in range(len(movies)) if index != movie_index),
        key=lambda index: distances[index],
        reverse=True,
    )[:5]

    return [
        (movies.iloc[index]["title"], movies.iloc[index]["movie_id"])
        for index in recommended_indices
    ]


st.title("Movies Recommender System")

selected_movie = st.selectbox(
    "Choose a movie",
    movies["title"].tolist(),
)

if st.button("Recommend"):
    recommendations = recommend(selected_movie)
    if not recommendations:
        st.warning("No recommendations were found for this movie.")
    else:
        bearer_token, api_key = get_tmdb_credentials()
        posters = [None] * len(recommendations)
        api_error = None

        if bearer_token or api_key:
            with requests.Session() as session:
                for index, (_, movie_id) in enumerate(recommendations):
                    try:
                        posters[index] = fetch_poster(
                            movie_id, session, bearer_token, api_key
                        )
                    except requests.RequestException as error:
                        response = getattr(error, "response", None)
                        status_code = getattr(response, "status_code", None)
                        if status_code:
                            api_error = (
                                f"TMDB returned HTTP {status_code}. "
                                "Check your credentials and API access."
                            )
                        else:
                            api_error = (
                                f"TMDB request failed ({type(error).__name__}). "
                                "Check your network connection and TMDB availability."
                            )
                        break
        else:
            st.warning(
                "TMDB credentials are not configured, so posters cannot be loaded. "
                "Set TMDB_BEARER_TOKEN or TMDB_API_KEY in your environment or "
                "Streamlit secrets."
            )

        if api_error:
            st.warning(api_error)

        columns = st.columns(len(recommendations))
        for column, (title, _), poster in zip(columns, recommendations, posters):
            with column:
                st.write(title)
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.caption("Poster unavailable")