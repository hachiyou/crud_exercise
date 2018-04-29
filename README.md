# CRUD with HTML exercise

Build a simple database and use Python to perform CRUD operations

## Getting Started

### Prerequisites

Since I wrote this in windows 10, all the software are windows based.  
The required softwares are:

1. [Python 3.6.5](https://wiki.python.org/moin/BeginnersGuide/Download)
2. [Vagrant 2.0.4](https://www.vagrantup.com/downloads.html)
3. [Virtual Box 5.2](https://www.virtualbox.org/wiki/Downloads)
4. [Git Bash](https://git-scm.com/downloads)

### Installation & Setup

1. Download and install all the required software.
2. Download the zip file from <https://github.com/udacity/fullstack-nanodegree-vm> and extract the zip file.
3. Navigate to this folder in Bash using `cd`. Change directory to <b>vagrant</b>
4. Run the command `vagrant up` to download the linux box, run command `vagrant ssh` after successful installation of linux.
5. Anytime after should you want to invoke vagrant, you just have to run the command `vagrant ssh` under the directory vagrant.
5. Download the files in this repository, unzip and place this folder under vagrant.
6. Run the command `python database_setup.py`, a new database will be setup for you.
7. You can download lotsofmenus.py file from <https://github.com/udacity/Full-Stack-Foundations/blob/master/Lesson_1/lotsofmenus.py> to populate the database, or create entries on your own.
8. Using bash, run the command 'python webserver.py', then use any web browser to access <http://localhost:8080/restaurant> to get started.


## Built With

* Python 3.6.5
