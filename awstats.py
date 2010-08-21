#!/usr/bin/python
# -*- coding: utf-8 -*-
#_______________________________________________________________
#     AwstatsGen
# *    Copyright (C) 2010   Ruslan Pisarev
# *	Version 0.5

import MySQLdb
import hashlib,urllib,subprocess
import socket
import os,sys,string
from optparse import OptionParser

def escape_str(str):
        return str.replace('.','_').replace('-','_')

def get_logs(str):
        return str.split()[1]

def get_servername(str):
        return str.split()[1]

def get_server_alias(str):
        return " ".join(str.split()[1:])

def gen_filename(sername):
        return "/etc/awstats/awstats."+sername+".conf"

def save_awstats_conf(logs,servername,server_alias,users):
        f=open(gen_filename(servername),'w')
        f.write(create_awstats_conf(logs,servername,server_alias,users))
        f.close()

def create_awstats_conf(logs,servername,server_alias,users):
        return """LogFile="%(log)s"
SiteDomain="%(stnm)s"
HostAliases="%(stnm)s %(stal)s"
AllowAccessFromWebToAuthenticatedUsersOnly=1
AllowAccessFromWebToFollowingAuthenticatedUsers="%(us)s"
Include "/etc/awstats/for_all_sites.inc"
    """ % {
"log" : logs,
"stnm": servername,
"stal": server_alias,
"us" : " ".join(users)
}

def awstats_users():
        f = open('/opt/awstatstab','r')
	user=0
	sites=1
        res=[]
	another_res=[]
        alias_db=f.readlines()
	f.close()

        for line in alias_db:
		if line.split()[sites] == '*':
			res+= [line.split()[user]]
		else:
			site_for_user = line.split()[sites].split(",")
			for i in site_for_user:
				another_res+=[(i,line.split()[user])]
	res+=[dict(another_res)]

        return (res)

def get_sites_list_all_info(user_list):
	f = open('/etc/apache2/sites-enabled/vhosts.conf','r')
	invhost=0
	res=[]
	users={}
	superuser_list=user_list[0:-1]
	site_users=user_list[-1]
	vhosts=f.readlines()
	f.close()
	for line in vhosts:
		if ':443' in line:
			continue
		if '<VirtualHost' in line:
                        invhost=1
                        continue
		if invhost==1:
			if 'CustomLog' in line:
				log=get_logs(line)
				continue
			if 'ServerName' in line:
				sername=get_servername(line)
        			if sername in site_users:
                        		users[sername]=superuser_list+[site_users[sername]]+[escape_str(sername)]
                		else:
                        		users[sername]=superuser_list+[escape_str(sername)]
				continue
			if 'ServerAlias' in line:
				seral=get_server_alias(line)
				continue
			if '</VirtualHost' in line:
				save_awstats_conf(log,sername,seral,users[sername])
				# /var/www/vhosts/stat/www/awstats.pl -config=SERNAME -update"
				subprocess.Popen(['/var/www/vhosts/stat/www/awstats.pl','-config='+sername, '-update']).communicate()
				invhost=0

#main
get_sites_list_all_info(awstats_users())

