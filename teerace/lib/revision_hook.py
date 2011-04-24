#!/usr/bin/env python
# coding: utf-8

import os, sys
sys.path.append(os.environ['PWD'])
from django.core.management import setup_environ
from teerace import settings
setup_environ(settings)
from django.core.cache import cache
from subprocess import Popen, PIPE

if len(sys.argv) > 2:
	rev = sys.argv[2]
else:
	cmd = ["git", "rev-list", "-n 1", "--first-parent", "master"]
	rev = Popen(cmd, stdout=PIPE).communicate()[0].strip()
cache.set('current_revision', rev, 0)
