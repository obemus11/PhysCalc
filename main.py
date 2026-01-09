import sys



import json

from datetime import datetime

from math import sin, radians, cos

from PyQt6.QtCore import Qt, QLocale

from PyQt6.QtWidgets import (

    QApplication,

    QWidget,

    QPushButton,

    QVBoxLayout,

    QHBoxLayout,

    QLineEdit,

    QComboBox,

    QStackedWidget,

    QTableWidget,

    QTableWidgetItem,

    QHeaderView,

    QMessageBox,

    QTextEdit

)

from PyQt6.QtGui import QIcon, QDoubleValidator

class HistoryFileManager:

    def __init__(self, filename="history.txt"):

        self.filename = filename

    def load_history(self):

        try:

            with open(self.filename, 'r', encoding='utf-8') as f:

                history = [json.loads(line) for line in f]

            return history

        except FileNotFoundError:

            return []

        except json.JSONDecodeError:

            return []

    def add_history_entry(self, section, formula, inputs, result):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = {

            "timestamp": timestamp,

            "section": section,

            "formula": formula,

            "inputs": inputs,

            "result": result

        }

        try:

            with open(self.filename, 'a', encoding='utf-8') as f:

                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        except Exception:

            pass

    def clear_history(self):

        try:

            with open(self.filename, 'w', encoding='utf-8') as f:

                f.write("")

            return True

        except Exception:

            return False

# Класс страницы меню

class MenuPage(QWidget):

    def __init__(self, stack):

        super().__init__()

        self.stack = stack

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        # Создание кнопок

        self.btn_convert = QPushButton("Конвертировать единицы измерения")

        self.btn_prefix = QPushButton("Приставки СИ")

        self.btn_formul = QPushButton("Формулы. Подставления в формулу")

        self.btn_const = QPushButton("Константы")

        self.btn_theory = QPushButton("Теория и подсказки")

        self.btn_history = QPushButton("История Конвентирования")

        self.btn_convert.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        self.btn_prefix.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        self.btn_formul.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        self.btn_const.clicked.connect(lambda: self.stack.setCurrentIndex(4))

        self.btn_theory.clicked.connect(lambda: self.stack.setCurrentIndex(5))

        self.btn_history.clicked.connect(lambda: self.stack.setCurrentIndex(6))

        self.btn_convert.setMinimumHeight(50)

        self.btn_prefix.setMinimumHeight(50)

        self.btn_formul.setMinimumHeight(50)

        self.btn_const.setMinimumHeight(50)

        self.btn_theory.setMinimumHeight(50)

        self.btn_history.setMinimumHeight(50)

        layout.addWidget(self.btn_convert)

        layout.addWidget(self.btn_prefix)

        layout.addWidget(self.btn_formul)

        layout.addWidget(self.btn_const)

        layout.addWidget(self.btn_theory)

        layout.addWidget(self.btn_history)

        self.setLayout(layout)

# Класс страницы конвертации единиц

