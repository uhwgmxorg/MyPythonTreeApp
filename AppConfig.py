import json
import os

class AppConfig:
    """
    Manages loading/saving of application settings to a JSON file.
    """

    # -------------------------------------------------
    # Initialization
    # -------------------------------------------------
    def __init__(self, path="config.json"):
        self.path = path

        # Default values
        self.data_source         = "DefaultSource"
        self.show_message_boxes  = True
        self.webservice_url      = "http://127.0.0.1:3000/api/"
        self.datasource_option   = "Files"
        self.window_x            = 100
        self.window_y            = 100
        self.window_width        = 900
        self.window_height       = 600

    # -------------------------------------------------
    # Load settings from disk
    # -------------------------------------------------
    def load(self):
        """Load settings from disk (if file exists)."""
        if os.path.isfile(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for key in ("data_source", "show_message_boxes", "webservice_url",
                            "datasource_option", "window_x", "window_y", "window_width", "window_height"):
                    if key in data:
                        setattr(self, key, data[key])
            except Exception:
                pass
        return self

    # -------------------------------------------------
    # Save current settings to disk
    # -------------------------------------------------
    def save(self):
        """Save current settings to disk."""
        data = {
            "data_source":        self.data_source,
            "show_message_boxes": self.show_message_boxes,
            "webservice_url":     self.webservice_url,
            "datasource_option":  self.datasource_option,
            "window_x":           self.window_x,
            "window_y":           self.window_y,
            "window_width":       self.window_width,
            "window_height":      self.window_height
        }
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Failed to save config:", e)
