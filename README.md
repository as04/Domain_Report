# Domain_Report

This python application pings each domain in the list (given in a text file), record its IP address and average latency to reach the domain. This is done by workers of thread pool executor.

* Worker thread which executed ping stores the details of each domain in a Redis hash data structure.

* Once all the details are fetched for all domains, program cleanly shutdown workers and close any file that was opened. 

* Program then collects summary of the whole work by reading from Redis and write a summary report with below details to a text file:
    a. Domain name that had highest average ping latency
    b. Domain name that had lowest average ping latency
    c. Total number of domain names pinged
    d. Total number of domain names which responded for ping
    e. Total number of domain names that did not respond for ping
    f.  Total number of domain names that had average ping latency < 10ms
    g. Total number of class A, B, C, D addresses collected

The script also generate half built reports in case of *keyboard interrupts*.

Basic Requirements includes *Python3, Redis, PIP, Python3 venv*. You should also have the *text file* of list of domains or adjust the code accordingly to read the domains.

Steps are as follows:
1. Create a python3 environment:
```
	python3 -m venv env
```

2. Activate the virtual environment:
```
	source env/bin/activate
```

3. Install the dependencies from the requirement.txt:
```
	pip install -r requirement.txt
```

4. Change the worker threads according to your need. 

7. Run the Script:
```
	python script.py
```
