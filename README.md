# 🎵 Audio Tag Stripper

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg?style=for-the-badge&logo=qt)
![Mutagen](https://img.shields.io/badge/Mutagen-1.47+-orange.svg?style=for-the-badge)

**Audio Tag Stripper** is a powerful desktop application built with **PyQt6** and **Mutagen** that removes cover art and normalizes metadata from **MP3**, **FLAC**, and **M4A** files — replacing titles with their filenames.

> 🎯 **Perfect for:** Musicians, DJs, archivists, and anyone who wants clean, consistent audio metadata without embedded covers.

---

## 📑 Table of Contents
- [🙌 Who is this for?](#-who-is-this-for)
- [💡 Why use Audio Tag Stripper?](#-why-use-audio-tag-stripper)
- [✨ Features](#-features)
- [📸 Screenshot](#-screenshot)
- [🚀 Getting Started](#-getting-started)
- [🧩 How It Works](#-how-it-works)
- [📊 Table Columns Explained](#-table-columns-explained)
- [🐛 Troubleshooting](#-troubleshooting)
- [🔧 Development](#-development)
- [🤝 Contributing](#-contributing)

---

## 🙌 Who is this for?

| Category | Description |
|----------|-------------|
| 🎧 **DJs & Musicians** | Clean up metadata and remove unwanted cover art from music libraries |
| 🗄️ **Archivists** | Standardize audio files for long-term storage |
| 💻 **Developers** | Prepare audio files for batch processing or testing |
| 📀 **Music collectors** | Remove bloat from embedded album art and fix mismatched titles |
| 🧹 **Minimalists** | Keep only filename-based titles and zero embedded images |

---

## 💡 Why use Audio Tag Stripper?

| Problem | Solution |
|---------|----------|
| ❌ Embedded cover art wastes storage space | ✅ **Removes all covers** from MP3, FLAC, M4A |
| ❌ Titles don’t match filenames | ✅ **Replaces title tag** with filename |
| ❌ Batch cleaning takes hours manually | ✅ **Batch processes** entire folders instantly |
| ❌ Inconsistent metadata across formats | ✅ **Works with MP3, FLAC, and M4A** |
| ❌ No visual feedback on tag status | ✅ **Table shows covers & status** before/after |

> 💡 **Pro Tip:** Use this tool before uploading music to cloud storage or embedding in documentation.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Batch Processing** | Load an entire folder — process all supported files at once |
| 🖼️ **Cover Removal** | Removes `APIC`, `PICT`, `covr`, and FLAC pictures |
| 🏷️ **Tag Normalization** | Sets `TIT2` (MP3), `title` (FLAC), or `©nam` (M4A) to the filename |
| 📊 **Visual Table** | Shows filename, current title, format, cover presence, and name match status |
| ✅ **Smart Detection** | Detects already-clean files and skips unnecessary writes |
| 📁 **Non-destructive** | Only tags are modified — audio data remains untouched |
| 🧹 **Clean UI** | Simple progress bar, clear buttons, and status icons |
| 🖼️ **Icon Feedback** | ✅ / ❌ icons for covers and name matching |

---

## 📸 Screenshot
<img width="902" height="485" alt="1" src="https://github.com/user-attachments/assets/a359b09f-fe69-418e-9b39-e4155626b963" />
<img width="917" height="744" alt="2" src="https://github.com/user-attachments/assets/21a2d0a0-5d03-45b2-8490-248c6223b902" />

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AudioTagStripper.git
cd AudioTagStripper
```

### 2️⃣ Install dependencies

```bash
pip install PyQt6 mutagen
```

### 3️⃣ Run the application

```bash
python AudioTagStripper.py
```

---

## 🧩 How It Works

| Step | Action |
|---------|-------------|
| 1️⃣ | Enter a folder path or use the UI to select one |
| 2️⃣ | Click **Load Files** — scans for `.mp3`, `.flac`, `.m4a` |
| 3️⃣ | Table shows current tags, covers, and name match status |
| 4️⃣ | Click **Start** — removes covers, updates title to filename |
| 5️⃣ | Progress bar updates in real time |
| 6️⃣ | Final summary shows how many files were cleaned |

---

## 📊 Table Columns Explained

| Column | Meaning |
|---------|-------------|
| **Name** | Actual filename (without extension) |
| **Title** | Current title tag from file metadata |
| **Format** | MP3, FLAC, or M4A |
| **Cover** | ✅ = cover exists / ❌ = no cover |
| **Status** | ✅ = filename matches title / ❌ = mismatch |

After processing:
- **Cover** always becomes ❌
- **Status** always becomes ✅

--- 

## 🐛 Troubleshooting

| Issue | Solution |
|---------|-------------|
| **No files found** | Make sure folder contains `.mp3`, `.flac`, or `.m4a` |
| **MP3 header error** | File may be corrupted or not a valid MP3 |
| **Tags not clearing**	| Check file permissions — some files are read-only |
| **UI file not loading** |	Ensure `./ui/AudioTagStripper.ui` exists |
| **Icons not showing**	| Place icons in `./assets/` (OK.png, Error.png, Warning.png) |

---

## 🔧 Development

Project Structure:

```python
AudioTagStripper.py
├── class AudioTagStripper(QMainWindow)
│   ├── __init__()              # Load UI, connect buttons
│   ├── customize_ui()          # Table settings, window size
│   ├── show_message()          # Custom message boxes
│   ├── load_files()            # Scan folder, populate table
│   └── start_process()         # Strip covers, fix titles
```

Supported formats & tag mappings:
| Format | Cover Tag | Title Tag |
|---------|----------|-----|
| MP3 |	APIC, PICT | TIT2 |
| FLAC | pictures | title |
| M4A | covr | ©nam |

---

## 🤝 Contributing

Pull requests and feature suggestions are always welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## ⭐ Support

If this tool helps you clean your music library, please give it a ⭐ on GitHub!
