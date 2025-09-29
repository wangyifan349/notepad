#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List

from PyQt5 import QtCore, QtGui, QtWidgets

APP_NAME = "简单记事本"
CFG_FILENAME = Path.home() / ".simplenotepad_config.json"
FILE_FILTER = "文本文件 (*.txt);;所有文件 (*)"
DEFAULT_ENCODING = "utf-8"
FALLBACK_ENCODINGS = ["utf-8", "gb18030", "gbk", "latin-1"]
MAX_RECENT = 8


@dataclass
class AppConfig:
    theme: str = "dark"
    font_family: str = "Sans Serif"
    font_size: int = 14
    encoding: str = DEFAULT_ENCODING
    recent_files: List[str] = None

    def __post_init__(self):
        if self.recent_files is None:
            self.recent_files = []


def load_config() -> AppConfig:
    try:
        if CFG_FILENAME.exists():
            with CFG_FILENAME.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return AppConfig(
                theme=data.get("theme", "dark"),
                font_family=data.get("font_family", "Sans Serif"),
                font_size=int(data.get("font_size", 14)) if data.get("font_size") is not None else 14,
                encoding=data.get("encoding", DEFAULT_ENCODING),
                recent_files=data.get("recent_files", []) or [],
            )
    except Exception as exc:
        print("load_config error:", exc, file=sys.stderr)
    return AppConfig()


