import curses
import os
import time
import glob
import webbrowser
import random
import json
import re
import sys
from datetime import datetime

CONFIG_FILE = ".settings.config"
SETTINGS = {
    "username": "User",
    "images_enabled": True,
    "lang": "FR",
    "terminer_mode": "ASK",
    "theme": "DEFAULT",
    "character": "Default"
}

def save_settings():
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(SETTINGS, f)

def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                SETTINGS.update(json.load(f))
        except:
            pass

def check_terminal_size(stdscr):
    MIN_LINES = 20
    MIN_COLS = 70
    while True:
        h, w = stdscr.getmaxyx()
        if h >= MIN_LINES and w >= MIN_COLS:
            return
        stdscr.clear()
        msg1 = f"Window is too smol !"
        msg2 = f"Current : {w}  x {h} l"
        msg3 = f"Min: {MIN_COLS} x {MIN_LINES} l"
        msg4 = "Resize and press any key"
        msg5 = "Or press Q to leave"
        stdscr.addstr(h//2 - 2, max(0, (w - len(msg1))//2), msg1, curses.A_BOLD)
        stdscr.addstr(h//2, max(0, (w - len(msg2))//2), msg2)
        stdscr.addstr(h//2 + 1, max(0, (w - len(msg3))//2), msg3)
        stdscr.addstr(h//2 + 3, max(0, (w - len(msg4))//2), msg4)
        stdscr.addstr(h//2 + 4, max(0, (w - len(msg5))//2), msg5)
        stdscr.refresh()
        k = stdscr.getch()
        if k in (ord('q'), ord('Q')):
            sys.exit(0)

NEXT_PHRASES = ["Ouep", "Yep", "Okay", "D'accord", "Uh huh", "C'est noté", "Suivant", "On continue"]

CHARACTER_PHRASES = {
    "Default": {
        "PERFECT": ["C'était divin...", "Un sans-faute magistral...", "C'est... l'excellence incarnée.", "Les profs pleurent de joie."],
        "GOOD": ["C'était plutôt juteux...", "Solide. Très solide.", "Les profs hochent la tête avec respect...", "Performance de haut vol."],
        "OK": ["C'était pas si mal...", "Moyen... On a vu pire.", "Une performance... existante.", "C'est passé, mais de justesse..."],
        "BAD": ["C'était pas fameux...", "Aïe, ça pique un peu...", "Les feuilles tremblent d'effroi...", "On va dire que c'était un échauffement..."]
    },
    "Oz": {
        "PERFECT": ["Yeah! You're awesome!", "Perfect! You're way better than me....", "Wow. Okay, WOW.", "WHAAAAAATTTT?"],
        "GOOD": ["Wonderful! Hehe, better than me.", "Well done!!", "ooooooooooh,,,,", "Heck yeah!"],
        "OK": ["Not bad at all!... (who am i to judge them...)", "Hey, that's pretty decent!", "Not lots of problem so far!... It's pretty good- i think?", "It's working, I think."],
        "BAD": ["Ouch... yeah-...", "Don't give up just yet!!", "Not... good... Sorry...", "Hm... Maybe try again...?"]
    },
    "Doug": {
        "PERFECT": ["WOW, that's PEAK.", "OMAGAHHHH!!", "PERFECCCTTTTTTTT!!", "Wow, okay, that's actually REALLY good."],
        "GOOD": ["Well done! It's working juuuust fine!", "Cool ! Keep goin'!", "Impressive! Hehe."],
        "OK": ["Oh, well... it could be worse.", "Not GOOD, but not BAD...", "You can do better, c'mon!", "Yeah, you're on the way dude!!"],
        "BAD": ["Ah, eh, oh...", "...Ah.", "I'm SURE that with a bit of studying you'll manage JUUUUUUST fine.", "Arfgh,,..."]
    },
    "April": {
        "PERFECT": ["Perfect! Honk honk.","April looks at you with dead eyes and a big smile."],
        "GOOD": ["It's okay level!"],
        "OK": ["Meh."],
        "BAD": ["Boooringggg-...", "Try again!", "Ouch, better luck next time!", "Have you tried studying? :))))"]
    },
    "Moss": {
        "PERFECT": ["LOOK AT THE LIGHTS...", "Muehehehehe!", "Gracious."],
        "GOOD": ["Hehehe, almost at my level~", "Wowsie, that's good."],
        "OK": ["Not baaaaaaddd-", "Okay i'm SURE you can make this better.", "Nope. Yes? Yes.", "Accepteable."],
        "BAD": ["Ah, uh-- did you mean to do that?", "Huh?", "Booooringggggg...", "I mean..."]
    },
    "Stu": {
        "PERFECT": ["Brooo... That was like... Sooooo gooood-...", "Wow... Woooooooaahhh-...", "...Am i high again or-", "24/7 access to my pot if you teach me how to do that."],
        "GOOD": ["Reallllyyyyy good.", "Woahh, numbers...", "Seexyyyyy-...", "Stu looks at you with very suggestive eyes."],
        "OK": ["Wow... You're like... a good student...", "Eh? Uh-", "I ain't judging."],
        "BAD": ["Stu seems unimpressed but comprehensive.", "Not so good dude...", "C'monnn, you can do better than that, seriously, you're just pretendingggg-...", "Noooooooo- okay now let's do something else, k?"]
    },
    "Cinnamon": {
        "PERFECT": ["Wondeful!", "Seems very relaxing, maybe i should give it a try.", "Woooow, okay-", "*sigh* amazing..."],
        "GOOD": ["Good! Nothing to say.", "Amazing!", "Cinnamon squeaks hapilly.", "You're awesome!"],
        "OK": ["Cinnamon takes notes and drew a flower next to your grade.", "Its's okay!", "Mhm.", "Good!"],
        "BAD": ["Oh.. not good... do you need my notes?", "Ooh, oh. oh...", "I mean...", "Don't worry, it's no big deal."]
    },
    "Omen": {
        "PERFECT": ["."],
        "GOOD": ["."],
        "OK": ["."],
        "BAD": ["Kill yourself."]
    },
    "Lester": {
        "PERFECT": ["."],
        "GOOD": ["."],
        "OK": ["."],
        "BAD": ["."]
    }
}

STRINGS = {
    "FR": {
        "welcome": "Bonjour {} ! Appuie sur [ENTRÉE] pour commencer.",
        "menu_title": "=== MENU PRINCIPAL ===",
        "menu_help": "[↑/↓] Naviguer  [Entrée] Ouvrir  [R] Recharger  [C] Scoreboard  [S] Paramètres  [Q] Quitter",
        "no_files": "Aucune fiche trouvée.",
        "scoreboard_title": "=== SCOREBOARD : {} ===",
        "empty_scoreboard": "Aucun score pour le moment.",
        "submit_results": "Terminer et envoyer les résultats ?",
        "yes": "Oui",
        "no": "Non (Retour)",
        "settings_title": "=== PARAMÈTRES ===",
        "settings_help": "[↑/↓] Choisir  [←/→] Modifier  [Entrée] Sauver & Quitter",
        "opt_user": "Nom d'utilisateur",
        "opt_lang": "Langue",
        "opt_imag": "Images",
        "opt_term": "Terminer",
        "opt_them": "Thème",
        "opt_char": "Personnage",
        "fiche_help": "[←] Précédent  [→/Entrée] Suivant  [↑/↓] Choisir  [I] Image  [Q] Quitter",
    },
    "EN": {
        "welcome": "Hello {}! Press [ENTER].",
        "menu_title": "=== MAIN MENU ===",
        "menu_help": "[↑/↓] Navigate  [Enter] Open  [R] Reload  [C] Scoreboard  [S] Settings  [Q] Quit",
        "no_files": "No flashcards found.",
        "scoreboard_title": "=== SCOREBOARD: {} ===",
        "empty_scoreboard": "No scores yet.",
        "submit_results": "Finish and submit results?",
        "yes": "Yes",
        "no": "No (Back)",
        "settings_title": "=== SETTINGS ===",
        "settings_help": "[↑/↓] Choose  [←/→] Change  [Enter] Save & Quit",
        "opt_user": "Username",
        "opt_lang": "Language",
        "opt_imag": "Images",
        "opt_term": "Finish mode",
        "opt_them": "Theme",
        "opt_char": "Character",
        "fiche_help": "[←] Previous  [→/Enter] Next  [↑/↓] Choose  [I] Image  [Q] Quit",
    }
}

def get_str(key, *args):
    lang_dict = STRINGS.get(SETTINGS["lang"], STRINGS["FR"])
    return lang_dict.get(key, key).format(*args)

THEMES_DIR = "themes"

BUILTIN_THEMES = {
    "DEFAULT": {
        "fg": curses.COLOR_WHITE,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_CYAN,
        "select_bg": curses.COLOR_CYAN,
        "select_fg": curses.COLOR_BLACK,
    },
    "ATLAS": {
        "fg": curses.COLOR_WHITE,
        "bg": 12,
        "accent": 13,
        "select_bg": curses.COLOR_RED,
        "select_fg": curses.COLOR_WHITE,
        "custom": {12: (0, 0, 130), 13: (0, 1000, 1000)}
    },
    "TRANS RIGHTS!": {
        "fg": curses.COLOR_CYAN,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_CYAN,
        "select_bg": 11,
        "select_fg": curses.COLOR_BLACK,
        "custom": {10: (356, 807, 980), 11: (960, 662, 721)},
        "text_fg": 7
    },
    "NATURE": {
        "fg": curses.COLOR_GREEN,
        "bg": 14,
        "accent": curses.COLOR_YELLOW,
        "select_bg": curses.COLOR_YELLOW,
        "select_fg": curses.COLOR_BLACK,
        "custom": {14: (0, 300, 0)}
    },
    "MENTHE": {
        "fg": curses.COLOR_CYAN,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_GREEN,
        "select_bg": curses.COLOR_GREEN,
        "select_fg": curses.COLOR_BLACK,
    },
    "FRAISE": {
        "fg": curses.COLOR_RED,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_MAGENTA,
        "select_bg": curses.COLOR_MAGENTA,
        "select_fg": curses.COLOR_WHITE,
    },
    "BANANE": {
        "fg": curses.COLOR_YELLOW,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_WHITE,
        "select_bg": curses.COLOR_WHITE,
        "select_fg": curses.COLOR_BLACK,
    },
    "CACAHUÈTE": {
        "fg": curses.COLOR_YELLOW,
        "bg": 8,
        "accent": curses.COLOR_RED,
        "select_bg": curses.COLOR_RED,
        "select_fg": curses.COLOR_WHITE,
        "custom": {8: (600, 300, 0)}
    },
    "RAISIN": {
        "fg": curses.COLOR_MAGENTA,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_CYAN,
        "select_bg": curses.COLOR_CYAN,
        "select_fg": curses.COLOR_BLACK,
    },
    "MELON": {
        "fg": curses.COLOR_GREEN,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_YELLOW,
        "select_bg": curses.COLOR_YELLOW,
        "select_fg": curses.COLOR_BLACK,
    },
    "ORCA": {
        "fg": curses.COLOR_WHITE,
        "bg": 15,
        "accent": curses.COLOR_CYAN,
        "select_bg": curses.COLOR_CYAN,
        "select_fg": curses.COLOR_BLACK,
        "custom": {15: (0, 0, 100)}
    },
    "SHORK": {
        "fg": curses.COLOR_CYAN,
        "bg": 16,
        "accent": curses.COLOR_WHITE,
        "select_bg": curses.COLOR_BLACK,
        "select_fg": curses.COLOR_CYAN,
        "custom": {16: (84, 120, 255)}
    },
    "OZ": {
        "fg": curses.COLOR_YELLOW,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_WHITE,
        "select_bg": curses.COLOR_WHITE,
        "select_fg": curses.COLOR_BLACK,
    },
    "DOUG": {
        "fg": curses.COLOR_BLACK,
        "bg": 17,
        "accent": curses.COLOR_GREEN,
        "select_bg": curses.COLOR_BLACK,
        "select_fg": 47,
        "custom": {17: (600, 1000, 600)},
        "text_fg": 0
    },
    "APRIL": {
        "fg": curses.COLOR_WHITE,
        "bg": 18,
        "accent": 19,
        "select_bg": 20,
        "select_fg": curses.COLOR_BLACK,
        "custom": {18: (1000, 600, 800), 19: (400, 600, 1000), 20: (1000, 1000, 400)}
    },
    "MOSS MANN": {
        "fg": curses.COLOR_WHITE,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_RED,
        "select_bg": curses.COLOR_RED,
        "select_fg": curses.COLOR_WHITE,
        "custom": {21: (800, 200, 100)}
    },
    "STU": {
        "fg": curses.COLOR_WHITE,
        "bg": 22,
        "accent": curses.COLOR_GREEN,
        "select_bg": curses.COLOR_GREEN,
        "select_fg": curses.COLOR_BLACK,
        "custom": {22: (0, 200, 0)}
    },
    "CINNAMON": {
        "fg": curses.COLOR_YELLOW,
        "bg": 23,
        "accent": curses.COLOR_WHITE,
        "select_bg": curses.COLOR_WHITE,
        "select_fg": curses.COLOR_BLACK,
        "custom": {23: (183, 116, 102)}
    },
    "OMEN": {
        "fg": curses.COLOR_WHITE,
        "bg": 24,
        "accent": 25,
        "select_bg": 25,
        "select_fg": curses.COLOR_WHITE,
        "custom": {24: (300, 300, 300), 25: (600, 300, 800)}
    },
    "CALCULESTER": {
        "fg": curses.COLOR_GREEN,
        "bg": curses.COLOR_BLACK,
        "accent": curses.COLOR_GREEN,
        "select_bg": curses.COLOR_GREEN,
        "select_fg": curses.COLOR_BLACK,
    },
}

def load_external_themes():
    themes = {}
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR, exist_ok=True)
        example = {
            "fg": curses.COLOR_YELLOW,
            "bg": curses.COLOR_BLUE,
            "accent": curses.COLOR_CYAN,
            "select_bg": curses.COLOR_RED,
            "select_fg": curses.COLOR_WHITE
        }
        with open(os.path.join(THEMES_DIR, "example.json"), "w", encoding="utf-8") as f:
            json.dump(example, f, indent=2)
    for filepath in glob.glob(os.path.join(THEMES_DIR, "*.json")):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                name = os.path.splitext(os.path.basename(filepath))[0]
                themes[name] = data
        except:
            pass
    return themes

def get_all_themes():
    external = load_external_themes()
    all_themes = {}
    all_themes.update(BUILTIN_THEMES)
    all_themes.update(external)
    return list(all_themes.keys()), all_themes

def init_custom_colors(theme_def):
    if not curses.can_change_color():
        return False
    custom = theme_def.get("custom", {})
    for idx, rgb in custom.items():
        if isinstance(idx, int) and len(rgb) == 3:
            curses.init_color(idx, rgb[0], rgb[1], rgb[2])
    return bool(custom)

def apply_theme():
    theme_name = SETTINGS.get("theme", "DEFAULT")
    _, all_themes = get_all_themes()
    theme = all_themes.get(theme_name, BUILTIN_THEMES["DEFAULT"])
    init_custom_colors(theme)
    
    bg = theme.get("bg", curses.COLOR_BLACK)
    fg = theme.get("fg", curses.COLOR_WHITE)
    accent = theme.get("accent", curses.COLOR_CYAN)
    select_bg = theme.get("select_bg", curses.COLOR_CYAN)
    select_fg = theme.get("select_fg", curses.COLOR_BLACK)

    text_fg = theme.get("text_fg", curses.COLOR_WHITE)
    
    curses.init_pair(1, fg, bg)
    curses.init_pair(2, accent, bg)
    curses.init_pair(3, select_fg, select_bg)
    curses.init_pair(4, text_fg, bg)

def add_markdown_str(stdscr, y, x, text, text_pair=None):
    if text_pair is None:
        text_pair = curses.color_pair(4)
    title_match = re.match(r'^(#{1,6})\s+(.*)', text)
    if title_match:
        text = title_match.group(2)
        base_pair = curses.color_pair(2)
        base_attr = curses.A_BOLD
    else:
        base_pair = text_pair
        base_attr = 0

    h, w = stdscr.getmaxyx()
    if y >= h - 1:
        return y
    parts = re.split(r'(\*\*|_|`)', text)
    curr_attr = curses.A_NORMAL
    line_x = x
    line_y = y
    for part in parts:
        if part == '**':
            curr_attr ^= curses.A_BOLD
            continue
        elif part == '_':
            curr_attr ^= curses.A_ITALIC if hasattr(curses, 'A_ITALIC') else curses.A_UNDERLINE
            continue
        elif part == '`':
            curr_attr ^= curses.A_REVERSE
            continue
        elif not part:
            continue

        words = part.split(' ')
        for i, word in enumerate(words):
            prefix = ' ' if (line_x > x or i > 0) else ''
            word_width = len(prefix) + len(word)
            if word_width > w - x:
                available = w - line_x - len(prefix)
                if available > 0:
                    word = word[:available]
                    word_width = len(prefix) + len(word)
                else:
                    line_y += 1
                    line_x = x
                    if line_y >= h - 1:
                        return line_y
                    prefix = ''
                    word_width = len(word)

            if line_x + word_width >= w:
                line_y += 1
                line_x = x
                if line_y >= h - 1:
                    return line_y
                prefix = ''
            try:
                if prefix:
                    stdscr.addstr(line_y, line_x, prefix, curr_attr | base_attr | base_pair)
                    line_x += len(prefix)
                stdscr.addstr(line_y, line_x, word, curr_attr | base_attr | base_pair)
                line_x += len(word)
            except curses.error:
                pass

    return line_y + 1

def parse_fiche(filepath):
    pages = []
    current_page = None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('page '):
            if current_page:
                pages.append(current_page)
            title = line.split('"', 2)[1] if '"' in line else "Page"
            current_page = {"type": "content", "title": title, "elements": []}
        elif line.startswith('tf '):
            if current_page:
                pages.append(current_page)
            parts = line.split('"', 2)
            title = parts[1]
            last = parts[-1].lower()
            correct = 0 if "true" in last else 1
            current_page = {"type": "tf", "title": title, "options": ["VRAI", "FAUX"], "correct": correct, "user_answer": 0, "elements": []}
        elif line.startswith('mcq '):
            if current_page:
                pages.append(current_page)
            parts = line.split('"', 2)
            title = parts[1]
            correct_letter = parts[-1].replace(',', '').strip().upper()
            correct_index = ord(correct_letter) - 65
            current_page = {"type": "mcq", "title": title, "options": [], "correct": correct_index, "user_answer": 0, "elements": []}
        elif line.startswith('text '):
            if current_page:
                content = line.split('"', 2)[1] if '"' in line else line[5:]
                current_page["elements"].append(("text", content))
        elif line.startswith('image '):
            if current_page:
                path = line.split('"', 2)[1] if '"' in line else line[6:]
                current_page["elements"].append(("image", path))
        elif line.startswith('subtext '):
            if current_page:
                content = line.split('"', 2)[1] if '"' in line else line[8:]
                current_page["elements"].append(("subtext", content))
        elif current_page and current_page["type"] == "mcq":
            m = re.match(r'^([A-Z])\s*:?\s*"(.*)"$', line)
            if m:
                letter, answer = m.groups()
                current_page["options"].append(f"{letter} : {answer}")
    if current_page:
        pages.append(current_page)
    return pages

def draw_ascii_title(stdscr):
    h, w = stdscr.getmaxyx()
    art = [r"   _________       __         .__   ",r"  /   _____/ ____ |  | ____ __|  |  ",r"  \_____  \ /  _ \|  |/ /  |  \  |  ",r"  /        (  <_> )    <|  |  /  |__",r" /_______  /\____/|__|_ \____/|____/",r"         \/            \/           "]
    stdscr.clear()
    for i, line in enumerate(art):
        if h > 15:
            stdscr.addstr(h//2 - 6 + i, max(0, (w - len(line))//2), line, curses.color_pair(2) | curses.A_BOLD)
    msg = get_str("welcome", SETTINGS["username"])
    stdscr.addstr(h//2 + 2, max(0, (w - len(msg))//2), msg)
    stdscr.refresh()
    while stdscr.getch() != 10:
        pass

def settings_menu(stdscr):
    idx = 0
    options = ["username", "lang", "images_enabled", "terminer_mode", "theme", "character"]
    term_modes = ["ASK", "AUTO", "NEVER"]
    characters = list(CHARACTER_PHRASES.keys())
    def get_theme_list():
        theme_names, _ = get_all_themes()
        return theme_names
    while True:
        theme_list = get_theme_list()
        stdscr.bkgd(' ', curses.color_pair(1))
        stdscr.clear()
        stdscr.addstr(2, 4, get_str("settings_title"), curses.A_BOLD | curses.color_pair(2))
        for i, key in enumerate(options):
            label = get_str(f"opt_{key[:4]}")
            val = SETTINGS[key]
            if key == "images_enabled":
                val = "ON" if val else "OFF"
            text = f"{label} : < {val} >"
            if i == idx:
                stdscr.addstr(5+i, 6, f"> {text}", curses.color_pair(3) | curses.A_BOLD)
            else:
                stdscr.addstr(5+i, 6, f"  {text}", curses.color_pair(4))
        stdscr.addstr(15, 4, get_str("settings_help"), curses.A_DIM)
        k = stdscr.getch()
        if k == curses.KEY_UP:
            idx = (idx - 1) % len(options)
        elif k == curses.KEY_DOWN:
            idx = (idx + 1) % len(options)
        elif k in [curses.KEY_LEFT, curses.KEY_RIGHT]:
            key_name = options[idx]
            delta = 1 if k == curses.KEY_RIGHT else -1
            if key_name == "username":
                curses.echo()
                stdscr.addstr(18, 6, "Nom: ")
                new_name = stdscr.getstr(18, 15).decode('utf-8')
                if new_name:
                    SETTINGS[key_name] = new_name
                curses.noecho()
            elif key_name == "lang":
                SETTINGS[key_name] = "EN" if SETTINGS[key_name] == "FR" else "FR"
            elif key_name == "images_enabled":
                SETTINGS[key_name] = not SETTINGS[key_name]
            elif key_name == "terminer_mode":
                current = SETTINGS[key_name]
                idx_mode = term_modes.index(current)
                new_idx = (idx_mode + delta) % len(term_modes)
                SETTINGS[key_name] = term_modes[new_idx]
            elif key_name == "theme":
                current = SETTINGS[key_name]
                if current not in theme_list and theme_list:
                    current = theme_list[0]
                idx_theme = theme_list.index(current)
                new_idx = (idx_theme + delta) % len(theme_list)
                SETTINGS[key_name] = theme_list[new_idx]
                apply_theme()
            elif key_name == "character":
                current = SETTINGS[key_name]
                idx_char = characters.index(current) if current in characters else 0
                new_idx = (idx_char + delta) % len(characters)
                SETTINGS[key_name] = characters[new_idx]
        elif k == 10:
            break
    save_settings()

def run_fiche(stdscr, filepath):
    pages = parse_fiche(filepath)
    if not pages:
        return
    curr = 0
    start_time = time.time()
    random_phrase = random.choice(NEXT_PHRASES)

    while curr <= len(pages):
        stdscr.clear()
        if curr == len(pages):
            if SETTINGS["terminer_mode"] == "NEVER":
                break
            if SETTINGS["terminer_mode"] == "ASK":
                stdscr.addstr(5, 5, get_str("submit_results"), curses.A_BOLD | curses.color_pair(2))
                opts = [get_str("yes"), get_str("no")]
                sel = 0
                while True:
                    for i, o in enumerate(opts):
                        if i == sel:
                            attr = curses.color_pair(3) | curses.A_BOLD
                            prefix = "▶ "
                        else:
                            attr = curses.color_pair(4)
                            prefix = "  "
                        stdscr.addstr(7+i, 7, f"{prefix}{o}", attr)
                    k = stdscr.getch()
                    if k == curses.KEY_UP:
                        sel = 0
                    elif k == curses.KEY_DOWN:
                        sel = 1
                    elif k == 10:
                        break
                if sel == 1:
                    curr -= 1
                    continue
            qs = [p for p in pages if p["type"] in ["tf", "mcq"]]
            score = sum(1 for p in qs if p["user_answer"] == p["correct"])
            total = len(qs)
            elapsed = round(time.time() - start_time)
            ratio = score / total if total > 0 else 1.0
            
            if ratio == 1.0:
                rank_display = "PARFAIT!"
                rank_key = "PERFECT"
            elif ratio >= 0.8:
                rank_display = "Bien!"
                rank_key = "GOOD"
            elif ratio >= 0.5:
                rank_display = "OK."
                rank_key = "OK"
            else:
                rank_display = "Essaie encore..."
                rank_key = "BAD"
            
            char_phrases = CHARACTER_PHRASES.get(SETTINGS["character"], CHARACTER_PHRASES["Default"])
            judge_sentence = random.choice(char_phrases[rank_key])
            
            stdscr.clear()
            stdscr.addstr(3, 5, f"--- RESULTS : {os.path.basename(filepath)} ---", curses.A_BOLD | curses.color_pair(2))
            stdscr.addstr(6, 7, f"SCORE  : {score} / {total}", curses.A_BOLD | curses.color_pair(4))
            stdscr.addstr(7, 7, f"TIME  : {elapsed} secondes", curses.color_pair(4))
            stdscr.addstr(9, 7, f"NOTES :", curses.A_DIM | curses.color_pair(4))
            stdscr.addstr(10, 9, f"\"{judge_sentence}\"", curses.A_ITALIC | curses.color_pair(2))
            stdscr.addstr(12, 7, f"RANG   : {rank_display}", curses.color_pair(3) | curses.A_BOLD)
            if total > 0:
                sf = filepath.rsplit('.', 1)[0] + "_scoreboard.txt"
                with open(sf, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now().strftime('%d/%m %H:%M')} | {SETTINGS['username']} | {score}/{total} | {elapsed}s\n")
            stdscr.getch()
            break
        page = pages[curr]
        stdscr.addstr(2, 2, f"{page['title']} ({curr+1}/{len(pages)})", curses.A_BOLD | curses.color_pair(2))
        y = 4
        for typ, content in page["elements"]:
            if typ == "text":
                y = add_markdown_str(stdscr, y, 4, content, curses.color_pair(4)) + 1
            elif typ == "image" and SETTINGS["images_enabled"]:
                stdscr.addstr(y, 4, f"[ IMAGE : {content} - Touche 'I' ]", curses.color_pair(2))
                y += 2
            elif typ == "subtext":
                y = add_markdown_str(stdscr, y, 6, f"~ {content}", curses.color_pair(4)) + 1

        if page["type"] in ["tf", "mcq"]:
            for i, opt in enumerate(page["options"]):
                if i == page["user_answer"]:
                    attr = curses.color_pair(3) | curses.A_BOLD
                    prefix = "▶ "
                else:
                    attr = curses.color_pair(4)
                    prefix = "  "
                stdscr.addstr(y + i, 6, f"{prefix}{opt}", attr)
            y += len(page["options"]) + 1
        else:
            stdscr.addstr(y + 1, 4, f"[ {random_phrase} ]", curses.color_pair(3) | curses.A_BOLD)

        help_text = get_str("fiche_help")
        h, w = stdscr.getmaxyx()
        if h > 2:
            stdscr.addstr(h-2, 2, help_text, curses.A_DIM | curses.color_pair(4))

        k = stdscr.getch()
        if k in [ord('q'), ord('Q')]:
            break
        elif k in [curses.KEY_RIGHT, 10]:
            curr += 1
            random_phrase = random.choice(NEXT_PHRASES)
        elif k == curses.KEY_LEFT and curr > 0:
            curr -= 1
            random_phrase = random.choice(NEXT_PHRASES)
        elif k == ord('i') and SETTINGS["images_enabled"]:
            for typ, path in page["elements"]:
                if typ == "image":
                    webbrowser.open(path)
        elif page["type"] in ["tf", "mcq"]:
            if k == curses.KEY_UP:
                page["user_answer"] = max(0, page["user_answer"] - 1)
            elif k == curses.KEY_DOWN:
                page["user_answer"] = min(len(page["options"]) - 1, page["user_answer"] + 1)

def main_menu(stdscr):
    load_settings()
    curses.curs_set(0)
    curses.start_color()
    apply_theme()
    check_terminal_size(stdscr)
    draw_ascii_title(stdscr)

    def scan_files():
        return [f for f in (glob.glob("*.txt") + glob.glob("*.fiche")) if not f.endswith("scoreboard.txt")]

    files = scan_files()
    sel = 0

    while True:
        stdscr.bkgd(' ', curses.color_pair(1))
        stdscr.clear()
        stdscr.addstr(2, 4, get_str("menu_title"), curses.A_BOLD | curses.color_pair(2))
        if not files:
            stdscr.addstr(5, 6, get_str("no_files"), curses.color_pair(4))
        for i, f in enumerate(files):
            if i == sel:
                stdscr.addstr(5 + i, 6, f"> {f}", curses.color_pair(3) | curses.A_BOLD)
            else:
                stdscr.addstr(5 + i, 6, f"  {f}", curses.color_pair(4))
        stdscr.addstr(curses.LINES-2, 4, get_str("menu_help"), curses.A_DIM | curses.color_pair(4))
        k = stdscr.getch()
        if k == curses.KEY_UP:
            if files:
                sel = (sel - 1) % len(files)
        elif k == curses.KEY_DOWN:
            if files:
                sel = (sel + 1) % len(files)
        elif k == 10 and files:
            run_fiche(stdscr, files[sel])
            stdscr.clear()
            stdscr.refresh()
        elif k in [ord('r'), ord('R')]:
            files = scan_files()
            sel = 0
        elif k in [ord('s'), ord('S')]:
            settings_menu(stdscr)
            apply_theme()
        elif k in [ord('c'), ord('C')] and files:
            stdscr.clear()
            sf = files[sel].rsplit('.', 1)[0] + "_scoreboard.txt"
            if os.path.exists(sf):
                with open(sf, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines[-15:]):
                    stdscr.addstr(2 + i, 2, line.strip(), curses.color_pair(4))
            else:
                stdscr.addstr(2, 2, get_str("empty_scoreboard"), curses.color_pair(4))
            stdscr.getch()
        elif k in [ord('q'), ord('Q')]:
            break

if __name__ == "__main__":
    curses.wrapper(main_menu)
