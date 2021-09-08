from flask import request, jsonify, make_response


from Admin import application
from Admin.services import ParticipantService, ElectionService
from validation import role_check


@application.route("/", methods=["GET"])
def index():
    return "Hello World"


@application.route("/createParticipant", methods=["POST"])
@role_check("administrator")
def create_participant():
    if not request.json:
        return make_response(jsonify(message="Field name is missing."), 400)
    name = request.json.get("name", "")
    individual = request.json.get("individual", "")

    message, status = ParticipantService.create_participant(name=name, individual=individual)

    if status == 200:
        return make_response(jsonify(id=message), status)
    else:
        return make_response(jsonify(message=message), status)


@application.route("/getParticipants", methods=["GET"])
@role_check("administrator")
def get_participants():

    message, status = ParticipantService.get_participant()
    return make_response(jsonify(participants=message), status)


@application.route("/createElection", methods=["POST"])
@role_check("administrator")
def create_election():
    if not request.json:
        return make_response(jsonify(message="Field start is missing."), 400)

    start = request.json.get("start", "")
    end = request.json.get("end", "")
    individual = request.json.get("individual", "")
    participant_ids = request.json.get("participants", "")

    message, status = ElectionService.create_election(
        start=start, end=end, individual=individual, participant_ids=participant_ids
    )

    if status == 200:
        return make_response(jsonify(pollNumbers=message), status)
    else:
        return make_response(jsonify(message=message), status)


@application.route("/getElections", methods=["GET"])
@role_check("administrator")
def get_election():
    message, status = ElectionService.get_elections()

    return make_response(jsonify(elections=message), status)


@application.route("/getResults", methods=["GET"])
@role_check("administrator")
def get_results():
    if not request.args:
        return make_response(jsonify(message="Field id is missing."), 400)

    id_ = request.args.get("id", "")
    try:
        id_ = int(id_)
    except Exception:
        return make_response(jsonify(message="Field id is missing."), 400)

    message, status = ElectionService.get_results(id_)
    if status == 200:
        participants, invalid_votes = message
        return make_response(jsonify(participants=participants, invalidVotes=invalid_votes), status)
    else:
        return make_response(jsonify(message=message), status)
