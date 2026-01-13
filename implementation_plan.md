
# i-Downloader - Implementation Plan

## 📋 Project Overview

**เป้าหมาย:** สร้าง Download Manager Application ด้วย Python + PyQt6 ที่มีความสามารถใกล้เคียง Internet Download Manager (IDM)

**เทคโนโลยีหลัก:**
- **Python 3.11+** - ภาษาหลัก
- **PyQt6** - GUI Framework
- **aiohttp** - Async HTTP client สำหรับ multi-threaded download
- **SQLite** - เก็บประวัติการดาวน์โหลด

---

## 🎯 Core Features

### 1. Multi-threaded Download Engine
- แบ่งไฟล์เป็น 8 segments (ปรับได้)
- ดาวน์โหลดแต่ละ segment พร้อมกัน
- รวมไฟล์อัตโนมัติเมื่อเสร็จ

### 2. Pause/Resume Support
- บันทึก progress ของแต่ละ segment
- Resume จากจุดที่ค้างได้แม้ปิดโปรแกรม
- รองรับ HTTP Range requests

### 3. Download Queue Management
- จัดคิวการดาวน์โหลด
- กำหนดจำนวน concurrent downloads (default: 3)
- ลำดับความสำคัญ (priority)

### 4. Progress Tracking
- แสดง % completion แบบ real-time
- แสดงความเร็ว (MB/s)
- แสดงเวลาที่เหลือโดยประมาณ (ETA)

### 5. Modern UI
- Dark theme สวยงาม
- System tray integration
- Drag & drop URL support

---

## 📁 Project Structure

```
c:\Users\Pondjs\Dev\i-downloader\
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/                   # Download engine
│   │   ├── __init__.py
│   │   ├── downloader.py       # Main download manager
│   │   ├── segment.py          # Segment download handler
│   │   ├── queue_manager.py    # Download queue
│   │   └── file_utils.py       # File operations
│   │
│   ├── ui/                     # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window
│   │   ├── download_dialog.py  # New download dialog
│   │   ├── download_item.py    # Download list item widget
│   │   ├── settings_dialog.py  # Settings panel
│   │   └── styles.py           # QSS styling
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── download.py         # Download model
│   │   └── database.py         # SQLite operations
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── constants.py        # App constants
│       └── helpers.py          # Helper functions
│
├── resources/                  # Assets
│   ├── icons/
│   └── themes/
│
└── tests/                      # Unit tests
    ├── __init__.py
    ├── test_downloader.py
    └── test_segment.py
```

---

## 🔧 Proposed Changes

### [NEW] Core Files

#### [NEW] [main.py](file:///c:/Users/Pondjs/Dev/i-downloader/main.py)
- Application entry point
- Initialize PyQt6 application
- Load main window

#### [NEW] [requirements.txt](file:///c:/Users/Pondjs/Dev/i-downloader/requirements.txt)
```
PyQt6>=6.6.0
aiohttp>=3.9.0
aiofiles>=23.2.0
```

---

### [NEW] Core Download Engine

#### [NEW] [src/core/downloader.py](file:///c:/Users/Pondjs/Dev/i-downloader/src/core/downloader.py)
- `DownloadManager` class - จัดการ downloads ทั้งหมด
- `DownloadTask` class - แทน download แต่ละอัน
- Methods: `add_download()`, `pause()`, `resume()`, `cancel()`
- Multi-segment download logic

#### [NEW] [src/core/segment.py](file:///c:/Users/Pondjs/Dev/i-downloader/src/core/segment.py)
- `SegmentDownloader` class - ดาวน์โหลด segment เดียว
- HTTP Range header support
- Progress callback

#### [NEW] [src/core/queue_manager.py](file:///c:/Users/Pondjs/Dev/i-downloader/src/core/queue_manager.py)
- `QueueManager` class - จัดคิว downloads
- Concurrent download limit
- Priority handling

---

### [NEW] User Interface

#### [NEW] [src/ui/main_window.py](file:///c:/Users/Pondjs/Dev/i-downloader/src/ui/main_window.py)
- Main application window
- Download list view (QTableView)
- Toolbar with actions (Add, Pause, Resume, Delete)
- Status bar with overall progress

#### [NEW] [src/ui/download_dialog.py](file:///c:/Users/Pondjs/Dev/i-downloader/src/ui/download_dialog.py)
- Dialog for adding new download
- URL input, save location picker
- Advanced options (segments, authentication)

