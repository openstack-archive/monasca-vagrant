# Test notifications
- The api is currently rejecting alarms with no action specified, so expect an error defining that alarm.
- Setup alarms and Notifications
  - run ./alarm_notification.py -e me@hp.com
- Run the jmeter tests
  - `jmeter -t notification-jmeter.jmx &`
  - The config is saved for a basic test that should create a notification on alarm and a hundred non-notification alarms. Change the thread
    loop counts to try different combinations.
