#!/usr/bin/env python
# coding: utf-8

import os, sys
sys.path.append(os.environ['PWD'])
from django.core.management import setup_environ
from teerace import settings
setup_environ(settings)
from django.core.cache import cache
from subprocess import Popen, PIPE

def get_revision():
	cmd = ["git", "rev-list", "-n 1", "--first-parent", "master"]
	return Popen(cmd, stdout=PIPE).communicate()[0].strip()

def set_cache(rev):
	cache.set('current_revision', rev, 0)

if __name__ == '__main__':
	rev = get_revision()
	set_cache(rev)
