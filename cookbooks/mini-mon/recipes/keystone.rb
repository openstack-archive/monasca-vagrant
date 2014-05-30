# Install a simple keystone just using sqlite, then setup a user mini-mon/password

package 'keystone' do
  action :install
end

service 'keystone' do
  action [ :enable, :start ]
end

# The python-keystoneclient that comes with precise is broken by a newer python-prettytable needed by python-monclient, so cmdline interaction is messed
# up, using the api directly is fine though

python 'make default keystone user' do
  action :run
  code <<-EOH
from keystoneclient.v2_0 import client
import sys
key = client.Client(token='ADMIN', endpoint='http://127.0.0.1:35357/v2.0/')
for user in key.users.list():
    if user.name == 'mini-mon':
        sys.exit(0)

key.users.create(name='mini-mon', password='password', email='mini@mon.com', enabled=True)
EOH
end
