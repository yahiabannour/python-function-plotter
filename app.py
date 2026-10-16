# Yahia Bannour
# app.py
# Entry point for GUI and headless modes.

import sys
import tkinter as tk
from gui import FunctionPlotterGUI
from config_parser import ConfigParser
from plotter import FunctionPlotter

def main():
    """Entry point for the Function Plotter application.

    The application can run in two modes:
    - GUI mode: If no command-line arguments are provided, the Tkinter
      graphical user interface will be launched.
      Example: `python app.py`

    - Headless mode: If a path to a configuration file is provided as a
      command-line argument, the application will parse the file and
      directly generate a plot in a Matplotlib window without launching the GUI.
      Example: `python app.py config.txt`
    """
    # Check if command line arguments are provided (Headless mode)
    if len(sys.argv) > 1:
        # Get the configuration file path from the first argument
        cfg_file = sys.argv[1]   
        
        # Initialize the configuration parser helper
        parser = ConfigParser()  
        
        # Parse the configuration file content into a Python dictionary
        cfg = parser.parse_config(cfg_file) 
        
        # If parsing was successful (cfg is not None), generate the plot
        if cfg:
            # Create a plotter instance and show the plot directly via Matplotlib
            FunctionPlotter().plot_from_config(cfg)
        else:
            print("Error: Could not parse configuration file")
    else:
        # No arguments provided: Launch the Graphical User Interface (GUI) mode
        
        # Create the main Tkinter root window
        root = tk.Tk()
        
        # Initialize the application GUI wrapper passing the root window
        FunctionPlotterGUI(root)
        
        # Start the Tkinter main event loop (waits for user interactions like clicks)
        root.mainloop()

if __name__ == "__main__":
    main()