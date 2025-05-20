# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import urllib.error
import json

class XmlSelectBoxDialog(tk.Toplevel):
    """
    Dialog for selecting, deleting, renaming and Save-As of XML entries
    from the web service. On Load or SaveAs OK, sets self.selected_id and self.selected_name.
    """

    # -------------------------------------------------
    # Initialization & Positioning
    # -------------------------------------------------
    def __init__(self,
                 parent,
                 webservice_url: str,
                 show_message_boxes: bool = True,
                 save_as_mode: bool = False,
                 tree_store=None):
        super().__init__(parent)
        self.parent = parent
        self.webservice_url = webservice_url.rstrip('/')
        self.show_message_boxes = show_message_boxes
        self.save_as_mode = save_as_mode
        self.tree_store = tree_store
        self.selected_id = None
        self.selected_name = None

        # Window size & position (top-right of parent)
        self.title("Select XML")
        self.geometry("340x300")
        self.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        # place 10px to the right, same top
        self.geometry(f"+{px+pw+10}+{py-30}")

        # Build all UI pieces
        self._build_ui()
        # Initial load of list
        self._load_list()

        # Make modal
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    # -------------------------------------------------
    # Build UI Sections
    # -------------------------------------------------
    def _build_ui(self):
        # Top: Save-As row
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=5, pady=(5,2))
        tk.Label(top, text="Save or Save XML as:").pack(side=tk.LEFT)
        self.entry_saveas = tk.Entry(top)
        self.entry_saveas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4,2))
        self.btn_saveas = tk.Button(top, text="Save/As", width=10, command=self._on_save_as)
        self.btn_saveas.pack(side=tk.LEFT)
        if not self.save_as_mode:
            self.entry_saveas.config(state="disabled")
            self.btn_saveas.config(state="disabled")

        # Middle: TreeView + Scrollbar + Buttons container
        mid = tk.Frame(self)
        mid.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # TreeView itself
        cols = ("ID", "Name")
        self.tree = ttk.Treeview(mid, columns=cols, show="headings", selectmode="browse", height=10)
        self.tree.heading("ID", text="ID");     self.tree.column("ID", width=50, anchor="center")
        self.tree.heading("Name", text="Name"); self.tree.column("Name", width=200, anchor="w")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Vertical scrollbar
        vsb = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        # Buttons panel: anchored bottom-right of mid
        btn_side = tk.Frame(mid)
        btn_side.pack(side=tk.RIGHT, anchor="s", fill=tk.Y, padx=(5,0), pady=(0,5))

        # Pack buttons bottom-up so that Reload ends up at top
        # 1) Close (last, at very bottom)
        tk.Button(btn_side, text="Close", width=10, command=self._on_close)\
            .pack(side=tk.BOTTOM, pady=2)
        # 2) Load (just above Close) — bold if not in save-as mode
        if not self.save_as_mode:
            tk.Button(btn_side,
                      text="Load",
                      width=10,
                      command=self._on_load,
                      font=("TkDefaultFont", 10, "bold"))\
                .pack(side=tk.BOTTOM, pady=2)
        # 3) Delete (above Load)
        tk.Button(btn_side, text="Delete", width=10, command=self._delete_entry)\
            .pack(side=tk.BOTTOM, pady=2)
        # 4) Reload (topmost)
        tk.Button(btn_side, text="Reload", width=10, command=self._load_list)\
            .pack(side=tk.BOTTOM, pady=2)

        # Highlight the Save/As button if in save-as mode
        if self.save_as_mode:
            self.btn_saveas.config(font=("TkDefaultFont", 10, "bold"))

        # Double-click binds
        self.tree.bind("<Double-1>", self._on_double_click)

    # -------------------------------------------------
    # Load & Delete Logic
    # -------------------------------------------------
    def _load_list(self):
        """Fetch /get_all_xml_info and populate tree."""
        try:
            with urllib.request.urlopen(f"{self.webservice_url}/get_all_xml_info") as resp:
                files = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file list:\n{e}")
            return

        self.tree.delete(*self.tree.get_children())
        for f in files:
            self.tree.insert("", tk.END, values=(f["id"], f["name"]))

    def _delete_entry(self):
        """Delete selected XML entry via DELETE."""
        sel = self.tree.selection()
        if not sel:
            return
        id_, name = self.tree.item(sel[0], "values")
        if self.show_message_boxes and not messagebox.askyesno(
               "Confirm Delete", f"Delete entry {id_}: {name}?"):
            return
        try:
            req = urllib.request.Request(
                f"{self.webservice_url}/delete_xml_by_id/{id_}",
                method="DELETE"
            )
            with urllib.request.urlopen(req):
                pass
            self._load_list()
        except urllib.error.HTTPError as e:
            messagebox.showerror("Error", f"Delete failed:\nHTTP {e.code}: {e.reason}")
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed:\n{e}")

    # -------------------------------------------------
    # Load & Close Actions
    # -------------------------------------------------
    def _on_load(self):
        """Take the selection and close dialog."""
        sel = self.tree.selection()
        if not sel:
            return
        self.selected_id, self.selected_name = self.tree.item(sel[0], "values")
        self.destroy()

    def _on_close(self):
        """Close dialog without selection."""
        self.destroy()

    # -------------------------------------------------
    # Inline Rename & Double-Click
    # -------------------------------------------------
    def _on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        col    = self.tree.identify_column(event.x)
        row    = self.tree.identify_row(event.y)
        if region != "cell" or not row:
            return
        if col == "#1":
            self._on_load()
        elif col == "#2":
            self._edit_name(row)

    def _edit_name(self, row):
        """Inline-edit 'Name' and PUT to update_xml_name_by_id."""
        x, y, w, h = self.tree.bbox(row, "#2")
        old = self.tree.item(row, "values")[1]
        ent = tk.Entry(self.tree)
        ent.place(x=x, y=y, width=w, height=h)
        ent.insert(0, old)
        ent.focus()

        def save(evt=None):
            new = ent.get().strip()
            ent.destroy()
            if not new or new == old:
                return
            id_, _ = self.tree.item(row, "values")
            payload = json.dumps({"id": int(id_), "name": new}).encode('utf-8')
            req = urllib.request.Request(
                f"{self.webservice_url}/update_xml_name_by_id",
                data=payload,
                headers={"Content-Type":"application/json"},
                method="PUT"
            )
            try:
                with urllib.request.urlopen(req):
                    pass
                self.tree.set(row, column="Name", value=new)
            except urllib.error.HTTPError as e:
                messagebox.showerror("Error", f"Rename failed:\nHTTP {e.code}: {e.reason}")
            except Exception as e:
                messagebox.showerror("Error", f"Rename failed:\n{e}")

        ent.bind("<Return>", save)
        ent.bind("<FocusOut>", save)

    # -------------------------------------------------
    # Save-As Logic
    # -------------------------------------------------
    def _on_save_as(self):
        """
        Use the top entry to POST to /create_new_xml,
        then refresh and close with new selected_id/name.
        """
        name = self.entry_saveas.get().strip()
        if not name:
            messagebox.showwarning("Input Required", "Please enter a name for Save As.")
            return

        xml_data = self.tree_store._serialize_tree_to_xml()
        payload = json.dumps({"name": name, "xmlData": xml_data}).encode('utf-8')
        req = urllib.request.Request(
            f"{self.webservice_url}/create_new_xml",
            data=payload,
            headers={"Content-Type":"application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                new_id = result.get("id") or result.get("nextId")
        except Exception as e:
            messagebox.showerror("Error", f"Save As failed:\n{e}")
            return

        if self.show_message_boxes:
            messagebox.showinfo("Saved", f"Created new XML '{name}' (ID {new_id})")

        # Refresh, set and close
        self._load_list()
        self.selected_id = new_id
        self.selected_name = name
        self.destroy()
