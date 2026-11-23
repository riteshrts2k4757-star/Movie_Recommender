# Movies Recommender

A Streamlit movie recommender that ranks films by similarity and can display
posters from The Movie Database (TMDB).

## Requirements

- Python 3.10 or later
- Git and Git LFS
- A TMDB API key or read access token to load movie posters (optional)

## Setup

Install Git LFS if it is not already installed, then clone the repository:

```powershell
git lfs install
git clone https://github.com/riteshrts2k4757-star/Movie_Recommender.git
cd Movie_Recommender
git lfs pull
```

Install the Python dependencies and start the app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The similarity model is stored with Git LFS. Make sure LFS is installed and
the model has downloaded before starting the app.

## TMDB credentials

Posters are optional. To enable them, set either `TMDB_BEARER_TOKEN` or
`TMDB_API_KEY` in your environment. For local Streamlit secrets, create
`.streamlit/secrets.toml` (this file is ignored by Git) with one of:

```toml
TMDB_BEARER_TOKEN = "your_read_access_token"
```

or

```toml
TMDB_API_KEY = "your_api_key"
```

Without credentials, recommendations still work and the app displays a notice
that posters are unavailable.

## Rebuilding the model

`movie.ipynb` contains the data preparation and similarity calculation steps.
Run its cells to regenerate the model files if needed. The notebook uses the
MovieLens/TMDb dataset files included in this repository.
