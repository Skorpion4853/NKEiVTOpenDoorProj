import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


class RoundedButton(tk.Canvas):
    """Упрощенная закругленная кнопка"""

    def __init__(self, parent, text, command, width=300, height=60,
                 corner_radius=15, bg_color="#1F43CD", text_color="white",
                 font=("Arial", 24), hover_color="#5EC9F5"):
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
        self.button_text = text  # Сохраняем текст как атрибут

        # Инициализируем атрибуты изображения
        self.button_image = None
        self.button_bg = None

        # Создаем изображение для кнопки
        self.create_button_image()

        # Привязка событий
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def create_button_image(self):
        """Создание закругленной кнопки через изображение"""
        # Создаем изображение с закругленными углами
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Рисуем закругленный прямоугольник
        color = self.hover_color if self.is_hovered else self.bg_color
        draw.rounded_rectangle([0, 0, self.width - 1, self.height - 1],
                               radius=self.corner_radius, fill=color)

        self.button_image = ImageTk.PhotoImage(image)

        # Если элемент уже создан, обновляем его
        if self.button_bg:
            self.itemconfig(self.button_bg, image=self.button_image)
        else:
            self.button_bg = self.create_image(0, 0, anchor="nw", image=self.button_image)

        # Добавляем текст
        self.create_text(self.width // 2, self.height // 2, text=self.button_text,
                         fill=self.text_color, font=self.font)

    def on_click(self, event):
        self.command()

    def on_enter(self, event):
        self.is_hovered = True
        self.create_button_image()

    def on_leave(self, event):
        self.is_hovered = False
        self.create_button_image()


class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- ОКНО ---
        self.title("Тест: какой ты арбуз")
        self.geometry("1920x1080")
        self.configure(bg="#F0F0F0")

        # --- ШРИФТЫ ---
        # Используем TT Travels как основной шрифт, Arial как запасной
        self.heading_font = ("TT Travels", 40, "bold")
        self.button_font = ("TT Travels", 30, "bold")
        self.main_font = ("TT Travels", 24)
        self.small_font = ("TT Travels", 16)

        # --- ЦВЕТА ---
        self.primary_color = "#1F43CD"
        self.accent_color = "#5EC9F5"
        self.bg_color = "#F0F0F0"
        self.white = "#FFFFFF"

        # Инициализируем атрибуты изображений
        self.logo_small = None
        self.logo_big = None
        self.people_image = None

        # Загрузка изображений
        self.load_images()

        # --- ДАННЫЕ ТЕСТА ---
        self.questions = [
            {
                "text": "Какая средняя цена за один кг\nарбуза?",
                "options": [
                    "миллиард рублей",
                    "миллиард долларов",
                    "50 копеек",
                    "все варианты верны",
                ],
            },
        ]
        self.current_index = 0

        # --- КОНТЕЙНЕР ДЛЯ СТРАНИЦ ---
        self.container = tk.Frame(self, bg=self.bg_color)
        self.container.pack(fill="both", expand=True)

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, QuestionPage, ResultPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def load_images(self):
        """Загрузка всех изображений"""
        try:
            # Маленькое лого
            mimg = Image.open("img/Logo+name.png")
            small_h = 80  # Увеличиваем для 1920x1080
            ratio_small = small_h / mimg.height
            small_size = (int(mimg.width * ratio_small), small_h)
            img_small = mimg.resize(small_size, Image.Resampling.LANCZOS)
            self.logo_small = ImageTk.PhotoImage(img_small)
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
            self.logo_small = None

        try:
            # Большое лого - немного увеличиваем и делаем правее
            bimg = Image.open("img/Logo.png")
            big_h = 480  # Немного увеличили (было 450)
            ratio_big = big_h / bimg.height
            big_size = (int(bimg.width * ratio_big), big_h)
            img_big = bimg.resize(big_size, Image.Resampling.LANCZOS)
            self.logo_big = ImageTk.PhotoImage(img_big)
        except Exception as e:
            print(f"Ошибка загрузки большого лого: {e}")
            self.logo_big = None

        try:
            # Изображение people для страницы результатов - уменьшаем размер
            pimg = Image.open("img/people.jpg")
            # Уменьшаем размер для размещения под кнопкой
            people_width = 300
            ratio_people = people_width / pimg.width
            people_size = (people_width, int(pimg.height * ratio_people))
            img_people = pimg.resize(people_size, Image.Resampling.LANCZOS)
            self.people_image = ImageTk.PhotoImage(img_people)
        except Exception as e:
            print(f"Ошибка загрузки people.jpg: {e}")
            print("Убедитесь, что файл people.jpg находится в папке img")
            self.people_image = None

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def start_quiz(self):
        self.current_index = 0
        self.update_question_page()
        self.show_frame("QuestionPage")

    def update_question_page(self):
        page = self.frames["QuestionPage"]
        q = self.questions[self.current_index]
        page.set_question(
            text=q["text"],
            index=self.current_index,
            total=len(self.questions),
            options=q["options"],
        )

    def answer_selected(self, option_text):
        self.show_frame("ResultPage")

    def restart_quiz(self):
        self.show_frame("StartPage")


