import pgeocode
import weather
import database
import pandas as pd
import numpy as np

zipcodes = np.array(pd.read_csv("zip_code_database.csv")["zip"])


def get_coord_from_zip(zip: int):
    nomi = pgeocode.Nominatim("us")
    query = nomi.query_postal_code(zip)
    return query["latitude"], query["longitude"]


def get_zip(Userid: str):
    # first check local cache has it

    # check if database has it
    x = database.get_zip((Userid))
    return x


def set_zip(Userid: str, zip: str, Username: str):
    # first check local cache has it
    # check if database has it
    x = database.add_zip(Userid, zip, Username)
    return x


def valid_zipcode_check(zipcode: int):
    return zipcode in zipcodes
