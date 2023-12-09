from newspost import app, db

with app.app_context():
    from newspost.model import User, Post
    db.create_all()



if __name__ == "__main__":
    app.run(debug=True)


    