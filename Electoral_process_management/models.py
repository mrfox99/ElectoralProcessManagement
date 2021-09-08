from flask_sqlalchemy import SQLAlchemy


database = SQLAlchemy()


class Ballot(database.Model):
    __tablename__ = "ballot"

    election_id = database.Column(database.ForeignKey('election.id'), primary_key=True)
    participant_id = database.Column(database.ForeignKey('participant.id'), primary_key=True)
    number = database.Column(database.Integer)
    election = database.relationship("Election", backref="ballots")
    participant = database.relationship("Participant", backref="ballots")


class Election(database.Model):
    __tablename__ = "election"

    id = database.Column(database.Integer, primary_key=True)
    start = database.Column(database.DateTime, nullable=False)
    end = database.Column(database.DateTime, nullable=False)
    type = database.Column(database.String(256), nullable=False)

    participants = database.relationship("Participant", secondary=Ballot.__table__, backref="elections")


class Participant(database.Model):
    __tablename__ = 'participant'

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    type = database.Column(database.String(256), nullable=False)


class Vote(database.Model):
    __tablename__ = "vote"

    id = database.Column(database.Integer, primary_key=True)
    ballot_election_id = database.Column(database.Integer)
    ballot_participant_id = database.Column(database.Integer)

    number = database.Column(database.Integer)

    __table_args__ = (database.ForeignKeyConstraint(
        ("ballot_election_id", "ballot_participant_id"),
        ["ballot.election_id", "ballot.participant_id"]
    ), {})

    # election_id = database.Column(database.ForeignKey('election.id'))
    # participant_id = database.Column(database.ForeignKey('participant.id'))
    jmbg = database.Column(database.String(13), nullable=False)
    guid = database.Column(database.String(36), nullable=False)
    info = database.Column(database.String(256), nullable=False)
    ballot = database.relationship("Ballot", backref="votes")
    # election = database.relationship("Election")
    # participant = database.relationship("Participant")
