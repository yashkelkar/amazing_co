from employee_management.api.v1.model import db


class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.String(256), primary_key=True)
    name = db.Column(db.String(256), unique=False)
    parent = db.column(db.String(256), unique=False)
    root = db.column(db.String(256), unique=False)
    height = db.column(db.Integer, unique=False)


class Relationship(db.Model):
    __tablename__ = 'relationship'

    id = db.Column(db.String(256), primary_key=True)
    ancestor = db.Column(db.String(256), unique=False)
    descendant = db.column(db.String(256), unique=False)