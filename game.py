import random
from time import sleep
import os
import json

import dungeon

try:
    from colorama import Fore, Style, init
    init()
    COLOR = True
except ImportError:
    COLOR = False


# ================================================
# ИГРА «ПЕЩЕРА ГОБЛИНОВ»
# Автор: Иван Абакумов
# Дата: сентябрь 2026
# ================================================

title = "ПЕЩЕРА ГОБЛИНОВ"
frame = "=" * 21

base_attack = 10
stamina_rest = 3
stamina_move = 2
stamina_train = 3
strikes_train = 6


# --- Карта и навигация ---------------------------
MAP = [
    ["#", "#", "#", "#", "#"],
    ["#", ".", ".", "#", "#"],
    ["#", ".", "#", ".", "#"],
    ["#", ".", "#", ".", "#"],
    ["#", "#", "S", ".", "#"],
]

DIRECTIONS = {
    "north": (-1, 0),
    "south": (1, 0),
    "west":  (0, -1),
    "east":  (0, 1),
}

LOOT = {
    (1, 1): "старая монета",
    (2, 3): "пыльное зелье",
    (3, 3): "камень стража",
}

num_to_verb = {
    "1": "look", "2": "go", "3": "rest", "4": "listen",
    "5": "torch", "6": "train", "7": "descend",
    "8": "leaders", "9": "shop", "10": "backpack",
    "11": "drink", "0": "exit",
}

commands = [
    "look", "go", "go <направление>", "rest", "listen", "torch",
    "train", "descend", "leaders", "shop", "backpack",
    "drink potion", "buy <item> [count]", "map", "scout",
    "newgame", "help", "exit",
]

MENU = [
    "Что делаешь? (номер или команда; help — справка)",
    "1 - осмотреться (look)",
    "2 - идти вперёд (go)",
    "3 - отдохнуть (rest)",
    "4 - прислушаться (listen)",
    "5 - обыскать мешок (torch)",
    "6 - тренировка (train)",
    "7 - спуститься глубже (descend)",
    "8 - таблица лидеров (leaders)",
    "9 - магазин (shop)",
    "10 - рюкзак (backpack)",
    "11 - выпить зелье (drink)",
    "   карта (map) / разведка (scout) / шаг (go north) / новая игра (newgame)",
    "0 - выйти из пещеры (exit)",
]


def write_save():
    """Сохраняет состояние забега в save.json."""
    save = {
        "hero": hero_name,
        "health": health,
        "stamina": stamina,
        "max_health": max_health,
        "max_stamina": max_stamina,
        "damage": damage,
        "crit_damage": crit_damage,
        "gold": gold_total,
        "actions": actions,
        "ability_bonus": ability_bonus,
        "inventory": inventory,
        "enemies": enemies,
        "log": log,
        "position": [hero_r, hero_c],
        "visited": [list(p) for p in visited],
        "loot": sorted(found_loot),
    }
    with open("save.json", "w", encoding="utf-8") as f:
        json.dump(save, f, ensure_ascii=False, indent=2)


def print_leaderboard(log):
    """Печатает таблицу лидеров по журналу log. Возвращает None."""
    if not log:
        print("Вы ещё не сражались — таблица лидеров пуста.")
        return

    top = sorted(log, key=lambda r: r[1], reverse=True)[:3]
    print("Таблица лидеров (по урону героя):")
    for i in range(len(top)):
        print(f"  {i + 1}. Раунд {top[i][0]}: {top[i][1]:.1f}")

    worst = max(log, key=lambda r: r[2])
    print(f"Сильнейший удар врага: {worst[2]} (раунд {worst[0]}).")


def print_run_summary(log):
    """Печатает итог забега. Возвращает None."""
    total = sum(r[1] for r in log)
    rounds = len(log)

    if rounds > 0:
        print(f"Урон: {total:.1f} за {rounds} раундов, средний: {total / rounds:.1f}.")
    else:
        print("Боёв в этом забеге не было.")


def scout(r, c, seen):
    """Рекурсивно считает доступные комнаты из клетки (r, c)."""
    if (r, c) in seen or MAP[r][c] == "#":
        return 0

    seen.add((r, c))
    total = 1

    for dr, dc in DIRECTIONS.values():
        total += scout(r + dr, c + dc, seen)

    return total


print(frame)
print("   " + title + "   ")
print(frame)
print()

# --- Загрузка сохранения --------------------------
loaded = None
if os.path.exists("save.json"):
    print("Сохранение найдено. Продолжить забег? (да/нет)")
    answer = input().strip().lower()
    if answer == "да":
        try:
            with open("save.json", encoding="utf-8") as f:
                loaded = json.load(f)
        except json.JSONDecodeError:
            print("Сохранение повреждено. Начинаем новый забег.")
            loaded = None


