from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

from sqlalchemy.orm import declarative_base

Base = declarative_base()



class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-recipes.user', '-_password_hash',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')

    # Protect password_hash from being accessed directly
    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    # Password setter method: hashes the password and stores it securely
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    # Method to authenticate the user by checking password validity
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.username}, {self.bio}>'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    serialize_rules = ('-user.recipes',)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user = db.relationship('User', back_populates='recipes')

    # Validation to ensure instructions have at least 50 characters
    @validates('instructions')
    def validates_instructions(self, key, instruction):
        if len(instruction) < 50:
            raise ValueError("The instructions should be at least 50 characters long.")
        return instruction

    def __repr__(self):
        return f'<Recipe {self.title}, {self.instructions}>'
