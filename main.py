from bs4 import BeautifulSoup as Bs
import requests
import lxml
import json

home_page = Bs(requests.get('https://zno.osvita.ua/physics/tema.html').text, 'lxml')

def get_links(home_page):
    # finding all test themes and links for them
    question_list = []
    for theme in home_page.find_all(class_='tag-item main'):
        # find all main themes to divide them
        theme_name = theme.find(class_='item-name').get_text()[3:-6]
        
        for title in theme.find_all('a'):
            # find links for all tests 
            title_name = title.find(class_='item-name').get_text().strip()
            question_list.append({
                'theme': f'{theme_name} => {title_name[:title.find(class_='item-name').get_text().strip().index('(')]}',
                'href': f'https://zno.osvita.ua{title.get('href')}',
                'questions': []
            })


    return question_list
            
def get_questions(question_list):
    for item in question_list:
        page = Bs(requests.get(item['href']).text, 'lxml')
        for q in page.find_all(class_='task-card'):
            if q.find(string='Впишіть відповідь:') != None:
                try:
                    # if task is showen as image
                    question_list[question_list.index(item)]['questions'].append({
                        'num': q.find('form').get('id').replace('q_form_', ''),
                        'q': f'https://zno.osvita.ua{q.find('img').get('src')}',
                        'is_comp': False, 
                        'ans': ''
                    })
                except:
                    # if task is writed in text
                    question_list[question_list.index(item)]['questions'].append({
                        'num': q.find('form').get('id').replace('q_form_', ''),
                        'q': q.find('p').get_text().strip(),
                        'is_comp': False,
                        'ans': ''
                    })
    
    return question_list


def run():
    print('Collecting pages...')
    question_list = get_links(home_page)
    print('Complite! \nSearching for questions...\n')
    question_list = get_questions(question_list)
    print('Complite! \nSaving resoults...\n')

    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(question_list, f, indent=4, ensure_ascii=False)

    print('\nAll done!')



if __name__ == '__main__':
    run()