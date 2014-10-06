SublimeGoCoverage
=================

A plugin that highlights lines that are uncovered by tests.

Configuration
-------------

Use Preferences->Package Settings->Go Coverage to configure.

Basically, you should tell where is the test suite (go test, ginkgo, etc)
and where the cover profile is saved. The configuration strings are templated and
have some variables that will later be replaced when the SublimeGoCoverage calls the
test suite.

Example:

With the filename at the view: */home/mendelson/go/src/ephemeris/core/handlers/events.go*, the variables will be:


```json
{
		"gopath": "/home/mendelson/go",
		"filename": "/home/mendelson/go/src/ephemeris/core/handlers/events.go",
		"package_dir": "/home/mendelson/go/src/ephemeris/core/handlers",
		"package_name": "handlers",
		"package_full_name": "ephemeris/core/handlers"
}
```

Usage
-----

Pressing `ctrl+alt+g` or saving a go file will trigger the execution of the test suite and markers
will appear for every line that isn't being covered by the tests.
If you have open more than one file of the same package, they'll all have the markers updated.

![Screenshot](img/screenshot.png)

Inspired by [integrum/SublimeRubyCoverage](https://github.com/integrum/SublimeRubyCoverage)
