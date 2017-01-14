# (c) 2012-2016 Continuum Analytics, Inc. / http://continuum.io
# All Rights Reserved
#
# conda is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.
'''
We use the following conventions in this module:

    dist:        canonical package name, e.g. 'numpy-1.6.2-py26_0'

    ROOT_PREFIX: the prefix to the root environment, e.g. /opt/anaconda

    PKGS_DIR:    the "package cache directory", e.g. '/opt/anaconda/pkgs'
                 this is always equal to ROOT_PREFIX/pkgs

    prefix:      the prefix of a particular environment, which may also
                 be the root environment

Also, this module is directly invoked by the (self extracting) tarball
installer to create the initial environment, therefore it needs to be
standalone, i.e. not import any other parts of `conda` (only depend on
the standard library).
'''
import os
import re
import sys
import json
import shutil
import stat
from os.path import abspath, dirname, exists, isdir, isfile, islink, join
from optparse import OptionParser


on_win = bool(sys.platform == 'win32')

LINK_HARD = 1
LINK_SOFT = 2  # never used during the install process
LINK_COPY = 3
link_name_map = {
    LINK_HARD: 'hard-link',
    LINK_SOFT: 'soft-link',
    LINK_COPY: 'copy',
}

# these may be changed in main()
ROOT_PREFIX = sys.prefix
PKGS_DIR = join(ROOT_PREFIX, 'pkgs')
SKIP_SCRIPTS = False
FORCE = False
IDISTS = {
  "_license-1.1-py27_1": {
    "md5": "dda038d00d891fc1b747471b2d248595", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/_license-1.1-py27_1.tar.bz2"
  }, 
  "_nb_ext_conf-0.3.0-py27_0": {
    "md5": "5711a814aa8297638bd478f96ce49c57", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/_nb_ext_conf-0.3.0-py27_0.tar.bz2"
  }, 
  "alabaster-0.7.9-py27_0": {
    "md5": "3fdb53d04c5caa9063faf06fc3046111", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/alabaster-0.7.9-py27_0.tar.bz2"
  }, 
  "anaconda-4.2.0-np111py27_0": {
    "md5": "a78e9de559a6d5e28d259c0ae9f3b0e4", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/anaconda-4.2.0-np111py27_0.tar.bz2"
  }, 
  "anaconda-clean-1.0.0-py27_0": {
    "md5": "324ae00df39b19e48a8a3da60161888a", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/anaconda-clean-1.0.0-py27_0.tar.bz2"
  }, 
  "anaconda-client-1.5.1-py27_0": {
    "md5": "dd5cffa6a2facc781c177c02f1521e1f", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/anaconda-client-1.5.1-py27_0.tar.bz2"
  }, 
  "anaconda-navigator-1.3.1-py27_0": {
    "md5": "9bf405bb533d47f805ab26499887254c", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/anaconda-navigator-1.3.1-py27_0.tar.bz2"
  }, 
  "argcomplete-1.0.0-py27_1": {
    "md5": "7aaf2d135a7de3dfe96ccafd9dd891d4", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/argcomplete-1.0.0-py27_1.tar.bz2"
  }, 
  "astroid-1.4.7-py27_0": {
    "md5": "91683916e0276efea37ef977d5d11eef", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/astroid-1.4.7-py27_0.tar.bz2"
  }, 
  "astropy-1.2.1-np111py27_0": {
    "md5": "685eb93a38234e8c76016b237f6067ef", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/astropy-1.2.1-np111py27_0.tar.bz2"
  }, 
  "babel-2.3.4-py27_0": {
    "md5": "5a7953e6e37d16ec149c5c3027b54d91", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/babel-2.3.4-py27_0.tar.bz2"
  }, 
  "backports-1.0-py27_0": {
    "md5": "3584e3c89857146300d90018dcd70c10", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/backports-1.0-py27_0.tar.bz2"
  }, 
  "backports_abc-0.4-py27_0": {
    "md5": "011fd16fb415b72d9b6f90c04dff1766", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/backports_abc-0.4-py27_0.tar.bz2"
  }, 
  "beautifulsoup4-4.5.1-py27_0": {
    "md5": "1e99953e2ad613620fc1af3ef12d4dd0", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/beautifulsoup4-4.5.1-py27_0.tar.bz2"
  }, 
  "bitarray-0.8.1-py27_0": {
    "md5": "63ac1570da537ba9894eab26e0a41d5f", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/bitarray-0.8.1-py27_0.tar.bz2"
  }, 
  "blaze-0.10.1-py27_0": {
    "md5": "76667d843b5f94468af1c5e7300b2684", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/blaze-0.10.1-py27_0.tar.bz2"
  }, 
  "bokeh-0.12.2-py27_0": {
    "md5": "0a9955e9b0a00ad5e08bd51eca389ff3", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/bokeh-0.12.2-py27_0.tar.bz2"
  }, 
  "boto-2.42.0-py27_0": {
    "md5": "edcfba5b5b4bc5fa35a483b1a7bf8b0d", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/boto-2.42.0-py27_0.tar.bz2"
  }, 
  "bottleneck-1.1.0-np111py27_0": {
    "md5": "6257d36c2226b0220431be5b0c593199", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/bottleneck-1.1.0-np111py27_0.tar.bz2"
  }, 
  "cairo-1.12.18-6": {
    "md5": "f4cf38da3656153c318987e8e928ace7", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/cairo-1.12.18-6.tar.bz2"
  }, 
  "cdecimal-2.3-py27_2": {
    "md5": "211b163663e5f4ced130f0f950c813e9", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/cdecimal-2.3-py27_2.tar.bz2"
  }, 
  "cffi-1.7.0-py27_0": {
    "md5": "8e696c09f61520307bed94e073153675", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/cffi-1.7.0-py27_0.tar.bz2"
  }, 
  "chest-0.2.3-py27_0": {
    "md5": "afe6d994273886e5f39d2babef0a2b2c", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/chest-0.2.3-py27_0.tar.bz2"
  }, 
  "click-6.6-py27_0": {
    "md5": "3ba6930a6334108ab6e486d4da901933", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/click-6.6-py27_0.tar.bz2"
  }, 
  "cloudpickle-0.2.1-py27_0": {
    "md5": "ba735a4a48eb55cb740c73f29ebfb184", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/cloudpickle-0.2.1-py27_0.tar.bz2"
  }, 
  "clyent-1.2.2-py27_0": {
    "md5": "97e9268eabcb5ccded58fb9188730786", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/clyent-1.2.2-py27_0.tar.bz2"
  }, 
  "colorama-0.3.7-py27_0": {
    "md5": "0e664c202b9f776cb5b94321eaeddfb8", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/colorama-0.3.7-py27_0.tar.bz2"
  }, 
  "conda-4.2.9-py27_0": {
    "md5": "b5579137b310ec3f34822c9709965a83", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/conda-4.2.9-py27_0.tar.bz2"
  }, 
  "conda-build-2.0.2-py27_0": {
    "md5": "1048721f77f9f8c91f0c945157340c51", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/conda-build-2.0.2-py27_0.tar.bz2"
  }, 
  "configobj-5.0.6-py27_0": {
    "md5": "058ebcb6414921a0d67a4914356768ec", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/configobj-5.0.6-py27_0.tar.bz2"
  }, 
  "configparser-3.5.0-py27_0": {
    "md5": "2ee94cf0f0fee3e7bf1c78368d79873a", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/configparser-3.5.0-py27_0.tar.bz2"
  }, 
  "contextlib2-0.5.3-py27_0": {
    "md5": "29c24a5b0c5f8e4c9d84862d8958c3c7", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/contextlib2-0.5.3-py27_0.tar.bz2"
  }, 
  "cryptography-1.5-py27_0": {
    "md5": "3e84f44595ea5f5f6fbf2f7b31fb5800", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/cryptography-1.5-py27_0.tar.bz2"
  }, 
  "curl-7.49.0-1": {
    "md5": "f54b5ebd9b0f9c2d0f7348926c9417ea", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/curl-7.49.0-1.tar.bz2"
  }, 
  "cycler-0.10.0-py27_0": {
    "md5": "5fa3237284832ffeaeded70c6b6953e6", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/cycler-0.10.0-py27_0.tar.bz2"
  }, 
  "cython-0.24.1-py27_0": {
    "md5": "70ee735524efe46a9cc6aa0ccfa28c48", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/cython-0.24.1-py27_0.tar.bz2"
  }, 
  "cytoolz-0.8.0-py27_0": {
    "md5": "52a5be1d09e272af3c526ba504bc5d1c", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/cytoolz-0.8.0-py27_0.tar.bz2"
  }, 
  "dask-0.11.0-py27_0": {
    "md5": "005607973093d205382cfd64c6ca3ec4", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/dask-0.11.0-py27_0.tar.bz2"
  }, 
  "datashape-0.5.2-py27_0": {
    "md5": "efad0854a229d56ca9a19e526fca1426", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/datashape-0.5.2-py27_0.tar.bz2"
  }, 
  "dbus-1.10.10-0": {
    "md5": "80493c5ee4ee933a24e8e25f9e09cdaa", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/dbus-1.10.10-0.tar.bz2"
  }, 
  "decorator-4.0.10-py27_0": {
    "md5": "452528cf4efb653a64a1a877d6828814", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/decorator-4.0.10-py27_0.tar.bz2"
  }, 
  "dill-0.2.5-py27_0": {
    "md5": "be598d82530829978c2aedbaef5f98d0", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/dill-0.2.5-py27_0.tar.bz2"
  }, 
  "docutils-0.12-py27_2": {
    "md5": "6e65657e3f2c0608213a3e5423aeeb64", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/docutils-0.12-py27_2.tar.bz2"
  }, 
  "dynd-python-0.7.2-py27_0": {
    "md5": "77e94accbe86996b90e7c84d0cb03025", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/dynd-python-0.7.2-py27_0.tar.bz2"
  }, 
  "entrypoints-0.2.2-py27_0": {
    "md5": "802805f7a9b76e5b1fccd12b20f7ebb2", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/entrypoints-0.2.2-py27_0.tar.bz2"
  }, 
  "enum34-1.1.6-py27_0": {
    "md5": "1407d00867af7f42ab47628d8639f943", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/enum34-1.1.6-py27_0.tar.bz2"
  }, 
  "et_xmlfile-1.0.1-py27_0": {
    "md5": "e14c617f590057cc25a5f23cb5af7811", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/et_xmlfile-1.0.1-py27_0.tar.bz2"
  }, 
  "expat-2.1.0-0": {
    "md5": "13df3cb2b432de77be2c13103c39692c", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/expat-2.1.0-0.tar.bz2"
  }, 
  "fastcache-1.0.2-py27_1": {
    "md5": "02f3d02f47cfb8d0a1fa828889e2b22a", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/fastcache-1.0.2-py27_1.tar.bz2"
  }, 
  "filelock-2.0.6-py27_0": {
    "md5": "b052b3ceae01082eaccaf392a03b8f9b", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/filelock-2.0.6-py27_0.tar.bz2"
  }, 
  "flask-0.11.1-py27_0": {
    "md5": "84745fa0cbb48f48a6a13d43303b09d7", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/flask-0.11.1-py27_0.tar.bz2"
  }, 
  "flask-cors-2.1.2-py27_0": {
    "md5": "b78772bef2635066d54351cadc3d2c5f", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/flask-cors-2.1.2-py27_0.tar.bz2"
  }, 
  "fontconfig-2.11.1-6": {
    "md5": "7613e859f05db6294c0aedb09a21f7e7", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/fontconfig-2.11.1-6.tar.bz2"
  }, 
  "freetype-2.5.5-1": {
    "md5": "7ee1d1c769f343a4ad3a5926efd3fb05", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/freetype-2.5.5-1.tar.bz2"
  }, 
  "funcsigs-1.0.2-py27_0": {
    "md5": "b7448f5cea660e2db1b6bf891106ac88", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/funcsigs-1.0.2-py27_0.tar.bz2"
  }, 
  "functools32-3.2.3.2-py27_0": {
    "md5": "f75142247b96c51882de66edcd2338ac", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/functools32-3.2.3.2-py27_0.tar.bz2"
  }, 
  "futures-3.0.5-py27_0": {
    "md5": "e42a13bf6f75ca2c2c94318064c9d9aa", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/futures-3.0.5-py27_0.tar.bz2"
  }, 
  "get_terminal_size-1.0.0-py27_0": {
    "md5": "25ad88504e366d061a845afef3c10f9d", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/get_terminal_size-1.0.0-py27_0.tar.bz2"
  }, 
  "gevent-1.1.2-py27_0": {
    "md5": "c3199e1413e523dbe3016ed5a4190696", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/gevent-1.1.2-py27_0.tar.bz2"
  }, 
  "glib-2.43.0-1": {
    "md5": "ddd6dd7a93f33a5a23e99b3014fe1bd3", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/glib-2.43.0-1.tar.bz2"
  }, 
  "greenlet-0.4.10-py27_0": {
    "md5": "d5fde4fc871f483088c4ae46b1013e26", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/greenlet-0.4.10-py27_0.tar.bz2"
  }, 
  "grin-1.2.1-py27_3": {
    "md5": "cccc667cfe6f813265f14782fb98008b", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/grin-1.2.1-py27_3.tar.bz2"
  }, 
  "gst-plugins-base-1.8.0-0": {
    "md5": "9c19173e0e6b8eaeadfb604000169f78", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/gst-plugins-base-1.8.0-0.tar.bz2"
  }, 
  "gstreamer-1.8.0-0": {
    "md5": "5a5e2aff3d6bd7f4d69a60140ed0a571", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/gstreamer-1.8.0-0.tar.bz2"
  }, 
  "h5py-2.6.0-np111py27_2": {
    "md5": "a053e1b55311f1ad70cb9c09e78ccb4e", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/h5py-2.6.0-np111py27_2.tar.bz2"
  }, 
  "harfbuzz-0.9.39-1": {
    "md5": "68e642863fb24758cd525dcd267d7760", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/harfbuzz-0.9.39-1.tar.bz2"
  }, 
  "hdf5-1.8.17-1": {
    "md5": "a10478d5543c24f8260d6b777c7f4bc7", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/hdf5-1.8.17-1.tar.bz2"
  }, 
  "heapdict-1.0.0-py27_1": {
    "md5": "48f42c6ae6230f702c00109990263427", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/heapdict-1.0.0-py27_1.tar.bz2"
  }, 
  "icu-54.1-0": {
    "md5": "c1d5cbeb7127a672211dd56b28603a8f", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/icu-54.1-0.tar.bz2"
  }, 
  "idna-2.1-py27_0": {
    "md5": "f936e2a7ff6b5dec2e7390d85e74b42d", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/idna-2.1-py27_0.tar.bz2"
  }, 
  "imagesize-0.7.1-py27_0": {
    "md5": "998736603119925e8aa7eaf9d052d747", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/imagesize-0.7.1-py27_0.tar.bz2"
  }, 
  "ipaddress-1.0.16-py27_0": {
    "md5": "9966d3f11a711d773ee4d7a834b3617e", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/ipaddress-1.0.16-py27_0.tar.bz2"
  }, 
  "ipykernel-4.5.0-py27_0": {
    "md5": "79412c0a2b843be592f3d387b33ef7b0", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/ipykernel-4.5.0-py27_0.tar.bz2"
  }, 
  "ipython-5.1.0-py27_0": {
    "md5": "6cd149df123c8bd005239638834b675b", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/ipython-5.1.0-py27_0.tar.bz2"
  }, 
  "ipython_genutils-0.1.0-py27_0": {
    "md5": "631fa79f4747effcfc95acbfff2fa4bd", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/ipython_genutils-0.1.0-py27_0.tar.bz2"
  }, 
  "ipywidgets-5.2.2-py27_0": {
    "md5": "8f198cce3e4a2a3ff3fd64bb6daacac6", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/ipywidgets-5.2.2-py27_0.tar.bz2"
  }, 
  "itsdangerous-0.24-py27_0": {
    "md5": "48295d6fb79e3c601a611515e5d9a6f6", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/itsdangerous-0.24-py27_0.tar.bz2"
  }, 
  "jbig-2.1-0": {
    "md5": "334b102413fec962bf65c4d60697da34", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jbig-2.1-0.tar.bz2"
  }, 
  "jdcal-1.2-py27_1": {
    "md5": "03859eea9c7e008ef91a592aa1fb1603", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jdcal-1.2-py27_1.tar.bz2"
  }, 
  "jedi-0.9.0-py27_1": {
    "md5": "e404420b7c2d27b529e502bcd25bf0dc", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jedi-0.9.0-py27_1.tar.bz2"
  }, 
  "jinja2-2.8-py27_1": {
    "md5": "24429f582bcb4cd7b1e67f65ee65b152", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jinja2-2.8-py27_1.tar.bz2"
  }, 
  "jpeg-8d-2": {
    "md5": "358a79e5fc4d3696a22af423dca52366", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jpeg-8d-2.tar.bz2"
  }, 
  "jsonschema-2.5.1-py27_0": {
    "md5": "58aa76b63e73f5bc79f4084cf6970cd4", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jsonschema-2.5.1-py27_0.tar.bz2"
  }, 
  "jupyter-1.0.0-py27_3": {
    "md5": "5aa301ad67ff8d6bef6a94015f769c77", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jupyter-1.0.0-py27_3.tar.bz2"
  }, 
  "jupyter_client-4.4.0-py27_0": {
    "md5": "d4a8c6194ea81f29f2d9165d03da6417", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jupyter_client-4.4.0-py27_0.tar.bz2"
  }, 
  "jupyter_console-5.0.0-py27_0": {
    "md5": "017b6d9f5ab5a75901313b8a72cbac7a", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jupyter_console-5.0.0-py27_0.tar.bz2"
  }, 
  "jupyter_core-4.2.0-py27_0": {
    "md5": "a43359146ee64179bfa4ddd2082876da", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/jupyter_core-4.2.0-py27_0.tar.bz2"
  }, 
  "lazy-object-proxy-1.2.1-py27_0": {
    "md5": "7c98ebde49571f43feaafa0584e7f983", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/lazy-object-proxy-1.2.1-py27_0.tar.bz2"
  }, 
  "libdynd-0.7.2-0": {
    "md5": "e9269a41a8e4a30f5f133f885d45f131", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libdynd-0.7.2-0.tar.bz2"
  }, 
  "libffi-3.2.1-0": {
    "md5": "33d6314ee39e7e340a7000d4805792b9", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libffi-3.2.1-0.tar.bz2"
  }, 
  "libgcc-4.8.5-2": {
    "md5": "fb7f042b7146a04e13597d7a20fe70b1", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libgcc-4.8.5-2.tar.bz2"
  }, 
  "libgfortran-3.0.0-1": {
    "md5": "d7c7e92a8ccc518709474dd3eda896b9", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libgfortran-3.0.0-1.tar.bz2"
  }, 
  "libpng-1.6.22-0": {
    "md5": "0467dfd6506a6edede2008da1b78e616", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libpng-1.6.22-0.tar.bz2"
  }, 
  "libsodium-1.0.10-0": {
    "md5": "bdc90579f54cf2cbcd5c0ec67247cfad", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libsodium-1.0.10-0.tar.bz2"
  }, 
  "libtiff-4.0.6-2": {
    "md5": "93159eed5cfc0044bd13e67672e7a28e", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libtiff-4.0.6-2.tar.bz2"
  }, 
  "libxcb-1.12-0": {
    "md5": "5289969a123ceb8f48da6bf1e9a02737", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libxcb-1.12-0.tar.bz2"
  }, 
  "libxml2-2.9.2-0": {
    "md5": "b0b1a3f8274a41231e25f15990975446", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libxml2-2.9.2-0.tar.bz2"
  }, 
  "libxslt-1.1.28-0": {
    "md5": "656b77543a90549faa4ef443bc7cc26e", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/libxslt-1.1.28-0.tar.bz2"
  }, 
  "llvmlite-0.13.0-py27_0": {
    "md5": "dfccda5d73fa61101685e060d6cca4c4", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/llvmlite-0.13.0-py27_0.tar.bz2"
  }, 
  "locket-0.2.0-py27_1": {
    "md5": "b0743bf6a6bf3d830f56e7858473edc2", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/locket-0.2.0-py27_1.tar.bz2"
  }, 
  "lxml-3.6.4-py27_0": {
    "md5": "442e325004fde4b867649cfb1fa5d136", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/lxml-3.6.4-py27_0.tar.bz2"
  }, 
  "markupsafe-0.23-py27_2": {
    "md5": "6309f1cf8fe22fe6c09c8085e878f386", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/markupsafe-0.23-py27_2.tar.bz2"
  }, 
  "matplotlib-1.5.3-np111py27_0": {
    "md5": "7bda1380fe993f227409bd2e5c0cf72f", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/matplotlib-1.5.3-np111py27_0.tar.bz2"
  }, 
  "mistune-0.7.3-py27_0": {
    "md5": "922ed441ee473ff94555b1ed1d35cedd", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/mistune-0.7.3-py27_0.tar.bz2"
  }, 
  "mkl-11.3.3-0": {
    "md5": "8eb22d7fda5328b19631ce2b969c4018", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/mkl-11.3.3-0.tar.bz2"
  }, 
  "mkl-service-1.1.2-py27_2": {
    "md5": "44c25ed9743b8a309a0784e5d4748000", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/mkl-service-1.1.2-py27_2.tar.bz2"
  }, 
  "mpmath-0.19-py27_1": {
    "md5": "e583fcd7efb1aaf5cac4ac31549f1f54", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/mpmath-0.19-py27_1.tar.bz2"
  }, 
  "multipledispatch-0.4.8-py27_0": {
    "md5": "018a550bf92b18f476348f9adc9b321e", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/multipledispatch-0.4.8-py27_0.tar.bz2"
  }, 
  "nb_anacondacloud-1.2.0-py27_0": {
    "md5": "55817c6e5425a721c921e92c3bad864a", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/nb_anacondacloud-1.2.0-py27_0.tar.bz2"
  }, 
  "nb_conda-2.0.0-py27_0": {
    "md5": "c490cab061470e8568e71231e5530e39", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/nb_conda-2.0.0-py27_0.tar.bz2"
  }, 
  "nb_conda_kernels-2.0.0-py27_0": {
    "md5": "b11fa91a1c4312ce21a045295a9e3aaf", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/nb_conda_kernels-2.0.0-py27_0.tar.bz2"
  }, 
  "nbconvert-4.2.0-py27_0": {
    "md5": "f683f1fe1fa57cd7e26e712659653c91", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/nbconvert-4.2.0-py27_0.tar.bz2"
  }, 
  "nbformat-4.1.0-py27_0": {
    "md5": "5862b1e921b1069928be510b97dbb003", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/nbformat-4.1.0-py27_0.tar.bz2"
  }, 
  "nbpresent-3.0.2-py27_0": {
    "md5": "a3d018343452a6a881c714c1f9e98e2d", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/nbpresent-3.0.2-py27_0.tar.bz2"
  }, 
  "networkx-1.11-py27_0": {
    "md5": "58015d5d4b112797b0ae0e9fa685476c", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/networkx-1.11-py27_0.tar.bz2"
  }, 
  "nltk-3.2.1-py27_0": {
    "md5": "e904619625ff0f7fc140ba8b79f46ee5", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/nltk-3.2.1-py27_0.tar.bz2"
  }, 
  "nose-1.3.7-py27_1": {
    "md5": "2d066c04cbb6d7315b627a74f3aba8b5", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/nose-1.3.7-py27_1.tar.bz2"
  }, 
  "notebook-4.2.3-py27_0": {
    "md5": "23e64c0896a8657f07f7ea16dbd009be", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/notebook-4.2.3-py27_0.tar.bz2"
  }, 
  "numba-0.28.1-np111py27_0": {
    "md5": "3810c834d93c5283bec85c90c9a676c3", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/numba-0.28.1-np111py27_0.tar.bz2"
  }, 
  "numexpr-2.6.1-np111py27_0": {
    "md5": "7729ad8a07974e1a16681bd1573081f7", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/numexpr-2.6.1-np111py27_0.tar.bz2"
  }, 
  "numpy-1.11.1-py27_0": {
    "md5": "1b5d7f9c1b555bf1b346c066c6b72cff", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/numpy-1.11.1-py27_0.tar.bz2"
  }, 
  "odo-0.5.0-py27_1": {
    "md5": "c5571a70751613e86a658d76cec5448d", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/odo-0.5.0-py27_1.tar.bz2"
  }, 
  "openpyxl-2.3.2-py27_0": {
    "md5": "35e3d3a2fc58bc0b3c7f9e57591702c8", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/openpyxl-2.3.2-py27_0.tar.bz2"
  }, 
  "openssl-1.0.2j-0": {
    "md5": "1c4e45f6fd4bb96e50921dbc06107fe3", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/openssl-1.0.2j-0.tar.bz2"
  }, 
  "pandas-0.18.1-np111py27_0": {
    "md5": "79a27fd75bf602b1484c7bbe3bba7e87", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pandas-0.18.1-np111py27_0.tar.bz2"
  }, 
  "partd-0.3.6-py27_0": {
    "md5": "61424c7587237831fc36b883e09e5ca0", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/partd-0.3.6-py27_0.tar.bz2"
  }, 
  "patchelf-0.9-0": {
    "md5": "656235794faa13f6a472c39c27b1e3f8", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/patchelf-0.9-0.tar.bz2"
  }, 
  "path.py-8.2.1-py27_0": {
    "md5": "f9083a8b015b76a916de6806940eb91a", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/path.py-8.2.1-py27_0.tar.bz2"
  }, 
  "pathlib2-2.1.0-py27_0": {
    "md5": "1e838a275cda673686401d93ec93d257", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pathlib2-2.1.0-py27_0.tar.bz2"
  }, 
  "patsy-0.4.1-py27_0": {
    "md5": "b78c3447b7cfab154b81571d2b011879", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/patsy-0.4.1-py27_0.tar.bz2"
  }, 
  "pep8-1.7.0-py27_0": {
    "md5": "f05d5198f0cc6830b624a732094ed965", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pep8-1.7.0-py27_0.tar.bz2"
  }, 
  "pexpect-4.0.1-py27_0": {
    "md5": "a4199a8c031e00cbaf9a4a57f1b86b59", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pexpect-4.0.1-py27_0.tar.bz2"
  }, 
  "pickleshare-0.7.4-py27_0": {
    "md5": "f60435aca432d6f1ec0c88df78b7ffc1", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pickleshare-0.7.4-py27_0.tar.bz2"
  }, 
  "pillow-3.3.1-py27_0": {
    "md5": "e064546ede160b61ddd5cc66637739ff", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pillow-3.3.1-py27_0.tar.bz2"
  }, 
  "pip-8.1.2-py27_0": {
    "md5": "8803777cb8b31eaf8949f9023affefa3", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pip-8.1.2-py27_0.tar.bz2"
  }, 
  "pixman-0.32.6-0": {
    "md5": "c62c2fe17ebb77464fc7a6272f97562d", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pixman-0.32.6-0.tar.bz2"
  }, 
  "pkginfo-1.3.2-py27_0": {
    "md5": "7b766e99dfc2f2468ac34b99254b090c", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pkginfo-1.3.2-py27_0.tar.bz2"
  }, 
  "ply-3.9-py27_0": {
    "md5": "a22941216dddaf8ac3bf5b68822ed47e", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/ply-3.9-py27_0.tar.bz2"
  }, 
  "prompt_toolkit-1.0.3-py27_0": {
    "md5": "0993e951d8afb8fe0782c1bccbfb4777", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/prompt_toolkit-1.0.3-py27_0.tar.bz2"
  }, 
  "psutil-4.3.1-py27_0": {
    "md5": "ad9e10afe86b0653dd85804f24b55e03", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/psutil-4.3.1-py27_0.tar.bz2"
  }, 
  "ptyprocess-0.5.1-py27_0": {
    "md5": "4c1006e594173fb0eccb8fcd7b9ab1ad", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/ptyprocess-0.5.1-py27_0.tar.bz2"
  }, 
  "py-1.4.31-py27_0": {
    "md5": "dea3d93be766654470ef77cd78ffa109", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/py-1.4.31-py27_0.tar.bz2"
  }, 
  "pyasn1-0.1.9-py27_0": {
    "md5": "57df6120bc6e1f24df4a8bceeb01d592", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pyasn1-0.1.9-py27_0.tar.bz2"
  }, 
  "pycairo-1.10.0-py27_0": {
    "md5": "fad9b73e4e310fb1a2169d78452ce9ec", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pycairo-1.10.0-py27_0.tar.bz2"
  }, 
  "pycosat-0.6.1-py27_1": {
    "md5": "c2655879ca20ab4969fd16699be1b4eb", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pycosat-0.6.1-py27_1.tar.bz2"
  }, 
  "pycparser-2.14-py27_1": {
    "md5": "f25503ba0ce328b1f3d85a12ce374568", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pycparser-2.14-py27_1.tar.bz2"
  }, 
  "pycrypto-2.6.1-py27_4": {
    "md5": "e8417ecd0f1f0d45f704bdd9fdfa9158", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pycrypto-2.6.1-py27_4.tar.bz2"
  }, 
  "pycurl-7.43.0-py27_0": {
    "md5": "10dc1d32f45b0a1127a2c092121426d1", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pycurl-7.43.0-py27_0.tar.bz2"
  }, 
  "pyflakes-1.3.0-py27_0": {
    "md5": "dceaf010ede6e648aea4ac7cdec89973", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pyflakes-1.3.0-py27_0.tar.bz2"
  }, 
  "pygments-2.1.3-py27_0": {
    "md5": "c905248d7d0b72e773051522935b0fb3", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pygments-2.1.3-py27_0.tar.bz2"
  }, 
  "pylint-1.5.4-py27_1": {
    "md5": "ba871cb22ce0a89c2a6f53f393447986", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pylint-1.5.4-py27_1.tar.bz2"
  }, 
  "pyopenssl-16.0.0-py27_0": {
    "md5": "827b9b47e26d7f22eebd58de08b72c5a", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pyopenssl-16.0.0-py27_0.tar.bz2"
  }, 
  "pyparsing-2.1.4-py27_0": {
    "md5": "8aaec959dfb65042e4dff555ffb83c26", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pyparsing-2.1.4-py27_0.tar.bz2"
  }, 
  "pyqt-5.6.0-py27_0": {
    "md5": "0db15433bd3a8d21169ec16e3acdfb85", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pyqt-5.6.0-py27_0.tar.bz2"
  }, 
  "pytables-3.2.3.1-np111py27_0": {
    "md5": "09ea5ed878fe2f344f377830abc3d837", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pytables-3.2.3.1-np111py27_0.tar.bz2"
  }, 
  "pytest-2.9.2-py27_0": {
    "md5": "58be3a3a1df55b8c8e7e6b829af46448", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pytest-2.9.2-py27_0.tar.bz2"
  }, 
  "python-2.7.12-1": {
    "md5": "bb956a5d1012b116dc3d89c9cf876bc5", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/python-2.7.12-1.tar.bz2"
  }, 
  "python-dateutil-2.5.3-py27_0": {
    "md5": "39119a3715a0f93f03a0df9d18f44e67", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/python-dateutil-2.5.3-py27_0.tar.bz2"
  }, 
  "pytz-2016.6.1-py27_0": {
    "md5": "744284fcebd53fedccd4cabb92d3ff1d", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pytz-2016.6.1-py27_0.tar.bz2"
  }, 
  "pyyaml-3.12-py27_0": {
    "md5": "02c068a0959abe5a83b15a2b022d886a", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pyyaml-3.12-py27_0.tar.bz2"
  }, 
  "pyzmq-15.4.0-py27_0": {
    "md5": "ba9b00567a0bd914fc9ac9763da0e8b4", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/pyzmq-15.4.0-py27_0.tar.bz2"
  }, 
  "qt-5.6.0-0": {
    "md5": "19733836e59104a824dcb717c6b29814", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/qt-5.6.0-0.tar.bz2"
  }, 
  "qtawesome-0.3.3-py27_0": {
    "md5": "6a708ab38df9da60ee46ee1897445754", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/qtawesome-0.3.3-py27_0.tar.bz2"
  }, 
  "qtconsole-4.2.1-py27_1": {
    "md5": "10f06a650c7d68afbc84651fbcf3497e", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/qtconsole-4.2.1-py27_1.tar.bz2"
  }, 
  "qtpy-1.1.2-py27_0": {
    "md5": "eff5bcad1b51f319a14df6b4bf002681", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/qtpy-1.1.2-py27_0.tar.bz2"
  }, 
  "readline-6.2-2": {
    "md5": "d050607fb2934282470d06872e0e6cce", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/readline-6.2-2.tar.bz2"
  }, 
  "redis-3.2.0-0": {
    "md5": "59f3bfa2246c4e53c5fdb2dc7f0da5b8", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/redis-3.2.0-0.tar.bz2"
  }, 
  "redis-py-2.10.5-py27_0": {
    "md5": "353ff8eecad2172d1f798236f0ef33e7", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/redis-py-2.10.5-py27_0.tar.bz2"
  }, 
  "requests-2.11.1-py27_0": {
    "md5": "28e486576b3b6c04284251174f0b3e3a", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/requests-2.11.1-py27_0.tar.bz2"
  }, 
  "rope-0.9.4-py27_1": {
    "md5": "e6017d8b755b05462880c7d30cf581e1", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/rope-0.9.4-py27_1.tar.bz2"
  }, 
  "ruamel_yaml-0.11.14-py27_0": {
    "md5": "5f1513fe0b1a117742ccd17edd122067", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/ruamel_yaml-0.11.14-py27_0.tar.bz2"
  }, 
  "scikit-image-0.12.3-np111py27_1": {
    "md5": "30e0f47d0c5a0900b441239fd2c6d6a6", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/scikit-image-0.12.3-np111py27_1.tar.bz2"
  }, 
  "scikit-learn-0.17.1-np111py27_2": {
    "md5": "62418164d875b99b91929c06451f56f6", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/scikit-learn-0.17.1-np111py27_2.tar.bz2"
  }, 
  "scipy-0.18.1-np111py27_0": {
    "md5": "d15e512ae2c85c22e38c05555be0888c", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/scipy-0.18.1-np111py27_0.tar.bz2"
  }, 
  "setuptools-27.2.0-py27_0": {
    "md5": "96b639928547b4f837f7d4d1ed5f2d7e", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/setuptools-27.2.0-py27_0.tar.bz2"
  }, 
  "simplegeneric-0.8.1-py27_1": {
    "md5": "419ef3d6235392a86d24867981306107", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/simplegeneric-0.8.1-py27_1.tar.bz2"
  }, 
  "singledispatch-3.4.0.3-py27_0": {
    "md5": "95ce90450ee1287efc3f3f7c70efc990", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/singledispatch-3.4.0.3-py27_0.tar.bz2"
  }, 
  "sip-4.18-py27_0": {
    "md5": "d8443d26dcaf83587f21eedb9c447da2", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/sip-4.18-py27_0.tar.bz2"
  }, 
  "six-1.10.0-py27_0": {
    "md5": "78d229dce568dd4bac1d88328f822fc5", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/six-1.10.0-py27_0.tar.bz2"
  }, 
  "snowballstemmer-1.2.1-py27_0": {
    "md5": "0834f6476d1d750a3654346a7dad8747", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/snowballstemmer-1.2.1-py27_0.tar.bz2"
  }, 
  "sockjs-tornado-1.0.3-py27_0": {
    "md5": "a3145cf16cb48ec6cc3e55e0c28db343", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/sockjs-tornado-1.0.3-py27_0.tar.bz2"
  }, 
  "sphinx-1.4.6-py27_0": {
    "md5": "429c19ecff448a36aa1b097eb204deef", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/sphinx-1.4.6-py27_0.tar.bz2"
  }, 
  "spyder-3.0.0-py27_0": {
    "md5": "216d7c09c1ebddbfda9c6ce48983a814", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/spyder-3.0.0-py27_0.tar.bz2"
  }, 
  "sqlalchemy-1.0.13-py27_0": {
    "md5": "c82c6cb0eb280b94f395562104f4ad14", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/sqlalchemy-1.0.13-py27_0.tar.bz2"
  }, 
  "sqlite-3.13.0-0": {
    "md5": "ceb2d63b0dc2ec8a2e1da9378f07ab98", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/sqlite-3.13.0-0.tar.bz2"
  }, 
  "ssl_match_hostname-3.4.0.2-py27_1": {
    "md5": "ffca0f9278ac34828b183820aa868c5d", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/ssl_match_hostname-3.4.0.2-py27_1.tar.bz2"
  }, 
  "statsmodels-0.6.1-np111py27_1": {
    "md5": "6c0610a8f5d3510a213a2416eaae6f9c", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/statsmodels-0.6.1-np111py27_1.tar.bz2"
  }, 
  "sympy-1.0-py27_0": {
    "md5": "e96b1b72f0e023184d6c32f620932ae9", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/sympy-1.0-py27_0.tar.bz2"
  }, 
  "terminado-0.6-py27_0": {
    "md5": "9f4870fb0d8ece71313189019b1c4163", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/terminado-0.6-py27_0.tar.bz2"
  }, 
  "tk-8.5.18-0": {
    "md5": "902f0fd689a01a835c9e69aefbe58fdd", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/tk-8.5.18-0.tar.bz2"
  }, 
  "toolz-0.8.0-py27_0": {
    "md5": "ff81cf0c0ad3d820251f579a619d6f7e", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/toolz-0.8.0-py27_0.tar.bz2"
  }, 
  "tornado-4.4.1-py27_0": {
    "md5": "1d6b534d946e54394a7e13bb61a2f619", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/tornado-4.4.1-py27_0.tar.bz2"
  }, 
  "traitlets-4.3.0-py27_0": {
    "md5": "a48a1bf098cb0ddc22c25f6da1c576d6", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/traitlets-4.3.0-py27_0.tar.bz2"
  }, 
  "unicodecsv-0.14.1-py27_0": {
    "md5": "17f5af29c443f26fa707b901aa54b8e6", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/unicodecsv-0.14.1-py27_0.tar.bz2"
  }, 
  "wcwidth-0.1.7-py27_0": {
    "md5": "2b9c7073f1210540923cf36f6053eb61", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/wcwidth-0.1.7-py27_0.tar.bz2"
  }, 
  "werkzeug-0.11.11-py27_0": {
    "md5": "4de63d30c224a11f16817710414b9a90", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/werkzeug-0.11.11-py27_0.tar.bz2"
  }, 
  "wheel-0.29.0-py27_0": {
    "md5": "35cf0da93616ea8c495ce1d143316d7c", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/wheel-0.29.0-py27_0.tar.bz2"
  }, 
  "widgetsnbextension-1.2.6-py27_0": {
    "md5": "23c28ea0d5492af41f8d0a080ca5e2ca", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/widgetsnbextension-1.2.6-py27_0.tar.bz2"
  }, 
  "wrapt-1.10.6-py27_0": {
    "md5": "e702b3e8bbba0cae3b483db4c9cfbb10", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/wrapt-1.10.6-py27_0.tar.bz2"
  }, 
  "xlrd-1.0.0-py27_0": {
    "md5": "e6a6cacdeb0f68b76913f8699c5ca6c1", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/xlrd-1.0.0-py27_0.tar.bz2"
  }, 
  "xlsxwriter-0.9.3-py27_0": {
    "md5": "eaed17272dde79cf2065c6b9c3de4c73", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/xlsxwriter-0.9.3-py27_0.tar.bz2"
  }, 
  "xlwt-1.1.2-py27_0": {
    "md5": "34785be60ec18d68a792bbc14b9dc6b0", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/xlwt-1.1.2-py27_0.tar.bz2"
  }, 
  "xz-5.2.2-0": {
    "md5": "e695dd33979086349147a4f354f5c2bd", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/xz-5.2.2-0.tar.bz2"
  }, 
  "yaml-0.1.6-0": {
    "md5": "dac36570434ddc9e16e54709c114bd96", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/yaml-0.1.6-0.tar.bz2"
  }, 
  "zeromq-4.1.4-0": {
    "md5": "3ca5060fe4311d8d098d4e005f198c16", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/zeromq-4.1.4-0.tar.bz2"
  }, 
  "zlib-1.2.8-3": {
    "md5": "60d5ea874984e4c750f187a26c827382", 
    "url": "https://repo.continuum.io/pkgs/free/linux-64/zlib-1.2.8-3.tar.bz2"
  }
}
C_ENVS = {
  "root": [
    "python-2.7.12-1", 
    "_license-1.1-py27_1", 
    "_nb_ext_conf-0.3.0-py27_0", 
    "alabaster-0.7.9-py27_0", 
    "anaconda-clean-1.0.0-py27_0", 
    "anaconda-client-1.5.1-py27_0", 
    "anaconda-navigator-1.3.1-py27_0", 
    "argcomplete-1.0.0-py27_1", 
    "astroid-1.4.7-py27_0", 
    "astropy-1.2.1-np111py27_0", 
    "babel-2.3.4-py27_0", 
    "backports-1.0-py27_0", 
    "backports_abc-0.4-py27_0", 
    "beautifulsoup4-4.5.1-py27_0", 
    "bitarray-0.8.1-py27_0", 
    "blaze-0.10.1-py27_0", 
    "bokeh-0.12.2-py27_0", 
    "boto-2.42.0-py27_0", 
    "bottleneck-1.1.0-np111py27_0", 
    "cairo-1.12.18-6", 
    "cdecimal-2.3-py27_2", 
    "cffi-1.7.0-py27_0", 
    "chest-0.2.3-py27_0", 
    "click-6.6-py27_0", 
    "cloudpickle-0.2.1-py27_0", 
    "clyent-1.2.2-py27_0", 
    "colorama-0.3.7-py27_0", 
    "configobj-5.0.6-py27_0", 
    "configparser-3.5.0-py27_0", 
    "contextlib2-0.5.3-py27_0", 
    "cryptography-1.5-py27_0", 
    "curl-7.49.0-1", 
    "cycler-0.10.0-py27_0", 
    "cython-0.24.1-py27_0", 
    "cytoolz-0.8.0-py27_0", 
    "dask-0.11.0-py27_0", 
    "datashape-0.5.2-py27_0", 
    "dbus-1.10.10-0", 
    "decorator-4.0.10-py27_0", 
    "dill-0.2.5-py27_0", 
    "docutils-0.12-py27_2", 
    "dynd-python-0.7.2-py27_0", 
    "entrypoints-0.2.2-py27_0", 
    "enum34-1.1.6-py27_0", 
    "et_xmlfile-1.0.1-py27_0", 
    "expat-2.1.0-0", 
    "fastcache-1.0.2-py27_1", 
    "filelock-2.0.6-py27_0", 
    "flask-0.11.1-py27_0", 
    "flask-cors-2.1.2-py27_0", 
    "fontconfig-2.11.1-6", 
    "freetype-2.5.5-1", 
    "funcsigs-1.0.2-py27_0", 
    "functools32-3.2.3.2-py27_0", 
    "futures-3.0.5-py27_0", 
    "get_terminal_size-1.0.0-py27_0", 
    "gevent-1.1.2-py27_0", 
    "glib-2.43.0-1", 
    "greenlet-0.4.10-py27_0", 
    "grin-1.2.1-py27_3", 
    "gst-plugins-base-1.8.0-0", 
    "gstreamer-1.8.0-0", 
    "h5py-2.6.0-np111py27_2", 
    "harfbuzz-0.9.39-1", 
    "hdf5-1.8.17-1", 
    "heapdict-1.0.0-py27_1", 
    "icu-54.1-0", 
    "idna-2.1-py27_0", 
    "imagesize-0.7.1-py27_0", 
    "ipaddress-1.0.16-py27_0", 
    "ipykernel-4.5.0-py27_0", 
    "ipython-5.1.0-py27_0", 
    "ipython_genutils-0.1.0-py27_0", 
    "ipywidgets-5.2.2-py27_0", 
    "itsdangerous-0.24-py27_0", 
    "jbig-2.1-0", 
    "jdcal-1.2-py27_1", 
    "jedi-0.9.0-py27_1", 
    "jinja2-2.8-py27_1", 
    "jpeg-8d-2", 
    "jsonschema-2.5.1-py27_0", 
    "jupyter-1.0.0-py27_3", 
    "jupyter_client-4.4.0-py27_0", 
    "jupyter_console-5.0.0-py27_0", 
    "jupyter_core-4.2.0-py27_0", 
    "lazy-object-proxy-1.2.1-py27_0", 
    "libdynd-0.7.2-0", 
    "libffi-3.2.1-0", 
    "libgcc-4.8.5-2", 
    "libgfortran-3.0.0-1", 
    "libpng-1.6.22-0", 
    "libsodium-1.0.10-0", 
    "libtiff-4.0.6-2", 
    "libxcb-1.12-0", 
    "libxml2-2.9.2-0", 
    "libxslt-1.1.28-0", 
    "llvmlite-0.13.0-py27_0", 
    "locket-0.2.0-py27_1", 
    "lxml-3.6.4-py27_0", 
    "markupsafe-0.23-py27_2", 
    "matplotlib-1.5.3-np111py27_0", 
    "mistune-0.7.3-py27_0", 
    "mkl-11.3.3-0", 
    "mkl-service-1.1.2-py27_2", 
    "mpmath-0.19-py27_1", 
    "multipledispatch-0.4.8-py27_0", 
    "nb_anacondacloud-1.2.0-py27_0", 
    "nb_conda-2.0.0-py27_0", 
    "nb_conda_kernels-2.0.0-py27_0", 
    "nbconvert-4.2.0-py27_0", 
    "nbformat-4.1.0-py27_0", 
    "nbpresent-3.0.2-py27_0", 
    "networkx-1.11-py27_0", 
    "nltk-3.2.1-py27_0", 
    "nose-1.3.7-py27_1", 
    "notebook-4.2.3-py27_0", 
    "numba-0.28.1-np111py27_0", 
    "numexpr-2.6.1-np111py27_0", 
    "numpy-1.11.1-py27_0", 
    "odo-0.5.0-py27_1", 
    "openpyxl-2.3.2-py27_0", 
    "openssl-1.0.2j-0", 
    "pandas-0.18.1-np111py27_0", 
    "partd-0.3.6-py27_0", 
    "patchelf-0.9-0", 
    "path.py-8.2.1-py27_0", 
    "pathlib2-2.1.0-py27_0", 
    "patsy-0.4.1-py27_0", 
    "pep8-1.7.0-py27_0", 
    "pexpect-4.0.1-py27_0", 
    "pickleshare-0.7.4-py27_0", 
    "pillow-3.3.1-py27_0", 
    "pip-8.1.2-py27_0", 
    "pixman-0.32.6-0", 
    "pkginfo-1.3.2-py27_0", 
    "ply-3.9-py27_0", 
    "prompt_toolkit-1.0.3-py27_0", 
    "psutil-4.3.1-py27_0", 
    "ptyprocess-0.5.1-py27_0", 
    "py-1.4.31-py27_0", 
    "pyasn1-0.1.9-py27_0", 
    "pycairo-1.10.0-py27_0", 
    "pycosat-0.6.1-py27_1", 
    "pycparser-2.14-py27_1", 
    "pycrypto-2.6.1-py27_4", 
    "pycurl-7.43.0-py27_0", 
    "pyflakes-1.3.0-py27_0", 
    "pygments-2.1.3-py27_0", 
    "pylint-1.5.4-py27_1", 
    "pyopenssl-16.0.0-py27_0", 
    "pyparsing-2.1.4-py27_0", 
    "pyqt-5.6.0-py27_0", 
    "pytables-3.2.3.1-np111py27_0", 
    "pytest-2.9.2-py27_0", 
    "python-dateutil-2.5.3-py27_0", 
    "pytz-2016.6.1-py27_0", 
    "pyyaml-3.12-py27_0", 
    "pyzmq-15.4.0-py27_0", 
    "qt-5.6.0-0", 
    "qtawesome-0.3.3-py27_0", 
    "qtconsole-4.2.1-py27_1", 
    "qtpy-1.1.2-py27_0", 
    "readline-6.2-2", 
    "redis-3.2.0-0", 
    "redis-py-2.10.5-py27_0", 
    "requests-2.11.1-py27_0", 
    "rope-0.9.4-py27_1", 
    "scikit-image-0.12.3-np111py27_1", 
    "scikit-learn-0.17.1-np111py27_2", 
    "scipy-0.18.1-np111py27_0", 
    "setuptools-27.2.0-py27_0", 
    "simplegeneric-0.8.1-py27_1", 
    "singledispatch-3.4.0.3-py27_0", 
    "sip-4.18-py27_0", 
    "six-1.10.0-py27_0", 
    "snowballstemmer-1.2.1-py27_0", 
    "sockjs-tornado-1.0.3-py27_0", 
    "sphinx-1.4.6-py27_0", 
    "spyder-3.0.0-py27_0", 
    "sqlalchemy-1.0.13-py27_0", 
    "sqlite-3.13.0-0", 
    "ssl_match_hostname-3.4.0.2-py27_1", 
    "statsmodels-0.6.1-np111py27_1", 
    "sympy-1.0-py27_0", 
    "terminado-0.6-py27_0", 
    "tk-8.5.18-0", 
    "toolz-0.8.0-py27_0", 
    "tornado-4.4.1-py27_0", 
    "traitlets-4.3.0-py27_0", 
    "unicodecsv-0.14.1-py27_0", 
    "wcwidth-0.1.7-py27_0", 
    "werkzeug-0.11.11-py27_0", 
    "wheel-0.29.0-py27_0", 
    "widgetsnbextension-1.2.6-py27_0", 
    "wrapt-1.10.6-py27_0", 
    "xlrd-1.0.0-py27_0", 
    "xlsxwriter-0.9.3-py27_0", 
    "xlwt-1.1.2-py27_0", 
    "xz-5.2.2-0", 
    "yaml-0.1.6-0", 
    "zeromq-4.1.4-0", 
    "zlib-1.2.8-3", 
    "anaconda-4.2.0-np111py27_0", 
    "ruamel_yaml-0.11.14-py27_0", 
    "conda-4.2.9-py27_0", 
    "conda-build-2.0.2-py27_0"
  ]
}



