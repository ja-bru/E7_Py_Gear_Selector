"""Export scored gear and optimization output."""

from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import paths
from gui.state import AppState

EXPORT_COLUMNS = [
    "efficiency",
    "hero",
    "enhance",
    "slot",
    "level",
    "set",
    "rarity",
    "mainStat",
    "subStat1",
    "subStat2",
    "subStat3",
    "subStat4",
    "id",
    "locked",
]


class ExportTab(QWidget):
    def __init__(self, state: AppState, parent=None):
        super().__init__(parent)
        self.state = state

        self.export_pickle_btn = QPushButton("Save scored gear (.pkl)")
        self.export_pickle_btn.clicked.connect(self._export_pickle)
        self.export_json_btn = QPushButton("Save gear JSON (equip_potential.json)")
        self.export_json_btn.clicked.connect(self._export_json)

        self.status_label = QLabel("Exports write to the outp/ folder.")
        self.status_label.setWordWrap(True)

        box = QGroupBox("Output files")
        box_layout = QVBoxLayout(box)
        box_layout.addWidget(self.export_pickle_btn)
        box_layout.addWidget(self.export_json_btn)
        box_layout.addWidget(self.status_label)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addStretch()

        self.refresh()

    def refresh(self) -> None:
        ready = self.state.is_scored
        self.export_pickle_btn.setEnabled(ready)
        self.export_json_btn.setEnabled(ready)

    def _export_pickle(self) -> None:
        try:
            paths.OUTP_DIR.mkdir(parents=True, exist_ok=True)
            self.state.df_items.to_pickle(paths.EQUIP_POTENTIAL_PKL)
            self.state.df_items.to_csv(paths.EQUIP_POTENTIAL_CSV)
            self.status_label.setText(f"Saved {paths.EQUIP_POTENTIAL_PKL}")
            QMessageBox.information(self, "Export complete", str(paths.EQUIP_POTENTIAL_PKL))
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))

    def _export_json(self) -> None:
        try:
            paths.OUTP_DIR.mkdir(parents=True, exist_ok=True)
            export = self.state.df_items[EXPORT_COLUMNS].to_dict("records")
            with open(paths.EQUIP_POTENTIAL_JSON, "w", encoding="utf-8") as fp:
                json.dump(export, fp)
            self.status_label.setText(f"Saved {paths.EQUIP_POTENTIAL_JSON}")
            QMessageBox.information(self, "Export complete", str(paths.EQUIP_POTENTIAL_JSON))
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
