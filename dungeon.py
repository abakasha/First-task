"""Правила игры «Пещера гоблинов»: бой, покупки, цены, герой, враги."""

import random
from time import sleep


prices = {"potion": 10, "torch_oil": 15, "war_elixir": 40}

enemy_stats = {
    "гоблин": {"hp": 30, "damage": 4, "loot": 15},
    "скелет": {"hp": 45, "damage": 6, "loot": 25},
    "паук": {"hp": 20, "damage": 3, "loot": 10},
    "кобольт": {"hp": 35, "damage": 5, "loot": 20},
}


class Hero:
    """Герой со своими характеристиками и правилами."""
    
    def __init__(self, name, health, strength, agility, endurance):
        self.name = name
        self.health = health
        self.strength = strength
        self.agility = agility
        self.endurance = endurance
        
        # Вычисляемые характеристики
        self.damage = 10 + strength * 1.5
        self.crit_damage = self.damage * 2
        self.stamina = agility * 2

    def __str__(self):
        return (f"{self.name}: здоровье {self.health}, "
                f"урон {self.damage:.1f}, крит {self.crit_damage:.1f}, "
                f"силы {self.stamina}")

    def strike(self, n):
        """Удар номер n: каждый третий — критический."""
        if n % 3 == 0:
            return self.crit_damage, True
        return self.damage, False

    def spend_stamina(self, cost):
        """Тратит силы. Если не хватает — списывает из здоровья. Возвращает True, если перешёл в упорство."""
        if self.stamina >= cost:
            self.stamina -= cost
            return False
        else:
            self.health -= cost - self.stamina
            self.stamina = 0
            return True

    def heal(self, amount, cap):
        """Лечит, не превышая потолок cap."""
        self.health = min(self.health + amount, cap)

    def to_dict(self):
        """Словарь для сохранения в JSON."""
        return {
            "name": self.name,
            "health": self.health,
            "stamina": self.stamina,
            "strength": self.strength,
            "agility": self.agility,
            "endurance": self.endurance,
        }

    @staticmethod
    def from_dict(data):
        """Создаёт героя из словаря сохранения."""
        hero = Hero(data["name"], data["health"], data["strength"], data["agility"], data["endurance"])
        hero.stamina = data["stamina"]
        return hero


class Enemy:
    """Враг на один бой."""
    
    def __init__(self, name, stats):
        self.name = name
        self.hp = float(stats["hp"])
        self.damage = stats["damage"]
        self.loot = stats["loot"]


def fight(enemy, hero, bonus=0):
    """Бой с enemy до гибели одного из двоих.
    
    Печатает строки раундов.
    Возвращает (rounds, won, loot).
    """
    round_n = 0
    rounds = []

    print(f"Вы спускаетесь по ступеням. Из темноты выходит {enemy.name}!")

    while enemy.hp > 0 and hero.health > 0:
        round_n += 1
        hit, crit = hero.strike(round_n)
        hero_hit_now = hit + bonus

        if crit:
            crit_mark = " - критический!"
        else:
            crit_mark = ""

        enemy.hp -= hero_hit_now
        print(f"Раунд {round_n}: вы наносите {hero_hit_now:.1f} урона{crit_mark}. Здоровье {enemy.name}: {max(enemy.hp, 0):.1f}.", end=" ")
        sleep(0.5)

        if enemy.hp <= 0:
            enemy_hit = 0
            print(f"{enemy.name} падает!")
        else:
            enemy_hit = enemy.damage
            hero.health -= enemy_hit
            print(f"{enemy.name} бьёт в ответ на {enemy_hit}.")
            sleep(0.5)

        rounds.append([round_n, hero_hit_now, enemy_hit])

    won = enemy.hp <= 0
    loot = enemy.loot if won else 0
    return rounds, won, loot


def buy(price, gold, quantity=1):
    """Покупает quantity штук товара ценой price за золото gold."""
    cost = price * quantity
    if gold >= cost:
        return gold - cost, True
    return gold, False


if __name__ == "__main__":
    test_hero = Hero("Тест", 100, 7, 5, 4)
    test_enemy = Enemy("скелет", enemy_stats["скелет"])
    rounds, won, loot = fight(test_enemy, test_hero, 0)
    print(f"self-test: {len(rounds)} rounds, won={won}, loot={loot}, hero hp={test_hero.health}")