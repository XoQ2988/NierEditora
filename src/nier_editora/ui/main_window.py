import functools
import logging
import shutil
import sys
import time
from pathlib import Path
from typing import Optional

import PySide6.QtWidgets
from PySide6.QtCore import Qt, QSettings, QTime
from PySide6.QtGui import QAction

import nier_editora.core
from nier_editora.core.constants import ITEM_LIST
from nier_editora.core.experience import Experience
from nier_editora.core.i18n import translate_item
from nier_editora.ui.chiptablemodel import ChipTableModel
from nier_editora.ui.itemtablemodel import ItemTableModel
from nier_editora.ui.weapontablemodel import WeaponTableModel

pcFileFormat = "SlotData_*.dat"
consoleFileFormat = "GameData"
fileFormats = f"PC Save File ({pcFileFormat})", f"Console Save File ({consoleFileFormat})"


def mark_dirty(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        result = fn(self, *args, **kwargs)
        self._dirty = True
        return result
    return wrapper


class NierEditoraUI(PySide6.QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(NierEditoraUI, self).__init__(parent)
        self.settings = QSettings("YourCompany", "NieREditora")
        self.setWindowTitle("Nier:Editora (PySide6 Edition)")
        self.resize(600, 400)

        self.savefile: Optional[nier_editora.core.SaveFile] = None
        self.file_path: Optional[Path] = None
        self._dirty: bool = False

        self._create_ui()
        self._connect_signals()
        self._create_shortcuts()
        self._post_init()

    def _create_ui(self) -> None:
        splitter = PySide6.QtWidgets.QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(splitter)

        # --- Menu bar ---
        # File Menu
        self.file_menu = self.menuBar().addMenu("&File")
        self.open_act = QAction("&Open...", self)

        self.save_act = QAction("&Save", self)

        self.save_as_act = QAction("Save &As...", self)

        self.quit_act = QAction("&Quit", self)

        self.file_menu.addAction(self.open_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_act)
        self.file_menu.addAction(self.save_as_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.quit_act)

        # Tools Menu
        self.validate_act = QAction("&Validate Save", self)
        self.backup_act = QAction("&Backup Save", self)
        self.restore_act = QAction("&Restore Save", self)
        self.export_pc_act = QAction("As &PC Save File", self)
        self.export_console_act = QAction("As &Console Save File", self)

        self.tools_menu = self.menuBar().addMenu("&Tools")
        self.tools_menu.addAction(self.validate_act)
        self.tools_menu.addSeparator()
        self.tools_menu.addAction(self.backup_act)
        self.tools_menu.addAction(self.restore_act)
        self.tools_menu.addSeparator()

        self.export_menu = self.tools_menu.addMenu("&Export")
        self.export_menu.addAction(self.export_pc_act)
        self.export_menu.addAction(self.export_console_act)

        # Help Menu
        self.help_menu = self.menuBar().addMenu("&Help")
        self.about_act = QAction("About", self)
        self.help_menu.addAction(self.about_act)


        # --- Side bar ---
        self.sidebar = PySide6.QtWidgets.QWidget()
        form = PySide6.QtWidgets.QFormLayout(self.sidebar)

        self.name_edit = PySide6.QtWidgets.QLineEdit()
        form.addRow("Name:", self.name_edit)

        self.money_edit = PySide6.QtWidgets.QSpinBox()
        self.money_edit.setRange(0, 10_000_000)
        self.money_edit.setSingleStep(100)
        form.addRow("Money:", self.money_edit)

        self.level_edit = PySide6.QtWidgets.QSpinBox()
        self.level_edit.setRange(1, 99)
        form.addRow("Level:", self.level_edit)

        self.xp_edit = PySide6.QtWidgets.QSpinBox()
        self.xp_edit.setRange(0, 2 ** 31 - 1)
        form.addRow("Experience:", self.xp_edit)

        self.time_edit = PySide6.QtWidgets.QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setMinimumTime(QTime(0, 0, 0))
        self.time_edit.setMaximumTime(QTime(23, 59, 59))
        form.addRow("Playtime:", self.time_edit)

        self.sidebar.setLayout(form)
        self.sidebar.setMaximumWidth(200)
        splitter.addWidget(self.sidebar)

        # --- Main are ---
        main = PySide6.QtWidgets.QWidget()
        layout = PySide6.QtWidgets.QVBoxLayout(main)
        splitter.addWidget(main)

        # Inventory tabs
        self.tabs = PySide6.QtWidgets.QTabWidget()
        layout.addWidget(self.tabs, 1)

        # --- Items tab ---
        items_page = PySide6.QtWidgets.QWidget()
        items_layout = PySide6.QtWidgets.QVBoxLayout(items_page)

        self.item_table = PySide6.QtWidgets.QTableView()
        self.item_model = ItemTableModel([])
        self.item_table.setModel(self.item_model)
        self.item_table.setAlternatingRowColors(True)

        vh = self.item_table.verticalHeader()
        vh.setVisible(True)
        vh.setDefaultSectionSize(24)
        vh.setSectionResizeMode(PySide6.QtWidgets.QHeaderView.Fixed)

        hh = self.item_table.horizontalHeader()
        hh.setSectionResizeMode(0, PySide6.QtWidgets.QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, PySide6.QtWidgets.QHeaderView.Stretch)
        hh.setSectionResizeMode(2, PySide6.QtWidgets.QHeaderView.ResizeToContents)

        items_layout.addWidget(self.item_table)

        item_buttons = PySide6.QtWidgets.QHBoxLayout()
        item_buttons.addStretch()
        self.btn_item_add = PySide6.QtWidgets.QPushButton("+")
        self.btn_item_remove = PySide6.QtWidgets.QPushButton("–")
        self.btn_item_add.setEnabled(False)
        self.btn_item_remove.setEnabled(False)
        item_buttons.addWidget(self.btn_item_add)
        item_buttons.addWidget(self.btn_item_remove)
        items_layout.addLayout(item_buttons)

        self.tabs.addTab(items_page, "Items")

        # --- Weapons tab ---
        weapons_page = PySide6.QtWidgets.QWidget()
        weapons_layout = PySide6.QtWidgets.QVBoxLayout(weapons_page)

        self.weapon_table = PySide6.QtWidgets.QTableView()
        self.weapon_model = WeaponTableModel([])
        self.weapon_table.setModel(self.weapon_model)
        self.weapon_table.setAlternatingRowColors(True)

        vh = self.weapon_table.verticalHeader()
        vh.setVisible(True)
        vh.setDefaultSectionSize(24)
        vh.setSectionResizeMode(PySide6.QtWidgets.QHeaderView.Fixed)

        hh = self.weapon_table.horizontalHeader()
        hh.setSectionResizeMode(0, PySide6.QtWidgets.QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, PySide6.QtWidgets.QHeaderView.Stretch)
        hh.setSectionResizeMode(2, PySide6.QtWidgets.QHeaderView.ResizeToContents)

        weapons_layout.addWidget(self.weapon_table)

        weapon_buttons = PySide6.QtWidgets.QHBoxLayout()
        weapon_buttons.addStretch()
        self.btn_add_weapon = PySide6.QtWidgets.QPushButton("+")
        self.btn_remove_weapon = PySide6.QtWidgets.QPushButton("–")
        weapon_buttons.addWidget(self.btn_add_weapon)
        weapon_buttons.addWidget(self.btn_remove_weapon)
        weapons_layout.addLayout(weapon_buttons)

        self.tabs.addTab(weapons_page, "Weapons")

        # --- Chips tab ---
        chips_page = PySide6.QtWidgets.QWidget()
        chips_layout = PySide6.QtWidgets.QVBoxLayout(chips_page)

        self.chip_table = PySide6.QtWidgets.QTableView()
        self.chip_model = ChipTableModel([])
        self.chip_table.setModel(self.chip_model)
        self.chip_table.setAlternatingRowColors(True)

        vh = self.chip_table.verticalHeader()
        vh.setVisible(True)
        vh.setDefaultSectionSize(24)
        vh.setSectionResizeMode(PySide6.QtWidgets.QHeaderView.Fixed)

        hh = self.chip_table.horizontalHeader()
        hh.setSectionResizeMode(0, PySide6.QtWidgets.QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, PySide6.QtWidgets.QHeaderView.Stretch)
        hh.setSectionResizeMode(2, PySide6.QtWidgets.QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, PySide6.QtWidgets.QHeaderView.ResizeToContents)

        chips_layout.addWidget(self.chip_table)

        chip_buttons = PySide6.QtWidgets.QHBoxLayout()
        chip_buttons.addStretch()
        self.btn_add_chip = PySide6.QtWidgets.QPushButton("+")
        self.btn_remove_chip = PySide6.QtWidgets.QPushButton("–")
        self.btn_add_chip.setEnabled(False)
        self.btn_remove_chip.setEnabled(False)
        chip_buttons.addWidget(self.btn_add_chip)
        chip_buttons.addWidget(self.btn_remove_chip)
        chips_layout.addLayout(chip_buttons)

        self.tabs.addTab(chips_page, "Chips")

        splitter.addWidget(main)


        # --- Status Bar ---
        self.status = PySide6.QtWidgets.QStatusBar(self)
        self.setStatusBar(self.status)

    def _connect_signals(self):
        self.open_act.triggered.connect(self.open_save)
        self.save_act.triggered.connect(self.save)
        self.save_as_act.triggered.connect(self.save_as)
        self.quit_act.triggered.connect(self.closeEvent)
        self.validate_act.triggered.connect(self.validate_save)
        self.backup_act.triggered.connect(self.backup_save)
        self.restore_act.triggered.connect(self.restore_backup)
        self.export_pc_act.triggered.connect(lambda: self._export_save(console=False))
        self.export_console_act.triggered.connect(lambda: self._export_save(console=True))
        self.about_act.triggered.connect(self.about_dialog)
        self.name_edit.editingFinished.connect(self._on_name_edited)
        self.money_edit.editingFinished.connect(self._on_money_edited)
        self.level_edit.editingFinished.connect(self._on_level_edited)
        self.xp_edit.editingFinished.connect(self._on_xp_edited)
        self.time_edit.editingFinished.connect(self._on_time_edited)

        self.btn_item_add.clicked.connect(self._on_add_item)
        self.btn_item_remove.clicked.connect(self._on_remove_item)
        self.item_table.selectionModel().selectionChanged.connect(self._update_item_buttons)

        self.btn_add_weapon.clicked.connect(self._on_add_weapon)
        self.btn_remove_weapon.clicked.connect(self._on_remove_weapon)
        self.weapon_table.selectionModel().selectionChanged.connect(self._update_weapon_buttons)

        self.btn_add_chip.clicked.connect(self._on_add_chip)
        self.btn_remove_chip.clicked.connect(self._on_remove_chip)
        self.chip_table.selectionModel().selectionChanged.connect(
            lambda *_: self._update_chip_buttons()
        )

    def _create_shortcuts(self) -> None:
        shortcuts = [
            (self.open_act,     "Ctrl+O"),
            (self.save_act,     "Ctrl+S"),
            (self.save_as_act,  "Ctrl+Shift+S"),
            (self.quit_act,     "Ctrl+Q"),
            (self.validate_act, "Ctrl+V"),
            (self.backup_act,   "Ctrl+B"),
            (self.restore_act,  "Ctrl+Shift+B"),
            (self.about_act,    "Ctrl+H"),
        ]

        for act, keys in shortcuts:
            act.setShortcut(keys)

    def _post_init(self) -> None:
        geom = self.settings.value("mainWindow/geometry")
        if geom: self.restoreGeometry(geom)

        warned = self.settings.value("seenChipWarning", False, type=bool)
        if not warned:
            PySide6.QtWidgets.QMessageBox.warning(
                self,
                "Chip Adding Unstable",
                "Heads up!\nThe chip‑adding system is currently unstable and may result in invalid items."
                "\nPlease save/backup often and use with caution."
            )
            self.settings.setValue("seenChipWarning", True)

        defaultVals = [
            (self.name_edit, "YoRHa No.2 Type B"),
            (self.money_edit, 42000),
            (self.level_edit, 69),
            (self.xp_edit, 483167),
            (self.time_edit, "23:59:59")
        ]

        for widget, val in defaultVals:
            if isinstance(widget, PySide6.QtWidgets.QLineEdit):
                widget.setText(val)
            elif isinstance(widget, PySide6.QtWidgets.QSpinBox):
                widget.setValue(int(val))
            elif isinstance(widget, PySide6.QtWidgets.QTimeEdit):
                h, m, s = map(int, val.split(":"))
                widget.setTime(QTime(h, m, s))
        for act in (
                self.save_act, self.save_as_act,
                self.validate_act, self.backup_act, self.restore_act, self.export_menu,
                self.btn_item_add, self.btn_item_remove, self.btn_add_weapon,
                self.btn_remove_weapon, self.btn_add_chip, self.btn_remove_chip
        ): act.setEnabled(False)

        for field in (
            self.name_edit, self.money_edit, self.level_edit, self.xp_edit, self.time_edit
        ): field.setEnabled(False)


    # public slots
    def open_save(self, path: Optional[Path] = None):
        if not path:
            last_dir = self.settings.value("lastDir", str(Path.cwd()))
            path, _ = PySide6.QtWidgets.QFileDialog.getOpenFileName(self, "Open Save File", str(last_dir),
                                                                filter=";;".join(fileFormats + ("All Files (*.*)",)))
            if path:
                self.settings.setValue("lastDir", str(Path(path).parent))
            else:
                return
        try:
            self.savefile = nier_editora.core.SaveFile.load_from_file(Path(path))
            self.file_path = Path(path)
            self.status.showMessage(f"Loaded {self.savefile.player_name}", 1200)
        except Exception as e:
            PySide6.QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load:\n{e}")
            return

        self.name_edit.setText(self.savefile.player_name)
        self.money_edit.setValue(self.savefile.money)

        lvl = Experience.get_level_from_experience(self.savefile.xp)
        self.level_edit.setValue(lvl)
        self.xp_edit.setValue(self.savefile.xp)

        total_secs = self.savefile.play_time
        h, rem = divmod(total_secs, 3600)
        m, s = divmod(rem, 60)
        self.time_edit.setTime(QTime(h, m, s))

        self._populate_items()
        self._populate_weapons()
        self._populate_chips()

        for field in (
            self.validate_act, self.backup_act, self.restore_act, self.export_menu,
            self.name_edit, self.money_edit, self.level_edit, self.xp_edit, self.time_edit,
            self.btn_item_add, self.btn_item_remove,
            self.btn_add_weapon, self.btn_remove_weapon,
            self.btn_add_chip, self.btn_remove_chip
        ): field.setEnabled(True)

        self._dirty = False

    def save(self):
        if self.file_path:
            self.savefile.save_to_file(self.file_path)
            self.status.showMessage(f"Saved {self.file_path.name}", 1200)
            self._dirty = False

    def save_as(self):
        p, _ = PySide6.QtWidgets.QFileDialog.getSaveFileName(self, "Save As...",
                                filter=";;".join(reversed(fileFormats) if self.savefile.is_console else fileFormats))
        if p:
            self.savefile.save_to_file(Path(p))
            self.status.showMessage(f"Saved as {Path(p).name}", 1200)

    def validate_save(self):
        try:
            nier_editora.core.SaveFile().load(self.file_path.read_bytes())
            PySide6.QtWidgets.QMessageBox.information(self, "Validate", "Save is valid.")
        except Exception as e:
            PySide6.QtWidgets.QMessageBox.critical(self, "Invalid", f"Validation failed:\n{e}")

    def backup_save(self):
        bak = self.file_path.with_suffix(self.file_path.suffix + f".{int(time.time())}.bak")
        shutil.copy2(self.file_path, bak)
        self.status.showMessage(f"Backup saved as {bak.name}", 800)

    def restore_backup(self):
        backups = sorted(self.file_path.parent.glob(f"{self.file_path.name}.*.bak"))
        if not backups:
            PySide6.QtWidgets.QMessageBox.warning(self, "Restore", "No backups found.")
            return
        shutil.copy2(backups[-1], self.file_path)
        self.open_save(self.file_path)
        self.status.showMessage(f"Restored {backups[-1].name}", 800)


    # helpers
    def _export_save(self, *, console: bool):
        if not self.savefile: return
        old = self.savefile.is_console
        self.savefile.is_console = console
        data = self.savefile.write()
        self.savefile.is_console = old

        EXPORT_OPTS = {
            True: dict(caption="Export as Console Save", filter=f"Console File ({consoleFileFormat});;All Files (*.*)"),
            False: dict(caption="Export as Pc Save", filter=f"PC File ({pcFileFormat});;All Files (*.*)"),
        }[console]
        opts = EXPORT_OPTS
        path, _ = PySide6.QtWidgets.QFileDialog.getSaveFileName(self, opts['caption'], filter=opts['filter'])

        if not path: return

        try:
            Path(path).write_bytes(data)
            self.status.showMessage(f"Exported save to {Path(path).name}", 1200)
        except Exception as e:
            PySide6.QtWidgets.QMessageBox.warning(self, "Export Error", str(e))

    @mark_dirty
    def _on_name_edited(self):
        text = self.name_edit.text()
        if not text:
            PySide6.QtWidgets.QMessageBox.warning(self, "Invalid Name", "Name cannot be empty.")
            self.name_edit.setText(self.savefile.player_name)
            return

        self.savefile.player_name = text
        
    @mark_dirty
    def _on_money_edited(self):
        txt = self.money_edit.value()
        try:
            money = int(txt)
            if money < 0:
                raise ValueError
        except ValueError:
            PySide6.QtWidgets.QMessageBox.warning(self, "Invalid Money", "Please enter a non‑negative integer.")
            self.money_edit.setValue(self.savefile.money)
            return

        self.savefile.money = money
        
    
    @mark_dirty
    def _on_xp_edited(self):
        xp = 0
        txt = self.xp_edit.text().strip()
        try:
            xp = int(txt)
            if xp < 0:
                raise ValueError
        except ValueError:
            self.status.showMessage(f"Experience Value \'{xp}\' INVALID", 1200)
            self.xp_edit.setValue(self.savefile.xp)
            return

        self.savefile.xp = xp
        lvl = Experience.get_level_from_experience(xp)
        self.level_edit.setValue(lvl)


    @mark_dirty
    def _on_level_edited(self):
        lvl = 0
        txt = self.level_edit.text().strip()
        try:
            lvl = int(txt)
            if not Experience.is_valid_level(lvl):
                raise ValueError
        except ValueError:
            self.status.showMessage(f"Level \'{lvl}\' INVALID", 1200)
            current_level = Experience.get_level_from_experience(self.savefile.xp)
            self.level_edit.setValue(current_level)
            return

        xp_needed = Experience.get_experience_for_level(lvl)
        self.savefile.xp = xp_needed
        self.xp_edit.setValue(xp_needed)

        

    @mark_dirty
    def _on_time_edited(self):
        h = m = s = 0
        txt = self.time_edit.text().strip()
        parts = txt.split(":")
        if len(parts) != 3:
            valid = False
        else:
            try:
                h, m, s = map(int, parts)
                valid = (0 <= m < 60 and 0 <= s < 60 and h >= 0)
            except ValueError:
                valid = False

        if not valid:
            PySide6.QtWidgets.QMessageBox.warning(self, "Invalid Time", "Please use HH:MM:SS format.")
            total = self.savefile.play_time
            h, rem = divmod(total, 3600)
            m, s = divmod(rem, 60)
            self.time_edit.setTime(QTime(h, m, s))
            return

        total_secs = h * 3600 + m * 60 + s
        self.savefile.play_time = total_secs

        self.time_edit.clearFocus()
        #

    def _populate_items(self):
        self.item_model.beginResetModel()
        self.item_model._items = list(self.savefile.inventory)
        self.item_model.endResetModel()
        self._update_item_buttons()

    def _update_item_buttons(self):
        sel = self.item_table.selectionModel().selectedRows()
        if not sel:
            self.btn_item_remove.setEnabled(False)
            return

        row = sel[0].row()
        slot = self.savefile.inventory.raw[row]
        self.btn_item_remove.setEnabled(slot.id != -1)

    @mark_dirty
    def _on_add_item(self):
        choices = [
            (iid, translate_item(iid) or raw)
            for iid, raw in ITEM_LIST.items()
            if raw.startswith("item_") or raw.startswith("fish_")
        ]
        items_str = [f"{hex(iid)}: {name}" for iid, name in choices]
        pick, ok = PySide6.QtWidgets.QInputDialog.getItem(
            self,
            "Add Item",
            "Select an item to add:",
            items_str,
            editable=False
        )
        if not ok:
            return

        chosen_hex = pick.split(":", 1)[0]
        new_id = int(chosen_hex, 16)

        for slot in self.savefile.inventory.raw:
            if slot.id == -1:
                idx = slot.index
                break
        else:
            PySide6.QtWidgets.QMessageBox.warning(self, "Inventory Full", "No empty slots left.")
            return

        new_item = nier_editora.core.Item.empty(idx)
        new_item.id = new_id
        new_item.quantity = 1
        self.savefile.inventory.raw[idx] = new_item

        self.item_model.appendRow(new_item)
        self._populate_items()
        

    @mark_dirty
    def _on_remove_item(self):
        sel = self.item_table.selectionModel().selectedRows()
        if not sel:
            PySide6.QtWidgets.QMessageBox.warning(self, "No Selection", "Please select an item to remove.")
            return

        row = sel[0].row()
        self.savefile.inventory.raw[row] = nier_editora.core.Item.empty(row)
        self.item_model.removeRow(row)
        

    def _populate_weapons(self):
        self.weapon_model.beginResetModel()
        self.weapon_model._weapons = list(self.savefile.weapons)
        self.weapon_model.endResetModel()
        self._update_weapon_buttons()

    def _update_weapon_buttons(self):
        sel = self.weapon_table.selectionModel().selectedRows()
        if not sel:
            self.btn_remove_weapon.setEnabled(False)
            return
        row = sel[0].row()
        slot = self.savefile.weapons.raw[row]
        self.btn_remove_weapon.setEnabled(slot.id != -1)

    @mark_dirty
    def _on_add_weapon(self):
        choices = [(iid, name) for iid, name in ITEM_LIST.items() if name.startswith("weapon_")]
        items_str = [f"{hex(iid)}: {translate_item(iid) or raw}" for iid, raw in choices]
        pick, ok = PySide6.QtWidgets.QInputDialog.getItem(
            self, "Add Weapon", "Select a weapon:", items_str, editable=False)
        if not ok: return
        new_id = int(pick.split(":", 1)[0], 16)
        for slot in self.savefile.weapons.raw:
            if slot.id == -1:
                idx = slot.index
                break
        else:
            PySide6.QtWidgets.QMessageBox.warning(self, "Full", "No empty weapon slot.")
            return
        new_slot = nier_editora.core.Weapon.empty(idx)
        new_slot.id = new_id
        new_slot.level = 0
        self.savefile.weapons.raw[idx] = new_slot
        self.open_save(self.file_path)  # or just re‑populate weapons
        

    @mark_dirty
    def _on_remove_weapon(self):
        sel = self.weapon_table.selectionModel().selectedRows()
        if not sel: return
        row = sel[0].row()
        idx = self.savefile.weapons.raw[row].index
        self.savefile.weapons.raw[idx] = nier_editora.core.Weapon.empty(idx)
        self.open_save(self.file_path)
        

    def _populate_chips(self):
        self.chip_model.beginResetModel()
        self.chip_model._chips = list(self.savefile.chips)
        self.chip_model.endResetModel()
        self._update_chip_buttons()

    def _update_chip_buttons(self):
        sel = self.chip_table.selectionModel().selectedRows()
        if not sel:
            self.btn_remove_chip.setEnabled(False)
            return

        row = sel[0].row()
        slot = self.savefile.chips.raw[row]
        # active if base_id != -1
        self.btn_remove_chip.setEnabled(slot.base_id != -1)

    @mark_dirty
    def _on_add_chip(self):
        choices = [
            (iid, translate_item(iid) or raw)
            for iid, raw in ITEM_LIST.items()
            if raw.startswith("skill_psv_") or raw.startswith("capacity_")
        ]
        items_str = [f"{hex(iid)}: {name}" for iid, name in choices]
        pick, ok = PySide6.QtWidgets.QInputDialog.getItem(self, "Add Chip", "Select a chip:", items_str, editable=False)
        if not ok: return
        new_id = int(pick.split(":", 1)[0], 16)

        for slot in self.savefile.chips.raw:
            if slot.base_id == -1:
                idx = slot.index
                break
        else:
            PySide6.QtWidgets.QMessageBox.warning(self, "Chip Inventory Full", "No empty chip slots.")
            return

        new_slot = nier_editora.core.Chip.empty(idx)
        new_slot.base_id = new_id
        new_slot.level = 0
        new_slot.weight = 0
        self.savefile.chips.raw[idx] = new_slot

        self._populate_chips()
        

    @mark_dirty
    def _on_remove_chip(self):
        sel = self.chip_table.selectionModel().selectedRows()
        if not sel: return
        row = sel[0].row()
        idx = self.savefile.chips.raw[row].index
        self.savefile.chips.raw[idx] = nier_editora.core.Chip.empty(idx)

        self._populate_chips()
        

    # shutdown hook
    def closeEvent(self, event):
        if self._dirty:
            msg = "You have unsaved changes. What would you like to do?"
            reply = PySide6.QtWidgets.QMessageBox.question(
                self,
                "Unsaved Changes",
                msg,
                PySide6.QtWidgets.QMessageBox.Save | PySide6.QtWidgets.QMessageBox.Discard
                | PySide6.QtWidgets.QMessageBox.Cancel,
                PySide6.QtWidgets.QMessageBox.Save
            )
            if reply == PySide6.QtWidgets.QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == PySide6.QtWidgets.QMessageBox.Save:
                if self.file_path and self.savefile:
                    self.save()
                else:
                    self.save_as()

        self.settings.setValue("mainWindow/geometry", self.saveGeometry())
        event.accept()


    # static helpers
    def about_dialog(self):
        PySide6.QtWidgets.QMessageBox.about(self, "About", "NieR:Editora\nby XoQ2988")



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

    app = PySide6.QtWidgets.QApplication(sys.argv)

    widget = NierEditoraUI()
    widget.show()

    sys.exit(app.exec())
