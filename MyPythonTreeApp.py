import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from FilesManagementStore import FilesManagementStore
from WebServiceManagementStore import WebServiceManagementStore
from AppConfig import AppConfig

class MyPythonTreeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Load persisted settings
        self.config_data = AppConfig().load()
        button_width = 12

        # -------------------------------------------------
        # Window setup
        # -------------------------------------------------
        self.title("MyPythonTreeApp - Debug Version 1.4.6")
        geom = f"{self.config_data.window_width}x{self.config_data.window_height}+{self.config_data.window_x}+{self.config_data.window_y}"
        self.geometry(geom)

        # -------------------------------------------------
        # Main paned window (splitter)
        # -------------------------------------------------
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # -------------------------------------------------
        # Left pane: TreeView
        # -------------------------------------------------
        self.tree_frame = tk.Frame(paned, bd=2, relief=tk.SUNKEN)
        paned.add(self.tree_frame, stretch="always")

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # TreeView bindings
        self.tree.bind("<Button-3>", self.show_tree_context_menu)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_drop)

        # -------------------------------------------------
        # Right pane: Controls & information
        # -------------------------------------------------
        self.right_frame = tk.Frame(paned, bd=2, relief=tk.SUNKEN)
        paned.add(self.right_frame, stretch="always")

        # -- Data Source display --
        top = tk.Frame(self.right_frame)
        top.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(top, text="Data Source:").grid(row=0, column=0, sticky="w")
        self.entry_data_source = tk.Entry(top, state="disabled")
        self.entry_data_source.grid(row=0, column=1, sticky="ew", padx=(5,0))
        self.entry_data_source.insert(0, self.config_data.data_source)
        top.grid_columnconfigure(1, weight=1)

        # -- Application title --
        tk.Label(self.right_frame,
                 text="MyPythonTreeApp",
                 font=("TkDefaultFont", 16, "bold"),
                 anchor="nw")\
          .pack(fill=tk.X, pady=(0,10), padx=5)

        # -- Description text --
        desc = (
            "With this small Python Tkinter application you can create nodes and sub-nodes\n"
            "in the TreeView on the left, change the text, delete them, save/load them\n"
            "from an XML file or web service, etc.\n\n"
            "Use the Context-Menu for actions (right-click on the TreeView)."
        )
        tk.Label(self.right_frame,
                 text=desc,
                 wraplength=300,
                 justify="left",
                 anchor="nw")\
          .pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # -------------------------------------------------
        # Bottom controls: settings and footer buttons
        # -------------------------------------------------
        bottom = tk.Frame(self.right_frame)
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=0)

        # -- Show message boxes & WebService URL --
        control = tk.Frame(bottom)
        control.grid(row=0, column=0, sticky="w")
        self.show_msg_var = tk.BooleanVar(value=self.config_data.show_message_boxes)
        tk.Checkbutton(control,
                       text="Show Message Boxes",
                       variable=self.show_msg_var,
                       command=self.on_show_msg_changed)\
          .pack(anchor="w")
        tk.Label(control, text="Web Service URL:").pack(anchor="w", pady=(5,0))
        self.entry_ws = tk.Entry(control, width=40)
        self.entry_ws.pack(anchor="w", fill=tk.X)
        self.entry_ws.insert(0, self.config_data.webservice_url)

        # -- Choose data source radios --
        rf = tk.LabelFrame(bottom, text="Choose the data source")
        rf.grid(row=0, column=1, sticky="e", padx=5)
        self.datasource_var = tk.StringVar(value=self.config_data.datasource_option)
        tk.Radiobutton(rf,
                       text="Files",
                       variable=self.datasource_var,
                       value="Files",
                       command=self.on_radio_changed)\
          .pack(anchor="w")
        tk.Radiobutton(rf,
                       text="Web Service",
                       variable=self.datasource_var,
                       value="WebService",
                       command=self.on_radio_changed)\
          .pack(anchor="w")

        # -- Footer buttons --
        footer = tk.Frame(bottom)
        footer.grid(row=1, column=0, columnspan=2, sticky="e", pady=(10,0))
        for txt, cmd in [
            ("Close", self.on_close_click),
            ("#3",    self.on_button3_click),
            ("#2",    self.on_button2_click),
            ("#1",    self.on_button1_click)
        ]:
            tk.Button(footer, text=txt, width=button_width, command=cmd)\
              .pack(side=tk.RIGHT, padx=2)

        # -------------------------------------------------
        # Initialize file & web‐service stores
        # -------------------------------------------------
        self.file_store = FilesManagementStore(
            treeview=self.tree,
            show_message_boxes=self.show_msg_var.get()
        )
        self.ws_store = WebServiceManagementStore(
            treeview=self.tree,
            webservice_url=self.config_data.webservice_url,
            show_message_boxes=self.show_msg_var.get()
        )

        # -------------------------------------------------
        # Context menu setup for TreeView
        # -------------------------------------------------
        self.tree_menu = tk.Menu(self, tearoff=False)

        menu_items = [
            ("Add Node",         self.add_node),
            ("Delete Node",      self.delete_node),
            ("Delete All Nodes", self.delete_all_nodes),
            ("Load Data",        self.load_tree),
            ("Save Data",        self.save_tree),
            ("Save As Data",     self.save_as_tree),
        ]

        for label, command in menu_items:
            if label == "Delete All Nodes":
                self.tree_menu.add_separator()  # separator before
                self.tree_menu.add_command(label=label, command=command)
                self.tree_menu.add_separator()  # separator after
            else:
                self.tree_menu.add_command(label=label, command=command)

    # -------------------------------------------------
    # Context menu action handlers
    # -------------------------------------------------
    def show_tree_context_menu(self, event):
        try:
            self.tree_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tree_menu.grab_release()

    def add_node(self):
        sel = self.tree.selection()
        self.tree.insert(sel[0] if sel else '', 'end', text="New Node")

    def delete_node(self):
        sel = self.tree.selection()
        if not sel:
            if self.show_msg_var.get():
                messagebox.showwarning("Select Node", "Please select a node to delete.")
            return
        if self.show_msg_var.get() and not messagebox.askyesno("Delete Node", "Are you sure?"):
            return
        for iid in sel:
            self.tree.delete(iid)

    def delete_all_nodes(self):
        if self.show_msg_var.get() and not messagebox.askyesno("Delete All Nodes", "Delete all nodes?"):
            return
        for iid in self.tree.get_children():
            self.tree.delete(iid)

    # -------------------------------------------------
    # Load / Save methods
    # -------------------------------------------------
    def load_tree(self):
        if self.datasource_var.get() == "Files":
            new_ds = self.file_store.load_tree(self.config_data.data_source)
        else:
            new_ds = self.ws_store.load_tree(self)
        if new_ds:
            self.config_data.data_source = new_ds
            self.entry_data_source.config(state="normal")
            self.entry_data_source.delete(0, tk.END)
            self.entry_data_source.insert(0, new_ds)
            self.entry_data_source.config(state="disabled")

    def save_tree(self):
        if self.datasource_var.get() == "Files":
            self.file_store.save_tree(self.config_data.data_source)
        else:
            self.ws_store.save_tree(self)

    def save_as_tree(self):
        if self.datasource_var.get() == "Files":
            new_ds = self.file_store.save_as_tree(self.config_data.data_source)
        else:
            new_ds = self.ws_store.save_as_tree(self)
        if new_ds:
            self.config_data.data_source = new_ds
            self.entry_data_source.config(state="normal")
            self.entry_data_source.delete(0, tk.END)
            self.entry_data_source.insert(0, new_ds)
            self.entry_data_source.config(state="disabled")

    # -------------------------------------------------
    # In-place editing of nodes
    # -------------------------------------------------
    def _on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        x, y, w, h = self.tree.bbox(item, "#0")
        entry = tk.Entry(self.tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, self.tree.item(item, "text"))
        entry.focus()

        def save(evt=None):
            self.tree.item(item, text=entry.get())
            entry.destroy()

        entry.bind("<Return>", save)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    # -------------------------------------------------
    # Drag-and-drop support
    # -------------------------------------------------
    def _on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            self._drag_item = None
            return
        self._drag_item = item
        text = self.tree.item(item, "text")
        self._ghost = tk.Toplevel(self)
        self._ghost.overrideredirect(True)
        self._ghost.attributes("-topmost", True)
        try:
            self._ghost.attributes("-alpha", 0.6)
        except:
            pass
        lbl = tk.Label(self._ghost, text=text, bg="#ddd", relief="solid", bd=1)
        lbl.pack()
        x, y = self.winfo_pointerx(), self.winfo_pointery()
        self._ghost.geometry(f"+{x+10}+{y+10}")

    def _on_drag_motion(self, event):
        if not getattr(self, "_drag_item", None):
            return
        try:
            x, y = self.winfo_pointerx(), self.winfo_pointery()
            self._ghost.geometry(f"+{x+10}+{y+10}")
        except:
            pass
        target = self.tree.identify_row(event.y)
        if hasattr(self, "_last_highlight"):
            self.tree.tag_configure(self._last_highlight, background="")
            del self._last_highlight
        if target and target != self._drag_item:
            tag = f"hl_{target}"
            self.tree.tag_configure(tag, background="#eef")
            self.tree.item(target, tags=(tag,))
            self._last_highlight = tag

    def _on_drag_drop(self, event):
        if hasattr(self, "_ghost"):
            self._ghost.destroy()
            del self._ghost
        if not getattr(self, "_drag_item", None):
            return

        target = self.tree.identify_row(event.y)

        if hasattr(self, "_last_highlight"):
            self.tree.tag_configure(self._last_highlight, background="")
            del self._last_highlight

        if target and target != self._drag_item:
            y_in_target = event.y - self.tree.bbox(target)[1]
            target_height = self.tree.bbox(target)[3]

            if y_in_target < target_height * 0.33:
                self._move_subtree(self._drag_item, target, position="before")
            elif y_in_target > target_height * 0.66:
                self._move_subtree(self._drag_item, target, position="after")
            else:
                self._move_subtree(self._drag_item, target, position="child")

        self._drag_item = None

    def _move_subtree(self, source, target, position="child"):
        def recurse(iid):
            return (self.tree.item(iid, "text"),
                    [recurse(c) for c in self.tree.get_children(iid)])

        data = recurse(source)
        self.tree.delete(source)

        def build(parent, node):
            txt, children = node
            if position == "before":
                index = self.tree.index(target)
                new_iid = self.tree.insert(self.tree.parent(target), index, text=txt)
            elif position == "after":
                index = self.tree.index(target) + 1
                new_iid = self.tree.insert(self.tree.parent(target), index, text=txt)
            else:
                new_iid = self.tree.insert(target, "end", text=txt)
            for c in children:
                build(new_iid, c)

        build(None, data)

    # -------------------------------------------------
    # Other event handlers
    # -------------------------------------------------
    def on_radio_changed(self):
        pass

    def on_show_msg_changed(self):
        val = self.show_msg_var.get()
        self.file_store.show_message_boxes = val
        self.ws_store.show_message_boxes = val

    def on_button1_click(self):
        print("Button1 clicked.")

    def on_button2_click(self):
        print("Button2 clicked.")

    def on_button3_click(self):
        print("Button3 clicked.")

    def on_close_click(self):
        # Persist settings before closing
        self.config_data.data_source = self.entry_data_source.get()
        self.config_data.show_message_boxes = self.show_msg_var.get()
        self.config_data.webservice_url = self.entry_ws.get().rstrip('/')
        self.config_data.datasource_option = self.datasource_var.get()

        # Save current window position and size
        self.update_idletasks()
        x = self.winfo_x()
        y = self.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        self.config_data.window_x = x
        self.config_data.window_y = y
        self.config_data.window_width = w
        self.config_data.window_height = h

        self.config_data.save()
        self.destroy()

if __name__ == "__main__":
    MyPythonTreeApp().mainloop()
