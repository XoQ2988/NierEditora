import logging
import shutil
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from typing import Optional

from nier_editora.core import Item
from nier_editora.core.constants import ITEM_LIST
from nier_editora.core.enums import ItemStatus
from nier_editora.core.i18n import translate_item
from nier_editora.core.save import SaveFile

logger = logging.getLogger(__name__)

COL_WIDTHS = {"idx":40, "qty":55, "lvl":55, "wgt":55}
MAX_QTY      = 99
MAX_WEAPON_L = 4
MAX_CHIP_W   = 99

class NierEditoraGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("NieR:Editora")
        self.resizable(False, False)

        # Internal state
        self.savefile: Optional[SaveFile] = None
        self.file_path: Optional[Path] = None
        self._has_unsaved: bool = False

        # Tk variables
        self.playtime_var   = tk.StringVar()
        self.player_name_var = tk.StringVar()
        self.money_var       = tk.IntVar()
        self.xp_var          = tk.IntVar()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._create_widgets()
        self.load_default()

    def load_default(self) -> None:
        self.player_name_var.set("2B")
        self.money_var.set(69000)
        self.xp_var.set(420)
        self.status.config(text="Ready")
        self.playtime_var.set("a long time")

        self.tree_items.insert("", "end", values=(8, translate_item(1), 1))
        self.tree_weapons.insert("", "end", values=(1, translate_item(1050), 3))
        self.tree_chips.insert("", "end", values=(1, translate_item(3338), 1, 2))

        self.update_idletasks()


    # UI Building
    def _create_widgets(self) -> None:
        # Configure overall padding
        main = ttk.Frame(self, padding=5)
        main.grid(column=0, row=0, sticky="NSEW")

        # Menu bar
        menubar = tk.Menu(self)
        # File menu
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open...",    command=self.load_save)
        file_menu.add_command(label="Save",       command=self.overwrite,   state="disabled")
        file_menu.add_command(label="Save As...", command=self.save_as,     state="disabled")
        file_menu.add_separator()
        file_menu.add_command(label="Exit",       command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=False)
        tools_menu.add_command(label="Validate Save", command=self._validate_save, state="disabled")
        tools_menu.add_separator()
        tools_menu.add_command(label="Backup Current Save...", command=self._backup_save, state="disabled")
        tools_menu.add_command(label="Restore Last Backup", command=self._restore_backup, state="disabled")
        tools_menu.add_separator()
        tools_menu.add_command(label="Export as PC Save...", command=self._export_pc, state="disabled")
        tools_menu.add_command(label="Export as Console Save...", command=self._export_console, state="disabled")
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)
        self._file_menu = file_menu
        self._tools_menu = tools_menu

        # Player Name
        ttk.Label(main, text="Name:").grid(row=0, column=0, sticky="W", pady=2)
        self.entry_name = ttk.Entry(main, textvariable=self.player_name_var,
                                width=15, state="disabled")
        self.entry_name.grid(row=0, column=1, sticky="EW")

        numeric = (self.register(lambda P: P.isdigit()), "%P")

        # Money
        ttk.Label(main, text="Money:").grid(row=1, column=0, sticky="W", pady=2)
        self.entry_money = ttk.Entry(main, textvariable=self.money_var,
                                width=15, state="disabled")
        self.entry_money.grid(row=1, column=1, sticky="EW")
        self.entry_money.configure(validate="key", validatecommand=numeric)

        # Playtime
        ttk.Label(main, text="Playtime:").grid(row=0, column=2, sticky="W", pady=2)
        self.entry_playtime = ttk.Entry(main, textvariable=self.playtime_var,
                                width=15, state="disabled")
        self.entry_playtime.grid(row=0, column=3, sticky="EW")

        # Experience
        ttk.Label(main, text="Experience:").grid(row=1, column=2, sticky="W", pady=2)
        self.entry_xp = ttk.Entry(main, textvariable=self.xp_var,
                                width=15, state="disabled")
        self.entry_xp.grid(row=1, column=3, sticky="EW")
        self.entry_xp.configure(validate="key", validatecommand=numeric)

        # Row 4: Notebook for inventories
        self.notebook = ttk.Notebook(main)
        self.notebook.grid(row=4, column=0, columnspan=4, sticky="NSEW", pady=(10, 0))
        main.rowconfigure(4, weight=1)

        # --- Items Tab ---
        items_frame = ttk.Frame(self.notebook)
        self.notebook.add(items_frame, text="Items")
        self.tree_items = self._make_tree(items_frame, [
            ("idx", "Index", COL_WIDTHS["idx"]), ("name", "Item Name", None), ("qty", "Quantity", COL_WIDTHS["qty"])])

        self.tree_items.bind("<Double-1>", self._on_item_double_click)

        # --- Weapons Tab ---
        weapons_frame = ttk.Frame(self.notebook)
        self.notebook.add(weapons_frame, text="Weapons")
        self.tree_weapons = self._make_tree(weapons_frame, [
            ("idx", "Index", COL_WIDTHS["idx"]), ("name", "Weapon", None), ("lvl", "Level", COL_WIDTHS["lvl"])])

        self.tree_weapons.bind("<Double-1>", self._on_weapon_double_click)

        # --- Chips Tab ---
        chips_frame = ttk.Frame(self.notebook)
        self.notebook.add(chips_frame, text="Chips")
        self.tree_chips = self._make_tree(chips_frame, [
            ("idx", "Index", COL_WIDTHS["idx"]), ("name", "Chip", None),
            ("lvl", "Level", COL_WIDTHS["lvl"]), ("wgt", "Weight", COL_WIDTHS["wgt"])])

        self.tree_chips.bind("<Double-1>", self._on_chip_double_click)
        self.tree_items.bind("<<TreeviewSelect>>", lambda e: self._update_item_buttons())

        # Add/Remove buttons
        btn_frame = ttk.Frame(main, padding=(2, 0))
        btn_frame.grid(row=4, column=3, sticky="NE", pady=(4, 0))
        self.btn_add = ttk.Button(btn_frame, text="+", width=3, command=self._add_item, state="disabled")
        self.btn_add.pack(side="right")
        self.btn_remove = ttk.Button(btn_frame, text="–", width=3, command=self._remove_item, state="disabled")
        self.btn_remove.pack(side="right", padx=5)

        # Status bar
        self.status = ttk.Label(main, text="Loading", anchor="w")
        self.status.grid(row=5, column=0, sticky="EW", columnspan=4)

        # Bind change tracking
        self.entry_name.bind("<KeyRelease>", lambda e: self._mark_dirty())
        self.entry_money.bind("<KeyRelease>", lambda e: self._mark_dirty())
        self.entry_playtime.bind("<KeyRelease>", lambda e: self._mark_dirty())
        self.entry_xp.bind("<KeyRelease>", lambda e: self._mark_dirty())

    def _make_tree(self, parent, cols):
        tree = ttk.Treeview(parent, columns=tuple(c[0] for c in cols), show="headings", height=8)
        for i, (col, heading, width) in enumerate(cols, start=1):
            self._enable_sorting(tree, col)
            tree.heading(col, text=heading)
            if width:
                tree.column(col, width=width, anchor="n", stretch=False)
            else:
                tree.column(col, anchor="w")
        self._disable_column_resize(tree)
        tree.pack(fill="both", expand=True)

        return tree

    # File actions
    def load_save(self, path: Optional[Path] = None) -> None:
        if not path:
            path = filedialog.askopenfilename(
                title="Select NieR:Automata Save File",
                filetypes=(
                    ("PC Save Files", "SlotData_*.dat"),
                    ("Console Save Files", "GameData"),
                    ("All files", "*.*"),
                )
            )
            if not path:
                return
            self.file_path = Path(path)
        else:
            self.file_path = path

        try:
            self.savefile = SaveFile.load_from_file(self.file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load save:\n{e}")
            return

        # Populate fields
        self.player_name_var.set(self.savefile.player_name)
        self.money_var.set(self.savefile.money)

        # Format playtime hh:mm:ss
        total = self.savefile.play_time
        h, rem = divmod(total, 3600)
        m, s   = divmod(rem, 60)
        self.playtime_var.set(f"{h:02d}:{m:02d}:{s:02d}")

        self.xp_var.set(self.savefile.xp)

        self._populate_items()
        self._populate_weapons()
        self._populate_chips()

        # Enable editing & saving
        for w in (
                self.entry_name, self.entry_money, self.entry_xp,
                self.entry_playtime, self.btn_add
        ): w.state(["!disabled"])

        self._set_menu_state(self._file_menu, Save="normal", **{"Save As...": "normal"})
        self._set_menu_state(self._tools_menu, **{
                                 "Validate Save": "normal",
                                 "Backup Current Save...": "normal",
                                 "Restore Last Backup": "normal",
                                 "Export as PC Save...": "normal",
                                 "Export as Console Save...": "normal"
                             })

        self._has_unsaved = False
        self.status.config(text=f"Loaded '{self.savefile.player_name}'")
        self.title(f"NieR:Editora - {self.file_path.name}")

    def overwrite(self) -> None:
        if not self.file_path:
            return
        self.save_as(self.file_path)
        self.status.config(text=f"Saved '{self.file_path.name}'")

    def save_as(self, path: Optional[Path] = None) -> None:
        if not self.savefile:
            return

        if not path:
            filename = filedialog.asksaveasfilename(
                title="Save As...",
                filetypes=(
                    ("PC Save Files", "SlotData_*.dat"),
                    ("Console Save Files", "GameData"),
                    ("All files", "*.*"),
                )
            )
            if not filename:
                return
            path = Path(filename)

        try:
            self.apply_changes()
            self.savefile.save_to_file(path)
            self._has_unsaved = False
            self._set_menu_state(self._file_menu, Save="disabled", **{"Save As...": "disabled"})
            logger.info("Saved file %s", path)
        except Exception as e:
            logger.exception("Save failed")
            messagebox.showerror("Save Error", str(e))

    # Tool menu actions
    def _validate_save(self):
        try:
            raw = self.file_path.read_bytes()
            SaveFile().load(raw)
            messagebox.showinfo("Validate", "Save file is valid.")
        except Exception as e:
            messagebox.showerror("Validate Error", f"Validation failed:\n{e}")

    def _backup_save(self):
        dst = self.file_path.with_suffix(self.file_path.suffix + f".{int(time.time())}.bak")
        shutil.copy2(self.file_path, dst)
        messagebox.showinfo("Backup", f"Backup created:\n{dst.name}")

    def _restore_backup(self):
        pattern = f"{self.file_path.name}.*.bak"
        bak_files = sorted(self.file_path.parent.glob(pattern))
        if not bak_files:
            messagebox.showwarning("Restore", "No backups found.")
            return
        latest = bak_files[-1]
        shutil.copy2(latest, self.file_path)
        messagebox.showinfo("Restore", f"Restored from:\n{latest.name}")
        self.load_save(self.file_path)

    def _export(self, to_console: bool):
        if not self.savefile: return
        orig = self.savefile.is_console
        self.savefile.is_console = to_console
        data = self.savefile.write()
        self.savefile.is_console = orig

        EXPORT_OPTS = {
            False: dict(title="Export as PC Save...",
                        defaultextension=".dat",
                        filetypes=[("PC Save File", "*.dat")]),
            True: dict(title="Export as Console Save...",
                       defaultextension="",
                       filetypes=[("GameData", "GameData")]),
        }
        opts = EXPORT_OPTS[to_console]
        path = filedialog.asksaveasfilename(**opts)

        if not path: return
        try:
            Path(path).write_bytes(data)
            self.status.config(text=f"Exported {EXPORT_OPTS[to_console]} save to {Path(path).name}")
        except Exception as e:
            logger.exception("Export failed")
            messagebox.showerror("Export Error", str(e))

    def _export_pc(self): self._export(to_console=False)

    def _export_console(self): self._export(to_console=True)


    # Populate views
    def _populate_items(self):
        self.tree_items.delete(*self.tree_items.get_children())
        for item in self.savefile.inventory:
            self.tree_items.insert(
                "", "end",
                iid=str(item.index),
                values=(item.index, item.name, item.quantity)
            )

    def _populate_weapons(self):
        self.tree_weapons.delete(*self.tree_weapons.get_children())
        for weapon in self.savefile.weapons:
            self.tree_weapons.insert(
                "", "end",
                iid=str(weapon.index),
                values=(weapon.index, weapon.name, weapon.level)
            )

    def _populate_chips(self):
        self.tree_chips.delete(*self.tree_chips.get_children())
        for chip in self.savefile.chips:
            self.tree_chips.insert(
                "", "end",
                iid=str(chip.index),
                values=(chip.index, chip.name, chip.level, chip.weight)
            )


    # In-place editing handlers
    def _on_item_double_click(self, event):
        row_id = self.tree_items.identify_row(event.y)
        col    = self.tree_items.identify_column(event.x)

        if not row_id or col != "#3" or not self.savefile:
            return

        index = int(row_id)
        item = self.savefile.inventory.raw[index]

        new_qty = simpledialog.askinteger(
            "Edit Quantity",
            f"Set new quantity for {item.name}",
            parent=self,
            initialvalue=item.quantity, minvalue=0, maxvalue=MAX_QTY
        )
        if new_qty is None or new_qty == item.quantity:
            return

        self.savefile.inventory.raw[index].quantity = new_qty
        self.tree_items.item(row_id, values=(item.index, item.name, new_qty))

        self._mark_dirty()

    def _on_weapon_double_click(self, event):
        row_id = self.tree_weapons.identify_row(event.y)
        col    = self.tree_weapons.identify_column(event.x)

        if not row_id or col != "#3" or not self.savefile:
            return

        index = int(row_id)
        weapon = self.savefile.weapons.raw[index]

        new_lvl = simpledialog.askinteger(
            "Edit Level",
            f"Set new Level for {weapon.name}",
            parent=self,
            initialvalue=weapon.level, minvalue=0, maxvalue=MAX_WEAPON_L
        )
        if new_lvl is None or new_lvl == weapon.level:
            return

        self.savefile.weapons.raw[index].level = new_lvl
        self.tree_weapons.item(row_id, values=(weapon.index, weapon.name, new_lvl))

        self._mark_dirty()

    def _on_chip_double_click(self, event):
        row_id = self.tree_chips.identify_row(event.y)
        col    = self.tree_chips.identify_column(event.x)

        if not row_id or col != "#3" or not self.savefile:
            return

        index = int(row_id)
        chip = self.savefile.chips.raw[index]

        new_wgt = simpledialog.askinteger(
            "Edit Weight",
            f"Set new Weight for {chip.name}",
            parent=self,
            initialvalue=chip.weight, minvalue=0, maxvalue=MAX_CHIP_W
        )
        if new_wgt is None or new_wgt == chip.weight:
            return

        self.savefile.chips.raw[index].weight = new_wgt
        self.tree_chips.item(row_id, values=(chip.index, chip.name, chip.level, new_wgt))

        self._mark_dirty()


    # Misc
    def _update_item_buttons(self):
        # Only enable “+” if a save is loaded
        if self.savefile:
            self.btn_add.state(["!disabled"])
        else:
            self.btn_add.state(["disabled"])

        # Enable “–” only when a non‑empty slot is selected
        sel = self.tree_items.selection()
        if self.savefile and sel:
            idx = int(sel[0])
            slot = self.savefile.inventory.raw[idx]
            if slot.id != -1:
                self.btn_remove.state(["!disabled"])
                return
        self.btn_remove.state(["disabled"])

    def _select_item_dialog(self) -> Optional[int]:
        # Only include inventory items and fish
        ALLOWED_PREFIXES = ("item_", "fish_")
        raw_items = {
            k: v for k, v in ITEM_LIST.items()
            if any(v.startswith(pref) for pref in ALLOWED_PREFIXES)
        }

        # Sort by ID
        items = sorted(raw_items.items(), key=lambda kv: kv[0])

        dialog = tk.Toplevel(self)
        dialog.title("Select Item")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("300x400")

        # Filter entry
        ttk.Label(dialog, text="Filter:").pack(anchor="w", padx=5, pady=(5, 0))
        filter_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=filter_var)
        entry.pack(fill="x", padx=5)

        # Listbox + scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        listbox = tk.Listbox(frame)
        listbox.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        sb.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=sb.set)

        def format_entry(k, raw):
            name = translate_item(k) or raw
            return f"{hex(k)}: {name}"

        # Populate full list
        for k, raw in items:
            listbox.insert("end", format_entry(k, raw))

        # Filter callback
        def on_filter(*_):
            flt = filter_var.get().lower()
            listbox.delete(0, "end")
            for k, raw in items:
                name = translate_item(k) or raw
                if flt in name.lower() or flt in hex(k):
                    listbox.insert("end", format_entry(k, raw))

        filter_var.trace_add("write", on_filter)

        # Capture selection
        selection: dict = {"id": None}

        def choose(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            text = listbox.get(sel[0])
            id_str = text.split(":", 1)[0]
            selection["id"] = int(id_str, 16)
            dialog.destroy()

        listbox.bind("<Double-Button-1>", choose)

        # OK / Cancel
        btns = ttk.Frame(dialog)
        btns.pack(fill="x", pady=(0, 5))
        ttk.Button(btns, text="OK", command=choose).pack(side="left", padx=5)
        ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)

        entry.focus()
        self.wait_window(dialog)
        return selection["id"]

    def _add_item(self):
        new_id = self._select_item_dialog()
        if new_id is None:
            return

        inv = self.savefile.inventory.raw
        for slot in inv:
            print(slot)
            if slot.id == -1:
                idx = slot.index
                break
        else:
            messagebox.showwarning("Inventory Full", "No empty slots available.")
            return


        new_slot = Item.empty(idx)
        new_slot.id = new_id
        new_slot.quantity = 1
        self.savefile.inventory.raw[idx] = new_slot

        print(new_slot)

        self.status.config(text=f"Added {self.savefile.inventory.raw[idx].name} at slot {idx}")
        self._populate_items()
        self._mark_dirty()

    def _remove_item(self):
        if not self.savefile:
            return

        sel = self.tree_items.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return

        idx = int(sel[0])

        # Replace with an empty slot
        self.savefile.inventory.raw[idx] = Item.empty(idx)

        # Refresh & mark dirty
        self._populate_items()
        self._mark_dirty()

    def _mark_dirty(self):
        self._has_unsaved = True
        self._set_menu_state(self._file_menu, Save="normal", **{"Save As...": "normal"})

    def apply_changes(self) -> None:
        if not self.savefile:
            return

        self.savefile.player_name = self.player_name_var.get()
        self.savefile.money = self.money_var.get()
        self.savefile.xp = self.xp_var.get()

        # parse playtime HH:MM:SS → seconds
        try:
            pt = self.playtime_var.get().split(":")
            h, m, s = map(int, pt)
            total_seconds = h * 3600 + m * 60 + s
            self.savefile.play_time = total_seconds
        except ValueError:
            messagebox.showwarning("Invalid Time", "Playtime must be in HH:MM:SS format")
            total = self.savefile.play_time
            h, rem = divmod(total, 3600)
            m, s = divmod(rem, 60)
            self.playtime_var.set(f"{h:02d}:{m:02d}:{s:02d}")

        # Disable saving until next change
        self._file_menu.entryconfig("Save", state="disabled")
        self._file_menu.entryconfig("Save As...", state="disabled")

        self.status.config(text="Unsaved changes")

    @staticmethod
    def _set_menu_state(menu: tk.Menu, **items: str) -> None:
        for label, state in items.items():
            try:
                menu.entryconfig(label, state=state)
            except tk.TclError:
                logger.warning("Menu item %r not found", label)

    @staticmethod
    def _disable_column_resize(tree: ttk.Treeview):
        def handler(event):
            region = tree.identify_region(event.x, event.y)
            if region == "separator":
                return "break"

        tree.bind("<Button-1>", handler, add=True)

    def _enable_sorting(self, tree: ttk.Treeview, col: str, reverse: bool = False):
        def handler():
            data = [(tree.set(k, col), k) for k in tree.get_children("")]
            try:
                data.sort(key=lambda t: float(t[0]), reverse=reverse)
            except ValueError:
                data.sort(key=lambda t: t[0], reverse=reverse)
            for index, (_, k) in enumerate(data):
                tree.move(k, "", index)

            tree.heading(col, command=lambda: self._enable_sorting(tree, col, not reverse))

        tree.heading(col, command=handler)

    @staticmethod
    def _show_about():
        messagebox.showinfo(
            "About NieR:Editora",
            "NieR:Editora v0.1.0\nby XoQ2988\nhttps://github.com/XoQ2988/NierEditora"
        )

    def _on_close(self):
        if self._has_unsaved:
            if not messagebox.askyesno("Quit", "You have unsaved changes. Quit anyway?"):
                return
        self.destroy()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
    app = NierEditoraGUI()
    app.mainloop()
