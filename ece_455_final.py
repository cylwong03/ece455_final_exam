# ECE 455 S2024 Final
# Caitlin Wong
# 20901429

import os
import sys

# Used to control print statements for debugging
DEBUG_LEVEL = 0

# Task class
class Task:
    def __init__(self, exec_time, period, deadline):
      self.exec_time = exec_time
      self.period = period
      self.deadline = deadline


# Validate argument input
def check_args():
    if len(sys.argv) < 2:
      print("Argument Error: Missing parameter of input file name.")
      return

    if not sys.argv[1].lower().endswith('.txt'):
      print("Argument Error: Input file must be a txt.")
      return


# Read the input file
# Returns a list of Task items
def read_input():
    tasks = []

    try:
      file = open(sys.argv[1], 'r')
    except:
      print("File Error: Input file does not exist or cannot be opened.")
      return tasks

    lines = file.readlines()
    for line in lines:
      if DEBUG_LEVEL == 0:
        print(line)
      data = line.rstrip().split(',')

      if len(data) < 3:
         print("Data Error: Missing task parameter.")
         tasks.clear()
         return tasks

      if DEBUG_LEVEL == 0:
        print("exec_time:", data[0], ", period:", data[1], ", deadline:", data[2])

      task = Task(data[0], data[1], data[2])
      tasks.append(task)

    return tasks

def main():
  print("Running main.")
  check_args()
  read_input()

if __name__ == "__main__":
    main()
