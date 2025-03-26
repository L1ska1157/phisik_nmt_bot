from random import randint
import json


class User():
    def __init__(self, user_id, themes=[]):
        self.user_id = user_id # => same to message.chat.id
        self.is_add = False # => to check does user adding new themes or not
        self.current_q = False # => current question. would be using to check if user is answering question and wich one should be checked
        self.themes = themes # => numbers of themes wich user have learned. tasks would be filtered by this list to not to give user questions answer for which user couldn't know
        
    # => reading questions from global file and saving them in individual one for new user
        with open(f'questions.json', 'r+', encoding='utf-8') as q: 
            try:
                with open(f'users_data/data_{self.user_id}.json', 'x', encoding='utf-8') as file:
                    json.dump({'themes': [],
                                'questions': json.load(q)
                                }, file, indent=4, ensure_ascii=False)
            except:
                pass



    def get_task(self, redo):
    
    # => loading questions
        with open(f'users_data/data_{self.user_id}.json', 'r', encoding='utf-8') as file: 
            info = json.loads(file.read())


        q_list = []
    # => filtering by themes list
        if info['themes'] != []: 
            for item in info['questions']:
                if item['theme'][0] in info['themes']:
                    for i in item['questions']:
                        if not redo:
                            if not i['is_comp']:
                                q_list.append(i)
                        else:
                            q_list.append(i)


    # => in case it's new user and he/she doesn't have any themes saved yet
        else:
            return 'У вас не збережена жодна тема. Додати нові? /add_theme'                   
        
    # => in case user have already  done all tasks 
        if q_list == []:
            return 'Вітаю, ви виконали всі завдання'
        

        question = q_list[randint(0, len(q_list)-1)]
        self.current_q = question
        

        for item in info['questions']:
            if question in item['questions']:
                title = f"{item['theme']} => {question['num']}"  

                print(question['ans'])
                
            # => cheking is task is in text or in image format for better showing
                if question['q'][:3]=='htt': 
                    return False, title, question['q']
                else: 
                    return True, title, question['q']
        


# => adding new themes wich user know        
    def add_theme(self, t_list): 
        with open(f'users_data/users.json', 'r', encoding='utf-8') as file:
            info = json.loads(file.read())

    # => some checks to not to save values which would cause an error
        for item in t_list:
            try: 
                if item not in info['themes'] and int(item)<=5:
                    info['themes'] += item
            except:                
                pass
            
                
    # => saving updated information in user's individual file        
        with open(f'users_data/users.json', 'w', encoding='utf-8') as file: 
            json.dump(info, file, indent=4, ensure_ascii=False)

        self.is_add = False



# => checking users's answears
    def check_ans(self, ans): 

    # => if answer is correct
        if ans == self.current_q['ans']: 

        # => saving question completed status
            with open(f'users_data/data_{self.user_id}.json', 'r', encoding='utf-8') as f:
                info = json.loads(f.read())
                for theme in info['questions']:
                    if self.current_q in theme['questions']:
                       info['questions'][info['questions'].index(theme)]['questions'][theme['questions'].index(self.current_q)]['is_comp'] = True

            with open(f'users_data/data_{self.user_id}.json', 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=4, ensure_ascii=False)

            self.current_q = False
            
            

    # => returning answer for user
            mes = '✅'
        else:
            mes = '❌'

        return mes



# => showing global progress for all themes an for each one divided 
    def show_progress(self):
        progress = {'t_1': { # => dictionary for more useble calculating
            'all': 0,
            'comp': 0
        },
        't_2': {
            'all': 0,
            'comp': 0
        },
        't_3': {
            'all': 0,
            'comp': 0
        },
        't_4': {
            'all': 0,
            'comp': 0
        },
        't_5': {
            'all': 0,
            'comp': 0
        },
        }

    # => loading question lest
        with open(f'users_data/data_{self.user_id}.json', 'r', encoding='utf-8') as f:
                info = json.loads(f.read())


    # => collecting data about number of compleated tasks and all
        for theme in info['questions']:
            for q in theme['questions']:
                if q['is_comp']:
                    progress[f't_{theme['theme'][0]}']['comp'] += 1
            progress[f't_{theme['theme'][0]}']['all'] += len(theme['questions'])


    # => returning prepaired and formated text
        try:
            return f'Загалом:\n  => {round((sum(theme["comp"] for theme in progress.values()) / sum(theme["all"] for theme in progress.values()))*100, 2)}%\n' \
                f'1. Механіка:\n  => {round((progress['t_1']['comp'] / progress['t_1']['all'])*100, 2)}%\n' \
                f'2. Молекулярна фізика і термодинаміка:\n  => {round((progress['t_2']['comp'] / progress['t_2']['all'])*100, 2)}%\n' \
                f'3. Електродинаміка:\n  => {round((progress['t_3']['comp'] / progress['t_3']['all'])*100, 2)}%\n' \
                f'4. Коливання та хвилі. Оптика:\n  => {round((progress['t_4']['comp'] / progress['t_4']['all'])*100, 2)}%\n' \
                f'5. Квантова фізика. Елементи теорії відносності:\n  => {round((progress['t_5']['comp'] / progress['t_5']['all'])*100, 2)}%\n'
        except Exception as ex:
            print(str(ex))
            return 'Сталася помилка. Можливо, данні про ваші тести було пошкоджено'



# => returning back to main menu
    def back(self):

    # => canceling all operations
        self.current_q = False
        self.is_add = False



# => deleting all user progress (recreating user's file)
    def delete_progress(self): 
        with open('questions.json', 'r', encoding='utf-8') as q:
            with open(f'users_data/data_{self.user_id}.json', 'r', encoding='utf-8') as file:
                themes = json.loads(file.read())['themes']
            with open(f'users_data/data_{self.user_id}.json', 'w', encoding='utf-8') as file:
                json.dump({'themes': themes,
                            'questions': json.load(q)
                            }, file, indent=4, ensure_ascii=False)



# => Additional function to refactor oblect for saving in json    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'themes': self.themes
        }
