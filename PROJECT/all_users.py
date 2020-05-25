import datetime

user1 = {
    'appearance': 'dog',
    'theme': 'theme1', 
    'complexity': False, 
    'recent_using_time': datetime.datetime(2020,3,20,14), 
    'recent_using_level': 1, 
    'desolation_time': 48, 
    'completion_num': 7
}

user2 = {
    'appearance': 'cat',
    'theme': 'theme2', 
    'complexity': False, 
    'recent_using_time': datetime.datetime(2020,3,20,2), 
    'recent_using_level': 0.7, 
    'desolation_time': 48, 
    'completion_num': 7
}

users_dict = {
    'user1': user1,
    'user2': user2
}
