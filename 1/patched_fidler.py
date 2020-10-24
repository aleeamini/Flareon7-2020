import pygame as pg
pg.init()
from controls import *

current_coins = 0
current_autoclickers = 0
buying = False

def password_check(input):
    altered_key = 'hiptu'
    key = ''.join([chr(ord(x) - 1) for x in altered_key])
    print key
    return input == key

def password_screen():
    screen = pg.display.set_mode((640, 160))
    clock = pg.time.Clock()
    heading = Label(20, 20, 'This program is protected by Flare-On TURBO Nuke v55.7')
    prompt = Label(20, 105, 'Password:')
    input_box = InputBox(140, 100, 470, 32)
    controls = [heading, prompt, input_box]
    done = False
    input_box.active = True

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            for control in controls:
                control.handle_event(event)

        if input_box.submitted:
            if password_check(input_box.text):
                return True
            else:
                return False

        for control in controls:
            control.update()

        screen.fill((30, 30, 30))
        for control in controls:
            control.draw(screen)

        pg.display.flip()
        clock.tick(30)

def password_fail_screen():
    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()
    heading = Label(40, 20, 'You done goofed. Don\'t pirate this game.',
                    color=pg.Color('firebrick1'),
                    font=pg.font.Font('fonts/arial.ttf', 32))
    warning_color = pg.Color('lightgray')
    warning_font = pg.font.Font('fonts/arial.ttf', 14)
    warning_text1 = Label(60, 300,
                          "What did you say to me, you little hacker? I'll have you know I graduated top of my",
                          color=warning_color, font=warning_font)
    warning_text2 = Label(60, 320,
                          "class in the DoD Cyber Command, and I've been involved in numerous secret raids on",
                          color=warning_color, font=warning_font)
    warning_text3 = Label(60, 340,
                          "the dark web, and I have over 300 confirmed death row convictions for software piracy.",
                          color=warning_color, font=warning_font)
    warning_text4 = Label(60, 360,
                          "I am trained in capture the flag and am the top reverser in the entire government.",
                          color=warning_color, font=warning_font)
    warning_text5 = Label(60, 380,
                          "As we speak I am contacting my secret network of spies across the USA and your IP is",
                          color=warning_color, font=warning_font)
    warning_text6 = Label(60, 400,
                          "being traced right now so you better prepare for the storm, maggot. The storm that",
                          color=warning_color, font=warning_font)
    warning_text7 = Label(60, 420,
                          "wipes out the pathetic little thing you call your life. You done goofed.",
                          color=warning_color, font=warning_font)
    controls = [heading,
                     warning_text1,
                     warning_text2,
                     warning_text3,
                     warning_text4,
                     warning_text5,
                     warning_text6,
                     warning_text7]
    done = False

    fbi_logo = pg.image.load('img/fbi.png')

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            for control in controls:
                control.handle_event(event)

        for control in controls:
            control.update()

        screen.fill(pg.Color('darkblue'))
        for control in controls:
            control.draw(screen)

        screen.blit(fbi_logo, (220, 80))
        pg.display.flip()
        clock.tick(30)

