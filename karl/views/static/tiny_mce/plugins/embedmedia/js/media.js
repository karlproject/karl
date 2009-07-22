tinyMCEPopup.requireLangPack();

var oldWidth, oldHeight, ed, url;

/*
if (url = tinyMCEPopup.getParam("media_external_list_url"))
    document.write('<script language="javascript" type="text/javascript" src="' + tinyMCEPopup.editor.documentBaseURI.toAbsolute(url) + '"></script>');
*/


function init() {
    var pl = "", f, val;
    var type = "flash", fe, i;

    ed = tinyMCEPopup.editor;

    tinyMCEPopup.resizeToInnerSize();
    f = document.forms[0]

    fe = ed.selection.getNode();
    if (/mceItemFlash/.test(ed.dom.getAttrib(fe, 'class'))) {
        pl = fe.title;
    }


    //document.getElementById('bgcolor_pickcontainer').innerHTML = getColorPickerHTML('bgcolor_pick','bgcolor');

    //var html = getMediaListHTML('medialist','src','media','media');
    //if (html == "")
    //    document.getElementById("linklistrow").style.display = 'none';
    //else
    //    document.getElementById("linklistcontainer").innerHTML = html;

    // Resize some elements
    //if (isVisible('filebrowser'))
    //    document.getElementById('embed').style.width = '230px';

    /*
    // Setup form
    if (pl != "") {
        pl = tinyMCEPopup.editor.plugins.media._parse(pl);

                //setBool(pl, 'flash', 'play');
                //setBool(pl, 'flash', 'loop');
                //setBool(pl, 'flash', 'menu');
                //setBool(pl, 'flash', 'swliveconnect');
                //setStr(pl, 'flash', 'quality');
                //setStr(pl, 'flash', 'scale');
                //setStr(pl, 'flash', 'salign');
                //setStr(pl, 'flash', 'wmode');
                //setStr(pl, 'flash', 'base');
                //setStr(pl, 'flash', 'flashvars');

        setStr(pl, null, 'embed');
        setStr(pl, null, 'id');
        setStr(pl, null, 'name');
        //setStr(pl, null, 'vspace');
        //setStr(pl, null, 'hspace');
        //setStr(pl, null, 'bgcolor');
        //setStr(pl, null, 'align');
        setStr(pl, null, 'width');
        setStr(pl, null, 'height');

        if ((val = ed.dom.getAttrib(fe, "width")) != "")
            pl.width = f.width.value = val;

        if ((val = ed.dom.getAttrib(fe, "height")) != "")
            pl.height = f.height.value = val;

        oldWidth = pl.width ? parseInt(pl.width) : 0;
        oldHeight = pl.height ? parseInt(pl.height) : 0;
    } else
        oldWidth = oldHeight = 0;

    //selectByValue(f, 'media_type', type);
    ////changedType(type);
    //updateColor('bgcolor_pick', 'bgcolor');

    */

    TinyMCE_EditableSelects.init();
    generatePreview();
}

function insertMedia() {
    var fe, f = document.forms[0], h;

    tinyMCEPopup.restoreSelection();

    if (!AutoValidator.validate(f)) {
        tinyMCEPopup.alert(ed.getLang('invalid_data'));
        return false;
    }

    f.width.value = f.width.value == "" ? 100 : f.width.value;
    f.height.value = f.height.value == "" ? 100 : f.height.value;

    fe = ed.selection.getNode();

    var result = $('<img />')
        .attr('src', tinyMCEPopup.getWindowArg("plugin_url") + '/img/trans.gif')
        .attr('class', 'mceItemFlash')
        .attr('title', f.embed.value)
        .attr('width', f.width.value)
        .attr('height', f.height.value);
        //.attr('align', f.align.options[f.align.selectedIndex].value);
    h = $('<div />').append(result).html();
    /*
    h = f.embed.value; 
    */

	tinyMCEPopup.editor.selection.setContent(h, {source_view : true});


        //ed.execCommand('mceInsertContent', false, h);

    tinyMCEPopup.close();
}

function updatePreview() {
    var f = document.forms[0], type;

    f.width.value = f.width.value || '320';
    f.height.value = f.height.value || '240';

    generatePreview();
}

/*
function serializeParameters() {
    var d = document, f = d.forms[0], s = '';

    var encoded = $('<div />').append(content).html();
    var result = $('<img />').
    alert(s);
    //s = s.length > 0 ? s.substring(0, s.length - 1) : s;

    return s;
}
*/

function setBool(pl, p, n) {
    if (typeof(pl[n]) == "undefined")
        return;

    document.forms[0].elements[p + "_" + n].checked = pl[n] != 'false';
}

function setStr(pl, p, n) {
    var f = document.forms[0], e = f.elements[(p != null ? p + "_" : '') + n];

    if (typeof(pl[n]) == "undefined")
        return;

    if (e.type == "text")
        e.value = pl[n];
    else
        selectByValue(f, (p != null ? p + "_" : '') + n, pl[n]);
}

