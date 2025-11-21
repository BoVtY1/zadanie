import os
import socket
import tkinter as tk
from tkinter import scrolledtext, Entry, Frame
import shlex


class ShellEmulator:
    def __init__(self, root):
        self.root = root
        self.current_directory = os.getcwd()
        self.command_history = []
        self.history_index = -1

        # Получаем реальные данные ОС
        self.username = os.getenv('USER') or os.getenv('USERNAME') or 'user'
        self.hostname = socket.gethostname()

        self.setup_gui()

        # Вывод приветственного сообщения
        self.print_output("Добро пожаловать в эмулятор командной оболочки!")
        self.print_output(f"Пользователь: {self.username}@{self.hostname}")
        self.print_output("Доступные команды: ls, cd, exit")
        self.print_output("")

    def get_short_path(self):
        """Получить сокращенный путь для prompt"""
        home = os.path.expanduser('~')
        if self.current_directory.startswith(home):
            return '~' + self.current_directory[len(home):]
        return self.current_directory

    # Настройка графического интерфейса
    def setup_gui(self):
        # Заголовок окна на основе реальных данных ОС - ТРЕБОВАНИЕ 2
        self.root.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        self.root.geometry("800x600")

        # Основная область вывода - ТРЕБОВАНИЕ 1 (GUI)
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

    # Вывод текста в область вывода
    def print_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    # Навигация по истории команд
    def previous_command(self, event):
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        return "break"

    def next_command(self, event):
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = len(self.command_history)
            self.command_entry.delete(0, tk.END)
        return "break"

    # Парсер команд с поддержкой кавычек - ТРЕБОВАНИЕ 3
    def parse_command(self, command_input):
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
        command_input = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)

        if not command_input:
            return

        # Добавляем команду в историю
        self.command_history.append(command_input)
        self.history_index = len(self.command_history)

        # Выводим введенную команду
        self.print_output(f"{self.username}@{self.hostname}:{self.get_short_path()}$ {command_input}")

        try:
            # Парсим команду - ТРЕБОВАНИЕ 3
            command, args = self.parse_command(command_input)

            # Обрабатываем команды
            if command == "exit":
                # ТРЕБОВАНИЕ 6
                self.print_output("Выход из эмулятора...")
                self.root.quit()

            elif command == "ls":
                # ТРЕБОВАНИЕ 5 - команда-заглушка
                self.print_output(f"Команда: ls")
                self.print_output(f"Аргументы: {args}")
                self.print_output("file1.txt  file2.txt  directory/")

            elif command == "cd":
                # ТРЕБОВАНИЕ 5 - команда-заглушка
                self.print_output(f"Команда: cd")
                self.print_output(f"Аргументы: {args}")

                if len(args) > 1:
                    # ТРЕБОВАНИЕ 4 - обработка ошибок
                    self.print_output("Ошибка: cd принимает только один аргумент")
                elif args:
                    self.current_directory = args[0]
                    self.print_output(f"Текущая директория изменена на: {self.current_directory}")
                else:
                    self.print_output("Ошибка: cd требует аргумент - имя директории")

            else:
                # ТРЕБОВАНИЕ 4 - неизвестная команда
                self.print_output(f"Ошибка: неизвестная команда '{command}'")
                self.print_output("Доступные команды: ls, cd, exit")

        except Exception as e:
            # ТРЕБОВАНИЕ 4 - обработка ошибок парсера
            self.print_output(f"Ошибка: {str(e)}")

        self.print_output("")
        # Обновляем prompt после выполнения команды
        self.prompt_label.config(text=f"{self.username}@{self.hostname}:{self.get_short_path()}$ ")


def main():
    root = tk.Tk()
    app = ShellEmulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()