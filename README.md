**Deutsch** | [English](README.en.md)

# 📈 Funktionsplotter – Python, Tkinter & Matplotlib 🚀

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)

Ein Desktop-Programm zum Zeichnen mathematischer Funktionen, Parameterkurven, Bode-Diagramme und 3D-Flächen – über
eine **Tkinter-Oberfläche** oder ohne Oberfläche mit einer Konfigurationsdatei im Textformat.

Entstanden im Python-Kurs an der Hochschule Hannover, Wintersemester 2025/26.

| 📉 Funktionen, Kurvenanalyse und Messwerte | 📶 Bode-Diagramm | 🏔️ 3D-Fläche und Höhenlinien |
|---|---|---|
| ![2D-Plot](docs/plot-2d.png) | ![Bode-Diagramm](docs/plot-bode.png) | ![3D-Plot](docs/plot-3d.png) |

---

## ✨ Funktionen

### 🖼️ Vier Plot-Modi
* **2D**: mehrere Funktionen f(x) gleichzeitig
* **🌀 Parametrisch**: Kurven x(t), y(t)
* **📶 Bode**: Betrag und Phase einer Übertragungsfunktion aus Zähler- und Nennerkoeffizienten
* **🏔️ 3D**: Flächen- und Höhenliniendiagramme von f(x, y)

### 🔬 Kurvenanalyse
* Numerische **1. und 2. Ableitung**
* Markierte **Nullstellen**, **Extrema** und **Wendepunkte** (Nullstellen durch lineare Interpolation verfeinert)

### 📊 Daten & Konfiguration
* **Messwerte**: x/y-Werte aus einer Textdatei laden und als Linie oder Punktwolke anzeigen
* **💾 Konfigurationen speichern und laden** als lesbare `Schlüssel: Wert`-Dateien
* **🎨 Darstellung**: Titel, Achsenbeschriftungen, Gitter, Legende sowie Farbe, Linienbreite und Linienstil pro
  Funktion

### 🖱️ Interaktive Oberfläche
* Cursor-Koordinaten live und Punkte **per Klick beschriften**
* Zoomen und Verschieben über die Matplotlib-Werkzeugleiste, **Export als Bild**

### 🔒 Sichere Auswertung von Ausdrücken
* Ausdrücke sehen nur eine **freigegebene Liste** von NumPy-Funktionen und Konstanten, keine Python-Built-ins;
  `^` funktioniert als Potenzoperator

---

## 🛠️ Starten

```bash
pip install numpy matplotlib
python app.py                                 # Oberfläche
python app.py examples/config_bode.txt        # ohne Oberfläche: direkt aus einer Konfigurationsdatei plotten
```

---

## 📝 Konfigurationsformat

```text
# Zwei Funktionen mit Kurvenanalyse und Messwerten
functions: [exp(-0.5*x)*sin(x), cos(x)]
xstart: 0
xend: 10
xstep: 0.1
find_roots: True
find_extrema: True
data_file: examples/messwerte.txt
title: Function Plot Example
```

Weitere Beispiele liegen in [`examples/`](examples/).

---

## 🏗️ Aufbau

| Datei | Aufgabe |
|-------|---------|
| `app.py` | Einstiegspunkt: Oberfläche, oder Modus ohne Oberfläche, wenn eine Konfigurationsdatei übergeben wird |
| `gui.py` | Tkinter-Oberfläche mit Bedienelementen für jeden Modus und eingebetteter Matplotlib-Zeichenfläche |
| `plotter.py` | Alle Plots und die numerische Analyse, unabhängig von der Oberfläche |
| `config_parser.py` | Liest `Schlüssel: Wert`-Dateien und wandelt die Werte in Wahrheitswerte, Zahlen und Listen um |
| `widgets.py` | Ein scrollbarer Rahmen für das lange Bedienfeld |

---

## 🧰 Technologien

Python · Tkinter · Matplotlib · NumPy