class StartPage(tk.Frame):
    """Стартовый экран"""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        # --- МИНИ-ЛОГО СЛЕВА СВЕРХУ ---
        if controller.logo_small is not None:
            mini_logo = tk.Label(self, image=controller.logo_small, bg=controller.bg_color)
            mini_logo.place(x=40, y=40, anchor="nw")  # Увеличили отступ для 1920x1080

        # --- БОЛЬШОЕ ЛОГО СПРАВА СНИЗУ - немного увеличиваем и смещаем правее ---
        if controller.logo_big is not None:
            big_logo = tk.Label(self, image=controller.logo_big, bg=controller.bg_color)
            # Смещаем правее (x=150 вместо 100)
            big_logo.place(relx=1.0, rely=1.0, anchor="se", x=250, y=40)

        # Центрируем основной контент по вертикали
        center_frame = tk.Frame(self, bg=controller.bg_color)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ЗАГОЛОВОК
        title = tk.Label(center_frame, text="Тест: какой ты арбуз",
                         font=controller.heading_font,
                         bg=controller.bg_color, fg=controller.primary_color,
                         anchor="center", justify="center")
        title.pack(pady=(0, 40))

        # ПОДЗАГОЛОВОК
        subtitle = tk.Label(center_frame, text="Ну что, поехали?",
                            font=controller.main_font,
                            bg=controller.bg_color,
                            anchor="center", justify="center")
        subtitle.pack(pady=(0, 80))

        # КНОПКА СТАРТА (закругленная)
        start_btn = RoundedButton(center_frame, text="Поехали!",
                                  command=controller.start_quiz,
                                  width=400, height=80,  # Увеличили для 1920x1080
                                  bg_color=controller.primary_color,
                                  hover_color=controller.accent_color,
                                  font=controller.button_font)
        start_btn.pack(pady=(0, 20))


