#! /bin/bash
#
# run.bash
# Copyright (C) 2019 Shlomi Fish <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.
#


set -e -x
make -f modsum.mak
"${PYTHON:-python3}" 662_v1.py
