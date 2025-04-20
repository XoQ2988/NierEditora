import sys
import logging
from PySide6.QtWidgets import QApplication
from nier_editora.ui.main_window import NierEditoraUI

def main():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    app = QApplication(sys.argv)

    window = NierEditoraUI()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