# --- Настройка или продолжение --------------------
if loaded is None:
    print("Как зовут героя?")
    hero_name = input()
    print(f"Добро пожаловать, {hero_name}!")
    print("Ты входишь в пещеру. Здесь темно и пахнет сыростью.")
    print()

    print("Настройка героя.")
    print("Здоровье, сила, ловкость, интеллект — по одному числу в строке:")

    while True:
        try:
            health = int(input())
            strength = int(input())
            agility = int(input())
            intelligence = int(input())
            if health <= 0:
                raise ValueError(f"Здоровье должно быть положительным, а введено {health}")
            if strength <= 0 or agility <= 0 or intelligence <= 0:
                raise ValueError("Характеристики не могут быть отрицательными")
            break
        except ValueError as e:
            print(f"{e}. Введите все четыре снова:")

    damage = base_attack + strength * 1.5
    crit_damage = damage * 2
    stamina = agility * 2

    max_health = health
    max_stamina = stamina

    print("Характеристики героя:")
    print(f"Здоровье:    {health:4d}")
    print(f"Сила:        {strength:4d}")
    print(f"Ловкость:    {agility:4d}")
    print(f"Интеллект:   {intelligence:4d}")
    print()
    print(f"Урон героя:         {damage:.1f}")
    print(f"Критический урон:   {crit_damage:.1f}")
    print(f"Запас сил:          {stamina}")
    print()

    actions = 0
    enemies = ["гоблин", "скелет", "паук", "кобольт"]
    log = []
    gold_total = 0
    ability_bonus = 0
    inventory = {}
    hero_r, hero_c = 4, 2
    visited = {(4, 2)}
    found_loot = set()

else:
    hero_name = loaded["hero"]
    health = loaded["health"]
    stamina = loaded["stamina"]
    max_health = loaded["max_health"]
    max_stamina = loaded["max_stamina"]
    damage = loaded["damage"]
    crit_damage = loaded["crit_damage"]
    gold_total = loaded["gold"]
    actions = loaded["actions"]
    ability_bonus = loaded["ability_bonus"]
    inventory = loaded["inventory"]
    enemies = loaded["enemies"]
    log = loaded["log"]
    hero_r, hero_c = loaded["position"]
    visited = {tuple(p) for p in loaded["visited"]}
    found_loot = set(loaded["loot"])
    
    print(f"Забег продолжен: здоровье {health}, золото {gold_total}, врагов {len(enemies)}.")
    print()


running = True
outcome = "прерывание"

