sudo mkdir elastic_data
sudo sysctl -w vm.max_map_count=262144
sudo docker run -it -p 9200:9200 -e "discovery.type=single-node" -v ~/elastic_data:/usr/share/elasticsearch/data docker.elastic.co/elasticsearch/elasticsearch:6.5.4
sudo chmod -R 777 elastic_data/