class ConvertPage(QWidget):

    def __init__(self, stack):

        super().__init__()

        self.stack = stack

        self.units = {

            "Масса": {"мг": 0.001, "г": 1, "кг": 1000, "т": 1_000_000},

            "Длина": {"мм": 0.001, "см": 0.01, "дм": 0.1, "м": 1, "км": 1000},

            "Температура": {"°C": "C", "K": "K", "°F": "F"},

            "Скорость": {"м/с": 1, "км/ч": 1000 / 3600},

            "Время": {"с": 1, "мин": 60, "ч": 3600},

            "Площадь": {"мм²": 0.000001, "см²": 0.0001, "м²": 1, "км²": 1_000_000},

            "Объем": {"мл": 0.001, "л": 1, "м³": 1000}

        }

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        gorlayout = QHBoxLayout()

        self.type_box = QComboBox()

        self.type_box.addItems(self.units.keys())

        self.type_box.currentTextChanged.connect(self.update_units)

        self.from_unit = QComboBox()

        self.to_unit = QComboBox()

        self.update_units(self.type_box.currentText())

        self.fromline = QLineEdit()

        self.fromline.setPlaceholderText("Введите значение")

        validator = QDoubleValidator(-1e20, 1e20, 10)

        validator.setLocale(QLocale(QLocale.Language.AnyLanguage, QLocale.Country.AnyCountry))

        self.fromline.setValidator(validator)

        self.toline = QLineEdit()

        self.toline.setReadOnly(True)

        self.conv_button = QPushButton("Конвертировать")

        self.button1 = QPushButton("Из")

        self.button2 = QPushButton("В")

        self.conv_button.clicked.connect(self.convert_units)

        gorlayout.addWidget(self.button1)

        gorlayout.addWidget(self.type_box)

        gorlayout.addWidget(self.from_unit)

        gorlayout.addWidget(self.fromline)

        gorlayout.addWidget(self.conv_button)

        gorlayout.addWidget(self.to_unit)

        gorlayout.addWidget(self.toline)

        gorlayout.addWidget(self.button2)

        layout.addStretch()

        layout.addLayout(gorlayout)

        layout.addStretch()

        back_btn = QPushButton("Назад")

        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(back_btn)

        self.setLayout(layout)

    def update_units(self, quantity_type):

        self.from_unit.clear()

        self.to_unit.clear()

        for unit in self.units[quantity_type].keys():

            self.from_unit.addItem(unit)

            self.to_unit.addItem(unit)

    def convert_units(self):

        try:

            # Заменяем запятую на точку для корректного преобразования в float

            value_text = self.fromline.text().replace(",", ".")

            value = float(value_text)

        except ValueError:

            self.toline.setText("Некорректный ввод")

            return

        from_u = self.from_unit.currentText()

        to_u = self.to_unit.currentText()

        quantity_type = self.type_box.currentText()

        try:

            if quantity_type == "Температура":

                result = self.convert_temperature(value, from_u, to_u)

            else:

                result = value * (self.units[quantity_type][from_u] / self.units[quantity_type][to_u])

            # Форматирование результата

            if abs(result) >= 1e5 or (abs(result) > 0 and abs(result) < 1e-3):

                formatted_res = "{:.1e}".format(result)

            else:

                formatted_res = "{:.4f}".format(result).rstrip('0').rstrip('.')

                if not formatted_res:

                    formatted_res = "0"

            self.toline.setText(formatted_res)

        except ZeroDivisionError:

            self.toline.setText("Деление на ноль")

        except Exception:

            self.toline.setText("Ошибка")

    def convert_temperature(self, val, from_u, to_u):

        if from_u == "K":

            val -= 273.15

        elif from_u == "°F":

            val = (val - 32) * 5 / 9

        if to_u == "K":

            return val + 273.15

        elif to_u == "°F":

            return val * 9 / 5 + 32

        else:

            return val

# Класс страницы приставок СИ

