from Buttons import *
from tkinter import filedialog, messagebox
from generator import generate_image
from Logger import write_error
from tkinter.messagebox import showerror

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
                                   hover_color=controller.second_color,
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
                write_error(e, "Не удалось загрузить фото")

    def update_prompt(self):
        prompt = self.controller.get_result_prompt()
        if prompt:
            self.prompt_text.config(state="normal")
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(1.0, prompt)
            self.prompt_text.config(state="disabled")

    def make_generation(self):
        controller = self.controller

        if not controller.loaded_photo_path:
            write_error("PhotoNotFoundError", "Фото не найдено, для начало сделайте фото!")
            showerror("Нет фото", "Сначала загрузите или сделайте фото")
            return

        prompt = controller.get_result_prompt()

        out_path = generate_image(controller.loaded_photo_path, prompt)
        controller.generated_photo = out_path  # сохраняем путь
        self.controller.frames["ResultPage"].update_result()
        self.controller.show_frame("ResultPage")

    def generate_image(self):
        if not self.controller.loaded_photo_path:
            messagebox.showwarning("Внимание", "Сначала загрузите фото!")
            return

        prompt = self.controller.get_result_prompt()
        self.make_generation()