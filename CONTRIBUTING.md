# Contributing to this project
Please read this section very carefully and keep the content of it in your
mind. This document outlines how we should work together. With rules outlined
in this document we guarantee higher efficiency in completing our tasks.

## Organizational structure
We divided our group into teams that have various tasks. Each team has exactly
one supervisor who is responsible for 
- organizing/assign tasks,
- checking the validity of the API,
- document API for other teams to better understand,
- merge branches
- hold milestone talks.
- (might implement some small features or bug fixes)
If needed the supervisor is also in charge of dividing the team into sub teams.

Important issues are only discussed with the least amount of people who are 
required for the meeting (e.g. one representative of each team, subgroup, ...). 
This makes sure that meetings that are synchronous meetings are 
- more easily scheduable, 
- short (not too many people not understanding an issue) and 
- clear.

## Branching
Troughout the project the main branch should always be deployable. Therefore
it's not allowed to push to the main branch. Supervisors should make sure 
that code that gets modified for an issue (at the same time) has a minimal 
amount of collision. This makes merging less painful. If a supervisor 
assigns a task to you then it should be somehow indicated either which 
branch should be used or the branch is already created. 

__Note__: Unfortunately I couldn't setup the protection of the main branch 
or rather it's enforcement. Otherwise we would need to go public or upgrade our 
organization subscription. Since we might store sensitive information in our
repository or database (and might not be aware of some security threads) 
we wouldn't others to access the code.

## Pull requests
If you want a branch to be merged, tell your supervisor. They will make 
sure that the changes are properly reviewed and then merge the branch 
into main (or another branch). In order to do it assign pull request to
your supervisor and set the other parameters of the pull request accordingly.
After the branch has been pulled the supervisor might decide to delete the
branch that has been pulled.

## Coding conventions
We use the standard conventions for python in order to guarantee more readable
and maintainable code. In case there are some projects that do not use this
convention you may refactor it or use tools to align them with the coding 
convention below. So before you start you should read:
1. [pep20](https://peps.python.org/pep-0020/): Short general principles of
the coding style.
2. [pep8](https://peps.python.org/pep-0008/): This is a style guide for 
python. That puts more specific rules and suggestions in place for python
coding. I heavily suggest you to program after those recommendations.
3. [pep257](https://peps.python.org/pep-0257/): Those are docstring 
conventions. This is required for those who will write the documentation
for the interface (so essentially the team/subgroup supervisors), but 
optional for everyone else.
4. [pep3107](https://peps.python.org/pep-3107/): This talks about adding
meta information for the functions. This is required for those who will write 
the documentation for the interface (so essentially the team/subgroup 
supervisors), but optional for everyone else.
