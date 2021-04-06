import tkinter as tk
import math


class BreakoutGame(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Breakout Game")
        self.resizable(width=False, height=False)
        self.game_over = False

        self.bind("<KeyPress>", lambda e: self.on_key_press(e))
        self.bind("<KeyPress-Escape>", lambda e: self.on_key_press(e))
        self.bind("<KeyPress-space>", lambda e: self.on_key_press(e))
        self.keys_to_process = []

        self.lives = tk.IntVar()
        self.lives.set(3)

        self.score = tk.IntVar()

        self.info_panel = tk.Frame(self)
        self.info_panel.grid(row=0, column=0)

        label_lives = self.LabelFrame(self.info_panel, 'Lives: ', self.lives)
        label_lives.grid(row=0, column=0)

        label_score = self.LabelFrame(self.info_panel, 'Score: ', self.score)
        label_score.grid(row=0, column=1)

        self.canvas = tk.Canvas(self)
        self.canvas.config(width=710, height=800, background='black')
        self.canvas.grid(row=1, column=0)

        self.blocks = []
        self.create_blocks()

        self.padding = self.canvas.create_rectangle(320, 700, 390, 720, fill='#0A85C2', tags=('padding'))
        self.ball = self.canvas.create_oval(345, 500, 365, 520, fill='white', tags=('ball'))

        self.wall_w = self.canvas.create_rectangle(-10, -10, 2, 810, fill='white', tags=('wall', 'w'))
        self.wall_n = self.canvas.create_rectangle(-10, -10, 720, 2, fill='white', tags=('wall', 'n'))
        self.wall_e = self.canvas.create_rectangle(720, -10, 708, 810, fill='white', tags=('wall', 'e'))
        self.wall_s = self.canvas.create_rectangle(-10, 798, 720, 810, fill='white', tags=('wall', 's'))

        self.speed = 3
        self.direction = 270

        self.game_over_text = None
        self.press_keys_text = None

        self.game_loop()

    def create_blocks(self):

        for j in range(0, 8):
            if j in [0, 1]:
                color = '#9D1D09'
                tags = ('forth', 'block')
            elif j in [2, 3]:
                color = '#C2850A'
                tags = ('third', 'block')
            elif j in [4, 5]:
                color = '#086727'
                tags = ('second', 'block')
            else:
                color = '#C2C229'
                tags = ('first', 'block')

            for i in range(0, 14):
                block = self.canvas.create_rectangle(10*(i+1) + 40*i, 40 + 10*(j+1) + 20*j, 10*(i+1) + 40*i + 40, 40 + 10*(j+1) + 20*j + 20, fill=color, tags=tags)
                self.blocks.append(block)

    def game_loop(self):
        if not self.game_over:
            coords = self.canvas.coords(self.ball)
            overlap = self.canvas.find_overlapping(coords[0]-1, coords[1]-1, coords[2]-1, coords[3]-1)
            for item in overlap:
                tags = self.canvas.gettags(item)
                if 'ball' in tags:
                    continue

                self.process_overlap(tags, item)
                # DON'T PROCESS HITTING TWO BLOCKS AT THE SAME TIME. IT WILL MESS WITH DIRECTIONS
                if 'block' in tags:
                    break

            self.process_keys_pressed()
            self.canvas.move(self.ball, -self.speed * math.cos(math.radians(self.direction)), -self.speed * math.sin(math.radians(self.direction)))
            self.after(3, self.game_loop)

    def process_overlap(self, tags, item):

        if 'padding' in tags:
            self.process_padding_hit()

        if 'wall' in tags:
            self.process_wall_hit(tags)

        if 'block' in tags:
            self.process_block_hit(item)
            self.process_block_destroy(tags, item)

    def process_padding_hit(self):

        coord_ball = self.canvas.coords(self.ball)
        coord_padding = self.canvas.coords(self.padding)
        if coord_ball[0] - coord_padding[0] < 25:
            padding_mode = 1
        elif 25 <= coord_ball[0] - coord_padding[0] <= 50:
            padding_mode = 2
        else:
            padding_mode = 3

        if 0 <= self.direction <= 90:
            if padding_mode == 1:
                self.direction = 360 - min(self.direction / 2, 15)
            elif padding_mode == 2:
                self.direction = 360 - self.direction
            elif padding_mode == 3:
                self.direction = 180 + self.direction
        elif 90 < self.direction <= 180:
            if padding_mode == 1:
                self.direction = 180 + self.direction
            elif padding_mode == 2:
                self.direction = 360 - self.direction
            elif padding_mode == 3:
                self.direction = min(360 - self.direction / 2, 200)
        elif 180 < self.direction <= 270:
            if padding_mode == 1:
                self.direction = self.direction - 180
            elif padding_mode == 2:
                self.direction = 360 - self.direction
            elif padding_mode == 3:
                self.direction = min(180 - (self.direction - 180) / 2, 160)
        elif 270 < self.direction <= 360:
            if padding_mode == 1:
                self.direction = min((360 - self.direction) / 2, 20)
            elif padding_mode == 2:
                self.direction = 360 - self.direction
            elif padding_mode == 3:
                self.direction = self.direction - 180

        if 175 < self.direction <= 180:
            self.direction = 165
        elif 180 < self.direction <= 185:
            self.direction = 195
        elif 355 <= self.direction <= 360:
            self.direction = 345
        elif 0 <= self.direction <= 5:
            self.direction = 15

    def process_wall_hit(self, tags):
        if 0 <= self.direction <= 90:
            if 'w' in tags:
                self.direction = 180 - self.direction
            elif 'n' in tags:
                self.direction = 360 - self.direction
        elif 90 < self.direction <= 180:
            if 'n' in tags:
                self.direction = 360 - self.direction
            elif 'e' in tags:
                self.direction = 180 - self.direction
        elif 180 < self.direction <= 270:
            if 'e' in tags:
                self.direction = 540 - self.direction
            elif 's' in tags:
                self.direction = 360 - self.direction
                self.process_out()
        elif 270 < self.direction <= 360:
            if 's' in tags:
                self.direction = 360 - self.direction
                self.process_out()
            elif 'w' in tags:
                self.direction = 540 - self.direction

    def process_block_hit(self, block):
        ball_coords = self.canvas.coords(self.ball)
        block_coords = self.canvas.coords(block)

        if 0 <= self.direction <= 90:
            # BALL'S UPPER Y LESS THAN BLOCK'S LOWER Y
            bottom_hit = ball_coords[1]-1 <= block_coords[3]
            # BALL'S UPPER Y HIGHER THAN BLOCK'S LOWER Y
            lateral_hit = ball_coords[1] > block_coords[3]

            if bottom_hit:
                self.direction = 315
            elif lateral_hit:
                self.direction = 180 - self.direction

        elif 90 < self.direction <= 180:
            # BALL'S UPPER Y LESS THAN BLOCK'S LOWER Y
            bottom_hit = (ball_coords[1]-1 <= block_coords[3])
            # BALL'S UPPER Y HIGHER THAN BLOCK'S LOWER Y
            lateral_hit = (ball_coords[1] > block_coords[3])

            if bottom_hit:
                self.direction = 225
            elif lateral_hit:
                self.direction = 180 - self.direction

        elif 180 < self.direction <= 270:
            # BALL'S LOWER Y HIGHER THAN BLOCK'S UPPER Y
            upper_hit = (ball_coords[3]-1 >= block_coords[1])
            # BALL'S RIGHT X LESS THAN BLOCK'S LEFT X
            lateral_hit = (ball_coords[2]+1 <= block_coords[0])

            # if upper_hit:
            #     self.direction = 135
            # elif lateral_hit:
            #     self.direction = 540 - self.direction

            if lateral_hit:
                self.direction = 540 - self.direction
            else:
                self.direction = 135

        elif 270 < self.direction <= 360:
            # BALL'S LOWER Y HIGHER THAN BLOCK'S UPPER Y
            upper_hit = (ball_coords[3]-1 >= block_coords[1])
            # BALL'S LOWER Y HIGHER THAN BLOCK'S UPPER Y
            lateral_hit = (ball_coords[3] < block_coords[1])

            # if upper_hit:
            #     self.direction = 45
            # elif lateral_hit:
            #     self.direction = 540 - self.direction
            if lateral_hit:
                self.direction = 540 - self.direction
            elif upper_hit:
                self.direction = 45


    def process_block_destroy(self, tags, block):
        score_block = 0

        if 'first' in tags:
            score_block = 50
        elif 'second' in tags:
            score_block = 100
        elif 'third' in tags:
            score_block = 150
            if self.speed < 5:
                self.speed = 5
        elif 'forth' in tags:
            score_block = 200
            if self.speed < 7:
                self.speed = 7

        self.score.set(self.score.get() + score_block)
        self.canvas.delete(block)

    def on_key_press(self, e):
        if e.keysym in ['Left', 'Right']:
            self.keys_to_process.append(e.keysym)
        if self.game_over:
            if e.keysym == 'Escape':
                self.destroy()
            elif e.keysym == 'space':
                self.reset_ball()
                self.lives.set(3)
                self.score.set(0)
                self.game_over = False
                self.game_loop()
                self.canvas.delete(self.game_over_text)
                self.canvas.delete(self.press_keys_text)

    def process_keys_pressed(self):
        if len(self.keys_to_process) > 0:
            key = self.keys_to_process.pop(0)
            coord_padding = self.canvas.coords(self.padding)
            if key == 'Left':
                if coord_padding[0] - 15 >= 0:
                    self.canvas.move(self.padding, -15, 0)
            elif key == 'Right':
                if coord_padding[2] + 15 <= 710:
                    self.canvas.move(self.padding, 15, 0)

    def process_out(self):
        self.lives.set(self.lives.get()-1)
        self.reset_ball()

        if self.lives.get() == 0:
            self.process_game_over()

    def reset_ball(self):
        self.direction = 270
        self.speed = 3
        self.canvas.coords(self.ball, 345, 500, 365, 520)
        self.canvas.coords(self.padding, 320, 700, 390, 720)

    def process_game_over(self):
        self.game_over = True
        self.game_over_text = self.canvas.create_text(355, 300, text="GAME OVER", fill='#FFAE0D', font=('Arial', 36, 'bold'), anchor="center")
        self.press_keys_text = self.canvas.create_text(355, 350, text="Press SPACE to continue or ESC to exit", fill='#FFAE0D', font=('Arial', 24, 'bold'), anchor="center")


    class LabelFrame(tk.Frame):
        def __init__(self, parent,  label_name, label_var, *args, **kwargs):
            super().__init__(parent, *args, **kwargs)
            label_text = tk.Label(self, text=label_name, font=('Lucida sans', 14))
            label_text.grid(row=0, column=0, padx=5, pady=5)
            label_info = tk.Label(self, textvariable=label_var, font=('Lucida sans', 14))
            label_info.grid(row=0, column=1, padx=5, pady=5)


if __name__ == "__main__":
    game = BreakoutGame()
    game.mainloop()
