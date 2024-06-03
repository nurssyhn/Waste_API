from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/waste_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)

class Waste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, nullable=False)
    waste_type_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)

@app.route('/waste', methods=['POST'])
def create_waste():
    data = request.get_json()
    new_waste = Waste(
        building_id=data['building_id'],
        waste_type_id=data['waste_type_id'],
        quantity=data['quantity'],
        record_date=datetime.strptime(data['record_date'], '%Y-%m-%d').date(),
        student_id=data['student_id']
    )
    db.session.add(new_waste)
    db.session.commit()
    return jsonify({'message': 'Waste record created'}), 201

@app.route('/waste', methods=['GET'])
def get_wastes():
    wastes = Waste.query.all()
    result = [
        {
            'id': waste.id,
            'building_id': waste.building_id,
            'waste_type_id': waste.waste_type_id,
            'quantity': waste.quantity,
            'record_date': waste.record_date.strftime('%Y-%m-%d'),
            'student_id': waste.student_id
        } for waste in wastes
    ]
    return jsonify(result), 200

@app.route('/waste/<int:id>', methods=['GET'])
def get_waste(id):
    waste = Waste.query.get_or_404(id)
    result = {
        'id': waste.id,
        'building_id': waste.building_id,
        'waste_type_id': waste.waste_type_id,
        'quantity': waste.quantity,
        'record_date': waste.record_date.strftime('%Y-%m-%d'),
        'student_id': waste.student_id
    }
    return jsonify(result), 200

@app.route('/waste/<int:id>', methods=['PUT'])
def update_waste(id):
    data = request.get_json()
    waste = Waste.query.get_or_404(id)
    waste.building_id = data.get('building_id', waste.building_id)
    waste.waste_type_id = data.get('waste_type_id', waste.waste_type_id)
    waste.quantity = data.get('quantity', waste.quantity)
    waste.record_date = datetime.strptime(data.get('record_date', waste.record_date.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
    waste.student_id = data.get('student_id', waste.student_id)
    db.session.commit()
    return jsonify({'message': 'Waste record updated'}), 200

@app.route('/waste/<int:id>', methods=['DELETE'])
def delete_waste(id):
    waste = Waste.query.get_or_404(id)
    db.session.delete(waste)
    db.session.commit()
    return jsonify({'message': 'Waste record deleted'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email, password=password).first()
    
    if user and user.user_type == 'student':
        return jsonify({'message': 'Login successful', 'user': {
            'id': user.id,
            'name': user.name,
            'surname': user.surname,
            'email': user.email,
            'user_type': user.user_type
        }}), 200
    else:
        return jsonify({'message': 'Invalid credentials or user type'}), 401

if "__name__" == '__main__':
    db.create_all()
    app.run(debug=True)
