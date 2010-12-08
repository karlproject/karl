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

from kaltura_client_base import *

class KalturaEntry:

	def __init__(self):
		self.name = None
		self.tags = None
		self.type = None
		self.mediaType = None
		self.source = None
		self.sourceId = None
		self.sourceLink = None
		self.licenseType = None
		self.credit = None
		self.groupId = None
		self.partnerData = None
		self.conversionQuality = None
		self.permissions = None
		self.dataContent = None
		self.desiredVersion = None
		self.url = None
		self.thumbUrl = None
		self.filename = None
		self.realFilename = None
		self.indexedCustomData1 = None
		self.thumbOffset = None
		self.mediaId = None
		self.screenName = None
		self.siteUrl = None
		self.description = None
		self.mediaDate = None
		self.adminTags = None

class KalturaBatchJob:

	def __init__(self):
		self.data = None
		self.status = None
		self.abort = None
		self.checkAgainTimeout = None
		self.progress = None
		self.message = None
		self.description = None
		self.updatesCount = None
		self.processorExpiration = None

class KalturaKShow:

	def __init__(self):
		self.name = None
		self.description = None
		self.tags = None
		self.indexedCustomData3 = None
		self.groupId = None
		self.permissions = None
		self.partnerData = None
		self.allowQuickEdit = None

class KalturaModeration:

	def __init__(self):
		self.comments = None
		self.objectType = None
		self.objectId = None
		self.reportCode = None
		self.status = None

class KalturaUiConf:

	def __init__(self):
		self.name = None
		self.objType = None
		self.width = None
		self.height = None
		self.htmlParams = None
		self.swfUrl = None
		self.swfUrlVersion = None
		self.confFile = None
		self.confVars = None
		self.useCdn = None
		self.tags = None

class KalturaUser:

	def __init__(self):
		self.screenName = None
		self.fullName = None
		self.email = None
		self.dateOfBirth = None
		self.aboutMe = None
		self.tags = None
		self.gender = None
		self.country = None
		self.state = None
		self.city = None
		self.zip = None
		self.urlList = None
		self.networkHighschool = None
		self.networkCollege = None
		self.partnerData = None

class KalturaWidget:

	def __init__(self):
		self.kshowId = None
		self.entryId = None
		self.sourceWidgetId = None
		self.uiConfId = None
		self.customData = None
		self.partnerData = None
		self.securityType = None

class KalturaPuserKuser:

	def __init__(self):
		pass

class KalturaConvesionProfileFilter:

	ORDER_BY_CREATED_AT_ASC = "+created_at";
	ORDER_BY_CREATED_AT_DESC = "-created_at";
	ORDER_BY_PROFILE_TYPE_ASC = "+profile_type";
	ORDER_BY_PROFILE_TYPE_DESC = "-profile_type";
	ORDER_BY_ID_ASC = "+id";
	ORDER_BY_ID_DESC = "-id";

	def __init__(self):
		self.equalId = None
		self.greaterThanOrEqualId = None
		self.equalStatus = None
		self.likeName = None
		self.inProfileType = None
		self.equalEnabled = None
		self.equalType = None
		self.equalUseWithBulk = None
		self.orderBy = None
		self.limit = None

class KalturaConversionProfile:

	def __init__(self):
		self.name = None
		self.profileType = None
		self.width = None
		self.height = None
		self.aspectRatio = None
		self.bypassFlv = None
		self.commercialTranscoder = None
		self.useWithBulk = None

class KalturaBatchJobFilter:

	ORDER_BY_ID_ASC = "+id";
	ORDER_BY_ID_DESC = "-id";

	def __init__(self):
		self.equalId = None
		self.greaterThanOrEqualId = None
		self.equalStatus = None
		self.equalJobType = None
		self.inJobType = None
		self.orderBy = None
		self.limit = None

class KalturaEntryFilter:

	ORDER_BY_CREATED_AT_ASC = "+created_at";
	ORDER_BY_CREATED_AT_DESC = "-created_at";
	ORDER_BY_VIEWS_ASC = "+views";
	ORDER_BY_VIEWS_DESC = "-views";
	ORDER_BY_NAME_ASC = "+name";
	ORDER_BY_NAME_DESC = "-name";
	ORDER_BY_MEDIA_DATE_ASC = "+media_date";
	ORDER_BY_MEDIA_DATE_DESC = "-media_date";
	ORDER_BY_TYPE_ASC = "+type";
	ORDER_BY_TYPE_DESC = "-type";
	ORDER_BY_MEDIA_TYPE_ASC = "+media_type";
	ORDER_BY_MEDIA_TYPE_DESC = "-media_type";
	ORDER_BY_PLAYS_ASC = "+plays";
	ORDER_BY_PLAYS_DESC = "-plays";
	ORDER_BY_RANK_ASC = "+rank";
	ORDER_BY_RANK_DESC = "-rank";
	ORDER_BY_MODERATION_COUNT_ASC = "+moderation_count";
	ORDER_BY_MODERATION_COUNT_DESC = "-moderation_count";
	ORDER_BY_MODERATION_STATUS_ASC = "+moderation_status";
	ORDER_BY_MODERATION_STATUS_DESC = "-moderation_status";
	ORDER_BY_MODIFIED_AT_ASC = "+modified_at";
	ORDER_BY_MODIFIED_AT_DESC = "-modified_at";
	ORDER_BY_ID_ASC = "+id";
	ORDER_BY_ID_DESC = "-id";

	def __init__(self):
		self.equalUserId = None
		self.equalKshowId = None
		self.equalStatus = None
		self.inStatus = None
		self.equalType = None
		self.inType = None
		self.equalMediaType = None
		self.inMediaType = None
		self.equalIndexedCustomData1 = None
		self.inIndexedCustomData1 = None
		self.likeName = None
		self.equalName = None
		self.equalTags = None
		self.likeTags = None
		self.multiLikeOrTags = None
		self.multiLikeAndTags = None
		self.multiLikeOrAdminTags = None
		self.multiLikeAndAdminTags = None
		self.likeAdminTags = None
		self.multiLikeOrName = None
		self.multiLikeAndName = None
		self.multiLikeOrSearchText = None
		self.multiLikeAndSearchText = None
		self.equalGroupId = None
		self.greaterThanOrEqualViews = None
		self.greaterThanOrEqualCreatedAt = None
		self.lessThanOrEqualCreatedAt = None
		self.greaterThanOrEqualUpdatedAt = None
		self.lessThanOrEqualUpdatedAt = None
		self.greaterThanOrEqualModifiedAt = None
		self.lessThanOrEqualModifiedAt = None
		self.inPartnerId = None
		self.equalPartnerId = None
		self.equalSourceLink = None
		self.greaterThanOrEqualMediaDate = None
		self.lessThanOrEqualMediaDate = None
		self.equalModerationStatus = None
		self.inModerationStatus = None
		self.inDisplayInSearch = None
		self.multiLikeOrTagsOrName = None
		self.multiLikeOrTagsOrAdminTags = None
		self.multiLikeOrTagsOrAdminTagsOrName = None
		self.orderBy = None
		self.limit = None

class KalturaKShowFilter:

	ORDER_BY_CREATED_AT_ASC = "+created_at";
	ORDER_BY_CREATED_AT_DESC = "-created_at";
	ORDER_BY_VIEWS_ASC = "+views";
	ORDER_BY_VIEWS_DESC = "-views";
	ORDER_BY_RANK_ASC = "+rank";
	ORDER_BY_RANK_DESC = "-rank";
	ORDER_BY_ID_ASC = "+id";
	ORDER_BY_ID_DESC = "-id";

	def __init__(self):
		self.likeName = None
		self.likeTags = None
		self.multiLikeOrTags = None
		self.multiLikeAndTags = None
		self.greaterThanOrEqualViews = None
		self.equalType = None
		self.equalProducerId = None
		self.greaterThanOrEqualCreatedAt = None
		self.lessThanOrEqualCreatedAt = None
		self.bitAndStatus = None
		self.equalIndexedCustomData3 = None
		self.orderBy = None
		self.limit = None

class KalturaModerationFilter:

	ORDER_BY_ID_ASC = "+id";
	ORDER_BY_ID_DESC = "-id";

	def __init__(self):
		self.equalId = None
		self.equalPuserId = None
		self.equalStatus = None
		self.inStatus = None
		self.likeComments = None
		self.equalObjectId = None
		self.equalObjectType = None
		self.equalGroupId = None
		self.orderBy = None
		self.limit = None

class KalturaNotificationFilter:

	ORDER_BY_ID_ASC = "+id";
	ORDER_BY_ID_DESC = "-id";

	def __init__(self):
		self.equalId = None
		self.greaterThanOrEqualId = None
		self.equalStatus = None
		self.equalType = None
		self.orderBy = None
		self.limit = None

class KalturaNotification:

	def __init__(self):
		self.id = None
		self.status = None
		self.notificationResult = None

class KalturaUiConfFilter:

	ORDER_BY_ID_ASC = "+id";
	ORDER_BY_ID_DESC = "-id";

	def __init__(self):
		self.equalId = None
		self.greaterThanOrEqualId = None
		self.equalStatus = None
		self.equalObjType = None
		self.likeName = None
		self.multiLikeOrTags = None
		self.orderBy = None
		self.limit = None

class KalturaBatchjobType:

	CONVERT = "0";
	IMPORT = "1";
	DELETE = "2";
	FLATTEN = "3";
	BULKUPLOAD = "4";
	DVDCREATOR = "5";
	DOWNLOAD = "6";

	def __init__(self):
		pass

class KalturaPartner:

	def __init__(self):
		self.name = None
		self.url1 = None
		self.url2 = None
		self.appearInSearch = None
		self.adminName = None
		self.adminEmail = None
		self.description = None
		self.commercialUse = None
		self.landingPage = None
		self.userLandingPage = None
		self.notificationsConfig = None
		self.notify = None
		self.allowMultiNotification = None
		self.contentCategories = None
		self.type = None