class PrefixPage(QWidget):

    def __init__(self, stack):

        super().__init__()

        self.stack = stack

        self.prefixes = {

            "тера (Т) 10¹²": 10 ** 12,

            "гига (Г) 10⁹": 10 ** 9,

            "мега (М) 10⁶": 10 ** 6,

            "кило (к) 10³": 10 ** 3,

            "гекто (г) 10²": 10 ** 2,

            "дека (да) 10¹": 10 ** 1,

            "(база) 10⁰": 1,

            "деци (д) 10⁻¹": 10 ** -1,

            "санти (с) 10⁻²": 10 ** -2,

            "милли (м) 10⁻³": 10 ** -3,

            "микро (мк) 10⁻⁶": 10 ** -6,

            "нано (н) 10⁻⁹": 10 ** -9,

            "пико (п) 10⁻¹²": 10 ** -12,

        }

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        gorlayout = QHBoxLayout()

        self.button1 = QPushButton("Из")

        self.from_prefix = QComboBox()

        self.from_prefix.addItems(self.prefixes.keys())

        # Замена QDoubleSpinBox на QLineEdit для ввода

        self.fromline = QLineEdit()

        self.fromline.setPlaceholderText("Введите значение")

        # ДОБАВЛЕНА ВАЛИДАЦИЯ ВВОДА

        validator = QDoubleValidator(-1e20, 1e20, 10)

        validator.setLocale(QLocale(QLocale.Language.AnyLanguage, QLocale.Country.AnyCountry))

        self.fromline.setValidator(validator)

        self.conv_button = QPushButton("Конвертировать")

        self.conv_button.clicked.connect(self.convert_prefixes)

        self.to_prefix = QComboBox()

        self.to_prefix.addItems(self.prefixes.keys())

        self.toline = QLineEdit()

        self.toline.setReadOnly(True)

        self.button2 = QPushButton("В")

        gorlayout.addWidget(self.button1)

        gorlayout.addWidget(self.from_prefix)

        gorlayout.addWidget(self.fromline)

        gorlayout.addWidget(self.conv_button)

        gorlayout.addWidget(self.to_prefix)

        gorlayout.addWidget(self.toline)

        gorlayout.addWidget(self.button2)

        layout.addStretch()

        layout.addLayout(gorlayout)

        layout.addStretch()

        back_btn = QPushButton("Назад")

        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(back_btn)

        self.setLayout(layout)

    def convert_prefixes(self):

        try:

            # Заменяем запятую на точку для корректного преобразования в float

            value_text = self.fromline.text().replace(",", ".")

            value = float(value_text)

        except ValueError:

            self.toline.setText("Некорректный ввод")

            return

        from_factor = self.prefixes[self.from_prefix.currentText()]

        to_factor = self.prefixes[self.to_prefix.currentText()]

        result = value * (from_factor / to_factor)

        # Форматирование результата

        if abs(result) >= 1e5 or (abs(result) > 0 and abs(result) < 1e-3):

            formatted_res = "{:.1e}".format(result)

        else:

            formatted_res = "{:.4f}".format(result).rstrip('0').rstrip('.')

            if not formatted_res:

                formatted_res = "0"

        self.toline.setText(formatted_res)

# Класс страницы формул

