from PyQt6.QtCore    import Qt, QThread, pyqtSignal
from PyQt6.QtGui     import QIcon, QPixmap
from PyQt6.uic       import loadUi
from PyQt6           import QtCore, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox

from mutagen.mp3     import MP3, HeaderNotFoundError
from mutagen.flac    import FLAC
from mutagen.mp4     import MP4
from mutagen.id3     import ID3, TIT2, error

import pathlib
import sys
import os

# === Worker: Load Files ===================================================================================== #

class LoadWorker(QThread):
    """Worker thread for loading audio files metadata without freezing the UI."""

    progress     = pyqtSignal(int)          # 0..100
    file_loaded  = pyqtSignal(list)         # [name, title, ext, has_cover, name_match]
    finished_ok  = pyqtSignal(int, str)     # count, dir_path
    no_files     = pyqtSignal(str)          # dir_path
    error        = pyqtSignal(str, str)     # title, message

    def __init__(self, dir_path):
        super().__init__()
        self.dir_path = dir_path
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        try:
            directory = os.listdir(self.dir_path)
        except Exception as e:
            self.error.emit('Read Error!', f'Could not read directory:\n{e}')
            return

        valid_exts = ('.mp3', '.flac', '.m4a')
        audio_files = [f for f in directory if pathlib.Path(f).suffix.lower() in valid_exts]
        total = len(audio_files)

        if total == 0:
            self.no_files.emit(self.dir_path)
            return

        count = 0
        for index, item in enumerate(audio_files):
            if self._stop:
                return

            file_path = os.path.join(self.dir_path, item)
            extension = pathlib.Path(item).suffix.lower()
            temp = None

            try:
                if extension == '.mp3':
                    audio = MP3(file_path, ID3=ID3)
                    has_cover = False
                    if audio.tags is not None:
                        has_cover = bool(audio.tags.getall('APIC')) or bool(audio.tags.getall('PICT'))
                    title = audio.get('TIT2', [''])[0]
                    name_match = (item[0:item.rfind('.')] == title)
                    temp = [item, title, extension[1:].upper(),
                            '✅' if has_cover else '❌',
                            '✅' if name_match else '❌']

                elif extension == '.flac':
                    audio = FLAC(file_path)
                    title = audio.get('title', [''])[0]
                    has_cover = bool(audio.pictures)
                    name_match = (item[0:item.rfind('.')] == title)
                    temp = [item, title, extension[1:].upper(),
                            '✅' if has_cover else '❌',
                            '✅' if name_match else '❌']

                elif extension == '.m4a':
                    audio = MP4(file_path)
                    title = audio.get('\xa9nam', [''])[0]
                    has_cover = bool(audio.get('covr'))
                    name_match = (item[0:item.rfind('.')] == title)
                    temp = [item, title, extension[1:].upper(),
                            '✅' if has_cover else '❌',
                            '✅' if name_match else '❌']

            except HeaderNotFoundError:
                print(f'[SKIPPED] Not a valid MP3: {item}')
                continue
            except Exception as e:
                print(f'[SKIPPED] {item}: {e}')
                continue

            if temp is not None:
                count += 1
                self.file_loaded.emit(temp)

            self.progress.emit(int((index + 1) / total * 100))

        self.finished_ok.emit(count, self.dir_path)

# === Worker: Process (Strip Tags) =========================================================================== #

