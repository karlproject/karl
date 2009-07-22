tinyMCEPopup.requireLangPack();

var oldWidth, oldHeight, ed, url;

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

    tinyMCEPopup.editor.selection.setContent(h, {source_view : true});

    tinyMCEPopup.close();
}

function updatePreview() {
    var f = document.forms[0], type;

    f.width.value = f.width.value || '320';
    f.height.value = f.height.value || '240';

    generatePreview();
}

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
}

tinyMCEPopup.onInit.add(init);
