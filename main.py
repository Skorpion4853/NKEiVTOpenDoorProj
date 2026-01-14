import json

from Logger import write_error, write_warning
from tkinter.messagebox import showerror
from Frames import *
from BackEnd import *
#******* Глобальные переменные (пути к файлам) *******

path_mini_logo = 'source/image/system/Logo+name.png'
path_big_logo = 'source/image/system/Logo.png'





#*************************
#*    Основное окно      *
#*************************

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()

        #******* Настройки окна приложения *******

        self.title("Тест: IT-специалист будущего")                      # Наименование окна
        self.geometry("1920x1080")                                      # Его разрешение
        self.configure(bg="#F0F0F0")                                    # Задний фон приложения


        #******* Установка глобальных шрифтов *******

        self.heading_font = ("Arial", 40, "bold")                       # Шрифт для заголовков
        self.button_font = ("Arial", 30, "bold")                        # Шрифт для клавиш
        self.main_font = ("Arial", 24)                                  # Шрифт для основного текста
        self.small_font = ("Arial", 16)                                 # Шрифт для маленького текста


        #******* Установка глобальных цветов *******

        self.primary_color = "#1F43CD"                                  # Основной цвет
        self.second_color = "#5EC9F5"                                   # Второстепенный цвет
        self.bg_color = "#F0F0F0"                                       # Цвет заднего фона
        self.white = "#FFFFFF"                                          # Белый цвет


        #******* Установка заглушек для будущего лого *******

        self.logo_small = None                                          # Путь к маленькому лого
        self.logo_big = None                                            # Путь к большому лого
        self.user_photo = None                                          # Путь к фото пользователя
        self.loaded_photo_path = None                                   # Путь к загруженному фото
        self.load_images()                                              # Вызов функции что открывает изображения и сохраняет их в атрибуты


        # ******* Пути к ответам и вопросам *******

        self.result_path = "source/Question database/result.json"
        self.questions_path = "source/Question database/questions.json"


        # ******* Создание контейнеров *******

        self.container = tk.Frame(self, bg=self.bg_color)                # Создание первичного контейнера|кадра|фрейма
        self.container.pack(fill="both", expand=True)                    # Установка контейнера в окно, с параметром "занять всё окно"
        self.container.rowconfigure(0, weight=1)                   # Установка весов для каждой строки (чтобы они занимали одинаковое пространство)
        self.container.columnconfigure(0, weight=1)                # Установка весов для каждого столбца (чтобы они занимали одинаковое пространство)

        self.frames = {}                                                 # Список всех контейнеров
        for F in (StartPage, QuestionPage, ResultPage, CameraPage, UploadPhotoPage):
            frame = F(parent=self.container, controller=self)            # Создания класса с установленными выше параметрами
            self.frames[F.__name__] = frame                              # Создание связи "Имя: класс" для словаря
            frame.grid(row=0, column=0, sticky="nsew")                   # Размещение контейнера в окне

        self.show_frame("StartPage")                                     # Отобразить контейнер с именем "StartPage"


        # ******* Создание параметров для теста *******
        self.current_index = 0
        self.answers_score = 0
        self.code = []
        self.questions = json.load(open(self.questions_path))
        self.question_names = list(self.questions.keys())
        self.results = json.load(open(self.result_path))
        self.result_specialty = None



    # **********************************
    # *   Функция загрузки логотипов   *
    # **********************************
    def load_images(self):
        global path_mini_logo, path_big_logo
        try:
            mimg = Image.open(path_mini_logo)
            small_h = 80
            ratio_small = small_h / mimg.height
            small_size = (int(mimg.width * ratio_small), small_h)
            img_small = mimg.resize(small_size, Image.Resampling.LANCZOS)
            self.logo_small = ImageTk.PhotoImage(img_small)
        except Exception as e:
            error_text = f"Ошибка загрузки логотипа: MiniLogoLoadError({e})"
            write_error("LoadImage",  error_text)                    # Дополнительное логирование
            showerror("MiniLogoLoadError", error_text)
            self.logo_small = None

        try:
            bimg = Image.open(path_big_logo)
            big_h = 480
            ratio_big = big_h / bimg.height
            big_size = (int(bimg.width * ratio_big), big_h)
            img_big = bimg.resize(big_size, Image.Resampling.LANCZOS)
            self.logo_big = ImageTk.PhotoImage(img_big)
        except Exception as e:
            error_text = f"Ошибка загрузки логотипа: BigLogoLoadError({e})"
            write_error("LoadImage", error_text)                      # Дополнительное логирование
            showerror("BigLogoLoadError", error_text)
            self.logo_big = None


    # *************************************
    # *   Функция отрисовки контейнеров   *
    # *************************************
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()


    # *****************************
    # *   Функция запуска теста   *
    # *****************************
    def start_quiz(self):
        self.current_index = 0
        #self.answers_score = {i: 0 for i in range(len(self.specialties))}
        self.update_question_page()
        self.show_frame("QuestionPage")

    # ********************************
    # *   Функция обновления теста   *
    # ********************************
    def update_question_page(self):
        page = self.frames["QuestionPage"]
        q = self.questions[self.question_names[self.current_index]]
        page.set_question(
            text = q["text"],
            index = self.current_index,
            total = len(self.questions),
            options = q["options"])

    # *****************************
    # *   Функция выбора ответа   *
    # *****************************
    def answer_selected(self, option_text):
        current_question = self.questions[self.question_names[self.current_index]]
        option_index = current_question["options"].index(option_text)
        #specialty_index = current_question["scores"][option_index]

        self.answers_score += current_question["weights"][option_index]
        self.code.append(current_question["codes"][option_index])

        self.current_index += 1
        if self.current_index < len(self.questions):                            #Если индекс меньше количества вопросов, обновляем тест
            self.update_question_page()
        else:
            self.calculate_result()     #В противном случае выводит итоговую страницу
            self.frames["ResultPage"].update_result()
            self.show_frame("ResultPage")


    # ************************************
    # *   Функция подсчёта результатов   *
    # ************************************
    def calculate_result(self):
        top_specialties = []                                                     #Переменная что хранит в себе всё специальности что подходят
        flag = True
        for i in self.results:
            if self.results[i]["code"] == self.code:
                top_specialties.append(self.results[i])
                flag = False
            elif self.answers_score in range(self.results[i]["weight_code"]["mn"], self.results[i]["weight_code"]["mx"]):
                top_specialties.append(self.results[i])
                flag = False
        if flag:
            warnings_text = "Ни один результат не подходит: EmptyResultError"
            write_error("EmptyResultError", warnings_text)              # Дополнительное логирование
            showerror("EmptyResultError", warnings_text)
            top_specialties = self.results[0]

        self.result_specialty = top_specialties[0]


    # *****************************************
    # *   Функция вывода текста результатов   *
    # *****************************************
    def get_result_text(self):
        if self.result_specialty is not None:
            spec = self.result_specialty
            return f"Ваша специальность:\n{spec['spec_code']}\n{spec['label']}\n\n{spec['text']}"
        return "Не удалось определить специальность"


    # ******************************************
    # *   Функция вывода промпта результатов   *
    # ******************************************
    def get_result_prompt(self):
        if self.result_specialty is not None:
            prompt = self.result_specialty['prompt']
            if self.loaded_photo_path:
                prompt += f" [Изображение пользователя: {self.loaded_photo_path}]"
            return prompt
        return ""

    # *********************************
    # *   Функция перезапуска теста   *
    # *********************************
    def restart_quiz(self):
        self.current_index = 0
        self.answers_score = 0
        self.result_specialty = None
        self.loaded_photo_path = None
        self.user_photo = None
        self.show_frame("StartPage")



app = QuizApp()
app.mainloop()