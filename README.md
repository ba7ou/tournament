Tournament
==========

## Description

PostgreSQL Database storing game matches between players. A Python module manage player ranks and match pairs for the tournament.


## Installation
You need to setup an Unix environment with PostgreSQL 9.4.5 and Python 3.5.1
* create PostgreSQL database Tournament
`$psql tournament`
* import tournament.sql `\i tournament.sql`
* ctrl d to close psql
* run tournament.py `$python tournament.py`

## Tests
You can run tournament_test.py to check if everything is fine
`$python tournament_test.py`

## Contributors
This is an Udacity project for the Fullstack Nanodegree

## License
MIT License
