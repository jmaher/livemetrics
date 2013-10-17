livemetrics
===========

A simple framework for taking selenium scripts and collecting internal
data from Firefox for optimizing on the web

Requires Python 2.7 and Selenium 2.35.0.

TODO Items:
* support nightly, aurora and beta builds of firefox (selenium is hardcoded for max firefox version)
* support the updated Log4Moz (now Log) in firefox nightly (version 27.0a1)
* figure out a solution to make this run in the background, it is not developer friendly
* write better documentation about requirements, usage
* make the sample test cases a bit more complete (specifically gmail/twitter)
* figure out how to get logging information from the gecko backend into the log files
* instrument the test cases to have better markers/logging
* write a simple test case guide/example
* create a setup.py which will ensure requirements are met