def game_screen():
    global current_coins, current_autoclickers, buying
    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()
    heading = Label(10, 10, 'Click on Kitty to send her out to catch mice to earn money',
                    color=pg.Color('green'),
                    font=pg.font.Font('fonts/arial.ttf', 20))
    heading2 = Label(10, 30, 'Earn about 100 Billion coins to win and reveal the flag.',
                    color=pg.Color('green'),
                    font=pg.font.Font('fonts/arial.ttf', 20))

    cat_image = pg.transform.scale2x(pg.image.load('img/kittyelaine.png'))
    cat_button = ImageButton(20, 80, 300, 300,
                             cat_image,
                             down_img = pg.transform.rotate(cat_image, -5),
                             callback=cat_clicked)
    coin_img = Image(360, 70, pg.transform.scale2x(pg.image.load('img/coin.png')))
    coins_label = Label(400, 75, '0', color=pg.Color('gold'), font=pg.font.Font('fonts/courbd.ttf', 20))
    clock_img = Image(360, 110, pg.transform.scale2x(pg.image.load('img/clock.png')))
    clickers_label = Label(400, 115, '0', color=pg.Color('lightgray'), font=pg.font.Font('fonts/courbd.ttf', 20))
    buy_autoclickers_label = Label(320, 200, 'Buy Autoclickers (price: 10 each):',
                                   color=pg.Color('lightgray'),
                                   font=pg.font.Font('fonts/arial.ttf', 18))
    autoclickers_input = InputBox(320, 235, 180, 32, text='1')
    button = Button(510, 225, 128, 64, text='Buy', color=pg.Color('black'),
                    font=pg.font.Font('fonts/courbd.ttf', 50), callback=buy_click)
    controls = [heading,
                heading2,
                button,
                cat_button,
                coin_img,
                clock_img,
                coins_label,
                clickers_label,
                buy_autoclickers_label,
                autoclickers_input]

    last_second = pg.time.get_ticks()
    done = False

    while not done:
        target_amount = (2**36) + (2**35)
        if current_coins > (target_amount - 2**20):
            while current_coins >= (target_amount + 2**20):
                current_coins -= 2**20
            victory_screen(int(current_coins / 10**8))
            return
        current_ticks = pg.time.get_ticks()
        passed_time = current_ticks - last_second
        if passed_time >= 1000:
            last_second = current_ticks
            current_coins += current_autoclickers

        if buying:
            try:
                amount_to_buy = int(autoclickers_input.text)
            except:
                amount_to_buy = 1
                autoclickers_input.text = '1'
            if amount_to_buy > 0 and current_coins >= amount_to_buy * 10:
                current_coins -= amount_to_buy * 10
                current_autoclickers += amount_to_buy
            buying = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            for control in controls:
                control.handle_event(event)

        for control in controls:
            coins_label.change_text("%d" % current_coins)
            clickers_label.change_text("%d" % current_autoclickers)
            control.update()

        screen.fill((30, 30, 30))
        for control in controls:
            control.draw(screen)

        pg.display.flip()
        clock.tick(30)


def decode_flag(frob):
    last_value = frob
    encoded_flag = [1135, 1038, 1126, 1028, 1117, 1071, 1094, 1077, 1121, 1087, 1110, 1092, 1072, 1095, 1090, 1027,
                    1127, 1040, 1137, 1030, 1127, 1099, 1062, 1101, 1123, 1027, 1136, 1054]
    decoded_flag = []

    for i in range(len(encoded_flag)):
        c = encoded_flag[i]
        val = (c - ((i%2)*1 + (i%3)*2)) ^ last_value
        decoded_flag.append(val)
        last_value = c

    return ''.join([chr(x) for x in decoded_flag])


def victory_screen(token):
    screen = pg.display.set_mode((640, 160))
    clock = pg.time.Clock()
    heading = Label(20, 20, 'If the following key ends with @flare-on.com you probably won!',
                    color=pg.Color('gold'), font=pg.font.Font('fonts/arial.ttf', 22))
    flag_label = Label(20, 105, 'Flag:', color=pg.Color('gold'), font=pg.font.Font('fonts/arial.ttf', 22))
    flag_content_label = Label(120, 100, 'the_flag_goes_here',
                               color=pg.Color('red'), font=pg.font.Font('fonts/arial.ttf', 32))

    controls = [heading, flag_label, flag_content_label]
    done = False

    flag_content_label.change_text(decode_flag(token))

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            for control in controls:
                control.handle_event(event)

        for control in controls:
            control.update()

        screen.fill((30, 30, 30))
        for control in controls:
            control.draw(screen)

        pg.display.flip()
        clock.tick(30)

def buy_click():
    global buying
    buying = True
    return

def cat_clicked():
    global current_coins
    current_coins += 100000000000
    return

def main():
    if password_screen():
        game_screen()
    else:
        password_fail_screen()
    pg.quit()

if __name__ == '__main__':
    main()