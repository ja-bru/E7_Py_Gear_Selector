"""Primary application window."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QStatusBar, QTabWidget

from gui.state import AppState
from gui.tabs import ExportTab, ImportTab, OptimizeTab, ResultsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = AppState()
        self.setWindowTitle("E7 Gear Selector")
        self.resize(960, 640)

        self.tabs = QTabWidget()
        self.import_tab = ImportTab(self.state, self._on_data_loaded)
        self.optimize_tab = OptimizeTab(self.state, self._on_optimized)
        self.results_tab = ResultsTab(self.state)
        self.export_tab = ExportTab(self.state)

        self.tabs.addTab(self.import_tab, "Import")
        self.tabs.addTab(self.optimize_tab, "Optimize")
        self.tabs.addTab(self.results_tab, "Results")
        self.tabs.addTab(self.export_tab, "Export")

        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    def _on_data_loaded(self) -> None:
        self.optimize_tab.refresh()
        self.export_tab.refresh()
        self.results_tab.clear()
        self.statusBar().showMessage("Gear data loaded")

    def _on_optimized(self, result) -> None:
        self.results_tab.show_result(result)
        self.tabs.setCurrentWidget(self.results_tab)
        self.statusBar().showMessage(f"Optimization complete for {result.char}")
