# ECE 455 S2024 Final
# Caitlin Wong
# 20901429

import os
import sys
import math

# Used to control print statements for debugging
DEBUG_LEVEL = 2

# List of task objects - note that index corresponds to task number
task_list = []

# List of all priorities for easy sorting - index does NOT correspond to task number
priority_list = []

# Dictionary mapping of task priority to task number, for efficient lookup
priority_task_num_dict = {}

# Task class
class Task:
    def __init__(self, task_num, exec_time, period, deadline):
      # Values initialized at creation (constants)
      self.task_num = float(task_num)
      self.exec_time = float(exec_time)
      self.period = float(period)
      self.deadline = float(deadline)
      self.priority = 1 / float(period)               # Longer period, lower priority

      # Values modified during simulation (dynamic)
      self.exec_time_left = exec_time


# Validate argument input
# Returns true (arguments are good) or false (error with arguments)
def check_args():
    if len(sys.argv) < 2:
      print("Argument Error: Missing parameter of input file name.")
      return False

    if not sys.argv[1].lower().endswith('.txt'):
      print("Argument Error: Input file must be a txt.")
      return False

    return True


# Helper function to get LCM from a list, used to identify hyperperiod
# Returns an integer value of the LCM
def get_lcm(periods):

    # Need to convert floats to ints - since max. precision is 3 decimals, we multiply by 1000
    int_periods = []
    for period in periods:
      int_periods.append(int(period * 1000))

    ret = 1
    for int_period in int_periods:
      ret = (ret * int_period) // (math.gcd(ret, int_period))

    # Convert back to original value by dividing by 1000; keep as int
    ret = ret // 1000

    return ret


# Read the input file
# Returns a list of Task items
def read_input():
    tasks = []

    # Attempts to open the input file
    try:
      file = open(sys.argv[1], 'r')
    except:
      print("File Error: Input file does not exist or cannot be opened.")
      return tasks

    # Reads the input file line by line
    lines = file.readlines()
    for index, line in enumerate(lines):
      if DEBUG_LEVEL == 1:
        print(line)
      data = line.rstrip().split(',')

      # Check that all the parameters are present
      if len(data) < 3:
         print("Data Error: Missing task parameter.")
         tasks.clear()
         return tasks

      # Check that all the parameters are integer/float values
      for param in data:
        try:
          float(param)
        except:
          print("Value Error: Task parameter is not an integer or float.")
          tasks.clear()
          return tasks

      if DEBUG_LEVEL == 1:
        print("task_num:", index, "exec_time:", data[0], ", period:", data[1], ", deadline:", data[2])

      # Adds each line as a new Task object to the list of tasks to be returned
      task = Task(index, data[0], data[1], data[2])
      # Adds the task object to the list of all tasks to be returned
      tasks.append(task)
      # Adds the task number and its object details to the dictionary
      task_list.append(task)
      # Adds the task priority and its number to the dictionary
      priority_task_num_dict[task.priority] = task.task_num
      # Adds the task priority to the list of all priorities
      priority_list.append(task.priority)

    if DEBUG_LEVEL == 1:
      for x in task_list:
        print(x.task_num, x.exec_time, x.period, x.deadline, x.priority)
      for x in priority_task_num_dict.keys():
        print(x, ":", priority_task_num_dict[x])

    return tasks


def main():
  print("Running main.")
  # Return if args are incorrect
  if not check_args():
     return

  read_input()
  # Return if task list is empty
  if not task_list:
     return

  # Determine the hyperperiod of the schedule
  # Get a list of all the periods
  periods = []
  for task in task_list:
     periods.append(task.period)

  # Call helper function to get LCM
  hyperperiod = get_lcm(periods)
  if DEBUG_LEVEL == 2:
     print(hyperperiod)

  # Repeat for every timestep until the hyperperiod
  for timestep in range(hyperperiod):

    # Sort the list of priorities
    priority_list.sort()
    if DEBUG_LEVEL == 2:
      print(priority_list)


if __name__ == "__main__":
    main()
