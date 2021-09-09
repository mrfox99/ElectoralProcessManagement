# Electoral Process Management

A RESTfull web service made in python with Flask and SQLAlchemy. It consists of two subsystems:
- Authentification - responsible for user accounts management using JSON Web Tokens (JWT)
- Electoral Process Management - implements core system functionality

The web service can be deployed on Docker Swarm with the appropriate dockerfiles and compose files.

Each subsytem has (bash and bat) scripts to run in development mode (development.sh|bat), deployment on Docker mode (deployment.sh|bat) and  deployment on Docker Swarm mode (stack.sh|bat)