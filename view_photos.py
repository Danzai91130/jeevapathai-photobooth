# view_photos.py
import streamlit as st
import os
from config import PHOTO_DIR

st.title('Voir les photos')
photos = [os.path.join(PHOTO_DIR, file) for file in os.listdir(PHOTO_DIR) if file.endswith('.jpg')]

if photos:
    for photo in sorted(photos, reverse=True):
        st.image(photo, caption=os.path.basename(photo))
else:
    st.write('Aucune photo disponible.')