class QuestionPage(tk.Frame):
    """Экран с вопросом и вариантами ответов"""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        # --- МИНИ-ЛОГО СЛЕВА СВЕРХУ ---
        if controller.logo_small is not None:
            mini_logo = tk.Label(self, image=controller.logo_small, bg=controller.bg_color)
            mini_logo.place(x=40, y=40, anchor="nw")  # Увеличили отступ для 1920x1080

        # --- БОЛЬШОЕ ЛОГО СПРАВА СНИЗУ - немного увеличиваем и смещаем правее ---
        if controller.logo_big is not None:
            big_logo = tk.Label(self, image=controller.logo_big, bg=controller.bg_color)
            # Смещаем правее (x=150 вместо 100)
            big_logo.place(relx=1.0, rely=1.0, anchor="se", x=250, y=40)

        # Центрируем основной контент по вертикали
        center_frame = tk.Frame(self, bg=controller.bg_color)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Прогресс «Вопрос 1 из 10» - размещаем выше
        self.progress_label = tk.Label(center_frame, font=controller.main_font,
                                       bg=controller.bg_color)
        self.progress_label.pack(pady=(0, 40))

        # ВОПРОС
        self.question_label = tk.Label(center_frame, font=controller.heading_font,
                                       bg=controller.bg_color, fg=controller.primary_color,
                                       anchor="center", justify="center")
        self.question_label.pack(pady=(0, 60))

        # БЛОК ВАРИАНТОВ ОТВЕТА (кнопки)
        self.options_frame = tk.Frame(center_frame, bg=controller.bg_color)
        self.options_frame.pack(pady=(0, 20))
        self.option_buttons = []

    def set_question(self, text, index, total, options):
        self.question_label.config(text=text)
        self.progress_label.config(text=f"Вопрос {index + 1} из {total}")

        # очистить старые кнопки
        for b in self.option_buttons:
            b.destroy()
        self.option_buttons.clear()

        for i, opt in enumerate(options):
            btn = RoundedButton(self.options_frame, text=opt,
                                command=lambda o=opt: self.controller.answer_selected(o),
                                width=600, height=70,  # Увеличили для 1920x1080
                                bg_color=self.controller.primary_color,
                                hover_color=self.controller.accent_color,
                                font=self.controller.main_font)
            btn.pack(pady=12)
            self.option_buttons.append(btn)


class ResultPage(tk.Frame):
    """Экран результатов с изображением"""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        # --- МИНИ-ЛОГО СЛЕВА СВЕРХУ ---
        if controller.logo_small is not None:
            mini_logo = tk.Label(self, image=controller.logo_small, bg=controller.bg_color)
            mini_logo.place(x=40, y=40, anchor="nw")  # Увеличили отступ для 1920x1080

        # --- БОЛЬШОЕ ЛОГО СПРАВА СНИЗУ - немного увеличиваем и смещаем правее ---
        if controller.logo_big is not None:
            big_logo = tk.Label(self, image=controller.logo_big, bg=controller.bg_color)
            # Смещаем правее (x=150 вместо 100)
            big_logo.place(relx=1.0, rely=1.0, anchor="se", x=250, y=40)

        # Центрируем основной контент по вертикали
        center_frame = tk.Frame(self, bg=controller.bg_color)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(center_frame, text="Тест завершен!",
                         font=controller.heading_font,
                         bg=controller.bg_color, fg=controller.primary_color,
                         anchor="center", justify="center")
        title.pack(pady=(0, 40))

        info = tk.Label(center_frame, text="Исходя из твоих ответов ИИ видит тебя\nвот так:",
                        font=controller.main_font,
                        bg=controller.bg_color,
                        anchor="center", justify="center")
        info.pack(pady=(0, 40))

        # Текст результата
        self.result_label = tk.Label(center_frame,
                                     text="Твоя специальность - это\n"
                                          "информационные системы и\n"
                                          "программирование",
                                     font=controller.main_font,
                                     bg=controller.bg_color,
                                     anchor="center", justify="center")
        self.result_label.pack(pady=(0, 50))

        # Кнопка «пройти ещё раз» - шире
        restart_btn = RoundedButton(center_frame, text="Пройти тест ещё раз",
                                    command=controller.restart_quiz,
                                    width=500, height=80,  # Увеличили для 1920x1080
                                    bg_color=controller.primary_color,
                                    hover_color=controller.accent_color,
                                    font=controller.button_font)
        restart_btn.pack(pady=(0, 40))

        # --- ИЗОБРАЖЕНИЕ PEOPLE - перемещаем под кнопку и уменьшаем ---
        if controller.people_image is not None:
            people_label = tk.Label(center_frame, image=controller.people_image, bg=controller.bg_color)
            people_label.pack(pady=(0, 20))
        else:
            # Если изображение не загружено, показываем сообщение
            error_label = tk.Label(center_frame,
                                   text="Ошибка загрузки изображения\nПроверьте файл people.jpg в папке img",
                                   font=controller.small_font,
                                   bg=controller.bg_color, fg="red",
                                   anchor="center", justify="center")
            error_label.pack(pady=(0, 20))


if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()