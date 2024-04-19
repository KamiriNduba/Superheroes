from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin

# Metadata for naming conventions
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize SQLAlchemy with metadata
db = SQLAlchemy(metadata=metadata)

# Hero model
class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)
    
    # Relationship with HeroPower
    hero_powers = relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')
    
    # Serialization rules
    serialize_rules = ('-hero_powers.hero', '-hero_powers.power')
    
    def __repr__(self):
        return f'<Hero {self.id}>'
    

# Power model
class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    
    # Relationship with HeroPower
    hero_powers = relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')
    
    # Serialization rules
    serialize_rules = ('-hero_powers.hero', '-hero_powers.power')
    
    # Validation for description length
    @validates('description')
    def validate_description(self, key, description):
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long.")
        return description
    
    def __repr__(self):
        return f'<Power {self.id}>'
    

# HeroPower model
class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    
    # Relationships
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id', ondelete='CASCADE'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id', ondelete='CASCADE'))
    hero = relationship('Hero', back_populates='hero_powers')
    power = relationship('Power', back_populates='hero_powers')
    
    # Validation for strength value
    @validates('strength')
    def validate_strength(self, key, strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be 'Strong', 'Weak', or 'Average'.")
        return strength
    
    def __repr__(self):
        return f'<HeroPower {self.id}>'