def _link(src, dst, linktype=LINK_HARD):
    if on_win:
        raise NotImplementedError

    if linktype == LINK_HARD:
        os.link(src, dst)
    elif linktype == LINK_COPY:
        # copy relative symlinks as symlinks
        if islink(src) and not os.readlink(src).startswith('/'):
            os.symlink(os.readlink(src), dst)
        else:
            shutil.copy2(src, dst)
    else:
        raise Exception("Did not expect linktype=%r" % linktype)


def rm_rf(path):
    """
    try to delete path, but never fail
    """
    try:
        if islink(path) or isfile(path):
            # Note that we have to check if the destination is a link because
            # exists('/path/to/dead-link') will return False, although
            # islink('/path/to/dead-link') is True.
            os.unlink(path)
        elif isdir(path):
            shutil.rmtree(path)
    except (OSError, IOError):
        pass


def yield_lines(path):
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        yield line


prefix_placeholder = ('/opt/anaconda1anaconda2'
                      # this is intentionally split into parts,
                      # such that running this program on itself
                      # will leave it unchanged
                      'anaconda3')

def read_has_prefix(path):
    """
    reads `has_prefix` file and return dict mapping filenames to
    tuples(placeholder, mode)
    """
    import shlex

    res = {}
    try:
        for line in yield_lines(path):
            try:
                placeholder, mode, f = [x.strip('"\'') for x in
                                        shlex.split(line, posix=False)]
                res[f] = (placeholder, mode)
            except ValueError:
                res[line] = (prefix_placeholder, 'text')
    except IOError:
        pass
    return res


