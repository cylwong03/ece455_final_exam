# ECE 455 S2024 Final
# Caitlin Wong
# 20901429

import os
import sys
import math

# Used to control print statements for debugging
DEBUG_LEVEL = 3

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
      self.task_num = int(task_num)
      self.exec_time = float(exec_time)
      self.period = float(period)
      self.deadline = float(deadline)
      self.priority = 1 / float(period)               # Longer period, lower priority

      # Values modified during simulation (dynamic)
      self.exec_time_left = float(exec_time)
      self.time_last_started = float(-1)              # Default value is -1, has not started yet
      self.num_times_run = int(0)
      self.times_preempted = int(0)


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


# Helper function for debugging purposes only - used to print task details
def print_task(task):
  print("task_num:", task.task_num,
        ", exec_time:", task.exec_time,
        ", period:", task.period,
        ", deadline:", task.deadline,
        ", priority:", task.priority,
        ", exec_time_left:", task.exec_time_left,
        ", time_last_started:", task.time_last_started,
        ", num_times_run:", task.num_times_run,
        ", times_preempted:", task.times_preempted)


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
        print("task_num:", index, ", exec_time:", data[0], ", period:", data[1], ", deadline:", data[2])

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
        print_task(x)
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

  # Create a list of "important" timesteps where information must be evaluated
  # Each element is a tuple of [value, type, task_num]
  # The type can be 'R' for a release time, 'D' for a deadline, or 'E' for a completed execution
  # To begin, this includes:
  #     -> release time of each task, up to the hyperperiod (based on the period)
  #     -> deadline of each task, up to the hyperperiod
  # Later, we will add:
  #     -> times when execution is expected to complete
  important_times = []
  for task in task_list:
     # Determining release times
    release_time = 0
    while (release_time < hyperperiod):
      important_time = [release_time, 'R', task.task_num]
      important_times.append(important_time)
      release_time = release_time + task.period

    # Determining deadlines
    deadline_time = task.deadline
    while (deadline_time < hyperperiod):
      important_time = [deadline_time, 'D', task.task_num]
      important_times.append(important_time)
      deadline_time = deadline_time + task.deadline

  # Sort the list of important times by timestep (ascending)
  important_times.sort()

  if DEBUG_LEVEL == 3:
    print(important_times)

  # Set the task number of the currently running task - default is -1
  current_running_task = -1

  # Continue until there are no more times in the list of important timesteps
  while(important_times):

    # Get the next time to be evaluated
    current_time = important_times.pop(0)

    # Get the task object of the task associated with the event
    handle_task = task_list[current_time[2]]
    if DEBUG_LEVEL == 3:
      print_task(handle_task)

    # Check the type to determine what important task happened
    if current_time[1] == 'R':
      # New task has been released
      # If no task currently running, run it
      if current_running_task == -1:
        current_running_task = handle_task.task_num
      # Check if priority of currently running task is lower - preempt if so



    # Sort the list of priorities
    priority_list.sort()
    if DEBUG_LEVEL == 2:
      print(priority_list)


    # # Check the tasks, in order of priority, to see which is ready to execute
    # for priority in priority_list:
    #    current_task_num = priority_task_num_dict[priority]
    #    current_task = task_list[current_task_num]

    #    if DEBUG_LEVEL == 2:
    #       print_task(current_task)


    # Re-sort the list of times
    important_times.sort()

if __name__ == "__main__":
    main()
