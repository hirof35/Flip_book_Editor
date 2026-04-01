import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class FlipbookEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python アニメーションエディタ Pro")
        
        self.image_data = [] # {"name": str, "pil": Image, "tk": ImageTk}
        self.current_idx = 0
        self.is_playing = False

        # --- 全体レイアウト ---
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=10, pady=10)

        # 左側: プレビューエリア
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT)
        
        self.canvas = tk.Canvas(self.left_frame, width=400, height=400, bg="gray")
        self.canvas.pack()

        # 右側: リスト操作エリア
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(self.right_frame, text="コマの順番").pack()
        self.listbox = tk.Listbox(self.right_frame, width=30, height=20)
        self.listbox.pack()
        self.listbox.bind('<<ListboxSelect>>', self.on_select_list) 

        # 操作ボタン
        btn_set = tk.Frame(self.right_frame)
        btn_set.pack(pady=5)
        tk.Button(btn_set, text="↑ 上へ", command=lambda: self.move_item(-1)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_set, text="↓ 下へ", command=lambda: self.move_item(1)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_set, text="削除", command=self.delete_item, fg="red").pack(side=tk.LEFT, padx=5)

        # 下部: 再生・保存コントロール
        self.ctrl_frame = tk.Frame(root)
        self.ctrl_frame.pack(pady=10)
        
        tk.Button(self.ctrl_frame, text="画像を追加", command=self.load_images).pack(side=tk.LEFT, padx=5)
        tk.Button(self.ctrl_frame, text="再生/停止", command=self.toggle_play).pack(side=tk.LEFT, padx=5)
        tk.Button(self.ctrl_frame, text="GIF保存", command=self.save_as_gif, bg="lightblue").pack(side=tk.LEFT, padx=5)

        self.speed_scale = tk.Scale(root, from_=10, to=500, orient=tk.HORIZONTAL, label="再生速度(ms)")
        self.speed_scale.set(100)
        self.speed_scale.pack()

    def load_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if not file_paths: return
        
        for path in sorted(file_paths):
            name = path.split("/")[-1]
            pil_img = Image.open(path).convert("RGB").resize((400, 400))
            tk_img = ImageTk.PhotoImage(pil_img)
            self.image_data.append({"name": name, "pil": pil_img, "tk": tk_img})
            self.listbox.insert(tk.END, name)
        
        if self.image_data:
            self.show_frame(0)

    def on_select_list(self, event):
        selection = self.listbox.curselection()
        if selection:
            self.show_frame(selection[0])

    def show_frame(self, index):
        if 0 <= index < len(self.image_data):
            self.current_idx = index
            self.canvas.delete("all")
            self.canvas.create_image(200, 200, image=self.image_data[index]["tk"])

    def move_item(self, direction):
        selection = self.listbox.curselection()
        if not selection: return
        idx = selection[0]
        new_idx = idx + direction
        
        if 0 <= new_idx < len(self.image_data):
            # データの入れ替え
            self.image_data[idx], self.image_data[new_idx] = self.image_data[new_idx], self.image_data[idx]
            self.update_listbox(new_idx)

    def delete_item(self):
        selection = self.listbox.curselection()
        if not selection: return
        idx = selection[0]
        self.image_data.pop(idx)
        self.update_listbox(max(0, idx-1))

    def update_listbox(self, select_idx):
        self.listbox.delete(0, tk.END)
        for item in self.image_data:
            self.listbox.insert(tk.END, item["name"])
        if self.image_data:
            self.listbox.select_set(select_idx)
            self.show_frame(select_idx)

    def toggle_play(self):
        if not self.image_data: return
        self.is_playing = not self.is_playing
        if self.is_playing: self.animate()

    def animate(self):
        if self.is_playing and self.image_data:
            self.current_idx = (self.current_idx + 1) % len(self.image_data)
            self.show_frame(self.current_idx)
            self.root.after(self.speed_scale.get(), self.animate)

    def save_as_gif(self):
        if not self.image_data: return
        save_path = filedialog.asksaveasfilename(defaultextension=".gif")
        if save_path:
            pil_frames = [item["pil"] for item in self.image_data]
            pil_frames[0].save(save_path, save_all=True, append_images=pil_frames[1:], 
                               duration=self.speed_scale.get(), loop=0)
            messagebox.showinfo("完了", "保存しました！")

if __name__ == "__main__":
    root = tk.Tk()
    app = FlipbookEditor(root)
    root.mainloop()
