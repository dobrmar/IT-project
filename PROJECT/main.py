import pygame
import datetime
import shelve
import random
import os.path


pygame.init()
screen = pygame.display.set_mode((1300, 800))


def print_text(text, x, y, color=(255, 255, 255), font_type="comic sans ms", font_size=30):
    font = pygame.font.SysFont(font_type, font_size)
    text = font.render(text, 1, color)
    screen.blit(text, (x, y))


class InputArea:
    def __init__(self, width=200, height=150, color=(0, 0, 0), passw=False, max_s=20, font_type="comic sans ms",
                 text_color=(255, 255, 255), text_size=30, answer=''):
        self.width = width
        self.height = height
        self.color = color
        self.text_size = text_size
        self.font_type = font_type
        self.text_color = text_color
        self.font_size = text_size
        self.answer = answer
        self.writing = False
        self.got_answer = False
        self.password = passw
        self.max_s = max_s

    def show_area(self, x, y):
        global state
        global running

        pygame.draw.rect(screen, self.color, (x, y, self.width, self.height))
        print_text(self.answer, x + 10, y + 10, self.text_color, self.font_type, self.font_size)

    def is_writing(self, x, y):
        global running
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width:
            if y < mouse[1] < y + self.height:
                if click[0]:
                    self.writing = True
                    pygame.time.delay(200)

        while self.writing:
            pygame.draw.rect(screen, self.color, (x, y, self.width, self.height))
            if self.password:
                print_text('*' * len(self.answer), x + 10, y + 10, self.text_color, self.font_type, self.font_size)
            else:
                print_text(self.answer, x + 10, y + 10, self.text_color, self.font_type, self.font_size)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.writing = False
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.writing = False
                    elif event.key == pygame.K_RETURN:
                        self.writing = False
                        self.got_answer = True
                    elif event.key == pygame.K_BACKSPACE:
                        if len(self.answer):
                            self.answer = self.answer[:-1]
                    elif len(self.answer) < self.max_s:
                        self.answer += event.unicode
            pygame.display.flip()
            clock.tick(60)


