#!/usr/bin/env python

import sqlite3
import datetime
import sys

class ToDoneTasks: 
    db = None
    def __init__(self, dbname="database.db"):
        self.db = sqlite3.connect(dbname)
        c = self.db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id integer primary key autoincrement,
                        description text,
                        source text,
                        date datetime
                );''')
        self.db.commit()

    # add a task to the db
    def addTask(self, taskDesc, task_src):
        self.db.execute('''INSERT INTO tasks (description, source, date) VALUES (?, ?, ?);''', (taskDesc, task_src, datetime.datetime.now()))
        self.db.commit()
    
    # get all tasks since a specific date / optionally from a specific source
    def getSince(self, date, source):
        c = self.db.cursor()
        if source is None:
            return c.execute("select * from tasks where date > ?;", (date, ))
        else:
            return c.execute("select * from tasks where date > ? and source=?;", (date, source))



if __name__ == "__main__":
    # parse CLI args
    import argparse
    parser = argparse.ArgumentParser(description="Keep track of the work you're doing as you're doing it.", epilog="Default behavior is to read log messages one line at a time from stdin")
    parser.add_argument('-p', '--print', help="Print all log messages, optionally since a date", nargs="?", metavar="YYYY-MM-DD", const=(datetime.date.today() - datetime.timedelta(days=32)).isoformat(), dest='initial_date')
    parser.add_argument('-s', '--source', help="Specify a source for the completion task, or filter on the source for printing (useful for other automations)")
    args = parser.parse_args()

    # init the database object
    tdt = ToDoneTasks()

    # deal with printing the results back out on the CLI.
    if args.initial_date is not None:
        date = datetime.datetime.strptime(args.initial_date, "%Y-%m-%d")
        lastDate = None
        for log in tdt.getSince(date, args.source):
            id=log[0]
            desc = log[1]
            source = log[2]
            date = datetime.datetime.strptime(log[3], '%Y-%m-%d %H:%M:%S.%f')
            if date.date() != lastDate:
                lastDate = date.date()
                print date.date().strftime("%Y-%m-%d")
                print "=========="
            print "%s (%s) %s" % (date.strftime("%H:%M:%S"), source, desc)


    # deal with adding new completed tasks
    else:
        prompt = "> " if sys.stdin.isatty() else "" 
        try:
            while True:
                task_description =  raw_input(prompt)
                if task_description.strip() != "":
                    tdt.addTask(task_description, args.source if args.source is not None else "cli")
        except KeyboardInterrupt:
            if sys.stdin.isatty():
                print
            pass
        except EOFError:
            if sys.stdin.isatty():
                print
            pass
