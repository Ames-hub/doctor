# Tasks
Tasks are scripts Doctor needs to run in order to check health performance

# Format
Tasks are formatted as such:
- A python file, optionally in a sub-folder in tasks folder.
- A function in the file named "task" which takes no arguments.
- A Variable named "CLOCK" equalling a datetime.timedelta object that specifies the time delta required in-between individual runs of a task.
- a variable named "TASK_ID" which is any unique string. (Cannot duplicate another task's id. Recommend using a uuid4)