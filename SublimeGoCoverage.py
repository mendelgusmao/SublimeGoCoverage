import sublime
import sublime_plugin
import subprocess
import os
import re
import shlex

gopath = os.environ["GOPATH"]
line_re = re.compile("^(?P<filename>.+):(?P<start_line>[0-9]+).(?P<start_column>[0-9]+),(?P<end_line>[0-9]+).(?P<end_column>[0-9]+) (?P<statements>[0-9]+) (?P<count>[0-9]+)$")
settings = "SublimeGoCoverage.sublime-settings"

class ShowGoCoverageListener(sublime_plugin.EventListener):
	"""Event listener to highlight uncovered lines when a Go file is loaded."""

	def on_post_save_async(self, view):
		on_save = sublime.load_settings(settings).get("on_save")

		if on_save:
			view.run_command("show_go_coverage")

	def on_load_async(self, view):
		create_outlines(view, parse_filename(view.file_name()))

class ShowGoCoverageCommand(sublime_plugin.TextCommand):
	"""Run gocov and highlight uncovered lines in the current file."""

	def run(self, action):
		view = self.view

		if "source.go" not in view.scope_name(0):
			return

		filename = view.file_name()

		if not filename:
			return

		file_info = parse_filename(filename)

		if run_tests(file_info):
			update_views(file_info)

def parse_filename(filename):
	package_dir = os.path.dirname(filename)
	package_name = os.path.basename(package_dir)
	package_full_name = package_dir.replace(gopath + "/src/", "")

	data = {
		"gopath": gopath,
		"filename": filename,
		"package_dir": package_dir,
		"package_name": package_name,
		"package_full_name": package_full_name
	}

	cover_profile_path = sublime.load_settings(settings).get("cover_profile_path")

	if not cover_profile_path:
		print("Can't run tests. Invalid 'cover_profile' configuration entry.")

	data["cover_profile"] = cover_profile_path % data

	return data

def run_tests(file_info):
	package_full_name = file_info["package_full_name"]
	package_dir = file_info["package_dir"]
	cover_profile = file_info["cover_profile"]

	print("Generating coverage profile for", package_full_name)
	
	command_line = sublime.load_settings(settings).get("command_line")

	if not command_line:
		print("Can't run tests. Invalid 'command_line' configuration entry.")

	handler = None

	try:
		handler = subprocess.Popen(
			shlex.split(command_line % file_info),
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT)
		output = handler.communicate()[0]
	except Exception as e:
		print("Error running tests:", e)
		return False
	finally:
		if handler and handler.returncode > 0:
			print("Error running tests:")
			print(output)
			return False

	return True

def update_views(file_info):
	for window in sublime.windows():
		for view in window.views():
			if view.file_name():
				other_file_info = parse_filename(view.file_name())

				if file_info["package_full_name"] == other_file_info["package_full_name"]:
					create_outlines(view, other_file_info)

def create_outlines(view, file_info):
	print("Creating outlines for", file_info["filename"])

	view.erase_status("SublimeGoCoverage")
	view.erase_regions("SublimeGoCoverage")

	outlines = []
	cover_profile = file_info["cover_profile"]

	for line in parse_coverage_profile(cover_profile):
		if line["count"] == "0" and view.file_name().endswith(line["filename"]):
			start = int(line["start_line"])
			end = int(line["end_line"])

			for line_number in range(start, end):
				region = view.full_line(view.text_point(line_number, 0))
				outlines.append(region)

	if outlines:
		view.add_regions("SublimeGoCoverage", outlines, "coverage.uncovered", "dot", sublime.HIDDEN)

def parse_coverage_profile(filename):
	lines = []

	try:
		with open(filename) as coverage:
			for current_line, line in enumerate(coverage):
				match = line_re.match(line)

				if not match:
					continue

				lines.append(match.groupdict())
	except Exception as e:
		print("Error reading coverage file: ", e)

	return lines

