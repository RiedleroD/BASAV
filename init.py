#!/usr/bin/python3
from distutils.core import setup, Extension

#run the command below in this directory to compile the helper module
#python3 init.py build_ext --inplace

def main():
	setup(name="helper",
	version="0.0.1",
	description="Helper module for BASAV",
	author="Riedler",
	author_email="dev@riedler.wien",
	ext_modules=[Extension("helper", ["helper.c"])])
if __name__ == "__main__":
	main()
