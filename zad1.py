from flask import Flask, jsonify, g, request, abort, json
import sqlite3
import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

DATABASE = "tasks.db"


def get_db():  # function returning database
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext  # function closing connection with database
def close_connection():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')  # default route to the website
def welcome():
    return 'Welcome'


@app.route('/todolist', methods=['GET', 'POST'])  # route /todolist with no arguments
def give():

    db = get_db()
    cursor = db.cursor()

    if request.method == 'GET':

        result = []

        idd = cursor.execute('SELECT id FROM tasks ').fetchall()
        title = cursor.execute('SELECT title FROM tasks').fetchall()
        done = cursor.execute('SELECT done FROM tasks').fetchall()
        author_ip = cursor.execute('SELECT author_ip FROM tasks').fetchall()
        created_date = cursor.execute('SELECT created_date FROM tasks').fetchall()
        done_date = cursor.execute('SELECT done_date FROM tasks').fetchall()

        a = len(title)
        for i in range(a):

            dic = {
                'id': None,
                'title': None,
                'done': None,
                'author_ip': None,
                'created_date': None,
                'done_date': None
            }

            dic['id'] = idd[i][0]
            dic['title'] = title[i][0]
            dic['done'] = done[i][0]
            dic['author_ip'] = author_ip[i][0]
            dic['created_date'] = created_date[i][0]
            dic['done_date'] = done_date[i][0]

            result.append(dic)

        return jsonify(result)

    elif request.method == 'POST':

        data = request.get_json()

        if data['title'] is None:
            return abort(400)

        title = data['title']

        done_date = None

        if 'done' in data:
            done = data['done']
        else:
            done = False

        if 'done' in data and data['done'] is True and 'done_date' in data:
            done_date = data['done_date']

        if 'done' in data and data['done'] is True and 'done_date' not in data:
            done_date = datetime.datetime.utcnow()

        if 'done_date' in data:
            if 'done' in data and data['done'] is False and data['done_date'] is not None:
                return abort(400)

            if 'done' in data and data['done'] is False and data['done_date'] is None:
                done_date = data['done_date']

        author_ip = request.remote_addr
        created_date = datetime.datetime.utcnow()

        cursor.execute(
            'INSERT INTO tasks (Title, Done, Author_ip, Created_date, Done_date) VALUES (?,?,?,?,?)',
            (title, done, author_ip, created_date, done_date)).fetchall()

        db.commit()
        cursor.close()

        db = get_db()
        cursor = db.cursor()

        res = {
            'task_id': None
        }

        # PRZYJMUJE ZALOZENIE ZE NIE MA DWOCH ZADAN O TYM SAMYM TYTULE
        id2 = cursor.execute('SELECT id FROM tasks WHERE title = ?', (title, )).fetchall()
        res['task_id'] = int(id2[0][0])

        cursor.close()
        return jsonify(res)

    cursor.close()


# route /todolist with id argument named number
@app.route('/todolist/<int:number>', methods=['GET', 'DELETE', 'PATCH'])
def funct(number):

    db = get_db()
    cursor = db.cursor()

    check = cursor.execute('SELECT title FROM tasks WHERE id = ?', (number,)).fetchall()
    if len(check) == 0:
        return abort(404)

    if request.method == 'GET':

        to_write = {
            'title': None,
            'done': None,
            'author_ip': None,
            'created_date': None,
            'done_date': None
        }

        result = cursor.execute('SELECT title, done, author_ip, created_date, done_date FROM tasks '
                                'WHERE id = ?', (number,)).fetchall()

        to_write['title'] = result[0][0]
        to_write['done'] = result[0][1]
        to_write['author_ip'] = result[0][2]
        to_write['created_date'] = result[0][3]
        to_write['done_date'] = result[0][4]

        cursor.close()
        return jsonify(to_write)

    elif request.method == 'DELETE':

        cursor.execute('DELETE FROM tasks WHERE id = ?', (number,))
        db.commit()
        cursor.close()
        return '', 204

    elif request.method == 'PATCH':

        data = request.get_json()
        check = cursor.execute('SELECT done FROM tasks WHERE id = ?', (number,)).fetchall()
        check2 = check[0][0]
        done = 0

        if done == 0 and 'done' in data and data['done'] is False and 'done_date' in data and \
                data['done_date'] is not None:
            return abort(400)

        if check2 == 1 and 'done' in data and data['done'] is False:
            cursor.execute('UPDATE tasks SET done_date = NULL WHERE id = ?', (number,))
            done = 1

        if done == 0 and 'done' in data and data['done'] is True and 'done_date' not in data:
            cursor.execute('UPDATE tasks SET done_date = ? WHERE id = ?', (datetime.datetime.utcnow(), number))

        if done == 0 and 'done_date' in data:
            cursor.execute('UPDATE tasks SET done_date = ? WHERE id = ?', (data['done_date'], number))

        if 'title' in data:
            cursor.execute('UPDATE tasks SET title = ? WHERE id = ?', (data['title'], number))

        if 'done' in data:
            cursor.execute('UPDATE tasks SET done = ? WHERE id = ?', (data['done'], number))

        db.commit()
        cursor.close()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
