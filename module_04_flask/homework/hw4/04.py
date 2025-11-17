from flask import Flask
import subprocess
import platform
from datetime import datetime

app = Flask(__name__)


def calculate_uptime_from_boot_time(boot_time_str):
    try:
        boot_time = datetime.strptime(boot_time_str, '%d.%m.%Y, %H:%M:%S')
        current_time = datetime.now()
        uptime_delta = current_time - boot_time

        days = uptime_delta.days
        hours = uptime_delta.seconds // 3600
        minutes = (uptime_delta.seconds % 3600) // 60

        if days > 0:
            return f"up {days} days, {hours} hours, {minutes} minutes"
        elif hours > 0:
            return f"up {hours} hours, {minutes} minutes"
        else:
            return f"up {minutes} minutes"

    except Exception as e:
        return f"system booted at {boot_time_str}"


def get_uptime_windows():
    try:
        result = subprocess.run(
            ['systeminfo'],
            capture_output=True,
            text=True,
            encoding='cp866',
            check=True,
            timeout=30
        )

        for line in result.stdout.split('\n'):
            if 'System Boot Time:' in line or 'Время загрузки системы:' in line:
                boot_time_str = line.split(':', 1)[1].strip()
                return calculate_uptime_from_boot_time(boot_time_str)

        return "uptime information not available"

    except Exception as e:
        return f"error: {str(e)}"


def get_uptime_linux():
    try:
        result = subprocess.run(
            ['uptime', '-p'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        try:
            result = subprocess.run(
                ['uptime'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            return f"error: {str(e)}"


@app.route('/uptime')
def uptime():
    system = platform.system()

    if system == "Windows":
        uptime_info = get_uptime_windows()
    else:
        uptime_info = get_uptime_linux()

    return f"Current uptime is {uptime_info}"


@app.route('/')
def home():
    return """
    <h1>Uptime Service</h1>
    <p>Server is running successfully!</p>
    <p>Visit: <a href="/uptime"><strong>/uptime</strong></a> to see system uptime</p>
    <p><em>Platform: {}</em></p>
    """.format(platform.system())


if __name__ == '__main__':
    print("=" * 50)
    print("Flask Server Started")
    print("Platform:", platform.system())
    print("URL: http://127.0.0.1:5000/uptime")
    print("=" * 50)
    app.run(debug=True)
