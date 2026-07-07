#!/usr/bin/env python3
"""
PyQt UI Stub Generator.

Automatically generates .pyi stub files for IDE autocompletion from Qt Designer .ui files.
This allows dynamic UI loading with uic.loadUi() while maintaining full type hints and
autocompletion in IDEs like VS Code and PyCharm.

Usage:
    python generate_stubs.py dlg_settings.ui
    python generate_stubs.py --all  # Process all .ui files in current directory
    python generate_stubs.py *.ui --pyqt 6  # Process multiple files for PyQt6

Author: Generated for PyQt5/6 projects
License: MIT
"""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict

# Mapping of Qt widget classes to their import modules
QT_WIDGET_IMPORTS: Dict[str, str] = {
    "QDialog": "PyQt5.QtWidgets",
    "QMainWindow": "PyQt5.QtWidgets",
    "QWidget": "PyQt5.QtWidgets",
    "QPushButton": "PyQt5.QtWidgets",
    "QLineEdit": "PyQt5.QtWidgets",
    "QTextEdit": "PyQt5.QtWidgets",
    "QPlainTextEdit": "PyQt5.QtWidgets",
    "QLabel": "PyQt5.QtWidgets",
    "QCheckBox": "PyQt5.QtWidgets",
    "QRadioButton": "PyQt5.QtWidgets",
    "QComboBox": "PyQt5.QtWidgets",
    "QSpinBox": "PyQt5.QtWidgets",
    "QDoubleSpinBox": "PyQt5.QtWidgets",
    "QSlider": "PyQt5.QtWidgets",
    "QProgressBar": "PyQt5.QtWidgets",
    "QListWidget": "PyQt5.QtWidgets",
    "QTableWidget": "PyQt5.QtWidgets",
    "QTreeWidget": "PyQt5.QtWidgets",
    "QTabWidget": "PyQt5.QtWidgets",
    "QGroupBox": "PyQt5.QtWidgets",
    "QScrollArea": "PyQt5.QtWidgets",
    "QFrame": "PyQt5.QtWidgets",
    "QSplitter": "PyQt5.QtWidgets",
    "QDateEdit": "PyQt5.QtWidgets",
    "QTimeEdit": "PyQt5.QtWidgets",
    "QDateTimeEdit": "PyQt5.QtWidgets",
    "QCalendarWidget": "PyQt5.QtWidgets",
    "QDial": "PyQt5.QtWidgets",
    "QLCDNumber": "PyQt5.QtWidgets",
    "QToolButton": "PyQt5.QtWidgets",
    "QCommandLinkButton": "PyQt5.QtWidgets",
    "QFontComboBox": "PyQt5.QtWidgets",
}


