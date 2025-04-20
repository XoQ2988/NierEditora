from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from nier_editora.core import Item


class ItemTableModel(QAbstractTableModel):
    HEADERS = ["Index", "Name", "Quantity"]

    def __init__(self, items: list["Item"], parent=None):
        super().__init__(parent)
        self._items = items

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
            return None

        item = self._items[index.row()]
        col = index.column()
        if col == 0:
            return item.index
        elif col == 1:
            return item.name
        elif col == 2:
            return item.quantity

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)

    def flags(self, index: QModelIndex):
        base = super().flags(index)
        if index.column() == 2:
            return base | Qt.ItemIsEditable
        return base

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if role != Qt.EditRole or index.column() != 2:
            return False
        try:
            qty = int(value)
        except ValueError:
            return False
        self._items[index.row()].quantity = qty
        self.dataChanged.emit(index, index, [Qt.DisplayRole])
        return True

    # ───────────────────────────────────────────────────
    # Convenience methods for adding/removing rows:

    def appendRow(self, item: "Item"):
        """
        Insert one new Item at the end of the model.
        """
        row = len(self._items)
        self.beginInsertRows(QModelIndex(), row, row)
        self._items.append(item)
        self.endInsertRows()

    def removeRow(self, row: int, parent=QModelIndex()):
        if 0 <= row < len(self._items):
            self.beginRemoveRows(parent, row, row)
            del self._items[row]
            self.endRemoveRows()
            return True
        return False

    def replaceRow(self, row: int, item: "Item"):
        if 0 <= row < len(self._items):
            self._items[row] = item
            top_left = self.index(row, 0)
            bottom_right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
            return True
        return False