try:
    while running:
        print("\n".join(MENU))
        print()

        line = input()
        cmd = line.strip().lower()
        while cmd == "":
            print("Пустая команда. Введи команду или номер.")
            line = input()
            cmd = line.strip().lower()

        words = cmd.split()
        verb = words[0] if words else ""

        if cmd in num_to_verb:
            verb = num_to_verb[cmd]

        match verb:
            case "look":
                print("Вы осмотрелись. Стены пещеры покрыты странными знаками.")
            case "go":
                if len(words) > 1 and words[1] in DIRECTIONS:
                    dr, dc = DIRECTIONS[words[1]]
                    nr, nc = hero_r + dr, hero_c + dc

                    if 0 <= nr < len(MAP) and 0 <= nc < len(MAP[nr]) and MAP[nr][nc] != "#":
                        hero_r, hero_c = nr, nc
                        visited.add((hero_r, hero_c))
                        print(f"Вы идёте {words[1]}. Комната ({hero_r}, {hero_c}).")

                        if (hero_r, hero_c) in LOOT:
                            item = LOOT[(hero_r, hero_c)]
                            if item not in found_loot:
                                found_loot.add(item)
                                print(f"Найдено: {item}! Уникальный лут: {len(found_loot)}.")
                    else:
                        print(f"Нельзя идти {words[1]}: стена или край.")
                else:
                    if stamina >= stamina_move:
                        stamina -= stamina_move
                        print("Вы осторожно идёте вперёд. Под ногами хрустят мелкие камни.")
                    else:
                        health -= stamina_move - stamina
                        stamina = 0
                        print("Сил больше нет — вы идёте на одном упорстве.")
            case "rest":
                stamina = min(stamina + stamina_rest, max_stamina)
                print("Вы присели у стены и перевели дух.")
            case "listen":
                print("Вы замерли и прислушались. Где-то в глубине капает вода.")
            case "torch":
                inventory["torch"] = inventory.get("torch", 0) + 1
                print("Вы обыскали мешок и нашли старый факел. Он теперь в рюкзаке.")
            case "train":
                print("Вы подходите к каменной глыбе, стоящей у стены.")
                print("На ней видны следы старых ударов — здесь тренировались до вас.")
                print()
                print(f"Наносите {strikes_train} ударов.")

                total_damage = 0
                crit_count = 0

                for i in range(1, strikes_train + 1):
                    hit_damage, is_crit = dungeon.hero_hit(i, damage, crit_damage)

                    if is_crit:
                        mark = " — критический!"
                        crit_count += 1
                    else:
                        mark = ""

                    print(f"Удар {i}: {hit_damage:.1f}{mark}")
                    sleep(0.5)
                    total_damage += hit_damage

                stamina -= stamina_train

                print()
                print(f"Итог: {strikes_train} ударов, критических: {crit_count}.")
                print(f"Общий урон: {total_damage:.1f}")
                print(f"Средний урон: {total_damage / strikes_train:.1f}")
            case "descend":
                if not enemies:
                    print("Вы спускаетесь глубже, но пещера пуста - здесь больше некому драться.")
                else:
                    enemy = random.choice(enemies)
                    rounds, won, health, loot = dungeon.fight(
                        enemy, health, ability_bonus, damage, crit_damage
                    )
                    log.extend(rounds)

                    if won:
                        gold_total += loot
                        enemies.remove(enemy)
                        msg = f"{enemy} побеждён! В пещере осталось врагов: {len(enemies)}. Трофеи: {loot} золота."
                        if COLOR:
                            print(Fore.YELLOW + msg + Style.RESET_ALL)
                        else:
                            print(msg)
                    print(f"Бой занял раундов: {len(rounds)}.")
            case "leaders":
                print_leaderboard(log)
            case "shop":
                print("Магазин:")
                for name, price in dungeon.prices.items():
                    print(f"{name}: {price} золота")
            case "backpack":
                if not inventory:
                    print("Рюкзак пуст.")
                else:
                    print("Рюкзак:")
                    for name, qty in inventory.items():
                        print(f"{name}: {qty} шт.")
            case "buy":
                if len(words) > 1 and words[-1].isdigit():
                    qty = int(words[-1])
                    item = " ".join(words[1:-1])
                else:
                    qty = 1
                    item = " ".join(words[1:])

                if item == "":
                    print("Купить что? Введи: buy <товар>.")
                    continue
                if item not in dungeon.prices:
                    print("Такого товара в магазине нет.")
                    continue

                gold_total, ok = dungeon.buy(dungeon.prices[item], gold_total, quantity=qty)
                if ok:
                    inventory[item] = inventory.get(item, 0) + qty
                    print(f"Куплено: {qty} {item} за {dungeon.prices[item] * qty} золота. Осталось золота: {gold_total}.")
                else:
                    print(f"Не хватает золота: нужно {dungeon.prices[item] * qty}, есть {gold_total}.")
            case "drink":
                item = " ".join(words[1:]) or "potion"
                if inventory.get(item, 0) == 0:
                    print(f"В рюкзаке нет: {item}.")
                else:
                    health = min(health + 10, max_health)
                    inventory[item] -= 1
                    if inventory[item] == 0:
                        del inventory[item]
                    print(f"Вы выпили {item}. Здоровье: {health}. Осталось: {inventory.get(item, 0)}.")
            case "map":
                print("Карта:")
                for i in range(len(MAP)):
                    cells = []
                    for j in range(len(MAP[i])):
                        if (i, j) == (hero_r, hero_c):
                            cells.append("@")
                        else:
                            cells.append(MAP[i][j])
                    print(" ".join(cells))
            case "scout":
                seen = set()
                count = scout(hero_r, hero_c, seen)
                print(f"Разведка: {count} доступных комнат.")
            case "newgame":
                if os.path.exists("save.json"):
                    os.remove("save.json")
                    print("Сохранение удалено. Следующий забег начнётся с чистого листа.")
                else:
                    print("Сохранения нет.")
                continue
            case "help":
                print("Команды: " + ", ".join(commands) + ".")
                print("Номера 0-11 работают как раньше.")
            case "exit":
                print("Вы поднимаетесь обратно к свету. Пещера остаётся позади.")
                write_save()
                print("Прогресс сохранён.")
                outcome = "выход"
                running = False
            case _:
                print(f"Не понимаю: '{line.strip()}'. Введи 'help'.")
                continue

        if running:
            actions += 1

        if health <= 0:
            print(f"{hero_name} падает без сил. Пещера забирает ещё одного искателя.")
            if os.path.exists("save.json"):
                os.remove("save.json")
            outcome = "гибель"
            running = False

        state = f"Здоровье: {health}   Запас сил: {stamina}   Врагов осталось: {len(enemies)}   Золото: {gold_total}   Лут: {len(found_loot)}"
        print()
        if COLOR:
            print(Fore.GREEN + state + Style.RESET_ALL)
        else:
            print(state)

except KeyboardInterrupt:
    print()
    print("Игрок прервал сеанс.")
    write_save()

finally:
    print()
    print(frame)
    if outcome == "гибель":
        print(f"Ты не дошёл, {hero_name}. Действий совершено: {actions}.")
    elif outcome == "выход":
        print(f"Забег окончен, {hero_name}. Действий совершено: {actions}.")
    else:
        print(f"Сеанс прерван, {hero_name}. Действий совершено: {actions}.")

    print_run_summary(log)

    if inventory:
        print("В рюкзаке осталось:")
        for name, qty in inventory.items():
            print(f"  {name}: {qty} шт.")
    else:
        print("В рюкзаке ничего не осталось.")

    if found_loot:
        print("Найденный уникальный лут: " + ", ".join(found_loot) + ".")
    else:
        print("Уникального лута не найдено.")

    print(frame)