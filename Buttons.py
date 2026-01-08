import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

class RoundedButton(tk.Canvas):
    """Упрощенная закругленная кнопка"""

    def __init__(self, parent, text, command, width=300, height=60,
                 corner_radius=15, bg_color="#1F43CD", text_color="white",
                 font=("Arial", 22), hover_color="#5EC9F5"):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bg=parent.cget("bg"))

        self.command = command
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.font = font
        self.corner_radius = corner_radius
        self.width = width
        self.height = height
        self.is_hovered = False
        self.button_text = text

        self.button_image = None
        self.button_bg = None

        self.create_button_image()

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def create_button_image(self):
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        color = self.hover_color if self.is_hovered else self.bg_color
        draw.rounded_rectangle([0, 0, self.width - 1, self.height - 1],
                               radius=self.corner_radius, fill=color)

        self.button_image = ImageTk.PhotoImage(image)

        if self.button_bg:
            self.itemconfig(self.button_bg, image=self.button_image)
        else:
            self.button_bg = self.create_image(0, 0, anchor="nw", image=self.button_image)

        # Добавляем текст с переносом строки
        words = self.button_text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            # Проверяем, не превышает ли строка определенную длину
            if len(' '.join(current_line)) > 40:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Размещаем текст в кнопке
        line_height = 25
        y_start = self.height // 2 - (len(lines) - 1) * line_height // 2

        for i, line in enumerate(lines):
            y_pos = y_start + i * line_height
            self.create_text(self.width // 2, y_pos, text=line,
                             fill=self.text_color, font=self.font, tags="text")

    def on_click(self, event):
        self.command()

    def on_enter(self, event):
        self.is_hovered = True
        self.create_button_image()

    def on_leave(self, event):
        self.is_hovered = False
        self.create_button_image()