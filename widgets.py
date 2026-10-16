# Yahia Bannour
# widgets.py
# Custom Tk widgets and helpers.

import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    """A custom ttk.Frame that scrolls vertically (useful for tall control panels).
    
    Tkinter's standard Frame widget does not support scrolling. To achieve this,
    we must embed a Frame *inside* a Canvas widget, which does support scrolling.
    """
    def __init__(self, parent, *args, **kwargs):
        """Initializes the scrollable frame.

        Args:
            parent: The parent tkinter widget.
            *args, **kwargs: Additional arguments passed to the parent ttk.Frame.
        """
        super().__init__(parent, *args, **kwargs)
        
        # 1. Create a Canvas to hold the scrollable area
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        
        # 2. Create a vertical scrollbar linked to the canvas
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        
        # 3. Pack them: Scrollbar to the right, Canvas fills the rest
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # 4. Create the actual content frame inside the Canvas
        # All widgets should be added to 'self.inner' instead of 'self'
        self.inner = ttk.Frame(self.canvas)
        
        # Embed the frame into the canvas at coordinates (0,0)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        # 5. Events to handle resizing
        # Update scrollregion when the inner frame changes size
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Ensure the inner frame fits the canvas width when the canvas resizes
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.inner_id, width=e.width))

        # Note: Mouse wheel binding was intentionally omitted to avoid UI conflicts.