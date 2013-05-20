#!/usr/bin/env python

import unittest, os, sys
from dj_nonrel_install import ResourceHandler as RH
from dj_nonrel_install import get_lib_urls

class MyTest(unittest.TestCase):
	def setUp(self):
		self.db = "gae" # dj_nonrel_install.query_user()
		self.fnames = []
		try:
			RH(["unittest", "--clean"])
		except SystemExit:
			pass
	
	def test_master(self):
		self.run_process("--master")
	def test_13(self):
		self.run_process("--dev13")
	def test_14(self):
		self.run_process("--dev14")
	def test_15(self):
		self.run_process("--dev15")
	
	def run_process(self, branch):
		rh = RH(["unittest", branch])
		
		libs = get_lib_urls(rh.branch_arg)[:6]
		
		rh.create_install_dir(rh.install_dir)
		
		for url in libs:
			self.fnames.append(rh.download(url[0]))
		
		for f in self.fnames:
			self.assertTrue(os.path.lexists(f))
		
		print "This should fail"
		print "This should fail"
		try:
			for f in self.fnames:
				rh.extract_file(f+"z") # This should fail.
		except IOError, e:
			pass
		
		for f in self.fnames:
			rh.extract_file(f)
		
		print "This should fail"
		print "This should fail"
		try:
			for f in self.fnames:
				rh.move_dir(f) # This should fail.
		except IOError, e:
			pass
		
		self.fnames = [ f.split(".")[0] for f in self.fnames ]
		for f in self.fnames:
			rh.move_dir(f)
		
		for i in xrange(len(self.fnames)):
			rh.symlink(self.fnames[i], libs[i][1], "django-testapp")
		
		listing = os.listdir(".")
		
		self.assertTrue("django-testapp" in listing)
		self.assertTrue("django-autoload" in listing)
	
	def tearDown(self):
		os.chdir("..")
		try:
			RH(["unittest", "--clean"])
		except SystemExit:
			pass
		


if __name__ == '__main__':
	#suite = unittest.TestSuite()
	#suite.addTest(MyTest("testProcess"))
	#unittest.TextTestRunner().run(suite)
	unittest.main()

