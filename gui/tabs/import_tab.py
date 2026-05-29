"""Load and score gear inventory."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import paths
from gui.state import AppState
from gui.workers import ScoreGearWorker


class ImportTab(QWidget):
    def __init__(self, state: AppState, on_loaded, parent=None):
        super().__init__(parent)
        self.state = state
        self.on_loaded = on_loaded
        self._worker: ScoreGearWorker | None = None

        self.path_edit = QLineEdit(str(paths.MASTER_DATA_JSON))
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse)

        self.load_btn = QPushButton("Load && Score Gear")
        self.load_btn.clicked.connect(self._load)

        self.status_label = QLabel("Load your gear JSON to begin.")
        self.status_label.setWordWrap(True)

        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit, stretch=1)
        path_row.addWidget(browse_btn)

        box = QGroupBox("Gear data")
        box_layout = QVBoxLayout(box)
        box_layout.addWidget(QLabel("master_data.json"))
        box_layout.addLayout(path_row)
        box_layout.addWidget(self.load_btn)
        box_layout.addWidget(self.status_label)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addStretch()

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select master_data.json",
            str(paths.INP_DIR),
            "JSON files (*.json)",
        )
        if path:
            self.path_edit.setText(path)

    def _set_busy(self, busy: bool) -> None:
        self.load_btn.setEnabled(not busy)
        self.path_edit.setEnabled(not busy)

    def _load(self) -> None:
        path = Path(self.path_edit.text().strip())
        if not path.is_file():
            QMessageBox.warning(self, "File not found", f"Could not find:\n{path}")
            return

        self._set_busy(True)
        self.status_label.setText("Working…")

        self._worker = ScoreGearWorker(path, self)
        self._worker.status.connect(self.status_label.setText)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.start()

    def _on_failed(self, message: str) -> None:
        self._set_busy(False)
        self.status_label.setText(message)
        QMessageBox.critical(self, "Load failed", message)

    def _on_finished(self, df_items, df_hero, data, char_list, target_stats) -> None:
        self._set_busy(False)
        self.state.master_data_path = Path(self.path_edit.text().strip())
        self.state.master_data = data
        self.state.df_items = df_items
        self.state.df_hero = df_hero
        self.state.char_list = list(char_list)
        self.state.target_stats = target_stats
        self.state.last_result = None

        item_count = len(df_items)
        hero_count = len(char_list)
        self.status_label.setText(f"Loaded {item_count:,} items for {hero_count} heroes.")
        self.on_loaded()