class KalturaEntryMediaType:

	ANY = "0";
	VIDEO = "1";
	IMAGE = "2";
	TEXT = "3";
	HTML = "4";
	AUDIO = "5";
	SHOW = "6";
	SHOW_XML = "7";
	BUBBLES = "9";
	XML = "10";
	GENERIC_1 = "101";
	GENERIC_2 = "102";
	GENERIC_3 = "103";
	GENERIC_4 = "104";

	def __init__(self):
		pass

class KalturaEntryMediaSource:

	FILE = "1";
	WEBCAM = "2";
	FLICKR = "3";
	YOUTUBE = "4";
	URL = "5";
	TEXT = "6";
	MYSPACE = "7";
	PHOTOBUCKET = "8";
	JAMENDO = "9";
	CCMIXTER = "10";
	NYPL = "11";
	CURRENT = "12";
	MEDIA_COMMONS = "13";
	KALTURA = "20";
	KALTURA_USER_CLIPS = "21";
	ARCHIVE_ORG = "22";
	KALTURA_PARTNER = "23";
	METACAFE = "24";
	KALTURA_QA = "25";
	KALTURA_KSHOW = "26";
	KALTURA_PARTNER_KSHOW = "27";
	SEARCH_PROXY = "28";

	def __init__(self):
		pass

class KalturaEntryType:

	BACKGROUND = "0";
	MEDIACLIP = "1";
	SHOW = "2";
	BUBBLES = "4";
	PLAYLIST = "5";
	DVD = "300";

	def __init__(self):
		pass

