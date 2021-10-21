# First time setup instructions:

0. Make sure that you have enabled [firewall settings](https://sites.duke.edu/compsci316_01_f2021/creating-and-running-vm-on-google-cloud/) for port 5000. 

1. Clone this repo. Confirm with the team which branch you should be on for up to date behavior.

2. Upgrade pip if necessary, and run `pip install virtualenv`

3. Run `./install.sh`. If there are errors, address them.

4. Run `source env/bin/activate`

5. Run `flask run`

At this point, you can then access the database by running `psql pikachooze` from another terminal, and you can access the WebUI by navigating to the IP address and appending `:5000` to the URL. 

3. In your VM, move into the repository directory and then run `./install.sh`.
   This will install a bunch of things, set up an important file called `.flashenv`, and creates a simple PostgreSQL database named `amazon`.

Flask and SQLAlchemy will hot deploy most of your changes, but if an unusual problem arises, you can always do a hard reset by running:

1. `dropdb pikachooze` (make sure that any active `psql` connections have been terminated)

2. `flask run`

# Updating Loads

TODO: Add quick load functionality. For now, see Troubleshooting Changes.

# Stopping

To stop your website, simply press <kbd>Ctrl</kbd><kbd>C</kbd> in the VM shell where flask is running.
You can then deactivate the environment using
```
deactivate
```

# Credits

Based on skeleton code for the CompSci 316 undergraduate course project.
Created by [Rickard Stureborg](http://www.rickard.stureborg.com) and [Yihao Hu](https://www.linkedin.com/in/yihaoh/).

# Useful Tips

You can randomly generate passwords with this tool: https://www.lastpass.com/password-generator

## Fixes and tips
If weird things happen, run 'dropdb pikachooze' and then 'flask run'. If you want to run sql queries, use 'psql pikachooze'. If you can't run 'source env/bin/activate', try upgrading pip and running 'pip install virtualenv'.
