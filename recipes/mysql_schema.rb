# Temporary way of loading in the mysql schema

bash 'maas_schema' do
  action :nothing
  code 'mysql -uroot -ppassword < /var/lib/mysql/mon.sql'
end

bash 'addr_validate_schema' do
  action :nothing
  code 'mysql -uroot -ppassword < /var/lib/mysql/addr_validate.sql'
end

cookbook_file '/var/lib/mysql/mon.sql' do
  action :create
  owner 'root'
  group 'root'
  source 'mon.sql'
  notifies :run, "bash[maas_schema]"
end

cookbook_file '/var/lib/mysql/addr_validate.sql' do
  action :create
  owner 'root'
  group 'root'
  source 'addr_validate.sql'
  notifies :run, "bash[addr_validate_schema]"
end
