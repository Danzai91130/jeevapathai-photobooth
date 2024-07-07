import streamlit as st
import firebase_admin
import ast
from firebase_admin import credentials, firestore
from config import FIREBASE_PROJECT_ID

# Convertir les informations d'identification de la base de données en dictionnaire
db_creds = ast.literal_eval(st.secrets.db_credentials['json_credentials'])

# Vérifier si l'application Firebase est déjà initialisée
if not firebase_admin._apps:
    cred = credentials.Certificate(db_creds)
    firebase_admin.initialize_app(cred, {
        'projectId': FIREBASE_PROJECT_ID
    })

# Initialiser le client Firestore
db = firestore.client()

st.title('Voir les photos')

# Récupérer les métadonnées des photos depuis Firestore
photos_ref = db.collection('photos').get()

if photos_ref:
    for photo_doc in photos_ref:
        photo_data = photo_doc.to_dict()
        photo_url = photo_data.get('photo_url')
        st.image(photo_url, use_column_width=True)
else:
    st.write('Aucune photo disponible.')
