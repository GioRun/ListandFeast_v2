import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

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
    {
        "name": "Veggie Tacos",
        "icon": "🌮",
        "tags": ["Mexican", "Vegetarian"],
        "ingredients": {"Taco Shells": "6", "Black Beans": "250g", "Cheddar Cheese": "50g", "Lettuce": "1 cup", "Salsa": "1/2 cup"},
        "instructions": "Warm taco shells. Fill with beans, lettuce, cheese, and salsa."
    },
    {
        "name": "Tofu Stir Fry",
        "icon": "🥦",
        "tags": ["Asian", "Vegetarian"],
        "ingredients": {"Tofu": "200g", "Mixed Vegetables": "2 cups", "Soy Sauce": "2 tbsp", "Garlic": "2 cloves", "Ginger": "1 tsp"},
        "instructions": "Stir fry garlic and ginger. Add vegetables and tofu. Cook until tender, add soy sauce."
    },
    {
        "name": "Vegan Pancakes",
        "icon": "🥞",
        "tags": ["Breakfast", "Sweet", "Vegan"],
        "ingredients": {"Flour": "1 cup", "Plant Milk": "1 cup", "Maple Syrup": "2 tbsp", "Baking Powder": "1 tsp"},
        "instructions": "Mix ingredients, pour batter on hot pan, cook until golden on both sides."
    },
    {
        "name": "Margherita Pizza",
        "icon": "🍕",
        "tags": ["Italian", "Pizza", "Vegetarian"],
        "ingredients": {"Pizza Dough": "1 base", "Tomato Sauce": "1/2 cup", "Mozzarella": "100g", "Basil": "handful"},
        "instructions": "Spread sauce on dough, top with cheese and basil, bake until golden."
    },
    {
        "name": "Lentil Soup",
        "icon": "🥣",
        "tags": ["Soup", "Vegan"],
        "ingredients": {"Lentils": "1 cup", "Carrots": "2", "Celery": "2 stalks", "Onion": "1", "Vegetable Stock": "4 cups"},
        "instructions": "Cook onion, carrots, celery until soft. Add lentils and stock, simmer until lentils are tender."
    },
    {
        "name": "Vegetarian Caesar Salad",
        "icon": "🥗",
        "tags": ["Salad", "Vegetarian"],
        "ingredients": {"Romaine Lettuce": "1 head", "Chickpea Croutons": "1 cup", "Parmesan Cheese": "50g", "Vegan Caesar Dressing": "1/4 cup"},
        "instructions": "Chop lettuce, add croutons and cheese, toss with dressing."
    },
    {
        "name": "Grilled Salmon",
        "icon": "🐟",
        "tags": ["Seafood", "Pescatarian"],
        "ingredients": {"Salmon Fillet": "200g", "Lemon": "1", "Olive Oil": "1 tbsp", "Salt": "to taste", "Pepper": "to taste"},
        "instructions": "Season salmon, grill for 4-5 minutes each side, squeeze lemon before serving."
    },
    {
        "name": "Prawn & Garlic Pasta",
        "icon": "🍤",
        "tags": ["Seafood", "Pescatarian", "Pasta"],
        "ingredients": {"Pasta": "200g", "Prawns": "150g", "Garlic": "2 cloves", "Olive Oil": "2 tbsp", "Parsley": "handful"},
        "instructions": "Cook pasta. Sauté garlic in olive oil, add prawns until cooked. Toss with pasta and parsley."
    }
]

class ListFeastApp:
    def __init__(self, root):
        self.root = root
        self.root.title("List & Feast")
        self.recipes = self.load_recipes()
        self.filtered_recipes = self.recipes.copy()
        self.init_ui()

    def load_recipes(self):
        if not os.path.exists("recipes.json"):
            with open("recipes.json", "w") as f:
                json.dump(DEFAULT_RECIPES, f, indent=4)
            return DEFAULT_RECIPES.copy()
        else:
            with open("recipes.json", "r") as f:
                return json.load(f)

    def save_recipes(self):
        with open("recipes.json", "w") as f:
            json.dump(self.recipes, f, indent=4)

    def init_ui(self):
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill='both', expand=True)

        # Top bar: Filter + Add button
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill="x", pady=(0, 10))

        self.tag_var = tk.StringVar(value="All")
        tags = ["All"] + sorted({tag for r in self.recipes for tag in r.get("tags", [])})
        for tag in tags:
            ttk.Radiobutton(self.top_frame, text=tag, value=tag,
                            variable=self.tag_var, command=self.apply_filter).pack(side="left", padx=3)

        ttk.Button(self.top_frame, text="Add Recipe", command=self.add_recipe).pack(side="right")

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

            ttk.Button(btn_frame, text="Edit", command=lambda r=recipe: self.edit_recipe(r)).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="Delete", command=lambda r=recipe: self.delete_recipe(r)).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="Copy", command=lambda r=recipe: self.copy_to_clipboard(r)).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="Print", command=lambda r=recipe: self.print_recipe(r)).pack(side="left", padx=2)

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

    def add_recipe(self):
        self.recipe_form()

    def edit_recipe(self, recipe):
        self.recipe_form(recipe)

    def delete_recipe(self, recipe):
        if messagebox.askyesno("Confirm Delete", f"Delete '{recipe['name']}'?"):
            self.recipes.remove(recipe)
            self.save_recipes()
            self.apply_filter()

    def recipe_form(self, recipe=None):
        form = tk.Toplevel(self.root)
        form.title("Recipe" if not recipe else f"Edit {recipe['name']}")

        tk.Label(form, text="Name:").pack()
        name_entry = tk.Entry(form)
        name_entry.pack()
        if recipe: name_entry.insert(0, recipe["name"])

        tk.Label(form, text="Icon:").pack()
        icon_entry = tk.Entry(form)
        icon_entry.pack()
        if recipe: icon_entry.insert(0, recipe.get("icon", ""))

        tk.Label(form, text="Tags (comma separated):").pack()
        tags_entry = tk.Entry(form)
        tags_entry.pack()
        if recipe: tags_entry.insert(0, ", ".join(recipe.get("tags", [])))

        tk.Label(form, text="Ingredients (one per line: qty ingredient):").pack()
        ing_text = tk.Text(form, height=5)
        ing_text.pack()
        if recipe:
            for ing, qty in recipe.get("ingredients", {}).items():
                ing_text.insert("end", f"{qty} {ing}\n")

        tk.Label(form, text="Instructions:").pack()
        instr_text = tk.Text(form, height=5)
        instr_text.pack()
        if recipe: instr_text.insert("end", recipe.get("instructions", ""))

        def save():
            name = name_entry.get().strip()
            icon = icon_entry.get().strip()
            tags = [t.strip() for t in tags_entry.get().split(",") if t.strip()]
            ingredients = {}
            for line in ing_text.get("1.0", "end").strip().split("\n"):
                if line.strip():
                    qty, *ing_parts = line.split(" ")
                    ingredients[" ".join(ing_parts)] = qty
            instructions = instr_text.get("1.0", "end").strip()

            if recipe:
                recipe.update({"name": name, "icon": icon, "tags": tags, "ingredients": ingredients, "instructions": instructions})
            else:
                self.recipes.append({"name": name, "icon": icon, "tags": tags, "ingredients": ingredients, "instructions": instructions})

            self.save_recipes()
            self.apply_filter()
            form.destroy()

        ttk.Button(form, text="Save", command=save).pack(pady=5)

if __name__ == '__main__':
    root = tk.Tk()
    app = ListFeastApp(root)
    root.mainloop()