from newspost import app,db

from newspost import routes

with app.app_context():
    
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)