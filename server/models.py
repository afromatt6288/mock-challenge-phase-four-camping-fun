from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    serialize_rules = ('-signups.camper', '-created_at', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    signups = db.relationship('Signup', backref='camper')
## This was in the solution code, but I do not know what it is or means... ##
    activities = association_proxy('signups', 'activity')

    def __repr__(self):
        return f'<Camper: {self.name}, Age: {self.age}>'
  
    @validates('name')
    def validate_name(self, key, name):
        campers = Camper.query.all()
        names = [camper.name for camper in campers]
        if not name:
            raise ValueError("Campers must have a name.")
        elif name in names:
            raise ValueError("Name must be unique.")
        return name
    
    @validates('age')
    def validate_age(self, key, age):
        if not age:
            raise ValueError("Campers must have an age.")
        elif age < 8:
            raise ValueError("Camper too young.")
        elif age > 18:
            raise ValueError("Camper too old.")
        return age


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    serialize_rules = ('-signups.activity', '-created_at', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

## cascade is added to allow the deletion of an Activity to also delete the Signup it is associated with ##
    signups = db.relationship('Signup', backref='activity', cascade="all, delete, delete-orphan")
## This was in the solution code, but I do not know what it is or means... ##
    campers = association_proxy('signups', 'camper')
    
    def __repr__(self):
        return f'<Activity: {self.name}, Difficulty: {self.difficulty}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    serialize_rules = ('-camper.signups', '-activity.signups', '-created_at', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    @validates('time')
    def validate_time(self, key, time):
        if not time:
            raise ValueError("signups must have a time")
        elif 1 <= time <=23:
            return time
        else:
            raise ValueError("Signups can only be between 1 hours and 23 hours.")

    @validates('camper_id')
    def validate_camper_id(self, key, camper_id):
        campers = Camper.query.all()
        ids = [camper.id for camper in campers]
        if not camper_id:
            raise ValueError("Signups must have a camper_id")
        elif not camper_id in ids:
            raise ValueError('Camper must exist.')
        # elif any(signup for signup in Signup.query.filter_by(camper_id=camper_id)):
        #     raise ValueError("Camper cannot accept the same signup twice")
        return camper_id
    
    @validates('activity_id')
    def validate_activity_id(self, key, activity_id):
        activities = Activity.query.all()
        ids = [activity.id for activity in activities]
        if not activity_id:
            raise ValueError("signups must have a activity_id")
        elif not activity_id in ids:
            raise ValueError('activity must exist.')
        return activity_id

    def __repr__(self):
        return f'<Signup: Camper: {self.camper.name}, Activity: {self.activity.name}, Time: {self.time}>'
