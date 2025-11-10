import tkinter as tk
import tkinter.messagebox
from tkinter import ttk, filedialog
import random, json

CELL_SIZE = 8

STRUCTURE_TYPES = {
    "FLOATING_ABOVE_GROUND": {"id": 0},
    "ON_GROUND": {"id": 1},
    "UNDER_GROUND": {"id": 2}
}

class StructurePlacementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generator")

        self.canvas = tk.Canvas(root, width=640, height=640, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=12, padx=10, pady=10)

        self._build_controls()

        self.placements = []
        self.generate()

    def _build_controls(self):
        # World size X/Z
        ttk.Label(self.root, text="World Size X (chunks):").grid(row=0, column=1, sticky="w")
        self.world_x_var = tk.IntVar(value=128)
        ttk.Entry(self.root, textvariable=self.world_x_var, width=10).grid(row=0, column=2, sticky="w")

        ttk.Label(self.root, text="World Size Z (chunks):").grid(row=1, column=1, sticky="w")
        self.world_z_var = tk.IntVar(value=96)
        ttk.Entry(self.root, textvariable=self.world_z_var, width=10).grid(row=1, column=2, sticky="w")

        ttk.Label(self.root, text="Y min:").grid(row=3, column=1, sticky="w")
        self.y_min = tk.IntVar(value=0)
        ttk.Entry(self.root, textvariable=self.y_min, width=10).grid(row=3, column=2, sticky="w")

        ttk.Label(self.root, text="Y max:").grid(row=3, column=3, sticky="w")
        self.y_max = tk.IntVar(value=0)
        ttk.Entry(self.root, textvariable=self.y_max, width=10).grid(row=3, column=4, sticky="w")


        ttk.Label(self.root, text="Region Size (chunks):").grid(row=2, column=1, sticky="w")
        self.region_size_var = tk.IntVar(value=16)
        ttk.Entry(self.root, textvariable=self.region_size_var, width=10).grid(row=2, column=2, sticky="w")


        ttk.Label(self.root, text="Structure Id:").grid(row=4, column=1, sticky="w")
        self.structure_id = tk.IntVar(value=16)
        ttk.Entry(self.root, textvariable=self.structure_id, width=10).grid(row=4, column=2, sticky="w")



        # Fill rate (probability)
        ttk.Label(self.root, text="Placement chance (0-1):").grid(row=4, column=3, sticky="w")
        self.fill_rate_var = tk.DoubleVar(value=0.8)
        ttk.Entry(self.root, textvariable=self.fill_rate_var, width=10).grid(row=4, column=4, sticky="w")

        # Seed and buttons
        ttk.Label(self.root, text="Seed:").grid(row=5, column=1, sticky="w")
        self.seed_var = tk.StringVar(value="42")
        ttk.Entry(self.root, textvariable=self.seed_var, width=10).grid(row=5, column=2, sticky="w")

        ttk.Button(self.root, text="Generate", command=self.generate).grid(row=6, column=2, sticky="w")
        ttk.Button(self.root, text="Export JSON", command=self.export_json).grid(row=7, column=2, sticky="w")



    # --- Algorithm ---


    def generate_region_based(self, world_x, world_z, y_min, y_max, region_size, fill_rate, structure_id, seed=None):
        if seed:
            random.seed(seed)

        placements = []
        for region_x in range(0, world_x, region_size):
            for region_z in range(0, world_z, region_size):
                if random.random() > fill_rate:
                    continue

                # Add small jitter
                chunk_x = region_x + random.randint(-2, region_size + 1)
                chunk_z = region_z + random.randint(-2, region_size + 1)
                chunk_x = max(0, min(world_x - 1, chunk_x))
                chunk_z = max(0, min(world_z - 1, chunk_z))


                y = 0
                if y_min <= y_max:
                    y = random.randint(y_min, y_max)
                else:
                    print("Error: y_min is higher than y_max")
                    tkinter.messagebox.showwarning("WARNING", "Error: y_min is higher than y_max")
                    y_max = y_min



                placements.append((chunk_x, chunk_z, y, structure_id))
        return placements

    # --- GUI Logic ---

    def generate(self):
        self.canvas.delete("all")

        structure_id = self.structure_id.get()
        world_x = self.world_x_var.get()
        world_z = self.world_z_var.get()
        y_min = self.y_min.get()
        y_max = self.y_max.get()
        region_size = self.region_size_var.get()
        fill_rate = self.fill_rate_var.get()
        seed = self.seed_var.get().strip()
        seed = int(seed) if seed.isdigit() else None

        self.placements = self.generate_region_based(world_x, world_z, y_min, y_max, region_size, fill_rate, structure_id, seed)
        self.draw_grid(world_x, world_z)

    def draw_grid(self, world_x, world_z):
        grid_width_px = min(world_x * CELL_SIZE, 640)
        grid_height_px = min(world_z * CELL_SIZE, 640)
        self.canvas.config(width=grid_width_px, height=grid_height_px)

        for x in range(world_x):
            for z in range(world_z):
                color = "white"
                if any(px == x and pz == z for px, pz, _, _ in self.placements):
                    color = "red"
                self.canvas.create_rectangle(
                    x * CELL_SIZE,
                    z * CELL_SIZE,
                    (x + 1) * CELL_SIZE,
                    (z + 1) * CELL_SIZE,
                    fill=color,
                    outline="gray"
                )

    def export_json(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return

        data = [{"x": x * 16, "y": y, "z": z * 16, "type": t} for (x, z, y, t) in self.placements]
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Exported {len(data)} placements → {file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StructurePlacementApp(root)
    root.mainloop()
