import math
import random

# TODO: BLOCKCHAIN ECHO ATTAck!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from .stubs import *

MAP_WIDTH = 40
MAP_HEIGHT = 40

TEAM_KEY = 88 if get_team() == TeamColor.BLUE else 176

# * Game stuff
COSTS = {
    RobotType.GUNNER: GameConstants.GUNNER_COST,
    RobotType.TANK: GameConstants.TANK_COST,
    RobotType.GRENADER: GameConstants.GRENADER_COST,
    RobotType.REFINERY: GameConstants.REFINERY_COST,
    RobotType.BARRACKS: GameConstants.BARRACKS_COST,
    RobotType.TURRET: GameConstants.TURRET_COST
}


# region helper funcs
def add(loc1, loc2):
    return loc1[0] + loc2[0], loc1[1] + loc2[1]


def sub(loc1, loc2):
    return loc1[0] - loc2[0], loc1[1] - loc2[1]


def dist(loc1, loc2):
    return (loc2[0] - loc1[0]) ** 2 + (loc2[1] - loc1[1]) ** 2


def inbounds(a, b):
    return 0 <= a < get_board_width() and 0 <= b < get_board_height()


def validate_blockchain(b, round_num):
    return (hash(tuple(b[:-1])) + 69 - TEAM_KEY - round_num) % 256 == b[-1]


def filter_blockchain(round_num):
    blocks = get_blockchain(round_num)
    valid = []
    for b in blocks:
        if validate_blockchain(b, round_num):
            valid.append(b)
    return valid


def get_rogue_block():
    invalid = []
    count = 0
    while not invalid and count < 40:
        count += 1
        round_num = random.randint(1, get_round_num() - 1)
        blocks = get_blockchain(round_num)
        invalid = []
        for b in blocks:
            if not validate_blockchain(b, round_num) and b not in get_rogue_block.allinvalid:
                invalid.append(b)
    if invalid:
        return random.choice(invalid)
    return [0] * 50


get_rogue_block.allinvalid = []


def sign_blockchain(b):
    b[-1] = (hash(tuple(b[:-1])) + 69 - TEAM_KEY - get_round_num()) % 256
    return b


def write_blockchain(b):
    add_to_blockchain(sign_blockchain(b))


def normalize(num):
    return 1 if num > 0 else -1 if num < 0 else 0


def getdir(loc1, loc2):
    diff = sub(loc2, loc1)
    greater = 1 if abs(diff[1]) > abs(diff[0]) else 0
    temp = [0, 0]
    temp[greater] = diff[greater]
    if abs(diff[1 - greater]) != 0 and abs(diff[greater]) / abs(diff[1 - greater]) < 2:
        temp[1 - greater] = diff[1 - greater]
    return normalize(temp[0]), normalize(temp[1])


def clockwise(loc):
    # angle = math.atan2(1, 0)
    angle = math.atan2(*loc)
    angle -= math.pi / 4
    pos = normalize(math.cos(angle)), normalize(math.sin(angle))
    return pos


def counter_clockwise(loc):
    # angle = math.atan2(1, 0)
    angle = math.atan2(*loc)
    angle += math.pi / 4
    pos = normalize(math.cos(angle)), normalize(math.sin(angle))
    return pos


# endregion helper funcs