class ProcessWorker(QThread):
    """Worker thread for stripping tags/covers without freezing the UI."""

    progress      = pyqtSignal(int)         # 0..100
    row_updated   = pyqtSignal(int, list)   # row index, item data
    finished_ok   = pyqtSignal(dict)        # stats
    error         = pyqtSignal(str, str)

    def __init__(self, music_list, dir_path):
        super().__init__()
        self.music_list = music_list
        self.dir_path = dir_path
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        total = len(self.music_list)
        if total == 0:
            self.error.emit('Error!', 'No files were processed! Please check the files and try again.')
            return

        percent_step = 100 / total
        processed_count = 0
        already_clean_count = 0

        for row, item in enumerate(self.music_list):
            if self._stop:
                return

            file_path = os.path.join(self.dir_path, item[0])
            extension = pathlib.Path(item[0]).suffix.lower()
            was_clean = (item[3] == '❌' and item[4] == '✅')

            try:
                if extension == '.mp3':
                    audio = MP3(file_path, ID3=ID3)
                    try:
                        audio.add_tags()
                    except error:
                        pass

                    if audio.tags is not None:
                        audio.tags.delall('APIC')
                        audio.tags.delall('PICT')

                    audio.delete()
                    new_title = item[0][0:item[0].rfind('.')]
                    audio['TIT2'] = TIT2(encoding=3, text=new_title)
                    audio.save()

                    item[1] = new_title
                    item[3] = '❌'
                    item[4] = '✅' if new_title == audio.get('TIT2', [''])[0] else '❌'
                    processed_count += 1

                elif extension == '.flac':
                    audio = FLAC(file_path)
                    audio.clear_pictures()
                    audio.delete()
                    new_title = item[0][0:item[0].rfind('.')]
                    audio['title'] = new_title
                    audio.save()

                    item[1] = new_title
                    item[3] = '❌'
                    item[4] = '✅' if new_title == audio.get('title', [''])[0] else '❌'
                    processed_count += 1

                elif extension == '.m4a':
                    audio = MP4(file_path)
                    if 'covr' in audio:
                        del audio['covr']
                    audio.delete()
                    new_title = item[0][0:item[0].rfind('.')]
                    audio['\xa9nam'] = new_title
                    audio.save()

                    item[1] = new_title
                    item[3] = '❌'
                    item[4] = '✅' if new_title == audio.get('\xa9nam', [''])[0] else '❌'
                    processed_count += 1

            except Exception as e:
                print(f'[ERROR] {item[0]}: {e}')
                # به هر حال ادامه بده

            if was_clean:
                already_clean_count += 1

            self.row_updated.emit(row, item)
            self.progress.emit(int((row + 1) * percent_step))

        self.finished_ok.emit({
            'total': total,
            'processed': processed_count,
            'already_clean': already_clean_count,
        })

# === Main Window ============================================================================================ #

