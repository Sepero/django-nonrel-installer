#!/usr/bin/env python

"""
Installs the base system for django-nonrel

Syntax:
python dj_nonrel_install.py --master # Installs master branches (Will be removed).
python dj_nonrel_install.py --dev13  # Installs 1.3 development branches.
python dj_nonrel_install.py --dev14  # Installs 1.4 development branches.
python dj_nonrel_install.py --dev15  # Installs 1.5 development branches.
python dj_nonrel_install.py --clean  # Deletes all created files.

license: BSD 2-Clause License, 2012, Sepero
license: http://www.opensource.org/licenses/BSD-2-Clause
I prefer GNU, but it would seem excessive for this small program.
"""

import os, sys, shutil, urllib2, tarfile

CONTACT=("sepero 111 @ gmx . com\n "
			"http://bitbucket.org/Sepero/install-django-nonrel/issues/new\n"
			"http://seperohacker.blogspot.com/2012/04/installing-django-nonrel-easily.html")
VERSION="0.43"

# Presents the user with a choice between GAE and MongoDB install.
def query_user(): # This function currently unused.
	print "Google App Engine is the default backend. Instead use MongoDB? [y/N] ",
	return "mongo" if sys.stdin.readline().lower()[0] == "y" else "gae"


class ResourceHandler(object):
	"""
	ResourceHandler is an object for
	parsing command line arguments,
	handling our errors,
	working with urls,
	working with files.
	"""
	def _exit_error(self, code, option=None, err=None):
		"""
		Error information is kept here for the purposes of easier management 
		and possibly language translation.
		Returns nothing. All calls exit the program, exit error status 128.
		"""
		error_codes = {
		"unknownarg":
			"Unknown argument: %s\n--dev13 --dev14 --dev15 --clean" % option,
		"mkdir":
			"Failed to create sub dir: %s\n(Run with option --clean to remove an old install)" % option,
		"fileopen":
			"Opening file: %s\n(Run with option --clean to remove an old install)" % option,
		"urlopen":
			"Connecting to the url:\n%s" % option,
		"filewrite":
			"Saving to file: %s" % option,
		"urlread":
			"Reading from url: %s" % option,
		"untar":
			"Extracting archive: %s" % option,
		"movedir":
			"Renaming directory from: %s" % option,
		"pathexists":
			"Path name already exists: %s\n(If trying to install twice, erase all files and begin again)" % option,
		"notfound":
			"Could not find a directory name containing: %s" % option,
		"symlink":
			"Could not create symbolic link from: %s" % option,
		"cleaning":
			"Failed to delete: %s" % option,
		}
		sys.stderr.write("version: %s\n" % VERSION)
		sys.stderr.write("Report issues to: %s\n" % CONTACT)
		if err: sys.stderr.write("%s\n" % str(err))
		sys.stderr.write("Error <%s>: %s\n\n" % (code, error_codes[code]))
		if __name__ == '__main__': # Don't exit if not running directly.
			print "<press enter>"
			sys.stdin.readline()
			sys.exit(128)
		else:
			raise
	
	def __init__(self, argv=sys.argv):
		"""
		Parse first commandline argument. self.branch will hold a string 
		which indicates the branch of django-nonrel to install.
		Options:
			--clean   Clean/erase all django files to prepare for reinstall.
			--master  Installs master branches (Will be removed).
			--dev13   Installs 1.3 development branches.
			--dev14   Installs 1.4 development branches.
			--dev15   Installs 1.5 development branches.
		"""
		
		self.install_dir = "django-nonrel"
		if len(argv) == 1:
			sys.stderr.write("Warning: Defaulting to option --master. Future default will be --dev15.\n")
			arg1 = "--master"
		else:
			arg1 = argv[1]
		
		if arg1 == "--clean": # Delete any created files and exit.
			self.clean(self.install_dir)
			sys.exit()
		
		if arg1 == "--master":
			sys.stderr.write(
					"Warning: Option --master is no longer supported and will "
					"be removed in future releases.\n")
			print " Master 1.3 branches selected"
		elif arg1 == "--dev13" or arg1 == "--dev" or arg1 == "--develop":
			print " Development 1.3 branches selected"
		elif arg1 == "--dev14":
			print " Development 1.4 branches selected"
		elif arg1 == "--dev15":
			print " Development 1.5 branches selected"
		else:
			self._exit_error("unknownarg", arg1)
		
		self.branch_arg = arg1
	
	def create_install_dir(self, dir):
		try:
			os.mkdir(dir)
			os.chdir(dir)
		except OSError, e:
			self._exit_error("mkdir", dir, e)
			raise
			
	
	def download(self, url):
		"""
		This function handles downloading of one url library at a time.
		"""
		# Each url will be saved to the filename determined by fname.
		fname = url.split('/')[4] +".tar.gz"
		
		try: # Open output file as f.
			f = open(fname, "wb")
		except Exception, e:
			self._exit_error("fileopen", fname, e)
		
		try: # Open url to read from as u.
			u = urllib2.urlopen(url)
		except Exception, e:
			self._exit_error("urlopen", url, e)
		
		loaded_bytes = 0
		while True: # Loop for reading, writing, and printing progress.
			try: # Read from url into buffer.
				buffer = u.read(8192)
			except Exception, e:
				self._exit_error("urlread", url, e)
			if not buffer: # If buffer is empty, finished reading url.
				print
				f.close()
				return fname
			
			loaded_bytes += len(buffer) # Track number of bytes read for printing.
			try: # Write bytes to output file f.
				f.write(buffer)
			except Exception, e:
				self._exit_error("filewrite", fname, e)
				
			# Print status of current download.
			sys.stdout.write("Downloading: %25s %10d Kbytes downloaded\r" %
					(f.name, (loaded_bytes / 1024 or 1)))
			sys.stdout.flush()
	
	def extract_file(self, fname):
		"""
		Extract the file fname, then delete it.
		"""
		print "Extracting file: %s	" % fname
		flag = "gz" if fname.endswith(".tar.gz") else "bz2"
		try:
			t = tarfile.open(fname, "r:%s" % flag)
			t.extractall()
			t.close()
		except Exception, e:
			self._exit_error("untar", fname, e)
		os.remove(fname)
		print "Deleted"
	
	def move_dir(self, fname):
		"""
		Renaming directories, for example
		if fname == "django-nonrel", then move a directory like so:
		from "ksjdff-django-nonrel-kdshf" to "django-nonrel".
		"""
		for path in os.listdir("."):
			#print(path, fname)
			if path.find("-%s-" % fname) != -1:
				if os.path.lexists(fname):
					self._exit_error("pathexists", fname)
				print "Renaming:%43s to %s" % (path, fname)
				try:
					shutil.move(path, fname)
				except Exception, e:
					self._exit_error("movedir", path+" to "+fname, e)
				return
		else:
			self._exit_error("notfound", fname) # This is likely to indicate a problem in directory naming.
	
	def symlink(self, target, ln_name, ln_root):
		"""
		Create a symbolic link named  ln_root/ln_name  which points to the
		directory	../target/ln_name/
		
		If ln_name == "", then create a symbolic link named  ln_root/target
		which points to the directory  ../target/
		
		If symbolic links aren't supported, then the directory
		target/ln_name/	or	target/	will simply be moved into ln_root/
		"""
		####### I'd like to make this function easier to read.
		if target == ln_root: # Don't link to self ("django-testapp").
			return
		if ln_name:
			target += os.sep + ln_name
		print(target)
		ln_name = ln_root + os.sep + (ln_name or target)
		print(ln_name)
		try: # Try symbolic link.
			os.symlink(".." + os.sep + target, ln_name)
			print "SymLinking From: %15s to ..%s" % (ln_name, os.sep + target)
		except: # If symbolic link fails, just move the folder.
			#print sys.exc_info()
			try:
				print "Moving Folder: %15s to %s" % (target, ln_name)
				shutil.move(target, ln_name)
			except Exception, e:
				self._exit_error("movedir", target+" to "+ln_name, e)
	
	def clean(self, dir):
		"""
		Deletes the directory "django-nonrel".
		"""
		try:
			shutil.rmtree(dir, True)
		except Exception, e:
			self._exit_error("cleaning", dir, e)

