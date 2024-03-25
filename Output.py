from termcolor import colored
import config



def print_execution_time(execution_time):
    if execution_time < config.HIGH_SPEED:
        print(colored(f"Average execution time: {execution_time} seconds", 'green'))
    elif execution_time < config.MIDDLING_SPEED:
        print(colored(f"Average execution time: {execution_time} seconds", 'yellow'))
    elif execution_time > config.MIDDLING_SPEED:
        print(colored(f"Average execution time: {execution_time} seconds", 'red'))