class AudioTagStripper(QMainWindow):

    # === Variables ========================================================================================= #

    music_list = []
    percent = 0

    # === Initializes ======================================================================================= #

    def __init__(self):
        super(AudioTagStripper, self).__init__()
        loadUi('./ui/AudioTagStripper.ui', self)

        self.load_worker = None
        self.process_worker = None

        self.customize_ui()

        self.LOAD.clicked.connect(self.load_files)
        self.START.clicked.connect(self.start_process)

    # === Customize UI ====================================================================================== #

    def customize_ui(self):
        self.setFixedSize(892, 451)
        self.setWindowTitle('Audio Tag Stripper')
        self.setWindowIcon(QIcon('./assets/AudioTagStripper.png'))

        self.TABLE.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.TABLE.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.TABLE.verticalHeader().setVisible(False)

        self.TABLE.setColumnWidth(0, 312)
        self.TABLE.setColumnWidth(1, 312)
        self.TABLE.setColumnWidth(2, 82)
        self.TABLE.setColumnWidth(3, 82)
        self.TABLE.setColumnWidth(4, 82)

    # === QMessageBox ======================================================================================= #

    def show_message(self, title, text, icon):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIconPixmap(QPixmap(icon).scaled(64, 64))
        msg.setWindowIcon(QIcon('./assets/AudioTagStripper.png'))
        msg.exec()
        return msg

    # === Helpers =========================================================================================== #

    def _set_controls_enabled(self, enabled: bool):
        """Enable/disable buttons while a worker is running."""
        self.LOAD.setEnabled(enabled)
        self.START.setEnabled(enabled)
        self.DIR_PATH.setEnabled(enabled)

    # === Load Files ======================================================================================== #

    def load_files(self):
        dir_path = self.DIR_PATH.text().strip()

        if not dir_path:
            self.show_message(
                'Path is empty!',
                'Please enter a valid directory path.',
                './assets/Error.png'
            )
            return

        if not os.path.exists(dir_path):
            self.show_message(
                'Directory does not exist!',
                f'Directory "{dir_path}" was not found.',
                './assets/Error.png'
            )
            return

        # Reset UI
        self.PROGRESS.setValue(0)
        self.percent = 0
        self.music_list.clear()
        self.TABLE.setRowCount(0)
        self._set_controls_enabled(False)

        # Start worker
        self.load_worker = LoadWorker(dir_path)
        self.load_worker.progress.connect(self.PROGRESS.setValue)
        self.load_worker.file_loaded.connect(self.on_file_loaded)
        self.load_worker.finished_ok.connect(self.on_load_finished)
        self.load_worker.no_files.connect(self.on_no_files)
        self.load_worker.error.connect(self.on_worker_error)
        self.load_worker.start()

    def on_file_loaded(self, item):
        """Called for each file found. Adds a row to the table."""
        self.music_list.append(item)
        row = self.TABLE.rowCount()
        self.TABLE.insertRow(row)

        for col in range(5):
            table_item = QtWidgets.QTableWidgetItem(item[col])
            table_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.TABLE.setItem(row, col, table_item)

    def on_load_finished(self, count, dir_path):
        self._set_controls_enabled(True)
        self.PROGRESS.setValue(0)
        self.show_message(
            'Found audio file(s)!',
            f'Successfully loaded {count} file(s) from:\n"{dir_path}"',
            './assets/OK.png'
        )

    def on_no_files(self, dir_path):
        self._set_controls_enabled(True)
        self.PROGRESS.setValue(0)
        self.show_message(
            'No audio files found!',
            f'The directory "{dir_path}" does not contain any MP3, FLAC, or M4A files.',
            './assets/Error.png'
        )

    def on_worker_error(self, title, message):
        self._set_controls_enabled(True)
        self.PROGRESS.setValue(0)
        self.show_message(title, message, './assets/Error.png')

    # === Start Process ===================================================================================== #

    def start_process(self):
        if len(self.music_list) == 0:
            self.show_message(
                'The table is empty!',
                'Please enter the path and press the Load Files button to check.',
                './assets/Error.png'
            )
            return

        self.PROGRESS.setValue(0)
        self.percent = 0
        self._set_controls_enabled(False)

        self.process_worker = ProcessWorker(self.music_list, self.DIR_PATH.text().strip())
        self.process_worker.progress.connect(self.PROGRESS.setValue)
        self.process_worker.row_updated.connect(self.on_row_updated)
        self.process_worker.finished_ok.connect(self.on_process_finished)
        self.process_worker.error.connect(self.on_worker_error)
        self.process_worker.start()

    def on_row_updated(self, row, item):
        for col in range(5):
            table_item = QtWidgets.QTableWidgetItem(item[col])
            table_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.TABLE.setItem(row, col, table_item)

    def on_process_finished(self, stats):
        self._set_controls_enabled(True)
        self.PROGRESS.setValue(100)

        total = stats['total']
        processed_count = stats['processed']
        already_clean_count = stats['already_clean']

        all_ok = all(item[3] == '❌' and item[4] == '✅' for item in self.music_list)

        if all_ok and processed_count > 0:
            if already_clean_count == total:
                self.show_message(
                    'Already Clean!',
                    f'All {total} audio file(s) were already clean.\n\n'
                    f'✓ No covers found\n'
                    f'✓ All tags match filenames\n\n'
                    f'No changes were needed.',
                    './assets/OK.png'
                )
            else:
                self.show_message(
                    'Process Completed Successfully!',
                    f'✅ Successfully processed {processed_count} audio file(s)!\n\n'
                    f'📊 Summary:\n'
                    f'• Total files: {total}\n'
                    f'• Successfully stripped: {processed_count - already_clean_count}\n'
                    f'• Already clean: {already_clean_count}\n\n'
                    f'✨ All covers removed and tags updated!',
                    './assets/OK.png'
                )
        elif processed_count > 0:
            problem_count = sum(1 for item in self.music_list if item[4] == '❌')
            cover_count = sum(1 for item in self.music_list if item[3] == '✅')

            self.show_message(
                'Process Completed with Warnings!',
                f'⚠️ Process completed with some issues!\n\n'
                f'📊 Summary:\n'
                f'• Total files: {total}\n'
                f'• Successfully stripped: {processed_count - already_clean_count}\n'
                f'• Already clean: {already_clean_count}\n'
                f'• Files with cover issues: {cover_count}\n'
                f'• Files with name mismatch: {problem_count}\n\n'
                f'💡 Please check the table for details.',
                './assets/Warning.png'
            )
        else:
            self.show_message(
                'Error!',
                'No files were processed! Please check the files and try again.',
                './assets/Error.png'
            )

    # === Close Event ======================================================================================= #

    def closeEvent(self, event):
        """Make sure workers stop cleanly when the window closes."""
        if self.load_worker is not None and self.load_worker.isRunning():
            self.load_worker.stop()
            self.load_worker.wait(2000)
        if self.process_worker is not None and self.process_worker.isRunning():
            self.process_worker.stop()
            self.process_worker.wait(2000)
        event.accept()


# === Main =================================================================================================== #

app = QApplication(sys.argv)
mainwindow = AudioTagStripper()
mainwindow.show()

try:
    sys.exit(app.exec())
except Exception:
    print('Exiting')

# === End ================================================================================================= #
