"""Hero selection and optimization controls."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.state import AppState
from gui.workers import OptimizeWorker


class OptimizeTab(QWidget):
    def __init__(self, state: AppState, on_optimized, parent=None):
        super().__init__(parent)
        self.state = state
        self.on_optimized = on_optimized
        self._worker: OptimizeWorker | None = None

        self.hero_combo = QComboBox()
        self.hero_combo.setEnabled(False)

        self.optimize_btn = QPushButton("Run optimization")
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.clicked.connect(self._run)

        self.status_label = QLabel("Load gear data on the Import tab first.")
        self.status_label.setWordWrap(True)

        box = QGroupBox("Hero")
        box_layout = QVBoxLayout(box)
        box_layout.addWidget(QLabel("Character"))
        box_layout.addWidget(self.hero_combo)
        box_layout.addWidget(self.optimize_btn)
        box_layout.addWidget(self.status_label)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addStretch()

    def refresh(self) -> None:
        ready = self.state.is_scored and self.state.target_stats is not None
        self.hero_combo.setEnabled(ready)
        self.optimize_btn.setEnabled(ready)

        if not ready:
            self.hero_combo.clear()
            self.status_label.setText("Load gear data on the Import tab first.")
            return

        current = self.hero_combo.currentText()
        self.hero_combo.blockSignals(True)
        self.hero_combo.clear()
        self.hero_combo.addItems(self.state.char_list)
        if current in self.state.char_list:
            self.hero_combo.setCurrentText(current)
        self.hero_combo.blockSignals(False)
        self.status_label.setText("Select a hero and run optimization.")

    def _set_busy(self, busy: bool) -> None:
        self.optimize_btn.setEnabled(not busy and self.state.is_scored)
        self.hero_combo.setEnabled(not busy and self.state.is_scored)

    def _run(self) -> None:
        char = self.hero_combo.currentText()
        if not char:
            return

        self._set_busy(True)
        self.status_label.setText(f"Optimizing {char}…")

        self._worker = OptimizeWorker(
            char,
            self.state.df_items,
            self.state.df_hero,
            self.state.target_stats,
            self,
        )
        self._worker.status.connect(self.status_label.setText)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.start()

    def _on_failed(self, message: str) -> None:
        self._set_busy(False)
        self.status_label.setText(message)
        QMessageBox.warning(self, "Optimization", message)

    def _on_finished(self, result) -> None:
        self._set_busy(False)
        self.state.last_result = result
        combo_count = len(result.odf)
        self.status_label.setText(
            f"Done — {combo_count:,} combinations scored for {result.char}."
        )
        self.on_optimized(result)