def exp_backoff_fn(fn, *args):
    """
    for retrying file operations that fail on Windows due to virus scanners
    """
    if not on_win:
        return fn(*args)

    import time
    import errno
    max_tries = 6  # max total time = 6.4 sec
    for n in range(max_tries):
        try:
            result = fn(*args)
        except (OSError, IOError) as e:
            if e.errno in (errno.EPERM, errno.EACCES):
                if n == max_tries - 1:
                    raise Exception("max_tries=%d reached" % max_tries)
                time.sleep(0.1 * (2 ** n))
            else:
                raise e
        else:
            return result


class PaddingError(Exception):
    pass


def binary_replace(data, a, b):
    """
    Perform a binary replacement of `data`, where the placeholder `a` is
    replaced with `b` and the remaining string is padded with null characters.
    All input arguments are expected to be bytes objects.
    """
    def replace(match):
        occurances = match.group().count(a)
        padding = (len(a) - len(b)) * occurances
        if padding < 0:
            raise PaddingError(a, b, padding)
        return match.group().replace(a, b) + b'\0' * padding

    pat = re.compile(re.escape(a) + b'([^\0]*?)\0')
    res = pat.sub(replace, data)
    assert len(res) == len(data)
    return res


def update_prefix(path, new_prefix, placeholder, mode):
    if on_win:
        # force all prefix replacements to forward slashes to simplify need
        # to escape backslashes - replace with unix-style path separators
        new_prefix = new_prefix.replace('\\', '/')

    path = os.path.realpath(path)
    with open(path, 'rb') as fi:
        data = fi.read()
    if mode == 'text':
        new_data = data.replace(placeholder.encode('utf-8'),
                                new_prefix.encode('utf-8'))
    elif mode == 'binary':
        new_data = binary_replace(data, placeholder.encode('utf-8'),
                                  new_prefix.encode('utf-8'))
    else:
        sys.exit("Invalid mode:" % mode)

    if new_data == data:
        return
    st = os.lstat(path)
    with exp_backoff_fn(open, path, 'wb') as fo:
        fo.write(new_data)
    os.chmod(path, stat.S_IMODE(st.st_mode))


