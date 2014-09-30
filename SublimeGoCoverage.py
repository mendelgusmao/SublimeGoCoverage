import sublime
import sublime_plugin
import subprocess
import os
import re

gopath = os.environ["GOPATH"]
line_re = re.compile("^(?P<filename>.+):(?P<start_line>[0-9]+).(?P<start_column>[0-9]+),(?P<end_line>[0-9]+).(?P<end_column>[0-9]+) (?P<statements>[0-9]+) (?P<count>[0-9]+)$")

class ShowGoCoverageCommand(sublime_plugin.TextCommand):
	"""Run gocov and highlight uncovered lines in the current file."""

	def run(self, action):
		view = self.view
		filename = view.file_name()
		
		if not filename:
			return

		package_dir = os.path.dirname(filename)
		package_name = os.path.basename(package_dir)

		print("Generating coverage profile for", package_dir.replace(gopath + "/src/", ""))
		
		result = subprocess.check_output([gopath + "/bin/ginkgo", "-cover", "-race", package_dir])
		coverprofile = "%s/%s.coverprofile" % (package_dir, package_name)

		view.erase_status("SublimeGoCoverage")
		view.erase_regions("SublimeGoCoverage")

		outlines = []

		for line in parse_coverage_file(coverprofile):
			if line["count"] == "0" and filename.endswith(line["filename"]):
				start = int(line["start_line"])
				end = int(line["end_line"])

				for line_number in range(start, end):
					region = view.full_line(view.text_point(line_number, 0))
					outlines.append(region)

		if outlines:
			view.add_regions('SublimeGoCoverage', outlines, 'coverage.uncovered', 'bookmark', sublime.HIDDEN)

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