def save_config(cfg: AppConfig) -> None:
    try:
        s = asdict(cfg)
        with CFG_FILENAME.open("w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        print("save_config error:", exc, file=sys.stderr)
def dark_palette() -> QtGui.QPalette:
    p = QtGui.QPalette()
    p.setColor(QtGui.QPalette.Window, QtGui.QColor("#0f1115"))
    p.setColor(QtGui.QPalette.Base, QtGui.QColor("#0b0d10"))
    p.setColor(QtGui.QPalette.Text, QtGui.QColor("#d7e0ea"))
    p.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#d7e0ea"))
    p.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#4fc3f7"))
    return p
class NotepadMainWindow(QtWidgets.QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self._current_file: Optional[Path] = None
        self._is_modified: bool = False
        self._current_encoding: str = config.encoding
        self._init_ui()
        self._connect_actions()
        self._update_title()
        self._apply_config_to_widgets()

    def _init_ui(self) -> None:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

        self.resize(1000, 700)
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))

        self.text_edit = QtWidgets.QPlainTextEdit(self)
        self.text_edit.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
        self.setCentralWidget(self.text_edit)

        self.status = self.statusBar()
        self.status_label = QtWidgets.QLabel("")
        self.pos_label = QtWidgets.QLabel("")
        self.enc_label = QtWidgets.QLabel("")
        self.status.addPermanentWidget(self.enc_label)
        self.status.addPermanentWidget(self.pos_label)
        self.status.addPermanentWidget(self.status_label)

        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_context_menu()

        self.setAcceptDrops(True)

        if self.config.theme == "dark":
            QtWidgets.QApplication.setPalette(dark_palette())
    def _create_actions(self) -> None:
        self.action_new = QtWidgets.QAction("新建", self, shortcut=QtGui.QKeySequence.New, triggered=self.file_new)
        self.action_open = QtWidgets.QAction("打开...", self, shortcut=QtGui.QKeySequence.Open, triggered=self.file_open)
        self.action_save = QtWidgets.QAction("保存", self, shortcut=QtGui.QKeySequence.Save, triggered=self.file_save)
        self.action_save_as = QtWidgets.QAction("另存为...", self, shortcut=QtGui.QKeySequence("Ctrl+Shift+S"), triggered=self.file_save_as)
        self.action_exit = QtWidgets.QAction("退出", self, shortcut=QtGui.QKeySequence.Quit, triggered=self.close)
        self.action_undo = QtWidgets.QAction("撤销", self, shortcut=QtGui.QKeySequence.Undo, triggered=self.text_edit.undo)
        self.action_redo = QtWidgets.QAction("重做", self, shortcut=QtGui.QKeySequence.Redo, triggered=self.text_edit.redo)
        self.action_cut = QtWidgets.QAction("剪切", self, shortcut=QtGui.QKeySequence.Cut, triggered=self.text_edit.cut)
        self.action_copy = QtWidgets.QAction("复制", self, shortcut=QtGui.QKeySequence.Copy, triggered=self.text_edit.copy)
        self.action_paste = QtWidgets.QAction("粘贴", self, shortcut=QtGui.QKeySequence.Paste, triggered=self.text_edit.paste)
        self.action_select_all = QtWidgets.QAction("全选", self, shortcut=QtGui.QKeySequence.SelectAll, triggered=self.text_edit.selectAll)
        self.action_increase_font = QtWidgets.QAction("放大字体", self, shortcut=QtGui.QKeySequence.ZoomIn, triggered=self.increase_font_size)
        self.action_decrease_font = QtWidgets.QAction("缩小字体", self, shortcut=QtGui.QKeySequence.ZoomOut, triggered=self.decrease_font_size)
        self.action_choose_font = QtWidgets.QAction("字体设置...", self, triggered=self.choose_font_dialog)
        self.action_toggle_theme = QtWidgets.QAction("切换主题", self, triggered=self.toggle_theme)
        self.action_choose_encoding = QtWidgets.QAction("选择默认编码...", self, triggered=self.choose_encoding_dialog)
        self.action_clear_recent = QtWidgets.QAction("清除最近文件", self, triggered=self._clear_recent)
        self.action_about = QtWidgets.QAction("关于", self, triggered=self._show_about_dialog)
    def _create_menus(self) -> None:
        mb = self.menuBar()
        file_menu = mb.addMenu("文件")
        file_menu.addAction(self.action_new)
        file_menu.addAction(self.action_open)
        file_menu.addAction(self.action_save)
        file_menu.addAction(self.action_save_as)
        self.recent_menu = file_menu.addMenu("最近文件")
        self._rebuild_recent_menu()
        file_menu.addAction(self.action_clear_recent)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)

        edit_menu = mb.addMenu("编辑")
        edit_menu.addAction(self.action_undo)
        edit_menu.addAction(self.action_redo)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_cut)
        edit_menu.addAction(self.action_copy)
        edit_menu.addAction(self.action_paste)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_select_all)
        view_menu = mb.addMenu("查看")
        view_menu.addAction(self.action_increase_font)
        view_menu.addAction(self.action_decrease_font)
        view_menu.addAction(self.action_choose_font)
        view_menu.addAction(self.action_toggle_theme)
        view_menu.addAction(self.action_choose_encoding)
        help_menu = mb.addMenu("帮助")
        help_menu.addAction(self.action_about)
    def _create_toolbars(self) -> None:
        tb = self.addToolBar("主工具栏")
        tb.setMovable(False)
        tb.setIconSize(QtCore.QSize(18, 18))
        tb.addAction(self.action_new)
        tb.addAction(self.action_open)
        tb.addAction(self.action_save)
        tb.addSeparator()
        tb.addAction(self.action_undo)
        tb.addAction(self.action_redo)
        tb.addSeparator()
        tb.addAction(self.action_cut)
        tb.addAction(self.action_copy)
        tb.addAction(self.action_paste)
        tb.addSeparator()

        # 字体选择控件
        font_combo = QtWidgets.QFontComboBox(self)
        try:
            font_combo.setCurrentFont(QtGui.QFont(self.config.font_family))
        except Exception as exc:
            print("font_combo.setCurrentFont error:", exc, file=sys.stderr)
        font_combo.currentFontChanged.connect(self._on_font_family_changed)
        font_combo.setMaximumWidth(220)
        tb.addWidget(font_combo)
        size_combo = QtWidgets.QComboBox(self)
        size_combo.setEditable(True)
        for s in [10, 11, 12, 13, 14, 16, 18, 20, 22, 24]:
            size_combo.addItem(str(s))
        size_combo.setCurrentText(str(self.config.font_size))
        size_combo.setMaximumWidth(70)
        # 直接在变化时应用，不隐藏错误
        size_combo.activated.connect(lambda idx, sc=size_combo: self._on_font_size_changed(sc.currentText()))
        size_combo.lineEdit().editingFinished.connect(lambda sc=size_combo: self._on_font_size_changed(sc.currentText()))
        tb.addWidget(size_combo)
        self._font_combo = font_combo
        self._size_combo = size_combo
    def _create_context_menu(self) -> None:
        self.text_edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self._show_context_menu)
    def _show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.action_undo)
        menu.addAction(self.action_redo)
        menu.addSeparator()
        menu.addAction(self.action_cut)
        menu.addAction(self.action_copy)
        menu.addAction(self.action_paste)
        menu.addSeparator()
        menu.addAction(self.action_select_all)
        menu.exec_(self.text_edit.mapToGlobal(pos))
    def _connect_actions(self) -> None:
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.copyAvailable.connect(self._on_copy_available)
        self.text_edit.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.text_edit.modificationChanged.connect(self._on_modification_changed)
        self._on_copy_available(False)
        self._on_cursor_position_changed()
    # 最近文件
    def _rebuild_recent_menu(self) -> None:
        self.recent_menu.clear()
        if not self.config.recent_files:
            self.recent_menu.addAction(QtWidgets.QAction("（无）", self, enabled=False))
            return
        for path in self.config.recent_files[:MAX_RECENT]:
            act = QtWidgets.QAction(path, self)
            act.triggered.connect(lambda checked=False, p=path: self._open_recent(p))
            self.recent_menu.addAction(act)
    def _add_to_recent(self, p: Path) -> None:
        s = str(p)
        if s in self.config.recent_files:
            try:
                self.config.recent_files.remove(s)
            except ValueError:
                pass
        self.config.recent_files.insert(0, s)
        self.config.recent_files = self.config.recent_files[:MAX_RECENT]
        self._rebuild_recent_menu()
    def _open_recent(self, path_str: str) -> None:
        p = Path(path_str)
        if p.exists():
            if not self._maybe_save():
                return
            self._load_file_with_encoding(p, try_auto=True)

    def _clear_recent(self) -> None:
        self.config.recent_files = []
        self._rebuild_recent_menu()
        save_config(self.config)

    # 状态回调
    def _on_text_changed(self) -> None:
        modified = self.text_edit.document().isModified()
        if modified != self._is_modified:
            self._is_modified = modified
            self._update_title()
            self._update_status()

    def _on_modification_changed(self, changed: bool) -> None:
        self._is_modified = changed
        self._update_title()
        self._update_status()
    def _on_copy_available(self, available: bool) -> None:
        self.action_cut.setEnabled(available)
        self.action_copy.setEnabled(available)
    def _on_cursor_position_changed(self) -> None:
        cursor = self.text_edit.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.pos_label.setText(f"行 {line}, 列 {col}")
    def _update_title(self) -> None:
        name = self._current_file.name if self._current_file else "未命名"
        mark = "*" if self._is_modified else ""
        self.setWindowTitle(f"{name}{mark} — {APP_NAME}")
    def _update_status(self) -> None:
        path = str(self._current_file) if self._current_file else "未保存"
        mark = "已修改" if self._is_modified else "已保存"
        self.status_label.setText(f"{path} — {mark}")
        self.enc_label.setText(f"编码: {self._current_encoding}")
    # 文件读取（简化稳定版）：只尝试常用编码并返回第一个成功
    def _try_read_with_encodings(self, path: Path):
        last_exc = None
        for e in FALLBACK_ENCODINGS:
            try:
                with path.open("r", encoding=e, errors="strict") as f:
                    return f.read(), e
            except Exception as exc:
                last_exc = exc
        try:
            with path.open("r", encoding="latin-1", errors="replace") as f:
                return f.read(), "latin-1"
        except Exception as exc:
            print("_try_read_with_encodings final error:", exc, file=sys.stderr)
            raise last_exc or IOError("无法读取文件")
    def _load_file_with_encoding(self, path: Path, try_auto: bool = True) -> None:
        try:
            if try_auto:
                text, enc_used = self._try_read_with_encodings(path)
            else:
                with path.open("r", encoding=self.config.encoding, errors="strict") as f:
                    text = f.read()
                enc_used = self.config.encoding
        except Exception as exc:
            print("_load_file_with_encoding error:", exc, file=sys.stderr)
            QtWidgets.QMessageBox.critical(self, "错误", f"打开文件失败：\n{exc}")
            return
        self._current_file = path
        self._current_encoding = enc_used
        self.text_edit.setPlainText(text)
        self.text_edit.document().setModified(False)
        self._is_modified = False
        self._add_to_recent(path)
        self._update_title()
        self._update_status()

    def file_new(self) -> None:
        if not self._maybe_save():
            return
        self.text_edit.clear()
        self._current_file = None
        self._current_encoding = self.config.encoding
        self.text_edit.document().setModified(False)
        self._is_modified = False
        self._update_title()
        self._update_status()

    def file_open(self) -> None:
        if not self._maybe_save():
            return
        path_str, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开文件", str(Path.home()), FILE_FILTER)
        if not path_str:
            return
        path = Path(path_str)
        self._load_file_with_encoding(path, try_auto=True)
    def _write_file(self, path: Path, text: str, encoding: str) -> bool:
        try:
            with path.open("w", encoding=encoding, newline="\n", errors="strict") as f:
                f.write(text)
            return True
        except Exception as exc:
            print("_write_file primary error:", exc, file=sys.stderr)
            try:
                with path.open("w", encoding="utf-8", newline="\n", errors="replace") as f:
                    f.write(text)
                return True
            except Exception as exc2:
                print("_write_file fallback error:", exc2, file=sys.stderr)
                QtWidgets.QMessageBox.critical(self, "错误", f"保存文件失败：\n{exc2}")
                return False
    def file_save(self) -> bool:
        if self._current_file is None:
            return self.file_save_as()
        text = self.text_edit.toPlainText()
        enc = self._current_encoding or self.config.encoding
        success = self._write_file(self._current_file, text, enc)
        if success:
            self.text_edit.document().setModified(False)
            self._is_modified = False
            self._update_title()
            self._update_status()
            self._add_to_recent(self._current_file)
        return success
    def file_save_as(self) -> bool:
        path_str, _ = QtWidgets.QFileDialog.getSaveFileName(self, "另存为", str(Path.home() / "untitled.txt"), FILE_FILTER)
        if not path_str:
            return False
        path = Path(path_str)
        enc, ok = QtWidgets.QInputDialog.getItem(self, "选择编码", "编码：", FALLBACK_ENCODINGS, editable=True)
        if not ok or not enc:
            enc = self._current_encoding or self.config.encoding
        text = self.text_edit.toPlainText()
        success = self._write_file(path, text, enc)
        if success:
            self._current_file = path
            self._current_encoding = enc
            self.text_edit.document().setModified(False)
            self._is_modified = False
            self._add_to_recent(path)
            self._update_title()
            self._update_status()
        return success

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self._maybe_save():
            save_config(self.config)
            event.accept()
        else:
            event.ignore()

    def _show_about_dialog(self) -> None:
        QtWidgets.QMessageBox.information(self, "关于", f"{APP_NAME}\n稳定版修复若干崩溃点。")

    # 字体与主题
    def _apply_config_to_widgets(self) -> None:
        try:
            font = QtGui.QFont(self.config.font_family, max(6, int(self.config.font_size)))
            self.text_edit.setFont(font)
        except Exception as exc:
            print("_apply_config_to_widgets setFont error:", exc, file=sys.stderr)
        try:
            if hasattr(self, "_font_combo"):
                self._font_combo.blockSignals(True)
                self._font_combo.setCurrentFont(QtGui.QFont(self.config.font_family))
                self._font_combo.blockSignals(False)
            if hasattr(self, "_size_combo"):
                self._size_combo.blockSignals(True)
                self._size_combo.setCurrentText(str(self.config.font_size))
                self._size_combo.blockSignals(False)
        except Exception as exc:
            print("_apply_config_to_widgets combo error:", exc, file=sys.stderr)

    def increase_font_size(self) -> None:
        try:
            self.config.font_size = int(self.config.font_size) + 1
        except Exception as exc:
            print("increase_font_size parse error:", exc, file=sys.stderr)
            self.config.font_size = 14
        # 直接生效并保存
        self._apply_config_to_widgets()
        save_config(self.config)

    def decrease_font_size(self) -> None:
        try:
            v = int(self.config.font_size) - 1
        except Exception as exc:
            print("decrease_font_size parse error:", exc, file=sys.stderr)
            v = 13
        self.config.font_size = max(6, v)
        self._apply_config_to_widgets()
        save_config(self.config)

    def choose_font_dialog(self) -> None:
        font, ok = QtWidgets.QFontDialog.getFont(QtGui.QFont(self.config.font_family, self.config.font_size), self, "选择字体")

        if ok and font:
            try:
                self.config.font_family = font.family() or self.config.font_family
                pt = font.pointSize()
                if pt and pt > 0:
                    self.config.font_size = pt
            except Exception as exc:
                print("choose_font_dialog error:", exc, file=sys.stderr)
            self._apply_config_to_widgets()
            save_config(self.config)
    # 直接应用字体修改（不静默忽略异常）
    def _on_font_family_changed(self, qfont: QtGui.QFont) -> None:
        try:
            if qfont and qfont.family():
                self.config.font_family = qfont.family()
                self._apply_config_to_widgets()
                save_config(self.config)
        except Exception as exc:
            print("_on_font_family_changed error:", exc, file=sys.stderr)
    def _on_font_size_changed(self, txt: str) -> None:
        try:
            size = int(str(txt).strip())
            if size >= 6 and size <= 200:
                self.config.font_size = size
                self._apply_config_to_widgets()
                save_config(self.config)
        except Exception as exc:
            print("_on_font_size_changed error:", exc, file=sys.stderr)
    def toggle_theme(self) -> None:
        self.config.theme = "light" if self.config.theme == "dark" else "dark"
        try:
            if self.config.theme == "dark":
                QtWidgets.QApplication.setPalette(dark_palette())
            else:
                QtWidgets.QApplication.setPalette(QtGui.QPalette())
        except Exception as exc:
            print("toggle_theme error:", exc, file=sys.stderr)
        save_config(self.config)
    def choose_encoding_dialog(self) -> None:
        enc, ok = QtWidgets.QInputDialog.getItem(self, "选择默认编码", "默认编码：", FALLBACK_ENCODINGS, editable=True)
        if ok and enc:
            self.config.encoding = enc
            self._current_encoding = enc
            save_config(self.config)
            self._update_status()
    def _maybe_save(self) -> bool:
        if not self._is_modified:
            return True
        reply = QtWidgets.QMessageBox.question(
            self,
            "保存更改",
            "文档已修改，是否保存更改？",
            QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard | QtWidgets.QMessageBox.StandardButton.Cancel,
            QtWidgets.QMessageBox.StandardButton.Save,
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Save:
            return self.file_save()
        if reply == QtWidgets.QMessageBox.StandardButton.Discard:
            return True
        return False
    # 拖放
    def dragEnterEvent(self, e):
        try:
            if e.mimeData().hasUrls():
                e.acceptProposedAction()
        except Exception as exc:
            print("dragEnterEvent error:", exc, file=sys.stderr)
    def dropEvent(self, e):
        try:
            urls = e.mimeData().urls()
            if not urls:
                return
            path = Path(urls[0].toLocalFile())
            if path.exists():
                if not self._maybe_save():
                    return
                self._load_file_with_encoding(path, try_auto=True)
        except Exception as exc:
            print("dropEvent error:", exc, file=sys.stderr)
def main(argv: Optional[list] = None) -> int:
    if argv is None:
        argv = sys.argv
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    cfg = load_config()
    app = QtWidgets.QApplication(argv)
    try:
        app.setFont(QtGui.QFont(cfg.font_family, cfg.font_size))
    except Exception as exc:
        print("app.setFont error:", exc, file=sys.stderr)
    main_win = NotepadMainWindow(cfg)
    main_win.show()
    try:
        return app.exec_()
    except Exception as exc:
        print("app.exec_ error:", exc, file=sys.stderr)
        return 1
if __name__ == "__main__":
    raise SystemExit(main())
