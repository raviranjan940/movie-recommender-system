import streamlit as st
import os
import requests
import zipfile
import pandas  as pd
import pickle
from PIL import Image
from random import shuffle


st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎥",
    layout="wide"
)

st.title(":red[Movie Recommender] [:red[$$\\infin$$]](https://github.com/raviranjan940/movie-recommender-system) ", )

## Defining the parameters
model_zip_link = "https://storage.googleapis.com/cushare-785.appspot.com/captain/2023-05-22%2012%3A49%3A43.509265%20Movie%20recommender%20pkl%20file/Result_EMREdl3.zip"
model_path = "model/Result_EMREdl3.zip"
main_model_path = "model/Result.pkl"
img_path = "model/img.jpg"

if not os.path.exists(model_path):
    with st.spinner("Downloading model..."):
        data = requests.get(model_zip_link)
        with open(model_path, "wb") as file:
            file.write(data.content)
            st.balloons()

if not os.path.exists(main_model_path):
    with st.spinner("Extracting model..."):   
        zip = zipfile.ZipFile(model_path)
        zip.extractall("model")
        zip.close()
        st.balloons()

movie_df = pd.read_csv("Movies.csv")
movie_list = dict(enumerate(movie_df['title'].values))


index = st.selectbox("Select a movie.", options=movie_list.keys(), format_func=lambda x : movie_list[x])

def get_results(res):
    ## Process to download the images.
    movie_id = movie_df['id'].iloc[res]
    movie_data_link = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=34abe623747f15664bb47c3d8e6c17e8"
    movie_data = requests.get(movie_data_link).json()
    poster_path = "https://image.tmdb.org/t/p/original" + movie_data['poster_path']

    poster_data = requests.get(poster_path)
    with open(img_path, 'wb') as file:
        file.write(poster_data.content)

    ## loading image
    img = Image.open(img_path)
    ## Movie title
    mv_title = movie_list[res]

    rating = movie_data['vote_average']
    tagline = movie_data['tagline']
    return img, mv_title, rating, tagline

if index is not None:
    ## Load the model
    try:
        total_rows , total_cols = 3, 5
        with st.spinner("Loading model..."):   
            model = pickle.load(open(main_model_path, 'rb'))
            results = [int(ind[0]) for ind in model[index][1:(total_rows * total_cols + 1)]]
            
            shuffle(results)
            results = iter(results)
            # print(results, type(results))
        
        with st.spinner("Loading results..."):
            for _ in range(total_rows): ## Number of rows
                for col in st.columns(total_cols): ## No of columns
                    img, mv_title, rating, tagline = get_results(next(results))

                    color = "green"
                    if rating >= 5.0 and rating < 7.5:
                        color = "orange"
                    elif rating < 5:
                        color = "red"

                    col.image(img)
                    col.markdown(f"##### {mv_title}")
                    if len(tagline) > 0:
                        col.markdown(f"***{tagline}***")
                    col.markdown(f"**:{color}[Rating {rating}]**")

                st.divider() ## ---------------------------------------

            st.balloons()
    except Exception as e:
        st.error("Unable to load model",e)







