import os
import mysql.connector
from flask import Flask, request, jsonify
import json
from werkzeug.utils import secure_filename
from flask_cors import CORS
import platform

import user, prints, admin

UPLOAD_FOLDER = '/usr/files'

if not platform.system() == "Linux":
    # os.mkdir("D:/Desktop/file")
    UPLOAD_FOLDER = "D:/Desktop/file"

ALLOWED_EXTENSIONS = set(['gcode'])

result = { "success": False, "data": [] }

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)

httpHeaders = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE",
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/user/<type>', methods=['POST'], defaults={'sessionId': None})
@app.route('/user/<type>/<sessionId>', methods=['GET', 'POST'])
def userHandler(type, sessionId):
    db, cursor = conDB()

    code = 500

    if request.method == 'POST':
        if type == 'login':
            result["data"], result["success"], code = user.login(db, cursor, request.json)
        elif type == 'register':
            result["data"], result["success"], code = user.register(db, cursor, request.json)
        elif type == 'changepw':
            result["data"], result["success"], code = user.changePW(db, cursor, request.json)
    
    elif request.method == 'GET':
        if type == 'group':
            result["data"], result["success"], code = user.getGroup(db, cursor, sessionId)
    
    cloDB(db)

    return jsonify(result), code, httpHeaders


@app.route('/print/<status>', methods=['GET'])
def printHandler(status):
    db, cursor = conDB()

    code = 500

    if request.method == 'GET':
        result["data"], result["success"], code = prints.getPrint(db, cursor, status)
    cloDB(db)
    
    return jsonify(result), code, httpHeaders


# @app.route('/job', methods=['POST'])
# def jobPostHandler():
#     db, cursor = conDB()

#     code = 500
#     result["data"], result["success"], code = prints.postJob(db, cursor, request.json)

#     cloDB(db)

#     return jsonify(result), code, httpHeaders


@app.route('/job', methods=['POST'], defaults={'status': None, 'sessionId': None})
@app.route('/job', methods=['PUT'], defaults={'status': None, 'sessionId': None})
@app.route('/job/<status>/<sessionId>', methods=['GET'])
def jobHandler(status, sessionId):
    db, cursor = conDB()

    code = 500

    if request.method == 'GET':
        info = { "status": status, "sessionId": sessionId}
        result["data"], result["success"], code = prints.getJob(db, cursor, info)
    
    elif request.method == 'POST':
        result["data"], result["success"], code = prints.postJob(db, cursor, request.json)
    
    elif request.method == 'PUT':
        result["data"], result["success"], code = prints.changeJobStatus(db, cursor, request.json)
    
    else:
        result["data"] = "Invalid Method"
        result["success"] = False
        code = 400
    
    cloDB(db)
    return jsonify(result), code, httpHeaders


@app.route('/admin/<table>/<status>/<sessionId>', methods=['GET'])
def adminGetHandler(table, status, sessionId):
    db, cursor = conDB()

    code = 500
    if table == "job":
        result["data"], result["success"], code = admin.getQueue(db, cursor, status, sessionId)
    elif table == "user":
        result["data"], result["success"], code = admin.getUsers(db, cursor, status, sessionId)

    cloDB(db)

    return jsonify(result), code, httpHeaders


@app.route('/admin/change', methods=['POST'])
def adminPostHandler():
    db, cursor = conDB()

    code = 500

    result["data"], result["success"], code = admin.changeJob(db, cursor, request.json)

    cloDB(db)

    return jsonify(result), code, httpHeaders


@app.route('/file', methods=['POST'])
def fileHandler():
    db, cursor = conDB()
    sql = "SELECT count(id) from print where filename = '%s'" % (request.files['file'].filename.replace(".gcode", ""))
    cursor.execute(sql)

    if cursor.fetchall()[0][0] > 0:
        if 'file' not in request.files:
            result["success"] = False
            result["data"] = "No file"
            cloDB(db)
        else:
            # TODO: Add following under else
            file = request.files['file']
            
            if file.filename == "":
                result["success"] = False
                result["data"] = "No filename"
                cloDB(db)
            else:
                # TODO: Add following under else
                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    result["success"] = True
                    result["data"] = "Successfully uploaded File"
                    cloDB(db)
                    return jsonify(result), 200, httpHeaders

    cloDB(db)
    result["success"] = False
    result["data"] = "No database reference to filename" 
    return jsonify(result), 409, httpHeaders

# NOTE: Function removed, price added to job get return
 
# @app.route('/price', methods=['POST'])
# def priceHandler():
#     db, cursor = conDB()
    
#     code = 500

#     # Request.json  - printWeight, spoolId
#     # Return        - price
#     result["data"], result["success"], code = prints.calcPrice(db, cursor, request.json["printWeight"], request.json["spoolId"])

#     cloDB(db)
#     return jsonify(result), code, httpHeaders


# ------------------------------------------------------------------------


def conDB():
    db = mysql.connector.connect(
        host="[mysq-ip]",
        user="[mysq-username]",
        passwd="[mysql-password]",
        database="[mysql_databasename]"
    )
    cursor = db.cursor()

    return db, cursor


def cloDB(db):
    db.close()


# Main
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3004)