class Robot:
    def __init__(self):
        self.team = get_team()
        self.type = get_type()
        self.location = get_location()
        self.board_width = get_board_width()
        self.board_height = get_board_height()
        self.round_num = get_round_num()
        self.since_spawn = 0

        if self.type != RobotType.HQ:
            blocks = filter_blockchain(0)
            assert (len(blocks) == 1)
            block = blocks[0]
            self.hq_loc = (block[2], block[3])
        else:
            self.hq_loc = self.location
        self.enemy_hq_loc = sub((self.board_width, self.board_height), self.hq_loc)
        self.robot_locs = {
            1: set(),  # builder
            2: set(),  # refiner
            3: set(),  # turret
            4: set(),  # barracks
            5: set(),  # tank
            6: set(),  # gunner
            7: set(),  # grenader
        }

    def parse_blockchain(self):
        if self.round_num == 0:
            return
        if self.type != RobotType.HQ:
            write_blockchain([{RobotType.BUILDER: 1, RobotType.REFINERY: 2,
                               RobotType.TURRET: 3, RobotType.BARRACKS: 4,
                               RobotType.TANK: 5, RobotType.GUNNER: 6, RobotType.GRENADER: 7}[self.type],
                              get_location()[0], get_location()[1]] + [54] * 47)
        for block in filter_blockchain(self.round_num - 1):
            block = block[:-1]
            robot_type = block[0]
            robot_loc = block[1], block[2]
            self.robot_locs[robot_type] = robot_loc

    def run(self):
        self.parse_blockchain()
        self.round_num += 1
        self.since_spawn += 1
        self.oil = get_oil()
        self.health = get_health()
        self.is_stunned = is_stunned()
        self.location = get_location()

    def trybuild(self, robot_type, exceptions=[]):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                delta = (dx, dy)
                loc = add(self.location, delta)
                if loc in exceptions or not inbounds(loc[0], loc[1]):
                    continue
                sensed = sense_location(loc)
                if sensed.type != RobotType.NONE:
                    continue
                create(robot_type, loc)
                return loc
        return None

    def trybuild2(self, robot_type, exceptions=[]):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                delta = (dx, dy)
                loc = add(self.location, delta)
                # if loc in exceptions or not bool(((loc[0] + 1) % 3) ^ (loc[1] % 3)) \
                #         or not inbounds(loc[0], loc[1]):
                if loc in exceptions or bool((loc[0] + 1) % 3) ^ bool(loc[1] % 3) \
                        or not inbounds(loc[0], loc[1]):
                    continue
                sensed = sense_location(loc)
                if sensed.type != RobotType.NONE:
                    continue
                create(robot_type, loc)
                return loc
        return None

    def trymove(self, loc):
        if not can_sense_location(loc):
            return False
        sensed = sense_location(loc)
        if sensed.type != RobotType.NONE:
            return False
        if dist(self.location, loc) > self.speed:
            return False
        move(loc)
        return True

    def move_diff(self, diff):
        loc = add(self.location, diff)
        return self.trymove(loc)

    def move_towards(self, loc):
        direction = getdir(self.location, loc)
        totry = [direction, clockwise(direction), counter_clockwise(direction)]
        if random.random() < 0.5:
            totry[1], totry[2] = totry[2], totry[1]
        for test in totry:
            if self.move_diff(test):
                return True
        return False

    def move_away(self, loc):
        direction = getdir(loc, self.location)
        totry = [direction, clockwise(direction), counter_clockwise(direction)]
        if random.random() < 0.5:
            totry[1], totry[2] = totry[2], totry[1]
        for test in totry:
            if self.move_diff(test):
                return True
        return False

    def charge(self):
        self.move_towards(self.enemy_hq_loc)

    def get_enemies(self):
        enemies = []
        sensed = sense()
        for robot in sensed:
            if robot.team != self.team:
                enemies.append(robot)
        return enemies

    def get_allys(self):
        allies = []
        sensed = sense()
        for robot in sensed:
            if robot.team == self.team:
                allies.append(robot)
        return allies

    def get_armed_allys(self):
        allies = []
        sensed = sense()
        for robot in sensed:
            if robot.team == self.team and robot.type in [RobotType.TANK, RobotType.GUNNER, RobotType.GRENADER]:
                allies.append(robot)
        return allies

    def try_attack(self):
        if self.oil < self.attack_cost:
            return False
        enemies = self.get_enemies()
        priority = {
            RobotType.HQ: 6,
            RobotType.GRENADER: 5,
            RobotType.BARRACKS: 4,
            RobotType.REFINERY: 3,
            RobotType.TURRET: 2.5,
            RobotType.GUNNER: 2,
            RobotType.TANK: 1,
        }
        enemies = sorted(enemies, key=lambda e: priority[e.type] if e.type in priority else 0, reverse=True)
        for enemy in enemies:
            if dist(self.location, enemy.location) > self.attack_range:
                continue
            attack(enemy.location)
            return True
        return False


class HQ(Robot):
    def __init__(self):
        super().__init__()
        # write_blockchain([96, 69, self.location[0], self.location[1], 0])
        write_blockchain([96, 69, self.location[0], self.location[1], 0] + [0] * 45)
        self.num_builders = 0.01

    def run(self):
        super().run()
        # REPEAT ATTACK!!!
        if self.round_num > 20:
            add_to_blockchain(get_rogue_block())

        if random.random() < 4 / self.num_builders and self.oil > GameConstants.BUILDER_COST:
            loc = self.trybuild(RobotType.BUILDER)
            if loc:
                self.num_builders += 1
                return


