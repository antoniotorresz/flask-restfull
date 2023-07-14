from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost/user_colors'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    colors = db.relationship('Color', secondary='user_colors', lazy='subquery', backref=db.backref('users', lazy=True))

class Color(db.Model):
    __tablename__ = 'colors'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(20), nullable=False)

user_color = db.Table('user_colors',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('color_id', db.Integer, db.ForeignKey('colors.id'), primary_key=True)
)


@app.route('/associate-color', methods=['POST'])
def associate_color():
    data = request.get_json()
    user_id = data.get('user_id')
    color_id = data.get('color_id')

    if user_id and color_id:
        user = User.query.get(user_id)
        color = Color.query.get(color_id)

        if user and color:
            user.colors.append(color)
            db.session.commit()
            return jsonify({'message': 'Color associated successfully'})
        else:
            return jsonify({'error': 'User or color not found'}), 404
    else:
        return jsonify({'error': 'Invalid user_id or color_id'}), 400

@app.route('/get-colors/<user_id>', methods=['GET'])
def get_colors(user_id):
    user = User.query.get(user_id)
    if user:
        colors = [color.color for color in user.colors]
        return jsonify({'colors': colors})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/remove-color', methods=['DELETE'])
def remove_color():
    data = request.get_json()
    user_id = data.get('user_id')
    color_id = data.get('color_id')

    if user_id and color_id:
        user = User.query.get(user_id)
        color = Color.query.get(color_id)

        if user and color:
            user.colors.remove(color)
            db.session.commit()
            return jsonify({'message': 'Color removed successfully'})
        else:
            return jsonify({'error': 'User or color not found'}), 404
    else:
        return jsonify({'error': 'Invalid user_id or color_id'}), 400

if __name__ == '__main__':
    app.run()
