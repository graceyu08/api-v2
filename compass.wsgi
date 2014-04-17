#!/usr/bin/env python
#activate_this = "/home/grace/compass-dev/bin/activate_this.py"
#execfile(activate_this, dict(__file__=activate_this))

from compass.api import app as application
from compass.utils import flags
from compass.utils import logsetting
from compass.utils import setting_wrapper as setting

flags.init()
flags.OPTIONS.logfile = setting.WEB_LOGFILE
logsetting.init()
