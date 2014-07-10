# Create an influxdb database and users
# Leverages the cookbook from https://github.com/SimpleFinance/chef-influxdb

service 'influxdb' do
  action :start
end

influxdb_database 'mon' do
  action :create
end

['mon_api', 'mon_persister'].each do |user|
  influxdb_user user do
    action :create
    password 'password'
    databases ['mon']
  end
end
