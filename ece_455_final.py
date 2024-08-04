# ECE 455 S2024 Final
# Caitlin Wong
# 20901429

import sys
import math

# Note that by convention, priority is determined by the LOWER VALUE
# (lower value = higher priority)

# Used to control print statements for debugging
DEBUG_LEVEL = 5

# List of task objects - note that index corresponds to task number
task_list = []

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
      self.priority = float(period)               # Longer period, lower priority

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

    if DEBUG_LEVEL == 1:
      for x in task_list:
        print_task(x)
      for x in priority_task_num_dict.keys():
        print(x, ":", priority_task_num_dict[x])

    return tasks


def RM_simulation():
  print("Running simulation.")
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
  if DEBUG_LEVEL == 4:
     print(hyperperiod)

  # Create a list of "important" timesteps where information must be evaluated
  # Each element is a tuple of [value, type, task_num]
  # The type can be 0 for a completed execution, 1 for a released task, or 2 for a deadline
  #     -> this helps enforce ordering - we want to evaluate, in order, execution tasks, release tasks, deadline tasks
  # To begin, this includes:
  #     -> release time of each task, up to the hyperperiod (based on the period)
  #     -> deadline of each task, up to the hyperperiod
  # Later, we will add:
  #     -> times when execution is expected to complete
  important_times = []

  type_dict = {
    "E" : 0,
    "R" : 1,
    "D" : 2
  }

  for task in task_list:
     # Determining release times
    release_time = 0
    while (release_time < hyperperiod):
      important_time = [release_time, type_dict["R"], task.task_num]
      important_times.append(important_time)

      # Add a deadline for every release time
      important_time = [release_time + task.deadline, type_dict["D"], task.task_num]
      important_times.append(important_time)

      # Increment release time
      release_time = release_time + task.period

  # Sort the list of important times by timestep (ascending)
  important_times.sort()

  if DEBUG_LEVEL == 3:
    print(important_times)

  # Set the task number of the currently running task - default is -1
  current_running_task = -1

  # Create the queue of tasks waiting to run
  # Holds tuples of [priority, task_num]
  queue = []

  # Continue until there are no more times in the list of important timesteps
  while(important_times):

    # Get the next time to be evaluated
    current_time_tuple = important_times.pop(0)

    if DEBUG_LEVEL == 4:
      print("currently evaluating timestep: ", current_time_tuple)

    # Get the task object of the task associated with the event
    handle_task_num = current_time_tuple[2]
    handle_task = task_list[handle_task_num]
    if DEBUG_LEVEL == 3:
      print_task(handle_task)

    # Check the type to determine what important task happened
    # New task has been released
    if current_time_tuple[1] == type_dict["R"]:

      # If no task currently running, run it
      if current_running_task == -1:
        # Update the variables of the task that is about to run
        task_list[handle_task_num].exec_time_left = handle_task.exec_time
        task_list[handle_task_num].time_last_started = current_time_tuple[0]

        # Add the completion time of the newly running task to the list of important times
        important_times.append([current_time_tuple[0] + task_list[handle_task_num].exec_time, type_dict["E"], handle_task_num])

        if DEBUG_LEVEL == 4:
          print(handle_task_num, "started running, instance", task_list[handle_task_num].num_times_run)

        # Update the currently running task
        current_running_task = handle_task_num

      # If the task currently running is the same task, add to queue
      elif current_running_task == handle_task_num:
        queue.append([handle_task.priority, handle_task_num])

        if DEBUG_LEVEL == 4:
          print(handle_task_num, "added to queue")

      # Check if priority of currently running task is higher (lower) - add incoming to queue if so
      elif task_list[current_running_task].priority < handle_task.priority:
        queue.append([handle_task.priority, handle_task_num])

        if DEBUG_LEVEL == 4:
          print(handle_task_num, "added to queue")

      # Check if priority of currently running task is equal and if number is higher priority (lower) - add to queue if so
      elif (task_list[current_running_task].priority == handle_task.priority
            and current_running_task < handle_task_num):
        queue.append([handle_task.priority, handle_task_num])

        if DEBUG_LEVEL == 4:
          print(handle_task_num, "added to queue")

      # Otherwise (priority of currently running task is lower (higher) or priority is equal and task number is lower (higher)), preempt
      else:
        # Update the variables of the task to be preempted
        # -> if the task was started in the same time step, no need to update anything, since we do not consider this a proper preemption
        if not (task_list[current_running_task].time_last_started == current_time_tuple[0]):
          task_list[current_running_task].times_preempted = task_list[current_running_task].times_preempted + 1

          if DEBUG_LEVEL == 4:
            print(current_running_task, "preempted by", handle_task_num)

        time_executed = current_time_tuple[0] - task_list[current_running_task].time_last_started
        task_list[current_running_task].exec_time_left = task_list[current_running_task].exec_time_left - time_executed

        # If the task to be preempted has not finished:
        if task_list[current_running_task].exec_time_left > 0:
          # Add it to the waiting queue
          queue_item = [task_list[current_running_task].priority, current_running_task]
          queue.append(queue_item)

          if DEBUG_LEVEL == 4:
            print(current_running_task, "added to queue with", task_list[current_running_task].exec_time - time_executed, "time left")

          # Remove its expected completed execution time (will be recalculated when it starts again)
          removal_idx = -1
          for time_tuple in important_times:
            if (time_tuple[1] == type_dict["E"] and time_tuple[2] == current_running_task):
              removal_idx = important_times.index(time_tuple)
              break
          if not removal_idx == -1:
            popped = important_times.pop(removal_idx)

            if DEBUG_LEVEL == 4:
              print(current_running_task, "expected execution time of", popped[0], "removed due to preemption")

        # Update the variables of the task that is preempting
        task_list[handle_task_num].exec_time_left = handle_task.exec_time
        task_list[handle_task_num].time_last_started = current_time_tuple[0]

        # Add the completion time of the newly running task to the list of important times
        important_times.append([current_time_tuple[0] + handle_task.exec_time, type_dict["E"], handle_task_num])

        # Update the currently running task
        current_running_task = handle_task_num

        if DEBUG_LEVEL == 4:
          print(handle_task_num, "started running, instance", task_list[handle_task_num].num_times_run)

    # Task has completed execution AND it's the currently running task (ignore otherwise, it has been preempted)
    elif current_time_tuple[1] == type_dict["E"] and handle_task_num == current_running_task:

      if DEBUG_LEVEL == 4:
          print(handle_task_num, "finished execution, instance", task_list[handle_task_num].num_times_run + 1)

      # If a task has finished executing, but the hyperperiod is over, return unscheduleable
      if current_time_tuple[0] > hyperperiod:
        return 0

      # Update the variables of the task that finished executing
      task_list[handle_task_num].exec_time_left = task_list[handle_task_num].exec_time
      task_list[handle_task_num].time_last_started = -1
      task_list[handle_task_num].num_times_run = task_list[handle_task_num].num_times_run + 1

      # If the queue is empty, set currently running task to -1
      if not queue:
        current_running_task = -1

        if DEBUG_LEVEL == 4:
          print("queue empty, processor idle")

      # Otherwise, get the next task from the queue
      else:

        if DEBUG_LEVEL == 4:
          print("queue:", queue)

        next_task_tuple = queue.pop(0)
        next_task_num = next_task_tuple[1]

        # Update the variables of the next task to run
        # -> we do not update exec_time_left since this task may have already executed for a bit
        task_list[next_task_num].time_last_started = current_time_tuple[0]

        # Add the completion time of the task to run to the list of important times
        important_times.append([current_time_tuple[0] + task_list[next_task_num].exec_time_left, type_dict["E"], next_task_num])

        # Update the currently running task
        current_running_task = next_task_num

        if DEBUG_LEVEL == 4:
          print(current_running_task, "started running, instance", task_list[next_task_num].num_times_run)

    # Task deadline reached
    elif current_time_tuple[1] == type_dict["D"]:

      # Check which deadline this is by subtracting to get the corresponding release time,
      # then set to 0 if 0 or take floor(current_time/release_time)
      corresponding_release_time = current_time_tuple[0] - task_list[handle_task_num].deadline
      if corresponding_release_time == 0:
        deadline_num = 0
      else:
        deadline_num = current_time_tuple[0] // corresponding_release_time

      if DEBUG_LEVEL == 4:
          print(handle_task_num, "deadline reached, instance", deadline_num)

      # Compare with the number of times this task has run
      # -> if the task has not completed the same number of times this deadline has passed,
      # -> immediately return that the workload is unscheduleable
      if deadline_num > task_list[handle_task_num].num_times_run:

        if DEBUG_LEVEL == 4:
          print(handle_task_num, "missed its deadline - ran", task_list[handle_task_num].num_times_run,
                "times, expected", deadline_num)

        return 0

      if DEBUG_LEVEL == 4:
          print(handle_task_num, "met its deadline")

    # Sort the priority queue
    queue.sort()

    # Sort the list of times
    important_times.sort()

  # The simulation has finished running and no tasks missed their deadlines
  # Return the number of times each task was preempted
  return_tuple = []
  for task in task_list:
    return_tuple.append(str(task.times_preempted))

  return [1, return_tuple]

if __name__ == "__main__":

    ret = RM_simulation()

    if ret:
      print("1")
      print(','.join(ret[1]))
    else:
      print("0")
      print("")