class Button:
    def __init__(self, text, width=300, height=70, color=(5, 171, 121), font_type="comic sans ms",
                 text_color=(255, 255, 255), text_size=30):
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.text_size = text_size
        self.font_type = font_type
        self.text_color = text_color
        self.font_size = text_size

    def show_button(self, x, y, act, act_p=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        pygame.draw.rect(screen, self.color, (x, y, self.width, self.height))
        print_text(self.text, x + 10, y + 10, self.text_color, self.font_type, self.font_size)

        if x < mouse[0] < x + self.width:
            if y < mouse[1] < y + self.height:
                if click[0]:
                    if not act_p:
                        act()
                    else:
                        act(act_p)
                    pygame.time.delay(200)


class GameObject:
    def __init__(self, theme, complexity, recent_time, recent_lvl, desolation_time, completion_num):
        global state
        self.theme = theme  # Текущая тема
        self.complexity = complexity  # Сложность
        self.recent_time = recent_time
        self.completion_num = completion_num
        self.desolation_time = desolation_time
        delta_time = datetime.datetime.today() - recent_time  # Время, прошедшее с последнего использования
        delta_time = delta_time.total_seconds()
        delta_time = delta_time / 3600
        level_down = delta_time / desolation_time  # Доля шкалы, на которую произошло понижение
        if level_down >= recent_lvl:  # Проверка на жизнь
            self.level = 0
            self.happy = 'feelsdeadman'
            self.dead = True
        else:
            self.dead = False
            self.level = recent_lvl - level_down
            if self.level <= 0.25:
                self.happy = 'pepehands'
            elif self.level <= 0.5:
                self.happy = 'feelsbadman'
            elif self.level <= 0.75:
                self.happy = 'feelsgoodman'
            else:
                self.happy = 'pogchamp'
        self.speed = 1 / completion_num
        self.que = {}
        self.q = None
        self.a = None
        self.state = 'ask_new'
        self.last_q = ''

    def question(self):
        global answer_area
        global current_acc
        global statics
        if self.state == 'ask_new':
            answer_area = InputArea(470)
            self.state = 'ans_waiting'
            self.q = random.choice(list(self.que.keys()))
            self.a = self.que[self.q]
        print_text("Вопрос: " + str(self.q), 100, 400, (255, 255, 255))
        print_text(current_acc, 100, 50)
        if self.state == 'ans_waiting':
            answer_area.show_area(500, 400)
            answer_area.is_writing(500, 400)
            if answer_area.got_answer:
                self.last_q = answer_area.answer
                self.state = 'button_waiting'
                del answer_area
                if str(self.last_q) == str(self.a):
                    self.level += self.speed
                    if self.level > 1:
                        self.level = 1
                    self.update()
                    self.safe()
                    statics[current_acc][self.complexity][0] += 1
                else:
                    statics[current_acc][self.complexity][1] += 1
        elif self.state == 'button_waiting':
            if str(self.last_q) == str(self.a):
                print_text("Верно!", 500, 400, (0, 255, 0))
            else:
                print_text("Неверно!", 500, 400, (255, 0, 0))
            show.play_button_next.show_button(500, 500, show.play_action_next)

    def update(self):
        global state
        delta_time = datetime.datetime.today() - self.recent_time
        delta_time = delta_time.total_seconds()
        delta_time = delta_time / 3600
        level_down = delta_time / self.desolation_time
        self.level -= level_down
        self.recent_time = datetime.datetime.today()

        if self.level <= 0:
            self.level = 0
            self.dead = True
            self.happy = 'feelsdeadman'
        elif self.level <= 0.25:
            self.happy = 'pepehands'
        elif self.level <= 0.5:
            self.happy = 'feelsbadman'
        elif self.level <= 0.75:
            self.happy = 'feelsgoodman'
        else:
            self.happy = 'pogchamp'
        self.safe()

    def safe(self):
        global current_acc
        file[current_acc] = {
            'theme': self.theme,
            'complexity': self.complexity,
            'recent_time': self.recent_time,
            'recent_lvl': self.level,
            'desolation_time': self.desolation_time,
            'completion_num': self.completion_num
        }


class Screens:
    def __init__(self):
        self.pause_color = (0, 0, 100)
        self.menu_color = (0, 0, 100)

        self.input_answer = InputArea()
        self.play_color = (0, 100, 100)
        self.play_button_next = Button("следующий вопрос", 300, 70, color=(0, 0, 155))

        self.settings_p_message = "Введите пароль:"

        self.settings_color = (0, 0, 100)

        self.des_time_text = ""
        self.com_num_text = ""
        self.change_password_text = ""
        self.frozen_button = Button("использовать")
        self.frozen_text = ""
        self.frozen_area = InputArea(100, 50, (0, 0, 0), False, 5)

        self.add_theme_text = ""
        self.new_acc_text = ""

        self.death_button = Button("да", 100, 70, (0, 0, 155))

    def frozen_action(self):
        print('nice nice')
        try:
            x = float(self.frozen_area.answer)
            if x > 0:
                self.frozen_text = "Активировано"
            else:
                self.frozen_area.answer = ""
                self.frozen_text = "значение должно быть положительным числом"
        except:
            self.frozen_area.answer = ""
            self.frozen_text = "значение должно быть положительным числом"

    def death_action(self):
        global game
        global state
        game = GameObject(game.theme, game.complexity, datetime.datetime.today(),
                          0.5, game.desolation_time, game.completion_num)
        state = "play"
        game.que = file1[game.theme][game.complexity]

    def play_action_next(self):
        game.state = 'ask_new'

    def pause_action_1(self):
        global state
        state = "play"

    def pause_action_2(self):
        global state
        state = "menu"

    def pause_action_3(self):
        global running
        running = False

    def menu_action_1(self):
        global state
        state = "change_acc"
        self.first_list = 0

    def menu_action_2(self):
        global state
        state = "settings_p"

    def menu_action_3(self):
        global state
        state = "sets"
        self.first_list = 0

    def menu_action_4(self):
        global state
        global current_acc
        state = "stats"
        self.save_stats = InputArea(width=400, height=70, answer="{}_stats".format(current_acc))
        self.save_stats_text = ""

    def settings_action_1(self):
        global state
        state = "change_theme"
        self.first_list = 0

    def settings_action_2(self):
        global state
        self.des_time_text = ""
        self.com_num_text = ""
        self.frozen_text = ""
        state = "time"

    def settings_action_3(self):
        global state
        state = "change_password"

    def settings_action_4(self):
        global state
        state = "change_complexity"

    def choose_theme_action(self, theme):
        game.theme = theme
        game.que = file1[theme][game.complexity]
        game.state = "ask_new"

    def edit_theme_save(self):
        global file1
        global state
        global edit_this_theme
        file1[edit_this_theme] = {0: {}, 1: {}, 2: {}}
        for i in range(len(questions)):
            file1[edit_this_theme][answers[i][0]][questions[i]] = answers[i][1]
        game.que = file1[game.theme][game.complexity]
        game.state = "ask_new"
        state = "menu"

    def show_theme_action(self, theme):
        global state
        global questions
        global answers
        global edit_this_theme
        edit_this_theme = theme
        self.first_list = 0
        questions = list(file1[theme][0].keys())
        answers = []
        for i in questions:
            answers.append([0, file1[theme][0][i]])
        questions = list(file1[theme][1].keys())
        for i in questions:
            answers.append([1, file1[theme][1][i]])
        questions = list(file1[theme][2].keys())
        for i in questions:
            answers.append([2, file1[theme][2][i]])
        questions = list(file1[theme][0].keys()) + list(file1[theme][1].keys()) + list(file1[theme][2].keys())
        state = "edit_theme"

    def death(self):
        screen.fill(self.play_color)
        #print_text(game.happy, 200, 100, (120, 200, 200))
        image = pygame.image.load('images/{}.png'.format(game.happy)).convert_alpha()
        image = pygame.transform.scale(image, (150, 150))
        screen.blit(image, [200, 100])
        print_text(str(game.level)[:4], 400, 250, (120, 200, 200))
        print_text("Уровень ноль. Перезапустить аккаунт?", 200, 500)
        self.death_button.show_button(200, 600, self.death_action)

    def pause(self):
        screen.fill(self.pause_color)
        Button("продолжить").show_button(500, 100, self.pause_action_1)
        Button("меню").show_button(500, 250, self.pause_action_2)
        Button("выход").show_button(500, 400, self.pause_action_3)

    def menu(self):
        screen.fill(self.menu_color)
        Button("смена пользователя").show_button(500, 100, self.menu_action_1)
        Button("настройки").show_button(500, 250, self.menu_action_2)
        Button("наборы").show_button(500, 400, self.menu_action_3)
        Button("статистика").show_button(500, 550, self.menu_action_4)

    def play(self):
        global state
        if game.dead:
            state = "death"
            return
        screen.fill(self.play_color)
        #print_text(game.happy, 200, 100, (120, 200, 200))
        image = pygame.image.load('images/{}.png'.format(game.happy)).convert_alpha()
        image = pygame.transform.scale(image, (150, 150))
        screen.blit(image, [200, 100])
        print_text(str(game.level)[:4], 400, 250, (120, 200, 200))
        game.question()

    def settings_p(self):
        global state
        screen.fill(self.settings_color)
        print_text(self.settings_p_message, 200, 100, (120, 200, 200))
        password_area = InputArea(400, 150, (0, 0, 0), True, 12)
        password_area.show_area(200, 400)
        password_area.is_writing(200, 400)
        if password_area.got_answer:
            if password_area.answer == password:
                del password_area
                state = "settings"
                self.settings_p_message = "Введите пароль"
            else:
                password_area.answer = ''
                self.settings_p_message = "Неверный пароль! Попробуйте еще раз"

    def settings(self):
        screen.fill(self.settings_color)
        Button("сменить тему").show_button(500, 100, self.settings_action_1)
        Button("настройки времени").show_button(500, 250, self.settings_action_2)
        Button("сменить пароль").show_button(500, 400, self.settings_action_3)
        Button("уровень сложности").show_button(500, 550, self.settings_action_4)

    def time(self):
        screen.fill(self.settings_color)
        print_text("desolation_time:", 50, 100)
        print_text("ч", 400, 100)
        print_text(self.des_time_text, 500, 100)
        des_time_area = InputArea(100, 50, (0, 0, 0), False, 5)
        des_time_area.show_area(300, 100)
        print_text("completion_num:", 50, 200)
        com_num_area = InputArea(100, 50, (0, 0, 0), False, 5)
        com_num_area.show_area(300, 200)
        print_text(self.com_num_text, 500, 200)

        print_text("Заморозка:", 50, 300)
        print_text("ч", 400, 300)
        print_text(self.frozen_text, 800, 300)
        self.frozen_button.show_button(450, 300, self.frozen_action)
        self.frozen_area.show_area(300, 300)
        des_time_area.is_writing(300, 100)
        if des_time_area.got_answer:
            try:
                x = float(des_time_area.answer)
                if x > 0:
                    self.des_time_text = "Сохранено"
                    game.desolation_time = x
                else:
                    des_time_area.answer = ""
                    self.des_time_text = "значение должно быть положительным числом"
            except:
                des_time_area.answer = ""
                self.des_time_text = "значение должно быть положительным числом"
        com_num_area.is_writing(300, 200)
        if com_num_area.got_answer:
            try:
                x = int(com_num_area.answer)
                if x > 0:
                    self.com_num_text = "Сохранено"
                    game.completion_num = x
                    game.speed = 1 / game.completion_num
                else:
                    com_num_area.answer = ""
                    self.com_num_text = "значение должно быть натуральным числом"
            except:
                com_num_area.answer = ""
                self.com_num_text = "значение должно быть натуральным числом"
        self.frozen_area.is_writing(300, 300)

    def change_password(self):
        screen.fill(self.settings_color)
        print_text("Новый пароль:", 50, 100)
        password_area = InputArea(300, 50, (0, 0, 0), False, 12)
        print_text(self.change_password_text, 650, 100)
        password_area.show_area(300, 100)
        password_area.is_writing(300, 100)
        if password_area.got_answer:
            if len(password_area.answer) >= 8:
                self.change_password_text = "Сохранено"
                common_file['password'] = password_area.answer
            else:
                password_area.answer = ""
                self.change_password_text = "Минимум 8 символов"

    def change_theme(self):
        global file1
        screen.fill(self.settings_color)
        Button('<--').show_button(0, 20, self.act_minus)
        Button('-->').show_button(1000, 20, self.act_plus)
        y = 100
        for i in range(self.first_list, min(self.first_list + 4, len(file1['themes']))):
            Button(file1['themes'][i]).show_button(400, y + (i % 4) * 100, self.choose_theme_action,
                                                   act_p=file1['themes'][i])

    def act_minus(self):
        if self.first_list > 0:
            self.first_list -= 4
            print('-')

    def act_plus(self, l):
        if self.first_list + 4 <= l:
            self.first_list += 4
            print('+')

    def add_set(self):
        global state
        state = "add_theme"
        self.add_theme_text = ""
        self.name_set = InputArea(width=300)

    def show_sets(self):
        global file1
        screen.fill(self.settings_color)
        Button('<--').show_button(0, 20, self.act_minus)
        Button('-->').show_button(1000, 20, self.act_plus, len(file1['themes']))
        #self.first_list = 0
        y = 100
        for i in range(self.first_list, min(self.first_list + 4, len(file1['themes']))):
            Button(file1['themes'][i]).show_button(400, y + (i % 4) * 100, self.show_theme_action, act_p=file1['themes'][i])
        Button("добавить").show_button(1000, 700, self.add_set)

    def add_theme(self):
        global file1
        global state
        screen.fill(self.settings_color)
        print_text("название набора:", 100, 100)
        print_text(self.add_theme_text, 100, 700)
        self.name_set.show_area(100, 400)
        self.name_set.is_writing(100, 400)
        if self.name_set.got_answer:
            if self.name_set.answer in file1['themes']:
                self.add_theme_text = "набор с таким названием уже есть"
            else:
                file1['themes'].append(self.name_set.answer)
                state = "sets"
                file1[self.name_set.answer] = {0: {}, 1: {}, 2: {}}

    def save_q(self):
        global file1
        global state
        global edit_this_theme
        global questions
        global answers
        theme = edit_this_theme
        cc = {
            'легкий': 0,
            'нормальный': 1,
            'сложный': 2
        }
        if self.compl_q.answer in cc:
            file1[edit_this_theme][cc[self.compl_q.answer]][self.name_q.answer] = self.name_a.answer
            game.que = file1[game.theme][game.complexity]
            game.state = "ask_new"
            state = "edit_theme"
            questions = list(file1[theme][0].keys())
            answers = []
            for i in questions:
                answers.append([0, file1[theme][0][i]])
            questions = list(file1[theme][1].keys())
            for i in questions:
                answers.append([1, file1[theme][1][i]])
            questions = list(file1[theme][2].keys())
            for i in questions:
                answers.append([2, file1[theme][2][i]])
            questions = list(file1[theme][0].keys()) + list(file1[theme][1].keys()) + list(file1[theme][2].keys())

    def add_q(self):
        global state
        state = "add_q"
        self.name_q = InputArea(width=500, max_s=30)
        self.name_a = InputArea(width=500, max_s=30)
        self.compl_q = InputArea(width=200, height=100, max_s=10)

    def add_question(self):
        global file1
        global state
        screen.fill(self.settings_color)
        print_text("вопрос:", 100, 100)
        print_text("ответ", 700, 100)
        self.name_q.show_area(100, 400)
        self.name_a.show_area(700, 400)
        self.compl_q.show_area(500, 600)
        print_text("сложность:", 100, 600)
        print_text("(легкий, нормальный или сложный)", 750, 600)
        Button("ок").show_button(1000, 700, self.save_q)
        self.name_q.is_writing(100, 400)
        self.name_a.is_writing(700, 400)
        self.compl_q.is_writing(500, 600)

    def edit_this_theme(self):
        global file1
        global questions
        global answers
        screen.fill(self.settings_color)
        Button('<--').show_button(0, 20, self.act_minus)
        Button('-->').show_button(1000, 20, self.act_plus, len(questions))
        Button("добавить").show_button(100, 700, self.add_q)
        #self.first_list = 0
        y = 100
        areas_a = []
        areas_q = []
        areas_c = []
        c = ['легкий', 'нормальный', 'сложный']
        cc = {
            'легкий': 0,
            'нормальный': 1,
            'сложный': 2
        }
        for i in range(self.first_list, min(self.first_list + 4, len(questions))):
            areas_q.append(InputArea(width=400, height=100, max_s=30, answer=str(questions[i])))
            areas_a.append(InputArea(width=400, height=100, max_s=30, answer=str(answers[i][1])))
            areas_c.append(InputArea(width=200, height=100, max_s=10, answer=c[answers[i][0]]))
            areas_q[i % 4].show_area(100, y + (i % 4) * 150)
            areas_a[i % 4].show_area(600, y + (i % 4) * 150)
            areas_c[i % 4].show_area(1100,y + (i % 4) * 150)
        Button("ок").show_button(1000, 700, self.edit_theme_save)
        for i in range(self.first_list, min(self.first_list + 4, len(questions))):
            areas_q[i % 4].is_writing(100, y + (i % 4) * 150)
            if areas_q[i % 4].got_answer:
                questions[i % 4] = areas_q[i % 4].answer
            areas_a[i % 4].is_writing(600, y + (i % 4) * 150)
            if areas_a[i % 4].got_answer:
                answers[i % 4][1] = areas_a[i % 4].answer
            areas_c[i % 4].is_writing(1100,y + (i % 4) * 150)
            if areas_c[i % 4].got_answer:
                if areas_c[i % 4].answer in cc:
                    answers[i % 4][0] = cc[areas_c[i % 4].answer]


    def choose_acc(self, acc):
        global game
        global state
        global theme
        global acc_chosen
        global current_acc
        game = GameObject(file[acc]['theme'], file[acc]['complexity'],
                  file[acc]['recent_time'], file[acc]['recent_lvl'],
                  file[acc]['desolation_time'], file[acc]['completion_num'])
        game.que = file1[game.theme][game.complexity]
        state = "pause"
        acc_chosen = True
        current_acc = acc
        print(acc, file[acc])
        print('acc_chosen')

    def add_acc(self):
        global state
        self.show_button = False
        self.name_acc_area = InputArea(width=300)
        state = "add_acc"

    def add_acc_2(self, name):
        global state
        global new_acc
        state = "add_acc2"
        file['accs'].append(name)
        file[name] = {}
        new_acc = name
        print(new_acc)
        self.first_list = 0
        print('ok')

    def add_acc_3(self, theme):
        global state
        global file
        file[new_acc]['theme'] = theme
        file[new_acc]['complexity'] = 0
        state = "add_acc3"

    def new_acc_yes(self):
        global state
        global file
        file[new_acc]['recent_lvl'] = 0.5
        file[new_acc]['desolation_time'] = 24
        file[new_acc]['completion_num'] = 10
        file[new_acc]['recent_time'] = datetime.datetime.today()
        if acc_chosen:
            state = "pause"
        else:
            state = "main"
        statics[new_acc] = {
            0: [0, 0],
            1: [0, 0],
            2: [0, 0]
        }

    def new_acc_no(self):
        global state
        self.des_time_area = InputArea(100, 50, (0, 0, 0), False, 5)
        self.com_num_area = InputArea(100, 50, (0, 0, 0), False, 5)
        self.compl_acc = InputArea(width=200, height=100, max_s=10)
        state = "add_acc4"

    def save_new_acc(self, x):
        global state
        global file
        global new_acc
        global statics
        file[new_acc]['recent_lvl'] = 0.5
        file[new_acc]['desolation_time'] = x[0]
        file[new_acc]['completion_num'] = x[1]
        file[new_acc]['recent_time'] = datetime.datetime.today()
        file[new_acc]['complexity'] = x[2]
        if acc_chosen:
            state = "pause"
        else:
            state = "main"
        statics[new_acc] = {
            0: [0, 0],
            1: [0, 0],
            2: [0, 0]
        }

    def new_acc_4(self):
        cc = {
            'легкий': 0,
            'нормальный': 1,
            'сложный': 2
        }
        screen.fill(self.settings_color)
        print_text("desolation_time:", 50, 100)
        print_text("ч", 400, 100)
        self.des_time_area.show_area(300, 100)
        print_text("completion_num:", 50, 200)
        self.com_num_area.show_area(300, 200)
        self.compl_acc.show_area(500, 600)
        print_text("сложность:", 100, 600)
        print_text("(легкий, нормальный или сложный)", 750, 600)
        self.com_num_area.is_writing(300, 200)
        self.des_time_area.is_writing(300, 100)
        self.compl_acc.is_writing(500, 600)

        try:
            x = float(self.des_time_area.answer)
            if x > 0:
                try:
                    y = int(self.com_num_area.answer)
                    if y > 0:
                        if self.compl_acc.answer in cc:
                            Button("сохранить").show_button(1000, 700, self.save_new_acc, [x, y, cc[self.compl_acc.answer]])
                except:
                    pass
        except:
            pass

    def new_acc_3(self):
        screen.fill(self.settings_color)
        print_text("установить настройки по умолчанию?", 100, 100)
        Button("да").show_button(100, 400, self.new_acc_yes)
        Button("нет").show_button(800, 400, self.new_acc_no)

    def new_acc_2(self):
        global file1
        screen.fill(self.settings_color)
        Button('<--').show_button(0, 20, self.act_minus)
        Button('-->').show_button(1000, 20, self.act_plus, len(file1['themes']))
        y = 100
        for i in range(self.first_list, min(self.first_list + 4, len(file1['themes']))):
            Button(file1['themes'][i]).show_button(400, y + (i % 4) * 100, self.add_acc_3,
                                                   act_p=file1['themes'][i])

    def new_acc(self):
        global file
        screen.fill(self.settings_color)
        self.name_acc_area.show_area(100, 200)
        print_text(self.new_acc_text, 100, 400)
        self.name_acc_area.is_writing(100, 200)
        if self.name_acc_area.got_answer:
            if self.name_acc_area.answer in file['accs']:
                self.new_acc_text = "профиль с таким названием уже есть"
            else:
                self.show_button = True
        if self.show_button:
            Button("далее").show_button(1000, 700, self.add_acc_2, act_p=self.name_acc_area.answer)

    def change_acc(self):
        global file
        screen.fill(self.settings_color)
        Button('<--').show_button(0, 20, self.act_minus)
        Button('-->').show_button(1000, 20, self.act_plus, len(file['accs']))
        Button("добавить").show_button(1000, 700, self.add_acc)
        y = 100
        for i in range(self.first_list, min(self.first_list + 4, len(file['accs']))):
            Button(file['accs'][i]).show_button(400, y + (i % 4) * 100, self.choose_acc, act_p=file['accs'][i])

    def main_screen(self):
        global file
        screen.fill(self.settings_color)
        print_text("выберите профиль", 100, 100)
        Button('<--').show_button(0, 20, self.act_minus)
        Button('-->').show_button(1000, 20, self.act_plus)
        Button("добавить").show_button(1000, 700, self.add_acc)
        y = 100
        for i in range(self.first_list, min(self.first_list + 4, len(file['accs']))):
            Button(file['accs'][i]).show_button(400, y + (i % 4) * 100, self.choose_acc, act_p=file['accs'][i])

    def change_compl(self):
        global file1
        screen.fill(self.settings_color)
        x = bool(file1[game.theme][0]) + bool(file1[game.theme][1]) + bool(file1[game.theme][1])
        if x == 1:
            print_text("для этой темы нет уровней сложности", 100, 100)
        else:
            if file1[game.theme][0]:
                Button("легкий").show_button(500, 100, self.choose_compl, '0')
            if file1[game.theme][1]:
                Button("нормальный").show_button(500, 300, self.choose_compl, '1')
            if file1[game.theme][2]:
                Button("сложный").show_button(500, 500, self.choose_compl, '2')

    def choose_compl(self, x):
        game.complexity = int(x)
        game.que = file1[game.theme][game.complexity]

    def stats(self):
        global current_acc
        global statics
        screen.fill(self.settings_color)
        print_text("Статистика профиля " + current_acc, 100, 50)

        print_text("Легкий:", 100, 200)
        print_text("правильных ответов", 300, 200)
        print_text("неправильных ответов", 750, 200)
        print_text(str(statics[current_acc][0][0]), 650, 200)
        print_text(str(statics[current_acc][0][1]), 1100, 200)

        print_text("Нормальный:", 100, 350)
        print_text("правильных ответов", 300, 350)
        print_text("неправильных ответов", 750, 350)
        print_text(str(statics[current_acc][1][0]), 650, 350)
        print_text(str(statics[current_acc][1][1]), 1100, 350)

        print_text("Сложный:", 100, 500)
        print_text("правильных ответов", 300, 500)
        print_text("неправильных ответов", 750, 500)
        print_text(str(statics[current_acc][2][0]), 650, 500)
        print_text(str(statics[current_acc][2][1]), 1100, 500)

        print_text(self.save_stats_text, 100, 730)
        self.save_stats.show_area(100, 650)
        Button("сохранить").show_button(700, 650, self.save_stats_action)
        self.save_stats.is_writing(100, 650)

    def save_stats_action(self):
        if len(self.save_stats.answer):
            if os.path.exists("{}.txt".format(self.save_stats.answer)):
                self.save_stats_text = "файл с таким названием уже существует"
            else:
                self.save_file()
                self.save_stats_text = "сохранено"
        else:
            self.save_stats_text = "введите название файла"

    def save_file(self):
        s_file = open("{}.txt".format(self.save_stats.answer), 'w')
        s_file.write("Стаистика профиля " + current_acc + '\n')
        s_file.write(
            "Легкий:    правильных ответов: {}, неправильных ответов: {}".format(str(statics[current_acc][0][0]), str(
                statics[current_acc][0][1])) + '\n')
        s_file.write(
            "Нормальный:    правильных ответов: {}, неправильных ответов: {}".format(str(statics[current_acc][1][0]), str(
                statics[current_acc][1][1])) + '\n')
        s_file.write(
            "Сложный:    правильных ответов: {}, неправильных ответов: {}".format(str(statics[current_acc][2][0]), str(
                statics[current_acc][2][1])) + '\n')
        s_file.close()



statics = shelve.open('statics', writeback=True)
st = {
    0: [0, 0],
    1: [0, 0],
    2: [0, 0]
}
statics['acc1'] = st

running = True
state = "main"
clock = pygame.time.Clock()
show = Screens()

common_file = shelve.open('password')
# common_file['password'] = '12345678'
password = common_file['password']
print(password)

file = shelve.open('profiles', writeback=True)

'''accs = ['acc1']
acc1 = {
    'theme': 'таблица умножения',
    'complexity': 0,
    'recent_time': datetime.datetime(2020, 10, 1, 2, 50, 0),
    'recent_lvl': 1,
    'desolation_time': 5,
    'completion_num': 10
}
file['accs'] = accs
file['acc1'] = acc1

print(file['acc1'])
print(file['accs'])'''

file1 = shelve.open('themes', writeback=True)

'''file1['themes'] = ['таблица умножения']
file1['таблица умножения'] = {
    0: {
        "1 * 1": 1,
        "1 * 2": 2,
        "1 * 3": 3,
        "2 * 1": 2,
        "2 * 2": 4,
        "2 * 3": 6,
        "2 * 4": 8,
        "3 * 1": 3,
        "3 * 2": 6,
        "3 * 3": 9,
        "4 * 1": 4,
        "5 * 1": 5,
        "6 * 1": 6,
        "7 * 1": 7,
        "8 * 1": 8,
        "9 * 1": 9
    },
    1: {
        "2 * 5": 10,
        "2 * 6": 12,
        "2 * 7": 14,
        "2 * 8": 16,
        "2 * 9": 18,
        "3 * 4": 12,
        "3 * 5": 15,
        "3 * 6": 18,
        "3 * 7": 21,
        "3 * 8": 24,
        "3 * 9": 27,
        "4 * 4": 16,
        "4 * 5": 20,
        "4 * 6": 24,
        "5 * 4": 20,
        "5 * 5": 25,
        "5 * 6": 30,
        "6 * 4": 24,
        "6 * 5": 30,
        "6 * 6": 36
    },
    2: {
        "4 * 7": 28,
        "4 * 8": 32,
        "4 * 9": 36,
        "5 * 7": 35,
        "5 * 8": 40,
        "5 * 9": 45,
        "6 * 7": 42,
        "6 * 8": 48,
        "6 * 9": 54,
        "7 * 7": 49,
        "7 * 8": 56,
        "7 * 9": 63,
        "8 * 7": 56,
        "8 * 8": 64,
        "8 * 9": 72,
        "9 * 7": 63,
        "9 * 8": 72,
        "9 * 9": 81
    }
}'''

acc_chosen = False

pygame.time.set_timer(pygame.USEREVENT, 1000)
show.first_list = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == "menu" or state == "change_acc":
                    state = "pause"
                elif state == "play":
                    state = "pause"
                elif state == "pause":
                    state = "play"
                elif state == "settings_p" or state == "settings" or state == "sets" or state == "change_theme" or state == "stats":
                    state = "menu"
                elif state == "time" or state == "change_password" or state == "change_complexity":
                    state = "settings"
                elif state == "add_theme" or state == "edit_theme":
                    state = "sets"
                elif state == "add_q":
                    state = "edit_theme"
        if event.type == pygame.USEREVENT:
            pygame.time.set_timer(pygame.USEREVENT, 1000)
            if acc_chosen:
                game.update()

    if state == "main":
        show.main_screen()
    elif state == "pause":
        show.pause()
    elif state == "menu":
        show.menu()
    elif state == "play":
        show.play()
    elif state == "settings_p":
        show.settings_p()
    elif state == "settings":
        show.settings()
    elif state == "time":
        show.time()
    elif state == "change_password":
        show.change_password()
    elif state == "death":
        show.death()
    elif state == "change_theme":
        show.change_theme()
    elif state == "sets":
        show.show_sets()
    elif state == "edit_theme":
        show.edit_this_theme()
    elif state == "add_theme":
        show.add_theme()
    elif state == "add_q":
        show.add_question()
    elif state == "change_acc":
        show.change_acc()
    elif state == "add_acc":
        show.new_acc()
    elif state == "add_acc2":
        show.new_acc_2()
    elif state == "add_acc3":
        show.new_acc_3()
    elif state == "add_acc4":
        show.new_acc_4()
    elif state == "change_complexity":
        show.change_compl()
    elif state == "stats":
        show.stats()

    pygame.display.flip()
    clock.tick(60)

if acc_chosen:
    game.safe()
file.close()
file1.close()
statics.close()
common_file.close()
pygame.quit()