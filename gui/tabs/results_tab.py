"""Display optimization results."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from gui.state import AppState

DISPLAY_COLUMNS = [
    "Gear",
    "Set",
    "ATK",
    "HP",
    "DEF",
    "SPD",
    "CRIT",
    "CDMG",
    "EFF",
    "RES",
    "EHP",
    "Dmg_Rating",
    "Score",
]


class ResultsTab(QWidget):
    def __init__(self, state: AppState, parent=None):
        super().__init__(parent)
        self.state = state

        self.summary_label = QLabel("No results yet.")
        self.summary_label.setWordWrap(True)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        box = QGroupBox("Combinations")
        box_layout = QVBoxLayout(box)
        box_layout.addWidget(self.summary_label)
        box_layout.addWidget(self.table)

        layout = QVBoxLayout(self)
        layout.addWidget(box)

    def show_result(self, result) -> None:
        odf = result.odf.copy()
        columns = [col for col in DISPLAY_COLUMNS if col in odf.columns]
        if not columns:
            columns = list(odf.columns[:12])

        preview = odf[columns].head(200)
        self.table.clear()
        self.table.setRowCount(len(preview))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        for row_idx, row in enumerate(preview.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                text = "" if value is None else str(value)
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

        self.table.resizeColumnsToContents()
        self.summary_label.setText(
            f"{result.char} — showing {len(preview):,} of {len(odf):,} rows "
            f"(recommended index {result.idx_reco})."
        )

    def clear(self) -> None:
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.summary_label.setText("No results yet.")
