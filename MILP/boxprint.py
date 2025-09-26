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

def boxprint(text: str, mode='s', tab_spaces=4, show=True):
    # Set mode
    if mode=='s':
        mode = 'simple'
    if mode=='d':
        mode = 'double'
    
    # Pre-changes
    text = text.replace('\t', ' '*tab_spaces)
    
    # Splitting 
    lines = text.splitlines()
    
    # Find max length/wide
    length = -1
    for l in lines:
        if len(l)>length:
            length = len(l)

    # Top 
    top = ascii[mode]['top_left_corner'] + ascii[mode]['horizontal']*(length+2) + ascii[mode]['top_right_corner']
    
    # Middle text
    middles = []
    for l in lines:
        filling_spaces = ' '*( length-len(l) )
        middles.append( ascii[mode]['vertical'] + ' ' + l + filling_spaces + ' ' + ascii[mode]['vertical'] )
    
    # Bottom
    bottom = ascii[mode]['bot_left_corner'] + ascii[mode]['horizontal']*(length+2) + ascii[mode]['bot_right_corner']
    
    # Output text
    output_text = '\n'.join([top, *middles, bottom])
    
    # Print
    if show:
        print(output_text)
    
    return output_text


if __name__=='__main__':
    print('test simple:')
    boxprint("Hello")
    
    print('test double:')
    boxprint("Hello", mode='d')
    
    print('test multi-line:')
    boxprint("Hello\nHow are you?\nVery good thanks .....       e")
    