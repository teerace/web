#!/usr/bin/env python
# coding: utf-8

from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.core.cache import cache
from subprocess import Popen, PIPE

if len(sys.argv) > 2:
	rev = sys.argv[2]
else:
	cmd = ["git", "rev-list", "-n 1", "--first-parent", "master"]
	rev = Popen(cmd, stdout=PIPE).communicate()[0].strip()
cache.set('current_revision', rev, 0)