class FormulPage(QWidget):

    def __init__(self, stack: QStackedWidget, history_manager: HistoryFileManager):

        super().__init__()

        self.stack = stack

        self.history_manager = history_manager

        self.inputs = []

        self.initUI()

    def initUI(self):

        main_layout = QVBoxLayout(self)

        main_layout.setSpacing(12)

        self.g = 10

        self.G = 6.67430e-11

        self.c = 2.99792458e8

        self.formulas = {

            "Кинематика": {

                "v = s / t": (["s (м)", "t (с)"], lambda s, t: s / t, "м/с"),

                "s = v * t": (["v (м/с)", "t (с)"], lambda v, t: v * t, "м"),

                "t = s / v": (["s (м)", "v (м/с)"], lambda s, v: s / v, "с"),

                "---": ([], lambda: None, ""),

                "v = v₀ + a * t": (["v₀ (м/с)", "a (м/с²)", "t (с)"], lambda v0, a, t: v0 + a * t, "м/с"),

                "s = v₀ * t + 0.5 * a * t²": (

                    ["v₀ (м/с)", "a (м/с²)", "t (с)"], lambda v0, a, t: v0 * t + 0.5 * a * t ** 2, "м"),

                "v = √(v₀² + 2 * a * s)": (

                    ["v₀ (м/с)", "a (м/с²)", "s (м)"], lambda v0, a, s: (v0 ** 2 + 2 * a * s) ** 0.5, "м/с")

            },

            "Динамика": {

                "F = m * a": (["m (кг)", "a (м/с²)"], lambda m, a: m * a, "Н"),

                "m = F / a": (["F (Н)", "a (м/с²)"], lambda F, a: F / a, "кг"),

                "a = F / m": (["F (Н)", "m (кг)"], lambda F, m: F / m, "м/с²"),

                "---": ([], lambda: None, ""),

                "P = F / S": (["F (Н)", "S (м²)"], lambda F, S: F / S, "Па")

            },

            "Механическая энергия": {

                "Eₖ = 0.5 * m * v²": (["m (кг)", "v (м/с)"], lambda m, v: 0.5 * m * v ** 2, "Дж"),

                "Eₚ = m * g * h": (["m (кг)", "h (м)"], lambda m, h: m * self.g * h, "Дж"),

                "---": ([], lambda: None, ""),

                "W = F * s": (["F (Н)", "s (м)"], lambda F, s: F * s, "Дж")

            },

            "Импульс и Закон сохранения": {

                "p = m * v": (["m (кг)", "v (м/с)"], lambda m, v: m * v, "кг·м/с"),

                "m = p / v": (["p (кг·м/с)", "v (м/с)"], lambda p, v: p / v, "кг"),

                "v = p / m": (["p (кг·м/с)", "m (кг)"], lambda p, m: p / m, "м/с"),

                "---": ([], lambda: None, ""),

                "v₂' = (m₁*v₁ + m₂*v₂ - m₁*v₁') / m₂":

                    (["m₁ (кг)", "v₁ (м/с)", "m₂ (кг)", "v₂ (м/с)", "v₁' (м/с)"],

                     lambda m1, v1, m2, v2, v1_: (m1 * v1 + m2 * v2 - m1 * v1_) / m2, "м/с")

            },

            "Давление": {

                "p = F / S": (["F (Н)", "S (м²)"], lambda F, S: F / S, "Па"),

                "F = p * S": (["p (Па)", "S (м²)"], lambda p, S: p * S, "Н"),

                "S = F / p": (["F (Н)", "p (Па)"], lambda F, p: F / p, "м²")

            },

            "Работа и Мощность": {

                "A = F * s": (["F (Н)", "s (м)"], lambda F, s: F * s, "Дж"),

                "P = A / t": (["A (Дж)", "t (с)"], lambda A, t: A / t, "Вт"),

                "A = P * t": (["P (Вт)", "t (с)"], lambda P, t: P * t, "Дж"),

                "t = A / P": (["A (Дж)", "P (Вт)"], lambda A, P: A / P, "с")

            },

            "Электричество": {

                "I = U / R": (["U (В)", "R (Ом)"], lambda U, R: U / R, "А"),

                "U = I * R": (["I (А)", "R (Ом)"], lambda I, R: I * R, "В"),

                "R = U / I": (["U (В)", "I (А)"], lambda U, I: U / I, "Ом"),

                "---": ([], lambda: None, ""),

                "P = U * I": (["U (В)", "I (А)"], lambda U, I: U * I, "Вт"),

                "Q = I * t": (["I (А)", "t (с)"], lambda I, t: I * t, "Кл")

            },

            "Магнетизм": {

                "F = B * I * L * sin(θ)":

                    (

                        ["B (Тл)", "I (А)", "L (м)", "θ (градусы)"],

                        lambda B, I, L, theta: B * I * L * sin(radians(theta)),

                        "Н"),

                "B = F / (I * L * sin(θ))":

                    (["F (Н)", "I (А)", "L (м)", "θ (градусы)"],

                     lambda F, I, L, theta: F / (I * L * sin(radians(theta))), "Тл")

            },

            "Волны и Звук": {

                "v = λ * f": (["λ (м)", "f (Гц)"], lambda l, f: l * f, "м/с"),

                "f = v / λ": (["v (м/с)", "λ (м)"], lambda v, l: v / l, "Гц"),

                "λ = v / f": (["v (м/с)", "f (Гц)"], lambda v, f: v / f, "м")

            },

            "Оптика": {

                "dᵢ = 1 / (1/f - 1/dₒ)": (["f (м)", "dₒ (м)"], lambda f, d_o: 1 / (1 / f - 1 / d_o), "м"),

                "n = c / v": (["v (м/с)"], lambda v: self.c / v, "ед. изм.")

            },

            "Термодинамика": {

                "Q = m * c * ΔT": (["m (кг)", "c (Дж/кг·°C)", "ΔT (°C)"], lambda m, c, dT: m * c * dT, "Дж"),

                "W = p * ΔV": (["p (Па)", "ΔV (м³)"], lambda p, dV: p * dV, "Дж"),

                "ΔU = Q - W": (["Q (Дж)", "W (Дж)"], lambda Q, W: Q - W, "Дж")

            },

            "Гравитация": {

                "F = G * m₁ * m₂ / r²": (

                    ["m₁ (кг)", "m₂ (кг)", "r (м)"], lambda m1, m2, r: self.G * m1 * m2 / r ** 2, "Н"),

                "g = G * M / R²": (["M (кг)", "R (м)"], lambda M, R: self.G * M / R ** 2, "м/с²"),

                "U = -G * m₁ * m₂ / r": (["m₁ (кг)", "m₂ (кг)", "r (м)"], lambda m1, m2, r: -self.G * m1 * m2 / r, "Дж")

            }

        }

        self.section_btn = QPushButton("Выбрать раздел физики")

        main_layout.addWidget(self.section_btn)

        self.section_box = QComboBox()

        self.section_box.addItems(self.formulas.keys())

        self.section_box.currentTextChanged.connect(self.update_find)

        main_layout.addWidget(self.section_box)

        self.formula_btn = QPushButton("Выбрать формулу (величина, которую хотите найти)")

        main_layout.addWidget(self.formula_btn)

        self.formula_box = QComboBox()

        self.formula_box.currentIndexChanged.connect(self.update_inputs)

        main_layout.addWidget(self.formula_box)

        self.inputs_layout = QVBoxLayout()

        main_layout.addLayout(self.inputs_layout)

        self.calc_btn = QPushButton("Рассчитать")

        self.calc_btn.clicked.connect(self.calculate)

        main_layout.addWidget(self.calc_btn)

        self.result = QLineEdit()

        self.result.setReadOnly(True)

        main_layout.addWidget(self.result)

        back_btn = QPushButton("Назад")

        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        main_layout.addWidget(back_btn)

        self.update_find()

    def update_find(self):

        self.formula_box.blockSignals(True)

        self.formula_box.clear()

        self.formula_box.addItems(

            self.formulas[self.section_box.currentText()].keys()

        )

        self.formula_box.blockSignals(False)

        self.update_inputs()

    def update_inputs(self):

        while self.inputs_layout.count():

            item = self.inputs_layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

        self.inputs.clear()

        current_formula = self.formula_box.currentText()

        if not current_formula:

            self.result.clear()

            return

        labels, _, _ = self.formulas[

            self.section_box.currentText()

        ][current_formula]

        # Валидатор для всех полей ввода формул

        validator = QDoubleValidator(-1e20, 1e20, 10)

        validator.setLocale(QLocale(QLocale.Language.AnyLanguage, QLocale.Country.AnyCountry))

        for text in labels:

            line_edit = QLineEdit()

            line_edit.setPlaceholderText(text)

            line_edit.setValidator(validator)  # Применяем валидатор

            self.inputs_layout.addWidget(line_edit)

            self.inputs.append(line_edit)

        self.result.clear()

    def calculate(self):

        try:

            values = []

            for le in self.inputs:

                # Заменяем запятую на точку для корректного преобразования в float

                text = le.text().replace(",", ".")

                if not text:

                    # Если поле пустое, считаем 0.0

                    values.append(0.0)

                else:

                    values.append(float(text))

            section = self.section_box.currentText()

            formula_name = self.formula_box.currentText()

            labels, func, unit = self.formulas[section][formula_name]

            res = func(*values)

            if res is None:

                self.result.clear()

                return

            if abs(res) >= 1e5 or (abs(res) > 0 and abs(res) < 1e-3):

                formatted_res = "{:.1e}".format(res)

            else:

                formatted_res = "{:.4f}".format(res).rstrip('0').rstrip('.')

                if not formatted_res:

                    formatted_res = "0"

            final_result_str = f"{formatted_res} {unit}"

            self.result.setText(final_result_str)

            input_data = [(labels[i], values[i]) for i in range(len(labels))]

            self.history_manager.add_history_entry(section, formula_name, input_data, final_result_str)

        except ValueError:

            self.result.setText("Некорректный ввод (не число)")

        except ZeroDivisionError:

            self.result.setText("Деление на ноль")

        except Exception as e:

            self.result.setText(f"Неизвестная ошибка: {type(e).__name__}")

