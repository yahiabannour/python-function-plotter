# Yahia Bannour
# gui.py
# Tkinter front-end (modes: 2D, Parametric, Bode, 3D).

import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import ast

from widgets import ScrollableFrame
from plotter import FunctionPlotter
from config_parser import ConfigParser

class FunctionPlotterGUI:
    """Tkinter GUI wrapping FunctionPlotter with multi-mode controls.

    This class builds and manages the main application window, providing user
    controls for generating various types of plots (2D, Parametric, Bode, 3D).
    It interacts with FunctionPlotter for drawing and ConfigParser for
    loading and saving settings.
    """
    def __init__(self, root):
        """Initializes the main GUI window.

        Args:
            root (tk.Tk): The root tkinter window instance.
        """
        self.root = root
        self.root.title("Function Plotter - Extended GUI")
        self.root.geometry("1200x820")
        self.root.minsize(1000, 700)

        # Initialize helper classes
        self.plotter = FunctionPlotter()
        self.config_parser = ConfigParser()
        
        # Variables to hold UI state
        self.data_file_path = tk.StringVar(value="")
        self.coord_annotation = None # Stores the annotation object for click events

        # Build the visual components
        self._build_gui()

    def _build_gui(self):
        """Constructs the entire graphical user interface layout."""
        # Main layout frame container
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Left Panel: Controls (Scrollable) ---
        # Using custom ScrollableFrame to handle many options on smaller screens
        left_scroll = ScrollableFrame(main)
        left_scroll.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left = ttk.LabelFrame(left_scroll.inner, text="Controls", padding=10)
        left.pack(fill=tk.Y)

        # --- Right Panel: Plot Area ---
        right = ttk.LabelFrame(main, text="Plot Area", padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Top Control Buttons ---
        # Buttons for global actions: loading/saving config, generating plot
        ttk.Button(left, text="Load Config File", command=self.load_config).pack(fill=tk.X, pady=3)
        ttk.Button(left, text="Save Config", command=self._save_config).pack(fill=tk.X, pady=3)
        ttk.Button(left, text="Generate Plot", command=self.generate_plot).pack(fill=tk.X, pady=3)
        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # --- Mode Selector ---
        # Dropdown to switch between different plotting modes (2D, 3D, etc.)
        ttk.Label(left, text="Mode:").pack(anchor=tk.W)
        self.mode_var = tk.StringVar(value="2D")
        mode_combo = ttk.Combobox(left, textvariable=self.mode_var,
                                  values=["2D", "Parametric", "Bode", "3D"], state="readonly")
        mode_combo.pack(fill=tk.X, pady=3)
        # Bind selection event to trigger UI update
        mode_combo.bind("<<ComboboxSelected>>", lambda e: self._show_mode(self.mode_var.get()))

        # --- Common Options (shared across modes) ---
        common = ttk.LabelFrame(left, text="Common Options", padding=10)
        common.pack(fill=tk.X, pady=8)
        self.grid_var = tk.BooleanVar(value=True)
        self.legend_var = tk.BooleanVar(value=True)
        # Grid and Legend checkboxes
        ttk.Checkbutton(common, text="Grid", variable=self.grid_var).grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        ttk.Checkbutton(common, text="Legend", variable=self.legend_var).grid(row=0, column=1, sticky=tk.W, padx=2, pady=2)

        # Title and Axis Labels
        ttk.Label(common, text="Title").grid(row=1, column=0, sticky=tk.W)
        self.title_entry = ttk.Entry(common); self.title_entry.insert(0, "Function Plot")
        self.title_entry.grid(row=1, column=1, sticky=tk.EW, padx=2, pady=2, columnspan=3)

        ttk.Label(common, text="X label").grid(row=2, column=0, sticky=tk.W)
        self.xlabel_entry = ttk.Entry(common); self.xlabel_entry.insert(0, "x")
        self.xlabel_entry.grid(row=2, column=1, sticky=tk.EW, padx=2, pady=2)
        ttk.Label(common, text="Y label").grid(row=2, column=2, sticky=tk.W)
        self.ylabel_entry = ttk.Entry(common); self.ylabel_entry.insert(0, "y / f(x)")
        self.ylabel_entry.grid(row=2, column=3, sticky=tk.EW, padx=2, pady=2)
        common.columnconfigure(1, weight=1)
        common.columnconfigure(3, weight=1)

        # --- Frames per mode (Initially hidden except default) ---
        
        # 1. 2D Functions Frame
        self.frame_2d = ttk.LabelFrame(left, text="2D Functions", padding=10)
        ttk.Label(self.frame_2d, text="Functions (one per line)").pack(anchor=tk.W)
        self.functions_text = tk.Text(self.frame_2d, height=6, width=30)
        self.functions_text.insert("1.0", "exp(-0.5*x)*sin(x)\ncos(2*x)")
        self.functions_text.pack(fill=tk.X, pady=4)

        # Range settings (x-start, x-end, x-step)
        rng = ttk.Frame(self.frame_2d); rng.pack(fill=tk.X)
        ttk.Label(rng, text="x-start").grid(row=0, column=0, sticky=tk.W)
        self.xstart_entry = ttk.Entry(rng, width=8); self.xstart_entry.insert(0, "0")
        self.xstart_entry.grid(row=0, column=1, padx=4)
        ttk.Label(rng, text="x-end").grid(row=0, column=2, sticky=tk.W)
        self.xend_entry = ttk.Entry(rng, width=8); self.xend_entry.insert(0, "5")
        self.xend_entry.grid(row=0, column=3, padx=4)
        ttk.Label(rng, text="x-step").grid(row=0, column=4, sticky=tk.W)
        self.xstep_entry = ttk.Entry(rng, width=8); self.xstep_entry.insert(0, "0.1")
        self.xstep_entry.grid(row=0, column=5, padx=4)

        # Style settings (Colors, Linewidths)
        styles = ttk.Frame(self.frame_2d); styles.pack(fill=tk.X, pady=4)
        ttk.Label(styles, text="colors (comma sep)").grid(row=0, column=0, sticky=tk.W)
        self.colors_entry = ttk.Entry(styles); self.colors_entry.insert(0, "blue, red, green")
        self.colors_entry.grid(row=0, column=1, padx=4, sticky=tk.EW)
        ttk.Label(styles, text="linewidths").grid(row=1, column=0, sticky=tk.W)
        self.linewidths_entry = ttk.Entry(styles); self.linewidths_entry.insert(0, "2, 2, 2")
        self.linewidths_entry.grid(row=1, column=1, padx=4, sticky=tk.EW)
        ttk.Label(styles, text="linestyles").grid(row=2, column=0, sticky=tk.W)
        self.linestyles_entry = ttk.Entry(styles); self.linestyles_entry.insert(0, "-, --, :")
        self.linestyles_entry.grid(row=2, column=1, padx=4, sticky=tk.EW)
        styles.columnconfigure(1, weight=1)

        # Advanced analysis options (Derivatives, Roots, etc.)
        adv = ttk.Frame(self.frame_2d); adv.pack(fill=tk.X, pady=4)
        self.der1_var = tk.BooleanVar(value=False)
        self.der2_var = tk.BooleanVar(value=False)
        self.roots_var = tk.BooleanVar(value=False)
        self.extrema_var = tk.BooleanVar(value=False)
        self.inflect_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv, text="1st derivative", variable=self.der1_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(adv, text="2nd derivative", variable=self.der2_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(adv, text="Roots", variable=self.roots_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(adv, text="Extrema", variable=self.extrema_var).grid(row=1, column=1, sticky=tk.W)
        ttk.Checkbutton(adv, text="Inflections", variable=self.inflect_var).grid(row=1, column=2, sticky=tk.W)

        # Optional Data File Overlay
        dataf = ttk.LabelFrame(self.frame_2d, text="Optional Data File", padding=6)
        dataf.pack(fill=tk.X, pady=6)
        dfrow = ttk.Frame(dataf); dfrow.pack(fill=tk.X)
        ttk.Button(dfrow, text="Choose .txt/.csv", command=self._choose_data_file).pack(side=tk.LEFT)
        ttk.Label(dfrow, textvariable=self.data_file_path).pack(side=tk.LEFT, padx=6)
        dopt = ttk.Frame(dataf); dopt.pack(fill=tk.X, pady=4)
        ttk.Label(dopt, text="Plot type").grid(row=0, column=0, sticky=tk.W)
        self.data_plot_type = tk.StringVar(value="scatter")
        ttk.Combobox(dopt, textvariable=self.data_plot_type, values=["scatter", "line"], state="readonly")\
            .grid(row=0, column=1, sticky=tk.W, padx=4)
        ttk.Label(dopt, text="Data color").grid(row=0, column=2, sticky=tk.W)
        self.data_color_entry = ttk.Entry(dopt, width=10); self.data_color_entry.insert(0, "tab:gray")
        self.data_color_entry.grid(row=0, column=3, padx=4)
        ttk.Label(dopt, text="Data label").grid(row=0, column=4, sticky=tk.W)
        self.data_label_entry = ttk.Entry(dopt, width=10); self.data_label_entry.insert(0, "data")
        self.data_label_entry.grid(row=0, column=5, padx=4)

        # 2. Parametric Mode Frame
        self.frame_param = ttk.LabelFrame(left, text="Parametric", padding=10)
        ttk.Label(self.frame_param, text="x(t) =").grid(row=0, column=0, sticky=tk.W)
        self.px_entry = ttk.Entry(self.frame_param); self.px_entry.insert(0, "cos(t)")
        self.px_entry.grid(row=0, column=1, sticky=tk.EW, padx=4)
        ttk.Label(self.frame_param, text="y(t) =").grid(row=1, column=0, sticky=tk.W)
        self.py_entry = ttk.Entry(self.frame_param); self.py_entry.insert(0, "sin(t)")
        self.py_entry.grid(row=1, column=1, sticky=tk.EW, padx=4)
        # Time variable setup
        tgrid = ttk.Frame(self.frame_param); tgrid.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=4)
        ttk.Label(tgrid, text="t-start").grid(row=0, column=0, sticky=tk.W)
        self.tstart_entry = ttk.Entry(tgrid, width=8); self.tstart_entry.insert(0, "0")
        self.tstart_entry.grid(row=0, column=1, padx=4)
        ttk.Label(tgrid, text="t-end").grid(row=0, column=2, sticky=tk.W)
        self.tend_entry = ttk.Entry(tgrid, width=8); self.tend_entry.insert(0, str(2*np.pi))
        self.tend_entry.grid(row=0, column=3, padx=4)
        ttk.Label(tgrid, text="t-step").grid(row=0, column=4, sticky=tk.W)
        self.tstep_entry = ttk.Entry(tgrid, width=8); self.tstep_entry.insert(0, "0.01")
        self.tstep_entry.grid(row=0, column=5, padx=4)
        self.frame_param.columnconfigure(1, weight=1)

        # 3. Bode Plot Frame
        self.frame_bode = ttk.LabelFrame(left, text="Bode", padding=10)
        ttk.Label(self.frame_bode, text="Numerator [a_n, ..., a_0]").grid(row=0, column=0, sticky=tk.W)
        self.bode_num_entry = ttk.Entry(self.frame_bode); self.bode_num_entry.insert(0, "[1]")
        self.bode_num_entry.grid(row=0, column=1, sticky=tk.EW, padx=4)
        ttk.Label(self.frame_bode, text="Denominator [b_n, ..., b_0]").grid(row=1, column=0, sticky=tk.W)
        self.bode_den_entry = ttk.Entry(self.frame_bode); self.bode_den_entry.insert(0, "[1, 1]")
        self.bode_den_entry.grid(row=1, column=1, sticky=tk.EW, padx=4)
        # Frequency range options
        bpar = ttk.Frame(self.frame_bode); bpar.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=4)
        ttk.Label(bpar, text="wmin").grid(row=0, column=0, sticky=tk.W)
        self.wmin_entry = ttk.Entry(bpar, width=8); self.wmin_entry.insert(0, "0.1")
        self.wmin_entry.grid(row=0, column=1, padx=4)
        ttk.Label(bpar, text="wmax").grid(row=0, column=2, sticky=tk.W)
        self.wmax_entry = ttk.Entry(bpar, width=8); self.wmax_entry.insert(0, "100")
        self.wmax_entry.grid(row=0, column=3, padx=4)
        ttk.Label(bpar, text="npoints").grid(row=0, column=4, sticky=tk.W)
        self.npoints_entry = ttk.Entry(bpar, width=8); self.npoints_entry.insert(0, "400")
        self.npoints_entry.grid(row=0, column=5, padx=4)
        self.frame_bode.columnconfigure(1, weight=1)

        # 4. 3D Surface/Contour Frame
        self.frame_3d = ttk.LabelFrame(left, text="3D Surface/Contour", padding=10)
        ttk.Label(self.frame_3d, text="f(x,y) =").grid(row=0, column=0, sticky=tk.W)
        self.fxy_entry = ttk.Entry(self.frame_3d); self.fxy_entry.insert(0, "sin(x)*cos(y)")
        self.fxy_entry.grid(row=0, column=1, sticky=tk.EW, padx=4)
        # X and Y grid definition
        grid3d = ttk.Frame(self.frame_3d); grid3d.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=4)
        ttk.Label(grid3d, text="x-start").grid(row=0, column=0, sticky=tk.W)
        self.xstart3_entry = ttk.Entry(grid3d, width=8); self.xstart3_entry.insert(0, "-2")
        self.xstart3_entry.grid(row=0, column=1, padx=4)
        ttk.Label(grid3d, text="x-end").grid(row=0, column=2, sticky=tk.W)
        self.xend3_entry = ttk.Entry(grid3d, width=8); self.xend3_entry.insert(0, "2")
        self.xend3_entry.grid(row=0, column=3, padx=4)
        ttk.Label(grid3d, text="x-step").grid(row=0, column=4, sticky=tk.W)
        self.xstep3_entry = ttk.Entry(grid3d, width=8); self.xstep3_entry.insert(0, "0.05")
        self.xstep3_entry.grid(row=0, column=5, padx=4)
        ttk.Label(grid3d, text="y-start").grid(row=1, column=0, sticky=tk.W)
        self.ystart3_entry = ttk.Entry(grid3d, width=8); self.ystart3_entry.insert(0, "-2")
        self.ystart3_entry.grid(row=1, column=1, padx=4)
        ttk.Label(grid3d, text="y-end").grid(row=1, column=2, sticky=tk.W)
        self.yend3_entry = ttk.Entry(grid3d, width=8); self.yend3_entry.insert(0, "2")
        self.yend3_entry.grid(row=1, column=3, padx=4)
        ttk.Label(grid3d, text="y-step").grid(row=1, column=4, sticky=tk.W)
        self.ystep3_entry = ttk.Entry(grid3d, width=8); self.ystep3_entry.insert(0, "0.05")
        self.ystep3_entry.grid(row=1, column=5, padx=4)
        # Visualization options (Surface, Contour, Levels)
        opts3d = ttk.Frame(self.frame_3d); opts3d.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=4)
        self.surface_var = tk.BooleanVar(value=True)
        self.contour_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts3d, text="Surface", variable=self.surface_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(opts3d, text="Contour", variable=self.contour_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(opts3d, text="Levels").grid(row=0, column=2, sticky=tk.W)
        self.levels_entry = ttk.Entry(opts3d, width=8); self.levels_entry.insert(0, "20")
        self.levels_entry.grid(row=0, column=3, padx=4)
        self.frame_3d.columnconfigure(1, weight=1)

        # Activate the default mode (2D)
        self._show_mode("2D")

        # --- Matplotlib Canvas Integration ---
        import matplotlib.pyplot as plt
        self.figure = plt.Figure(figsize=(8, 6))
        self.ax = self.figure.add_subplot(111)
        # The FigureCanvasTkAgg bridges Matplotlib figures to Tkinter widgets
        self.canvas = FigureCanvasTkAgg(self.figure, right)

        # Add Matplotlib Navigation Toolbar (Zoom, Pan, Save)
        toolbar_frame = ttk.Frame(right)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        NavigationToolbar2Tk(self.canvas, toolbar_frame)

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # --- Status Bar ---
        status_bar = ttk.Frame(right)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.coords_var = tk.StringVar()
        coords_label = ttk.Label(status_bar, textvariable=self.coords_var, anchor=tk.W)
        coords_label.pack(side=tk.LEFT, padx=5)

        # Connect Matplotlib events (Mouse move, Click) to handlers
        self.figure.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.figure.canvas.mpl_connect('button_press_event', self._on_click)

    # ---- GUI Event Handlers ----
    def _on_mouse_move(self, event):
        """Callback: Updates the status bar with cursor coordinates."""
        if event.inaxes:
            # For 3D plots, format_coord is available and handles z-coords
            if hasattr(event.inaxes, 'format_coord'):
                self.coords_var.set(event.inaxes.format_coord(event.xdata, event.ydata))
            else:
                x, y = event.xdata, event.ydata
                self.coords_var.set(f"x = {x:.4f},  y = {y:.4f}")
        else:
            self.coords_var.set("")

    def _on_click(self, event):
        """Callback: Adds a text annotation at the click location (2D only)."""
        # Remove previous annotation if it exists
        if self.coord_annotation and self.coord_annotation.get_visible():
            self.coord_annotation.set_visible(False)

        # Check if click is inside axes
        if event.inaxes and hasattr(event.inaxes, 'format_coord'):
            x, y = event.xdata, event.ydata

            # Create annotation object if not exists or if axes changed
            if not self.coord_annotation or self.coord_annotation.axes != event.inaxes:
                self.coord_annotation = event.inaxes.annotate(
                    "", xy=(0,0), xytext=(15, -15),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w", alpha=0.5),
                    arrowprops=dict(arrowstyle="->")
                )

            # Update annotation position and text
            self.coord_annotation.xy = (x, y)
            self.coord_annotation.set_text(f"({x:.2f}, {y:.2f})")
            self.coord_annotation.set_visible(True)
            self.canvas.draw_idle()
        else:
            self.canvas.draw_idle()

    def _save_config(self):
        """Collects current GUI settings and saves them to a file."""
        try:
            config = self._collect_config_from_gui()
        except Exception as e:
            messagebox.showerror("Error", f"Could not collect settings: {e}")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Configuration As",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            defaultextension=".txt"
        )
        if not filename:
            return

        try:
            # Write key:value pairs to the selected file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Configuration saved from Function Plotter GUI\n\n")

                # Handle functions separately to write formatted f1, f2, ...
                if 'functions' in config:
                    functions = config.pop('functions')
                    for i, func_str in enumerate(functions):
                        f.write(f"f{i+1}: {func_str}\n")

                # Write all other key-value pairs
                for key, value in config.items():
                    if value is None or value == '':
                        continue
                    
                    if isinstance(value, list):
                        if not value: continue
                        # Join string lists (like colors) with comma
                        if all(isinstance(item, str) for item in value):
                            f.write(f"{key}: {','.join(value)}\n")
                        # Write other lists (like coefficients) as standard representation
                        else:
                            f.write(f"{key}: {str(value)}\n")
                    else:
                        f.write(f"{key}: {str(value)}\n")

            messagebox.showinfo("Success", f"Configuration saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save configuration: {e}")

    def _show_mode(self, mode):
        """Switches the visible control frame based on the selected mode.

        Args:
            mode (str): The mode to display ("2D", "Parametric", "Bode", "3D").
        """
        # Hide all frames first
        for fr in (self.frame_2d, self.frame_param, self.frame_bode, self.frame_3d):
            fr.pack_forget()
        # Pack the relevant frame
        if mode == "2D":
            self.frame_2d.pack(fill=tk.X, pady=8)
        elif mode == "Parametric":
            self.frame_param.pack(fill=tk.X, pady=8)
        elif mode == "Bode":
            self.frame_bode.pack(fill=tk.X, pady=8)
        elif mode == "3D":
            self.frame_3d.pack(fill=tk.X, pady=8)

    def _choose_data_file(self):
        """Dialog to select a data file path."""
        filename = filedialog.askopenfilename(
            title="Select data file",
            filetypes=[("Text/CSV files", "*.txt *.csv"), ("All files", "*.*")]
        )
        if filename:
            self.data_file_path.set(filename)

    def _save_plot(self):
        """(Legacy) Saves the plot. Functionality now handled by NavigationToolbar."""
        if not self.figure or not self.figure.axes:
            messagebox.showwarning("Warning", "No plot to save. Please generate a plot first.")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Plot As",
            filetypes=[
                ("PNG Image", "*.png"),
                ("SVG Vector Image", "*.svg"),
                ("PDF Document", "*.pdf"),
                ("JPEG Image", "*.jpg"),
                ("All files", "*.*")
            ],
            defaultextension=".png"
        )
        if filename:
            try:
                self.figure.savefig(filename, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save plot: {e}")

    def load_config(self):
        """Loads a config file and populates the GUI fields accordingly."""
        filename = filedialog.askopenfilename(
            title="Select configuration file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filename:
            return
        # Parse the file
        config = self.config_parser.parse_config(filename)
        if not config:
            messagebox.showerror("Error", "Could not parse configuration file")
            return

        # --- Populate Shared Fields ---
        self.title_entry.delete(0, tk.END); self.title_entry.insert(0, str(config.get('title', 'Function Plot')))
        self.xlabel_entry.delete(0, tk.END); self.xlabel_entry.insert(0, str(config.get('xlabel', 'x')))
        self.ylabel_entry.delete(0, tk.END); self.ylabel_entry.insert(0, str(config.get('ylabel', 'y')))
        self.grid_var.set(bool(config.get('grid', True)))
        self.legend_var.set(bool(config.get('legend', True)))

        # --- Detect Mode and Populate Specific Fields ---
        if config.get('bode_num') is not None and config.get('bode_den') is not None:
            self.mode_var.set("Bode"); self._show_mode("Bode")
            self.bode_num_entry.delete(0, tk.END); self.bode_num_entry.insert(0, str(config.get('bode_num')))
            self.bode_den_entry.delete(0, tk.END); self.bode_den_entry.insert(0, str(config.get('bode_den')))
            self.wmin_entry.delete(0, tk.END); self.wmin_entry.insert(0, str(config.get('wmin', 0.1)))
            self.wmax_entry.delete(0, tk.END); self.wmax_entry.insert(0, str(config.get('wmax', 100.0)))
            self.npoints_entry.delete(0, tk.END); self.npoints_entry.insert(0, str(config.get('npoints', 400)))
        elif config.get('fxy') is not None:
            self.mode_var.set("3D"); self._show_mode("3D")
            self.fxy_entry.delete(0, tk.END); self.fxy_entry.insert(0, str(config.get('fxy')))
            self.xstart3_entry.delete(0, tk.END); self.xstart3_entry.insert(0, str(config.get('xstart', -2)))
            self.xend3_entry.delete(0, tk.END); self.xend3_entry.insert(0, str(config.get('xend', 2)))
            self.xstep3_entry.delete(0, tk.END); self.xstep3_entry.insert(0, str(config.get('xstep', 0.05)))
            self.ystart3_entry.delete(0, tk.END); self.ystart3_entry.insert(0, str(config.get('ystart', -2)))
            self.yend3_entry.delete(0, tk.END); self.yend3_entry.insert(0, str(config.get('yend', 2)))
            self.ystep3_entry.delete(0, tk.END); self.ystep3_entry.insert(0, str(config.get('ystep', 0.05)))
            self.surface_var.set(bool(config.get('surface', True)))
            self.contour_var.set(bool(config.get('contour', True)))
            self.levels_entry.delete(0, tk.END); self.levels_entry.insert(0, str(config.get('levels', 20)))
        elif config.get('px') is not None and config.get('py') is not None:
            self.mode_var.set("Parametric"); self._show_mode("Parametric")
            self.px_entry.delete(0, tk.END); self.px_entry.insert(0, str(config.get('px')))
            self.py_entry.delete(0, tk.END); self.py_entry.insert(0, str(config.get('py')))
            self.tstart_entry.delete(0, tk.END); self.tstart_entry.insert(0, str(config.get('tstart', 0)))
            self.tend_entry.delete(0, tk.END); self.tend_entry.insert(0, str(config.get('tend', 2*np.pi)))
            self.tstep_entry.delete(0, tk.END); self.tstep_entry.insert(0, str(config.get('tstep', 0.01)))
        else:
            self.mode_var.set("2D"); self._show_mode("2D")
            funs = []
            if 'functions' in config and isinstance(config['functions'], list):
                funs = [str(f) for f in config['functions']]
            elif 'fi' in config:
                funs = [str(config['fi'])]
            self.functions_text.delete("1.0", tk.END)
            self.functions_text.insert("1.0", "\n".join(funs) if funs else "exp(-0.5*x)*sin(x)")
            self.xstart_entry.delete(0, tk.END); self.xstart_entry.insert(0, str(config.get('xstart', 0)))
            self.xend_entry.delete(0, tk.END); self.xend_entry.insert(0, str(config.get('xend', 5)))
            self.xstep_entry.delete(0, tk.END); self.xstep_entry.insert(0, str(config.get('xstep', 0.1)))
            if 'colors' in config: self.colors_entry.delete(0, tk.END); self.colors_entry.insert(0, ",".join(config['colors']) if isinstance(config['colors'], list) else str(config['colors']))
            if 'linewidths' in config: self.linewidths_entry.delete(0, tk.END); self.linewidths_entry.insert(0, ",".join(map(str, config['linewidths'])) if isinstance(config['linewidths'], list) else str(config['linewidths']))
            if 'linestyles' in config: self.linestyles_entry.delete(0, tk.END); self.linestyles_entry.insert(0, ",".join(config['linestyles']) if isinstance(config['linestyles'], list) else str(config['linestyles']))
            self.der1_var.set(bool(config.get('derivative1', False)))
            self.der2_var.set(bool(config.get('derivative2', False)))
            self.roots_var.set(bool(config.get('find_roots', False)))
            self.extrema_var.set(bool(config.get('find_extrema', False)))
            self.inflect_var.set(bool(config.get('find_inflections', False)))
            if config.get('data_file'): self.data_file_path.set(str(config['data_file']))
            if config.get('plot_type'): self.data_plot_type.set(str(config['plot_type']))
            if config.get('data_color'): self.data_color_entry.delete(0, tk.END); self.data_color_entry.insert(0, str(config['data_color']))
            if config.get('data_label'): self.data_label_entry.delete(0, tk.END); self.data_label_entry.insert(0, str(config['data_label']))

        messagebox.showinfo("Success", "Configuration loaded successfully!")
        self.generate_plot_from_config(config)

    def _collect_config_from_gui(self):
        """Gathers all settings from the UI fields into a dictionary.

        This method reads the current state of all entry fields, checkboxes,
        and selections, and organizes them into a configuration dictionary
        that can be used by the FunctionPlotter.

        Returns:
            dict: A dictionary containing all current GUI settings.
        """
        cfg = {
            'grid': self.grid_var.get(),
            'legend': self.legend_var.get(),
            'title': self.title_entry.get().strip(),
            'xlabel': self.xlabel_entry.get().strip(),
            'ylabel': self.ylabel_entry.get().strip()
        }
        mode = self.mode_var.get()

        if mode == "2D":
            # Split multiline text into list of functions
            funs = [ln.strip() for ln in self.functions_text.get("1.0", tk.END).splitlines() if ln.strip()]
            cfg['functions'] = funs if funs else ["sin(x)"]
            cfg['xstart'] = float(self.xstart_entry.get())
            cfg['xend'] = float(self.xend_entry.get())
            cfg['xstep'] = float(self.xstep_entry.get())
            
            # Parse style lists
            if self.colors_entry.get().strip():
                cfg['colors'] = [c.strip() for c in self.colors_entry.get().split(',')]
            if self.linewidths_entry.get().strip():
                cfg['linewidths'] = [float(v.strip()) for v in self.linewidths_entry.get().split(',')]
            if self.linestyles_entry.get().strip():
                cfg['linestyles'] = [s.strip() for s in self.linestyles_entry.get().split(',')]
            
            # Analysis flags
            cfg['derivative1'] = self.der1_var.get()
            cfg['derivative2'] = self.der2_var.get()
            cfg['find_roots'] = self.roots_var.get()
            cfg['find_extrema'] = self.extrema_var.get()
            cfg['find_inflections'] = self.inflect_var.get()
            
            # Optional data file
            if self.data_file_path.get().strip():
                cfg['data_file'] = self.data_file_path.get().strip()
                cfg['plot_type'] = self.data_plot_type.get().strip()
                cfg['data_color'] = self.data_color_entry.get().strip()
                cfg['data_label'] = self.data_label_entry.get().strip()

        elif mode == "Parametric":
            cfg['px'] = self.px_entry.get().strip()
            cfg['py'] = self.py_entry.get().strip()
            cfg['tstart'] = float(self.tstart_entry.get())
            cfg['tend'] = float(self.tend_entry.get())
            cfg['tstep'] = float(self.tstep_entry.get())

        elif mode == "Bode":
            # Handle list input for numerator/denominator
            try:
                cfg['bode_num'] = ast.literal_eval(self.bode_num_entry.get().strip())
                cfg['bode_den'] = ast.literal_eval(self.bode_den_entry.get().strip())
            except Exception:
                # Fallback for simple comma separated strings
                cfg['bode_num'] = [float(v) for v in self.bode_num_entry.get().split(',')]
                cfg['bode_den'] = [float(v) for v in self.bode_den_entry.get().split(',')]
            cfg['wmin'] = float(self.wmin_entry.get())
            cfg['wmax'] = float(self.wmax_entry.get())
            cfg['npoints'] = int(self.npoints_entry.get())

        elif mode == "3D":
            cfg['fxy'] = self.fxy_entry.get().strip()
            cfg['xstart'] = float(self.xstart3_entry.get())
            cfg['xend'] = float(self.xend3_entry.get())
            cfg['xstep'] = float(self.xstep3_entry.get())
            cfg['ystart'] = float(self.ystart3_entry.get())
            cfg['yend'] = float(self.yend3_entry.get())
            cfg['ystep'] = float(self.ystep3_entry.get())
            cfg['surface'] = self.surface_var.get()
            cfg['contour'] = self.contour_var.get()
            cfg['levels'] = int(self.levels_entry.get())

        return cfg

    def generate_plot_from_config(self, config):
        """Generates a plot on the canvas from a given config dictionary.

        Args:
            config (dict): A dictionary of configuration parameters.
        """
        try:
            # Delegate drawing to the Plotter class
            self.ax = self.plotter.plot_on_canvas(self.figure, self.ax, config)
            # Adjust layout to prevent clipping
            self.figure.tight_layout()
            # Refresh the canvas
            self.canvas.draw_idle()
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate plot: {e}")

    def generate_plot(self):
        """Generates a plot based on the current settings in the GUI."""
        try:
            config = self._collect_config_from_gui()
            self.generate_plot_from_config(config)
        except ValueError:
            messagebox.showerror("Input Error", "Please check numeric fields and expressions.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate plot: {e}")