#### [NEW] [src/ui/download_item.py](file:///c:/Users/Pondjs/Dev/i-downloader/src/ui/download_item.py)
- Custom widget for download list item
- Progress bar, speed, ETA display
- Action buttons (pause/resume/cancel)

#### [NEW] [src/ui/styles.py](file:///c:/Users/Pondjs/Dev/i-downloader/src/ui/styles.py)
- Dark theme QSS stylesheet
- Modern color palette
- Custom widget styling

---

### [NEW] Data Models

#### [NEW] [src/models/download.py](file:///c:/Users/Pondjs/Dev/i-downloader/src/models/download.py)
- `Download` dataclass - เก็บข้อมูล download
- Fields: url, filename, size, progress, status, segments

#### [NEW] [src/models/database.py](file:///c:/Users/Pondjs/Dev/i-downloader/src/models/database.py)
- SQLite database handler
- Save/load download history
- Resume data persistence

---

## 🖥️ UI Design Preview

```
┌─────────────────────────────────────────────────────────────────┐
│  i-Downloader                                        [─] [□] [×]│
├─────────────────────────────────────────────────────────────────┤
│  [+ Add] [▶ Resume All] [⏸ Pause All] [🗑 Clear]    [⚙ Settings]│
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  📄 ubuntu-22.04.iso                                        │ │
│ │  ████████████████████░░░░░░░░░░  72% │ 15.2 MB/s │ 2:34 ETA │ │
│ │  [⏸ Pause] [× Cancel]                                       │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │  📄 nodejs-v20.msi                                          │ │
│ │  ██████████████████████████████  100% │ Complete            │ │
│ │  [📂 Open] [📁 Open Folder]                                 │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │  📄 vscode-setup.exe                                        │ │
│ │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  Queued                     │ │
│ │  [▶ Start] [× Remove]                                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Downloads: 3  │  Active: 1  │  Speed: 15.2 MB/s               │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Verification Plan

### Automated Tests

```bash
# Run all unit tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_downloader.py -v
```

**Test cases:**
1. `test_segment_download` - ทดสอบดาวน์โหลด segment เดียว
2. `test_multi_segment_merge` - ทดสอบรวมไฟล์หลาย segments
3. `test_pause_resume` - ทดสอบ pause และ resume
4. `test_queue_management` - ทดสอบจัดการคิว

### Manual Verification

1. **Test Basic Download**
   - รันโปรแกรม: `python main.py`
   - กด "Add" แล้วใส่ URL: `https://releases.ubuntu.com/22.04/ubuntu-22.04.5-desktop-amd64.iso`
   - ตรวจสอบว่าดาวน์โหลดเริ่มและแสดง progress

2. **Test Pause/Resume**
   - ระหว่างดาวน์โหลด กด "Pause"
   - ตรวจสอบว่าหยุดดาวน์โหลด
   - กด "Resume" ตรวจสอบว่าดาวน์โหลดต่อจากจุดเดิม

3. **Test Multi-threaded Speed**
   - เปรียบเทียบความเร็วกับ browser download
   - ควรเร็วกว่า 2-3 เท่าสำหรับไฟล์ใหญ่

---

## 📊 Development Phases

| Phase | ระยะเวลา | รายละเอียด |
|-------|---------|------------|
| 1. Setup | ~10 tools | สร้างโครงสร้างโปรเจกต์ |
| 2. Core Engine | ~30 tools | Download engine + segments |
| 3. UI | ~25 tools | Main window + dialogs |
| 4. Integration | ~15 tools | เชื่อม UI กับ engine |
| 5. Polish | ~10 tools | Theme, icons, final touches |
| 6. Testing | ~10 tools | ทดสอบและแก้ไขบัก |

**รวม: ~100 tool calls**

---

## ⚠️ User Review Required

> [!IMPORTANT]
> กรุณาตรวจสอบและอนุมัติ:
> 1. **Features** - ฟีเจอร์ที่ระบุครบถ้วนหรือไม่?
> 2. **UI Design** - ต้องการปรับเปลี่ยน UI หรือไม่?
> 3. **โครงสร้างโปรเจกต์** - เหมาะสมหรือไม่?

> [!NOTE]
> หลังอนุมัติ จะเริ่มพัฒนาตาม phases ที่กำหนด