def name_dist(dist):
    return dist.rsplit('-', 2)[0]


def create_meta(prefix, dist, info_dir, extra_info):
    """
    Create the conda metadata, in a given prefix, for a given package.
    """
    # read info/index.json first
    with open(join(info_dir, 'index.json')) as fi:
        meta = json.load(fi)
    # add extra info
    meta.update(extra_info)
    # write into <prefix>/conda-meta/<dist>.json
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        os.makedirs(meta_dir)
    with open(join(meta_dir, dist + '.json'), 'w') as fo:
        json.dump(meta, fo, indent=2, sort_keys=True)


def run_script(prefix, dist, action='post-link'):
    """
    call the post-link (or pre-unlink) script, and return True on success,
    False on failure
    """
    path = join(prefix, 'Scripts' if on_win else 'bin', '.%s-%s.%s' % (
            name_dist(dist),
            action,
            'bat' if on_win else 'sh'))
    if not isfile(path):
        return True
    if SKIP_SCRIPTS:
        print("WARNING: skipping %s script by user request" % action)
        return True

    if on_win:
        try:
            args = [os.environ['COMSPEC'], '/c', path]
        except KeyError:
            return False
    else:
        shell_path = '/bin/sh' if 'bsd' in sys.platform else '/bin/bash'
        args = [shell_path, path]

    env = os.environ
    env['PREFIX'] = prefix

    import subprocess
    try:
        subprocess.check_call(args, env=env)
    except subprocess.CalledProcessError:
        return False
    return True


