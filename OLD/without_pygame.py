import all_users as u
import datetime
import theme as th
import random

class Game_Object:
    def __init__(self, appearance, theme, complexity, recent_using_time, recent_using_level, desolation_time, completion_num):
        self.appearance = appearance # Выбранный персонаж
        self.theme = theme # Текущая тема
        self.complexity = complexity # Сложность
        delta_time = datetime.datetime.today() - recent_using_time # Время, прошедшее с последнего использования
        delta_time = delta_time.total_seconds()
        delta_time = delta_time / 3600
        level_down = delta_time / desolation_time # Доля шкалы, на которую произошло понижение
        if level_down >= recent_using_level: # Проверка на жизнь
            self.dead = True
            self.level = 0
        else:
            self.dead = False
            self.level = recent_using_level - level_down
        self.speed = 1 / completion_num # Скорость заполнения шкалы, completion_num - целое число, задаваемое в настройках
        
    def start_game(self):
        theme = th.themes[self.theme]
        running_game = True
        while running_game: # ДОБАВИТЬ УЧЁТ СЛОЖНОСТИ
            q = random.choice(list(theme.keys())) # Выбор рандомного вопроса 
            ans = theme[q]
            print(q)
            us_ans = input()
            if us_ans == ans:
                print('Верно!')
                self.level += self.speed # Повышение шкалы
                if self.level >= 1:
                    self.level = 1
            elif us_ans == 'esc':
                running_game = False
            else:
                print('Неверно!')


print("Выберите пользователя:")
for i in u.users_dict:
    print('- {}'.format(i))
    
user_name = input()
us_dt = u.users_dict[user_name]
user = Game_Object(us_dt['appearance'], us_dt['theme'], us_dt['complexity'], us_dt['recent_using_time'], us_dt['recent_using_level'], us_dt['desolation_time'], us_dt['completion_num'])

print('К игре')

if input() == 'К игре':
    user.start_game()
