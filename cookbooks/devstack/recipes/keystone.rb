# Sets up a user mini-mon username/password in keystone

python 'make default keystone users' do
  action :run
  code <<-EOH
import keystoneclient
from keystoneclient.v2_0 import client

def add_service_endpoint(key, service_name, endpoint_host):
  """Add the Monasca service to the catalog with the specified endpoint, if it doesn't yet exist."""
  service_names = { service.name: service.id for service in key.services.list() }
  if service_name in service_names.keys():
    service_id = service_names[service_name] 
  else:
    service=key.services.create(name=service_name, service_type='monitoring', description='Monasca monitoring service')
    service_id = service.id
 
  for endpoint in key.endpoints.list():
    if endpoint.service_id == service_id:
      return

  key.endpoints.create(region="RegionOne", service_id=service_id,
                            publicurl="http://%s:8080/v2.0/" % endpoint_host,
                            adminurl="http://%s:8080/v2.0/" % endpoint_host,
                            internalurl="http://%s:8080/v2.0/" % endpoint_host)

def create_user(user_name, password, email,tenant_id):
  user_id = None
  user_list = key.users.list()

  # Create the user if it doesn't exist
  for user in user_list:
    if user.name == user_name:
      user_id = user.id

  if user_id is None:
    user_id = key.users.create(name=user_name, password=password, email=email, tenant_id=tenant_id, enabled=True)

  return user_id

def create_role(user_name, role_name, tenant_id):
  role_id = None
  for role in key.roles.list():
    if role.name == role_name:
      role_id = role.id
    
  #create role it doesn't exist 
  if role_id is None:
    role_id = key.roles.create(role_name)
    key.roles.add_user_role(user_name, role_id, tenant_id)

def create_tenant(tenant_name):
  tenant_id = None
  for tenant in key.tenants.list():
    if tenant.name == tenant_name:
      tenant_id = tenant.id

  if tenant_id is None:
    tenant_id = key.tenants.create(tenant_name).id

  return tenant_id

try:
  key = client.Client(token='ADMIN', endpoint='http://127.0.0.1:35357/v2.0/')
except keystoneclient.exceptions:
  time.sleep(2)  # Sometimes chef is too fast and the service is not yet up
  key = client.Client(token='ADMIN', endpoint='http://127.0.0.1:35357/v2.0/')
    
tenant_id = create_tenant('mini-mon')
create_user('mini-mon', 'password', 'mini@mon.com', tenant_id)
monasca_user_id = create_user('monasca-agent', 'password', 'monasca-agent@mon.com', tenant_id)

create_role(monasca_user_id, 'monasca-agent', tenant_id)

add_service_endpoint(key, 'monasca', '192.168.10.4')
EOH
end
