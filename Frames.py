from Buttons import *


#************************
#*    Стартовое окно    *
#************************
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)
        self.controller = controller
        self.labelTest = "Тест: IT-специалист будущего"
        self.descTest = "Узнай, какая IT-специальность тебе подходит!\nОтветь на 10 вопросов"

        if controller.logo_small is not None:
            mini_logo = tk.Label(self, image=controller.logo_small, bg=controller.bg_color)
            mini_logo.place(x=40, y=40, anchor="nw")

        if controller.logo_big is not None:
            big_logo = tk.Label(self, image=controller.logo_big, bg=controller.bg_color)
            big_logo.place(relx=1.0, rely=1.0, anchor="se", x=250, y=40)

        center_frame = tk.Frame(self, bg=controller.bg_color)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(center_frame, text=self.labelTest,
                         font=controller.heading_font,
                         bg=controller.bg_color, fg=controller.primary_color,
                         anchor="center", justify="center")
        title.pack(pady=(0, 40))

        subtitle = tk.Label(center_frame, text=self.descTest,
                            font=controller.main_font,
                            bg=controller.bg_color,
                            anchor="center", justify="center")
        subtitle.pack(pady=(0, 80))

        start_btn = RoundedButton(center_frame, text="Начать тест",
                                  command=controller.start_quiz,
                                  width=400, height=80,
                                  bg_color=controller.primary_color,
                                  hover_color=controller.second_color,
                                  font=controller.button_font)
        start_btn.pack(pady=(0, 20))



#*****************************
#*    Вопросительное окно    *
#*****************************
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
                                hover_color=self.controller.second_color,
                                font=self.controller.main_font)
            btn.pack(pady=10)
            self.option_buttons.append(btn)

#************************
#*    Итоговое окно    *
#************************
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
                                   hover_color=controller.second_color,
                                   font=controller.button_font)
        upload_btn.pack(pady=20)

        restart_btn = RoundedButton(buttons_container, text="Пройти тест ещё раз",
                                    command=controller.restart_quiz,
                                    width=800, height=70,  # Уменьшил ширину
                                    bg_color=controller.second_color,
                                    hover_color=controller.primary_color,
                                    font=controller.button_font)
        restart_btn.pack(pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def update_result(self):
        result_text = self.controller.get_result_text()
        self.result_label.config(text=result_text)