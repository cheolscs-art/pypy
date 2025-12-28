import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame
import os
import random

# --- 스타일 설정 (Denon Antique 테마) ---
SKIN_BG = "#d4c8b4"    
LCD_BG = "#000000"     
LCD_FG = "#00ff00"     
BTN_COLOR = "#e0d5c5"  

class DenonUltimatePlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("DENON Antique Audio System")
        self.root.geometry("460x720")
        self.root.configure(bg="#2d2d2d")
        self.root.resizable(False, False)

        pygame.mixer.init()
        
        self.playlist = []
        self.current_idx = -1
        self.is_paused = False
        self.song_length = 0
        self.is_dragging = False
        self.seek_offset = 0

        self.setup_ui()
        self.listbox.bind('<Delete>', lambda e: self.delete_selected_song())
        self.update_timer()

    def setup_ui(self):
        self.main_panel = tk.Frame(self.root, bg=SKIN_BG, bd=4, relief=tk.RAISED)
        self.main_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        display_frame = tk.Frame(self.main_panel, bg=LCD_BG, bd=5, relief=tk.SUNKEN)
        display_frame.place(x=15, y=15, width=420, height=150)

        self.time_label = tk.Label(display_frame, text="00:00 / 00:00", font=("Courier New", 18, "bold"), bg=LCD_BG, fg=LCD_FG)
        self.time_label.place(x=10, y=10)

        self.title_label = tk.Label(display_frame, text="INSERT DISC", font=("Arial", 10), bg=LCD_BG, fg=LCD_FG, anchor="w")
        self.title_label.place(x=10, y=50, width=390)

        self.canvas = tk.Canvas(display_frame, bg=LCD_BG, highlightthickness=0)
        self.canvas.place(x=10, y=80, width=390, height=60)
        self.bars = [self.canvas.create_rectangle(i*16, 60, i*16 + 12, 60, fill=LCD_FG, outline="") for i in range(24)]

        self.progress_scale = tk.Scale(
            self.main_panel, from_=0, to=100, orient=tk.HORIZONTAL,
            bg=SKIN_BG, troughcolor="#444", highlightthickness=0, showvalue=False,
            command=self.on_scale_touch
        )
        self.progress_scale.place(x=20, y=175, width=410)
        self.progress_scale.bind("<Button-1>", self.on_drag_start)
        self.progress_scale.bind("<ButtonRelease-1>", self.seek_music)

        # 버튼 섹션
        btn_frame = tk.Frame(self.main_panel, bg=SKIN_BG)
        btn_frame.place(x=20, y=220, width=410)
        
        # 기본 스타일에서 bg를 제외한 공통 스타일 정의
        common_ops = {"font": ("Arial", 9, "bold"), "relief": tk.RAISED, "bd": 3, "width": 5}
        
        tk.Button(btn_frame, text="◀◀", command=self.prev_song, bg=BTN_COLOR, **common_ops).grid(row=0, column=0, padx=3)
        # 에러 수정된 부분: bg를 중복되지 않게 한 번만 선언
        tk.Button(btn_frame, text="▶", command=self.play_song, bg="#0078d7", fg="white", **common_ops).grid(row=0, column=1, padx=3)
        tk.Button(btn_frame, text="||", command=self.pause_song, bg=BTN_COLOR, **common_ops).grid(row=0, column=2, padx=3)
        tk.Button(btn_frame, text="■", command=self.stop_song, bg=BTN_COLOR, **common_ops).grid(row=0, column=3, padx=3)
        tk.Button(btn_frame, text="▶▶", command=self.next_song, bg=BTN_COLOR, **common_ops).grid(row=0, column=4, padx=3)
        tk.Button(btn_frame, text="ADD", command=self.add_songs, bg="#bcae99", width=7, relief=tk.RAISED, bd=3).grid(row=0, column=5, padx=10)

        vol_frame = tk.Frame(self.main_panel, bg=SKIN_BG)
        vol_frame.place(x=20, y=275, width=410)

        tk.Label(vol_frame, text="VOLUME", bg=SKIN_BG, font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=5)
        self.vol_scale = tk.Scale(
            vol_frame, from_=0, to=100, orient=tk.HORIZONTAL,
            bg=SKIN_BG, troughcolor="#bcae99", highlightthickness=0, showvalue=False,
            command=self.set_volume
        )
        self.vol_scale.set(70)
        self.vol_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.vol_label = tk.Label(vol_frame, text="70%", bg=LCD_BG, fg=LCD_FG, font=("Courier New", 9, "bold"), width=5)
        self.vol_label.pack(side=tk.RIGHT, padx=5)

        list_tools = tk.Frame(self.main_panel, bg=SKIN_BG)
        list_tools.place(x=20, y=325, width=410)
        tk.Label(list_tools, text="TRACK LIST", bg=SKIN_BG, font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        tk.Button(list_tools, text="DELETE", command=self.delete_selected_song, bg="#cc0000", fg="white", font=("Arial", 8), bd=1).pack(side=tk.RIGHT)

        self.listbox = tk.Listbox(
            self.main_panel, bg="#1a1a1a", fg=SKIN_BG, 
            selectbackground=LCD_FG, selectforeground="black", 
            font=("Malgun Gothic", 10), bd=2, highlightthickness=0
        )
        self.listbox.place(x=20, y=350, width=410, height=310)
        self.listbox.bind("<Double-Button-1>", lambda e: self.play_song())

    # --- 기능 로직 (동일) ---

    def add_songs(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        for f in files:
            self.playlist.append(f)
            self.listbox.insert(tk.END, f"{len(self.playlist)}. {os.path.basename(f)}")

    def play_song(self):
        selected = self.listbox.curselection()
        if selected:
            self.current_idx = selected[0]
            path = self.playlist[self.current_idx]
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            
            sound = pygame.mixer.Sound(path)
            self.song_length = sound.get_length()
            self.progress_scale.config(to=self.song_length)
            self.seek_offset = 0
            self.title_label.config(text=os.path.basename(path).upper())
            self.is_paused = False

    def pause_song(self):
        if self.current_idx == -1: return
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.title_label.config(text="PAUSED")
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.title_label.config(text=os.path.basename(self.playlist[self.current_idx]).upper())

    def stop_song(self):
        pygame.mixer.music.stop()
        self.seek_offset = 0
        self.progress_scale.set(0)
        self.time_label.config(text="00:00 / 00:00")
        self.title_label.config(text="STOPPED")
        for bar in self.bars: self.canvas.coords(bar, self.canvas.coords(bar)[0], 60, self.canvas.coords(bar)[2], 60)

    def next_song(self):
        if self.current_idx < len(self.playlist) - 1:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.current_idx + 1)
            self.play_song()

    def prev_song(self):
        if self.current_idx > 0:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.current_idx - 1)
            self.play_song()

    def delete_selected_song(self):
        selected = self.listbox.curselection()
        if selected:
            idx = selected[0]
            if idx == self.current_idx: self.stop_song()
            self.listbox.delete(idx)
            self.playlist.pop(idx)
            current_items = [os.path.basename(f) for f in self.playlist]
            self.listbox.delete(0, tk.END)
            for i, name in enumerate(current_items): self.listbox.insert(tk.END, f"{i+1}. {name}")

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val)/100)
        self.vol_label.config(text=f"{val}%")

    def on_drag_start(self, event): self.is_dragging = True

    def on_scale_touch(self, val):
        if self.is_dragging and self.song_length > 0:
            curr_min, curr_sec = divmod(int(float(val)), 60)
            total_min, total_sec = divmod(int(self.song_length), 60)
            self.time_label.config(text=f"{curr_min:02}:{curr_sec:02} / {total_min:02}:{total_sec:02}")

    def seek_music(self, event):
        if self.current_idx != -1:
            target_time = self.progress_scale.get()
            self.seek_offset = target_time
            pygame.mixer.music.play(start=target_time)
            if self.is_paused: pygame.mixer.music.pause()
            self.is_dragging = False

    def update_timer(self):
        if pygame.mixer.music.get_busy() and not self.is_paused and not self.is_dragging:
            current_pos = self.seek_offset + (pygame.mixer.music.get_pos() / 1000)
            self.progress_scale.set(current_pos)
            curr_min, curr_sec = divmod(int(current_pos), 60)
            total_min, total_sec = divmod(int(self.song_length), 60)
            self.time_label.config(text=f"{curr_min:02}:{curr_sec:02} / {total_min:02}:{total_sec:02}")
            for bar in self.bars:
                h = random.randint(5, 55)
                x1, _, x2, _ = self.canvas.coords(bar)
                self.canvas.coords(bar, x1, 60-h, x2, 60)
        self.root.after(100, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = DenonUltimatePlayer(root)
    root.mainloop()