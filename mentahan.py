# Python3
# GITHUB: https://github.com/denoyey/Mentahan-Python
# LICENSE: MIT License

import os
import random
import subprocess
import platform
import itertools
import logging
from datetime import datetime
from rich.console import Console
from rich.text import Text


class CommandRunner:
    """
    Kelas untuk menjalankan perintah terminal sederhana, khususnya membersihkan layar konsol.

    Cara pakai:
    1. Buat instance CommandRunner:
        cmd = CommandRunner()
    2. Panggil method clear_screen() untuk membersihkan layar terminal sesuai OS:
        cmd.clear_screen()

    Contoh:
        cmd = CommandRunner()
        cmd.clear_screen()
    """

    def __init__(self):
        self.is_windows = platform.system() == "Windows"

    def clear_screen(self):
        subprocess.run("cls" if self.is_windows else "clear", shell=True)


class LogoPrinter:
    """
    Kelas untuk menampilkan logo ASCII berwarna di terminal dengan library rich.

    Cara pakai:
    1. Import dan buat objek Console dari rich:
        from rich.console import Console
        console = Console()
    2. Buat instance LogoPrinter dengan parameter console:
        logo_printer = LogoPrinter(console)
    3. Panggil print_logo() untuk menampilkan logo berwarna:
        logo_printer.print_logo()

    Contoh lengkap:
        from rich.console import Console

        console = Console()
        logo_printer = LogoPrinter(console)
        logo_printer.print_logo()
    """

    def __init__(self, console: Console):
        self.console = console
        self.colors = [
            "bold bright_cyan",
            "bold bright_green",
            "bold bright_blue",
            "bold bright_magenta",
            "bold bright_yellow",
        ]
        random.shuffle(self.colors)

    def print_logo(self):
        logo = r"""
 /$$$$$$$                                                             
| $$__  $$                                                            
| $$  \ $$  /$$$$$$  /$$$$$$$   /$$$$$$  /$$   /$$  /$$$$$$  /$$   /$$
| $$  | $$ /$$__  $$| $$__  $$ /$$__  $$| $$  | $$ /$$__  $$| $$  | $$
| $$  | $$| $$$$$$$$| $$  \ $$| $$  \ $$| $$  | $$| $$$$$$$$| $$  | $$
| $$  | $$| $$_____/| $$  | $$| $$  | $$| $$  | $$| $$_____/| $$  | $$
| $$$$$$$/|  $$$$$$$| $$  | $$|  $$$$$$/|  $$$$$$$|  $$$$$$$|  $$$$$$$
|_______/  \_______/|__/  |__/ \______/  \____  $$ \_______/ \____  $$
                                         /$$  | $$           /$$  | $$
                                        |  $$$$$$/          |  $$$$$$/
                                         \______/            \______/ 

              Github: github.com/denoyey/Mentahan-Python
        """
        lines = logo.strip("\n").split("\n")
        color_cycle = itertools.cycle(self.colors)
        for line in lines:
            style = next(color_cycle)
            self.console.print(Text(line, style=style))


