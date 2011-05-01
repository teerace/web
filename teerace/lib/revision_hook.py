#!/usr/bin/env python
# coding: utf-8

import os, sys
from subprocess import Popen, PIPE

def get_revision():
	from django.conf import settings
	old_path = os.getcwd()
	os.chdir(settings.PROJECT_DIR)
	cmd = ["git", "rev-list", "-n 1", "--first-parent", "master"]
	rev = Popen(cmd, stdout=PIPE).communicate()[0].strip()
	os.chdir(old_path)
	return rev

def set_cache(rev):
	from django.core.cache import cache
	cache.set('current_revision', rev, 0)

if __name__ == '__main__':
	sys.path.append(os.environ['PWD'])
	from django.core.management import setup_environ
	from teerace import settings
	setup_environ(settings)

	rev = get_revision()
	set_cache(rev)
