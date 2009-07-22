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

    // update the parameters and preview based on the embedded test
    changeEmbed();
}


var EmbedSnippet = function EmbedSnippet() {};
$.extend(EmbedSnippet.prototype, {

    setContent: function(html) {
        this.wrapper = $('<div />');
        var wrapper = this.wrapper;
        wrapper.append(html);
        this.root = wrapper.children();
        var root = this.root;
        // detect type
        this.emtype = null;
        if (root.is('object')) {
            var inside = root.find('embed');
            if (inside) {
                this.emtype = 'object+embed';
                this.inside = inside;
            }
        }
        // cascade
        return this;
    },

    getContent: function() {
        return this.wrapper.html();
    },

    getParms: function() {
        return {
            width: this.root.attr('width'),
            height: this.root.attr('height')
        };
    },

    setParms: function(parms) {
        if (this.emtype == 'object+embed') {
            parms.width && this.root.attr('width', parms.width); 
            parms.height && this.root.attr('height', parms.height); 
            parms.width && this.inside.attr('width', parms.width); 
            parms.height && this.inside.attr('height', parms.height); 
        } else {
            parms.width && this.root.attr('width', parms.width); 
            parms.height && this.root.attr('height', parms.height); 
        }
        return this;
    }

});

function fetchSnippetFromForm() {
    // fetch snippet from the form
    var f = document.forms[0];
    var snippet = new EmbedSnippet();
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

    //var snippet = new EmbedSnippet();

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

    tinyMCEPopup.close();
}

function changeEmbed() {
    var f = document.forms[0];
    // update snippet
    var snippet = new EmbedSnippet();
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
    var snippet = new EmbedSnippet();
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
        .css('width', parseInt(snippet.getParms().width))
        .css('height', parseInt(snippet.getParms().height));
}

tinyMCEPopup.onInit.add(init);
