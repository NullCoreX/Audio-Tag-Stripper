from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QIcon, QPixmap
from PyQt6.uic       import loadUi
from PyQt6           import QtCore, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox

from mutagen.mp3     import MP3, HeaderNotFoundError
from mutagen.flac    import FLAC
from mutagen.mp4     import MP4
from mutagen.id3     import ID3, TIT2, APIC, error

import pathlib
import sys
import os

class AudioTagStripper(QMainWindow):
    
    # === Variables ======================================================================================= #
    
    music_list = []
    percent = 0

    # === Initializes ===================================================================================== #

    def __init__(self):
        super(AudioTagStripper, self).__init__()
        loadUi('./ui/AudioTagStripper.ui', self)
        
        self.customize_ui()

        self.LOAD.clicked.connect(self.load_files)
        self.START.clicked.connect(self.start_process)

    # === Customiza UI ===================================================================================== #

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

    # === QMessageBox ===================================================================================== #

    def show_message(self, title, text, icon):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIconPixmap(QPixmap(icon).scaled(64, 64))
        msg.setWindowIcon(QIcon('./assets/AudioTagStripper.png'))
        msg.exec()
        return msg

    # === Load Files ====================================================================================== #

    def load_files(self):
        QApplication.processEvents()
        self.PROGRESS.setValue(0)
        self.percent = 0

        dir_path = self.DIR_PATH.text().strip()
        
        if not dir_path:
            self.show_message (
                'Path is empty!',
                'Please enter a valid directory path.',
                './assets/Error.png'
            )
            return 

        if not os.path.exists(dir_path):
            self.show_message (
                'Directory does not exist!',
                f'Directory "{dir_path}" was not found.', 
                './assets/Error.png'
            )
            return
        
        QApplication.processEvents()
        self.music_list.clear()
        directory = os.listdir(self.DIR_PATH.text())

        for item in directory:
            QApplication.processEvents()
            temp = []
            file_path = os.path.join(self.DIR_PATH.text(), item)
            extension = pathlib.Path(item).suffix.lower()

            if extension == '.mp3':
                try:
                    audio = MP3(file_path, ID3=ID3)
                    temp.append(item)
                    temp.append(audio.get('TIT2', [''])[0])
                    temp.append(extension[1:].upper())
                    temp.append('✅' if bool(audio.tags.getall('APIC')) or bool(audio.tags.getall('PICT')) else '❌')
                    temp.append('✅' if item[0:item.rfind('.')] == audio.get('TIT2', [''])[0] else '❌')
                    self.music_list.append(temp)
                except HeaderNotFoundError:
                    print(f'[SKIPPED] Not a valid MP3: {item}')
                    continue

            elif extension == '.flac':
                audio = FLAC(file_path)
                temp.append(item)
                temp.append(audio.get('title', [''])[0])
                temp.append(extension[1:].upper())
                temp.append('✅' if bool(audio.pictures) else '❌')
                temp.append('✅' if item[0:item.rfind('.')] == audio.get('title', [''])[0] else '❌')
                self.music_list.append(temp)

            elif extension == '.m4a':
                audio = MP4(file_path)
                temp.append(item)
                temp.append(audio.get('\xa9nam', [''])[0])
                temp.append(extension[1:].upper())
                temp.append('✅' if bool(audio.get('covr')) else '❌')
                temp.append('✅' if item[0:item.rfind('.')] == audio.get('\xa9nam', [''])[0] else '❌')
                self.music_list.append(temp)

        if len(self.music_list) == 0:
            self.show_message (
                'No audio files found!',
                f'The directory "{dir_path}" does not contain any MP3, FLAC, or M4A files.',
                './assets/Error.png'
            )
            return 

        self.TABLE.setRowCount(len(self.music_list))

        for row, item in enumerate(self.music_list):
            QApplication.processEvents()
            for col in range(5):
                table_item = QtWidgets.QTableWidgetItem(item[col])
                table_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.TABLE.setItem(row, col, table_item)

        if len(self.music_list) != 0:
            self.show_message (
                f'Found audio file(s)!',
                f'Successfully loaded {len(self.music_list)} file(s) from:"{dir_path}"',
                './assets/OK.png'
            )

    # === Start Process ===================================================================================================== #

    def start_process(self):
        QApplication.processEvents()
        
        if len(self.music_list) == 0:
            self.show_message (
                'The table is empty!',
                'Please enter the path and press the Load Files button to check.',
                './assets/Error.png'
            )
            return

        if self.PROGRESS.value() == 0:
            self.PROGRESS.setValue(0)
            self.percent = 0

        percent_ = 100 // len(self.music_list) + 1

        row = 0
        processed_count = 0
        already_clean_count = 0
        
        for item in self.music_list:
            QApplication.processEvents()
            file_path = os.path.join(self.DIR_PATH.text(), item[0])
            extension = pathlib.Path(item[0]).suffix.lower()
            
            was_clean = (item[3] == '❌' and item[4] == '✅')
            
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
                audio['TIT2'] = TIT2(encoding=3, text=item[0][0:item[0].rfind('.')])
                audio.save()

                item[1] = item[0][0:item[0].rfind('.')]
                item[3] = '❌'
                item[4] = '✅' if item[0][0:item[0].rfind('.')] == audio.get('TIT2', [''])[0] else '❌'
                processed_count += 1

            elif extension == '.flac':
                audio = FLAC(file_path)
                audio.clear_pictures()
                audio.delete()
                audio['title'] = item[0][0:item[0].rfind('.')]
                audio.save()

                item[1] = item[0][0:item[0].rfind('.')]
                item[3] = '❌'
                item[4] = '✅' if item[0][0:item[0].rfind('.')] == audio.get('title', [''])[0] else '❌'
                processed_count += 1

            elif extension == '.m4a':
                audio = MP4(file_path)
                
                if 'covr' in audio:
                    del audio['covr']
                
                audio.delete()
                audio['\xa9nam'] = item[0][0:item[0].rfind('.')]
                audio.save()

                item[1] = item[0][0:item[0].rfind('.')]
                item[3] = '❌'
                item[4] = '✅' if item[0][0:item[0].rfind('.')] == audio.get('\xa9nam', [''])[0] else '❌'
                processed_count += 1
            
            if was_clean:
                already_clean_count += 1
            
            for col in range(0, len(item)):
                table_item = QtWidgets.QTableWidgetItem(item[col])
                table_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.TABLE.setItem(row, col, table_item)

            row += 1
            self.percent += percent_ 

            if self.percent <= 100:
                self.PROGRESS.setValue(self.percent)
            else:
                self.PROGRESS.setValue(100)

        self.PROGRESS.setValue(100)

        # === Display the Final Message =================================================================== #
        
        all_ok = all(item[3] == '❌' and item[4] == '✅' for item in self.music_list)
        
        if all_ok and processed_count > 0:
            if already_clean_count == len(self.music_list):
                self.show_message(
                    'Already Clean!',
                    f'All {len(self.music_list)} audio file(s) were already clean.\n\n'
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
                    f'• Total files: {len(self.music_list)}\n'
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
                f'• Total files: {len(self.music_list)}\n'
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

# === Main ================================================================================================ #

app = QApplication(sys.argv)
mainwindow = AudioTagStripper()
mainwindow.show()

try: 
    sys.exit(app.exec())
except:
    print('Exiting')

# === End ================================================================================================= #
