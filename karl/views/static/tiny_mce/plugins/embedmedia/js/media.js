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
        var snippet = new tinyMCEPopup.editor.plugins.embedmedia.EmbedSnippet();
        snippet.setContent(fe.title);
        snippet.setParms({
            width: ed.dom.getAttrib(fe, 'width'),
            height: ed.dom.getAttrib(fe, 'height')
        });
        pl = snippet.getContent();
    }

    // Setup form
    if (pl != "") {
        f.embed.value = pl;
    }

    TinyMCE_EditableSelects.init();

    // update the parameters and preview based on the embedded test
    changeEmbed();
}


function fetchSnippetFromForm() {
    // fetch snippet from the form
    var f = document.forms[0];
    var snippet = new tinyMCEPopup.editor.plugins.embedmedia.EmbedSnippet();
    snippet
        .setContent(f.embed.value);
        //.setParms({
        //    width: f.width.value || undefined,
        //    height: f.height.value || undefined
        //});
    return snippet;
};

function insertMedia() {
    var fe, f = document.forms[0], h;

    tinyMCEPopup.restoreSelection();

    if (!AutoValidator.validate(f)) {
        tinyMCEPopup.alert(ed.getLang('invalid_data'));
        return false;
    }

    // update snippet
    var snippet = fetchSnippetFromForm();
    var parms = snippet.getParms();

    f.width.value = parms.width;
    f.height.value = parms.height;

    fe = ed.selection.getNode();

    var result = $('<img />')
        .attr('src', tinyMCEPopup.getWindowArg("plugin_url") + '/img/trans.gif')
        .attr('class', 'mceItemFlash')
        .attr('title', snippet.getContent())
        .attr('width', parms.width)
        .attr('height', parms.height);
        //.attr('align', f.align.options[f.align.selectedIndex].value);
    h = $('<div />').append(result).html();

    tinyMCEPopup.editor.selection.setContent(h, {source_view : true});
    
    ed.execCommand('mceRepaint');
    
    tinyMCEPopup.close();
}

function changeEmbed() {
    var f = document.forms[0];
    // update snippet
    var snippet = new tinyMCEPopup.editor.plugins.embedmedia.EmbedSnippet();
    snippet.setContent(f.embed.value);
    var parms = snippet.getParms();
    f.width.value = parms.width || '';
    f.height.value = parms.height || '';
    // update preview
    generatePreview();
}

function changeDimension(dim) {
    var f = document.forms[0];
    // update snippet
    var snippet = new tinyMCEPopup.editor.plugins.embedmedia.EmbedSnippet();
    snippet.setContent(f.embed.value);
    var oldparms = snippet.getParms(); 
    oldparms.width = oldparms.width ? parseInt(oldparms.width) : 0;
    oldparms.height = oldparms.height ? parseInt(oldparms.height) : 0;
    var parms = {};
    parms[dim] = f[dim].value ? parseInt(f[dim].value) : 0;
    // Is ratio fixed?
    if (f.constrain.checked) {
        var otherdim = (dim == 'width') ? 'height' : 'width';
        if (oldparms.width && oldparms.height) {
            parms[otherdim] = f[otherdim].value = 
                Math.round((oldparms[otherdim] / oldparms[dim]) * parms[dim]);
        }
    }
    // set the parms on the snippet code 
    snippet.setParms(parms);
    f.embed.value = snippet.getContent();
    // update preview
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

function generatePreview() {
    var snippet = fetchSnippetFromForm();
    var dumdum = 'Y';
    $('#prev')
        .html(snippet.getContent())
        .css('width', parseInt(snippet.getParms().width) + 4)
        .css('height', parseInt(snippet.getParms().height) + 4);
}

tinyMCEPopup.onInit.add(init);