def get_lib_urls(branch_arg):
	"""
	Return a list of lists.
	Each sub-list contains 2 strings: A url to a gzipped library, 
	and the directory location of the library inside each gzip archive.
	"""
	urls_master = [
		"http://github.com/django-nonrel/djangotoolbox/tarball/toolbox-1.3",
		"http://github.com/django-nonrel/djangoappengine/tarball/appengine-1.3",
		"http://github.com/django-nonrel/django-dbindexer/tarball/dbindexer-1.3",
		"http://github.com/django-nonrel/django-testapp/tarball/testapp-1.3",
		"http://github.com/django-nonrel/nonrel-search/tarball/master",
		"http://github.com/django-nonrel/django-permission-backend-nonrel/tarball/master",
		"http://github.com/django-nonrel/django-nonrel/tarball/master",
	]
	urls_13 = [
		"http://github.com/django-nonrel/djangotoolbox/tarball/toolbox-1.3",
		"http://github.com/django-nonrel/djangoappengine/tarball/appengine-1.3",
		"http://github.com/django-nonrel/django-dbindexer/tarball/dbindexer-1.3",
		"http://github.com/django-nonrel/django-testapp/tarball/testapp-1.3",
		"http://github.com/django-nonrel/nonrel-search/tarball/develop",
		"http://github.com/django-nonrel/django-permission-backend-nonrel/tarball/develop",
		"http://github.com/django-nonrel/django/tarball/nonrel-1.3",
	]
	urls_14 = [
		"http://github.com/django-nonrel/djangotoolbox/tarball/toolbox-1.4",
		"http://github.com/django-nonrel/djangoappengine/tarball/appengine-1.4",
		"http://github.com/django-nonrel/django-dbindexer/tarball/dbindexer-1.4",
		"http://github.com/django-nonrel/django-testapp/tarball/testapp-1.4",
		"http://github.com/django-nonrel/nonrel-search/tarball/develop",
		"http://github.com/django-nonrel/django-permission-backend-nonrel/tarball/develop",
		"http://github.com/django-nonrel/django/tarball/nonrel-1.4",
	]
	urls_15 = [
		"http://github.com/django-nonrel/djangotoolbox/tarball/toolbox-1.5-beta",
		"http://github.com/django-nonrel/djangoappengine/tarball/appengine-1.5-beta",
		"http://github.com/django-nonrel/django-dbindexer/tarball/dbindexer-1.5-beta",
		"http://github.com/django-nonrel/django-testapp/tarball/testapp-1.5-beta",
		"http://github.com/django-nonrel/nonrel-search/tarball/develop",
		"http://github.com/django-nonrel/django-permission-backend-nonrel/tarball/develop",
		"http://github.com/django-nonrel/django/tarball/nonrel-1.5-beta",
	]
	lib_dirs = [
		"autoload",
		"djangotoolbox",
		"djangoappengine",
		"dbindexer",
		"",
		"search",
		"permission_backend_nonrel",
		"django",
	]
	
	# This same library goes with all branches.
	return_list = [[ "http://bitbucket.org/twanschik/django-autoload/get/default.tar.gz" ]]
	
	if branch_arg == "--master":
		return_list += [ [url] for url in urls_master ]
	elif branch_arg == "--dev13":
		return_list += [ [url] for url in urls_13 ]
	elif branch_arg == "--dev14":
		return_list += [ [url] for url in urls_14 ]
	elif branch_arg == "--dev15":
		return_list += [ [url] for url in urls_15 ]
	
	# Append the directory location of each library with it's URL.
	# Resulting in a list like this: [ [ url, dir ], [ url, dir ], ... ]
	for i in xrange(8):
		return_list[i].append(lib_dirs[i])
	
	return return_list

