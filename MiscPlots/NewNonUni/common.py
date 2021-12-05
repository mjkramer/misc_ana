#!/usr/bin/env python-3

from collections import OrderedDict

import numpy as np

DIVS_R2 = np.linspace(0., 4e6, 11)
DIVS_Z = np.linspace(-2e3, 2e3, 11)

_CONFIGS = [('test_newNonUni_alphas_ngd', "$\\alpha$+nGd"),
            ('test_newNonUni_alphas_only',  "$\\alpha$-only"),
            ('test_newNonUni_off',  "no corr.")]
CONFIGS = OrderedDict(_CONFIGS)

_TAGS = [('p17b_v4_NL', 'P17B'), ('post17_v5v3v1_NL', 'Post17')]
TAGS = OrderedDict(_TAGS)
