# Sets up a user mini-mon username/password in keystone

python 'make default keystone users' do
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

# Create the tenant for mini-mon if it doesn't exist
tenant_id = None
monasca_agent_id = None

#Need to create monasca-agent

for tenant in key.tenants.list():
  if tenant.name == 'mini-mon':
    tenant_id = tenant.id
  if monasca_agent_id == 'monasca_agent':
    monasca_agent_id = tenant.id

if tenant_id is None:
  tenant_id = key.tenants.create('mini-mon').id

if monasca_agent_id is None:
  monasca_agent_id = key.tenants.create('monasca-agent').id

create_mini_mon_user = True
create_monasca_agent_user = True
# Create the user if it doesn't exist
for user in user_list:
    if user.name == 'mini-mon':
        create_mini_mon_user = False
        create_monasca_agent_user = False
if create_mini_mon_user:
    key.users.create(name='mini-mon', password='password', email='mini@mon.com', tenant_id=tenant_id, enabled=True)

monasca_user = None
if create_monasca_agent_user:
    monasca_agent_user = key.users.create(name='monasca-agent', password='password', email='monasca-agent@mon.com', tenant_id=monasca_agent_id, enabled=True)

#create role for monasca agent
if create_monasca_agent_user:
  role = key.roles.create('monasca-agent')
  key.roles.add_user_role(monasca_agent_user, role, monasca_agent_id);
EOH
end
