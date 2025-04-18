# NieR:Editora
[![PyPI version](https://img.shields.io/pypi/v/NierEditora.svg)](https://pypi.org/project/NierEditora)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A cross‑platform save editor for _NieR:Automata_, supporting both PC and PS4/5 formats.
Work with it via a command‑line interface, or GUI (tbi)

---

## Features


- **Dual-format support**: **_Read and write_** both PC (SlotData_*.dat) and PS4 (GameData) save files.
- **CLI ~~& GUI~~**: Command‑line tools for scripting and batch operations, GUI is planned
- **Core edits**: 
  - **_View and change_** Player Name, Play Time, Money, and XP.
  - **_Convert_** saves PC ↔ Console format.
- **Pluggable**: Easily extend with inventory dumps, weapon/chip editors, and localization.
- **i18n skeleton**: Out-of-the-box support for **_translating_** all item names (as if anyone would do that)

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