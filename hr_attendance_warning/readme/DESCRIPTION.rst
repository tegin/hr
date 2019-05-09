This module allows you to get warnings when there are
inconsistencies between the theoric check in time of an employee
and what has happened.

Every time there is a check_in or a check_out the module checks whether
it is inside the employee's working time or not and creates a warning if it's
not.

It also testes the opposite case, and employee not comming to work at expected
time. A cron is executed every 5 minutes checking resource.calendar.attendaces
and checks if every employee related to it has done what it was expected.
