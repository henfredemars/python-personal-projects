
#A dead-man's switch for sending important information in the event that I die

import smtplib
import Config
from Messages import msgs
from datetime import datetime
from datetime import timedelta
from time import sleep
import os, sys, signal

def send_emails():
  s = smtplib.SMTP_SSL(Config.host)
  s.login(Config.email,Config.password)
  for msg in msgs:
    s.sendmail(Config.email,msg["To"],msg.as_string())
  s.quit()
  sys.exit(0)

def is_clock_sane():
  t = datetime.today()
  year = t.year
  if year < Config.min_sane_year or year > Config.max_sane_year:
    return False
  return True

def get_touch_time():
  return datetime.fromtimestamp(os.path.getmtime(Config.touchfile))

def get_current_time():
  return datetime.today()

def time_since_touch():
  cur_time = get_current_time()
  t_time = get_touch_time()
  if t_time > cur_time or t_time.year < Config.min_sane_year:
    return timedelta()
  return cur_time-t_time

def activate_switch_if_needed():
  if is_clock_sane() and time_since_touch() > Config.time_to_wait:
    send_emails()

def signal_handler(sig,frame):
  pass

def daemonize():
  if os.fork():
    os._exit(0)
  os.setsid()
  if os.fork():
    os._exit(0)
  signal.signal(signal.SIGHUP,signal_handler)
  os.chdir("/")
  sys.stdin.close()
  sys.stdout.close()
  sys.stderr.close()

if __name__=='__main__':
  daemonize()
  sleep_time = Config.check_period.total_seconds()
  while True:
    activate_switch_if_needed()
    sleep(sleep_time)
