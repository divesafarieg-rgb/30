from flask import Flask, request, jsonify
import logging
from logging.handlers import HTTPHandler
import threading
from datetime import datetime

app = Flask(__name__)

logs_storage = []


@app.route('/log', methods=['POST'])
def receive_log():
    try:
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'service': request.form.get('service', 'unknown'),
            'level': request.form.get('level', 'INFO'),
            'message': request.form.get('message', ''),
            'ip_address': request.remote_addr
        }

        logs_storage.append(log_data)
        print(f"Received log: {log_data}")

        return 'OK', 200
    except Exception as e:
        return f'Error: {str(e)}', 500


@app.route('/logs', methods=['GET'])
def get_logs():
    service_filter = request.args.get('service')
    level_filter = request.args.get('level')

    filtered_logs = logs_storage.copy()

    if service_filter:
        filtered_logs = [log for log in filtered_logs if log['service'] == service_filter]

    if level_filter:
        filtered_logs = [log for log in filtered_logs if log['level'] == level_filter]

    return jsonify(filtered_logs)


@app.route('/logs/clear', methods=['DELETE'])
def clear_logs():
    logs_storage.clear()
    return 'Logs cleared', 200


def setup_logger(service_name):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    http_handler = HTTPHandler(
        host='127.0.0.1:5000',
        url='/log',
        method='POST'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    http_handler.setFormatter(formatter)

    logger.addHandler(http_handler)

    return logger


if __name__ == '__main__':
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    app.run(host='0.0.0.0', port=5000, debug=False)
