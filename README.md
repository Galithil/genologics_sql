# genologics_sql

[![Documentation Status](https://readthedocs.org/projects/genologics-sql/badge/?version=latest)](http://genologics-sql.readthedocs.org/en/latest/?badge=latest)

Python interface for the Genologics Postgres database. 

[Documentation on RTD](http://genologics-sql.readthedocs.org/en/latest/)

This requires a configuration file named ".genosqlrc.yaml". This file can be located either in your home directory, or in the working directory.

This file must follow the structure:

<pre>
username: ***
password: *** (can be empty)
url : *** (can be localhost)
db : ***
</pre>

A _very_ simple test framework is provided in the test directory.
In order to use it, get into the tests directory and run nosetests. 
Nosetest can be installed via `pip install nose`


The documentation of this package is built via sphinx with the ReadTheDocs theme. 
If you wish to build your own documentation, you must install sphinx_rtd_theme
