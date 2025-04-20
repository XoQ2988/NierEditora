from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from nier_editora.core import Weapon


class WeaponTableModel(QAbstractTableModel):
    HEADERS = ["Index", "Name", "Level"]

    def __init__(self, weapons: list[Weapon], parent=None):
        super().__init__(parent)
        self._weapons = weapons

    def rowCount(self, parent=QModelIndex()):
        return len(self._weapons)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        w = self._weapons[index.row()]
        col = index.column()
        if col == 0:
            return w.index
        elif col == 1:
            return w.name
        elif col == 2:
            return w.level

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)

    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 2:
            return flags | Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.column() == 2:
            try:
                lvl = int(value)
            except ValueError:
                return False
            self._weapons[index.row()].level = lvl
            self.dataChanged.emit(index, index, [Qt.DisplayRole])
            return True
        return False
