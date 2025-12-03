import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import json
import os


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


class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Тест: IT-специалист будущего")
        self.geometry("1920x1080")
        self.configure(bg="#F0F0F0")

        self.heading_font = ("Arial", 40, "bold")
        self.button_font = ("Arial", 30, "bold")
        self.main_font = ("Arial", 24)
        self.small_font = ("Arial", 16)

        self.primary_color = "#1F43CD"
        self.accent_color = "#5EC9F5"
        self.bg_color = "#F0F0F0"
        self.white = "#FFFFFF"

        self.logo_small = None
        self.logo_big = None
        self.user_photo = None
        self.loaded_photo_path = None

        self.load_images()

        self.specialties = {
            0: {
                "code": "09.02.01",
                "name": "Компьютерные системы и комплексы",
                "prompt": "A technical expert in a modern server room or hardware lab, wearing a stylish lab coat or a polo shirt with a company logo, holding a motherboard or a server component. The scene is clean and high-tech, with blue accent lighting. In the style of a professional corporate photoshoot, sharp focus, photorealistic.",
                "description": "Вы - технический специалист, который разбирается в аппаратном обеспечении. Вам интересно, как устроены компьютеры изнутри, как компоненты взаимодействуют между собой."
            },
            1: {
                "code": "09.01.03",
                "name": "Оператор информационных систем и ресурсов",
                "prompt": "A friendly and competent IT operator at a modern, multi-monitor workstation. Screens display data flow diagrams, server status dashboards, and code. The person is smiling, wearing a casual business outfit, in a bright, clean office. Corporate photography style, natural lighting, professional.",
                "description": "Вы - оператор информационных систем. Вам нравится работать с готовыми системами, помогать пользователям, обеспечивать стабильную работу ПО."
            },
            2: {
                "code": "09.02.06",
                "name": "Сетевое и системное администрирование",
                "prompt": "A focused network administrator, crawling under a desk or working in a server rack, tracing ethernet cables. Wearing a casual shirt with a tool belt. The environment is a bit more 'hands-on' with visible network switches and cable management. Dramatic lighting, photorealistic, sense of action.",
                "description": "Вы - сетевой инженер. Вам нравится работать с сетевым оборудованием, настраивать маршрутизацию, обеспечивать стабильную работу сетей."
            },
            3: {
                "code": "09.02.07",
                "name": "Информационные системы и программирование",
                "prompt": "A skilled software developer writing code on a laptop in a creative, modern workspace with plants and a whiteboard full of algorithms in the background. The person has a thoughtful expression, wearing a hoodie or a t-shirt with a geeky print. Dynamic angle, shallow depth of field, cinematic lighting.",
                "description": "Вы - программист. Вам нравится создавать программы, алгоритмы, работать с кодом. У вас аналитический склад ума."
            },
            4: {
                "code": "09.02.13",
                "name": "Интеграция решений с применением технологий искусственного интеллекта",
                "prompt": "A visionary AI specialist interacting with a large, holographic interface displaying neural networks and data streams. The person looks innovative and confident, in a sleek, futuristic environment with neon light accents. Sci-fi aesthetic, cyberpunk elements, high detail, photorealistic.",
                "description": "Вы - специалист по искусственному интеллекту. Вам интересны нейросети, машинное обучение, анализ данных."
            },
            5: {
                "code": "11.02.16",
                "name": "Монтаж, техническое обслуживание и ремонт электронных приборов и устройств",
                "prompt": "A meticulous electronics technician soldering a complex circuit board on a workbench. Wearing protective glasses and an apron, surrounded by oscilloscopes, multimeters, and electronic components. The style is a detailed, close-up shot, workshop lighting, hyper-realistic.",
                "description": "Вы - техник по электронным приборам. Вам нравится работать с электроникой, паять, ремонтировать, разбираться в схемотехнике."
            },
            6: {
                "code": "10.02.05",
                "name": "Обеспечение информационной безопасности автоматизированных систем",
                "prompt": "A cybersecurity analyst in a dimly lit Security Operations Center (SOC), facing a wall of monitors showing lines of code, network maps, and threat detection alerts. The person has a serious, vigilant expression, wearing a dark, tactical-style jacket. Moody lighting, high contrast, cinematic style.",
                "description": "Вы - специалист по информационной безопасности. Вам важно защищать данные, вы умеете мыслить как хакер, чтобы находить уязвимости."
            }
        }

        # Сокращенные варианты ответов для лучшего отображения
        self.questions = [
            {
                "text": "Какую задачу вам было бы интереснее решать?",
                "options": [
                    "Собрать компьютер с оптимальными компонентами",
                    "Написать программу для автоматизации",
                    "Настроить локальную сеть в офисе",
                    "Защитить сеть от хакерских атак"
                ],
                "scores": [0, 3, 2, 6]
            },
            {
                "text": "Что вам ближе в работе с техникой?",
                "options": [
                    "Физический монтаж и пайка",
                    "Настройка ПО и драйверов",
                    "Диагностика сетевых неполадок",
                    "Анализ данных для обучения ИИ"
                ],
                "scores": [5, 1, 2, 4]
            },
            {
                "text": "Какой проект вызвал бы у вас энтузиазм?",
                "options": [
                    "Разработка системы 'умный дом'",
                    "Создание веб-приложения для записи",
                    "Построение VPN-туннеля между филиалами",
                    "Программирование чат-бота с ИИ"
                ],
                "scores": [5, 3, 6, 4]
            },
            {
                "text": "Что для вас важнее в работе?",
                "options": [
                    "Четкие инструкции и последовательность",
                    "Творческий подход и эксперименты",
                    "Реакция на внештатные ситуации",
                    "Работа с большими данными"
                ],
                "scores": [1, 3, 2, 4]
            },
            {
                "text": "Какой формат работы комфортнее?",
                "options": [
                    "Работа с оборудованием 'в железе'",
                    "Удаленная работа с кодом",
                    "Администрирование серверов",
                    "Исследование новых технологий"
                ],
                "scores": [5, 3, 2, 4]
            },
            {
                "text": "Что вызывает большее любопытство?",
                "options": [
                    "Как работает процессор физически",
                    "Как программы взаимодействуют",
                    "Как данные передаются по оптоволокну",
                    "Как предсказать поведение пользователя"
                ],
                "scores": [0, 3, 2, 4]
            },
            {
                "text": "Какую проблему предпочли бы решать?",
                "options": [
                    "Компьютер не включается",
                    "Программа выдает ошибку",
                    "Сеть периодически 'падает'",
                    "Обнаружить уязвимость до хакеров"
                ],
                "scores": [5, 3, 2, 6]
            },
            {
                "text": "Что важнее в IT-системе?",
                "options": [
                    "Надежность оборудования",
                    "Удобный интерфейс",
                    "Быстрота передачи данных",
                    "Защищенность информации"
                ],
                "scores": [0, 3, 2, 6]
            },
            {
                "text": "Какой вид деятельности привлекает?",
                "options": [
                    "Тестирование электронных плат",
                    "Обучение пользователей",
                    "Планирование сетевой инфраструктуры",
                    "Анализ логов на аномалии"
                ],
                "scores": [5, 1, 2, 6]
            },
            {
                "text": "К чему больше склонностей?",
                "options": [
                    "Кропотливая работа с деталями",
                    "Логическое мышление",
                    "Организация процессов",
                    "Математический анализ"
                ],
                "scores": [5, 3, 1, 4]
            }
        ]

        self.current_index = 0
        self.answers_score = {i: 0 for i in range(len(self.specialties))}
        self.result_specialty = None

        self.container = tk.Frame(self, bg=self.bg_color)
        self.container.pack(fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, QuestionPage, ResultPage, UploadPhotoPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def load_images(self):
        try:
            mimg = Image.open("img/Logo+name.png")
            small_h = 80
            ratio_small = small_h / mimg.height
            small_size = (int(mimg.width * ratio_small), small_h)
            img_small = mimg.resize(small_size, Image.Resampling.LANCZOS)
            self.logo_small = ImageTk.PhotoImage(img_small)
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
            self.logo_small = None

        try:
            bimg = Image.open("img/Logo.png")
            big_h = 480
            ratio_big = big_h / bimg.height
            big_size = (int(bimg.width * ratio_big), big_h)
            img_big = bimg.resize(big_size, Image.Resampling.LANCZOS)
            self.logo_big = ImageTk.PhotoImage(img_big)
        except Exception as e:
            print(f"Ошибка загрузки большого лого: {e}")
            self.logo_big = None

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def start_quiz(self):
        self.current_index = 0
        self.answers_score = {i: 0 for i in range(len(self.specialties))}
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
        current_question = self.questions[self.current_index]
        option_index = current_question["options"].index(option_text)
        specialty_index = current_question["scores"][option_index]

        self.answers_score[specialty_index] += 1

        self.current_index += 1
        if self.current_index < len(self.questions):
            self.update_question_page()
        else:
            self.calculate_result()
            # Обновляем результат перед показом страницы
            self.frames["ResultPage"].update_result()
            self.show_frame("ResultPage")

    def calculate_result(self):
        max_score = max(self.answers_score.values())
        top_specialties = [code for code, score in self.answers_score.items() if score == max_score]

        if len(top_specialties) == 1:
            self.result_specialty = top_specialties[0]
        else:
            self.result_specialty = top_specialties[0]

    def get_result_text(self):
        if self.result_specialty is not None:
            spec = self.specialties[self.result_specialty]
            return f"Ваша специальность:\n{spec['code']}\n{spec['name']}\n\n{spec['description']}"
        return "Не удалось определить специальность"

    def get_result_prompt(self):
        if self.result_specialty is not None:
            spec = self.specialties[self.result_specialty]
            prompt = spec['prompt']
            if self.loaded_photo_path:
                prompt += f" [Изображение пользователя: {self.loaded_photo_path}]"
            return prompt
        return ""

    def restart_quiz(self):
        self.current_index = 0
        self.answers_score = {i: 0 for i in range(len(self.specialties))}
        self.result_specialty = None
        self.loaded_photo_path = None
        self.user_photo = None
        self.show_frame("StartPage")


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        if controller.logo_small is not None:
            mini_logo = tk.Label(self, image=controller.logo_small, bg=controller.bg_color)
            mini_logo.place(x=40, y=40, anchor="nw")

        if controller.logo_big is not None:
            big_logo = tk.Label(self, image=controller.logo_big, bg=controller.bg_color)
            big_logo.place(relx=1.0, rely=1.0, anchor="se", x=250, y=40)

        center_frame = tk.Frame(self, bg=controller.bg_color)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(center_frame, text="Тест: IT-специалист будущего",
                         font=controller.heading_font,
                         bg=controller.bg_color, fg=controller.primary_color,
                         anchor="center", justify="center")
        title.pack(pady=(0, 40))

        subtitle = tk.Label(center_frame, text="Узнай, какая IT-специальность тебе подходит!\nОтветь на 10 вопросов",
                            font=controller.main_font,
                            bg=controller.bg_color,
                            anchor="center", justify="center")
        subtitle.pack(pady=(0, 80))

        start_btn = RoundedButton(center_frame, text="Начать тест",
                                  command=controller.start_quiz,
                                  width=400, height=80,
                                  bg_color=controller.primary_color,
                                  hover_color=controller.accent_color,
                                  font=controller.button_font)
        start_btn.pack(pady=(0, 20))


class QuestionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        if controller.logo_small is not None:
            mini_logo = tk.Label(self, image=controller.logo_small, bg=controller.bg_color)
            mini_logo.place(x=40, y=40, anchor="nw")

        if controller.logo_big is not None:
            big_logo = tk.Label(self, image=controller.logo_big, bg=controller.bg_color)
            big_logo.place(relx=1.0, rely=1.0, anchor="se", x=250, y=40)

        center_frame = tk.Frame(self, bg=controller.bg_color)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.progress_label = tk.Label(center_frame, font=controller.main_font,
                                       bg=controller.bg_color)
        self.progress_label.pack(pady=(0, 30))

        self.question_label = tk.Label(center_frame, font=controller.heading_font,
                                       bg=controller.bg_color, fg=controller.primary_color,
                                       anchor="center", justify="center",
                                       wraplength=800)
        self.question_label.pack(pady=(0, 40))

        self.options_frame = tk.Frame(center_frame, bg=controller.bg_color)
        self.options_frame.pack(pady=(0, 10))
        self.option_buttons = []

    def set_question(self, text, index, total, options):
        self.question_label.config(text=text)
        self.progress_label.config(text=f"Вопрос {index + 1} из {total}")

        for b in self.option_buttons:
            b.destroy()
        self.option_buttons.clear()

        for i, opt in enumerate(options):
            btn = RoundedButton(self.options_frame, text=opt,
                                command=lambda o=opt: self.controller.answer_selected(o),
                                width=700, height=80,
                                bg_color=self.controller.primary_color,
                                hover_color=self.controller.accent_color,
                                font=self.controller.main_font)
            btn.pack(pady=10)
            self.option_buttons.append(btn)


class ResultPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        if controller.logo_small is not None:
            mini_logo = tk.Label(self, image=controller.logo_small, bg=controller.bg_color)
            mini_logo.place(x=40, y=40, anchor="nw")

        if controller.logo_big is not None:
            big_logo = tk.Label(self, image=controller.logo_big, bg=controller.bg_color)
            big_logo.place(relx=1.0, rely=1.0, anchor="se", x=250, y=40)

        # Основной контейнер с прокруткой для всего контента
        main_container = tk.Frame(self, bg=controller.bg_color)
        main_container.place(relx=0.5, rely=0.5, anchor="center", width=1000, height=800)

        # Canvas для прокрутки
        canvas = tk.Canvas(main_container, bg=controller.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=controller.bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        title = tk.Label(scrollable_frame, text="Тест завершен!",
                         font=controller.heading_font,
                         bg=controller.bg_color, fg=controller.primary_color,
                         anchor="center", justify="center")
        title.pack(pady=(0, 30))

        # Текст результата
        self.result_label = tk.Label(scrollable_frame,
                                     text="",
                                     font=controller.main_font,
                                     bg=controller.bg_color,
                                     anchor="center", justify="center",
                                     wraplength=900)  # Увеличил ширину для текста
        self.result_label.pack(pady=(0, 40), padx=50)

        # Кнопки расположены вертикально с достаточным пространством
        buttons_container = tk.Frame(scrollable_frame, bg=controller.bg_color)
        buttons_container.pack(pady=(0, 40), padx=50)

        upload_btn = RoundedButton(buttons_container, text="Загрузить фото для генерации",
                                   command=lambda: controller.show_frame("UploadPhotoPage"),
                                   width=800, height=70,  # Уменьшил ширину
                                   bg_color=controller.primary_color,
                                   hover_color=controller.accent_color,
                                   font=controller.button_font)
        upload_btn.pack(pady=20)

        restart_btn = RoundedButton(buttons_container, text="Пройти тест ещё раз",
                                    command=controller.restart_quiz,
                                    width=800, height=70,  # Уменьшил ширину
                                    bg_color=controller.accent_color,
                                    hover_color=controller.primary_color,
                                    font=controller.button_font)
        restart_btn.pack(pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def update_result(self):
        result_text = self.controller.get_result_text()
        self.result_label.config(text=result_text)


class UploadPhotoPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller

        if controller.logo_small is not None:
            mini_logo = tk.Label(self, image=controller.logo_small, bg=controller.bg_color)
            mini_logo.place(x=40, y=40, anchor="nw")

        if controller.logo_big is not None:
            big_logo = tk.Label(self, image=controller.logo_big, bg=controller.bg_color)
            big_logo.place(relx=1.0, rely=1.0, anchor="se", x=250, y=40)

        # Основной контейнер с прокруткой
        main_container = tk.Frame(self, bg=controller.bg_color)
        main_container.place(relx=0.5, rely=0.5, anchor="center", width=1000, height=800)

        canvas = tk.Canvas(main_container, bg=controller.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=controller.bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        title = tk.Label(scrollable_frame, text="Генерация изображения",
                         font=controller.heading_font,
                         bg=controller.bg_color, fg=controller.primary_color,
                         anchor="center", justify="center")
        title.pack(pady=(0, 30))

        # Контейнер для фото
        photo_frame = tk.Frame(scrollable_frame, bg=controller.bg_color)
        photo_frame.pack(pady=(0, 20))

        self.photo_label = tk.Label(photo_frame, text="Фото не загружено",
                                    font=controller.main_font,
                                    bg=controller.bg_color, fg="gray",
                                    width=40, height=15,
                                    relief="solid", borderwidth=2)
        self.photo_label.pack(pady=(0, 10))

        upload_btn = RoundedButton(photo_frame, text="Выбрать фото",
                                   command=self.upload_photo,
                                   width=400, height=70,
                                   bg_color=controller.primary_color,
                                   hover_color=controller.accent_color,
                                   font=controller.button_font)
        upload_btn.pack(pady=(0, 10))

        generate_btn = RoundedButton(scrollable_frame, text="Сгенерировать изображение",
                                     command=self.generate_image,
                                     width=600, height=70,
                                     bg_color="#5EC9F5",
                                     hover_color="#1F43CD",
                                     font=controller.button_font)
        generate_btn.pack(pady=(0, 30))

        # Контейнер для промпта с прокруткой
        prompt_container = tk.Frame(scrollable_frame, bg=controller.bg_color)
        prompt_container.pack(pady=(0, 20), fill="x", padx=50)

        prompt_label_title = tk.Label(prompt_container, text="Промпт для генерации:",
                                      font=controller.main_font,
                                      bg=controller.bg_color,
                                      anchor="w", justify="left")
        prompt_label_title.pack(anchor="w", pady=(0, 5))

        prompt_canvas = tk.Canvas(prompt_container, bg=controller.bg_color,
                                  height=150, width=900, highlightthickness=0,
                                  relief="solid", borderwidth=1)
        prompt_scrollbar = tk.Scrollbar(prompt_container, orient="vertical", command=prompt_canvas.yview)
        scrollable_prompt_frame = tk.Frame(prompt_canvas, bg=controller.bg_color)

        scrollable_prompt_frame.bind(
            "<Configure>",
            lambda e: prompt_canvas.configure(scrollregion=prompt_canvas.bbox("all"))
        )

        prompt_canvas.create_window((0, 0), window=scrollable_prompt_frame, anchor="nw")
        prompt_canvas.configure(yscrollcommand=prompt_scrollbar.set)

        self.prompt_text = tk.Text(scrollable_prompt_frame,
                                   font=controller.small_font,
                                   bg=controller.bg_color,
                                   wrap="word",
                                   width=90, height=6,
                                   relief="flat")
        self.prompt_text.pack(padx=10, pady=10)
        self.prompt_text.config(state="disabled")

        prompt_canvas.pack(side="left", fill="both", expand=True)
        prompt_scrollbar.pack(side="right", fill="y")

        back_btn = RoundedButton(scrollable_frame, text="Назад к результатам",
                                 command=lambda: controller.show_frame("ResultPage"),
                                 width=500, height=60,
                                 bg_color="#AAAAAA",
                                 hover_color="#888888",
                                 font=controller.button_font)
        back_btn.pack(pady=(0, 40))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            title="Выберите фото",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )

        if file_path:
            try:
                self.controller.loaded_photo_path = file_path
                img = Image.open(file_path)
                img.thumbnail((400, 400))  # Увеличил размер превью
                photo = ImageTk.PhotoImage(img)

                self.photo_label.config(
                    text="",
                    image=photo,
                    width=400,
                    height=400
                )
                self.photo_label.image = photo

                # Обновляем промпт
                self.update_prompt()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить фото: {e}")

    def update_prompt(self):
        prompt = self.controller.get_result_prompt()
        if prompt:
            self.prompt_text.config(state="normal")
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(1.0, prompt)
            self.prompt_text.config(state="disabled")

    def generate_image(self):
        if not self.controller.loaded_photo_path:
            messagebox.showwarning("Внимание", "Сначала загрузите фото!")
            return

        prompt = self.controller.get_result_prompt()
        if prompt:
            # Сохраняем промпт в файл
            try:
                with open("generated_prompt.txt", "w", encoding="utf-8") as f:
                    f.write(prompt)

                messagebox.showinfo("Готово",
                                    f"Промпт сохранен в файл 'generated_prompt.txt'!\n\n"
                                    f"Для генерации изображения используйте этот промпт в AI-сервисах:\n"
                                    f"1. Midjourney\n"
                                    f"2. Stable Diffusion\n"
                                    f"3. DALL-E\n\n"
                                    f"Загрузите ваше фото и вставьте промпт.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить промпт: {e}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать промпт")


if __name__ == "__main__":
    app = QuizApp()


    def on_closing():
        app.quit()


    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()