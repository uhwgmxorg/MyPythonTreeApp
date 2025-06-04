import re
import urllib.request
import urllib.error
import json
import xml.etree.ElementTree as ET
from tkinter import messagebox
from XmlSelectBoxDialog import XmlSelectBoxDialog

class WebServiceManagementStore:
    """
    Manages loading, saving, and save-as of a tkinter Treeview
    against a remote XML web service.
    """

    # -------------------------------------------------
    # Constructor
    # -------------------------------------------------
    def __init__(self, treeview, webservice_url: str, show_message_boxes: bool = True):
        self.treeview = treeview
        self.webservice_url = webservice_url.rstrip('/')
        self.show_message_boxes = show_message_boxes

    # -------------------------------------------------
    # Public interface: Load from service
    # -------------------------------------------------
    def load_tree(self, parent) -> str | None:
        """
        Opens XmlSelectBoxDialog to pick an ID,
        fetches the XML, populates the Treeview,
        and returns "Id: X Name: Y".
        """
        dlg = XmlSelectBoxDialog(
            parent=parent,
            webservice_url=self.webservice_url,
            show_message_boxes=self.show_message_boxes,
            save_as_mode=False,
            tree_store=self
        )
        if dlg.selected_id is None or dlg.selected_name is None:
            return None

        xml_id = dlg.selected_id
        try:
            with urllib.request.urlopen(f"{self.webservice_url}/get_xml_by_id/{xml_id}") as resp:
                xml_data = resp.read().decode('utf-8')
        except Exception as e:
            if self.show_message_boxes:
                messagebox.showerror("Load Error", f"Could not load XML data:\n{e}")
            else:
                print(f"Load Error: Could not load XML data:\n{e}")
            return None

        # clear existing nodes
        for iid in self.treeview.get_children():
            self.treeview.delete(iid)

        # parse and populate
        try:
            root = ET.fromstring(xml_data)
            self._read_nodes(root, '')
            if self.show_message_boxes:
                messagebox.showinfo("Load Successful", f"Loaded XML ID {xml_id}")
        except ET.ParseError as e:
            if self.show_message_boxes:
                messagebox.showerror("Parse Error", f"Failed to parse XML:\n{e}")
            else:
                print(f"Parse Error: Failed to parse XML:\n{e}")
            return None

        return f"Id: {xml_id} Name: {dlg.selected_name}"

    # -------------------------------------------------
    # Public interface: Save existing XML
    # -------------------------------------------------
    def save_tree(self, parent):
        """
        Reads the current data_source ID from parent.config_data,
        serializes the Treeview to XML, and sends a PUT request.
        """
        # extract ID from parent.config_data.data_source
        ds = getattr(parent.config_data, "data_source", "") or ""
        match = re.search(r"Id:\s*(\d+)", ds)
        if not match:
            msg = "Keine gültige XML-ID gefunden."
            if self.show_message_boxes:
                messagebox.showerror("Save Error", msg)
            else:
                print(f"Save Error: {msg}")
            return
        xml_id = int(match.group(1))

        xml_str = self._serialize_tree_to_xml()
        payload = json.dumps({"id": xml_id, "xmlData": xml_str}).encode('utf-8')

        req = urllib.request.Request(
            url=f"{self.webservice_url}/update_xml_by_id",
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        try:
            with urllib.request.urlopen(req):
                pass
            if self.show_message_boxes:
                messagebox.showinfo("Update Successful", f"Updated XML ID {xml_id}")
        except Exception as e:
            if self.show_message_boxes:
                messagebox.showerror("Save Error", f"Could not update XML:\n{e}")
            else:
                print(f"Save Error: Could not update XML:\n{e}")

    # -------------------------------------------------
    # Public interface: Save As (create new XML)
    # -------------------------------------------------
    def save_as_tree(self, parent) -> str | None:
        """
        Opens XmlSelectBoxDialog in save-as mode,
        lets the user enter a new name,
        POSTs the XML to create a new entry,
        and returns "Id: X Name: Y".
        """
        dlg = XmlSelectBoxDialog(
            parent=parent,
            webservice_url=self.webservice_url,
            show_message_boxes=self.show_message_boxes,
            save_as_mode=True,
            tree_store=self
        )
        if dlg.selected_id is None or dlg.selected_name is None:
            return None

        return f"Id: {dlg.selected_id} Name: {dlg.selected_name}"

    # -------------------------------------------------
    # Internal: Serialize Treeview to XML string
    # -------------------------------------------------
    def _serialize_tree_to_xml(self) -> str:
        """
        Serializes the Treeview nodes into an XML string.
        """
        root = ET.Element("TreeView")
        self._write_nodes('', root)
        return ET.tostring(root, encoding='unicode')

    # -------------------------------------------------
    # Internal helper: Write nodes recursively
    # -------------------------------------------------
    def _write_nodes(self, parent_iid, parent_elem):
        """
        Recursively writes all child nodes into parent_elem.
        """
        for iid in self.treeview.get_children(parent_iid):
            text = self.treeview.item(iid, 'text')
            node_elem = ET.SubElement(parent_elem, 'Node', Text=text)
            self._write_nodes(iid, node_elem)

    # -------------------------------------------------
    # Internal helper: Read nodes recursively
    # -------------------------------------------------
    def _read_nodes(self, xml_parent, parent_iid):
        """
        Recursively reads <Node> elements and inserts into the Treeview.
        """
        for node_elem in xml_parent.findall('Node'):
            text = node_elem.get('Text', '')
            new_iid = self.treeview.insert(parent_iid, 'end', text=text)
            self._read_nodes(node_elem, new_iid)
