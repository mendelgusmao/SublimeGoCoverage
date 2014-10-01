import sublime
import sublime_plugin
import subprocess
import os
import re
import shlex

gopath = os.environ["GOPATH"]
line_re = re.compile("^(?P<filename>.+):(?P<start_line>[0-9]+).(?P<start_column>[0-9]+),(?P<end_line>[0-9]+).(?P<end_column>[0-9]+) (?P<statements>[0-9]+) (?P<count>[0-9]+)$")
settings = "SublimeGoCoverage.sublime-settings"

class ShowGoCoverageCommand(sublime_plugin.TextCommand):
	"""Run gocov and highlight uncovered lines in the current file."""

	def run(self, action):
		view = self.view

		if "source.go" not in view.scope_name(0):
			return

		filename = view.file_name()

		if not filename:
			return

		coverprofile = run_coverage(filename)
		create_outlines(view, coverprofile)

def run_coverage(filename):
	package_dir = os.path.dirname(filename)
	package_name = os.path.basename(package_dir)
	package_full_name = package_dir.replace(gopath + "/src/", "")
	coverprofile = "%s/%s.coverprofile" % (package_dir, package_name)

	print("Generating coverage profile for", package_dir)
	
	runner = sublime.load_settings(settings).get("runner") or "go-test"
	moreargs = sublime.load_settings(settings).get("moreargs") or ""

	cmd = ""

	if runner == "go-test":
		cmd = "go test %s -cover -coverprofile=%s %s" % (moreargs, coverprofile, package_full_name)
	elif runner == "ginkgo":
		cmd = "ginkgo %s -cover %s" % (moreargs, package_dir)

	subprocess.check_output(shlex.split(cmd))

	return coverprofile

def create_outlines(view, coverprofile):
	view.erase_status("SublimeGoCoverage")
	view.erase_regions("SublimeGoCoverage")

	outlines = []

	for line in parse_coverage_file(coverprofile):
		if line["count"] == "0" and view.file_name().endswith(line["filename"]):
			start = int(line["start_line"])
			end = int(line["end_line"])

			for line_number in range(start, end):
				region = view.full_line(view.text_point(line_number, 0))
				outlines.append(region)

	if outlines:
		view.add_regions("SublimeGoCoverage", outlines, "coverage.uncovered", "dot", sublime.HIDDEN)

def parse_coverage_file(filename):
	lines = []

	try:
		with open(filename) as coverage:
			for current_line, line in enumerate(coverage):
				match = line_re.match(line)

				if not match:
					continue

				lines.append(match.groupdict())
	except:
		print("error!")

	return lines
