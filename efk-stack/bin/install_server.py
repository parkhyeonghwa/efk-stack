import urllib2
import subprocess
import sys
import argparse
import os

def internet_check():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib2.URLError as err:
        print 'No Internet connection.!!'
        raise err


def install_server():
    '''
    Installing server components : Kibana and Elasticsearch
    '''

    commands_to_run = [['wget', 'https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.2.1.rpm',
                        '-O', '/tmp/elasticsearch-5.2.1.rpm'],
                       ['rpm', '-ivh', '/tmp/elasticsearch-5.2.1.rpm'],
                       ['wget', 'https://artifacts.elastic.co/downloads/kibana/kibana-5.2.1-x86_64.rpm',
                        '-O', '/tmp/kibana-5.2.1-x86_64.rpm'],
                       ['rpm', '-ivh', '/tmp/kibana-5.2.1-x86_64.rpm']]

    for commands in commands_to_run:
        print subprocess.check_output(commands)


def configure_elastic(args):
    '''
    Configure elasticsearch for first run
    '''

    cluster_name = 'cluster.name: %s' % args.cluster_name
    hostname = 'network.host: %s' % args.hostname

    path = '/etc/elasticsearch/elasticsearch.yml'
    key = ['#cluster.name: my-application', '#node.name: node-1', '#path.data: /path/to/data',
           '#path.logs: /path/to/logs', '#network.host: 192.168.0.1', '#http.port: 9200']
    value = [cluster_name, 'node.name: node-1', 'path.data: /tmp/el-data',
             'path.logs: /var/log/elasticsearch', hostname, 'http.port: 9200']

    config_editor(path, key, value)


def configure_kibana(args):
    '''
    Configure Kibana for first run
    '''

    hostname = 'network.host: %s' % args.hostname
    elastic_host = 'elasticsearch.url: "http://%s:9200"' % args.hostname

    path = '/etc/kibana/kibana.yml'
    key = ['#server.port: 5601', '#server.host: "localhost"', '#elasticsearch.url: "http://localhost:9200"']
    value = ['server.port: 5601', hostname, elastic_host]

    config_editor(path, key, value)


def config_editor(path, key, value):
    '''
    yml config editor
    '''

    for count in range(0, len(key)):
        try:
            with open(path, 'r') as infile:
                data = infile.read().replace(key[count], value[count])
        except OSError as exception:
            print('ERROR: could not read file:')
            print('  %s' % exception)
        else:
            with open(path, 'w') as outfile:
                outfile.write(data)


def main():
    parser = argparse.ArgumentParser(prog='install_server.py')

    parser.add_argument('--cluster-name', default="efk",
                        help='Name of Elasticsearch index (defaults to %(default)s)')
    parser.add_argument('hostname', help="FQDN of the server (defaults to %(default)s)")

    args = parser.parse_args()

    if sys.version_info < (2, 7):
        print 'Python version should be 2.7 or greater'
        sys.exit()

    print "Checking Internet connection"
    internet_check()
    print "Installing server components"
    install_server()
    print "Configuring Elasticsearch"
    configure_elastic(args)
    print "Configuring Kibana"
    configure_kibana(args)
    print 'Starting Elasticsearch and Kibana'
    os.system('/etc/init.d/elasticsearch start')
    os.system('/etc/init.d/kibana start')

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())

    except Exception as e:
        raise e