# Temporary way of loading in the mysql schema

bash 'mon_schema' do
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
  notifies :run, "bash[mon_schema]"
end

cookbook_file '/var/lib/mysql/addr_validate.sql' do
  action :create
  owner 'root'
  group 'root'
  source 'addr_validate.sql'
  notifies :run, "bash[addr_validate_schema]"
end

# Write out for root a .my.cnf with the user/pass used by the mon-setup program
# Note: The permissions below are quite insecure but this is sufficient for mini-mon
directory '/root' do
  action :create
  mode 755
end
file '/root/.my.cnf' do
  action :create_if_missing
  owner "root"
  group "root"
  mode "0644"
  content "[client]\nuser=root\npassword=password"
end
