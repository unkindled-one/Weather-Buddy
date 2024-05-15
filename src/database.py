import psycopg2
import os
import sqlite3


def get_preference(Userid: str):
    # def add_preference(Userid: int, pref: int):
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        cur.execute("SELECT pref FROM userpreference WHERE userid = " + Userid + "")
        var = cur.fetchone()
        if cur.rowcount == 0:
            x = -1
        else:
            x = var[0]

        cur.close()
        return x

    except Exception as error:
        print("Cause: {}".format(error))
        return -1

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


def add_preference(Userid: str, pref: str):
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO userpreference (userid,pref) values ("
            + Userid
            + ","
            + pref
            + ") ON CONFLICT (userid) DO UPDATE SET pref = "
            + pref
            + ""
        )
        conn.commit()
        cur.close()
        return 1

    except Exception as error:
        print("Cause: {}".format(error))
        return -1

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


def update_preference(Userid: str, pref: str):
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        cur.execute(
            "UPDATE userpreference set pref = "
            + pref
            + " WHERE userid = "
            + Userid
            + ""
        )
        conn.commit()
        cur.close()
        return 1

    except Exception as error:
        print("Cause: {}".format(error))
        return -1

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


def add_zip(Userid: str, zip: str, Un: str):
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO userpreference (userid,zipcode) values ("
            + Userid
            + ","
            + zip
            + ") ON CONFLICT (userid) DO UPDATE SET zipcode = "
            + zip
            + ""
        )
        conn.commit()
        cur.execute(
            "UPDATE userpreference SET username = '"
            + Un
            + "' WHERE userid = "
            + Userid
            + ""
        )
        # cur.execute("INSERT INTO userpreference (userid,username) VALUES (" + Userid + "," + Un + ") ON CONFLICT (id) DO UPDATE SET username = "+Un+"")
        # cur.execute("INSERT INTO userpreference (username) values (" + Un + ") WHERE userid = " + Userid + " ON CONFLICT (userid) DO UPDATE SET username = " + Un + "")
        conn.commit()
        cur.close()
        return 1

    except Exception as error:
        print("Cause: {}".format(error))
        return -1

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


def get_zip(Userid: str):
    # def add_preference(Userid: int, pref: int):
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        cur.execute("SELECT zipcode FROM userpreference WHERE userid = " + Userid + "")
        var = cur.fetchone()
        if cur.rowcount == 0:
            x = -1
        else:
            x = var[0]

        cur.close()
        return x

    except Exception as error:
        print("Cause: {}".format(error))
        return -1

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


def test_connection():
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        cur.execute(
            """CREATE TABLE USERPREFERENCE
              (USERID INT PRIMARY KEY     NOT NULL,
              USERNAME        TEXT,
              PREF            INT,
              ZIPCODE         INT,
              REMINDERHOUR    INT,
              REMINDERMINUTE  INT);"""
        )
        print("Table created successfully")

        # cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
        #   VALUES (1, 'Paul', 32, 'California', 20000.00 )");

        conn.commit()

        conn.commit()
        cur.close()
    except Exception as error:
        print("Cause: {}".format(error))

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


def add_reminder(Userid: str, hour: str, min: str):
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        # cur.execute("SELECT "+Userid+" FROM userpreference");
        # cur.execute("INSERT INTO userpreference (userid,zipcode) values (" + Userid + "," + zip + ") ON CONFLICT (userid) DO UPDATE SET zipcode = " + zip + "")
        cur.execute(
            "INSERT INTO userpreference (userid,reminderhour) values ("
            + str(Userid)
            + ","
            + str(hour)
            + ") ON CONFLICT (userid) DO UPDATE SET reminderhour = "
            + str(hour)
            + ""
        )

        cur.execute(
            "INSERT INTO userpreference (userid,reminderminute) values ("
            + str(Userid)
            + ","
            + str(min)
            + ") ON CONFLICT (userid) DO UPDATE SET reminderminute = "
            + str(min)
            + ""
        )
        conn.commit()

        cur.close()
        return 1

    except Exception as error:
        print("Cause: {}".format(error))
        return -1

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


def get_reminder(Userid: str):
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT reminderhour FROM userpreference WHERE userid = " + Userid + ""
        )
        hour = cur.fetchone()
        cur.execute(
            "SELECT reminderminute FROM userpreference WHERE userid = " + Userid + ""
        )
        min = cur.fetchone()
        conn.commit()

        cur.close()
        return hour[0], min[0]

    except Exception as error:
        print("Cause: {}".format(error))
        return ["error", "error"]

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


def get_ids_from_time(hour: str, minute: str):
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        cur.execute(
            f"SELECT userid,username FROM userpreference WHERE reminderhour={hour} AND reminderminute={minute}"
        )
        users = cur.fetchall()
        conn.commit()

        cur.close()
        return users

    except Exception as error:
        print("Cause: {}".format(error))
        return ["error", "error"]

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


def get_all_users():
    """
    Gets all users from the database. Used for checking if the user has warnings in their area.
    """
    conn = None
    try:
        conn = sqlite3.connect("../database.db")
        cur = conn.cursor()

        cur.execute(f"SELECT zipcode,username,userid FROM userpreference")
        users = cur.fetchall()
        conn.commit()
        cur.close()
        return users

    except Exception as error:
        print("Cause: {}".format(error))
        return ["error", "error"]

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


if __name__ == "__main__":
    test_connection()

