# Script to consume the GitHub API
import requests
import json
import sys
import getopt
import subprocess
import os
import pandas

# considering a db as a .csv file

# create a db
def _create_db(name):
    """
    Create a new database.

    Args:
        name (str): The name of the database.

    Returns:
        None

    """
    # create a new file

    # check if file exists
    if os.path.exists(name):
        # skip
        return

    with open(name, "w") as f:
        f.write("")

    return

# delete a db
def _delete_db(name):
    """
    Delete a database.

    Args:
        name (str): The name of the database.

    Returns:
        None

    """
    # delete a file
    os.remove(name)

    return

# add row to db
def _write_to_db(name, row):
    """
    Add a row to a database.

    Args:
        name (str): The name of the database.
        row (str): The row to be added to the database.

    Returns:
        None

    """
    # add row to file
    print(row)

    # convert row to string, spliting elements by semicolon
    row = ";".join(row)
    with open(name, "a") as f:
        f.write(row + "\n")

    return

# read db
def _read_db(name):
    """
    Read a database.

    Args:
        name (str): The name of the database.

    Returns:
        list: A list of rows in the database.

    """
    # read file
    with open(name, "r") as f:
        lines = f.readlines()

    return lines

# correct csv data
def _correct_csv_data(data):
    """
    Correct the data in a CSV file.

    Args:
        data (list): The data to be corrected.

    Returns:
        list: The corrected data.

    """
    # get column url and remove '' and "" if the url is inside
    csv = pandas.read_csv("cachyos.csv", sep=";")
    data = csv["url"].tolist()
    print(data)

    # if data is nan, replace with missing
    data = [x if str(x) != "nan" else "missing" for x in data]

    data = [x.replace("'", "") for x in data]
    data = [x.replace('"', "") for x in data]

    csv["url"] = data

    pandas.DataFrame.to_csv(csv, "cachyos.csv", sep=";", index=False)
    
# get file content
def _view_db(name):
    """
    View the contents of a database.

    Args:
        name (str): The name of the database.

    Returns:
        None

    """
    # read file
    csv = pandas.read_csv("cachyos.csv", sep=";")

    # make sure all data is string
    csv = csv.astype(str)

    # convert data to dict
    data = csv.to_dict("records")

    #print(data)

    repo = subprocess.run(["gum", "table", "--separator=;", "--file=cachyos.csv", "--columns=packages,version,release,url", "--widths=30,30,30,30"], text=True)



    return