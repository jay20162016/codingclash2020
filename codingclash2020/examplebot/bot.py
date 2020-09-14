import math

from .stubs import *

# * Blockchain constants
TEAM_KEY = 100 if get_team() == TeamColor.RED else 200

# Purposes
HQ_LOCATION = 1
BUILDER_BUILT = 2
REFINERY_BUILT = 3
BARRACKS_BUILT = 4
SAVE_OIL = 5

# * Game stuff
COSTS = {
    RobotType.GUNNER: GameConstants.GUNNER_COST,
    RobotType.TANK: GameConstants.TANK_COST,
}


def add(loc1, loc2):
    return loc1[0] + loc2[0], loc1[1] + loc2[1]


def sub(loc1, loc2):
    return loc1[0] - loc2[0], loc1[1] - loc2[1]


def dist(loc1, loc2):
    return (loc2[0] - loc1[0]) ** 2 + (loc2[1] - loc1[1]) ** 2


def inbounds(a, b):
    return 0 <= a < get_board_width() and 0 <= b < get_board_height()


def filter_blockchain(round_num):
    blocks = get_blockchain(round_num)
    valid = []
    for b in blocks:
        if b[0] == TEAM_KEY:
            valid.append(b)
    return valid


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
        self.building_locs = {
            RobotType.BARRACKS: set(),
            RobotType.REFINERY: set(),
            RobotType.TURRET: set()
        }

    def parse_blockchain(self):
        if self.round_num == 0:
            return
        blocks = filter_blockchain(self.round_num - 1)
        for block in blocks:
            if block[1] == REFINERY_BUILT:
                loc = (block[2], block[3])
                self.building_locs[RobotType.REFINERY].add(loc)
            elif block[1] == BARRACKS_BUILT:
                loc = (block[2], block[3])
                self.building_locs[RobotType.BARRACKS].add(loc)
            elif block[1] == SAVE_OIL:
                self.saving = True

    def run(self):
        self.saving = False
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
                if loc in exceptions:
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
        for test in totry:
            if self.move_diff(test):
                return True
        return False

    def move_away(self, loc):
        direction = getdir(loc, self.location)
        totry = [direction, clockwise(direction), counter_clockwise(direction)]
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

    def send_saving_message(self):
        add_to_blockchain([TEAM_KEY, SAVE_OIL, 0, 0, 0])

    def try_attack(self):
        if self.oil < self.attack_cost:
            if dist(self.location, self.enemy_hq_loc) <= self.attack_range:
                self.send_saving_message()
            return False
        enemies = self.get_enemies()
        priority = {
            RobotType.HQ: 6,
            RobotType.GRENADER: 5,
            RobotType.BARRACKS: 4,
            RobotType.REFINERY: 3,
            RobotType.GUNNER: 2,
            RobotType.TANK: 1,
        }
        enemies = sorted(enemies, key=lambda e: priority[e.type] if e.type in priority else 0, reverse=True)
        for enemy in enemies:
            if dist(self.location, enemy.location) > self.attack_range:
                continue
            if not self.saving or enemy.type == RobotType.HQ:
                attack(enemy.location)
            return True
        return False


class HQ(Robot):

    def __init__(self):
        super().__init__()
        add_to_blockchain([TEAM_KEY, HQ_LOCATION, self.location[0], self.location[1], 0])
        self.num_builders = 0
        self.max_builders = 1

    def run(self):
        super().run()
        if self.num_builders < self.max_builders:
            if self.oil > GameConstants.BUILDER_COST:
                loc = self.trybuild(RobotType.BUILDER)
                if loc:
                    add_to_blockchain([TEAM_KEY, BUILDER_BUILT, loc[0], loc[1], self.num_builders])
                    self.num_builders += 1
                    return


class Builder(Robot):

    def __init__(self):
        super().__init__()
        self.speed = GameConstants.BUILDER_SPEED
        self.sense_range = GameConstants.BUILDER_SENSE_RANGE
        chain = filter_blockchain(self.round_num - 1)
        assert (len(chain) > 0)
        self.purpose_map = {0: "R", 1: "B", 2: "R", 3: "B"}
        self.purpose = "R"
        self.refineries = 0
        self.barracks = 0
        self.max_refineries = 2
        self.max_barracks = 2

    def run(self):
        super().run()
        if self.refineries >= self.max_refineries and self.barracks >= self.max_barracks:
            return
        if self.purpose == "R":
            if self.oil > GameConstants.REFINERY_COST:
                loc = self.trybuild(RobotType.REFINERY)
                if loc:
                    add_to_blockchain([TEAM_KEY, REFINERY_BUILT, loc[0], loc[1], self.refineries])
                    self.refineries += 1
                    self.purpose = "B"
        elif self.purpose == "B":
            if self.oil > GameConstants.BARRACKS_COST:
                loc = self.trybuild(RobotType.BARRACKS)
                if loc:
                    add_to_blockchain([TEAM_KEY, BARRACKS_BUILT, loc[0], loc[1], self.barracks])
                    self.barracks += 1
                    self.purpose = "R"


class Refinery(Robot):
    def __init__(self):
        super().__init__()

    def run(self):
        super().run()


class Barracks(Robot):
    def __init__(self):
        super().__init__()
        self.spawn_sequence = [RobotType.TANK, RobotType.TANK, RobotType.GUNNER, RobotType.GUNNER, RobotType.GUNNER]
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
        if self.round_num > 100:
            self.charge()


class Gunner(Robot):
    def __init__(self):
        super().__init__()
        self.speed = GameConstants.GUNNER_SPEED
        self.attack_range = GameConstants.GUNNER_ATTACK_RANGE
        self.attack_cost = GameConstants.GUNNER_ATTACK_COST

    def run(self):
        super().run()
        if self.try_attack():
            return
        if self.round_num > 100:
            self.charge()


type_to_obj = {
    RobotType.HQ: HQ,
    RobotType.BUILDER: Builder,
    RobotType.REFINERY: Refinery,
    RobotType.BARRACKS: Barracks,
    RobotType.TANK: Tank,
    RobotType.GUNNER: Gunner
}

obj = type_to_obj[get_type()]
robot = obj()


def turn():
    robot.run()
