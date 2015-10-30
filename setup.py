from setuptools import setup, find_packages
import sys, os
import subprocess
import glob

# Fetch version from git tags, and write to version.py.
# Also, when git is not available (PyPi package), use stored version.py.
version_py = os.path.join(os.path.dirname(__file__), 'version.py')

try:
    version_git = subprocess.Popen(["git", "describe"],stdout=subprocess.PIPE).communicate()[0].rstrip()
except:
    with open(version_py, 'r') as fh:
        version_git = open(version_py).read().strip().split('=')[-1].replace('"','')


setup(name='genologics_sql',
      version=version_git,
      description="Python interface to the GenoLogics LIMS (Laboratory Information Management System) server via its postgres database.",
      long_description="""A basic module for interacting with the GenoLogics LIMS server via its postgres database.
                          The goal is to provide simple access to the most common entities and their attributes in a reasonably Pythonic fashion.""",
      classifiers=[
	"Development Status :: 4 - Beta",
	"Environment :: Console",
	"Intended Audience :: Developers",
	"Intended Audience :: Healthcare Industry",
	"Intended Audience :: Science/Research",
	"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
	"Operating System :: POSIX :: Linux",
	"Programming Language :: Python",
	"Topic :: Scientific/Engineering :: Medical Science Apps."
	],
      keywords='genologics database postgres',
      author='Denis Moreno',
      author_email='milui.galithil@gmail.com',
      maintainer='Denis Moreno',
      maintainer_email='denis.moreno@scilifelab.se',
      url='https://github.com/Galithil/genologics-sql',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      scripts=glob.glob("scripts/*.py"),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "SQLAlchemy",
          "pyyaml",
          "psycopg2"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
