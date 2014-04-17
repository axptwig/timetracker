from flask_tracking.data import CRUDMixin, db


import datetime

class Entry(CRUDMixin, db.Model):
    __tablename__ = 'tracking_entries'


    user_id = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    punchIn = db.Column(db.TIMESTAMP)
    punchOut = db.Column(db.TIMESTAMP, default = datetime.datetime.min)
    punchInComment = db.Column(db.String)
    punchOutComment = db.Column(db.String)
    id = db.Column(db.Integer, primary_key = True)

    def __repr__(self):
        return '<Entry {:d}>'.format(self.id)

    def __init__(self, user_id=None):
        self.user_id = user_id
        self.punchIn = datetime.datetime.now()

    def punch_out(self):
        self.punchOut = datetime.datetime.now()
        db.session.commit()

    def updateComment(self, comment):
        self.punchOutComment = comment
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        return str(self.punchOut)




class Site(CRUDMixin, db.Model):
    __tablename__ = 'tracking_site'

    base_url = db.Column(db.String)
    visits = db.relationship('Visit', backref='site', lazy='select')
    user_id = db.Column(db.Integer, db.ForeignKey('users_user.id'))

    def __repr__(self):
        return '<Site {:d} {}>'.format(self.id, self.base_url)

    def __str__(self):
        return self.base_url