url_pat = re.compile(r'''
(?P<baseurl>\S+/)                 # base URL
(?P<fn>[^\s#/]+)                  # filename
([#](?P<md5>[0-9a-f]{32}))?       # optional MD5
$                                 # EOL
''', re.VERBOSE)

def read_urls(dist):
    try:
        data = open(join(PKGS_DIR, 'urls')).read()
        for line in data.split()[::-1]:
            m = url_pat.match(line)
            if m is None:
                continue
            if m.group('fn') == '%s.tar.bz2' % dist:
                return {'url': m.group('baseurl') + m.group('fn'),
                        'md5': m.group('md5')}
    except IOError:
        pass
    return {}


def read_no_link(info_dir):
    res = set()
    for fn in 'no_link', 'no_softlink':
        try:
            res.update(set(yield_lines(join(info_dir, fn))))
        except IOError:
            pass
    return res


def linked(prefix):
    """
    Return the (set of canonical names) of linked packages in prefix.
    """
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        return set()
    return set(fn[:-5] for fn in os.listdir(meta_dir) if fn.endswith('.json'))


def link(prefix, dist, linktype=LINK_HARD):
    '''
    Link a package in a specified prefix.  We assume that the packacge has
    been extra_info in either
      - <PKGS_DIR>/dist
      - <ROOT_PREFIX>/ (when the linktype is None)
    '''
    if linktype:
        source_dir = join(PKGS_DIR, dist)
        info_dir = join(source_dir, 'info')
        no_link = read_no_link(info_dir)
    else:
        info_dir = join(prefix, 'info')

    files = list(yield_lines(join(info_dir, 'files')))
    has_prefix_files = read_has_prefix(join(info_dir, 'has_prefix'))

    if linktype:
        for f in files:
            src = join(source_dir, f)
            dst = join(prefix, f)
            dst_dir = dirname(dst)
            if not isdir(dst_dir):
                os.makedirs(dst_dir)
            if exists(dst):
                if FORCE:
                    rm_rf(dst)
                else:
                    raise Exception("dst exists: %r" % dst)
            lt = linktype
            if f in has_prefix_files or f in no_link or islink(src):
                lt = LINK_COPY
            try:
                _link(src, dst, lt)
            except OSError:
                pass

    for f in sorted(has_prefix_files):
        placeholder, mode = has_prefix_files[f]
        try:
            update_prefix(join(prefix, f), prefix, placeholder, mode)
        except PaddingError:
            sys.exit("ERROR: placeholder '%s' too short in: %s\n" %
                     (placeholder, dist))

    if not run_script(prefix, dist, 'post-link'):
        sys.exit("Error: post-link failed for: %s" % dist)

    meta = {
        'files': files,
        'link': ({'source': source_dir,
                  'type': link_name_map.get(linktype)}
                 if linktype else None),
    }
    try:    # add URL and MD5
        meta.update(IDISTS[dist])
    except KeyError:
        meta.update(read_urls(dist))
    meta['installed_by'] = 'Anaconda2-4.2.0-Linux-x86_64'
    create_meta(prefix, dist, info_dir, meta)