class Builder(Robot):
    def __init__(self):
        super().__init__()
        self.speed = GameConstants.BUILDER_SPEED
        self.sense_range = GameConstants.BUILDER_SENSE_RANGE

    def run(self):
        super().run()

        sucess = False
        buildtype = RobotType.REFINERY if random.random() < 75 / self.round_num else \
            RobotType.BARRACKS if random.random() < 0.9 else RobotType.TURRET
        if self.oil > COSTS[buildtype]:
            loc = self.trybuild2(buildtype)
            sucess = loc is not None
        if not sucess:
            # self.move_away(self.hq_loc)
            if random.random() < 0.95:
                self.move_diff((random.choice([-1, 1]), random.choice([-1, 1])))
            else:
                self.charge()


class Refinery(Robot):
    def __init__(self):
        super().__init__()

    def run(self):
        super().run()


class Turret(Robot):
    def __init__(self):
        super().__init__()
        self.attack_range = GameConstants.TURRET_ATTACK_RANGE
        self.attack_cost = GameConstants.TURRET_ATTACK_COST

    def run(self):
        super().run()
        self.try_attack()


class Barracks(Robot):
    def __init__(self):
        super().__init__()
        self.spawn_sequence = [RobotType.TANK, RobotType.GUNNER, RobotType.GRENADER, RobotType.GUNNER]
        self.spawn_idx = 0

    def run(self):
        super().run()
        next_spawn = self.spawn_sequence[self.spawn_idx]
        if self.oil >= COSTS[next_spawn]:
            loc = self.trybuild(next_spawn)
            if loc:
                self.spawn_idx += 1
                self.spawn_idx %= len(self.spawn_sequence)


class Tank(Robot):
    def __init__(self):
        super().__init__()
        self.speed = GameConstants.TANK_SPEED
        self.attack_range = GameConstants.TANK_ATTACK_RANGE
        self.attack_cost = GameConstants.TANK_ATTACK_COST

    def run(self):
        super().run()
        if self.try_attack():
            return
        if len(self.get_armed_allys()) > 20:
            self.charge()


class Gunner(Robot):
    def __init__(self):
        super().__init__()
        self.speed = GameConstants.GUNNER_SPEED
        self.attack_range = GameConstants.GUNNER_ATTACK_RANGE
        self.attack_cost = GameConstants.GUNNER_ATTACK_COST

        self.protect = random.random() < 0.3

    def run(self):
        super().run()
        if self.try_attack():
            return
        if self.protect and len(self.get_armed_allys()) > 25:
            self.move_towards(self.hq_loc)
        elif len(self.get_armed_allys()) > 10:
            self.charge()


class Grenader(Robot):
    def __init__(self):
        super().__init__()
        self.speed = GameConstants.GRENADER_SPEED
        self.attack_range = GameConstants.GRENADER_STUN_RANGE
        self.attack_cost = GameConstants.GRENADER_STUN_COST

    def run(self):
        super().run()

        if not self.try_attack():
            self.charge()

    def try_attack(self):
        if self.oil < self.attack_cost:
            return False
        enemies = self.get_enemies()
        priority = {
            RobotType.HQ: 6,
            RobotType.GRENADER: 5,
            RobotType.BARRACKS: 4,
            RobotType.REFINERY: 3,
            RobotType.TURRET: 2.5,
            RobotType.GUNNER: 2,
            RobotType.TANK: 1,
        }
        enemies = sorted(enemies, key=lambda e: priority[e.type] if e.type in priority else 0, reverse=True)
        for enemy in enemies:
            if dist(self.location, enemy.location) > self.attack_range:
                continue
            attack(enemy.location)
            return True
        return False


type_to_obj = {
    RobotType.HQ: HQ,
    RobotType.REFINERY: Refinery,
    RobotType.TURRET: Turret,
    RobotType.BARRACKS: Barracks,
    RobotType.BUILDER: Builder,
    RobotType.TANK: Tank,
    RobotType.GUNNER: Gunner,
    RobotType.GRENADER: Grenader,
}

obj = type_to_obj[get_type()]
robot = obj()


def turn():
    robot.run()
