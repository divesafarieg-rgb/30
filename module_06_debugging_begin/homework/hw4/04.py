import json
import re
from collections import Counter


def analyze_logs_improved(filename):
    level_count = Counter()
    hour_count = Counter()
    critical_5am = 0
    dog_messages = 0
    warning_word_count = Counter()

    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'its', 'their', 'this', 'that', 'these',
        'those', 'from', 'as', 'so', 'than', 'then', 'just', 'more', 'also',
        'very', 'too', 'such', 'only', 'not', 'no', 'yes', 'if', 'else', 'when',
        'where', 'how', 'why', 'what', 'which', 'who', 'whom', 'there', 'here'
    }

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            log = json.loads(line)
            level = log['level']
            time_str = log['time']
            message = log['message'].lower()

            level_count[level] += 1

            hour = int(time_str.split(':')[0])
            hour_count[hour] += 1

            if level == 'CRITICAL' and time_str.startswith('05:'):
                minute = int(time_str.split(':')[1])
                if minute <= 20:
                    critical_5am += 1

            if 'dog' in message:
                dog_messages += 1

            if level == 'WARNING':
                words = re.findall(r'\b[a-z]{4,}\b', message)
                filtered_words = [word for word in words if word not in stop_words and not word.isdigit()]
                warning_word_count.update(filtered_words)

    print("1. Сообщения по уровням:")
    for level, count in level_count.items():
        print(f"   {level}: {count}")

    max_hour, max_count = hour_count.most_common(1)[0]
    print(f"\n2. Час с наибольшим количеством логов: {max_hour}:00 ({max_count} логов)")

    print(f"\n3. CRITICAL логи с 05:00 до 05:20: {critical_5am}")

    print(f"\n4. Сообщения со словом 'dog': {dog_messages}")

    if warning_word_count:
        print(f"\n5. Анализ WARNING сообщений:")
        print(f"   Всего уникальных слов: {len(warning_word_count)}")

        top_words = warning_word_count.most_common(10)
        print(f"   Топ-10 самых частых слов:")
        for i, (word, count) in enumerate(top_words, 1):
            print(f"   {i:2d}. '{word}': {count} раз")
    else:
        print("\n5. Нет WARNING сообщений")


analyze_logs_improved('skillbox_json_messages.log')