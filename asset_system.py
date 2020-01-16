from flask import Flask
from flask import render_template, request, make_response, send_file
import sqlite3
from sqlite3 import Error
from itertools import groupby
from operator import itemgetter
from datetime import *
import csv
import os
import time
from functools import wraps


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'user' and auth.password == 'password':
            return f(*args, **kwargs)

        return make_response('Could not verify your login!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

    return decorated


# Database:
db_path = "assets.db"


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_all_tables():
    database = db_path

    sql_create_projects_training_list = """ CREATE TABLE IF NOT EXISTS training_list (
                                        laptop_number integer PRIMARY KEY,
                                        model text NOT NULL,
                                        serial_num text NOT NULL,
                                        available integer NOT NULL,
                                        taken_by text,
                                        return_date text,
                                        notes text
                                    ); """

    sql_create_projects_history = """ CREATE TABLE IF NOT EXISTS history (
                                        laptop_number integer NOT NULL,
                                        model text NOT NULL,
                                        serial_num text NOT NULL,
                                        loan_user text NOT NULL,
                                        loan_date_time text NOT NULL,
                                        return_date_time text,
                                        returned_by text,
                                        notes text
                                    ); """
    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_projects_training_list)
        create_table(conn, sql_create_projects_history)

    else:
        print("Error! cannot create the database connection.")


# Get the Table for "Our Training Laptops" tab:
def select_data_training_list():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM training_list")
    rows_tl = cursor.fetchall()
    rows_tl = sorted(rows_tl)
    tl_html_table = []
    for data, rows in groupby(rows_tl, itemgetter(0)):
        table = []
        for lap_num, model, serial_num, avail, taken_by, ret_date, notes in rows:
            lap_num = "Training " + str(lap_num)
            if avail == 0:
                avail = "No"
            else:
                avail = "Yes"
            if taken_by is None:
                taken_by = ""
            if ret_date is None:
                ret_date = ""
            if notes is None:
                notes = ""
            table.append(
                "<tr>\n\t<td>{}</td>\n\t<td>{}</td>\n\t<td>{}</td>\n\t<td>{}</td>\n\t<td>{}</td>\n\t<td>{}</td>\n\t<td>{}</td>\n</tr>".format(lap_num, model, serial_num, avail, taken_by, ret_date, notes))

        table = "{}\n".format('\n'.join(table))
        tl_html_table.append(table)

    tl_html_table = "\n{}\n".format('\n'.join(tl_html_table))
    return tl_html_table


# Get the Table for "Training Laptops" tab:
def select_data_training_laptops():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM training_list")
    rows_tl = cursor.fetchall()
    rows_tl = sorted(rows_tl)
    tl_html_table = []
    for data, rows in groupby(rows_tl, itemgetter(0)):
        table = []
        for lap_num, model, serial_num, avail, taken_by, ret_date, notes in rows:
            training_num = "Training " + str(lap_num)
            if avail == 0:
                avail = f'<button onclick="return_lap({lap_num})" class="button button2">Return Laptop</button>'
            else:
                loan_lap_list = [lap_num,model,serial_num]
                avail = f'<button onclick="loan_lap({loan_lap_list})" class="button button1">Loan Laptop</button>'
            if taken_by is None:
                taken_by = ""
            if ret_date is None:
                ret_date = ""
            if notes is None:
                notes = ""
            table.append(
                "<tr>\n\t<td>{}</td>\n\t<td>{}</td>\n\t<td>{}</td>\n\t<td>{}</td>\n\t<td>{}</td>\n</tr>".format(training_num, model, taken_by, ret_date, avail))

        table = "{}\n".format('\n'.join(table))
        tl_html_table.append(table)

    tl_html_table = "\n{}\n".format('\n'.join(tl_html_table))
    return tl_html_table


# change the availablity when returning laptop
def return_lap(lap_num, returned_by):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'UPDATE training_list SET available = 1, taken_by = "", return_date = "", notes = "" WHERE laptop_number = {lap_num}')
    cursor.execute(f'UPDATE history SET return_date_time = "{now}", returned_by = "{returned_by}" WHERE laptop_number = {lap_num} AND return_date_time = ""')
    conn.commit()


# change the availablity when loaning laptop
def loan_lap(lap_num, model, serial_num, loan_usr, ret_date, notes):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'UPDATE training_list SET available = 0, taken_by = "{loan_usr}", return_date = "{ret_date}", notes = "{notes}" WHERE laptop_number = {lap_num}')
    cursor.execute(f'INSERT INTO history (laptop_number, model, serial_num, loan_user, loan_date_time, return_date_time, returned_by, notes) VALUES ("{lap_num}","{model}","{serial_num}","{loan_usr}","{now}","","","{notes}")')
    conn.commit()


def clear_sql():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'UPDATE training_list SET available = 1, taken_by = "", return_date = "", notes = "" WHERE laptop_number = "*"')
    conn.commit()


def history_csv_file():
    # Export data into CSV file
    os.remove('csv/history_report_asset_system.csv')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history')
    with open(f'csv/history_report_asset_system.csv', 'w', newline='') as out_csv_file:
        csv_out = csv.writer(out_csv_file)
        # write header
        csv_out.writerow([d[0] for d in cursor.description])
        # write data
        for result in cursor:
            csv_out.writerow(result)
    conn.commit()


@app.route('/return_laptop_page', methods=['POST'])
def return_laptop_page():
    return_lap(int(request.form['laptop']), str(request.form['returned_by']))
    return ""


@app.route('/loan_laptop_page', methods=['POST'])
def loan_laptop_page():
    loan_lap_num = (request.form['laptop'])
    loan_model = (request.form['model1'])
    loan_serial_number = (request.form['serial_number'])
    loan_username = (request.form['user'])
    return_date = (request.form['return_date'])
    notes = (request.form['notes'])
    loan_lap(int(loan_lap_num), str(loan_model), str(loan_serial_number), str(loan_username), str(return_date), str(notes))
    return ""


@app.route('/', methods=["GET"])
@auth_required
def asset():
    return render_template('main_tabs_window.html', tl_rows=select_data_training_list(),
                           training_laptops_tab=select_data_training_laptops())


@app.route('/download')
@auth_required
def download_history_log():
    history_csv_file()
    time.sleep(2)
    path = "./csv/history_report_asset_system.csv"
    return send_file(path, as_attachment=True, cache_timeout=0)


if __name__ == '__main__':

    create_connection(db_path)
    app.run()



