Dependencies
============
You will need a reachable redis server in addition to the python dependencies.

Python Dependencies
-------------------
Dependencies are listed in ``requirements.txt``.  The recommended
method for installation is to use virtualenv_.

Install virtualenv, usually this is installed system wide, you may want to use
your systems package manager to install this instead of pip::

	sudo pip install virtualenv

Create a new prefix to hold the libraries, this prefix directory will be
filled with you current version of python and the standard library::

	prefix="$HOME/usr/timeline"
	virtualenv "$prefix"

Activate the prefix, this prepends the prefix to your `PATH` so when you
execute `python` it will run the version in your prefix using the libraries in
your prefix.  Activating will also make pip install to the prefix.  You will
also want to add the top of the smartstories repo to your ``PYTHONPATH``::

	. "$prefix/bin/activate"
	cd "$repo-toplevel"
	export PYTHONPATH="$(pwd):$PYTHONPATH"

Some of the libraries are extension modules and require a working compiler or
existing libraries, do the right thing for your platform here::

    root@debian# apt-get install build-essentials
    root@debian# apt-get build-dep python-scipy

Install required 3rd party libraries::

	pip install -r requirements.txt

You are now ready to go, remember to use the ``python`` command instead of
executing the scripts, since that would use the sha-bang path for python
instead of the activated script.  During your next session you will only need
to source the activate script.

OSX with Xcode 5.1 problems
---------------------------
Looks like Xcode 5.1 breaks clang install of modules
This can be fixed by setting the following env variables
CC=clang
CXX=clang
FFLAGS=-ff2c
ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future

SciPy requires a fortran compiler, use:
brew install gfortran


Configuration
=============
Rename ``config/config.template.json`` to ``config/config.json`` and modify it
to point to your redis instance.


Rollbar reporting
==================
To enable error reporting to Rollbar_, set the
``ROLLBAR_API_KEY_${project_name}``.  The ``${project_name}`` should be either
``API`` or ``INGEST``.  Here is an example with bogus values, get the real
keys off the Rollbar website::

	export ROLLBAR_API_KEY_INGEST=f7956d6e0c430bc22e4872f9f20b3341

You can adjust the environment by setting the ``ERROR_REPORTING_ENVIRONMENT``
environment variable (default environment=dev)::

	export ERROR_REPORTING_ENVIRONMENT=production


Ingest
======
Make sure you have ``DATASIFT_USERNAME`` and ``DATASIFT_API_KEY`` defined in
your environment with the proper values::

	python ingest/consume.py


Url Fetcher
===========
This process runs forever fetching urls that are missing metadata directly
from the source site.  By default it will work out of a queue in the urldb and
block while there are no urls that need fetched.

    python ingest/urlfetch.py


Streaming from a text file
--------------------------
To stream from a text file instead of Datasift_, add a sources key to your
config.  The text file should contain one Datasift_ JSON message per line.  The
following example reads from ``interactions.json`` and maps the keys to topic
``2422``:

.. code:: json

	{
		"config": {
			"sources": { "file": [{ "filename": "interactions.json", "topic": "2422" }] },
		}
	}

Topic configuration
-------------------
You can use the topic subcommand of ``platform-tool.py`` to update and define
topics.  After every invocation of the tool the ingest script will receive a
command to update enabled topics, so you can provide multiple changes on a
single command line.  This allows you to make many changes without
disconnecting the consumer.

First add new definitions or change the existing topics::

	python platform-tool.py topics --update '{"name": "natural-disasters", "hash": "a2f939e1d7cad07048fbea18b765bc2b", "map": "2422"}'

Then enable/disable topics::

	python platform-tool.py topics --enable 2422 --disable 1234

You can remove definitions using ``--remove``, however this should only be done
for topic id's that were never inserted into the database.  Normally you will
only want to disable the topic.

If you would like to load all the topics from a configuration file which has
topics in the ``dstopics`` format, use ``--load-config``, all topics will be enabled::

	python platform-tool.py -c foo/config.json topics --load-config

For more info::

	python platform-tool.py topics --help


API Server
==========
::

	python server.py -d

Geo Setup
---------
Before using the geo endpoint you will need to import a database file from
GeoNames_.  The production server uses the ``allCountries.txt``
file::

	python platform-tool.py geo --import allCountries.txt

Running Tests
=============
Install additional dependencies to your virtualenv_::

	pip install -r requirements.unittest.txt

Unittests require nose nose_ to run::

	pip install nose
	cd "$repo-toplevel"
	nosetests-2.7

.. _nose: http://nose.readthedocs.org/en/latest/
.. _virtualenv: http://www.virtualenv.org/en/latest/
.. _Rollbar: https://rollbar.com
.. _Datasift: http://dev.datasift.com/docs
.. _GeoNames: http://download.geonames.org/export/dump/
