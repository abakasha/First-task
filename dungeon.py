"""Правила игры «Пещера гоблинов»: бой, покупки, цены, враги."""

import random
from time import sleep


prices = {"potion": 10, "torch_oil": 15, "war_elixir": 40}

enemy_stats = {
    "гоблин": {"hp": 30, "damage": 4, "loot": 15},
    "скелет": {"hp": 45, "damage": 6, "loot": 25},
    "паук": {"hp": 20, "damage": 3, "loot": 10},
    "кобольт": {"hp": 35, "damage": 5, "loot": 20},
}


def hero_hit(strike_n, damage, crit_damage):
    """Урон героя в удар strike_n; возвращает (hit, crit)."""
    if strike_n % 3 == 0:
        return crit_damage, True
    return damage, False


def fight(enemy, hero_health, bonus, damage, crit_damage):
    """Бой с enemy до гибели одного из двоих.

    Карточка врага берётся из enemy_stats.
    bonus — надбавка к урону героя.
    Печатает строки раундов.
    Возвращает (rounds, won, hero_health, loot).
    """
    stats = enemy_stats[enemy]
    enemy_hp = float(stats["hp"])
    round_n = 0
    rounds = []

    print(f"Вы спускаетесь по ступеням. Из темноты выходит {enemy}!")

    while enemy_hp > 0 and hero_health > 0:
        round_n += 1
        hit, crit = hero_hit(round_n, damage, crit_damage)
        hero_hit_now = hit + bonus

        if crit:
            crit_mark = " - критический!"
        else:
            crit_mark = ""

        enemy_hp -= hero_hit_now
        print(f"Раунд {round_n}: вы наносите {hero_hit_now:.1f} урона{crit_mark}. Здоровье {enemy}: {max(enemy_hp, 0):.1f}.", end=" ")
        sleep(0.5)

        if enemy_hp <= 0:
            enemy_hit = 0
            print(f"{enemy} падает!")
        else:
            enemy_hit = stats["damage"]
            hero_health -= enemy_hit
            print(f"{enemy} бьёт в ответ на {enemy_hit}.")
            sleep(0.5)

        rounds.append([round_n, hero_hit_now, enemy_hit])

    won = enemy_hp <= 0
    loot = stats["loot"] if won else 0
    return rounds, won, hero_health, loot


def buy(price, gold, quantity=1):
    """Покупает quantity штук товара ценой price за золото gold.

    quantity по умолчанию 1.
    Возвращает (gold_left, ok).
    Ничего не печатает.
    """
    cost = price * quantity
    if gold >= cost:
        return gold - cost, True
    return gold, False


if __name__ == "__main__":
    rounds, won, hp, loot = fight("скелет", 100, 0, 20.5, 41.0)
    print(f"self-test: {len(rounds)} rounds, won={won}, loot={loot}")