def duplicates_to_remove(linked_dists, keep_dists):
    """
    Returns the (sorted) list of distributions to be removed, such that
    only one distribution (for each name) remains.  `keep_dists` is an
    interable of distributions (which are not allowed to be removed).
    """
    from collections import defaultdict

    keep_dists = set(keep_dists)
    ldists = defaultdict(set) # map names to set of distributions
    for dist in linked_dists:
        name = name_dist(dist)
        ldists[name].add(dist)

    res = set()
    for dists in ldists.values():
        # `dists` is the group of packages with the same name
        if len(dists) == 1:
            # if there is only one package, nothing has to be removed
            continue
        if dists & keep_dists:
            # if the group has packages which are have to be kept, we just
            # take the set of packages which are in group but not in the
            # ones which have to be kept
            res.update(dists - keep_dists)
        else:
            # otherwise, we take lowest (n-1) (sorted) packages
            res.update(sorted(dists)[:-1])
    return sorted(res)


def link_idists():
    src = join(PKGS_DIR, 'urls')
    dst = join(ROOT_PREFIX, '.hard-link')
    assert isfile(src), src
    assert not isfile(dst), dst
    try:
        _link(src, dst, LINK_HARD)
        linktype = LINK_HARD
    except OSError:
        linktype = LINK_COPY
    finally:
        rm_rf(dst)

    for env_name in sorted(C_ENVS):
        dists = C_ENVS[env_name]
        assert isinstance(dists, list)
        if len(dists) == 0:
            continue

        prefix = prefix_env(env_name)
        for dist in dists:
            assert dist in IDISTS
            link(prefix, dist, linktype)

        for dist in duplicates_to_remove(linked(prefix), dists):
            meta_path = join(prefix, 'conda-meta', dist + '.json')
            print("WARNING: unlinking: %s" % meta_path)
            try:
                os.rename(meta_path, meta_path + '.bak')
            except OSError:
                rm_rf(meta_path)


