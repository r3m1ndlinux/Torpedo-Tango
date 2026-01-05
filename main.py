import customtkinter as ctk
import random
from tkinter import messagebox
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class BattleshipApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Torpedo Tango")
        self.geometry("1200x800")
        self.configure(bg= "black")
        self.iconbitmap(resource_path("icon.ico"))
        
        self.after(0, lambda: self.state('zoomed'))

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.ship_info = {
            "Carrier": {"length": 5, "char": "C", "color": "#1A5276"},
            "Battleship": {"length": 4, "char": "B", "color": "#21618C"},
            "Cruiser": {"length": 3, "char": "R", "color": "#2874A6"},
            "Submarine": {"length": 3, "char": "S", "color": "#2E86C1"},
            "Destroyer": {"length": 2, "char": "D", "color": "#3498DB"}
        }
        self.char_to_name = {v["char"]: k for k, v in self.ship_info.items()}

        self.player_board = self.create_empty_board()
        self.computer_board = self.create_empty_board()
        
        self.player_buttons = []
        self.computer_buttons = []
        self.status_indicators = {"Player": {}, "Computer": {}}

        self.game_over = False
        self.setup_mode = True
        self.turn = "Setup"
        self.player_name = "Commander"
        
        self.ships_to_place = []
        self.placement_orientation = "horizontal"
        
        self.player_health = {}
        self.computer_health = {}
        self.computer_target_queue = []
        
        self.layout_mode = "horizontal"

        self.create_widgets()
        
        self.after(200, self.ask_name_and_start)
        
        self.bind("<Configure>", self.on_resize)

    def create_empty_board(self):
        return [["~" for _ in range(10)] for _ in range(10)]

    def ask_name_and_start(self):
        dialog = ctk.CTkInputDialog(text="Enter your name, Commander:", title="Identity Verification")
        name = dialog.get_input()
        if name:
            self.player_name = name
        self.new_game()

    def place_ships_random(self, board, health_dict):
        for name in self.ship_info:
            health_dict[name] = 0

        for ship_name, info in self.ship_info.items():
            length = info["length"]
            char = info["char"]
            placed = False
            while not placed:
                orientation = random.choice(["horizontal", "vertical"])
                row = random.randint(0, 9)
                col = random.randint(0, 9 - length if orientation == "horizontal" else 10 - 1)

                if self.is_valid_placement(board, row, col, orientation, length):
                    placed = True
                    for i in range(length):
                        if orientation == "horizontal":
                            board[row][col + i] = char
                        else:
                            board[row + i][col] = char

    def is_valid_placement(self, board, row, col, orientation, length):
        if orientation == "horizontal":
            for i in range(length):
                if (
                    row < 0 or row >= 10 or col + i < 0 or col + i >= 10
                    or board[row][col + i] != "~"
                ):
                    return False
        else:
            for i in range(length):
                if (
                    row + i < 0 or row + i >= 10 or col < 0 or col >= 10
                    or board[row + i][col] != "~"
                ):
                    return False
        return True

    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.title_label = ctk.CTkLabel(self.main_container, text="Torpedo Tango", font=("Impact", 48), text_color="#3498DB")
        self.title_label.pack(pady=(60, 20))

        self.boards_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.boards_frame.pack(expand=True, fill="both")
        
        self.boards_frame.grid_columnconfigure(0, weight=1)
        self.boards_frame.grid_columnconfigure(1, weight=0)
        self.boards_frame.grid_columnconfigure(2, weight=1)
        self.boards_frame.grid_rowconfigure(0, weight=1)

        self.left_container = ctk.CTkFrame(self.boards_frame, fg_color="transparent")

        self.player_frame = ctk.CTkFrame(self.left_container, fg_color="#1a1a1a")
        self.player_frame.pack()
        self.player_title = ctk.CTkLabel(self.player_frame, text="YOUR FLEET", font=("Roboto", 16, "bold"))
        self.player_title.grid(row=0, column=0, columnspan=11, pady=5)
        
        self.player_status_frame = ctk.CTkFrame(self.left_container, fg_color="#222222")
        self.player_status_frame.pack(fill="x", pady=10)

        self.center_container = ctk.CTkFrame(self.boards_frame, fg_color="transparent")
        
        self.message_frame = ctk.CTkFrame(self.center_container, width=400, height=100, fg_color="transparent")
        self.message_frame.pack(pady=(80, 10))
        self.message_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(self.message_frame, text="Initializing...", font=("Roboto Medium", 20), text_color="white", wraplength=380)
        self.status_label.pack(expand=True, fill="both")

        self.setup_buttons_frame = ctk.CTkFrame(self.center_container, width=400, height=100, fg_color="transparent")
        self.setup_buttons_frame.pack(pady=10)
        self.setup_buttons_frame.pack_propagate(False)
        self.setup_buttons_frame.grid_columnconfigure(0, weight=1)
        self.setup_buttons_frame.grid_columnconfigure(1, weight=1)
        
        self.random_btn = ctk.CTkButton(self.setup_buttons_frame, text="Randomize", command=self.random_place_player_ships, width=140, fg_color="#d35400", hover_color="#e67e22")
        self.rotate_btn = ctk.CTkButton(self.setup_buttons_frame, text="Rotate Ship: Horizontal", command=self.toggle_orientation, width=200)
        self.ready_btn = ctk.CTkButton(self.setup_buttons_frame, text="DEPLOY FLEET", command=self.finish_setup, width=200, fg_color="#27ae60", hover_color="#2ecc71")

        self.right_container = ctk.CTkFrame(self.boards_frame, fg_color="transparent")

        self.computer_frame = ctk.CTkFrame(self.right_container, fg_color="#1a1a1a")
        self.computer_frame.pack()
        ctk.CTkLabel(self.computer_frame, text="ENEMY WATERS", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=11, pady=5)

        self.computer_status_frame = ctk.CTkFrame(self.right_container, fg_color="#222222")
        self.computer_status_frame.pack(fill="x", pady=10)

        self.create_board_grid(self.player_frame, self.player_buttons, is_player=True)
        self.create_board_grid(self.computer_frame, self.computer_buttons, is_player=False)
        
        self.create_status_panel(self.player_status_frame, "Player")
        self.create_status_panel(self.computer_status_frame, "Computer")

        self.new_game_button = ctk.CTkButton(self.center_container, text="NEW GAME", font=("Roboto", 14, "bold"), height=40, command=self.confirm_new_game, fg_color="#2ecc71", hover_color="#27ae60")
        self.new_game_button.pack(pady=(30, 10))
        
        self.instructions_btn = ctk.CTkButton(self.center_container, text="INSTRUCTIONS", font=("Roboto", 12, "bold"), height=30, command=self.show_instructions, fg_color="#7f8c8d", hover_color="#95a5a6")
        self.instructions_btn.pack(pady=10)

        self.update_layout()

    def on_resize(self, event):
        if event.widget != self:
            return
            
        width = self.winfo_width()
        new_mode = "horizontal" if width >= 1100 else "vertical"
        
        if new_mode != self.layout_mode:
            self.layout_mode = new_mode
            self.update_layout()

    def update_layout(self):
        if self.layout_mode == "vertical":
            self.left_container.grid(row=0, column=0, sticky="ew", padx=10)
            
            self.center_container.grid(row=1, column=0, sticky="ew", pady=20)
            
            self.right_container.grid(row=2, column=0, sticky="ew", padx=10)
        else:
            self.left_container.grid(row=0, column=0, sticky="nsew", padx=10)
            
            self.center_container.grid(row=0, column=1, sticky="ns", pady=20)
            
            self.right_container.grid(row=0, column=2, sticky="nsew", padx=10)

    def create_status_panel(self, frame, owner):
        ctk.CTkLabel(frame, text=f"{owner} Fleet Status", font=("Roboto", 16, "bold")).pack(pady=5)
        self.status_indicators[owner] = {}

        grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=5)
        
        for i, (ship_name, info) in enumerate(self.ship_info.items()):
            name_lbl = ctk.CTkLabel(grid_frame, text=ship_name, font=("Roboto", 12, "bold"), anchor="w")
            name_lbl.grid(row=i, column=0, sticky="w", padx=(0, 10), pady=2)
            
            pips_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            pips_frame.grid(row=i, column=1, sticky="w")
            
            pips = []
            for _ in range(info["length"]):
                pip = ctk.CTkLabel(pips_frame, text="•", font=("Arial", 18), width=20, text_color="#555555") 
                pip.pack(side="left", padx=1)
                pips.append(pip)
            
            self.status_indicators[owner][ship_name] = pips

    def update_status_ui(self):
        for owner in ["Player", "Computer"]:
            health_dict = self.player_health if owner == "Player" else self.computer_health
            for ship, hits in health_dict.items():
                pips = self.status_indicators[owner][ship]
                max_hits = self.ship_info[ship]["length"]
                base_color = self.ship_info[ship]["color"] if owner == "Player" else "#555555"
                
                for i in range(max_hits):
                    if i < hits:
                        pips[i].configure(text="X", text_color="#e74c3c")
                    else:
                        pips[i].configure(text="•", text_color=base_color)

    def create_board_grid(self, frame, button_list, is_player):
        row_labels = [chr(ord('A') + i) for i in range(10)]
        col_labels = [str(i+1) for i in range(10)]

        for i, col_label in enumerate(col_labels):
            header_label = ctk.CTkLabel(frame, text=col_label, width=30, height=30)
            header_label.grid(row=1, column=i+1)

        for i, row_label in enumerate(row_labels):
            header_label = ctk.CTkLabel(frame, text=row_label, width=30, height=30)
            header_label.grid(row=i+2, column=0)

        for row in range(10):
            button_row = []
            for col in range(10):
                cmd = (lambda r=row, c=col, p=is_player: self.handle_grid_click(r, c, p))
                
                button = ctk.CTkButton(
                    frame, 
                    text="", 
                    width=45, 
                    height=45, 
                    corner_radius=4,
                    fg_color="#333333", 
                    hover_color="#444444",
                    state="normal",
                    command=cmd
                )
                button.grid(row=row+2, column=col+1, padx=2, pady=2)
                button_row.append(button)
                
                if is_player:
                    button.bind("<Enter>", lambda e, r=row, c=col: self.on_player_hover(r, c))
                    button.bind("<Leave>", lambda e, r=row, c=col: self.on_player_leave(r, c))
            button_list.append(button_row)

    def toggle_orientation(self):
        self.placement_orientation = "vertical" if self.placement_orientation == "horizontal" else "horizontal"
        self.rotate_btn.configure(text=f"Rotate Ship: {self.placement_orientation.title()}")

    def on_player_hover(self, row, col):
        if not self.setup_mode or not self.ships_to_place:
            return
            
        ship_name = self.ships_to_place[0]
        length = self.ship_info[ship_name]["length"]
        
        if self.is_valid_placement(self.player_board, row, col, self.placement_orientation, length):
            color = self.ship_info[ship_name]["color"]
        else:
            color = "#c0392b"
            
        for i in range(length):
            r, c = (row, col + i) if self.placement_orientation == "horizontal" else (row + i, col)
            if 0 <= r < 10 and 0 <= c < 10:
                self.player_buttons[r][c].configure(fg_color=color)

    def on_player_leave(self, row, col):
        if not self.setup_mode:
            return
        for r in range(10):
            for c in range(10):
                if self.player_board[r][c] != "~":
                    char = self.player_board[r][c]
                    name = self.char_to_name[char]
                    self.player_buttons[r][c].configure(fg_color=self.ship_info[name]["color"])
                else:
                    self.player_buttons[r][c].configure(fg_color="#333333")

    def handle_grid_click(self, row, col, is_player_board):
        if self.setup_mode and is_player_board:
            cell_content = self.player_board[row][col]
            if cell_content != "~":
                self.pickup_ship(cell_content)
                return

            self.place_manual_ship(row, col)
        elif not self.setup_mode and not is_player_board:
            self.handle_player_shot(row, col)

    def pickup_ship(self, char):
        if self.ships_to_place:
            return
            
        ship_name = self.char_to_name[char]
        
        coords = []
        for r in range(10):
            for c in range(10):
                if self.player_board[r][c] == char:
                    coords.append((r, c))
        
        if len(coords) > 1:
            if coords[0][0] == coords[1][0]:
                self.placement_orientation = "horizontal"
            else:
                self.placement_orientation = "vertical"
            self.rotate_btn.configure(text=f"Rotate Ship: {self.placement_orientation.title()}")

        for r, c in coords:
            self.player_board[r][c] = "~"
            self.player_buttons[r][c].configure(fg_color="#333333")
        
        self.ships_to_place.insert(0, ship_name)
        self.update_setup_ui_state()

    def place_manual_ship(self, row, col):
        if not self.ships_to_place:
            return
            
        ship_name = self.ships_to_place[0]
        length = self.ship_info[ship_name]["length"]
        char = self.ship_info[ship_name]["char"]
        
        if self.is_valid_placement(self.player_board, row, col, self.placement_orientation, length):
            for i in range(length):
                r, c = (row, col + i) if self.placement_orientation == "horizontal" else (row + i, col)
                self.player_board[r][c] = char
                self.player_buttons[r][c].configure(fg_color=self.ship_info[ship_name]["color"])
            
            self.ships_to_place.pop(0)
            self.update_setup_ui_state()

    def random_place_player_ships(self):
        self.player_board = self.create_empty_board()
        for r in range(10):
            for c in range(10):
                self.player_buttons[r][c].configure(fg_color="#333333")
        
        self.place_ships_random(self.player_board, self.player_health)
        
        for r in range(10):
            for c in range(10):
                if self.player_board[r][c] != "~":
                    char = self.player_board[r][c]
                    name = self.char_to_name[char]
                    self.player_buttons[r][c].configure(fg_color=self.ship_info[name]["color"])
        
        self.ships_to_place = []
        self.update_setup_ui_state()

    def update_setup_ui_state(self):
        self.random_btn.grid(row=0, column=0, padx=5, pady=5)
        self.rotate_btn.grid(row=0, column=1, padx=5, pady=5)
        if self.ships_to_place:
            self.status_label.configure(text=f"Place your {self.ships_to_place[0]} ({self.ship_info[self.ships_to_place[0]]['length']})")
            self.ready_btn.grid_forget()
        else:
            self.status_label.configure(text="Fleet Positioned. Ready to Deploy?")
            self.ready_btn.grid(row=1, column=0, columnspan=2, pady=5)

    def finish_setup(self):
        self.setup_mode = False
        self.setup_buttons_frame.pack_forget()
        self.status_label.configure(text=f"Battle Stations, {self.player_name}! Your Turn.")
        self.turn = "Your turn"

    def handle_player_shot(self, row, col):
        if self.game_over or self.turn != "Your turn" or self.computer_board[row][col] in ["H", "M"]:
            return

        target = self.computer_board[row][col]
        btn = self.computer_buttons[row][col]

        if target not in ["~", "H", "M"]:
            ship_char = target
            ship_name = self.char_to_name[ship_char]
            self.computer_health[ship_name] += 1
            
            self.computer_board[row][col] = "H"
            btn.configure(fg_color="#c0392b", state="disabled")
            self.status_label.configure(text="HIT! Nice shot!")
            self.animate_explosion(row, col, self.computer_buttons)
        else:
            self.computer_board[row][col] = "M"
            btn.configure(fg_color="#7f8c8d", state="disabled")
            self.status_label.configure(text="MISS!")
        
        self.update_status_ui()
        self.check_win()
        if not self.game_over:
            self.turn = "Computer"
            self.after(2000, self.computer_turn)

    def animate_explosion(self, row, col, button_grid):
        colors = ["#FFFFFF", "#FFFF00", "#e67e22", "#c0392b"]
        
        def step(idx):
            if idx < len(colors):
                button_grid[row][col].configure(fg_color=colors[idx])
                if idx == 1:
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < 10 and 0 <= nc < 10 and (nr != row or nc != col):
                                button_grid[nr][nc].configure(fg_color="#e67e22")
                if idx == 2:
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < 10 and 0 <= nc < 10 and (nr != row or nc != col):
                                val = self.computer_board[nr][nc] if button_grid == self.computer_buttons else self.player_board[nr][nc]
                                c = "#333333"
                                if val == "H": c = "#c0392b"
                                elif val == "M": c = "#7f8c8d"
                                elif val not in ["~", "H", "M"] and button_grid == self.player_buttons: c = self.ship_info[self.char_to_name[val]]["color"]
                                button_grid[nr][nc].configure(fg_color=c)

                self.after(100, lambda: step(idx + 1))
            else:
                button_grid[row][col].configure(fg_color="#c0392b")

        step(0)

    def computer_turn(self):
        if self.game_over:
            return

        row, col = -1, -1
        while self.computer_target_queue:
            best_index = -1
            # Prioritize targets that continue a line of hits (orientation detection)
            for i, (r, c) in enumerate(self.computer_target_queue):
                # Check Horizontal Line Alignment (Left or Right)
                if (c > 1 and self.player_board[r][c-1] == "H" and self.player_board[r][c-2] == "H") or \
                   (c < 8 and self.player_board[r][c+1] == "H" and self.player_board[r][c+2] == "H"):
                    best_index = i
                    break
                # Check Vertical Line Alignment (Up or Down)
                if (r > 1 and self.player_board[r-1][c] == "H" and self.player_board[r-2][c] == "H") or \
                   (r < 8 and self.player_board[r+1][c] == "H" and self.player_board[r+2][c] == "H"):
                    best_index = i
                    break

            if best_index != -1:
                r, c = self.computer_target_queue.pop(best_index)
            else:
                r, c = self.computer_target_queue.pop(random.randrange(len(self.computer_target_queue)))
            
            if 0 <= r < 10 and 0 <= c < 10 and self.player_board[r][c] not in ["H", "M"]:
                row, col = r, c
                break
        
        if row == -1:
            unfired_cells = [(r, c) for r in range(10) for c in range(10) if self.player_board[r][c] != "H" and self.player_board[r][c] != "M"]
            if not unfired_cells: return
            row, col = random.choice(unfired_cells)

        target = self.player_board[row][col]
        btn = self.player_buttons[row][col]

        if target not in ["~", "H", "M"]:
            ship_char = target
            ship_name = self.char_to_name[ship_char]
            self.player_health[ship_name] += 1
            
            self.player_board[row][col] = "H"
            btn.configure(fg_color="#c0392b")
            self.animate_explosion(row, col, self.player_buttons)
            
            if self.player_health[ship_name] == self.ship_info[ship_name]["length"]:
                self.status_label.configure(text=f"Computer SUNK your {ship_name}!")
                self.computer_target_queue.clear()
            else:
                self.status_label.configure(text=f"Computer HIT at {chr(ord('A') + row)}{col+1}!")
                neighbors = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
                random.shuffle(neighbors)
                for nr, nc in neighbors:
                    if 0 <= nr < 10 and 0 <= nc < 10 and self.player_board[nr][nc] not in ["H", "M"]:
                        if (nr, nc) not in self.computer_target_queue:
                            self.computer_target_queue.append((nr, nc))
        else:
            self.player_board[row][col] = "M"
            btn.configure(fg_color="#7f8c8d")
            self.status_label.configure(text=f"Computer Missed at {chr(ord('A') + row)}{col+1}")

        self.update_status_ui()
        self.check_win()
        if not self.game_over:
            self.turn = "Your turn"

    def check_win(self):
        if self.all_ships_sunk(self.computer_board):
            self.status_label.configure(text=f"VICTORY! {self.player_name} sank all enemy ships!", text_color="#2ecc71")
            self.game_over = True
            self.reveal_computer_ships()
        elif self.all_ships_sunk(self.player_board):
            self.status_label.configure(text=f"DEFEAT! {self.player_name}'s fleet was destroyed!", text_color="#e74c3c")
            self.game_over = True

    def all_ships_sunk(self, board):
        for row in board:
            for cell in row:
                if cell not in ["~", "H", "M"]:
                    return False
        return True

    def reveal_computer_ships(self):
        for row in range(10):
            for col in range(10):
                cell = self.computer_board[row][col]
                if cell not in ["~", "H", "M"]:
                    ship_name = self.char_to_name[cell]
                    color = self.ship_info[ship_name]["color"]
                    self.computer_buttons[row][col].configure(fg_color=color)

    def show_instructions(self):
        instructions = (
            "MISSION BRIEFING: TORPEDO TANGO\n\n"
            "OBJECTIVE:\n"
            "Sink all 5 enemy ships before they destroy your fleet.\n\n"
            "SETUP PHASE:\n"
            "1. Drag and drop ships to position them.\n"
            "2. Click an existing ship to pick it up and move it.\n"
            "3. Use 'Rotate Ship' to change orientation.\n"
            "4. Click 'Randomize' for quick deployment.\n"
            "5. Press 'DEPLOY FLEET' to begin combat.\n\n"
            "COMBAT PHASE:\n"
            "- Click coordinates on 'ENEMY WATERS' to fire.\n"
            "- Red 'X' = HIT | Grey '•' = MISS\n"
            "- Ships sink when all segments are destroyed.\n"
        )
        messagebox.showinfo("Instructions", instructions)

    def confirm_new_game(self):
        if not self.game_over and not self.setup_mode:
            confirm = messagebox.askyesno("Confirm Reset", "Current game will be lost. Are you sure?")
            if confirm:
                self.new_game()
        else:
            self.new_game()

    def new_game(self):
        self.player_board = self.create_empty_board()
        self.computer_board = self.create_empty_board()
        self.game_over = False
        self.setup_mode = True
        self.turn = "Setup"
        self.player_title.configure(text=f"{self.player_name.upper()}'S FLEET")
        self.computer_target_queue = []
        
        self.ships_to_place = list(self.ship_info.keys())
        self.setup_buttons_frame.pack(after=self.message_frame, pady=10)
        self.status_label.configure(text=f"Place your {self.ships_to_place[0]} ({self.ship_info[self.ships_to_place[0]]['length']})", text_color="white")
        self.update_setup_ui_state()
        
        self.place_ships_random(self.computer_board, self.computer_health)
        for name in self.ship_info: self.player_health[name] = 0
        
        self.update_status_ui()

        for r in range(10):
            for c in range(10):
                self.computer_buttons[r][c].configure(fg_color="#333333", state="normal", text="")
                
                self.player_buttons[r][c].configure(fg_color="#333333", state="normal", text="")


if __name__ == "__main__":
    app = BattleshipApp()
    app.mainloop()
