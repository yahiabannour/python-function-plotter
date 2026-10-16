[Deutsch](README.md) | **English**

# 📈 Function Plotter – Python, Tkinter & Matplotlib 🚀

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)

A desktop program for plotting mathematical functions, parametric curves, Bode diagrams and 3D surfaces – through
a **Tkinter GUI** or without a GUI from a plain-text configuration file.

Built for the Python course at Hochschule Hannover, winter semester 2025/26.

| 📉 Functions, curve analysis and measured data | 📶 Bode diagram | 🏔️ 3D surface and contour lines |
|---|---|---|
| ![2D plot](docs/plot-2d.png) | ![Bode diagram](docs/plot-bode.png) | ![3D plot](docs/plot-3d.png) |

---

## ✨ Features

### 🖼️ Four plot modes
* **2D**: several functions f(x) at once
* **🌀 Parametric**: curves x(t), y(t)
* **📶 Bode**: magnitude and phase of a transfer function from numerator and denominator coefficients
* **🏔️ 3D**: surface and contour plots of f(x, y)

### 🔬 Curve analysis
* Numerical **1st and 2nd derivatives**
* Marked **roots**, **extrema** and **inflection points** (roots refined by linear interpolation)

### 📊 Data & configuration
* **Measured data**: load x/y values from a text file and show them as a line or scatter plot
* **💾 Save and load configurations** as readable `key: value` files
* **🎨 Styling**: title, axis labels, grid, legend, and colour, line width and line style per function

### 🖱️ Interactive GUI
* Live cursor coordinates and **click-to-annotate** points
* Zoom and pan through the Matplotlib toolbar, **export as an image**

### 🔒 Safe expression evaluation
* Expressions only see a **whitelist** of NumPy functions and constants, with no Python built-ins; `^` works as
  the power operator

---

## 🛠️ Getting Started

```bash
pip install numpy matplotlib
python app.py                                 # GUI
python app.py examples/config_bode.txt        # without GUI: plot straight from a configuration file
```

---

## 📝 Configuration Format

```text
# Two functions with curve analysis and measured data
functions: [exp(-0.5*x)*sin(x), cos(x)]
xstart: 0
xend: 10
xstep: 0.1
find_roots: True
find_extrema: True
data_file: examples/messwerte.txt
title: Function Plot Example
```

More examples are in [`examples/`](examples/).

---

## 🏗️ Structure

| File | Role |
|------|------|
| `app.py` | Entry point: GUI, or no-GUI mode when a configuration file is passed |
| `gui.py` | Tkinter interface with controls for each mode and the embedded Matplotlib canvas |
| `plotter.py` | All plotting and the numerical analysis, independent of the GUI |
| `config_parser.py` | Reads `key: value` files and converts the values to booleans, numbers and lists |
| `widgets.py` | A scrollable frame for the long control panel |

---

## 🧰 Tech Stack

Python · Tkinter · Matplotlib · NumPy
