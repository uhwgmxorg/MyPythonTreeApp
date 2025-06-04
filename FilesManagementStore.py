import os
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox

class FilesManagementStore:
    """
    Manages loading/saving of a tkinter Treeview to/from XML files,
    in a format compatible with the original C# implementation.
    """

    # -------------------------------------------------
    # Initialization
    # -------------------------------------------------
    def __init__(self, treeview, show_message_boxes: bool = True):
        self.treeview = treeview
        self.show_message_boxes = show_message_boxes

    # -------------------------------------------------
    # Public load/save methods
    # -------------------------------------------------
    def load_tree(self, last_used_path: str = None) -> str | None:
        """
        Opens an Open dialog, loads the XML and fills the Treeview.
        Returns the selected file path (or None if cancelled).
        """
        init_dir = last_used_path if last_used_path and os.path.isdir(last_used_path) else os.getcwd()
        try:
            filename = filedialog.askopenfilename(
                title="Load Tree...",
                initialdir=init_dir,
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
            )
        except Exception as e:
            messagebox.showerror("Dialog Error", f"Could not open file dialog:\n{e}")
            return None

        if not filename:
            return None

        self._load_from_file(filename)
        return filename

    def save_tree(self, filename: str):
        """
        Saves the Treeview to the specified file. Shows an error if the path is empty.
        """
        if not filename:
            msg = "Please provide a file name to save the tree view data."
            if self.show_message_boxes:
                messagebox.showerror("Save Error", msg)
            else:
                print(f"Save Error: {msg}")
            return

        self._save_to_file(filename)

    def save_as_tree(self, last_used_path: str = None) -> str | None:
        """
        Opens a Save As dialog and then saves.
        Returns the selected file path (or None if cancelled).
        """
        init_dir = last_used_path if last_used_path and os.path.isdir(last_used_path) else os.getcwd()
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Tree As...",
                initialdir=init_dir,
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
            )
        except Exception as e:
            if self.show_message_boxes:
                messagebox.showerror("Dialog Error", f"Could not open save dialog:\n{e}")
            else:
                print(f"Dialog Error: Could not open save dialog:\n{e}")
            return None

        if not filename:
            return None

        self._save_to_file(filename)
        return filename

    # -------------------------------------------------
    # Private helper methods
    # -------------------------------------------------
    def _save_to_file(self, filename: str):
        """
        Recursively builds XML and saves it to file.
        """
        root = ET.Element("TreeView")
        self._write_nodes("", root)

        # Optional: pretty-print
        xml_str = ET.tostring(root, "utf-8")
        tree = ET.ElementTree(ET.fromstring(xml_str))
        tree.write(filename, encoding="utf-8", xml_declaration=True)

        if self.show_message_boxes:
            messagebox.showinfo(
                "Save Successful",
                f"Tree view data saved to file:\n{filename}"
            )

    def _write_nodes(self, parent_iid: str, parent_elem: ET.Element):
        """
        Recursively write all child nodes into parent_elem.
        """
        for iid in self.treeview.get_children(parent_iid):
            text = self.treeview.item(iid, "text")
            node_elem = ET.SubElement(parent_elem, "Node", Text=text)
            self._write_nodes(iid, node_elem)

    def _load_from_file(self, filename: str):
        """
        Clears the Treeview and loads nodes from XML file.
        """
        for iid in self.treeview.get_children():
            self.treeview.delete(iid)

        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            self._read_nodes(root, "")
            if self.show_message_boxes:
                messagebox.showinfo(
                    "Load Successful",
                    f"Tree view data loaded from file:\n{filename}"
                )
        except Exception as ex:
            if self.show_message_boxes:
                messagebox.showerror(
                    "Load Error",
                    f"Error loading tree view data:\n{ex}"
                )
            else:
                print(f"[Debug] Load error: {ex}")

    def _read_nodes(self, xml_parent: ET.Element, parent_iid: str):
        """
        Recursively read all <Node> elements from xml_parent and insert them into the Treeview.
        """
        for node_elem in xml_parent.findall("Node"):
            text = node_elem.get("Text", "")
            new_iid = self.treeview.insert(parent_iid, "end", text=text)
            self._read_nodes(node_elem, new_iid)
