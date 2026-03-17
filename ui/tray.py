"""
ui/tray.py — CYRUS system tray icon
Always visible. Right-click for menu. Double-click to show HUD.
"""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui     import QIcon, QPixmap, QPainter, QColor, QPen, QBrush
from PySide6.QtCore    import Qt


def _make_icon():
    """Draw a clean teal arc-reactor style tray icon."""
    px = QPixmap(64, 64)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)

    # dark circle background
    p.setBrush(QBrush(QColor(10, 12, 18)))
    p.setPen(Qt.NoPen)
    p.drawEllipse(2, 2, 60, 60)

    # outer ring
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(QColor(200, 200, 200, 180), 2))
    p.drawEllipse(4, 4, 56, 56)

    # 3 arcs like the HUD
    p.setPen(QPen(QColor(220, 220, 220, 230), 3))
    for i in range(3):
        p.drawArc(10, 10, 44, 44, i * 120 * 16, 80 * 16)

    # centre dot
    p.setBrush(QBrush(QColor(255, 255, 255, 220)))
    p.setPen(Qt.NoPen)
    p.drawEllipse(26, 26, 12, 12)

    p.end()
    return QIcon(px)


class CyrusTray(QSystemTrayIcon):

    def __init__(self, app):
        super().__init__(_make_icon(), app)
        self._app = app
        self._win = None
        self.setToolTip("CYRUS")

        menu = QMenu()
        menu.addAction("Show CYRUS",   self._show)
        menu.addAction("Hide CYRUS",  self._hide)
        menu.addSeparator()
        menu.addAction("Quit CYRUS",   self._quit)
        self.setContextMenu(menu)

        # double-click shows HUD
        self.activated.connect(self._on_activate)

        # show tray icon immediately
        self.show()
        print("[Tray] icon visible.")

    def _on_activate(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show()

    def _show(self):
        for w in self._app.topLevelWidgets():
            from ui.hud import CyrusHUD
            if isinstance(w, CyrusHUD):
                w.show()
                w.raise_()
                w.activateWindow()
                return

    def _hide(self):
        for w in self._app.topLevelWidgets():
            from ui.hud import CyrusHUD
            if isinstance(w, CyrusHUD):
                w.hide()
                return

    def _quit(self):
        self._app.quit()