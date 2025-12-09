import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask App
app = Flask(__name__)

# Database Configuration (SQLite)
# valid sqlite connection string
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "restaurant.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    # Relationship: One Menu has many Dishes
    dishes = db.relationship('Dish', backref='menu', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'menuId': self.menu_id
        }

# --- ROUTES ---


@app.route("/")
def home():
    return render_template("index.html")

# --- API ENDPOINTS (CRUD) ---

# 1. Menus


@app.route("/api/menus", methods=["GET"])
def get_menus():
    menus = Menu.query.all()
    return jsonify([menu.to_dict() for menu in menus])


@app.route("/api/menus", methods=["POST"])
def create_menu():
    data = request.json
    new_menu = Menu(name=data['name'], description=data.get('description', ''))
    db.session.add(new_menu)
    db.session.commit()
    return jsonify(new_menu.to_dict()), 201


@app.route("/api/menus/<int:id>", methods=["PUT"])
def update_menu(id):
    menu = Menu.query.get_or_404(id)
    data = request.json
    menu.name = data.get('name', menu.name)
    menu.description = data.get('description', menu.description)
    db.session.commit()
    return jsonify(menu.to_dict())


@app.route("/api/menus/<int:id>", methods=["DELETE"])
def delete_menu(id):
    menu = Menu.query.get_or_404(id)
    db.session.delete(menu)
    db.session.commit()
    return jsonify({'message': 'Menu deleted'}), 200

# 2. Dishes


@app.route("/api/dishes", methods=["GET"])
def get_dishes():
    # Optional filter by menu_id
    menu_id = request.args.get('menu_id')
    if menu_id:
        dishes = Dish.query.filter_by(menu_id=menu_id).all()
    else:
        dishes = Dish.query.all()
    return jsonify([dish.to_dict() for dish in dishes])


@app.route("/api/dishes", methods=["POST"])
def create_dish():
    data = request.json
    new_dish = Dish(
        name=data['name'],
        description=data.get('description', ''),
        price=float(data['price']),
        menu_id=data['menuId']
    )
    db.session.add(new_dish)
    db.session.commit()
    return jsonify(new_dish.to_dict()), 201


@app.route("/api/dishes/<int:id>", methods=["PUT"])
def update_dish(id):
    dish = Dish.query.get_or_404(id)
    data = request.json
    dish.name = data.get('name', dish.name)
    dish.description = data.get('description', dish.description)
    if 'price' in data:
        dish.price = float(data['price'])
    db.session.commit()
    return jsonify(dish.to_dict())


@app.route("/api/dishes/<int:id>", methods=["DELETE"])
def delete_dish(id):
    dish = Dish.query.get_or_404(id)
    db.session.delete(dish)
    db.session.commit()
    return jsonify({'message': 'Dish deleted'}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)

if __name__ == "__main__":
    # It MUST listen on the port defined by the environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)