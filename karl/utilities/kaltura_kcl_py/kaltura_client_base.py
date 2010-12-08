#
# This file is part of the Kaltura Collaborative Media Suite which allows users
# to do with audio, video, and animation what Wiki platfroms allow them to do with
# text.
#
# Copyright (C) 2006-2008 Kaltura Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import urllib
import urllib2
import datetime
from xmlobject import XMLFile

class KalturaClientBase:

	FORMATS = {
		"KALTURA_SERVICE_FORMAT_JSON" : 1, 
		"KALTURA_SERVICE_FORMAT_XML" : 2,
		"KALTURA_SERVICE_FORMAT_PHP" : 3}

	KALTURA_API_VERSION = "0.7"

	def post(self, path, options):
		f = urllib2.urlopen(path, urllib.urlencode(options))
		return f.read()

	def headers(self):
		pass
		#@headers ||= { 'Content-Type' => 'application/x-www-form-urlencoded' }

	#
	# Kaltura client constuctor, expecting configuration object 
	#
	# @param KalturaConfiguration $config
	#
	def __init__(self, config):
		self.ks = None
  		self.shouldLog = False
  		self.config = config;
  		
  		logger = config.getLogger()

  		if logger != None:
			self.shouldLog = true

	def hit(self, method, session_user, params):
		start_time = datetime.time()
  
		self.log("service url: [%s]" % self.config.serviceUrl);
		self.log("trying to call method: [%s] for user id: [%s] using session: [%s]" % (method, session_user.userId, self.ks));
  
		# append the basic params
		params["kaltura_api_version"] 	= KalturaClientBase.KALTURA_API_VERSION
		params["partner_id"]		= self.config.partnerId
		params["subp_id"]			= self.config.subPartnerId
		params["format"]			= self.config.format
		params["uid"]				= session_user.userId
		self.addOptionalParam(params, "user_name", session_user.screenName)
		self.addOptionalParam(params, "ks", self.ks)

		#params["kalsig"] = signature(params);

		url = self.config.serviceUrl + "/index.php/partnerservices2/" + method
		self.log("full reqeust url: [%s] params: [%s]" % (url, urllib.urlencode(params)))

		response = self.post(url, params)

		self.log("result (serialized): %s" % response)

		xml = XMLFile(raw = response)

		#self.log("result (object dump): #{dump}")

		end_time = datetime.time()

		#log("execution time for method [#{method}]: [#{end_time - start_time}]")
		
		return xml.root


	def start(self, session_user, secret):
		result = self.startSession(session_user, secret)

  		self.ks = result.result.ks._text
  		return result

	def signature(self, params):
#		str = params.keys.map {|key| key.to_s }.sort.map {|key|
#		"#{escape(key)}#{escape(params[key])}"
#		}.join("")

#	  Digest::MD5.hexdigest(str)
		pass
  		
	def getKs(self):
  		return self.ks

	def setKs(self, ks):
		self.ks = ks

	def addOptionalParam(self, params, paramName, paramValue):
  		if paramValue != None: params[paramName] = paramValue 

	def log(self, msg):
		if self.shouldLog: config.getLogger().log(msg)


class KalturaSessionUser:

	def __init__(self, userId, screenName = None):
	  	self.userId = userId;
	  	self.screenName = screenName;


class KalturaConfiguration:

	serviceUrl  = "http://www.kaltura.com/"
	format = KalturaClientBase.FORMATS["KALTURA_SERVICE_FORMAT_XML"]

	#
	# Constructs new kaltura configuration object, expecting partner id & sub partner id
	#
	# @param int $partnerId
	# @param int $subPartnerId
	#
	def __init__(self, partnerId, subPartnerId):
		self.partnerId = partnerId;
		self.subPartnerId = subPartnerId;
		self.logger = None

	#
	# Set logger to get kaltura client debug logs
	#
	# @param IKalturaLogger $log
	#
	def setLogger(self, log):
		self.logger = log

	#
	# Gets the logger (Internal client use)
	#
	# @return unknown
	#
	def getLogger(self):
		return self.logger

#
# Implement to get kaltura client logs
#
#
class IKalturaLogger:
	def log(self, msg):
		pass
