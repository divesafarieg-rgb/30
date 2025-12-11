<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>До Нового Года!</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            text-align: center;
            background: linear-gradient(180deg, #000b1a 0%, #001f3f 50%, #003366 100%);
            color: white;
            min-height: 100vh;
            overflow: hidden;
            position: relative;
        }

        .content {
            position: relative;
            z-index: 2;
            padding-top: 100px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        h1 {
            font-size: 3rem;
            margin-bottom: 30px;
            color: #4df;
            text-shadow: 0 0 10px #0ff, 0 0 20px #0ff;
            background: linear-gradient(90deg, #0ff, #f0f);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        #countdown {
            font-size: 5rem;
            font-weight: bold;
            margin: 40px 0;
            padding: 20px;
            display: inline-block;
            background: rgba(0, 20, 40, 0.7);
            border-radius: 20px;
            border: 2px solid rgba(0, 255, 255, 0.3);
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
            min-width: 300px;
        }

        .days {
            color: #ff6b9d;
            text-shadow: 0 0 10px #ff0066;
        }

        .time {
            font-size: 2.5rem;
            color: #6bf;
            text-shadow: 0 0 10px #0066ff;
        }

        .message {
            font-size: 1.5rem;
            margin-top: 30px;
            opacity: 0.9;
            color: #bdf;
        }

        .note {
            position: absolute;
            bottom: 20px;
            width: 100%;
            font-size: 0.9rem;
            opacity: 0.6;
        }

        /* Для снежинок */
        .snowflake {
            position: fixed !important;
            pointer-events: none !important;
            user-select: none !important;
            z-index: 1 !important;
        }
    </style>
</head>
<body>
    <div class="content">
        <h1>❄ До Нового Года осталось: ❄</h1>

        <div id="countdown">
            <span class="days" id="days">...</span>
            <br>
            <span class="time" id="time">00:00:00</span>
        </div>


    </div>

    <script>
        function updateCountdown() {
            const now = new Date();
            const currentYear = now.getFullYear();
            const nextYear = currentYear + 1;
            const newYearDate = new Date(nextYear, 0, 1, 0, 0, 0);

            const diff = newYearDate - now;

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            document.getElementById('days').textContent = days + ' дней';
            document.getElementById('time').textContent =
                hours.toString().padStart(2, '0') + ':' +
                minutes.toString().padStart(2, '0') + ':' +
                seconds.toString().padStart(2, '0');

            setTimeout(updateCountdown, 1000);
        }

        document.addEventListener('DOMContentLoaded', function() {
            updateCountdown();
            console.log('Сайт загружен. Ожидаем снежинки...');
        });
    </script>

    <script src="js/snowstorm.js"></script>
</body>
</html>
