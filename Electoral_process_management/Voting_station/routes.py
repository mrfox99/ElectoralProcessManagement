from flask import request, jsonify, make_response
from flask_jwt_extended import get_jwt
from redis import Redis
import csv
import io


from Voting_station import application
from validation import role_check
from configuration import Configuration


@application.route("/", methods=["GET"])
def index():
    return "Hello World"


@application.route("/vote", methods=["POST"])
@role_check("election_official")
def vote():
    file = request.files.get("file")
    if not file:
        return make_response(jsonify(message="Field file is missing."), 400)

    content = file.stream.read().decode("UTF-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    line = 0
    vote_list = []
    for row in reader:
        if len(row) != 2:
            return make_response(jsonify(message=f"Incorrect number of values on line {line}."), 400)
        try:
            number = int(row[1])
            if number <= 0:
                raise Exception()
        except Exception:
            return make_response(jsonify(message=f"Incorrect poll number on line {line}."), 400)
        vote_list.append((row[0], number))
        line += 1

    with Redis(host=Configuration.REDIS_HOST) as redis:
        for vote_ in vote_list:
            vote_string = str(vote_[0]) + "#" + str(vote_[1]) + "#" + str(get_jwt()["jmbg"])
            # print(vote_string)
            redis.rpush(Configuration.REDIS_VOTE_LIST, vote_string)

        bytes_list = redis.lrange(Configuration.REDIS_VOTE_LIST, 0, -1)
        # print(bytes_list)

    return make_response("", 200)
