from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from nier_editora.core import Chip

class ChipTableModel(QAbstractTableModel):
    HEADERS = ["Index", "Name", "Level", "Weight"]

    def __init__(self, chips: list[Chip], parent=None):
        super().__init__(parent)
        self._chips = chips

    def rowCount(self, parent=QModelIndex()):
        return len(self._chips)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
            return None

        chip = self._chips[index.row()]
        col = index.column()

        if col == 0:
            return chip.index
        elif col == 1:
            return chip.name
        elif col == 2:
            return chip.level
        elif col == 3:
            return chip.weight

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)

    def flags(self, index):
        base = super().flags(index)
        # Allow editing of Level and Weight
        if index.column() in (2, 3):
            return base | Qt.ItemIsEditable
        return base

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False

        chip = self._chips[index.row()]
        col = index.column()

        try:
            iv = int(value)
        except ValueError:
            return False

        if col == 2:
            chip.level = iv
        elif col == 3:
            chip.weight = iv
        else:
            return False

        self.dataChanged.emit(index, index, [Qt.DisplayRole])
        return True