class KalturaClient(KalturaClientBase):
	def addDownload(self, kalturaSessionUser, entryId, fileFormat, entryVersion = None):
		params = {}
		params["entry_id"] = entryId;
		params["file_format"] = fileFormat;
		self.addOptionalParam(params, "entry_version", entryVersion);

		return self.hit("adddownload", kalturaSessionUser, params);

	def addDvdEntry(self, kalturaSessionUser, dvdEntry):
		params = {}
		self.addOptionalParam(params, "dvdEntry_name", dvdEntry.name);
		self.addOptionalParam(params, "dvdEntry_tags", dvdEntry.tags);
		self.addOptionalParam(params, "dvdEntry_type", dvdEntry.type);
		self.addOptionalParam(params, "dvdEntry_mediaType", dvdEntry.mediaType);
		self.addOptionalParam(params, "dvdEntry_source", dvdEntry.source);
		self.addOptionalParam(params, "dvdEntry_sourceId", dvdEntry.sourceId);
		self.addOptionalParam(params, "dvdEntry_sourceLink", dvdEntry.sourceLink);
		self.addOptionalParam(params, "dvdEntry_licenseType", dvdEntry.licenseType);
		self.addOptionalParam(params, "dvdEntry_credit", dvdEntry.credit);
		self.addOptionalParam(params, "dvdEntry_groupId", dvdEntry.groupId);
		self.addOptionalParam(params, "dvdEntry_partnerData", dvdEntry.partnerData);
		self.addOptionalParam(params, "dvdEntry_conversionQuality", dvdEntry.conversionQuality);
		self.addOptionalParam(params, "dvdEntry_permissions", dvdEntry.permissions);
		self.addOptionalParam(params, "dvdEntry_dataContent", dvdEntry.dataContent);
		self.addOptionalParam(params, "dvdEntry_desiredVersion", dvdEntry.desiredVersion);
		self.addOptionalParam(params, "dvdEntry_url", dvdEntry.url);
		self.addOptionalParam(params, "dvdEntry_thumbUrl", dvdEntry.thumbUrl);
		self.addOptionalParam(params, "dvdEntry_filename", dvdEntry.filename);
		self.addOptionalParam(params, "dvdEntry_realFilename", dvdEntry.realFilename);
		self.addOptionalParam(params, "dvdEntry_indexedCustomData1", dvdEntry.indexedCustomData1);
		self.addOptionalParam(params, "dvdEntry_thumbOffset", dvdEntry.thumbOffset);
		self.addOptionalParam(params, "dvdEntry_mediaId", dvdEntry.mediaId);
		self.addOptionalParam(params, "dvdEntry_screenName", dvdEntry.screenName);
		self.addOptionalParam(params, "dvdEntry_siteUrl", dvdEntry.siteUrl);
		self.addOptionalParam(params, "dvdEntry_description", dvdEntry.description);
		self.addOptionalParam(params, "dvdEntry_mediaDate", dvdEntry.mediaDate);
		self.addOptionalParam(params, "dvdEntry_adminTags", dvdEntry.adminTags);

		return self.hit("adddvdentry", kalturaSessionUser, params);

	def addDvdJob(self, kalturaSessionUser, entryId):
		params = {}
		params["entry_id"] = entryId;

		return self.hit("adddvdjob", kalturaSessionUser, params);

	def addEntry(self, kalturaSessionUser, kshowId, entry, uid = None):
		params = {}
		params["kshow_id"] = kshowId;
		self.addOptionalParam(params, "entry_name", entry.name);
		self.addOptionalParam(params, "entry_tags", entry.tags);
		self.addOptionalParam(params, "entry_type", entry.type);
		self.addOptionalParam(params, "entry_mediaType", entry.mediaType);
		self.addOptionalParam(params, "entry_source", entry.source);
		self.addOptionalParam(params, "entry_sourceId", entry.sourceId);
		self.addOptionalParam(params, "entry_sourceLink", entry.sourceLink);
		self.addOptionalParam(params, "entry_licenseType", entry.licenseType);
		self.addOptionalParam(params, "entry_credit", entry.credit);
		self.addOptionalParam(params, "entry_groupId", entry.groupId);
		self.addOptionalParam(params, "entry_partnerData", entry.partnerData);
		self.addOptionalParam(params, "entry_conversionQuality", entry.conversionQuality);
		self.addOptionalParam(params, "entry_permissions", entry.permissions);
		self.addOptionalParam(params, "entry_dataContent", entry.dataContent);
		self.addOptionalParam(params, "entry_desiredVersion", entry.desiredVersion);
		self.addOptionalParam(params, "entry_url", entry.url);
		self.addOptionalParam(params, "entry_thumbUrl", entry.thumbUrl);
		self.addOptionalParam(params, "entry_filename", entry.filename);
		self.addOptionalParam(params, "entry_realFilename", entry.realFilename);
		self.addOptionalParam(params, "entry_indexedCustomData1", entry.indexedCustomData1);
		self.addOptionalParam(params, "entry_thumbOffset", entry.thumbOffset);
		self.addOptionalParam(params, "entry_mediaId", entry.mediaId);
		self.addOptionalParam(params, "entry_screenName", entry.screenName);
		self.addOptionalParam(params, "entry_siteUrl", entry.siteUrl);
		self.addOptionalParam(params, "entry_description", entry.description);
		self.addOptionalParam(params, "entry_mediaDate", entry.mediaDate);
		self.addOptionalParam(params, "entry_adminTags", entry.adminTags);
		self.addOptionalParam(params, "uid", uid);

		return self.hit("addentry", kalturaSessionUser, params);

	def addKShow(self, kalturaSessionUser, kshow, detailed = None, allowDuplicateNames = None):
		params = {}
		self.addOptionalParam(params, "kshow_name", kshow.name);
		self.addOptionalParam(params, "kshow_description", kshow.description);
		self.addOptionalParam(params, "kshow_tags", kshow.tags);
		self.addOptionalParam(params, "kshow_indexedCustomData3", kshow.indexedCustomData3);
		self.addOptionalParam(params, "kshow_groupId", kshow.groupId);
		self.addOptionalParam(params, "kshow_permissions", kshow.permissions);
		self.addOptionalParam(params, "kshow_partnerData", kshow.partnerData);
		self.addOptionalParam(params, "kshow_allowQuickEdit", kshow.allowQuickEdit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "allow_duplicate_names", allowDuplicateNames);

		return self.hit("addkshow", kalturaSessionUser, params);

	def addModeration(self, kalturaSessionUser, moderation):
		params = {}
		self.addOptionalParam(params, "moderation_comments", moderation.comments);
		self.addOptionalParam(params, "moderation_objectType", moderation.objectType);
		self.addOptionalParam(params, "moderation_objectId", moderation.objectId);
		self.addOptionalParam(params, "moderation_reportCode", moderation.reportCode);
		self.addOptionalParam(params, "moderation_status", moderation.status);

		return self.hit("addmoderation", kalturaSessionUser, params);

	def addPartnerEntry(self, kalturaSessionUser, kshowId, entry, uid = None):
		params = {}
		params["kshow_id"] = kshowId;
		self.addOptionalParam(params, "entry_name", entry.name);
		self.addOptionalParam(params, "entry_tags", entry.tags);
		self.addOptionalParam(params, "entry_type", entry.type);
		self.addOptionalParam(params, "entry_mediaType", entry.mediaType);
		self.addOptionalParam(params, "entry_source", entry.source);
		self.addOptionalParam(params, "entry_sourceId", entry.sourceId);
		self.addOptionalParam(params, "entry_sourceLink", entry.sourceLink);
		self.addOptionalParam(params, "entry_licenseType", entry.licenseType);
		self.addOptionalParam(params, "entry_credit", entry.credit);
		self.addOptionalParam(params, "entry_groupId", entry.groupId);
		self.addOptionalParam(params, "entry_partnerData", entry.partnerData);
		self.addOptionalParam(params, "entry_conversionQuality", entry.conversionQuality);
		self.addOptionalParam(params, "entry_permissions", entry.permissions);
		self.addOptionalParam(params, "entry_dataContent", entry.dataContent);
		self.addOptionalParam(params, "entry_desiredVersion", entry.desiredVersion);
		self.addOptionalParam(params, "entry_url", entry.url);
		self.addOptionalParam(params, "entry_thumbUrl", entry.thumbUrl);
		self.addOptionalParam(params, "entry_filename", entry.filename);
		self.addOptionalParam(params, "entry_realFilename", entry.realFilename);
		self.addOptionalParam(params, "entry_indexedCustomData1", entry.indexedCustomData1);
		self.addOptionalParam(params, "entry_thumbOffset", entry.thumbOffset);
		self.addOptionalParam(params, "entry_mediaId", entry.mediaId);
		self.addOptionalParam(params, "entry_screenName", entry.screenName);
		self.addOptionalParam(params, "entry_siteUrl", entry.siteUrl);
		self.addOptionalParam(params, "entry_description", entry.description);
		self.addOptionalParam(params, "entry_mediaDate", entry.mediaDate);
		self.addOptionalParam(params, "entry_adminTags", entry.adminTags);
		self.addOptionalParam(params, "uid", uid);

		return self.hit("addpartnerentry", kalturaSessionUser, params);

	def addPlaylist(self, kalturaSessionUser, playlist):
		params = {}
		self.addOptionalParam(params, "playlist_name", playlist.name);
		self.addOptionalParam(params, "playlist_tags", playlist.tags);
		self.addOptionalParam(params, "playlist_type", playlist.type);
		self.addOptionalParam(params, "playlist_mediaType", playlist.mediaType);
		self.addOptionalParam(params, "playlist_source", playlist.source);
		self.addOptionalParam(params, "playlist_sourceId", playlist.sourceId);
		self.addOptionalParam(params, "playlist_sourceLink", playlist.sourceLink);
		self.addOptionalParam(params, "playlist_licenseType", playlist.licenseType);
		self.addOptionalParam(params, "playlist_credit", playlist.credit);
		self.addOptionalParam(params, "playlist_groupId", playlist.groupId);
		self.addOptionalParam(params, "playlist_partnerData", playlist.partnerData);
		self.addOptionalParam(params, "playlist_conversionQuality", playlist.conversionQuality);
		self.addOptionalParam(params, "playlist_permissions", playlist.permissions);
		self.addOptionalParam(params, "playlist_dataContent", playlist.dataContent);
		self.addOptionalParam(params, "playlist_desiredVersion", playlist.desiredVersion);
		self.addOptionalParam(params, "playlist_url", playlist.url);
		self.addOptionalParam(params, "playlist_thumbUrl", playlist.thumbUrl);
		self.addOptionalParam(params, "playlist_filename", playlist.filename);
		self.addOptionalParam(params, "playlist_realFilename", playlist.realFilename);
		self.addOptionalParam(params, "playlist_indexedCustomData1", playlist.indexedCustomData1);
		self.addOptionalParam(params, "playlist_thumbOffset", playlist.thumbOffset);
		self.addOptionalParam(params, "playlist_mediaId", playlist.mediaId);
		self.addOptionalParam(params, "playlist_screenName", playlist.screenName);
		self.addOptionalParam(params, "playlist_siteUrl", playlist.siteUrl);
		self.addOptionalParam(params, "playlist_description", playlist.description);
		self.addOptionalParam(params, "playlist_mediaDate", playlist.mediaDate);
		self.addOptionalParam(params, "playlist_adminTags", playlist.adminTags);

		return self.hit("addplaylist", kalturaSessionUser, params);

	def addRoughcutEntry(self, kalturaSessionUser, kshowId, entry):
		params = {}
		params["kshow_id"] = kshowId;
		self.addOptionalParam(params, "entry_name", entry.name);
		self.addOptionalParam(params, "entry_tags", entry.tags);
		self.addOptionalParam(params, "entry_type", entry.type);
		self.addOptionalParam(params, "entry_mediaType", entry.mediaType);
		self.addOptionalParam(params, "entry_source", entry.source);
		self.addOptionalParam(params, "entry_sourceId", entry.sourceId);
		self.addOptionalParam(params, "entry_sourceLink", entry.sourceLink);
		self.addOptionalParam(params, "entry_licenseType", entry.licenseType);
		self.addOptionalParam(params, "entry_credit", entry.credit);
		self.addOptionalParam(params, "entry_groupId", entry.groupId);
		self.addOptionalParam(params, "entry_partnerData", entry.partnerData);
		self.addOptionalParam(params, "entry_conversionQuality", entry.conversionQuality);
		self.addOptionalParam(params, "entry_permissions", entry.permissions);
		self.addOptionalParam(params, "entry_dataContent", entry.dataContent);
		self.addOptionalParam(params, "entry_desiredVersion", entry.desiredVersion);
		self.addOptionalParam(params, "entry_url", entry.url);
		self.addOptionalParam(params, "entry_thumbUrl", entry.thumbUrl);
		self.addOptionalParam(params, "entry_filename", entry.filename);
		self.addOptionalParam(params, "entry_realFilename", entry.realFilename);
		self.addOptionalParam(params, "entry_indexedCustomData1", entry.indexedCustomData1);
		self.addOptionalParam(params, "entry_thumbOffset", entry.thumbOffset);
		self.addOptionalParam(params, "entry_mediaId", entry.mediaId);
		self.addOptionalParam(params, "entry_screenName", entry.screenName);
		self.addOptionalParam(params, "entry_siteUrl", entry.siteUrl);
		self.addOptionalParam(params, "entry_description", entry.description);
		self.addOptionalParam(params, "entry_mediaDate", entry.mediaDate);
		self.addOptionalParam(params, "entry_adminTags", entry.adminTags);

		return self.hit("addroughcutentry", kalturaSessionUser, params);

	def addUiConf(self, kalturaSessionUser, uiconf):
		params = {}
		self.addOptionalParam(params, "uiconf_name", uiconf.name);
		self.addOptionalParam(params, "uiconf_objType", uiconf.objType);
		self.addOptionalParam(params, "uiconf_width", uiconf.width);
		self.addOptionalParam(params, "uiconf_height", uiconf.height);
		self.addOptionalParam(params, "uiconf_htmlParams", uiconf.htmlParams);
		self.addOptionalParam(params, "uiconf_swfUrl", uiconf.swfUrl);
		self.addOptionalParam(params, "uiconf_swfUrlVersion", uiconf.swfUrlVersion);
		self.addOptionalParam(params, "uiconf_confFile", uiconf.confFile);
		self.addOptionalParam(params, "uiconf_confVars", uiconf.confVars);
		self.addOptionalParam(params, "uiconf_useCdn", uiconf.useCdn);
		self.addOptionalParam(params, "uiconf_tags", uiconf.tags);

		return self.hit("adduiconf", kalturaSessionUser, params);

	def addUser(self, kalturaSessionUser, userId, user):
		params = {}
		params["user_id"] = userId;
		self.addOptionalParam(params, "user_screenName", user.screenName);
		self.addOptionalParam(params, "user_fullName", user.fullName);
		self.addOptionalParam(params, "user_email", user.email);
		self.addOptionalParam(params, "user_dateOfBirth", user.dateOfBirth);
		self.addOptionalParam(params, "user_aboutMe", user.aboutMe);
		self.addOptionalParam(params, "user_tags", user.tags);
		self.addOptionalParam(params, "user_gender", user.gender);
		self.addOptionalParam(params, "user_country", user.country);
		self.addOptionalParam(params, "user_state", user.state);
		self.addOptionalParam(params, "user_city", user.city);
		self.addOptionalParam(params, "user_zip", user.zip);
		self.addOptionalParam(params, "user_urlList", user.urlList);
		self.addOptionalParam(params, "user_networkHighschool", user.networkHighschool);
		self.addOptionalParam(params, "user_networkCollege", user.networkCollege);
		self.addOptionalParam(params, "user_partnerData", user.partnerData);

		return self.hit("adduser", kalturaSessionUser, params);

	def addWidget(self, kalturaSessionUser, widget):
		params = {}
		self.addOptionalParam(params, "widget_kshowId", widget.kshowId);
		self.addOptionalParam(params, "widget_entryId", widget.entryId);
		self.addOptionalParam(params, "widget_sourceWidgetId", widget.sourceWidgetId);
		self.addOptionalParam(params, "widget_uiConfId", widget.uiConfId);
		self.addOptionalParam(params, "widget_customData", widget.customData);
		self.addOptionalParam(params, "widget_partnerData", widget.partnerData);
		self.addOptionalParam(params, "widget_securityType", widget.securityType);

		return self.hit("addwidget", kalturaSessionUser, params);

	def adminLogin(self, kalturaSessionUser, email, password):
		params = {}
		params["email"] = email;
		params["password"] = password;

		return self.hit("adminlogin", kalturaSessionUser, params);

	def appendEntryToRoughcut(self, kalturaSessionUser, entryId, kshowId, showEntryId = None):
		params = {}
		params["entry_id"] = entryId;
		params["kshow_id"] = kshowId;
		self.addOptionalParam(params, "show_entry_id", showEntryId);

		return self.hit("appendentrytoroughcut", kalturaSessionUser, params);

	def checkNotifications(self, kalturaSessionUser, notificationIds, separator = ",", detailed = None):
		params = {}
		params["notification_ids"] = notificationIds;
		self.addOptionalParam(params, "separator", separator);
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("checknotifications", kalturaSessionUser, params);

	def cloneKShow(self, kalturaSessionUser, kshowId, detailed = None):
		params = {}
		params["kshow_id"] = kshowId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("clonekshow", kalturaSessionUser, params);

	def cloneRoughcut(self, kalturaSessionUser, entryId, detailed = None):
		params = {}
		params["entry_id"] = entryId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("cloneroughcut", kalturaSessionUser, params);

	def cloneUiConf(self, kalturaSessionUser, uiconfId, detailed = None):
		params = {}
		params["uiconf_id"] = uiconfId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("cloneuiconf", kalturaSessionUser, params);

	def deleteEntry(self, kalturaSessionUser, entryId):
		params = {}
		params["entry_id"] = entryId;

		return self.hit("deleteentry", kalturaSessionUser, params);

	def deleteKShow(self, kalturaSessionUser, kshowId):
		params = {}
		params["kshow_id"] = kshowId;

		return self.hit("deletekshow", kalturaSessionUser, params);

	def deletePlaylist(self, kalturaSessionUser, entryId):
		params = {}
		params["entry_id"] = entryId;

		return self.hit("deleteplaylist", kalturaSessionUser, params);

	def deleteUser(self, kalturaSessionUser, userId):
		params = {}
		params["user_id"] = userId;

		return self.hit("deleteuser", kalturaSessionUser, params);

	def executePlaylist(self, kalturaSessionUser, playlistId, fp = None, filter1 = None, filter2 = None, filter3 = None, filter4 = None, detailed = None, pageSize = 10, page = 1, useFilterPuserId = None):
		params = {}
		params["playlist_id"] = playlistId;
		self.addOptionalParam(params, "fp", fp);
		self.addOptionalParam(params, "filter1", filter1);
		self.addOptionalParam(params, "filter2", filter2);
		self.addOptionalParam(params, "filter3", filter3);
		self.addOptionalParam(params, "filter4", filter4);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "use_filter_puser_id", useFilterPuserId);

		return self.hit("executeplaylist", kalturaSessionUser, params);

	def getAdminTags(self, kalturaSessionUser):
		params = {}

		return self.hit("getadmintags", kalturaSessionUser, params);

	def getAllEntries(self, kalturaSessionUser, entryId, kshowId, listType = None, version = None, disableRoughcutEntryData = None):
		params = {}
		params["entry_id"] = entryId;
		params["kshow_id"] = kshowId;
		self.addOptionalParam(params, "list_type", listType);
		self.addOptionalParam(params, "version", version);
		self.addOptionalParam(params, "disable_roughcut_entry_data", disableRoughcutEntryData);

		return self.hit("getallentries", kalturaSessionUser, params);

	def getDefaultWidget(self, kalturaSessionUser, uiConfId = None):
		params = {}
		self.addOptionalParam(params, "ui_conf_id", uiConfId);

		return self.hit("getdefaultwidget", kalturaSessionUser, params);

	def getDvdEntry(self, kalturaSessionUser, dvdEntryId, detailed = None):
		params = {}
		params["dvdEntry_id"] = dvdEntryId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("getdvdentry", kalturaSessionUser, params);

	def getEntries(self, kalturaSessionUser, entryIds, separator = ",", detailed = None):
		params = {}
		params["entry_ids"] = entryIds;
		self.addOptionalParam(params, "separator", separator);
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("getentries", kalturaSessionUser, params);

	def getEntry(self, kalturaSessionUser, entryId, detailed = None, version = None):
		params = {}
		params["entry_id"] = entryId;
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "version", version);

		return self.hit("getentry", kalturaSessionUser, params);

	def getEntryRoughcuts(self, kalturaSessionUser, entryId):
		params = {}
		params["entry_id"] = entryId;

		return self.hit("getentryroughcuts", kalturaSessionUser, params);

	def getKShow(self, kalturaSessionUser, kshowId, detailed = None):
		params = {}
		params["kshow_id"] = kshowId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("getkshow", kalturaSessionUser, params);

	def getLastVersionsInfo(self, kalturaSessionUser, kshowId):
		params = {}
		params["kshow_id"] = kshowId;

		return self.hit("getlastversionsinfo", kalturaSessionUser, params);

	def getMetaDataAction(self, kalturaSessionUser, entryId, kshowId, version):
		params = {}
		params["entry_id"] = entryId;
		params["kshow_id"] = kshowId;
		params["version"] = version;

		return self.hit("getmetadata", kalturaSessionUser, params);

	def getPartner(self, kalturaSessionUser, partnerAdminEmail, cmsPassword, partnerId):
		params = {}
		params["partner_adminEmail"] = partnerAdminEmail;
		params["cms_password"] = cmsPassword;
		params["partner_id"] = partnerId;

		return self.hit("getpartner", kalturaSessionUser, params);

	def getPlaylist(self, kalturaSessionUser, playlistId, detailed = None):
		params = {}
		params["playlist_id"] = playlistId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("getplaylist", kalturaSessionUser, params);

	def getThumbnail(self, kalturaSessionUser, filename):
		params = {}
		params["filename"] = filename;

		return self.hit("getthumbnail", kalturaSessionUser, params);

	def getUIConf(self, kalturaSessionUser, uiConfId, detailed = None):
		params = {}
		params["ui_conf_id"] = uiConfId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("getuiconf", kalturaSessionUser, params);

	def getUser(self, kalturaSessionUser, userId, detailed = None):
		params = {}
		params["user_id"] = userId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("getuser", kalturaSessionUser, params);

	def getWidget(self, kalturaSessionUser, widgetId, detailed = None):
		params = {}
		params["widget_id"] = widgetId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("getwidget", kalturaSessionUser, params);

	def handleModeration(self, kalturaSessionUser, moderationId, moderationStatus):
		params = {}
		params["moderation_id"] = moderationId;
		params["moderation_status"] = moderationStatus;

		return self.hit("handlemoderation", kalturaSessionUser, params);

	def listConversionProfile(self, kalturaSessionUser, filter, detailed = None, pageSize = 10, page = 1):
		params = {}
		self.addOptionalParam(params, "filter__eq_id", filter.equalId);
		self.addOptionalParam(params, "filter__gte_id", filter.greaterThanOrEqualId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__in_profile_type", filter.inProfileType);
		self.addOptionalParam(params, "filter__eq_enabled", filter.equalEnabled);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__eq_use_with_bulk", filter.equalUseWithBulk);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);

		return self.hit("listconversionprofiles", kalturaSessionUser, params);

	def listDownloads(self, kalturaSessionUser, filter, detailed = None, pageSize = 10, page = 1):
		params = {}
		self.addOptionalParam(params, "filter__eq_id", filter.equalId);
		self.addOptionalParam(params, "filter__gte_id", filter.greaterThanOrEqualId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__eq_job_type", filter.equalJobType);
		self.addOptionalParam(params, "filter__in_job_type", filter.inJobType);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);

		return self.hit("listdownloads", kalturaSessionUser, params);

	def listDvdEntries(self, kalturaSessionUser, filter, detailed = None, detailedFields = None, pageSize = 10, page = 1, useFilterPuserId = None):
		params = {}
		self.addOptionalParam(params, "filter__eq_user_id", filter.equalUserId);
		self.addOptionalParam(params, "filter__eq_kshow_id", filter.equalKshowId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__in_status", filter.inStatus);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__in_type", filter.inType);
		self.addOptionalParam(params, "filter__eq_media_type", filter.equalMediaType);
		self.addOptionalParam(params, "filter__in_media_type", filter.inMediaType);
		self.addOptionalParam(params, "filter__eq_indexed_custom_data_1", filter.equalIndexedCustomData1);
		self.addOptionalParam(params, "filter__in_indexed_custom_data_1", filter.inIndexedCustomData1);
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__eq_name", filter.equalName);
		self.addOptionalParam(params, "filter__eq_tags", filter.equalTags);
		self.addOptionalParam(params, "filter__like_tags", filter.likeTags);
		self.addOptionalParam(params, "filter__mlikeor_tags", filter.multiLikeOrTags);
		self.addOptionalParam(params, "filter__mlikeand_tags", filter.multiLikeAndTags);
		self.addOptionalParam(params, "filter__mlikeor_admin_tags", filter.multiLikeOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeand_admin_tags", filter.multiLikeAndAdminTags);
		self.addOptionalParam(params, "filter__like_admin_tags", filter.likeAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_name", filter.multiLikeOrName);
		self.addOptionalParam(params, "filter__mlikeand_name", filter.multiLikeAndName);
		self.addOptionalParam(params, "filter__mlikeor_search_text", filter.multiLikeOrSearchText);
		self.addOptionalParam(params, "filter__mlikeand_search_text", filter.multiLikeAndSearchText);
		self.addOptionalParam(params, "filter__eq_group_id", filter.equalGroupId);
		self.addOptionalParam(params, "filter__gte_views", filter.greaterThanOrEqualViews);
		self.addOptionalParam(params, "filter__gte_created_at", filter.greaterThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__lte_created_at", filter.lessThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__gte_updated_at", filter.greaterThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__lte_updated_at", filter.lessThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__gte_modified_at", filter.greaterThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__lte_modified_at", filter.lessThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__in_partner_id", filter.inPartnerId);
		self.addOptionalParam(params, "filter__eq_partner_id", filter.equalPartnerId);
		self.addOptionalParam(params, "filter__eq_source_link", filter.equalSourceLink);
		self.addOptionalParam(params, "filter__gte_media_date", filter.greaterThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__lte_media_date", filter.lessThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__eq_moderation_status", filter.equalModerationStatus);
		self.addOptionalParam(params, "filter__in_moderation_status", filter.inModerationStatus);
		self.addOptionalParam(params, "filter__in_display_in_search", filter.inDisplayInSearch);
		self.addOptionalParam(params, "filter__mlikeor_tags-name", filter.multiLikeOrTagsOrName);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags", filter.multiLikeOrTagsOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags-name", filter.multiLikeOrTagsOrAdminTagsOrName);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "detailed_fields", detailedFields);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "use_filter_puser_id", useFilterPuserId);

		return self.hit("listdvdentries", kalturaSessionUser, params);

	def listEntries(self, kalturaSessionUser, filter, detailed = None, detailedFields = None, pageSize = 10, page = 1, useFilterPuserId = None):
		params = {}
		self.addOptionalParam(params, "filter__eq_user_id", filter.equalUserId);
		self.addOptionalParam(params, "filter__eq_kshow_id", filter.equalKshowId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__in_status", filter.inStatus);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__in_type", filter.inType);
		self.addOptionalParam(params, "filter__eq_media_type", filter.equalMediaType);
		self.addOptionalParam(params, "filter__in_media_type", filter.inMediaType);
		self.addOptionalParam(params, "filter__eq_indexed_custom_data_1", filter.equalIndexedCustomData1);
		self.addOptionalParam(params, "filter__in_indexed_custom_data_1", filter.inIndexedCustomData1);
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__eq_name", filter.equalName);
		self.addOptionalParam(params, "filter__eq_tags", filter.equalTags);
		self.addOptionalParam(params, "filter__like_tags", filter.likeTags);
		self.addOptionalParam(params, "filter__mlikeor_tags", filter.multiLikeOrTags);
		self.addOptionalParam(params, "filter__mlikeand_tags", filter.multiLikeAndTags);
		self.addOptionalParam(params, "filter__mlikeor_admin_tags", filter.multiLikeOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeand_admin_tags", filter.multiLikeAndAdminTags);
		self.addOptionalParam(params, "filter__like_admin_tags", filter.likeAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_name", filter.multiLikeOrName);
		self.addOptionalParam(params, "filter__mlikeand_name", filter.multiLikeAndName);
		self.addOptionalParam(params, "filter__mlikeor_search_text", filter.multiLikeOrSearchText);
		self.addOptionalParam(params, "filter__mlikeand_search_text", filter.multiLikeAndSearchText);
		self.addOptionalParam(params, "filter__eq_group_id", filter.equalGroupId);
		self.addOptionalParam(params, "filter__gte_views", filter.greaterThanOrEqualViews);
		self.addOptionalParam(params, "filter__gte_created_at", filter.greaterThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__lte_created_at", filter.lessThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__gte_updated_at", filter.greaterThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__lte_updated_at", filter.lessThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__gte_modified_at", filter.greaterThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__lte_modified_at", filter.lessThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__in_partner_id", filter.inPartnerId);
		self.addOptionalParam(params, "filter__eq_partner_id", filter.equalPartnerId);
		self.addOptionalParam(params, "filter__eq_source_link", filter.equalSourceLink);
		self.addOptionalParam(params, "filter__gte_media_date", filter.greaterThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__lte_media_date", filter.lessThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__eq_moderation_status", filter.equalModerationStatus);
		self.addOptionalParam(params, "filter__in_moderation_status", filter.inModerationStatus);
		self.addOptionalParam(params, "filter__in_display_in_search", filter.inDisplayInSearch);
		self.addOptionalParam(params, "filter__mlikeor_tags-name", filter.multiLikeOrTagsOrName);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags", filter.multiLikeOrTagsOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags-name", filter.multiLikeOrTagsOrAdminTagsOrName);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "detailed_fields", detailedFields);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "use_filter_puser_id", useFilterPuserId);

		return self.hit("listentries", kalturaSessionUser, params);

	def listKShows(self, kalturaSessionUser, filter, detailed = None, pageSize = 10, page = 1, useFilterPuserId = None):
		params = {}
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__like_tags", filter.likeTags);
		self.addOptionalParam(params, "filter__mlikeor_tags", filter.multiLikeOrTags);
		self.addOptionalParam(params, "filter__mlikeand_tags", filter.multiLikeAndTags);
		self.addOptionalParam(params, "filter__gte_views", filter.greaterThanOrEqualViews);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__eq_producer_id", filter.equalProducerId);
		self.addOptionalParam(params, "filter__gte_created_at", filter.greaterThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__lte_created_at", filter.lessThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__bitand_status", filter.bitAndStatus);
		self.addOptionalParam(params, "filter__eq_indexed_custom_data_3", filter.equalIndexedCustomData3);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "use_filter_puser_id", useFilterPuserId);

		return self.hit("listkshows", kalturaSessionUser, params);

	def listModerations(self, kalturaSessionUser, filter, detailed = None, pageSize = 10, page = 1):
		params = {}
		self.addOptionalParam(params, "filter__eq_id", filter.equalId);
		self.addOptionalParam(params, "filter__eq_puser_id", filter.equalPuserId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__in_status", filter.inStatus);
		self.addOptionalParam(params, "filter__like_comments", filter.likeComments);
		self.addOptionalParam(params, "filter__eq_object_id", filter.equalObjectId);
		self.addOptionalParam(params, "filter__eq_object_type", filter.equalObjectType);
		self.addOptionalParam(params, "filter__eq_group_id", filter.equalGroupId);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);

		return self.hit("listmoderations", kalturaSessionUser, params);

	def listMyDvdEntries(self, kalturaSessionUser, filter, detailed = None, pageSize = 10, page = 1, useFilterPuserId = None):
		params = {}
		self.addOptionalParam(params, "filter__eq_user_id", filter.equalUserId);
		self.addOptionalParam(params, "filter__eq_kshow_id", filter.equalKshowId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__in_status", filter.inStatus);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__in_type", filter.inType);
		self.addOptionalParam(params, "filter__eq_media_type", filter.equalMediaType);
		self.addOptionalParam(params, "filter__in_media_type", filter.inMediaType);
		self.addOptionalParam(params, "filter__eq_indexed_custom_data_1", filter.equalIndexedCustomData1);
		self.addOptionalParam(params, "filter__in_indexed_custom_data_1", filter.inIndexedCustomData1);
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__eq_name", filter.equalName);
		self.addOptionalParam(params, "filter__eq_tags", filter.equalTags);
		self.addOptionalParam(params, "filter__like_tags", filter.likeTags);
		self.addOptionalParam(params, "filter__mlikeor_tags", filter.multiLikeOrTags);
		self.addOptionalParam(params, "filter__mlikeand_tags", filter.multiLikeAndTags);
		self.addOptionalParam(params, "filter__mlikeor_admin_tags", filter.multiLikeOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeand_admin_tags", filter.multiLikeAndAdminTags);
		self.addOptionalParam(params, "filter__like_admin_tags", filter.likeAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_name", filter.multiLikeOrName);
		self.addOptionalParam(params, "filter__mlikeand_name", filter.multiLikeAndName);
		self.addOptionalParam(params, "filter__mlikeor_search_text", filter.multiLikeOrSearchText);
		self.addOptionalParam(params, "filter__mlikeand_search_text", filter.multiLikeAndSearchText);
		self.addOptionalParam(params, "filter__eq_group_id", filter.equalGroupId);
		self.addOptionalParam(params, "filter__gte_views", filter.greaterThanOrEqualViews);
		self.addOptionalParam(params, "filter__gte_created_at", filter.greaterThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__lte_created_at", filter.lessThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__gte_updated_at", filter.greaterThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__lte_updated_at", filter.lessThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__gte_modified_at", filter.greaterThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__lte_modified_at", filter.lessThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__in_partner_id", filter.inPartnerId);
		self.addOptionalParam(params, "filter__eq_partner_id", filter.equalPartnerId);
		self.addOptionalParam(params, "filter__eq_source_link", filter.equalSourceLink);
		self.addOptionalParam(params, "filter__gte_media_date", filter.greaterThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__lte_media_date", filter.lessThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__eq_moderation_status", filter.equalModerationStatus);
		self.addOptionalParam(params, "filter__in_moderation_status", filter.inModerationStatus);
		self.addOptionalParam(params, "filter__in_display_in_search", filter.inDisplayInSearch);
		self.addOptionalParam(params, "filter__mlikeor_tags-name", filter.multiLikeOrTagsOrName);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags", filter.multiLikeOrTagsOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags-name", filter.multiLikeOrTagsOrAdminTagsOrName);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "use_filter_puser_id", useFilterPuserId);

		return self.hit("listmydvdentries", kalturaSessionUser, params);

	def listMyEntries(self, kalturaSessionUser, filter, detailed = None, pageSize = 10, page = 1, useFilterPuserId = None):
		params = {}
		self.addOptionalParam(params, "filter__eq_user_id", filter.equalUserId);
		self.addOptionalParam(params, "filter__eq_kshow_id", filter.equalKshowId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__in_status", filter.inStatus);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__in_type", filter.inType);
		self.addOptionalParam(params, "filter__eq_media_type", filter.equalMediaType);
		self.addOptionalParam(params, "filter__in_media_type", filter.inMediaType);
		self.addOptionalParam(params, "filter__eq_indexed_custom_data_1", filter.equalIndexedCustomData1);
		self.addOptionalParam(params, "filter__in_indexed_custom_data_1", filter.inIndexedCustomData1);
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__eq_name", filter.equalName);
		self.addOptionalParam(params, "filter__eq_tags", filter.equalTags);
		self.addOptionalParam(params, "filter__like_tags", filter.likeTags);
		self.addOptionalParam(params, "filter__mlikeor_tags", filter.multiLikeOrTags);
		self.addOptionalParam(params, "filter__mlikeand_tags", filter.multiLikeAndTags);
		self.addOptionalParam(params, "filter__mlikeor_admin_tags", filter.multiLikeOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeand_admin_tags", filter.multiLikeAndAdminTags);
		self.addOptionalParam(params, "filter__like_admin_tags", filter.likeAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_name", filter.multiLikeOrName);
		self.addOptionalParam(params, "filter__mlikeand_name", filter.multiLikeAndName);
		self.addOptionalParam(params, "filter__mlikeor_search_text", filter.multiLikeOrSearchText);
		self.addOptionalParam(params, "filter__mlikeand_search_text", filter.multiLikeAndSearchText);
		self.addOptionalParam(params, "filter__eq_group_id", filter.equalGroupId);
		self.addOptionalParam(params, "filter__gte_views", filter.greaterThanOrEqualViews);
		self.addOptionalParam(params, "filter__gte_created_at", filter.greaterThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__lte_created_at", filter.lessThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__gte_updated_at", filter.greaterThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__lte_updated_at", filter.lessThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__gte_modified_at", filter.greaterThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__lte_modified_at", filter.lessThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__in_partner_id", filter.inPartnerId);
		self.addOptionalParam(params, "filter__eq_partner_id", filter.equalPartnerId);
		self.addOptionalParam(params, "filter__eq_source_link", filter.equalSourceLink);
		self.addOptionalParam(params, "filter__gte_media_date", filter.greaterThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__lte_media_date", filter.lessThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__eq_moderation_status", filter.equalModerationStatus);
		self.addOptionalParam(params, "filter__in_moderation_status", filter.inModerationStatus);
		self.addOptionalParam(params, "filter__in_display_in_search", filter.inDisplayInSearch);
		self.addOptionalParam(params, "filter__mlikeor_tags-name", filter.multiLikeOrTagsOrName);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags", filter.multiLikeOrTagsOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags-name", filter.multiLikeOrTagsOrAdminTagsOrName);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "use_filter_puser_id", useFilterPuserId);

		return self.hit("listmyentries", kalturaSessionUser, params);

	def listMyKShows(self, kalturaSessionUser, filter, detailed = None, pageSize = 10, page = 1, useFilterPuserId = None):
		params = {}
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__like_tags", filter.likeTags);
		self.addOptionalParam(params, "filter__mlikeor_tags", filter.multiLikeOrTags);
		self.addOptionalParam(params, "filter__mlikeand_tags", filter.multiLikeAndTags);
		self.addOptionalParam(params, "filter__gte_views", filter.greaterThanOrEqualViews);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__eq_producer_id", filter.equalProducerId);
		self.addOptionalParam(params, "filter__gte_created_at", filter.greaterThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__lte_created_at", filter.lessThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__bitand_status", filter.bitAndStatus);
		self.addOptionalParam(params, "filter__eq_indexed_custom_data_3", filter.equalIndexedCustomData3);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "use_filter_puser_id", useFilterPuserId);

		return self.hit("listmykshows", kalturaSessionUser, params);

	def listNotifications(self, kalturaSessionUser, filter, pageSize = 10, page = 1):
		params = {}
		self.addOptionalParam(params, "filter__eq_id", filter.equalId);
		self.addOptionalParam(params, "filter__gte_id", filter.greaterThanOrEqualId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);

		return self.hit("listnotifications", kalturaSessionUser, params);

	def listPartnerEntries(self, kalturaSessionUser, filter, detailed = None, pageSize = 10, page = 1, useFilterPuserId = None):
		params = {}
		self.addOptionalParam(params, "filter__eq_user_id", filter.equalUserId);
		self.addOptionalParam(params, "filter__eq_kshow_id", filter.equalKshowId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__in_status", filter.inStatus);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__in_type", filter.inType);
		self.addOptionalParam(params, "filter__eq_media_type", filter.equalMediaType);
		self.addOptionalParam(params, "filter__in_media_type", filter.inMediaType);
		self.addOptionalParam(params, "filter__eq_indexed_custom_data_1", filter.equalIndexedCustomData1);
		self.addOptionalParam(params, "filter__in_indexed_custom_data_1", filter.inIndexedCustomData1);
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__eq_name", filter.equalName);
		self.addOptionalParam(params, "filter__eq_tags", filter.equalTags);
		self.addOptionalParam(params, "filter__like_tags", filter.likeTags);
		self.addOptionalParam(params, "filter__mlikeor_tags", filter.multiLikeOrTags);
		self.addOptionalParam(params, "filter__mlikeand_tags", filter.multiLikeAndTags);
		self.addOptionalParam(params, "filter__mlikeor_admin_tags", filter.multiLikeOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeand_admin_tags", filter.multiLikeAndAdminTags);
		self.addOptionalParam(params, "filter__like_admin_tags", filter.likeAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_name", filter.multiLikeOrName);
		self.addOptionalParam(params, "filter__mlikeand_name", filter.multiLikeAndName);
		self.addOptionalParam(params, "filter__mlikeor_search_text", filter.multiLikeOrSearchText);
		self.addOptionalParam(params, "filter__mlikeand_search_text", filter.multiLikeAndSearchText);
		self.addOptionalParam(params, "filter__eq_group_id", filter.equalGroupId);
		self.addOptionalParam(params, "filter__gte_views", filter.greaterThanOrEqualViews);
		self.addOptionalParam(params, "filter__gte_created_at", filter.greaterThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__lte_created_at", filter.lessThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__gte_updated_at", filter.greaterThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__lte_updated_at", filter.lessThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__gte_modified_at", filter.greaterThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__lte_modified_at", filter.lessThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__in_partner_id", filter.inPartnerId);
		self.addOptionalParam(params, "filter__eq_partner_id", filter.equalPartnerId);
		self.addOptionalParam(params, "filter__eq_source_link", filter.equalSourceLink);
		self.addOptionalParam(params, "filter__gte_media_date", filter.greaterThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__lte_media_date", filter.lessThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__eq_moderation_status", filter.equalModerationStatus);
		self.addOptionalParam(params, "filter__in_moderation_status", filter.inModerationStatus);
		self.addOptionalParam(params, "filter__in_display_in_search", filter.inDisplayInSearch);
		self.addOptionalParam(params, "filter__mlikeor_tags-name", filter.multiLikeOrTagsOrName);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags", filter.multiLikeOrTagsOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags-name", filter.multiLikeOrTagsOrAdminTagsOrName);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "use_filter_puser_id", useFilterPuserId);

		return self.hit("listpartnerentries", kalturaSessionUser, params);

	def listPlaylists(self, kalturaSessionUser, filter, detailed = None, detailedFields = None, pageSize = 10, page = 1, useFilterPuserId = None):
		params = {}
		self.addOptionalParam(params, "filter__eq_user_id", filter.equalUserId);
		self.addOptionalParam(params, "filter__eq_kshow_id", filter.equalKshowId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__in_status", filter.inStatus);
		self.addOptionalParam(params, "filter__eq_type", filter.equalType);
		self.addOptionalParam(params, "filter__in_type", filter.inType);
		self.addOptionalParam(params, "filter__eq_media_type", filter.equalMediaType);
		self.addOptionalParam(params, "filter__in_media_type", filter.inMediaType);
		self.addOptionalParam(params, "filter__eq_indexed_custom_data_1", filter.equalIndexedCustomData1);
		self.addOptionalParam(params, "filter__in_indexed_custom_data_1", filter.inIndexedCustomData1);
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__eq_name", filter.equalName);
		self.addOptionalParam(params, "filter__eq_tags", filter.equalTags);
		self.addOptionalParam(params, "filter__like_tags", filter.likeTags);
		self.addOptionalParam(params, "filter__mlikeor_tags", filter.multiLikeOrTags);
		self.addOptionalParam(params, "filter__mlikeand_tags", filter.multiLikeAndTags);
		self.addOptionalParam(params, "filter__mlikeor_admin_tags", filter.multiLikeOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeand_admin_tags", filter.multiLikeAndAdminTags);
		self.addOptionalParam(params, "filter__like_admin_tags", filter.likeAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_name", filter.multiLikeOrName);
		self.addOptionalParam(params, "filter__mlikeand_name", filter.multiLikeAndName);
		self.addOptionalParam(params, "filter__mlikeor_search_text", filter.multiLikeOrSearchText);
		self.addOptionalParam(params, "filter__mlikeand_search_text", filter.multiLikeAndSearchText);
		self.addOptionalParam(params, "filter__eq_group_id", filter.equalGroupId);
		self.addOptionalParam(params, "filter__gte_views", filter.greaterThanOrEqualViews);
		self.addOptionalParam(params, "filter__gte_created_at", filter.greaterThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__lte_created_at", filter.lessThanOrEqualCreatedAt);
		self.addOptionalParam(params, "filter__gte_updated_at", filter.greaterThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__lte_updated_at", filter.lessThanOrEqualUpdatedAt);
		self.addOptionalParam(params, "filter__gte_modified_at", filter.greaterThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__lte_modified_at", filter.lessThanOrEqualModifiedAt);
		self.addOptionalParam(params, "filter__in_partner_id", filter.inPartnerId);
		self.addOptionalParam(params, "filter__eq_partner_id", filter.equalPartnerId);
		self.addOptionalParam(params, "filter__eq_source_link", filter.equalSourceLink);
		self.addOptionalParam(params, "filter__gte_media_date", filter.greaterThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__lte_media_date", filter.lessThanOrEqualMediaDate);
		self.addOptionalParam(params, "filter__eq_moderation_status", filter.equalModerationStatus);
		self.addOptionalParam(params, "filter__in_moderation_status", filter.inModerationStatus);
		self.addOptionalParam(params, "filter__in_display_in_search", filter.inDisplayInSearch);
		self.addOptionalParam(params, "filter__mlikeor_tags-name", filter.multiLikeOrTagsOrName);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags", filter.multiLikeOrTagsOrAdminTags);
		self.addOptionalParam(params, "filter__mlikeor_tags-admin_tags-name", filter.multiLikeOrTagsOrAdminTagsOrName);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "detailed_fields", detailedFields);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "use_filter_puser_id", useFilterPuserId);

		return self.hit("listplaylists", kalturaSessionUser, params);

	def listUiconf(self, kalturaSessionUser, filter, detailed = None, detailedFields = None, pageSize = 10, page = 1):
		params = {}
		self.addOptionalParam(params, "filter__eq_id", filter.equalId);
		self.addOptionalParam(params, "filter__gte_id", filter.greaterThanOrEqualId);
		self.addOptionalParam(params, "filter__eq_status", filter.equalStatus);
		self.addOptionalParam(params, "filter__eq_obj_type", filter.equalObjType);
		self.addOptionalParam(params, "filter__like_name", filter.likeName);
		self.addOptionalParam(params, "filter__mlikeor_tags", filter.multiLikeOrTags);
		self.addOptionalParam(params, "filter__order_by", filter.orderBy);
		self.addOptionalParam(params, "filter__limit", filter.limit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "detailed_fields", detailedFields);
		self.addOptionalParam(params, "page_size", pageSize);
		self.addOptionalParam(params, "page", page);

		return self.hit("listuiconfs", kalturaSessionUser, params);

	def ping(self, kalturaSessionUser):
		params = {}

		return self.hit("ping", kalturaSessionUser, params);

	def queuePendingBatchJob(self, kalturaSessionUser, jobType, processorName, processorTimeout, overQuotaPartners = None, deferedPartners = None):
		params = {}
		params["job_type"] = jobType;
		params["processor_name"] = processorName;
		params["processor_timeout"] = processorTimeout;
		self.addOptionalParam(params, "over_quota_partners", overQuotaPartners);
		self.addOptionalParam(params, "defered_partners", deferedPartners);

		return self.hit("queuependingbatchjob", kalturaSessionUser, params);

	def rankKShow(self, kalturaSessionUser, kshowId, rank):
		params = {}
		params["kshow_id"] = kshowId;
		params["rank"] = rank;

		return self.hit("rankkshow", kalturaSessionUser, params);

	def registerPartner(self, kalturaSessionUser, partner, cmsPassword = None):
		params = {}
		self.addOptionalParam(params, "partner_name", partner.name);
		self.addOptionalParam(params, "partner_url1", partner.url1);
		self.addOptionalParam(params, "partner_url2", partner.url2);
		self.addOptionalParam(params, "partner_appearInSearch", partner.appearInSearch);
		self.addOptionalParam(params, "partner_adminName", partner.adminName);
		self.addOptionalParam(params, "partner_adminEmail", partner.adminEmail);
		self.addOptionalParam(params, "partner_description", partner.description);
		self.addOptionalParam(params, "partner_commercialUse", partner.commercialUse);
		self.addOptionalParam(params, "partner_landingPage", partner.landingPage);
		self.addOptionalParam(params, "partner_userLandingPage", partner.userLandingPage);
		self.addOptionalParam(params, "partner_notificationsConfig", partner.notificationsConfig);
		self.addOptionalParam(params, "partner_notify", partner.notify);
		self.addOptionalParam(params, "partner_allowMultiNotification", partner.allowMultiNotification);
		self.addOptionalParam(params, "partner_contentCategories", partner.contentCategories);
		self.addOptionalParam(params, "partner_type", partner.type);
		self.addOptionalParam(params, "cms_password", cmsPassword);

		return self.hit("registerpartner", kalturaSessionUser, params);

	def reportEntry(self, kalturaSessionUser, moderation):
		params = {}
		self.addOptionalParam(params, "moderation_comments", moderation.comments);
		self.addOptionalParam(params, "moderation_objectType", moderation.objectType);
		self.addOptionalParam(params, "moderation_objectId", moderation.objectId);
		self.addOptionalParam(params, "moderation_reportCode", moderation.reportCode);
		self.addOptionalParam(params, "moderation_status", moderation.status);

		return self.hit("reportentry", kalturaSessionUser, params);

	def reportError(self, kalturaSessionUser, reportingObj = None, errorCode = None, errorDescription = None):
		params = {}
		self.addOptionalParam(params, "reporting_obj", reportingObj);
		self.addOptionalParam(params, "error_code", errorCode);
		self.addOptionalParam(params, "error_description", errorDescription);

		return self.hit("reporterror", kalturaSessionUser, params);

	def reportKShow(self, kalturaSessionUser, moderation):
		params = {}
		self.addOptionalParam(params, "moderation_comments", moderation.comments);
		self.addOptionalParam(params, "moderation_objectType", moderation.objectType);
		self.addOptionalParam(params, "moderation_objectId", moderation.objectId);
		self.addOptionalParam(params, "moderation_reportCode", moderation.reportCode);
		self.addOptionalParam(params, "moderation_status", moderation.status);

		return self.hit("reportkshow", kalturaSessionUser, params);

	def reportUser(self, kalturaSessionUser, moderation):
		params = {}
		self.addOptionalParam(params, "moderation_comments", moderation.comments);
		self.addOptionalParam(params, "moderation_objectType", moderation.objectType);
		self.addOptionalParam(params, "moderation_objectId", moderation.objectId);
		self.addOptionalParam(params, "moderation_reportCode", moderation.reportCode);
		self.addOptionalParam(params, "moderation_status", moderation.status);

		return self.hit("reportuser", kalturaSessionUser, params);

	def rollbackKShow(self, kalturaSessionUser, kshowId, kshowVersion):
		params = {}
		params["kshow_id"] = kshowId;
		params["kshow_version"] = kshowVersion;

		return self.hit("rollbackkshow", kalturaSessionUser, params);

	def search(self, kalturaSessionUser, mediaType, mediaSource, search, authData = None, page = 1, pageSize = 10):
		params = {}
		params["media_type"] = mediaType;
		params["media_source"] = mediaSource;
		params["search"] = search;
		self.addOptionalParam(params, "auth_data", authData);
		self.addOptionalParam(params, "page", page);
		self.addOptionalParam(params, "page_size", pageSize);

		return self.hit("search", kalturaSessionUser, params);

	def searchAuthData(self, kalturaSessionUser, mediaSource, username, password):
		params = {}
		params["media_source"] = mediaSource;
		params["username"] = username;
		params["password"] = password;

		return self.hit("searchauthdata", kalturaSessionUser, params);

	def searchFromUrl(self, kalturaSessionUser, url, mediaType):
		params = {}
		params["url"] = url;
		params["media_type"] = mediaType;

		return self.hit("searchfromurl", kalturaSessionUser, params);

	def searchMediaInfo(self, kalturaSessionUser, mediaType, mediaSource, mediaId):
		params = {}
		params["media_type"] = mediaType;
		params["media_source"] = mediaSource;
		params["media_id"] = mediaId;

		return self.hit("searchmediainfo", kalturaSessionUser, params);

	def searchmediaproviders(self, kalturaSessionUser):
		params = {}

		return self.hit("searchmediaproviders", kalturaSessionUser, params);

	def setMetaData(self, kalturaSessionUser, entryId, kshowId, hasRoughCut, xml):
		params = {}
		params["entry_id"] = entryId;
		params["kshow_id"] = kshowId;
		params["HasRoughCut"] = hasRoughCut;
		params["xml"] = xml;

		return self.hit("setmetadata", kalturaSessionUser, params);

	def startSession(self, kalturaSessionUser, secret, admin = None, privileges = None, expiry = 86400):
		params = {}
		params["secret"] = secret;
		self.addOptionalParam(params, "admin", admin);
		self.addOptionalParam(params, "privileges", privileges);
		self.addOptionalParam(params, "expiry", expiry);

		return self.hit("startsession", kalturaSessionUser, params);

	def startWidgetSession(self, kalturaSessionUser, widgetId, expiry = 86400):
		params = {}
		params["widget_id"] = widgetId;
		self.addOptionalParam(params, "expiry", expiry);

		return self.hit("startwidgetsession", kalturaSessionUser, params);

	def testNotification(self, kalturaSessionUser):
		params = {}

		return self.hit("testnotification", kalturaSessionUser, params);

	def updateBatchJob(self, kalturaSessionUser, batchjobId, batchjob):
		params = {}
		params["batchjob_id"] = batchjobId;
		self.addOptionalParam(params, "batchjob_data", batchjob.data);
		self.addOptionalParam(params, "batchjob_status", batchjob.status);
		self.addOptionalParam(params, "batchjob_abort", batchjob.abort);
		self.addOptionalParam(params, "batchjob_checkAgainTimeout", batchjob.checkAgainTimeout);
		self.addOptionalParam(params, "batchjob_progress", batchjob.progress);
		self.addOptionalParam(params, "batchjob_message", batchjob.message);
		self.addOptionalParam(params, "batchjob_description", batchjob.description);
		self.addOptionalParam(params, "batchjob_updatesCount", batchjob.updatesCount);
		self.addOptionalParam(params, "batchjob_processorExpiration", batchjob.processorExpiration);

		return self.hit("updatebatchjob", kalturaSessionUser, params);

	def updateDvdEntry(self, kalturaSessionUser, entryId, entry):
		params = {}
		params["entry_id"] = entryId;
		self.addOptionalParam(params, "entry_name", entry.name);
		self.addOptionalParam(params, "entry_tags", entry.tags);
		self.addOptionalParam(params, "entry_type", entry.type);
		self.addOptionalParam(params, "entry_mediaType", entry.mediaType);
		self.addOptionalParam(params, "entry_source", entry.source);
		self.addOptionalParam(params, "entry_sourceId", entry.sourceId);
		self.addOptionalParam(params, "entry_sourceLink", entry.sourceLink);
		self.addOptionalParam(params, "entry_licenseType", entry.licenseType);
		self.addOptionalParam(params, "entry_credit", entry.credit);
		self.addOptionalParam(params, "entry_groupId", entry.groupId);
		self.addOptionalParam(params, "entry_partnerData", entry.partnerData);
		self.addOptionalParam(params, "entry_conversionQuality", entry.conversionQuality);
		self.addOptionalParam(params, "entry_permissions", entry.permissions);
		self.addOptionalParam(params, "entry_dataContent", entry.dataContent);
		self.addOptionalParam(params, "entry_desiredVersion", entry.desiredVersion);
		self.addOptionalParam(params, "entry_url", entry.url);
		self.addOptionalParam(params, "entry_thumbUrl", entry.thumbUrl);
		self.addOptionalParam(params, "entry_filename", entry.filename);
		self.addOptionalParam(params, "entry_realFilename", entry.realFilename);
		self.addOptionalParam(params, "entry_indexedCustomData1", entry.indexedCustomData1);
		self.addOptionalParam(params, "entry_thumbOffset", entry.thumbOffset);
		self.addOptionalParam(params, "entry_mediaId", entry.mediaId);
		self.addOptionalParam(params, "entry_screenName", entry.screenName);
		self.addOptionalParam(params, "entry_siteUrl", entry.siteUrl);
		self.addOptionalParam(params, "entry_description", entry.description);
		self.addOptionalParam(params, "entry_mediaDate", entry.mediaDate);
		self.addOptionalParam(params, "entry_adminTags", entry.adminTags);

		return self.hit("updatedvdentry", kalturaSessionUser, params);

	def updateEntriesThumbnails(self, kalturaSessionUser, entryIds, timeOffset):
		params = {}
		params["entry_ids"] = entryIds;
		params["time_offset"] = timeOffset;

		return self.hit("updateentriesthumbnails", kalturaSessionUser, params);

	def updateEntry(self, kalturaSessionUser, entryId, entry, allowEmptyField = None):
		params = {}
		params["entry_id"] = entryId;
		self.addOptionalParam(params, "entry_name", entry.name);
		self.addOptionalParam(params, "entry_tags", entry.tags);
		self.addOptionalParam(params, "entry_type", entry.type);
		self.addOptionalParam(params, "entry_mediaType", entry.mediaType);
		self.addOptionalParam(params, "entry_source", entry.source);
		self.addOptionalParam(params, "entry_sourceId", entry.sourceId);
		self.addOptionalParam(params, "entry_sourceLink", entry.sourceLink);
		self.addOptionalParam(params, "entry_licenseType", entry.licenseType);
		self.addOptionalParam(params, "entry_credit", entry.credit);
		self.addOptionalParam(params, "entry_groupId", entry.groupId);
		self.addOptionalParam(params, "entry_partnerData", entry.partnerData);
		self.addOptionalParam(params, "entry_conversionQuality", entry.conversionQuality);
		self.addOptionalParam(params, "entry_permissions", entry.permissions);
		self.addOptionalParam(params, "entry_dataContent", entry.dataContent);
		self.addOptionalParam(params, "entry_desiredVersion", entry.desiredVersion);
		self.addOptionalParam(params, "entry_url", entry.url);
		self.addOptionalParam(params, "entry_thumbUrl", entry.thumbUrl);
		self.addOptionalParam(params, "entry_filename", entry.filename);
		self.addOptionalParam(params, "entry_realFilename", entry.realFilename);
		self.addOptionalParam(params, "entry_indexedCustomData1", entry.indexedCustomData1);
		self.addOptionalParam(params, "entry_thumbOffset", entry.thumbOffset);
		self.addOptionalParam(params, "entry_mediaId", entry.mediaId);
		self.addOptionalParam(params, "entry_screenName", entry.screenName);
		self.addOptionalParam(params, "entry_siteUrl", entry.siteUrl);
		self.addOptionalParam(params, "entry_description", entry.description);
		self.addOptionalParam(params, "entry_mediaDate", entry.mediaDate);
		self.addOptionalParam(params, "entry_adminTags", entry.adminTags);
		self.addOptionalParam(params, "allow_empty_field", allowEmptyField);

		return self.hit("updateentry", kalturaSessionUser, params);

	def updateEntryTModeration(self, kalturaSessionUser, entryId, moderationStatus):
		params = {}
		params["entry_id"] = entryId;
		params["moderation_status"] = moderationStatus;

		return self.hit("updateentrymoderation", kalturaSessionUser, params);

	def updateEntryThumbnail(self, kalturaSessionUser, entryId, sourceEntryId = None, timeOffset = None):
		params = {}
		params["entry_id"] = entryId;
		self.addOptionalParam(params, "source_entry_id", sourceEntryId);
		self.addOptionalParam(params, "time_offset", timeOffset);

		return self.hit("updateentrythumbnail", kalturaSessionUser, params);

	def updateEntryThumbnailJpeg(self, kalturaSessionUser, entryId):
		params = {}
		params["entry_id"] = entryId;

		return self.hit("updateentrythumbnailjpeg", kalturaSessionUser, params);

	def updateKShow(self, kalturaSessionUser, kshowId, kshow, detailed = None, allowDuplicateNames = None):
		params = {}
		params["kshow_id"] = kshowId;
		self.addOptionalParam(params, "kshow_name", kshow.name);
		self.addOptionalParam(params, "kshow_description", kshow.description);
		self.addOptionalParam(params, "kshow_tags", kshow.tags);
		self.addOptionalParam(params, "kshow_indexedCustomData3", kshow.indexedCustomData3);
		self.addOptionalParam(params, "kshow_groupId", kshow.groupId);
		self.addOptionalParam(params, "kshow_permissions", kshow.permissions);
		self.addOptionalParam(params, "kshow_partnerData", kshow.partnerData);
		self.addOptionalParam(params, "kshow_allowQuickEdit", kshow.allowQuickEdit);
		self.addOptionalParam(params, "detailed", detailed);
		self.addOptionalParam(params, "allow_duplicate_names", allowDuplicateNames);

		return self.hit("updatekshow", kalturaSessionUser, params);

	def updateKshowOwner(self, kalturaSessionUser, kshowId, detailed = None):
		params = {}
		params["kshow_id"] = kshowId;
		self.addOptionalParam(params, "detailed", detailed);

		return self.hit("updatekshowowner", kalturaSessionUser, params);

	def updateNotification(self, kalturaSessionUser, notification):
		params = {}
		self.addOptionalParam(params, "notification_id", notification.id);
		self.addOptionalParam(params, "notification_status", notification.status);
		self.addOptionalParam(params, "notification_notificationResult", notification.notificationResult);

		return self.hit("updatenotification", kalturaSessionUser, params);

	def updatePartner(self, kalturaSessionUser, partner):
		params = {}
		self.addOptionalParam(params, "partner_name", partner.name);
		self.addOptionalParam(params, "partner_url1", partner.url1);
		self.addOptionalParam(params, "partner_url2", partner.url2);
		self.addOptionalParam(params, "partner_appearInSearch", partner.appearInSearch);
		self.addOptionalParam(params, "partner_adminName", partner.adminName);
		self.addOptionalParam(params, "partner_adminEmail", partner.adminEmail);
		self.addOptionalParam(params, "partner_description", partner.description);
		self.addOptionalParam(params, "partner_commercialUse", partner.commercialUse);
		self.addOptionalParam(params, "partner_landingPage", partner.landingPage);
		self.addOptionalParam(params, "partner_userLandingPage", partner.userLandingPage);
		self.addOptionalParam(params, "partner_notificationsConfig", partner.notificationsConfig);
		self.addOptionalParam(params, "partner_notify", partner.notify);
		self.addOptionalParam(params, "partner_allowMultiNotification", partner.allowMultiNotification);
		self.addOptionalParam(params, "partner_contentCategories", partner.contentCategories);
		self.addOptionalParam(params, "partner_type", partner.type);

		return self.hit("updatepartner", kalturaSessionUser, params);

	def updatePlaylist(self, kalturaSessionUser, entryId, entry):
		params = {}
		params["entry_id"] = entryId;
		self.addOptionalParam(params, "entry_name", entry.name);
		self.addOptionalParam(params, "entry_tags", entry.tags);
		self.addOptionalParam(params, "entry_type", entry.type);
		self.addOptionalParam(params, "entry_mediaType", entry.mediaType);
		self.addOptionalParam(params, "entry_source", entry.source);
		self.addOptionalParam(params, "entry_sourceId", entry.sourceId);
		self.addOptionalParam(params, "entry_sourceLink", entry.sourceLink);
		self.addOptionalParam(params, "entry_licenseType", entry.licenseType);
		self.addOptionalParam(params, "entry_credit", entry.credit);
		self.addOptionalParam(params, "entry_groupId", entry.groupId);
		self.addOptionalParam(params, "entry_partnerData", entry.partnerData);
		self.addOptionalParam(params, "entry_conversionQuality", entry.conversionQuality);
		self.addOptionalParam(params, "entry_permissions", entry.permissions);
		self.addOptionalParam(params, "entry_dataContent", entry.dataContent);
		self.addOptionalParam(params, "entry_desiredVersion", entry.desiredVersion);
		self.addOptionalParam(params, "entry_url", entry.url);
		self.addOptionalParam(params, "entry_thumbUrl", entry.thumbUrl);
		self.addOptionalParam(params, "entry_filename", entry.filename);
		self.addOptionalParam(params, "entry_realFilename", entry.realFilename);
		self.addOptionalParam(params, "entry_indexedCustomData1", entry.indexedCustomData1);
		self.addOptionalParam(params, "entry_thumbOffset", entry.thumbOffset);
		self.addOptionalParam(params, "entry_mediaId", entry.mediaId);
		self.addOptionalParam(params, "entry_screenName", entry.screenName);
		self.addOptionalParam(params, "entry_siteUrl", entry.siteUrl);
		self.addOptionalParam(params, "entry_description", entry.description);
		self.addOptionalParam(params, "entry_mediaDate", entry.mediaDate);
		self.addOptionalParam(params, "entry_adminTags", entry.adminTags);

		return self.hit("updateplaylist", kalturaSessionUser, params);

	def updateUiconf(self, kalturaSessionUser, uiconfId, uiconf):
		params = {}
		params["uiconf_id"] = uiconfId;
		self.addOptionalParam(params, "uiconf_name", uiconf.name);
		self.addOptionalParam(params, "uiconf_objType", uiconf.objType);
		self.addOptionalParam(params, "uiconf_width", uiconf.width);
		self.addOptionalParam(params, "uiconf_height", uiconf.height);
		self.addOptionalParam(params, "uiconf_htmlParams", uiconf.htmlParams);
		self.addOptionalParam(params, "uiconf_swfUrl", uiconf.swfUrl);
		self.addOptionalParam(params, "uiconf_swfUrlVersion", uiconf.swfUrlVersion);
		self.addOptionalParam(params, "uiconf_confFile", uiconf.confFile);
		self.addOptionalParam(params, "uiconf_confVars", uiconf.confVars);
		self.addOptionalParam(params, "uiconf_useCdn", uiconf.useCdn);
		self.addOptionalParam(params, "uiconf_tags", uiconf.tags);

		return self.hit("updateuiconf", kalturaSessionUser, params);

	def updateUser(self, kalturaSessionUser, userId, user):
		params = {}
		params["user_id"] = userId;
		self.addOptionalParam(params, "user_screenName", user.screenName);
		self.addOptionalParam(params, "user_fullName", user.fullName);
		self.addOptionalParam(params, "user_email", user.email);
		self.addOptionalParam(params, "user_dateOfBirth", user.dateOfBirth);
		self.addOptionalParam(params, "user_aboutMe", user.aboutMe);
		self.addOptionalParam(params, "user_tags", user.tags);
		self.addOptionalParam(params, "user_gender", user.gender);
		self.addOptionalParam(params, "user_country", user.country);
		self.addOptionalParam(params, "user_state", user.state);
		self.addOptionalParam(params, "user_city", user.city);
		self.addOptionalParam(params, "user_zip", user.zip);
		self.addOptionalParam(params, "user_urlList", user.urlList);
		self.addOptionalParam(params, "user_networkHighschool", user.networkHighschool);
		self.addOptionalParam(params, "user_networkCollege", user.networkCollege);
		self.addOptionalParam(params, "user_partnerData", user.partnerData);

		return self.hit("updateuser", kalturaSessionUser, params);

	def updateUserId(self, kalturaSessionUser, userId, newUserId):
		params = {}
		params["user_id"] = userId;
		params["new_user_id"] = newUserId;

		return self.hit("updateuserid", kalturaSessionUser, params);

	def upload(self, kalturaSessionUser, filename):
		params = {}
		params["filename"] = filename;

		return self.hit("upload", kalturaSessionUser, params);

	def uploadJpeg(self, kalturaSessionUser, filename, hash):
		params = {}
		params["filename"] = filename;
		params["hash"] = hash;

		return self.hit("uploadjpeg", kalturaSessionUser, params);

	def viewWidget(self, kalturaSessionUser, entryId = None, kshowId = None, widgetId = None, host = None):
		params = {}
		self.addOptionalParam(params, "entry_id", entryId);
		self.addOptionalParam(params, "kshow_id", kshowId);
		self.addOptionalParam(params, "widget_id", widgetId);
		self.addOptionalParam(params, "host", host);

		return self.hit("viewwidget", kalturaSessionUser, params);


