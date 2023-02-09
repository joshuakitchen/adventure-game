
HAND = 0
BRONZE_SWORD = 10
IRON_SWORD = 20
STEEL_SWORD = 30
MITHRIL_SWORD = 40
ADAMANTINE_SWORD = 50

player = (
    'player',
    dict(
        hp=10,
        strength=8,
        sword=1,
        melee_strength=ADAMANTINE_SWORD))
enemy = ('slime', dict(hp=5))


def get_max_hit(strength_level: int, skill_level: int, equipment_bonus: int):
    a = pow(strength_level, 0.3) + pow(skill_level, 0.3)
    return int(a * ((equipment_bonus + 16) / 32))


for i in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
    print(
        get_max_hit(
            1, 1, i), get_max_hit(
            5, 5, i), get_max_hit(
                50, 50, i), get_max_hit(
                    99, 99, i))

while True:
    action = input()
    if action == 'attack':
        print(
            'You attack the \x1b[31mSlime\x1b[0m and deal \x1b[31m4\x1b[0m damage.')
