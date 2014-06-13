# Sets up a user mini-mon username/password in keystone

python 'make default keystone user' do
  action :run
  code <<-EOH
import keystoneclient
from keystoneclient.v2_0 import client
import sys
try:
    key = client.Client(token='ADMIN', endpoint='http://127.0.0.1:35357/v2.0/')
    user_list = key.users.list()
except keystoneclient.exceptions:
    time.sleep(2)  # Sometimes chef is too fast and the service is not yet up
    key = client.Client(token='ADMIN', endpoint='http://127.0.0.1:35357/v2.0/')
    user_list = key.users.list()

for user in user_list:
    if user.name == 'mini-mon':
        sys.exit(0)

key.users.create(name='mini-mon', password='password', email='mini@mon.com', enabled=True)
EOH
end
