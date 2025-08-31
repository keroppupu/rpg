# -*- coding: utf-8 -*-
import pyxel
import random

# --- 設定 ---
JAPANESE_FONT_FILE = "umplus_j10r.bdf"
ENCOUNTER_RATE = 2  # エンカウント率 (%)
CHEST_IMAGE_FILE = "assets/chest.png"
ENEMY_IMAGE_FILE = "assets/enemies.png"
SHOPKEEPER_IMAGE_FILE = "assets/shopkeeper.png"

class Game:
    def __init__(self):
        pyxel.init(256, 192, title="Pyxel 3Dダンジョン", fps=30)
        pyxel.colors.from_list([
            0x000000, 0x111111, 0x222222, 0x333333, 0x444444, 0x555555, 0x666666, 0x777777,
            0x888888, 0x999999, 0xaaaaaa, 0xbbbbbb, 0xcccccc, 0xdddddd, 0xeeeeee, 0xffffff,
        ])
        
        self.jp_font = None
        try:
            self.jp_font = pyxel.Font(JAPANESE_FONT_FILE)
        except Exception:
            print("警告: 日本語フォントの読み込みに失敗しました。")

        self.assets_loaded = False
        try:
            pyxel.image(1).load(0, 0, CHEST_IMAGE_FILE)
            pyxel.image(1).load(0, 16, ENEMY_IMAGE_FILE)
            pyxel.image(2).load(0, 0, SHOPKEEPER_IMAGE_FILE)
            self.assets_loaded = True
            print("画像アセットの読み込みに成功しました。")
        except Exception as e:
            print(f"警告: 画像ファイルの読み込みに失敗しました。 {e}")

        self.monster_types = [
            {"name": "スライム",   "hp": 18, "attack": 4, "gold": 5, "exp": 3, "img_u": 0, "img_v": 16},
            {"name": "ゴブリン",   "hp": 30, "attack": 7, "gold": 12, "exp": 8, "img_u": 48, "img_v": 16},
            {"name": "おおこうもり", "hp": 22, "attack": 8, "gold": 8, "exp": 5, "img_u": 96, "img_v": 16}
        ]
        
        self.shop_items = [
            {"name":"どうのつるぎ", "type":"weapon", "attack":8, "price": 100},
            {"name":"てつのたて", "type":"armor",  "defense":5, "price": 120},
            {"name":"やくそう", "type":"heal", "effect": 25, "price": 15}
        ]
        
        # ★★★★★ 変更点(1): レベルアップに必要な経験値を大幅に増加 ★★★★★
        self.exp_table = [0, 20, 60, 150, 350, 800, 1800, 3500, 6000, 10000] 

        self.map_data = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,3,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,2,1],
            [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,1,0,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,0,1],
            [1,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,0,0,1,0,1],
            [1,2,1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1,0,1,0,1,0,1],
            [1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,2,1,0,1,0,1],
            [1,0,0,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1,0,1],
            [1,0,1,0,1,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,1,0,0,2,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1],
            [1,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1,0,1,1,1,1,1,2,1,0,1,1,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1],
            [1,1,1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1,0,1],
            [1,0,0,0,1,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,2,1],
            [1,2,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        self.map_width = len(self.map_data[0]); self.map_height = len(self.map_data)
        
        self.chests_content = {
            (1, 6):  {"name":"どうのつるぎ", "type":"weapon", "attack":8},
            (18, 7): {"name":"てつのたて", "type":"armor",  "defense":5},
            (22, 1): {"name":"はがねのけん", "type":"weapon", "attack":15},
            (9, 11): {"name":"くさりかたびら", "type":"armor", "defense":7},
            (1, 18): {"name":"まほうのたて", "type":"armor",  "defense":12},
            (16, 14):{"name":"バトルアックス", "type":"weapon", "attack":18},
            (22, 17):{"name":"ほのおのつるぎ", "type":"weapon", "attack":25}
        }

        self.game_state = "title"
        self.message_text = ""
        self.inventory_cursor_index = 0
        self.shop_cursor_index = 0
        self.shop_message = ""
        self.result_message = ""
        
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.player_x, self.player_y, self.player_dir = 1.5, 1.5, 0
        self.player_level = 1
        self.player_exp = 0
        self.player_max_hp = 70
        self.player_hp = self.player_max_hp
        self.player_base_attack = 2
        self.player_base_defense = 0
        self.player_radius = 0.2
        self.player_gold = 20
        self.inventory = [
            {"name":"ひのきのぼう","type":"weapon","attack":5},
            {"name":"ぬののふく","type":"armor","defense":1},
        ]
        self.equipped_weapon = self.inventory[0]
        self.equipped_armor = self.inventory[1]
        self.opened_chests = set()
        self.battle_messages, self.battle_command_index = [], 0
        self.enemy_name, self.enemy_hp, self.enemy_max_hp, self.enemy_attack = "", 0, 0, 0
        self.enemy_img_u, self.enemy_img_v = 0, 0

    def draw_jp_text(self, x, y, text, color):
        if self.jp_font: pyxel.text(x, y, text, color, font=self.jp_font)
        else: pyxel.text(x, y, text, color)

    def get_map_tile(self, x, y):
        x, y = int(x), int(y)
        if not (0 <= x < self.map_width and 0 <= y < self.map_height): return 1
        return self.map_data[y][x]

    def update(self):
        if self.game_state == "title": self.update_title()
        elif self.game_state == "field": self.update_field()
        elif self.game_state == "battle": self.update_battle()
        elif self.game_state == "inventory": self.update_inventory()
        elif self.game_state == "shop": self.update_shop()
        elif self.game_state in ["result", "gameover", "message"]: self.update_message_screen()

    def draw(self):
        pyxel.cls(0)
        if self.game_state == "title": self.draw_title()
        elif self.game_state in ["field", "message", "inventory"]:
            self.draw_field()
            if self.game_state == "message":
                self.draw_message_window(self.message_text)
            elif self.game_state == "inventory":
                self.draw_inventory_screen()
        elif self.game_state == "battle": self.draw_battle()
        elif self.game_state == "shop": self.draw_shop()
        elif self.game_state == "result": self.draw_result(self.result_message)
        elif self.game_state == "gameover": self.draw_result("げーむ おーばー")

    def update_title(self):
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN):
            self.reset_game()
            self.game_state = "field"

    def draw_title(self):
        pyxel.cls(0)
        title_text = "Pyxel 3D Dungeon"
        text_width = len(title_text) * pyxel.FONT_WIDTH
        self.draw_jp_text(128 - text_width / 2, 80, title_text, 15)
        if (pyxel.frame_count // 15) % 2 == 0:
            start_text = "PRESS Z TO START"
            start_width = len(start_text) * pyxel.FONT_WIDTH
            self.draw_jp_text(128 - start_width / 2, 110, start_text, 14)

    def update_field(self):
        moved = False
        if pyxel.btnp(pyxel.KEY_LEFT, 8, 2): self.player_dir = (self.player_dir - 1 + 4) % 4
        if pyxel.btnp(pyxel.KEY_RIGHT, 8, 2): self.player_dir = (self.player_dir + 1 + 4) % 4
        dx, dy, speed = [0, 1, 0, -1], [-1, 0, 1, 0], 0.1
        move_vec = [0.0, 0.0]
        if pyxel.btn(pyxel.KEY_UP):
            move_vec[0] += dx[self.player_dir] * speed
            move_vec[1] += dy[self.player_dir] * speed
        if pyxel.btn(pyxel.KEY_DOWN):
            move_vec[0] -= dx[self.player_dir] * speed
            move_vec[1] -= dy[self.player_dir] * speed
        if move_vec[0] != 0.0 or move_vec[1] != 0.0:
            moved = True
            next_x = self.player_x + move_vec[0]
            if self.get_map_tile(next_x + self.player_radius * (-1 if move_vec[0] < 0 else 1), self.player_y) == 0:
                self.player_x = next_x
            next_y = self.player_y + move_vec[1]
            if self.get_map_tile(self.player_x, next_y + self.player_radius * (-1 if move_vec[1] < 0 else 1)) == 0:
                self.player_y = next_y
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN):
            fx, fy = int(self.player_x + dx[self.player_dir]), int(self.player_y + dy[self.player_dir])
            tile_front = self.get_map_tile(fx, fy)
            if tile_front == 2 and (fx, fy) not in self.opened_chests:
                self.open_chest(fx, fy)
            elif tile_front == 3:
                self.game_state = "shop"
                self.shop_cursor_index = 0
                self.shop_message = ""
        if pyxel.btnp(pyxel.KEY_X):
            self.game_state = "inventory"
            self.inventory_cursor_index = 0
        if moved and random.randint(1, 100) <= ENCOUNTER_RATE:
            self.start_battle()

    def open_chest(self, x, y):
        item = self.chests_content.get((x,y))
        if not item: return
        self.inventory.append(item.copy())
        self.message_text = f"たからばこを あけた！\n{item['name']}を てにいれた！"
        self.opened_chests.add((x,y))
        self.game_state = "message"

    def draw_field(self):
        self.draw_dungeon_view(); self.draw_field_ui(); self.draw_minimap()

    def update_inventory(self):
        if pyxel.btnp(pyxel.KEY_UP): self.inventory_cursor_index = max(0, self.inventory_cursor_index - 1)
        if pyxel.btnp(pyxel.KEY_DOWN): self.inventory_cursor_index = min(len(self.inventory)-1, self.inventory_cursor_index + 1)
        
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN):
            if not self.inventory: return
            
            selected_item = self.inventory[self.inventory_cursor_index]
            
            if selected_item["type"] == "weapon":
                self.equipped_weapon = selected_item
                self.message_text = f"{selected_item['name']}を そうびした。"
                self.game_state = "message"
            elif selected_item["type"] == "armor":
                self.equipped_armor = selected_item
                self.message_text = f"{selected_item['name']}を そうびした。"
                self.game_state = "message"
            elif selected_item["type"] == "heal":
                if self.player_hp >= self.player_max_hp:
                    self.message_text = "HPは まんたんだ！"
                    self.game_state = "message"
                else:
                    self.player_hp = min(self.player_max_hp, self.player_hp + selected_item["effect"])
                    self.message_text = f"{selected_item['name']}をつかって HPがかいふくした！"
                    self.inventory.pop(self.inventory_cursor_index)
                    self.inventory_cursor_index = max(0, self.inventory_cursor_index - 1)
                    self.game_state = "message"
        
        if pyxel.btnp(pyxel.KEY_X): self.game_state = "field"
        
    def draw_inventory_screen(self):
        win_x, win_y, win_w, win_h = 40, 20, 176, 140
        pyxel.rect(win_x, win_y, win_w, win_h, 2)
        pyxel.rectb(win_x, win_y, win_w, win_h, 13)
        self.draw_jp_text(win_x + 6, win_y + 6, "--- もちもの ---", 15)
        if not self.inventory:
            self.draw_jp_text(win_x + 10, win_y + 25, "なにももっていない", 8)
        else:
            for i, item in enumerate(self.inventory):
                item_y = win_y + 20 + i * 10
                prefix = ""
                if item == self.equipped_weapon or item == self.equipped_armor:
                    prefix = "E:"
                self.draw_jp_text(win_x + 20, item_y, prefix + item["name"], 15)
            if self.inventory:
                cursor_y = win_y + 20 + self.inventory_cursor_index * 10
                pyxel.tri(win_x+8, cursor_y, win_x+13, cursor_y+2, win_x+8, cursor_y+4, 15)
        self.draw_jp_text(win_x + 6, win_y + win_h - 14, "↑↓:せんたく Z:しらべる X:もどる", 14)

    def update_shop(self):
        if self.shop_message:
            if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_X):
                self.shop_message = ""
            return

        if pyxel.btnp(pyxel.KEY_UP): self.shop_cursor_index = max(0, self.shop_cursor_index - 1)
        if pyxel.btnp(pyxel.KEY_DOWN): self.shop_cursor_index = min(len(self.shop_items), self.shop_cursor_index + 1)

        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN):
            if self.shop_cursor_index == len(self.shop_items):
                self.game_state = "field"
                return
            
            item = self.shop_items[self.shop_cursor_index]
            if self.player_gold >= item["price"]:
                self.player_gold -= item["price"]
                self.inventory.append(item.copy())
                self.shop_message = f"{item['name']}を こうにゅうした！"
            else:
                self.shop_message = "ゴールドが たりない！"

        if pyxel.btnp(pyxel.KEY_X): self.game_state = "field"

    def draw_shop(self):
        pyxel.cls(2)
        self.draw_jp_text(20, 20, "いらっしゃいませ！", 15)
        pyxel.rect(10, 40, 160, 140, 0); pyxel.rectb(10, 40, 160, 140, 13)
        for i, item in enumerate(self.shop_items):
            text = f"{item['name']:<12} {item['price']:>4}G"
            self.draw_jp_text(20, 50 + i * 10, text, 15)
        self.draw_jp_text(20, 50 + len(self.shop_items) * 10, "やめる", 15)
        cursor_y = 50 + self.shop_cursor_index * 10
        pyxel.tri(12, cursor_y, 17, cursor_y + 2, 12, cursor_y + 4, 15)
        pyxel.rect(175, 150, 75, 30, 0); pyxel.rectb(175, 150, 75, 30, 13)
        self.draw_jp_text(180, 155, "G:", 15)
        gold_text = f"{self.player_gold}"
        self.draw_jp_text(240 - len(gold_text) * pyxel.FONT_WIDTH, 165, gold_text, 15)
        if self.assets_loaded:
            pyxel.blt(180, 50, 2, 0, 0, 64, 80, 0)
        if self.shop_message:
            self.draw_message_window(self.shop_message)

    def start_battle(self):
        self.game_state="battle"
        self.battle_command_index=0
        monster = random.choice(self.monster_types)
        self.enemy_name = monster["name"]
        self.enemy_max_hp = monster["hp"]
        self.enemy_hp = monster["hp"]
        self.enemy_attack = monster["attack"]
        self.enemy_img_u = monster["img_u"]
        self.enemy_img_v = monster["img_v"]
        self.battle_messages=[f"{self.enemy_name}が あらわれた！"]

    def update_battle(self):
        if pyxel.btnp(pyxel.KEY_UP): self.battle_command_index=(self.battle_command_index-1+2)%2
        if pyxel.btnp(pyxel.KEY_DOWN): self.battle_command_index=(self.battle_command_index+1)%2
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN):
            if self.battle_command_index == 0: self.player_attack()
            elif self.battle_command_index == 1: self.player_escape()

    def get_player_total_attack(self):
        return self.player_base_attack + self.equipped_weapon.get("attack", 0)

    def get_player_total_defense(self):
        return self.player_base_defense + self.equipped_armor.get("defense", 0)

    def player_attack(self):
        base_damage = self.get_player_total_attack()
        damage = base_damage + random.randint(0, 3)
        self.enemy_hp -= damage
        self.battle_messages=[f"プレイヤーの こうげき！",f"{damage}のダメージを あたえた！"]
        if self.enemy_hp<=0: 
            self.enemy_hp=0
            monster_data = next((m for m in self.monster_types if m["name"] == self.enemy_name), None)
            
            gold_won = 0
            exp_won = 0
            if monster_data:
                gold_won = monster_data.get("gold", 0) + random.randint(0, monster_data.get("gold", 0) // 2)
                exp_won = monster_data.get("exp", 0) + random.randint(0, monster_data.get("exp", 0) // 2)
                self.player_gold += gold_won
                self.player_exp += exp_won

            self.result_message = f"きみの かち！\n{gold_won}Gと {exp_won}のけいけんちを てにいれた！"
            
            leveled_up, level_up_messages = self.check_for_level_up()
            if leveled_up:
                self.result_message += "\n" + "\n".join(level_up_messages)

            self.game_state="result"
        else: self.enemy_turn()

    # ★★★★★ 変更点(2): レベルアップ時のHP全回復を削除 ★★★★★
    def check_for_level_up(self):
        leveled_up = False
        messages = []
        while self.player_level < len(self.exp_table) and self.player_exp >= self.exp_table[self.player_level]:
            leveled_up = True
            self.player_level += 1
            messages.append(f"レベルが {self.player_level} にあがった！")
            
            hp_up = random.randint(5, 8)
            self.player_max_hp += hp_up
            # self.player_hp = self.player_max_hp # ← この行を削除
            messages.append(f"さいだいHPが {hp_up} あがった！")
            
            atk_up = random.randint(1, 3)
            self.player_base_attack += atk_up
            messages.append(f"こうげきりょくが {atk_up} あがった！")

            def_up = random.randint(1, 2)
            self.player_base_defense += def_up
            messages.append(f"ぼうぎょりょくが {def_up} あがった！")

        return leveled_up, messages

    def player_escape(self):
        if random.randint(1,100)<=50: 
            self.result_message="うまく にげきれた！"
            self.game_state="result"
        else: 
            self.battle_messages=["しかし まわりこまれてしまった！"]
            self.enemy_turn()
            
    def enemy_turn(self):
        damage = max(0, self.enemy_attack - self.get_player_total_defense()) + random.randint(0,2)
        self.player_hp -= damage
        self.battle_messages.append(f"{self.enemy_name}の こうげき！")
        self.battle_messages.append(f"{damage}のダメージを うけた！")
        if self.player_hp<=0: self.player_hp=0; self.game_state="gameover"

    def draw_battle(self):
        pyxel.rect(10,10,236,172,2); pyxel.rectb(10,10,236,172,13)
        if self.assets_loaded:
            img_w, img_h = 48, 48
            pyxel.blt(128 - img_w / 2, 96 - img_h, 1, self.enemy_img_u, self.enemy_img_v, img_w, img_h, 0)
        else:
            ex,ey,er=128,70,25; pyxel.circ(ex,ey,er,8); pyxel.circ(ex-7,ey-5,3,15); pyxel.circ(ex+7,ey-5,3,15)
        pyxel.rect(20,110,216,70,2); pyxel.rectb(20,110,216,70,13)
        for i,msg in enumerate(self.battle_messages): self.draw_jp_text(30,120+i*10,msg,15)
        pyxel.rect(160,20,70,40,2); pyxel.rectb(160,20,70,40,13)
        self.draw_jp_text(175,30,"たたかう",15); self.draw_jp_text(175,40,"にげる",15)
        pyxel.tri(165,30+self.battle_command_index*10,170,32+self.battle_command_index*10,165,34+self.battle_command_index*10,15)
        self.draw_jp_text(30,20,f"HP: {self.player_hp}/{self.player_max_hp}",15)
        self.draw_jp_text(30,90,f"{self.enemy_name} HP: {self.enemy_hp}",15)

    def update_message_screen(self):
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_X):
            if self.game_state == "gameover":
                self.game_state = "title"
            else:
                self.game_state = "field"
    
    def draw_result(self, message): self.draw_message_window(message)

    def draw_message_window(self, text):
        lines=text.split('\n'); max_width=0
        for line in lines: width=sum(10 if ord(c)>127 else 5 for c in line); max_width=max(width, max_width)
        win_w,win_h=max_width+20,len(lines)*10+12; win_x,win_y=(256-win_w)/2,(192-win_h)/2
        pyxel.rect(win_x,win_y,win_w,win_h,2); pyxel.rectb(win_x,win_y,win_w,win_h,13)
        for i,line in enumerate(lines): self.draw_jp_text(win_x+10,win_y+6+i*10,line,15)

    def draw_dungeon_view(self):
        view_vectors=[[[0,-1],[-1,0],[1,0]],[[1,0],[0,-1],[0,1]],[[0,1],[1,0],[-1,0]],[[-1,0],[0,1],[0,-1]]]
        f_vec,l_vec,r_vec=view_vectors[self.player_dir]; walls_to_draw=[]
        for i in range(5,-1,-1):
            fx,fy=self.player_x+f_vec[0]*i,self.player_y+f_vec[1]*i; tile=self.get_map_tile(fx,fy)
            if tile>0: walls_to_draw.append({'dist':i,'type':'front','tile':tile,'opened':(int(fx),int(fy))in self.opened_chests})
            if i>0:
                bx,by=self.player_x+f_vec[0]*(i-1),self.player_y+f_vec[1]*(i-1)
                if self.get_map_tile(bx+f_vec[0],by+f_vec[1])!=0 and i>1:continue
                lx,ly=bx+l_vec[0],by+l_vec[1]; rx,ry=bx+r_vec[0],by+r_vec[1]
                if self.get_map_tile(lx,ly)!=0:walls_to_draw.append({'dist':i-0.5,'type':'left'})
                if self.get_map_tile(rx,ry)!=0:walls_to_draw.append({'dist':i-0.5,'type':'right'})
        for wall in sorted(walls_to_draw,key=lambda x:x['dist'],reverse=True):
            dist=wall['dist'];color=max(2,15-int(dist*2.5));
            if dist<0:continue
            if wall['type']=='front':
                h,w=192/(dist+1),192/(dist+1);x1,y1=128-w/2,96-h/2
                if wall['tile'] == 2:
                    base_color = 5 if wall['opened'] else color
                    pyxel.rect(x1, y1, w, h, base_color)
                    pyxel.rectb(x1, y1, w, h, 0)
                    if self.assets_loaded and dist < 1.5:
                        u = 16 if wall['opened'] else 0
                        img_w, img_h = 16, 16
                        scale_factor = 2.0
                        scaled_w, scaled_h = img_w * scale_factor, img_h * scale_factor
                        draw_x, draw_y = x1 + (w - scaled_w) / 2, y1 + (h - scaled_h) / 2
                        try: pyxel.blt(draw_x, draw_y, 1, u, 0, img_w, img_h, 0, scale=scale_factor)
                        except TypeError: pyxel.blt(draw_x, draw_y, 1, u, 0, img_w, img_h, 0)
                elif wall['tile'] == 3:
                    pyxel.rect(x1, y1, w, h, 6); pyxel.rectb(x1, y1, w, h, 0)
                else:
                    pyxel.rect(x1, y1, w, h, color); pyxel.rectb(x1, y1, w, h, 0)
            else:
                df,db=dist-0.5,dist+0.5;c=max(1,color-2)
                hf,wf=192/(df+1),192/(df+1);xfl,xfr=128-wf/2,128+wf/2;yft,yfb=96-hf/2,96+hf/2
                hb,wb=192/(db+1),192/(db+1);xbl,xbr=128-wb/2,128+wb/2;ybt,ybb=96-hb/2,96+hb/2
                if wall['type']=='left': pyxel.tri(xbl,ybt,xfl,yft,xfl,yfb,c);pyxel.tri(xbl,ybt,xfl,yfb,xbl,ybb,c);pyxel.line(xfl,yft,xfl,yfb,0)
                else: pyxel.tri(xbr,ybt,xfr,yft,xfr,yfb,c);pyxel.tri(xbr,ybt,xfr,yfb,xbr,ybb,c);pyxel.line(xfr,yft,xfr,yfb,0)

    def draw_field_ui(self):
        pyxel.rect(0,152,256,40,2);pyxel.rectb(0,152,256,40,13)
        self.draw_jp_text(10,157,f"LV: {self.player_level}",15)
        self.draw_jp_text(10,167,f"HP: {self.player_hp}/{self.player_max_hp}",15)
        self.draw_jp_text(10,177,f"G: {self.player_gold}",15)
        next_exp = self.exp_table[self.player_level] - self.player_exp if self.player_level < len(self.exp_table) else "---"
        self.draw_jp_text(80, 157, f"のこりEXP: {next_exp}", 15)
        self.draw_jp_text(80,167,f"こうげき: {self.get_player_total_attack()}",15)
        self.draw_jp_text(80,177,f"ぼうぎょ: {self.get_player_total_defense()}",15)
        self.draw_jp_text(170,167,f"ぶき: {self.equipped_weapon['name']}",15)
        self.draw_jp_text(170,177,f"たて: {self.equipped_armor['name']}",15)

    def draw_minimap(self):
        mbx, mby, ts = 177, 10, 3
        pyxel.rect(mbx - 1, mby - 1, self.map_width * ts + 2, self.map_height * ts + 2, 2)
        pyxel.rectb(mbx - 1, mby - 1, self.map_width * ts + 2, self.map_height * ts + 2, 13)
        for y in range(self.map_height):
            for x in range(self.map_width):
                tile = self.get_map_tile(x, y)
                c = -1
                if tile == 1: c = 8
                elif tile == 2: c = 9 if (x, y) not in self.opened_chests else 5
                elif tile == 3: c = 10 
                if c != -1:
                    pyxel.rect(mbx + x * ts, mby + y * ts, ts, ts, c)
        pmx, pmy = mbx + self.player_x * ts, mby + self.player_y * ts
        pyxel.pset(pmx, pmy, 15)
        pyxel.pset(pmx - 1, pmy, 15)
        pyxel.pset(pmx + 1, pmy, 15)
        pyxel.pset(pmx, pmy - 1, 15)
        pyxel.pset(pmx, pmy + 1, 15)
        dx, dy = [0, 1, 0, -1], [-1, 0, 1, 0]
        pyxel.line(pmx, pmy, pmx + dx[self.player_dir] * 3, pmy + dy[self.player_dir] * 3, 15)

Game()