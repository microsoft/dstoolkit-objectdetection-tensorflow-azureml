import streamlit as st
from PIL import Image
import requests
import json


def read_config():
    """
    Reads a JSON configuration file

    :cfg_path: Absolute path to JSON file
    :returns: Configuration as JSON object
    """
    with open('demo_config.json') as config_file:
        config = json.load(config_file)
    return config


def load_image(image_file):
    img = Image.open(image_file)
    return img


def score_img(cfg, img):
    # Call the endpoint

    headers = {'Content-Type': 'application/json'}
    if cfg['ENABLE_AUTH']:
        auth = cfg['AUTH']
        headers['Authorization'] = f'Bearer {auth}'
    resp = requests.post(cfg['ENDPOINT'], img, headers=headers)
    results = resp.text
    return results


def side_bar():
    image_file = st.sidebar.file_uploader('Upload Image', type=['png', 'jpg', 'jpeg'])
    return image_file


def main():
    page_title = "dstoolkit-objectdetection-tensorflow-azureml"
    st.set_page_config(page_title=page_title, page_icon=None, layout="centered",
                       initial_sidebar_state="auto", menu_items=None)

    # Sidebar code
    image_file = side_bar()

    col1, col2 = st.columns([6, 1])

    # Set subheader
    col1.subheader('Predicting BB on Image')
    # Get local image file

    # Download image from blobstorage (TBD later)

    if image_file is not None:
        # See image details
        file_details = {"filename": image_file.name,
                        "filetype": image_file.type,
                        "filesize": image_file.size}
        # Load image PIL
        img = load_image(image_file)

        # Make scoring a button

        # Make GT loading possible

        # Load image binary and score image in score image function

        # View Uploaded Image
        col1.image(img, use_column_width=True)

        with col1.expander("File details"):
            st.write(file_details)

        with col1.expander(".json results"):
            st.write('score results')


if __name__ == "__main__":
    main()
