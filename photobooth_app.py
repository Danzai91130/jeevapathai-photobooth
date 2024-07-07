import streamlit as st
import os
import time
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from email_validator import validate_email, EmailNotValidError
from datetime import datetime

# Configuration SMTP
SMTP_SERVER = 'smtp-mail.outlook.com'
SMTP_PORT = 587
SMTP_USER = 'poleservicejeevapathai@outlook.com'
SMTP_PASSWORD = 'Wefollowchrist91'

# Dossier pour stocker les photos
PHOTO_DIR = 'photos'

if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

# Fonctions pour capturer la photo et envoyer l'email
def capture_photo(filename):
    # Commande pour capturer une photo avec gphoto2
    os.system(f'gphoto2 --capture-image-and-download --filename={filename}')

def send_email(recipient, subject, body, attachment_path):
    msg = EmailMessage()
    msg['From'] = formataddr(('Photobooth', SMTP_USER))
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body)

    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype='image', subtype='jpeg', filename=file_name)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

# Streamlit interface
st.sidebar.title('Photobooth')
page = st.sidebar.selectbox('Choisissez une page', ['Prendre une photo', 'Voir les photos'])

if page == 'Prendre une photo':
    st.title('Prendre une photo')
    email = st.text_input('Entrez votre email :')

    if st.button('Prendre une photo'):
        if email:
            try:
                # Validation de l'email
                validate_email(email)
                st.write('Préparation pour la prise de photo dans 10 secondes...')
                time.sleep(10)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                photo_path = os.path.join(PHOTO_DIR, f'photo_{timestamp}.jpg')
                capture_photo(photo_path)
                st.image(photo_path, caption='Voici votre photo !')
                send_email(email, 'Votre photo Photobooth', 'Merci d\'utiliser notre photobooth !', photo_path)
                st.success(f'La photo a été envoyée à {email}')
                st.experimental_rerun()  # Rafraîchir la page après la prise de photo
            except EmailNotValidError as e:
                st.error(f'Email invalide : {e}')
            except Exception as e:
                st.error(f'Erreur lors de la prise ou de l\'envoi de la photo : {e}')
        else:
            st.error('Veuillez entrer un email valide.')

elif page == 'Voir les photos':
    st.title('Voir les photos')
    photos = [os.path.join(PHOTO_DIR, file) for file in os.listdir(PHOTO_DIR) if file.endswith('.jpg')]

    if photos:
        for photo in sorted(photos, reverse=True):
            st.image(photo, caption=os.path.basename(photo))
    else:
        st.write('Aucune photo disponible.')
