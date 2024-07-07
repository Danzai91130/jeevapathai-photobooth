import streamlit as st
import os
import time
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import ast
import firebase_admin
from firebase_admin import credentials, storage, firestore
from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, PHOTO_DIR, GIF_PATH, FIREBASE_PROJECT_ID

# Convertir les informations d'identification de la base de données en dictionnaire
db_creds = ast.literal_eval(st.secrets.db_credentials['json_credentials'])

# Vérifier si l'application Firebase est déjà initialisée
if not firebase_admin._apps:
    cred = credentials.Certificate(db_creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': f'{FIREBASE_PROJECT_ID}.appspot.com'
    })

# Initialiser le client Firestore
db = firestore.client()

# Initialiser le bucket de stockage
bucket_name = f'{FIREBASE_PROJECT_ID}.appspot.com'
bucket = storage.bucket(bucket_name)

if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

def capture_photo(filename):
    os.system(f'gphoto2 --capture-image-and-download --filename={filename}')

def send_email(recipient, subject, body):
    msg = EmailMessage()
    msg['From'] = formataddr(('😎Photobooth Jeevapathai🎥', SMTP_USER))
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

# Fonction pour téléverser une photo dans Firebase Storage et enregistrer les métadonnées dans Firestore
def upload_to_firebase(local_path, filename, email):
    # Upload de la photo dans le bucket Firebase Storage
    blob = bucket.blob(filename)
    blob.upload_from_filename(local_path)
    blob.make_public()

    # Enregistrer les métadonnées dans Firestore
    doc_ref = db.collection('photos').document(filename)
    doc_ref.set({
        'email': email,
        'photo_url': blob.public_url
    })

    return blob.public_url

st.title('Prendre une photo')
email_placeholder = st.empty()
email = email_placeholder.text_input('Entrez votre email :')
button_placeholder = st.empty()
ok_button = button_placeholder.button('Prendre une photo')
if ok_button:
    if email:
        try:
            validate_email(email)
            gif_placeholder = st.empty()
            gif_placeholder.image(GIF_PATH, caption='Souriez !')

            countdown_placeholder = st.empty()
            for i in range(10, 0, -1):
                countdown_placeholder.text(f"Photo dans {i} secondes...")
                time.sleep(1)

            countdown_placeholder.empty()  # Supprimer le message de décompte

            loading_message_placeholder = st.empty()
            loading_message_placeholder.text("Chargement de votre photo...")

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            photo_filename = f'photo_{timestamp}.jpg'
            photo_path = os.path.join(PHOTO_DIR, photo_filename)
            capture_photo(photo_path)

            photo_url = upload_to_firebase(photo_path, photo_filename, email)
            send_email(email, 'Votre photo Photobooth', f"Merci d'utiliser notre photobooth ! Voici le lien vers votre photo : {photo_url}")
            loading_message_placeholder.empty()  # Supprimer le message de chargement
            countdown_placeholder.empty() 
            gif_placeholder.empty()
            email_placeholder.empty()
            button_placeholder.empty()
            st.image(photo_path, caption='Voici votre photo !')

            photo_url = upload_to_firebase(photo_path, photo_filename, email)
            st.success(f"L'e-mail avec le lien vers votre photo a été envoyé à {email}")
            
            # Bouton pour prendre une nouvelle photo sans rafraîchir automatiquement la page
            if st.button('Nouvelle photo'):
                st.experimental_rerun()
        except EmailNotValidError as e:
            st.error(f'Email invalide : {e}')
        except Exception as e:
            st.error(f'Erreur lors de la prise ou de l\'envoi de la photo : {e}')
    else:
        st.error('Veuillez entrer un email valide.')