# Класс страницы констант

class ConstantPage(QWidget):

    def __init__(self, stack):

        super().__init__()

        self.stack = stack

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        layout.addStretch()

        self.constants_info = QLineEdit()

        self.constants_info.setReadOnly(True)

        self.constants_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.constants_info.setMinimumHeight(60)

        font = self.constants_info.font()

        font.setPointSize(12)

        self.constants_info.setFont(font)

        layout.addWidget(self.constants_info)

        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()

        self.constants_box = QComboBox()

        self.constants_box.addItems([

            "Ускорение свободного падения",

            "Скорость света",

            "Заряд электрона",

            "Постоянная Планка",

            "Постоянная Больцмана"

        ])

        self.constants_box.setMinimumHeight(40)

        font_box = self.constants_box.font()

        font_box.setPointSize(11)

        self.constants_box.setFont(font_box)

        buttons_layout.addWidget(self.constants_box)

        self.show_button = QPushButton("Показать")

        self.show_button.setMinimumHeight(40)

        self.show_button.clicked.connect(self.show_constant)

        buttons_layout.addWidget(self.show_button)

        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        layout.addStretch()

        back_btn = QPushButton("Назад")

        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(back_btn)

        self.setLayout(layout)

    def show_constant(self):

        constants_data = {

            "Ускорение свободного падения": ("g", "9.81 ≈ 10.0", "м/с²"),

            "Скорость света": ("c", "3.00 × 10⁸", "м/с"),

            "Заряд электрона": ("e", "1.602 × 10⁻¹⁹", "Кл"),

            "Постоянная Планка": ("h", "6.626 × 10⁻³⁴", "Дж·с"),

            "Постоянная Больцмана": ("k", "1.381 × 10⁻²³", "Дж/К")

        }

        selected = self.constants_box.currentText()

        if selected in constants_data:

            symbol, value, unit = constants_data[selected]

            info_text = f"Название: {selected} | Символ: {symbol} | Значение: {value} | Единицы: {unit}"

            self.constants_info.setText(info_text)

