from sqlalchemy import and_, or_
from datetime import datetime
from dateutil.parser import isoparse

from models import *

NUM_OF_MANDATES = 250
CENSUS = 5


class ParticipantService:
    @staticmethod
    def is_name_valid(name):
        if name is "":
            return False

        if type(name) != str:
            return False

        if len(name) == 0:
            return False

        return True

    @staticmethod
    def is_type_valid(_type):
        if _type is "":
            return False

        if type(_type) != bool:
            return False

        return True

    @staticmethod
    def create_participant(name, individual):
        if not ParticipantService.is_name_valid(name):
            return "Field name is missing.", 400

        if not ParticipantService.is_type_valid(individual):
            return "Field individual is missing.", 400

        if individual:
            type_ = "individual"
        else:
            type_ = "political_party"
        participant = Participant(name=name, type=type_)

        database.session.begin()
        database.session.add(participant)
        database.session.commit()

        return participant.id, 200

    @staticmethod
    def get_participant():

        participants = Participant.query.all()

        participants_list = []

        for participant in participants:
            participants_list.append({
                "id": participant.id,
                "name": participant.name,
                "individual": participant.type == "individual"
            })

        return participants_list, 200


class ElectionService:
    @staticmethod
    def is_date_valid(datetime_):
        if type(datetime_) != str:
            return False

        try:
            isoparse(datetime_)
        except Exception:
            return False

        return True

    @staticmethod
    def is_type_valid(_type):
        if _type is "":
            return False

        if type(_type) != bool:
            return False

        return True

    @staticmethod
    def are_participants_valid(participant_ids, election_type):
        if participant_ids is "":
            return False

        if type(participant_ids) != list:
            return False

        if len(participant_ids) < 2:
            return False

        for participant_id in participant_ids:
            participant = Participant.query.filter(Participant.id == participant_id).first()
            if not participant:
                return False
            if election_type == "president" and not participant.type == "individual":
                return False
            if election_type == "parliament" and not participant.type == "political_party":
                return False

        return True

    @staticmethod
    def create_election(start, end, individual, participant_ids):
        database.session.begin()
        if start is "":
            return "Field start is missing.", 400

        if end is "":
            return "Field end is missing.", 400

        if individual is "" or not ElectionService.is_type_valid(individual):
            return "Field individual is missing.", 400

        if participant_ids is "":
            return "Field participants is missing.", 400

        if not ElectionService.is_date_valid(start) or not ElectionService.is_date_valid(end):
            return "Invalid date and time.", 400

        start_datetime = isoparse(start)
        end_datetime = isoparse(end)

        if not (start_datetime < end_datetime):
            return "Invalid date and time.", 400

        overlapping_election = Election.query.filter(
            or_(
                and_(Election.start <= start_datetime,
                     start_datetime < Election.end),
                and_(Election.start <= end_datetime,
                     end_datetime < Election.end)
            )
        ).first()

        if overlapping_election:
            return "Invalid date and time.", 400

        if individual:
            type_ = "president"
        else:
            type_ = "parliament"

        if not ElectionService.are_participants_valid(participant_ids, type_):
            return "Invalid participants.", 400

        election = Election(start=start_datetime, end=end_datetime, type=type_)

        database.session.add(election)

        number = 1
        ballot_list = []
        for participant_id in participant_ids:
            ballot = Ballot(participant_id=participant_id, number=number)
            number += 1
            ballot_list.append(ballot)

        election.ballots.extend(ballot_list)

        database.session.commit()

        return list(range(1, number)), 200

    @staticmethod
    def get_elections():

        elections = Election.query.all()

        election_list = [
            {
                "id": election.id,
                "start": election.start.isoformat(),
                "end": election.end.isoformat(),
                "individual": election.type == "president",
                "participants": [
                    {
                        "id": participant.id,
                        "name": participant.name
                    }
                    for participant in election.participants
                ]
            }

            for election in elections
        ]

        return election_list, 200

    @staticmethod
    def are_elections_over(election):
        return election.end < datetime.now()

    @staticmethod
    def get_results(id_):

        election = Election.query.filter(Election.id == id_).first()

        if not election:
            return "Election does not exist.", 400

        if not ElectionService.are_elections_over(election):
            return "Election is ongoing.", 400

        invalid_votes = Vote.query.filter(and_(Vote.ballot_election_id == election.id,
                                               Vote.info != "")).all()

        invalid_votes_list = [
            {
                "electionOfficialJmbg": invalid_vote.jmbg,
                "ballotGuid": invalid_vote.guid,
                "pollNumber": invalid_vote.number,
                "reason": invalid_vote.info
            }
            for invalid_vote in invalid_votes
        ]

        vote_number = len(Vote.query.filter(and_(Vote.ballot_election_id == election.id,
                                                 Vote.info == "")).all())

        participants_list = []

        if election.type == "president":
            for ballot in election.ballots:
                participants_list.append({
                    "pollNumber": ballot.number,
                    "name": ballot.participant.name,
                    "result": round(len(ballot.votes) / vote_number if vote_number else 0, 2)

                })

        elif election.type == "parliament":
            ballots_with_mandates_and_votes = [
                [ballot, 0, len(ballot.votes), len(ballot.votes) / vote_number >= 0.05]
                for ballot in election.ballots
                # if len(ballot.votes) / vote_number >= 0.05
            ]

            for counter in range(0, 250):
                participant = None
                votes = -1
                for tmp in ballots_with_mandates_and_votes:
                    if tmp[3] and tmp[2] / (tmp[1] + 1) > votes:
                        votes = tmp[2] / (tmp[1] + 1)
                        participant = tmp
                participant[1] += 1

            for ballot_with_ in ballots_with_mandates_and_votes:
                participants_list.append({
                    "pollNumber": ballot_with_[0].number,
                    "name": ballot_with_[0].participant.name,
                    "result": ballot_with_[1]
                })

        return (participants_list, invalid_votes_list), 200
