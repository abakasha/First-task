import random
from time import sleep

# ================================================
# ИГРА «ПЕЩЕРА ГОБЛИНОВ»
# Автор: Иван Абакумов
# Дата: сентябрь 2026
#
# Пункт 4 — «прислушаться»: герой замирает
# и слушает, что происходит в темноте.
# ================================================

title = "ПЕЩЕРА ГОБЛИНОВ"
frame = "=" * 21
print(frame)
print("   " + title + "   ")
print(frame)
print()

print("Как зовут героя?")
hero_name = input()
print(f"Добро пожаловать, {hero_name}!")
print("Ты входишь в пещеру. Здесь темно и пахнет сыростью.")
print()

# --- Настройка героя (с защитой) ------------------
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

base_attack = 10
damage = base_attack + strength * 1.5
crit_damage = damage * 2
stamina = agility * 2

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

# --- Состояние игры -------------------------------
running = True
actions = 0
menu_last = 7
outcome = "прерывание"

enemies = ["гоблин", "скелет", "паук", "кобольт"]
log = []

try:
    while running:
        print("Что делаешь?")
        print("1 - осмотреться")
        print("2 - идти вперёд")
        print("3 - отдохнуть")
        print("4 - прислушаться")
        print("5 - обыскать мешок")
        print("6 - тренировка")
        print("7 - спуститься глубже")
        print("0 - выйти из пещеры")

        while True:
            choice = input()
            try:
                menu_number = int(choice)
            except ValueError:
                print("Такого пункта нет. Введи номер пункта из меню.")
                continue
            if 0 <= menu_number <= menu_last:
                break
            print("Такого пункта нет. Введи номер пункта из меню.")

        match choice:
            case "1":
                print("Вы осмотрелись. Стены пещеры покрыты странными знаками.")
            case "2":
                cost = 2
                if stamina >= cost:
                    stamina -= cost
                    print("Вы осторожно идёте вперёд. Под ногами хрустят мелкие камни.")
                else:
                    health -= cost - stamina
                    stamina = 0
                    print("Сил больше нет — вы идёте на одном упорстве.")
            case "3":
                stamina += 3
                print("Вы присели у стены и перевели дух.")
            case "4":
                print("Вы замерли и прислушались. Где-то в глубине капает вода.")
            case "5":
                print("Вы обыскали мешок и нашли старый факел.")
            case "6":
                strikes = 6
                print("Вы подходите к каменной глыбе, стоящей у стены.")
                print("На ней видны следы старых ударов — здесь тренировались до вас.")
                print()
                print(f"Наносите {strikes} ударов.")

                total_damage = 0
                crit_count = 0

                for i in range(1, strikes + 1):
                    if i % 3 == 0:
                        hit_damage = crit_damage
                        mark = " — критический!"
                        crit_count += 1
                    else:
                        hit_damage = damage
                        mark = ""

                    print(f"Удар {i}: {hit_damage:.1f}{mark}")
                    sleep(0.5)
                    total_damage += hit_damage

                stamina -= 3

                print()
                print(f"Итог: {strikes} ударов, критических: {crit_count}.")
                print(f"Общий урон: {total_damage:.1f}")
                print(f"Средний урон: {total_damage / strikes:.1f}")
            case "7":
                if not enemies:
                    print("Вы спускаетесь глубже, но пещера пуста - здесь больше некому драться.")
                else:
                    enemy = random.choice(enemies)
                    enemy_hp = random.randint(50, 85)
                    round_n = 0
                    print(f"Вы спускаетесь по ступеням. Из темноты выходит {enemy}!")

                    while enemy_hp > 0 and health > 0:
                        round_n += 1

                        if round_n % 3 == 0:
                            hit_damage = crit_damage
                            crit_mark = " - критический!"
                        else:
                            hit_damage = damage
                            crit_mark = ""

                        enemy_hp -= hit_damage
                        print(f"Раунд {round_n}: вы наносите {hit_damage:.1f} урона{crit_mark}. Здоровье {enemy}: {max(enemy_hp, 0):.1f}.", end=" ")
                        sleep(0.5)

                        if enemy_hp <= 0:
                            print(f"{enemy} падает!")
                            log.append(f"раунд {round_n}: герой -{hit_damage:.1f}, {enemy} мёртв")
                        else:
                            enemy_damage = random.randint(10, 16)
                            health -= enemy_damage
                            print(f"{enemy} бьёт в ответ на {enemy_damage}.")
                            sleep(0.5)
                            log.append(f"раунд {round_n}: герой -{hit_damage:.1f}, {enemy} -{enemy_damage}")

                    if enemy_hp <= 0:
                        enemies.remove(enemy)
                        print(f"{enemy} побеждён! В пещере осталось врагов: {len(enemies)}.")
                    print(f"Бой занял раундов: {round_n}.")
                    print(f"Последняя запись журнала: {log[-1]}")
            case "0":
                print("Вы поднимаетесь обратно к свету. Пещера остаётся позади.")
                outcome = "выход"
                running = False

        if running:
            actions += 1

        if health <= 0:
            print(f"{hero_name} падает без сил. Пещера забирает ещё одного искателя.")
            outcome = "гибель"
            running = False

        print()
        print(f"Здоровье: {health}   Запас сил: {stamina}   Врагов осталось: {len(enemies)}")

except KeyboardInterrupt:
    print()
    print("Игрок прервал сеанс.")

finally:
    print()
    print(frame)
    if outcome == "гибель":
        print(f"Ты не дошёл, {hero_name}. Действий совершено: {actions}.")
    elif outcome == "выход":
        print(f"Забег окончен, {hero_name}. Действий совершено: {actions}.")
    else:
        print(f"Сеанс прерван, {hero_name}. Действий совершено: {actions}.")
    print(frame)