def prefix_env(env_name):
    if env_name == 'root':
        return ROOT_PREFIX
    else:
        return join(ROOT_PREFIX, 'envs', env_name)


def post_extract(env_name='root'):
    """
    assuming that the package is extracted in the environment `env_name`,
    this function does everything link() does except the actual linking,
    i.e. update prefix files, run 'post-link', creates the conda metadata,
    and removed the info/ directory afterwards.
    """
    prefix = prefix_env(env_name)
    info_dir = join(prefix, 'info')
    with open(join(info_dir, 'index.json')) as fi:
        meta = json.load(fi)
    dist = '%(name)s-%(version)s-%(build)s' % meta
    link(prefix, dist, linktype=None)
    shutil.rmtree(info_dir)


def main():
    global ROOT_PREFIX, PKGS_DIR, FORCE

    p = OptionParser(description="conda link tool used by installers")

    p.add_option('--root-prefix',
                 action="store",
                 default=abspath(join(__file__, '..', '..')),
                 help="root prefix (defaults to %default)")

    p.add_option('--post',
                 action="store",
                 help="perform post extract (on a single package), "
                      "in environment NAME",
                 metavar='NAME')

    opts, args = p.parse_args()
    if args:
        p.error('no arguments expected')

    ROOT_PREFIX = opts.root_prefix
    PKGS_DIR = join(ROOT_PREFIX, 'pkgs')

    if opts.post:
        post_extract(opts.post)
        return

    try:
        FORCE = bool(int(os.getenv('FORCE', 0)))
    except ValueError:
        FORCE = False

    if FORCE:
        print("using -f (force) option")

    link_idists()


def main2():
    global SKIP_SCRIPTS

    p = OptionParser(description="conda post extract tool used by installers")

    p.add_option('--skip-scripts',
                 action="store_true",
                 help="skip running pre/post-link scripts")

    opts, args = p.parse_args()
    if args:
        p.error('no arguments expected')

    if opts.skip_scripts:
        SKIP_SCRIPTS = True

    post_extract()


if __name__ == '__main__':
    if IDISTS:
        main()
    else: # common usecase
        main2()
