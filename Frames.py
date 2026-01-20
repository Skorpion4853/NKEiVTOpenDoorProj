from Buttons import *
import cv2
import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import time
from generator import generate_image
from Logger import write_error
from tkinter.messagebox import showerror

''
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

#***********************
#*    Итоговое окно    *
#***********************
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

        # ===== Основной контейнер как в BackEnd =====
        main_container = tk.Frame(self, bg=controller.bg_color)
        main_container.place(relx=0.51, rely=0.5, anchor="center", width=1000, height=800)

        canvas = tk.Canvas(main_container, bg=controller.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=controller.bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ===== Контент =====

        title = tk.Label(scrollable_frame, text="Тест завершен!",
                         font=controller.heading_font,
                         bg=controller.bg_color, fg=controller.primary_color,
                         anchor="center", justify="center")
        title.pack(pady=(20, 30))

        # Фото результата
        self.photo_label = tk.Label(scrollable_frame, bg=controller.bg_color)
        self.photo_label.pack(pady=(0, 30))

        # Текст результата
        self.result_label = tk.Label(scrollable_frame,
                                     text="",
                                     font=controller.main_font,
                                     bg=controller.bg_color,
                                     anchor="center", justify="center",
                                     wraplength=900)
        self.result_label.pack(pady=(0, 40), padx=50)

        # Кнопки
        buttons_container = tk.Frame(scrollable_frame, bg=controller.bg_color)
        buttons_container.pack(pady=(0, 40))

        upload_btn = RoundedButton(buttons_container, text="Сгенерировать изображение",
                                   command=lambda: controller.show_frame("CameraPage"),
                                   width=800, height=70,
                                   bg_color=controller.primary_color,
                                   hover_color=controller.second_color,
                                   font=controller.button_font)
        upload_btn.pack(pady=20)

        restart_btn = RoundedButton(buttons_container, text="Пройти тест ещё раз",
                                    command=controller.restart_quiz,
                                    width=800, height=70,
                                    bg_color=controller.primary_color,
                                    hover_color=controller.second_color,
                                    font=controller.button_font)
        restart_btn.pack(pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def update_result(self):
        result_text = self.controller.get_result_text()
        self.result_label.config(text=result_text)

        # Если есть сгенерированное фото — показать
        if getattr(self.controller, "generated_photo", None):
            try:
                img = Image.open(self.controller.generated_photo)
                img = img.resize((400, 400))
                imgtk = ImageTk.PhotoImage(img)

                self.photo_label.configure(image=imgtk)
                self.photo_label.image = imgtk
            except Exception as e:
                write_error("ResultImageError", str(e))


# *******************
# *    Фото окно    *
# *******************
class CameraPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.bg_color)

        self.controller = controller
        self.cap = None
        self.current_cam_index = 0
        self.video_label = None
        self.running = False

        if controller.logo_small is not None:
            mini_logo = tk.Label(self, image=controller.logo_small, bg=controller.bg_color)
            mini_logo.place(x=40, y=40, anchor="nw")

        if controller.logo_big is not None:
            big_logo = tk.Label(self, image=controller.logo_big, bg=controller.bg_color)
            big_logo.place(relx=1.0, rely=1.0, anchor="se", x=250, y=40)

        center_frame = tk.Frame(self, bg=controller.bg_color)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(self, text="Сделайте фото", font=controller.heading_font,
                         bg=controller.bg_color, fg=controller.primary_color)
        title.pack(pady=20)

        # Выбор камеры
        cam_frame = tk.Frame(self, bg=controller.bg_color)
        cam_frame.pack(pady=10)

        tk.Label(cam_frame, text="Камера:", font=controller.main_font,
                 bg=controller.bg_color).pack(side="left", padx=5)

        self.cam_selector = ttk.Combobox(cam_frame, font=controller.main_font, width=5)
        self.cam_selector.pack(side="left")
        self.cam_selector.bind("<<ComboboxSelected>>", self.change_camera)

        # Видео
        self.video_label = tk.Label(self, bg="black")
        self.video_label.pack(pady=20)

        # Кнопки
        btn_frame = tk.Frame(self, bg=controller.bg_color)
        btn_frame.pack(pady=20)


        screenshot_btn = RoundedButton(btn_frame, text="Сгенерировать изображение",
                                 command=self.take_photo,
                                 width=800, height=70,
                                 bg_color=controller.primary_color,
                                 hover_color=controller.second_color,
                                 font=controller.button_font)
        screenshot_btn.pack(pady=20)


        back_btn = RoundedButton(btn_frame, text="Назад",
                                    command=self.go_back,
                                    width=800, height=70,
                                    bg_color=controller.primary_color,
                                    hover_color=controller.second_color,
                                    font=controller.button_font)
        back_btn.pack(pady=20)

        self.find_cameras()

    # Поиск доступных камер
    def find_cameras(self):
        cams = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                cams.append(str(i))
            cap.release()

        if not cams:
            cams = ["0"]

        self.cam_selector["values"] = cams
        self.cam_selector.current(0)
        self.current_cam_index = int(cams[0])

    def change_camera(self, event=None):
        self.current_cam_index = int(self.cam_selector.get())
        self.stop_camera()
        self.start_camera()

    def start_camera(self):
        self.cap = cv2.VideoCapture(self.current_cam_index)
        self.running = True
        self.update_frame()

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.after(20, self.update_frame)

    def make_generation(self):
        controller = self.controller

        if not controller.loaded_photo_path:
            write_error("PhotoNotFoundError", "Фото не найдено, для начало сделайте фото!")
            showerror("Нет фото", "Сначала загрузите или сделайте фото")
            return

        prompt = controller.get_result_prompt()

        out_path = generate_image(controller.loaded_photo_path, prompt)
        controller.generated_photo = out_path   # сохраняем путь

    def take_photo(self):
        if not self.cap:
            return

        ret, frame = self.cap.read()
        if ret:
            os.makedirs("source/user_photos", exist_ok=True)
            filename = f"source/user_photos/user_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)

            # сохраняем путь в контроллер
            self.controller.loaded_photo_path = filename

        self.stop_camera()
        self.make_generation()
        self.controller.frames["ResultPage"].update_result()
        self.controller.show_frame("ResultPage")

    def go_back(self):
        self.stop_camera()
        self.controller.show_frame("ResultPage")

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.start_camera()