# Класс страницы теории и подсказок

class TheoryPage(QWidget):

    def __init__(self, stack):

        super().__init__()

        self.stack = stack

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        layout.addStretch()

        self.theory_info = QTextEdit()

        self.theory_info.setReadOnly(True)

        self.theory_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.theory_info.setMinimumHeight(100)

        self.theory_info.setMaximumHeight(200)

        self.theory_info.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        font = self.theory_info.font()

        font.setPointSize(12)

        self.theory_info.setFont(font)

        layout.addWidget(self.theory_info)

        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()

        self.formulas_box = QComboBox()

        self.formulas_box.addItems([

            "Скорость",

            "Ускорение",

            "Равномерное движение",

            "Равноускоренное движение",

            "Сила",

            "Вес тела",

            "Сила трения",

            "Давление",

            "Гидростатическое давление",

            "Количество теплоты",

            "Плавление/кристаллизация",

            "Парообразование/конденсация",

            "Уравнение теплового баланса",

            "Закон Ома",

            "Мощность тока",

            "Работа тока",

            "Сопротивление проводника",

            "Закон Джоуля-Ленца",

            "Закон отражения",

            "Закон преломления",

            "Фокусное расстояние",

            "Работа",

            "Мощность",

            "Потенциальная энергия",

            "Кинетическая энергия"

        ])

        self.formulas_box.setMinimumHeight(40)

        font_box = self.formulas_box.font()

        font_box.setPointSize(11)

        self.formulas_box.setFont(font_box)

        buttons_layout.addWidget(self.formulas_box)

        self.show_button = QPushButton("Показать")

        self.show_button.setMinimumHeight(40)

        self.show_button.clicked.connect(self.show_formula)

        buttons_layout.addWidget(self.show_button)

        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        layout.addStretch()

        back_btn = QPushButton("Назад")

        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(back_btn)

        self.setLayout(layout)

    def show_formula(self):

        formulas_data = {

            "Скорость": ("v = S / t", "Скорость равна отношению пройденного пути к времени движения", "м/с"),

            "Ускорение": ("a = (v - v₀) / t", "Ускорение равно отношению изменения скорости к времени", "м/с²"),

            "Равномерное движение": ("S = vt", "Путь при равномерном движении равен произведению скорости на время", "м"),

            "Равноускоренное движение": ("S = v₀t + (at²) / 2", "Путь при равноускоренном движении зависит от начальной скорости, ускорения и времени", "м"),

            "Сила": ("F = ma", "Сила равна произведению массы на ускорение", "Н"),

            "Вес тела": ("P = mg", "Вес тела равен произведению массы на ускорение свободного падения", "Н"),

            "Сила трения": ("F_тр = μN", "Сила трения равна произведению коэффициента трения на силу нормальной реакции опоры", "Н"),

            "Давление": ("p = F / S", "Давление равно отношению силы к площади поверхности", "Па"),

            "Гидростатическое давление": ("p = ρgh", "Гидростатическое давление зависит от плотности жидкости, ускорения свободного падения и глубины", "Па"),

            "Количество теплоты": ("Q = cmΔt", "Количество теплоты равно произведению удельной теплоемкости, массы и изменения температуры", "Дж"),

            "Плавление/кристаллизация": ("Q = λm", "Количество теплоты при плавлении или кристаллизации равно произведению удельной теплоты плавления на массу", "Дж"),

            "Парообразование/конденсация": ("Q = Lm", "Количество теплоты при парообразовании или конденсации равно произведению удельной теплоты парообразования на массу", "Дж"),

            "Уравнение теплового баланса": ("Q_получ = Q_отдано", "Количество теплоты, полученное одним телом, равно количеству теплоты, отданному другим телом", "Дж"),

            "Закон Ома": ("I = U / R", "Сила тока равна отношению напряжения к сопротивлению", "А"),

            "Мощность тока": ("P = IU", "Мощность тока равна произведению силы тока на напряжение", "Вт"),

            "Работа тока": ("A = UIt", "Работа тока равна произведению напряжения, силы тока и времени", "Дж"),

            "Сопротивление проводника": ("R = ρl / S", "Сопротивление проводника зависит от удельного сопротивления, длины и площади поперечного сечения", "Ом"),

            "Закон Джоуля-Ленца": ("Q = I²Rt", "Количество теплоты, выделяемое проводником, равно произведению квадрата силы тока, сопротивления и времени", "Дж"),

            "Закон отражения": ("угол падения = угол отражения", "Угол падения луча равен углу его отражения от поверхности", "градусы"),

            "Закон преломления": ("n₁ sin α = n₂ sin β", "Произведение показателя преломления первой среды на синус угла падения равно произведению показателя преломления второй среды на синус угла преломления", "безразмерная величина"),

            "Фокусное расстояние": ("1/f = 1/d + 1/F", "Обратное фокусное расстояние равно сумме обратных расстояний от предмета и изображения до линзы", "м"),

            "Работа": ("A = F · S · cos α", "Работа равна произведению силы, перемещения и косинуса угла между ними", "Дж"),

            "Мощность": ("P = A / t", "Мощность равна отношению работы к времени", "Вт"),

            "Потенциальная энергия": ("E_p = mgh", "Потенциальная энергия тела в поле тяжести равна произведению массы, ускорения свободного падения и высоты", "Дж"),

            "Кинетическая энергия": ("E_k = mv² / 2", "Кинетическая энергия равна половине произведения массы на квадрат скорости", "Дж")

        }

        selected = self.formulas_box.currentText()

        if selected in formulas_data:

            formula, explanation, unit = formulas_data[selected]

            from PyQt6.QtGui import QTextCursor

            info_text = f"Название: {selected}\n\nФормула: {formula}\n\nОбъяснение: {explanation}\n\nЕдиницы измерения: {unit}"

            self.theory_info.setPlainText(info_text)

            cursor = self.theory_info.textCursor()

            cursor.movePosition(QTextCursor.MoveOperation.Start)

            self.theory_info.setTextCursor(cursor)

