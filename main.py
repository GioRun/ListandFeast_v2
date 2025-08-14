import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import defaultdict

class ListFeastApp:
    def __init__(self, root):
        self.root = root
        self.root.title("List & Feast")
        self.recipes = self.load_recipes()
        self.filtered_recipes = self.recipes.copy()
        self.init_ui()

    def load_recipes(self):
        try:
            with open("recipes.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showwarning("Missing File", "recipes.json not found.")
            return []

    def init_ui(self):
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill='both', expand=True)

        # Tag filter bar
        self.filter_frame = ttk.LabelFrame(self.main_frame, text="Filter by Tag")
        self.filter_frame.pack(fill='x')
        self.tag_var = tk.StringVar(value="All")
        tags = ["All"] + sorted({tag for r in self.recipes for tag in r.get("tags", [])})
        for tag in tags:
            b = ttk.Radiobutton(self.filter_frame, text=tag, value=tag, variable=self.tag_var, command=self.apply_filter)
            b.pack(side="left", padx=5)

        # Scrollable area
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.display_recipes()

    def display_recipes(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for recipe in self.filtered_recipes:
            card = ttk.LabelFrame(self.scrollable_frame, text=f"{recipe.get('icon', '')} {recipe['name']}", padding=10)
            card.pack(fill='x', pady=5)

            tags_str = ', '.join(recipe.get("tags", []))
            ttk.Label(card, text=f"Tags: {tags_str}").pack(anchor="w")
            for ing, qty in recipe.get("ingredients", {}).items():
                ttk.Label(card, text=f"• {qty} {ing}").pack(anchor="w")

            ttk.Label(card, text=f"Instructions: {recipe.get('instructions', 'No instructions')}").pack(anchor="w", pady=(5, 0))
            btn_frame = ttk.Frame(card)
            btn_frame.pack(anchor="e", pady=(5, 0))
            ttk.Button(btn_frame, text="Copy", command=lambda r=recipe: self.copy_to_clipboard(r)).pack(side="right", padx=5)
            ttk.Button(btn_frame, text="Print", command=lambda r=recipe: self.print_recipe(r)).pack(side="right", padx=5)

    def apply_filter(self):
        tag = self.tag_var.get()
        if tag == "All":
            self.filtered_recipes = self.recipes.copy()
        else:
            self.filtered_recipes = [r for r in self.recipes if tag in r.get("tags", [])]
        self.display_recipes()

    def copy_to_clipboard(self, recipe):
        content = f"{recipe['name']}\nTags: {', '.join(recipe.get('tags', []))}\n\nIngredients:\n"
        for ing, qty in recipe.get("ingredients", {}).items():
            content += f"- {qty} {ing}\n"
        content += f"\nInstructions:\n{recipe.get('instructions', '')}"
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()

    def print_recipe(self, recipe):
        content = f"{recipe['name']}\n\nIngredients:\n"
        for ing, qty in recipe.get("ingredients", {}).items():
            content += f"- {qty} {ing}\n"
        content += f"\nInstructions:\n{recipe.get('instructions', '')}"
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Recipe saved to {file_path}")

if __name__ == '__main__':
    root = tk.Tk()
    app = ListFeastApp(root)
    root.mainloop()