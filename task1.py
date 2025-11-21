import argparse
import os
import socket
import tkinter as tk
from tkinter import scrolledtext, Entry, Frame
import shlex
import logging
from datetime import datetime
import time


class ShellEmulator:
    def __init__(self, root, vfs_path=None, log_file=None, startup_script=None):
        self.root = root
        self.current_directory = os.getcwd()
        self.command_history = []
        self.history_index = -1
        self.vfs_path = vfs_path
        self.log_file = log_file
        self.startup_script = startup_script

        # Получаем реальные данные ОС
        self.username = os.getenv('USER') or os.getenv('USERNAME') or 'user'
        self.hostname = socket.gethostname()

        # Настраиваем логирование
        self.setup_logging()

        self.setup_gui()

        # Отладочный вывод параметров
        self.debug_output()

        # Выполнение стартового скрипта если указан
        if self.startup_script:
            self.execute_startup_script()
        else:
            # Вывод приветственного сообщения
            self.print_output("Добро пожаловать в эмулятор командной оболочки!")
            self.print_output(f"Пользователь: {self.username}@{self.hostname}")
            self.print_output("Доступные команды: ls, cd, exit")
            self.print_output("")

    def setup_logging(self):
        """Настройка XML-логирования"""
        if self.log_file:
            try:
                # Создаем кастомный форматтер для XML
                class XMLFormatter(logging.Formatter):
                    def format(self, record):
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        return f'<event timestamp="{timestamp}" command="{record.msg}"/>'

                # Настраиваем логгер
                self.logger = logging.getLogger('shell_emulator')
                self.logger.setLevel(logging.INFO)
                self.logger.handlers = []

                # Файловый обработчик
                file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
                file_handler.setFormatter(XMLFormatter())
                self.logger.addHandler(file_handler)

                # Логируем начало работы
                self.logger.info("START_SESSION")
            except Exception as e:
                print(f"Ошибка настройки логирования: {e}")
                self.logger = None
        else:
            self.logger = None

    def log_command(self, command):
        """Логирование команды"""
        if self.logger:
            try:
                self.logger.info(command)
            except Exception as e:
                print(f"Ошибка логирования: {e}")

    def debug_output(self):
        """Отладочный вывод параметров конфигурации"""
        self.print_output("=== КОНФИГУРАЦИЯ ЭМУЛЯТОРА ===")
        self.print_output(f"VFS Path: {self.vfs_path or 'Не указан'}")
        self.print_output(f"Log File: {self.log_file or 'Не указан'}")
        self.print_output(f"Startup Script: {self.startup_script or 'Не указан'}")
        self.print_output("================================")
        self.print_output("")

    def execute_startup_script(self):
        """Выполнение стартового скрипта"""
        try:
            self.print_output(f"ВЫПОЛНЕНИЕ СТАРТОВОГО СКРИПТА: {self.startup_script}")
            self.print_output("")

            with open(self.startup_script, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                if not line:
                    continue

                if line.startswith('#'):
                    self.print_output(f"[Комментарий] {line}")
                    continue

                self.root.update()
                time.sleep(0.5)

                success = self.execute_script_command(line)
                if not success:
                    self.print_output("СКРИПТ ОСТАНОВЛЕН ИЗ-ЗА ОШИБКИ")
                    break

            self.print_output("ВЫПОЛНЕНИЕ СКРИПТА ЗАВЕРШЕНО")
            self.print_output("")

        except FileNotFoundError:
            self.print_output(f"ОШИБКА: Стартовый скрипт '{self.startup_script}' не найден")
        except Exception as e:
            self.print_output(f"ОШИБКА выполнения скрипта: {e}")

    def execute_script_command(self, command_input):
        """Выполнение команды из скрипта"""
        self.print_output(f"{self.username}@{self.hostname}:{self.get_short_path()}$ {command_input}")

        try:
            command, args = self.parse_command(command_input)
            self.log_command(command_input)

            if command == "exit":
                self.print_output("exit: команда проигнорирована в скрипте")
                return True

            elif command == "ls":
                self.print_output(f"Команда: ls")
                if args:
                    self.print_output(f"Аргументы: {args}")
                self.print_output("file1.txt  file2.txt  directory/")
                return True

            elif command == "cd":
                self.print_output(f"Команда: cd")
                if args:
                    self.print_output(f"Аргументы: {args}")
                    self.current_directory = args[0]
                    self.print_output(f"Текущая директория изменена на: {self.current_directory}")
                    self.update_prompt()
                    return True
                else:
                    self.print_output("Ошибка: cd требует аргумент - имя директории")
                    return False

            else:
                self.print_output(f"Ошибка: неизвестная команда '{command}'")
                return False

        except Exception as e:
            self.print_output(f"Ошибка: {str(e)}")
            return False

        finally:
            self.print_output("")

    def get_short_path(self):
        """Получить сокращенный путь для prompt"""
        home = os.path.expanduser('~')
        if self.current_directory.startswith(home):
            return '~' + self.current_directory[len(home):]
        return self.current_directory

    def setup_gui(self):
        """Настройка графического интерфейса"""
        # ЗАГОВОЛОК ОКНА - ИСПРАВЛЕННАЯ СТРОКА:
        self.root.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        self.root.geometry("800x600")

        # Основная область вывода
        self.output_area = scrolledtext.ScrolledText(
            self.root,
            height=20,
            width=80,
            bg='black',
            fg='white',
            font=('Courier New', 12)
        )
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.output_area.config(state=tk.DISABLED)

        # Фрейм для ввода команды
        input_frame = Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)

        # Метка приглашения к вводу
        self.prompt_label = tk.Label(
            input_frame,
            text=f"{self.username}@{self.hostname}:{self.get_short_path()}$ ",
            bg='black',
            fg='green',
            font=('Courier New', 12)
        )
        self.prompt_label.pack(side=tk.LEFT)

        # Поле ввода команды
        self.command_entry = Entry(
            input_frame,
            bg='black',
            fg='white',
            font=('Courier New', 12),
            insertbackground='white'
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind('<Return>', self.execute_command)
        self.command_entry.bind('<Up>', self.previous_command)
        self.command_entry.bind('<Down>', self.next_command)
        self.command_entry.focus()

    def print_output(self, text):
        """Вывод текста в область вывода"""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def update_prompt(self):
        """Обновление prompt"""
        self.prompt_label.config(text=f"{self.username}@{self.hostname}:{self.get_short_path()}$ ")

    def previous_command(self, event):
        """Навигация по истории команд"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        return "break"

    def next_command(self, event):
        """Навигация по истории команд"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = len(self.command_history)
            self.command_entry.delete(0, tk.END)
        return "break"

    def parse_command(self, command_input):
        """Парсер команд с поддержкой кавычек"""
        try:
            parts = shlex.split(command_input)
            if not parts:
                return "", []
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            return command, args
        except ValueError as e:
            raise ValueError("Ошибка синтаксиса: неправильное использование кавычек")

    def execute_command(self, event=None):
        """Обработка команд от пользователя"""
        command_input = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)

        if not command_input:
            return

        self.command_history.append(command_input)
        self.history_index = len(self.command_history)

        self.print_output(f"{self.username}@{self.hostname}:{self.get_short_path()}$ {command_input}")
        self.log_command(command_input)

        try:
            command, args = self.parse_command(command_input)

            if command == "exit":
                self.print_output("Выход из эмулятора...")
                self.root.quit()

            elif command == "ls":
                self.print_output(f"Команда: ls")
                self.print_output(f"Аргументы: {args}")
                self.print_output("file1.txt  file2.txt  directory/")

            elif command == "cd":
                self.print_output(f"Команда: cd")
                self.print_output(f"Аргументы: {args}")

                if len(args) > 1:
                    self.print_output("Ошибка: cd принимает только один аргумент")
                elif args:
                    self.current_directory = args[0]
                    self.print_output(f"Текущая директория изменена на: {self.current_directory}")
                    self.update_prompt()
                else:
                    self.print_output("Ошибка: cd требует аргумент - имя директории")

            else:
                self.print_output(f"Ошибка: неизвестная команда '{command}'")
                self.print_output("Доступные команды: ls, cd, exit")

        except Exception as e:
            self.print_output(f"Ошибка: {str(e)}")

        self.print_output("")
        self.update_prompt()


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Эмулятор командной оболочки')

    parser.add_argument('--vfs-path', type=str, default=None)
    parser.add_argument('--log-file', type=str, default=None)
    parser.add_argument('--startup-script', type=str, default=None)

    return parser.parse_args()


def main():
    args = parse_arguments()
    root = tk.Tk()
    app = ShellEmulator(
        root,
        vfs_path=args.vfs_path,
        log_file=args.log_file,
        startup_script=args.startup_script
    )
    root.mainloop()


if __name__ == "__main__":
    main()