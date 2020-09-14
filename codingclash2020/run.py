import os
import argparse
from codingclash2020.supervisor import Supervisor

parser = argparse.ArgumentParser()
parser.add_argument('folders', nargs='+', help='Folder name of the first bot')
parser.add_argument('--max-rounds', default=200, type=int, help='Set the maximum round number')
parser.add_argument('--save', default=None, type=str, help='Save the replay')
parser.add_argument('--map', default='empty', type=str, help='The map for the game to be played on')
args = parser.parse_args()

filename1 = os.path.join(args.folders[0], "bot.py")
filename2 = os.path.join(args.folders[1], "bot.py")

game = Supervisor(filename1, filename2, args.map)

game.run(max_rounds=args.max_rounds)

if args.save:
    replay = game.get_replay()
    with open(args.save, "w+") as file:
        file.write(replay)
    print("Saved")
