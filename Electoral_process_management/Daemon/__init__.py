import datetime

from flask import Flask
from flask_jwt_extended import JWTManager
from redis import Redis
from sqlalchemy import and_, or_

from models import database, Vote, Election
from configuration import Configuration

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)
jwt = JWTManager(application)


def find_ongoing_election():
    now = datetime.datetime.now()
    return Election.query.filter(and_(Election.start <= now, now < Election.end)).first()


def is_pool_number_valid(election, pool_number):
    return pool_number in [ballot.number for ballot in election.ballots]


def is_ballot_unique(guid):
    if not Vote.query.filter(Vote.guid == guid).first():
        return True
    return False


def run():
    while True:
        try:
            with application.app_context():
                with Redis(host=Configuration.REDIS_HOST) as redis:
                    while True:
                        bytes_ = redis.blpop(Configuration.REDIS_VOTE_LIST)
                        vote = bytes_[1].decode("UTF-8")
                        guid, number, jmbg = vote.split("#")
                        number = int(number)
                        print(guid, number, jmbg)

                        database.session.begin()

                        election = find_ongoing_election()
                        if not election:
                            database.session.rollback()
                            continue

                        if not is_ballot_unique(guid):
                            vote = Vote(
                                ballot_election_id=election.id,
                                ballot_participant_id=None,
                                number=number,
                                jmbg=jmbg,
                                guid=guid,
                                info="Duplicate ballot.")
                        elif not is_pool_number_valid(election, number):
                            vote = Vote(
                                ballot_election_id=election.id,
                                ballot_participant_id=None,
                                number=number,
                                jmbg=jmbg,
                                guid=guid,
                                info="Invalid poll number.")
                        else:
                            for ballot in election.ballots:
                                if ballot.number == number:
                                    participant_id = ballot.participant_id
                                    break
                            vote = Vote(
                                ballot_election_id=election.id,
                                ballot_participant_id=participant_id,
                                number=number,
                                jmbg=jmbg,
                                guid=guid,
                                info="")

                        database.session.add(vote)
                        database.session.commit()

        except Exception as error:
            print(error)
