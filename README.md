# NieR:Editora
[![PyPI version](https://img.shields.io/pypi/v/NierEditora.svg)](https://pypi.org/project/NierEditora)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A cross‑platform save editor for _NieR:Automata_, supporting both PC and PS4/5 formats.  
Work with it via a command‑line interface **and** a Qt‑based GUI.

---

## Features

- **Dual-format support**: **_Read and write_** both PC (`SlotData_*.dat`) and PS4 (`GameData`) save files.
- **CLI & GUI**:  
  - **CLI** for scripting and batch operations (`niereditora info`, `set`, `convert`, etc.)  
  - **Qt6 GUI**—fully implemented with PySide6 for editing name, play time, money, XP, inventory, weapons, and chips.
- **Core edits**:  
  - **_View and change_** Player Name, Play Time, Money, and XP.  
  - **_Convert_** saves PC ↔ Console format.  
  - **_Inventory editors_** for items, weapons, and chips (chip‑adding currently marked experimental; one‑time warning on first use).
- **Real‑time XP↔Level sync**: Editing XP updates Level field and vice versa.
- **Pluggable architecture**: Easily extend with new inventory dumps, custom editors, and localization.
- **i18n skeleton**: Out‑of‑the‑box support for **_translating_** all item names.

## Installation
```shell
# Clone the repo
git clone https://github.com/<your‑username>/NierEditora.git
cd NierEditora

# Install in editable mode (requires Python 3.8+)
pip install -e .
```

## CLI Usage
```shell
# Show save metadata
niereditora info path/to/SlotData_001.dat

# Modify multiple fields in place
niereditora set path/to/GameData \
  --name "2B" \
  --time 12:34:56 \
  --money 999999 \
  --xp 123456

# Write to a new file instead of overwriting
niereditora set path/to/SlotData_001.dat \
  --xp 50000 \
  --output edited.dat

# Convert PS4 save → PC format
niereditora convert GameData --to-pc

# Convert PC save → PS4 format
niereditora convert SlotData_001.dat --to-console

# See help for any command
niereditora --help
niereditora set --help
```

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "feat: add X"`).
4. Push to your fork (`git push origin feature/your-feature`)
5. Open a pull request on GitHub

## License
This project is licensed under the MIT License. See the LICENSE file for details.