# Класс страницы истории

class HistoryPage(QWidget):

    def __init__(self, stack, history_manager: HistoryFileManager):

        super().__init__()

        self.stack = stack

        self.history_manager = history_manager

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        self.table = QTableWidget()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels(["Время", "Формула", "Входные данные", "Результат"])

        # ИСПРАВЛЕНИЕ: QHeaderView.ResizeToContents заменено на QHeaderView.ResizeMode.ResizeToContents

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        self.btn_refresh = QPushButton("Обновить")

        self.btn_clear = QPushButton("Очистить историю")

        self.btn_refresh.clicked.connect(self.load_history)

        self.btn_clear.clicked.connect(self.clear_history)

        btn_layout.addWidget(self.btn_refresh)

        btn_layout.addWidget(self.btn_clear)

        layout.addLayout(btn_layout)

        back_btn = QPushButton("Назад")

        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(back_btn)

        self.setLayout(layout)

        self.load_history()

    def load_history(self):

        history = self.history_manager.load_history()

        self.table.setRowCount(len(history))

        for row_num, entry in enumerate(history):

            # Форматируем входные данные для отображения

            inputs_str = "; ".join([f"{label.split(' ')[0]}={value}" for label, value in entry["inputs"]])

            row_data = [

                entry["timestamp"],

                f"{entry['section']}: {entry['formula']}",

                inputs_str,

                entry["result"]

            ]

            for col_num, data in enumerate(row_data):

                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def clear_history(self):

        reply = QMessageBox.question(self, 'Очистка истории',

                                     "Вы уверены, что хотите полностью очистить историю расчетов?",

                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,

                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:

            self.history_manager.clear_history()

            self.load_history()

# Класс главного окна

class Example(QWidget):

    def __init__(self):

        super().__init__()

        self.history_manager = HistoryFileManager()

        self.setGeometry(560, 240, 400, 400)

        self.setWindowTitle("PhysCalc")

        self.setWindowIcon(QIcon(""))

        self.initUI()

    def initUI(self):

        main_layout = QVBoxLayout()

        self.stack = QStackedWidget()

        self.setStyleSheet("""

            QPushButton {

                background-color: #2b2d42;

                color: #edf2f4;

                padding: 10px 18px;

                border-radius: 8px;

                border: none;

                font-size: 15px;

                font-weight: 500;

            }

            QPushButton:hover {

               	background-color: #3c3f58;

            }

            QPushButton:pressed {

                background-color: #1f2132;

            }

            QScrollBar:vertical {

                width: 0px;

                background: transparent;

            }

        """)

        # создаём страницы

        self.menu_page = MenuPage(self.stack)

        self.conv_page = ConvertPage(self.stack)

        self.pref_page = PrefixPage(self.stack)

        self.form_page = FormulPage(self.stack, self.history_manager)

        self.const_page = ConstantPage(self.stack)

        self.theory_page = TheoryPage(self.stack)

        self.history_page = HistoryPage(self.stack, self.history_manager)

        # добавляем страницы в stack

        self.stack.addWidget(self.menu_page)

        self.stack.addWidget(self.conv_page)

        self.stack.addWidget(self.pref_page)

        self.stack.addWidget(self.form_page)

        self.stack.addWidget(self.const_page)

        self.stack.addWidget(self.theory_page)

        self.stack.addWidget(self.history_page)

        # добавляем stack в главный layout

        main_layout.addWidget(self.stack)

        self.setLayout(main_layout)

if __name__ == '__main__':

    app = QApplication(sys.argv)

    ex = Example()

    ex.show()

    sys.exit(app.exec())