"Checks" is a folder filled with checks for system health that are ran by "Doctor."
This readme is meant for project contributors. (If it gets any. If it does, thank you for your help)

No plugin registration is needed, you simply create a python file to the following specifications below and it'll automatically begin running
that check on restart.

# Format
The correct format to create another check is as follows:
0. A File in "(project root)/checks" with an optional sub-directory ONE sub-directory deep at maximum.
1. A function called "check" in a file named anything, which takes no arguments.
2. A Variable in the file named "DISPLAY_NAME", which is a string.
3. Function "check" returns True if healthy/passed.
4. Function "check" returns False if unhealthy/failed, with an optional message/detal. (add message/detail by returning two values in a tuple)
5. Must contain a "LEVEL" INT Flag.

## The display name
The display name is just what the check is called in the summary report.
Name it anything, ideally something that tells the user exactly what its checking. Eg, "Extended-session check" 

## The level flag
The level flag indicates how nit-picky the check is.
So for example, a check that indicates if the Kernel is tainted would be very nitpicky.
Why? Because something as simple as proprietry nvidia drivers taint the kernel. But, of course, those don't cause problems (normally)

The recommended levels, in descending priority, are:
1. Red-flags (things like "Kernel panic", "The BIOS is missing", "The CPU is currently reading 945 degrees celcius.")
2. Orange-flags (things like "Systems been running for a long time")
3. Yellow-flags (Things like "Packages could use an update")
4. Green-flags (This is where "Kernel tainted" is)

# What about "Severities"?
Doctor is meant to be a basic system for predicting failures and providing accurate health diagnostics so you know where to look to fix stuff.
A "100% Severe" counter would not fit this purpose. Its not meant to have much intricacy by default, if you need to determine how severe something is, you make multiple checks. For example, 2 checks. One is "Storage 80% consumed, consider clearing some storage soon" and a second for "Storage 95% consumed, clear out space now!"

If you wanted to mod in such a percentages system, it could probably be done with relative ease. But I won't be doing that unless it proves exceptionally useful.

# The Optional detail.
Certain times checks need to provide more information than "Did not pass", such as for "a drive is failing." Knowing a drive is failing is good, but what's even better? Knowing WHICH drive is failing. This detail will be provided as the full message detailing what's wrong in the summary report. So do not have it just be
"/dev/sda" have it be "/dev/sda has reported its worn down by 95%, replace it immediately."

Proper conventions for a detail is:
"(Problem), (Solution)"

Details can only be added on a check not passing.

# Multi-checks
In the case that a check checks multiple things at once, and therefore needs to potentially return multiple values, a list of tuples is expected. Each tuple is expected to be (False, Not optional Detail)

Details are not optional on multi-check checks as it can lead to confusion