class LoggerManager:
    """
    Kelas untuk mengelola pencatatan (logging) ke file dengan fitur:
    - Menambahkan baris kosong setiap tanggal berganti di log file.
    - Membersihkan file log jika ukurannya melebihi batas maksimum (default 500KB).

    Cara pakai:
    1. Buat instance LoggerManager, misalnya:
        logger_manager = LoggerManager(
            logger_name="my_logger",
            log_file_name="app.log",
            log_dir="log",
            level=logging.INFO
        )
    2. Dapatkan logger untuk mencatat pesan:
        logger = logger_manager.logger
    3. Gunakan logger sesuai standar logging Python:
        logger.info("Pesan informasi")
        logger.error("Pesan error")
    4. Setelah selesai (biasanya di akhir program), panggil:
        logger_manager.cleanup()
       untuk membersihkan log jika sudah terlalu besar.

    Contoh lengkap:
        logger_manager = LoggerManager(
            logger_name="my_logger",
            log_file_name="app.log",
            log_dir="log",
            level=logging.INFO
        )
        logger = logger_manager.logger
        logger.info("Program dimulai")
        # kode program ...
        logger_manager.cleanup()
    """

    class DayChangeHandler(logging.FileHandler):
        def __init__(self, filename, encoding=None):
            super().__init__(filename, encoding=encoding)
            self.last_date = self._get_last_log_date(filename)

        def _get_last_log_date(self, filename):
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, encoding="utf-8") as f:
                    for line in reversed(f.readlines()):
                        try:
                            date_str = line.split(" - ")[0]
                            return datetime.strptime(
                                date_str, "%Y-%m-%d %H:%M:%S"
                            ).date()
                        except Exception:
                            continue
            return None

        def emit(self, record):
            current_date = datetime.fromtimestamp(record.created).date()
            if self.last_date and self.last_date != current_date and self.stream:
                self.stream.write("\n\n")
            self.last_date = current_date
            super().emit(record)

    def __init__(
        self,
        logger_name="default_logger",
        log_file_name="logfile.log",
        log_dir="log",
        level=logging.INFO,
        max_kb=500,
        formatter="%(asctime)s - %(levelname)s - %(message)s",
    ):
        self.logger_name = logger_name
        self.log_dir = log_dir
        self.log_file = os.path.join(self.log_dir, log_file_name)
        self.level = level
        self.max_kb = max_kb
        self.formatter = formatter

        self._ensure_log_dir()
        self.logger = self._setup_logger()

    def _ensure_log_dir(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _setup_logger(self):
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.level)

        if not logger.handlers:
            handler = self.DayChangeHandler(self.log_file, encoding="utf-8")
            handler.setFormatter(logging.Formatter(self.formatter, "%Y-%m-%d %H:%M:%S"))
            logger.addHandler(handler)

        return logger

    def cleanup(self):
        """
        Bersihkan file log jika ukurannya melebihi max_kb.

        Biasanya dipanggil di akhir program agar log file tidak membengkak.
        """
        if (
            os.path.exists(self.log_file)
            and os.path.getsize(self.log_file) > self.max_kb * 1024
        ):
            for h in logging.root.handlers[:]:
                logging.root.removeHandler(h)
                h.close()
            open(self.log_file, "w", encoding="utf-8").close()


class SystemSetup:
    """
    Kelas utama yang menggabungkan fungsi CommandRunner, LogoPrinter, dan LoggerManager
    untuk memberikan contoh bagaimana menggunakan ketiga kelas tersebut secara bersamaan.

    Cara pakai:
    1. Buat instance SystemSetup:
        system = SystemSetup()
    2. Jalankan method run() untuk membersihkan layar, menampilkan logo, dan mengelola logging:
        system.run()

    Program ini otomatis menangani error dan interrupt user, serta membersihkan log jika terlalu besar.

    Contoh lengkap:
        if __name__ == "__main__":
            system = SystemSetup()
            system.run()
    """

    def __init__(self):
        self.console = Console()
        self.cmd = CommandRunner()
        self.logo = LogoPrinter(self.console)

        # Inisialisasi LoggerManager dan dapatkan logger-nya
        self.logger_manager = LoggerManager(
            logger_name="mentahan_logger",
            log_file_name="mentahan.log",
            log_dir="log",
            level=logging.INFO,
        )
        self.logger = self.logger_manager.logger

    def run(self):
        try:
            self.cmd.clear_screen()
            self.logo.print_logo()
            self.logger.info("SystemSetup started successfully.")
        except KeyboardInterrupt:
            self.logger.warning("Process interrupted by user.")
            self.console.print("[bold red]Process interrupted by user.[/bold red]")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.console.print(f"[bold red]Error: {e}[/bold red]")
        finally:
            self.logger_manager.cleanup()


if __name__ == "__main__":
    SystemSetup().run()
