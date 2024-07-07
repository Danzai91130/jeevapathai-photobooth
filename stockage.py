def inserer_photo(db, email, picture):
    """Insère un picture dans la base de données."""
    _, picture_ref = db.collection('pictures').add({
        'email': email,
        'picture': picture
    })
    print(type(picture_ref))
    print(picture_ref)
    print(f"Added document with id {picture_ref.id}")
    return picture_ref.id