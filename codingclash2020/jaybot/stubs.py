from enum import Enum, auto


# Basic getter methods

def get_board_width():
    pass


def get_board_height():
    pass


def get_team():
    pass


def get_type():
    pass


def get_health():
    pass


def get_location():
    pass


def get_oil():
    pass


def get_round_num():
    pass


def is_stunned():
    pass


# Sensing

def sense():
    pass


def sense_radius(radius):
    pass


def can_sense_location(location):
    pass


def sense_location(location):
    pass


# Creating robots

def create(robot_type, location):
    pass


# Robot actions (can only do one per turn)

def move(location):
    pass


def attack(location):
    pass


def stun(location):
    pass


# Blockchain

def add_to_blockchain(data):
    pass


def get_blockchain(round_num):
    pass


# Logging

def dlog(message):
    pass


class GameConstants:
    """
    Notes
    Ranges are in euclidian distance
    """

    # General constants
    TIME_LIMIT = 0.1

    # Navigation constants
    MOVEMENT_SPEED = 2

    ## Buildings

    # HQ constants
    HQ_HEALTH = 200
    HQ_MAX_SPAWNS = 1
    HQ_SENSE_RANGE = 36
    HQ_SPAWN_RADIUS = 2
    HQ_OIL_PRODUCTION = 8

    # Refinery constants
    REFINERY_HEALTH = 50
    REFINERY_COST = 40
    REFINERY_PRODUCTION = 5
    REFINERY_SENSE_RANGE = 25

    # Turrets constants
    TURRET_HEALTH = 50
    TURRET_COST = 15
    TURRET_DAMAGE = 10
    TURRET_ATTACK_COST = 3
    TURRET_ATTACK_RANGE = 13
    TURRET_SENSE_RANGE = 25
    TURRET_AOE = 0

    # Barracks constants
    BARRACKS_HEALTH = 50
    BARRACKS_COST = 25
    BARRACKS_MAX_SPAWNS = 3
    BARRACKS_SPAWN_RADIUS = 2
    BARRACKS_SENSE_RANGE = 8

    # Walls constants
    WALL_HEALTH = 20
    WALL_COST = 2

    ## Troops constants

    # Builders constants
    BUILDER_HEALTH = 75
    BUILDER_COST = 10
    BUILDER_SPAWN_RADIUS = 2
    BUILDER_MAX_SPAWNS = 1
    BUILDER_SPEED = 8
    BUILDER_SENSE_RANGE = 20

    # Tank constants
    TANK_HEALTH = 75
    TANK_COST = 10
    TANK_DAMAGE = 30
    TANK_ATTACK_COST = 5
    TANK_ATTACK_RANGE = 2
    TANK_SPEED = 2
    TANK_SENSE_RANGE = 25
    TANK_AOE = 0

    # Gunner constants
    GUNNER_HEALTH = 20
    GUNNER_COST = 5
    GUNNER_DAMAGE = 10
    GUNNER_ATTACK_COST = 2
    GUNNER_ATTACK_RANGE = 5
    GUNNER_SPEED = 2
    GUNNER_SENSE_RANGE = 36
    GUNNER_AOE = 0

    # Grenade launcher constants
    GRENADER_HEALTH = 10
    GRENADER_COST = 5
    GRENADER_SPEED = 2
    GRENADER_SENSE_RANGE = 25
    # Stun grenade constants
    GRENADER_STUN_TURNS = 2
    GRENADER_STUN_COST = 10
    GRENADER_STUN_AOE = 2
    GRENADER_STUN_RANGE = 5
    # Damage grenade constants
    GRENADER_DAMAGE_COST = 4
    GRENADER_DAMAGE_AOE = 2
    GRENADER_DAMAGE_DAMAGE = 8
    GRENADER_DAMAGE_RANGE = 5

    # Blockchain constants
    BLOCKCHAIN_BYTE_COUNT = 3
    BLOCKCHAIN_MIN_NUM_SIZE = 0
    BLOCKCHAIN_MAX_NUM_SIZE = 255


class RobotType(Enum):
    NONE = None
    HQ = auto()
    REFINERY = auto()
    TURRET = auto()
    BARRACKS = auto()
    BUILDER = auto()
    TANK = auto()
    GUNNER = auto()
    GRENADER = auto()
    WALL = auto()


class TeamColor(Enum):
    RED = auto()
    BLUE = auto()
