(function($){
    $.fn.kalturaEditableName = function(opts) {
        // support mutltiple elements
        if (this.length > 1){ 
            this.each(function() { 
                $(this).kalturaEditableName(opts) 
            }); 
            return this;
        }
        
        // private vars;
        var _currentContent;
        var _$inputBox;
        var _$wait;
        var self = this, $self = jQuery(this);
 
        // private function;
        var _onNameClick = function(args) {
            jQuery(self).unbind('click');
            
            _$wait = jQuery('<span>Saving...</span>');
            _$wait.hide();
            
            _$inputBox = jQuery('<input type="text">');
            _$inputBox.attr('name', options.name);
            _$inputBox.blur(_onInputBlur);
            _$inputBox.keypress(_onInputKeyPress);
            _currentContent = jQuery.trim(jQuery(this).text());
            _$inputBox.val(_currentContent);
            
            jQuery(self).empty().append(_$inputBox).append(_$wait);
            _$inputBox.focus();
        }
        
        var _onInputBlur = function(args) {
            _save();
        }

        var _onInputKeyPress = function(args) {
            if (args.keyCode == 13)
                _save();
            if (args.keyCode == 27)
                _finishEditing();
        }
        
        var _save = function() {
            if (_currentContent != _$inputBox.val()) // if changed
            {
                var params = {};
                params[options.namePostParam] = _$inputBox.val();
                params[options.idPostParam] = self.attr('id').replace(options.idPrefix, '');
                _$inputBox.hide();
                _$wait.show();
                jQuery.ajax({
                    url: options.url,
                    data: params,
                    type: 'POST',
                    success: _onSaveHandler
                });
            }
            else
            {
                _finishEditing();
            }
        }
        
        var _onSaveHandler = function() {
            _currentContent = _$inputBox.val();
            _finishEditing();
        }
        
        var _finishEditing = function() {
            jQuery(self).click(_onNameClick).empty().append(_currentContent);
        }
        
        // options
        var defaultOptions = { name: 'name' };  
        var options = $.extend({}, defaultOptions, opts);
 
        this.intialize = function() {
            this.click(_onNameClick);
            return $self;
        };  
 
        return this.intialize();
    }
    
    $.fn.kalturaPlayerSelector = function(opts) {
        var self = this;
        // options
        var defaultOptions = { 
                url: null,
                defaultId: null,
                swfBaseUrl: null,
                previewId: null,
                entryId: '_KMCLOGO',
                id: 'kplayer',
                width: 240,
                onSelect: null
        };  
        var options = $.extend({}, defaultOptions, opts);
        
        var _players = [];
        var _$playersList = jQuery(options.playersList);
        
        var _showLoader = function() {
            var swf = new SWFObject(Kaltura_PluginUrl + '/images/loader.swf', 'kloader', 35, 35, '9', '#000000');
            swf.addParam('wmode', 'transparent');
            swf.write(options.previewId);
            jQuery('#kloader').css('margin-top', '40px');
        }
        
        var _hideLoader = function() {
            jQuery('#kloader').remove();
        }
        
        var _getPlayer = function(uiConfId) {
            for(var i = 0; i < _players.length; i++) {
                if (_players[i].id == uiConfId)
                    return _players[i];
            };
        }
        
        var _onPlayersLoadedSuccess = function(data) {
            if (data && data.objects)
            {
                _players = data.objects;
                _$playersList.empty();
                jQuery.each(data.objects, function(index){
                    var player = data.objects[index];
                    var option = jQuery('<option>');
                    option.attr('value', player.id);
                    if (player.id == options.defaultId)
                        option.attr('selected', true);
                    option.text(player.name);
                    _$playersList.append(option);
                });
                _$playersList.change(_onPlayerChange);
                _onPlayerChange();
                _enableSubmit();
            }
        }
        
        var _onPlayersLoadedError = function() {
            _$playersList.empty();
            _$playersList.append('<option>Error loading players</option>');
            _hideLoader();
        }
        
        var _onPlayerChange = function(args) {
            var uiConfId = _$playersList.val();
            var player = _getPlayer(uiConfId);
            var swfUrl = options.swfBaseUrl;
            swfUrl += ('/uiconf_id/' + uiConfId);
            if (options.entryId)
                swfUrl += ('/entry_id/' + options.entryId);
            
            var height = _calculateHeight(player, options.width);
            var swf = new SWFObject(swfUrl, options.id, options.width, height, "9", "#000000");
            swf.addParam("flashVars", "");
            swf.addParam("wmode", "opaque");
            swf.addParam("allowScriptAccess", "always");
            swf.addParam("allowFullScreen", "true");
            swf.addParam("allowNetworking", "all");
            swf.write(options.previewId);
            
            if (typeof(options.onSelect) == "function")
                options.onSelect();
        }
        
        var _calculateHeight = function(player, width) {
            var ratio = jQuery(options.dimensions).filter(':checked').val();
            ratio = '4:3' // don't preview 16:9, the player doesn't look good in small size
            var spacer = player.height - (player.width / 4) * 3; // assume the width and height saved in kaltura is 4/3
            if (ratio == '16:9')
                var height = (width / 16) * 9 + spacer;
            else
                var height = (width / 4) * 3 + spacer;
            return parseInt(height);
        }
        
        var _disableSubmit = function() {
            jQuery(options.submit).attr('disabled', true);
        }
        
        var _enableSubmit = function() {
            jQuery(options.submit).removeAttr('disabled');
        }
 
        this.intialize = function() {
            _disableSubmit();
            _showLoader();
            _$playersList.append('<option>Loading...</option>');
            
            //jQuery(options.dimensions).click(_onPlayerChange);
            jQuery.ajax({
                url: options.url,
                cache: false,
                success: _onPlayersLoadedSuccess,
                error: _onPlayersLoadedError,
                dataType: 'json'
            });
            return self;
        };  
 
        return this.intialize();
    }
    
    $.fn.kalturaEntryStatusChecker = function(opts) {
        var self = this;
        var defaultOptions = { 
            url: null,
            idPrefix: null,
            idSelector: null,
            loader: null,
            interval: 20*1000 // every 20 seconds
        };  
        var options = $.extend({}, defaultOptions, opts);
        
        var _players = [];
        var _$playersList = jQuery(options.playersList);
        
        var _queueCheck = function () {
            if (self.find('li.statusConverting').size() > 0) {
                setTimeout(_checkStatuses, options.interval);
            }
        }
        
        var _checkStatuses = function() {
            if (options.loader)
                options.loader.show();
            
            var entryIds = [];
            self.find('li.statusConverting ' + options.idSelector).each(function(index, element) {
                var entryId = element.id.replace(options.idPrefix, '');
                entryIds.push(entryId);
            });
            
            jQuery.ajax({
                url: options.url,
                data: { 'entryIds[]': entryIds },
                dataType: 'json',
                cache: false,
                success: _checkStatusesSuccess,
                error: _checkStatusesError
            });
        }
        
        var _checkStatusesSuccess = function(data) {
            if (data) {
                jQuery.each(data, function(entryId, status) {
                    if (status == 2)
                    {
                        var $li = self.find('li #' + options.idPrefix + entryId).parent();
                        var $img = $li.find('img');
                        $img.show();
                        $img.attr('src', $img.attr('src') + "?" + new Date().getTime());
                        $li.attr('class', 'statusReady');
                    }
                    else if(status == -1 || status == -2 || status == 3)
                    {
                        self.find('li #' + options.idPrefix + entryId).parent().attr('class', 'statusError');
                    }
                });
            }
            _queueCheck();
            
            if (options.loader)
                options.loader.hide();
        }
        
        var _checkStatusesError = function() {
            _queueCheck();
            
            if (options.loader)
                options.loader.hide();
        }
 
        this.intialize = function() {
            var $li = self.find('li.statusConverting').parent();
            $li.each(function(index, element) {
                jQuery(element).find('img').hide();
            });
            _queueCheck();
            return self;
        };  
 
        return this.intialize();
    }
})(jQuery);
