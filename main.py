import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import platform
import re

# ==============================
#  FILE PATHS & DEFAULTS
# ==============================
RECIPES_FILE = "recipes.json"
SETTINGS_FILE = "settings.json"

DEFAULT_RECIPES = [
    {
        "name": "Spaghetti Bolognese",
        "icon": "🍝",
        "tags": ["Italian", "Pasta", "Vegetarian"],
        "ingredients": {"Spaghetti": "200g", "Tomato Sauce": "1 cup", "Lentils": "150g"},
        "instructions": "Boil pasta. Cook lentils with tomato sauce. Mix together and serve hot."
    },
    {
        "name": "Chickpea Salad",
        "icon": "🥗",
        "tags": ["Healthy", "Salad", "Vegetarian"],
        "ingredients": {"Chickpeas": "200g", "Lettuce": "1 head", "Olive Oil": "2 tbsp"},
        "instructions": "Drain and rinse chickpeas. Chop lettuce. Toss with olive oil and chickpeas."
    },
    # ... (add other pescatarian/vegetarian defaults here)
]

# ==============================
#  MAIN APP CLASS
# ==============================
class ListFeastApp:
    def __init__(self, root):
        self.root = root
        self.root.title("List & Feast")

        # Load recipes & settings
        self.recipes = self.load_recipes()
        self.settings = self.load_settings()

        # Track selected recipes for shopping list
        self.selected_recipes = set(self.settings.get("selected_recipes", []))

        # Build UI
        self.init_ui()

        # Auto-open shopping list if selections exist
        if self.selected_recipes:
            self.open_shopping_list()

    # ==============================
    #  DATA LOADING / SAVING
    # ==============================
    def load_recipes(self):
        """Load recipes from file or create with defaults"""
        if not os.path.exists(RECIPES_FILE):
            with open(RECIPES_FILE, "w") as f:
                json.dump(DEFAULT_RECIPES, f, indent=4)
            return DEFAULT_RECIPES.copy()
        with open(RECIPES_FILE, "r") as f:
            return json.load(f)

    def save_recipes(self):
        """Save recipes to file"""
        with open(RECIPES_FILE, "w") as f:
            json.dump(self.recipes, f, indent=4)

    def load_settings(self):
        """Load settings from file or return defaults"""
        if not os.path.exists(SETTINGS_FILE):
            return {}
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)

    def save_settings(self):
        """Save settings to file"""
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f)

    # ==============================
    #  UI SETUP
    # ==============================
    def init_ui(self):
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill='both', expand=True)

        # Top bar
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(self.top_frame, text="View Shopping List", command=self.open_shopping_list).pack(side="right")
        ttk.Button(self.top_frame, text="Clear Selections", command=self.clear_selections).pack(side="right", padx=5)
        ttk.Button(self.top_frame, text="Add Recipe", command=self.add_recipe).pack(side="left")

        self.display_recipes()

    # ==============================
    #  DISPLAY RECIPES
    # ==============================
    def display_recipes(self):
        """Display all recipes with checkboxes and action buttons"""
        for widget in self.main_frame.pack_slaves():
            if widget not in [self.top_frame]:
                widget.destroy()

        for recipe in self.recipes:
            frame = ttk.LabelFrame(self.main_frame, text=f"{recipe.get('icon', '')} {recipe['name']}", padding=10)
            frame.pack(fill="x", pady=5)

            # Checkbox for selection
            var = tk.BooleanVar(value=recipe['name'] in self.selected_recipes)
            chk = ttk.Checkbutton(frame, variable=var,
                                  command=lambda r=recipe, v=var: self.toggle_selection(r, v))
            chk.pack(side="left")

            # Highlight if selected
            if recipe['name'] in self.selected_recipes:
                frame.config(style="Selected.TLabelframe")

            # Tags
            ttk.Label(frame, text=f"Tags: {', '.join(recipe.get('tags', []))}").pack(anchor="w")

            # Ingredients
            for ing, qty in recipe.get("ingredients", {}).items():
                ttk.Label(frame, text=f"• {qty} {ing}").pack(anchor="w")

            # Instructions (bulleted)
            bullets = "• " + "\n• ".join(recipe.get("instructions", "").split(". "))
            ttk.Label(frame, text=bullets, wraplength=500, justify="left").pack(anchor="w", pady=(5, 0))

            # Action buttons
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(anchor="e", pady=(5, 0))
            ttk.Button(btn_frame, text="Quick View", command=lambda r=recipe: self.quick_view(r)).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="Edit", command=lambda r=recipe: self.edit_recipe(r)).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="Delete", command=lambda r=recipe: self.delete_recipe(r)).pack(side="left", padx=2)

    # ==============================
    #  SELECTION LOGIC
    # ==============================
    def toggle_selection(self, recipe, var):
        """Add/remove recipe from selected set"""
        if var.get():
            self.selected_recipes.add(recipe['name'])
        else:
            self.selected_recipes.discard(recipe['name'])
        self.settings["selected_recipes"] = list(self.selected_recipes)
        self.save_settings()
        self.display_recipes()

    def clear_selections(self):
        self.selected_recipes.clear()
        self.settings["selected_recipes"] = []
        self.save_settings()
        self.display_recipes()

    # ==============================
    #  SHOPPING LIST
    # ==============================
    def open_shopping_list(self):
        """Open popup with merged shopping list and Quick View buttons"""
        popup = tk.Toplevel(self.root)
        popup.title("Shopping List")
        popup.geometry(self.settings.get("shopping_popup_geometry", "400x400"))

        # Save geometry on close
        def save_geom():
            self.settings["shopping_popup_geometry"] = popup.geometry()
            self.save_settings()
            popup.destroy()
        popup.protocol("WM_DELETE_WINDOW", save_geom)

        # Recipe quick view buttons
        for recipe in self.recipes:
            if recipe['name'] in self.selected_recipes:
                ttk.Button(popup, text=f"Quick View: {recipe['name']}",
                           command=lambda r=recipe: self.quick_view(r)).pack(fill="x", pady=2)

        # Editable shopping list
        text_box = tk.Text(popup)
        text_box.pack(fill="both", expand=True)
        text_box.insert("1.0", self.generate_shopping_list())

        # Save & copy buttons
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Copy", command=lambda: self.copy_to_clipboard(text_box.get("1.0", "end"))).pack(side="left")
        ttk.Button(btn_frame, text="Save as TXT", command=lambda: self.save_as_txt(text_box.get("1.0", "end"))).pack(side="left")

    def generate_shopping_list(self):
        """Merge and return ingredients from selected recipes"""
        merged = {}
        for recipe in self.recipes:
            if recipe['name'] in self.selected_recipes:
                for ing, qty in recipe.get("ingredients", {}).items():
                    if ing in merged:
                        merged[ing].append(qty)
                    else:
                        merged[ing] = [qty]
        return "\n".join([f"{', '.join(qtys)} {ing}" for ing, qtys in merged.items()])

    # ==============================
    #  QUICK VIEW
    # ==============================
    def quick_view(self, recipe):
        """Open large, stay-on-top guided cooking mode"""
        popup = tk.Toplevel(self.root)
        popup.title(f"{recipe['icon']} {recipe['name']}")
        popup.attributes("-topmost", True)

        ttk.Label(popup, text=f"{recipe['icon']} {recipe['name']}", font=("Arial", 20, "bold")).pack()
        ttk.Label(popup, text=f"Tags: {', '.join(recipe.get('tags', []))}").pack()

        ttk.Label(popup, text="Ingredients:", font=("Arial", 14, "underline")).pack(anchor="w")
        for ing, qty in recipe.get("ingredients", {}).items():
            ttk.Label(popup, text=f"• {qty} {ing}").pack(anchor="w")

        steps = recipe.get("instructions", "").split(". ")
        step_var = tk.IntVar(value=0)

        step_label = ttk.Label(popup, text=f"Step 1: {steps[0]}", wraplength=500, justify="left")
        step_label.pack(pady=10)

        def next_step():
            step = step_var.get() + 1
            if step < len(steps):
                step_var.set(step)
                step_label.config(text=f"Step {step+1}: {steps[step]}")

        def prev_step():
            step = step_var.get() - 1
            if step >= 0:
                step_var.set(step)
                step_label.config(text=f"Step {step+1}: {steps[step]}")

        nav_frame = ttk.Frame(popup)
        nav_frame.pack()
        ttk.Button(nav_frame, text="Previous", command=prev_step).pack(side="left", padx=5)
        ttk.Button(nav_frame, text="Next", command=next_step).pack(side="left", padx=5)

    # ==============================
    #  UTILS
    # ==============================
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def save_as_txt(self, text):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, "w") as f:
                f.write(text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ListFeastApp(root)
    root.mainloop()