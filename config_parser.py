# Yahia Bannour
# config_parser.py
# Simple "key: value" configuration file reader.

import ast  # abstract syntax tree --> ast.literal_eval    strings--->datenstrukturen
import re   # regular expression    --> muster in texten zu finden 

class ConfigParser:
    """Parses simple 'key: value' config files into a dictionary.

    This class reads text-based configuration files, handling comments (#),
    and converts values to appropriate Python types like bool, int, float, or list.
    It also handles special cases like collecting 'f1', 'f2', ... into a list.
    """
    def __init__(self):
        """Initializes the parser."""
        # A set of all known/supported configuration keys.
        # This is primarily for documentation purposes and potential future validation
        # to ensure the config file doesn't contain unknown parameters.
        self.valid_keys = {
            'fi', 'functions',
            'xstart', 'xend', 'xstep',
            'ystart', 'yend', 'ystep',
            'grid', 'legend', 'title', 'xlabel', 'ylabel', 'zlabel',
            'color', 'colors', 'linewidth', 'linewidths', 'linestyles',
            'data_file', 'plot_type', 'data_color', 'data_label',
            'derivative1', 'derivative2',
            'find_roots', 'find_extrema', 'find_inflections',
            # Parametric mode keys
            'px', 'py', 'tstart', 'tend', 'tstep',
            # Bode plot keys
            'bode_num', 'bode_den', 'wmin', 'wmax', 'npoints',
            # 3D plot keys
            'fxy', 'surface', 'contour', 'levels'
        }

    def parse_config(self, filename):
        """Parses a configuration file and returns a dictionary of parameters.

        Args:
            filename (str): The path to the configuration file.

        Returns:
            dict or None: A dictionary containing the parsed configuration
            parameters, or None if an error occurs.
        """
        config = {}
        try:
            # Open file with utf-8 encoding to handle special characters
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                # Skip empty lines or comment lines starting with '#'
                if not line or line.startswith('#'):
                    continue
                
                # Parse lines containing a key-value pair separated by ':'
                if ':' in line:
                    key, value = line.split(':', 1)
                    key, value = key.strip(), value.strip()
                    # Convert the string value to a proper Python type
                    config[key] = self._convert_value(value)

            # Special handling for multiple functions defined as f1, f2, f3...
            # Identify keys matching the pattern "f" followed by numbers
            func_keys = sorted(
                [k for k in config.keys() if re.fullmatch(r"f\d+", k)],
                key=lambda s: int(s[1:]) # Sort numerically by the number after 'f'
            )
            
            # If such keys exist, collect their values into a 'functions' list
            if func_keys:
                config['functions'] = [config[k] for k in func_keys]

            # Backward compatibility: Map 'fi' key to 'functions' list if not already set
            if 'fi' in config and 'functions' not in config:
                config['functions'] = [config['fi']]

            return config
        except Exception as e:
            print(f"Error reading configuration file: {e}")
            return None

    def _convert_value(self, value):
        """Converts a string value to a more specific type if possible.

        Handles:
        - Booleans: 'true', 'yes', 'on' -> True
        - Numbers: '123' -> 123, '12.34' -> 12.34
        - Lists: '[1, 2, 3]' -> [1, 2, 3]

        Args:
            value (str): The string value from the config file.

        Returns:
            bool, int, float, list, or str: The converted value.
        """
        if isinstance(value, str):
            low = value.lower()
            # Check for boolean string representations
            if low in ('true', 'yes', 'on'):
                return True
            if low in ('false', 'no', 'off'):
                return False

        # Try to convert to float or int
        try:
            return float(value) if '.' in str(value) else int(value)
        except (ValueError, TypeError):
            pass

        # Check if the value looks like a Python list (e.g., "[1, 2, 3]")
        if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
            try:
                # Safely evaluate the string as a Python literal
                return ast.literal_eval(value)
            except Exception:
                # Fallback: If literal_eval fails (e.g. for list of expressions),
                # strip brackets and split by comma manually.
                content = value.strip()[1:-1].strip()
                if content:
                    return [item.strip() for item in content.split(',')]
                return []

        # Return original string if no conversion matched
        return value