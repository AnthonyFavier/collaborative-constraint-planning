ascii = {
    'simple':{
        'top_left_corner': '┌',
        'top_right_corner': '┐',
        'bot_left_corner': '└',
        'bot_right_corner': '┘',
        'top_bot_middle': '┬',
        'bot_top_middle': '┴',
        'right_left_middle': '├',
        'left_right_middle': '┤',
        'horizontal': '─',
        'vertical': '│',
        'cross': '┼',
        },
    'double':{
        'top_left_corner': '╔',
        'top_right_corner': '╗',
        'bot_left_corner': '╚',
        'bot_right_corner': '╝',
        'top_bot_middle': '╦',
        'bot_top_middle': '╩',
        'right_left_middle': '╠',
        'left_right_middle': '╣',
        'horizontal': '═',
        'vertical': '║',
        'cross': '╬',
        },
}

def boxprint(text, mode='s'):
    if mode=='s':
        mode = 'simple'
    if mode=='d':
        mode = 'double'
        
    length = len(text)
    
    top = ascii[mode]['top_left_corner'] + ascii[mode]['horizontal']*(length+2) + ascii[mode]['top_right_corner']
    middle = ascii[mode]['vertical'] + ' ' + text + ' ' + ascii[mode]['vertical']
    bottom = ascii[mode]['bot_left_corner'] + ascii[mode]['horizontal']*(length+2) + ascii[mode]['bot_right_corner']
    
    print('\n'.join([top, middle, bottom]))

