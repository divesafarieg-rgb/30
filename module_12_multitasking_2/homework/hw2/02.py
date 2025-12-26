import subprocess
import getpass
import platform
import os


def process_count(username: str) -> int:
    if platform.system() == "Windows":
        try:
            cmd = f'tasklist /FI "USERNAME eq {username}" /FO CSV /NH'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='cp866',
                errors='ignore'
            )

            count = 0
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and line.startswith('"') and ',' in line:
                    count += 1

            return count
        except:
            return 0
    else:
        cmd = f"ps -u {username} -o pid= | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return int(result.stdout.strip()) if result.stdout.strip() else 0


def total_memory_usage(root_pid: int) -> float:
    if platform.system() == "Windows":
        try:
            ps_script = f"""
            function Get-ProcessTree {{
                param([int]$pid)
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if (-not $process) {{ return 0 }}

                $totalMemory = $process.WorkingSet64

                # Получаем дочерние процессы
                $children = Get-WmiObject Win32_Process | Where-Object {{$_.ParentProcessId -eq $pid}}
                foreach ($child in $children) {{
                    $totalMemory += $child.WorkingSetSize
                }}

                # Конвертируем в проценты (примерно, от 8 ГБ RAM)
                $totalGB = $totalMemory / 1GB
                $percent = ($totalGB / 8) * 100  # Предполагаем 8 ГБ ОЗУ
                return [math]::Round($percent, 2)
            }}

            Get-ProcessTree -pid {root_pid}
            """

            cmd = ["powershell", "-Command", ps_script]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.stdout.strip():
                return float(result.stdout.strip())
        except:
            pass

        try:
            cmd = f'wmic process where ProcessId={root_pid} get WorkingSetSize /Value'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            for line in result.stdout.split('\n'):
                if 'WorkingSetSize=' in line:
                    mem_bytes = int(line.split('=')[1])
                    mem_gb = mem_bytes / (1024 ** 3)
                    mem_percent = (mem_gb / 8) * 100
                    return round(mem_percent, 2)
        except:
            pass

        return 0.0
    else:
        try:
            cmd = f"""
            # Функция для получения всех потомков
            get_children() {{
                local parent=$1
                ps -eo pid,ppid | awk -v p="$parent" '$2 == p {{print $1}}' | while read child; do
                    echo "$child"
                    get_children "$child"
                done
            }}

            # Собираем все PID: корневой + все потомки
            all_pids="{root_pid} $(get_children {root_pid})"

            # Получаем память для всех PID
            ps -o pmem= -p $all_pids 2>/dev/null | awk '{{sum += $1}} END {{printf "%.1f", sum+0}}'
            """

            result = subprocess.run(
                cmd,
                shell=True,
                executable='/bin/bash',
                capture_output=True,
                text=True
            )

            output = result.stdout.strip()
            return float(output) if output else 0.0
        except:
            cmd = f"ps --ppid {root_pid} -o pmem=; ps -p {root_pid} -o pmem="
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            total = 0.0
            for num in result.stdout.split():
                if num:
                    try:
                        total += float(num)
                    except:
                        continue
            return total


if __name__ == "__main__":

    user = getpass.getuser()
    current_pid = os.getpid()

    print(f"\nОперационная система: {platform.system()}")
    print(f"Текущий пользователь: {user}")
    print(f"PID текущего процесса: {current_pid}")

    print(f"\n1. process_count('{user}'):")
    count = process_count(user)
    print(f"Результат: {count} процессов")

    print(f"\n2. total_memory_usage({current_pid}):")
    usage = total_memory_usage(current_pid)
    print(f"Использование памяти: {usage}%")

    print(f"\n3. Тест на системных процессах Windows:")

    print(f"   • System Idle Process (PID 0): {total_memory_usage(0)}%")

    print(f"   • System Process (PID 4): {total_memory_usage(4)}%")

    print(f"\n4. Поиск процесса explorer.exe:")
    try:
        cmd = 'tasklist /FI "IMAGENAME eq explorer.exe" /FO CSV /NH'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if 'explorer.exe' in line:
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        explorer_pid = int(parts[1])
                        print(f"   • explorer.exe (PID {explorer_pid}): {total_memory_usage(explorer_pid)}%")
                        break
    except:
        pass

    print(f"\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")