# Exercise 01 — Terminal scavenger hunt

Use **only the terminal**: no file browser, no editor. Write down the command you used for each step.

1. Print the full path of your home folder.
2. Go to the handbook repository. Print the path you're in.
3. List every file in the repository root, **including hidden ones**. What hidden folder is there, and what is it for?
4. Find every `.md` file in `modules/` whose name contains `field-track`. How many are there?
5. Find the line in the whole repository that contains the text `APP_PORT`. Which file(s) and line numbers?
6. Create the folders `~/fde-practice/m02/notes` in **one** command.
7. Copy `leads_sample.csv` into `~/fde-practice/m02/` and rename the copy to `leads.csv`.
8. Show the permissions of `leads.csv`. Remove read permission for "others". Show them again.
9. Write the text `Module 02 started` into `~/fde-practice/m02/notes/log.txt`. Then **append** today's date (use the `date` command) to the same file without overwriting it.
10. Start `python3 -m http.server 8123` in the background. Find its process ID with `ps`. Stop it with `kill`. Confirm it's gone.
11. Delete `~/fde-practice/m02/leads.csv`, but first prove (with `ls`) exactly what you're about to delete.

**Bonus:** press <kbd>Ctrl</kbd>+<kbd>R</kbd> and find the `mkdir` command from step 6 in your history without retyping it.