def parse_ui_file(
    ui_path: Path,
) -> tuple[str, str, list[tuple[str, str]], dict[str, tuple[str, str]]]:
    """
    Parse a Qt Designer .ui file and extract widget information.

    This function reads the XML structure of a .ui file and extracts:
    - The base class of the main widget (QDialog, QMainWindow, etc.)
    - The class name defined in the UI
    - All named child widgets with their types
    - Custom widget definitions with their base classes and headers

    Args:
        ui_path: Path to the .ui file to parse.

    Returns:
        A tuple containing:
            - class_name (str): The name of the main widget class
            - base_class (str): The Qt base class (e.g., 'QDialog', 'QMainWindow')
            - widgets (list): List of (widget_name, widget_class) tuples for all child widgets
            - custom_widgets (dict): Dict mapping custom class names to (base_class, header) tuples

    Raises:
        ValueError: If no widget element is found in the .ui file.
        xml.etree.ElementTree.ParseError: If the .ui file is not valid XML.

    Example:
        >>> class_name, base_class, widgets, custom = parse_ui_file(Path("dialog.ui"))
        >>> print(class_name)
        'DlgSettings'
        >>> print(base_class)
        'QDialog'
        >>> print(widgets[0])
        ('btn_ok', 'QPushButton')
        >>> print(custom)
        {'CustomButton': ('QPushButton', 'widgets.custom_button')}
    """
    tree = ET.parse(ui_path)
    root = tree.getroot()

    # Find the base class (QDialog, QMainWindow, etc.)
    widget_elem = root.find("widget")
    if widget_elem is None:
        raise ValueError(f"No widget element found in {ui_path}")

    base_class = widget_elem.get("class", "QWidget")
    class_name = widget_elem.get("name", ui_path.stem.title().replace("_", ""))

    # Extract custom widget definitions
    custom_widgets: dict[str, tuple[str, str]] = {}
    customwidgets = root.find("customwidgets")
    if customwidgets is not None:
        for customwidget in customwidgets.findall("customwidget"):
            custom_class = customwidget.findtext("class")
            extends = customwidget.findtext("extends", "QWidget")
            header = customwidget.findtext("header", "")

            if custom_class:
                # Convert header path to module path (e.g., "widgets/button.h" -> "widgets.button")
                module = (
                    header.replace("/", ".")
                    .replace("\\", ".")
                    .replace(".h", "")
                    .replace(".py", "")
                )
                custom_widgets[custom_class] = (extends, module)

    # Extract all named widgets
    widgets = []
    for widget in root.iter("widget"):
        name = widget.get("name")
        widget_class = widget.get("class")

        if name and widget_class and name != class_name:
            widgets.append((name, widget_class))

    return class_name, base_class, widgets, custom_widgets


def generate_stub(
    ui_path: Path, output_path: Path | None = None, pyqt_version: int = 5
) -> None:
    """
    Generate a .pyi stub file from a Qt Designer .ui file.

    This function creates a Python stub file (.pyi) containing type hints for all widgets
    defined in a .ui file. The stub file enables full IDE autocompletion and type checking
    when using uic.loadUi() to dynamically load UI files at runtime.

    The generated stub includes:
    - Proper imports for all Qt widget classes used
    - Imports for custom widgets from their respective modules
    - Type-hinted class attributes for each named widget
    - A basic __init__ method signature

    Custom widgets are handled automatically:
    - If a custom widget is defined in the .ui file, its import path is extracted
    - If no import path is found, the widget falls back to its base class (extends)

    Args:
        ui_path: Path to the source .ui file to process.
        output_path: Optional path for the output .pyi file. If None, the stub will be
                    created in the same directory as the .ui file with the same name
                    but .pyi extension. Defaults to None.
        pyqt_version: PyQt version to use for imports (5 or 6). Determines whether to
                     import from PyQt5 or PyQt6 modules. Defaults to 5.

    Returns:
        None. The stub file is written to disk.

    Raises:
        ValueError: If the .ui file has invalid structure.
        OSError: If the output file cannot be written.

    Example:
        >>> generate_stub(Path("dlg_settings.ui"))
        ✓ Generated: dlg_settings.pyi

        >>> generate_stub(Path("main.ui"), Path("stubs/main.pyi"), pyqt_version=6)
        ✓ Generated: stubs/main.pyi
    """
    if output_path is None:
        output_path = ui_path.with_suffix(".pyi")

    class_name, base_class, widgets, custom_widgets = parse_ui_file(ui_path)

    # Determine the PyQt module prefix
    pyqt_module = f"PyQt{pyqt_version}"

    # Collect necessary imports
    qt_imports: Dict[str, set[str]] = {}  # PyQt imports
    custom_imports: Dict[str, set[str]] = {}  # Custom widget imports

    # Add base class import
    if base_class in QT_WIDGET_IMPORTS:
        module = QT_WIDGET_IMPORTS[base_class].replace("PyQt5", pyqt_module)
        qt_imports.setdefault(module, set()).add(base_class)

    # Process each widget
    for _, widget_class in widgets:
        # Check if it's a custom widget
        if widget_class in custom_widgets:
            extends, module = custom_widgets[widget_class]
            if module:
                # Import the custom widget from its module
                custom_imports.setdefault(module, set()).add(widget_class)
            else:
                # Fallback: use the base class it extends
                if extends in QT_WIDGET_IMPORTS:
                    qt_module = QT_WIDGET_IMPORTS[extends].replace("PyQt5", pyqt_module)
                    qt_imports.setdefault(qt_module, set()).add(extends)
        # Standard Qt widget
        elif widget_class in QT_WIDGET_IMPORTS:
            module = QT_WIDGET_IMPORTS[widget_class].replace("PyQt5", pyqt_module)
            qt_imports.setdefault(module, set()).add(widget_class)

    # Generate stub file content
    lines = [
        f'"""Type hints auto-generated from {ui_path.name}"""',
        "",
    ]

    # Add Qt imports (sorted)
    for module in sorted(qt_imports.keys()):
        classes = ", ".join(sorted(qt_imports[module]))
        lines.append(f"from {module} import {classes}")

    # Add custom widget imports (sorted)
    if custom_imports:
        if qt_imports:
            lines.append("")  # Blank line between Qt and custom imports
        for module in sorted(custom_imports.keys()):
            classes = ", ".join(sorted(custom_imports[module]))
            lines.append(f"from {module} import {classes}")

    lines.extend(
        [
            "",
            "",
            f"class {class_name}({base_class}):",
        ]
    )

    # Add widget attributes
    if widgets:
        for widget_name, widget_class in sorted(widgets):
            # Use the actual custom class or fallback to base class
            if widget_class in custom_widgets and not custom_widgets[widget_class][1]:
                # No module path: use base class
                widget_type = custom_widgets[widget_class][0]
            else:
                widget_type = widget_class
            lines.append(f"    {widget_name}: {widget_type}")
    else:
        lines.append("    pass")

    lines.extend(
        [
            "",
            "    def __init__(self, parent=None) -> None: ...",
            "",
        ]
    )

    # Write the file
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ Generated: {output_path}")


