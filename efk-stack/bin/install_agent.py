# Author : Suraj Kumar
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


def install_agent():
    '''
    Installing agent components : Fluentd
    '''

    commands_to_run = [['wget', 'https://toolbelt.treasuredata.com/sh/install-redhat-td-agent2.sh',
                        '-O', '/tmp/install-redhat-td-agent2.sh'],
                       ['/bin/bash', '/tmp/install-redhat-td-agent2.sh']]

    for commands in commands_to_run:
        print subprocess.check_output(commands)


def configure_fluentd(args):
    '''
    Configuring fluentd with custom regex needed for Cloudera, Hortonwork, Pivotal.
    '''
    stack_dir = os.path.abspath(os.path.join(__file__, '../..'))
    conf_dir = os.path.abspath(os.path.join(__file__, '../../conf'))
    tmp_dir = os.path.abspath(os.path.join(__file__, '../../tmp'))
    log_dir = os.path.abspath(os.path.join(__file__, '../../log'))
    es_host = 'host' + ' ' + args.elasticsearch_hostname + ':9200'

    os.system('mv /etc/td-agent/td-agent.conf /etc/td-agent/td-agent.conf_old')
    if args.hadoop_distribution == 'cloudera':
        os.system('cp %s/td-agent-cloudera.conf /etc/td-agent/td-agent.conf' % conf_dir)
    elif args.hadoop_distribution == 'hdp':
        os.system('cp %s/td-agent-hdp.conf /etc/td-agent/td-agent.conf' % conf_dir)
    elif args.hadoop_distribution == 'pivotal':
        os.system('cp %s/td-agent-pivotal.conf /etc/td-agent/td-agent.conf' % conf_dir)

    os.system('cp %s/es_config.conf /etc/td-agent/es_config.conf' % conf_dir)
    os.system('cp %s/grok_patterns /etc/td-agent/grok_patterns' % conf_dir)

    try:
        with open('/etc/td-agent/es_config.conf', 'r') as infile:
            data = infile.read().replace('hosts 127.0.0.1:9200', es_host)
    except OSError as exception:
        print('ERROR: could not read file:')
        print('  %s' % exception)
    else:
        with open('/etc/td-agent/es_config.conf', 'w') as outfile:
            outfile.write(data)

    os.system('chown td-agent. /etc/td-agent/*')


def main():
    parser = argparse.ArgumentParser(prog='install_server.py')

    parser.add_argument('hadoop_distribution', help='Specify hadoop distribution installed',
                        choices=['cloudera', 'hortonworks', 'pivotal'])
    parser.add_argument('elasticsearch_hostname', help="FQDN of the elasticsearch server")

    args = parser.parse_args()

    if sys.version_info < (2, 7):
        print 'Python version should be 2.7 or greater'
        sys.exit()

    print "Checking Internet connection"
    internet_check()
    print "Installing agent components"
    install_agent()
    print "Configuring Fluentd"
    configure_fluentd(args)

    print 'Starting Fluentd'
    os.system('/etc/init.d/td-agent start')

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())

    except Exception as e:
        raise e
