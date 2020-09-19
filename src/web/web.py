from datetime import datetime

from flask import Flask, jsonify, request

from src.db.db import PostgreSQLEngine
from src.util.config import Configs

DB_CONFIG = Configs["db"]
DB_ENGINE = None
DATETIME_FORMAT = "%Y-%m-%d-%H:%M"


def get_db_handler():
    global DB_ENGINE
    if DB_ENGINE is None:
        DB_ENGINE = PostgreSQLEngine(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            db=DB_CONFIG["db"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            echo=DB_CONFIG["echo"])
    return DB_ENGINE


app = Flask(__name__)


@app.route("/oceans", methods=["GET"])
def get_oceans():
    engine = get_db_handler()
    return jsonify(engine.select_all_ocean())


@app.route("/cyclones", methods=["GET"])
def get_cyclones():
    engine = get_db_handler()
    return jsonify(engine.select_all_cyclone())


@app.route("/activity", methods=["GET"])
def get_activity():
    args = request.args.to_dict()

    start_time = args.get("start_time")
    end_time = args.get("end_time")
    ocean = args.get("ocean")

    try:
        start_time = datetime.strptime(start_time, DATETIME_FORMAT) if start_time else None
        end_time = datetime.strptime(end_time, DATETIME_FORMAT) if end_time else None
    except Exception:
        return jsonify({"message": "Timestamp should be in the format "
                                   f"{DATETIME_FORMAT}"})

    engine = get_db_handler()
    return jsonify(engine.select_activity(
        start_time=start_time,
        end_time=end_time,
        ocean=ocean))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
