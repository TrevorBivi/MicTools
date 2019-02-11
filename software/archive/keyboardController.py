from programHandler import *

controller = keyboard.Controller()

def on_press(key):
    print('pressed:',key)
    if  str(key) == 'Key.left':
        print('switching to tts input')
        input_tts_act()
    elif  str(key) == 'Key.f20':
        print('switching to audio search imput')
        search_foob_act()
    
    elif str(key) == 'Key.enter':
        if in_search_menu:
            print('done audio search')
            finish_search_foob_act()
        elif in_tts:
            print('done tts input')
            finish_tts_act()

if __name__ == '__main__':
    runPrograms()
    with keyboard.Listener(on_press=on_press) as listener:
        pass
        listener.join()
    