def main():
    """
    Main entry point for the stub generator CLI.

    Parses command-line arguments and processes .ui files to generate corresponding
    .pyi stub files. Supports single file processing, batch processing of all .ui
    files in a directory, and configuration of PyQt version and output location.

    Command-line arguments:
        files: Positional arguments specifying .ui files to process
        --all: Process all .ui files in the current directory
        --pyqt {5,6}: Specify PyQt version (default: 5)
        --output-dir: Specify output directory for generated stubs

    Exit codes:
        0: Success
        1: Error during processing (partial failures may occur)

    Examples:
        Process a single file:
            $ python generate_stubs.py dialog.ui

        Process all .ui files in current directory:
            $ python generate_stubs.py --all

        Process specific files for PyQt6:
            $ python generate_stubs.py main.ui settings.ui --pyqt 6

        Process all files to a specific output directory:
            $ python generate_stubs.py --all --output-dir ./stubs
    """
    parser = argparse.ArgumentParser(
        description="Generate .pyi stub files from Qt Designer .ui files for IDE autocompletion",
        epilog="Example: python generate_stubs.py --all --pyqt 6",
    )
    parser.add_argument(
        "files", nargs="*", help="UI files to process (e.g., dialog.ui main.ui)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all .ui files in the current directory",
    )
    parser.add_argument(
        "--pyqt",
        type=int,
        choices=[5, 6],
        default=5,
        help="PyQt version for imports (default: 5)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for stub files (default: same as source files)",
    )

    args = parser.parse_args()

    # Determine which files to process
    if args.all:
        ui_files = list(Path.cwd().glob("*.ui"))
    elif args.files:
        ui_files = [Path(f) for f in args.files]
    else:
        parser.print_help()
        return

    if not ui_files:
        print("No .ui files found")
        return

    # Generate stubs
    for ui_file in ui_files:
        try:
            output_path = None
            if args.output_dir:
                output_path = args.output_dir / ui_file.with_suffix(".pyi").name

            generate_stub(ui_file, output_path, args.pyqt)
        except Exception as e:
            print(f"✗ Error processing {ui_file}: {e}")


if __name__ == "__main__":
    main()