function getBool(p, n, d, tv, fv) {
    var v = document.forms[0].elements[p + "_" + n].checked;

    tv = typeof(tv) == 'undefined' ? 'true' : "'" + jsEncode(tv) + "'";
    fv = typeof(fv) == 'undefined' ? 'false' : "'" + jsEncode(fv) + "'";

    return (v == d) ? '' : n + (v ? ':' + tv + ',' : ":\'" + fv + "\',");
}

function getStr(p, n, d) {
    var e = document.forms[0].elements[(p != null ? p + "_" : "") + n];
    var v = e.value;

    return ((n == d || v == '') ? '' : n + ":'" + jsEncode(v) + "',");
}

function getInt(p, n, d) {
    var e = document.forms[0].elements[(p != null ? p + "_" : "") + n];
    var v = e.type == "text" ? e.value : e.options[e.selectedIndex].value;

    return ((n == d || v == '') ? '' : n + ":" + v.replace(/[^0-9]+/g, '') + ",");
}

function jsEncode(s) {
    s = s.replace(new RegExp('\\', 'g'), '\\\\');
    s = s.replace(new RegExp('"', 'g'), '\\"');
    s = s.replace(new RegExp("'", 'g'), "\\'");

    return s;
}

function generatePreview(c) {
    return;


    var f = document.forms[0], p = document.getElementById('prev'), h = '', cls, pl, n, type, codebase, wp, hp, nw, nh;

    p.innerHTML = '<!-- x --->';

    nw = parseInt(f.width.value);
    nh = parseInt(f.height.value);

    if (f.width.value != "" && f.height.value != "") {
        if (f.constrain.checked) {
            if (c == 'width' && oldWidth != 0) {
                wp = nw / oldWidth;
                nh = Math.round(wp * nh);
                f.height.value = nh;
            } else if (c == 'height' && oldHeight != 0) {
                hp = nh / oldHeight;
                nw = Math.round(hp * nw);
                f.width.value = nw;
            }
        }
    }

    if (f.width.value != "")
        oldWidth = nw;

    if (f.height.value != "")
        oldHeight = nh;

    // After constrain
    pl = serializeParameters();

    switch (f.media_type.options[f.media_type.selectedIndex].value) {
        case "flash":
            cls = 'clsid:D27CDB6E-AE6D-11cf-96B8-444553540000';
            codebase = 'http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0';
            type = 'application/x-shockwave-flash';
            break;

        case "shockwave":
            cls = 'clsid:166B1BCA-3F9C-11CF-8075-444553540000';
            codebase = 'http://download.macromedia.com/pub/shockwave/cabs/director/sw.cab#version=8,5,1,0';
            type = 'application/x-director';
            break;

        case "qt":
            cls = 'clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B';
            codebase = 'http://www.apple.com/qtactivex/qtplugin.cab#version=6,0,2,0';
            type = 'video/quicktime';
            break;

        case "wmp":
            cls = ed.getParam('media_wmp6_compatible') ? 'clsid:05589FA1-C356-11CE-BF01-00AA0055595A' : 'clsid:6BF52A52-394A-11D3-B153-00C04F79FAA6';
            codebase = 'http://activex.microsoft.com/activex/controls/mplayer/en/nsmp2inf.cab#Version=5,1,52,701';
            type = 'application/x-mplayer2';
            break;

        case "rmp":
            cls = 'clsid:CFCDAA03-8BE4-11cf-B84B-0020AFBBCCFA';
            codebase = 'http://activex.microsoft.com/activex/controls/mplayer/en/nsmp2inf.cab#Version=5,1,52,701';
            type = 'audio/x-pn-realaudio-plugin';
            break;
    }

    if (pl == '') {
        p.innerHTML = '';
        return;
    }

    pl = tinyMCEPopup.editor.plugins.media._parse(pl);

    if (!pl.src) {
        p.innerHTML = '';
        return;
    }

    pl.src = tinyMCEPopup.editor.documentBaseURI.toAbsolute(pl.src);
    pl.width = !pl.width ? 100 : pl.width;
    pl.height = !pl.height ? 100 : pl.height;
    pl.id = !pl.id ? 'obj' : pl.id;
    pl.name = !pl.name ? 'eobj' : pl.name;
    pl.align = !pl.align ? '' : pl.align;

    // Avoid annoying warning about insecure items
    if (!tinymce.isIE || document.location.protocol != 'https:') {
        h += '<object classid="' + cls + '" codebase="' + codebase + '" width="' + pl.width + '" height="' + pl.height + '" id="' + pl.id + '" name="' + pl.name + '" align="' + pl.align + '">';

        for (n in pl) {
            h += '<param name="' + n + '" value="' + pl[n] + '">';

            // Add extra url parameter if it's an absolute URL
            if (n == 'src' && pl[n].indexOf('://') != -1)
                h += '<param name="url" value="' + pl[n] + '" />';
        }
    }

    h += '<embed type="' + type + '" ';

    for (n in pl)
        h += n + '="' + pl[n] + '" ';

    h += '></embed>';

    // Avoid annoying warning about insecure items
    if (!tinymce.isIE || document.location.protocol != 'https:')
        h += '</object>';

    p.innerHTML = "<!-- x --->" + h;
}

tinyMCEPopup.onInit.add(init);