def print_final():
	from textwrap import fill # Format line printing.
	print
	print "==FINISHED=="
	s = os.sep # Operating system slash "/" or "\".
	print fill("Assuming everything went correctly, "
	"django-nonrel should be ready to run with Google App Engine SDK. "
	"To run it, you will need the GAE SDK installed and listed in your "
	"environment $PATH. Also, you may need to put the path to GAE webob "
	"in your python environment $PYTHONPATH (google_appengine"
	+ s + "lib" + s + "webob_1_1_1). When ready, begin the "
	"local server by changing to the directory django-nonrel"
	+ s + "django-testapp" + s +
	" and running:")
	print "python manage.py runserver\nThen point your browser to:"
	print "http://localhost:8000\nFurther django-nonrel documentation:"
	print "http://django-nonrel.readthedocs.org/en/latest/"
	print "http://groups.google.com/group/django-non-relational"
	print "Report issues/thanks to: %s" % CONTACT
	print "<press enter to end>",
	sys.stdin.readline() # Waits for Windows machines that might close CLI.

def main():
	rh = ResourceHandler()
	rh.create_install_dir(rh.install_dir)
	
	libs = get_lib_urls(rh.branch_arg)
	
	fnames = []
	# Download archived library files.
	for url in libs:
		fnames.append(rh.download(url[0]))
	# Extract the archive files and delete them.
	for fname in fnames:
		rh.extract_file(fname)
	# Remove file extensions from file names list.
	fnames = [ fname[:-7] for fname in fnames ]
	# Rename directories cleanly.
	for fname in fnames:
		rh.move_dir(fname)
	# Create symbolic links.
	for i in xrange(len(fnames)):
		rh.symlink(fnames[i], libs[i][1], "django-testapp")
	
	print_final()
	# Done and print final output.
	
if __name__ == '__main__':
	main()

