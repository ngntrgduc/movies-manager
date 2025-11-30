MOVIE_TYPES = ['movie', 'series']

MOVIE_STATUSES = ['waiting', 'completed', 'dropped']
UNWATCHED_STATUS = 'waiting'
# WATCHED_STATUS   = 'completed'
# DROPPED_STATUS   = 'dropped'

COUNTRIES = ['China', 'Japan', 'Korea', 'US']
# TODO: soft code COUNTRIES using get_countries when `add` and `update` command 
# can add new country instead of added countries from the database
# from utils.db import get_connection
# from utils.movie import get_statuses, get_types
# from utils.movie import get_countries
# with get_connection() as con:
#     cur = con.cursor()
#     # STATUSES = get_statuses(cur) 
#     # TYPES = get_types(cur) 
#     COUNTRIES = get_countries(cur) 