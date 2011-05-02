/*!
 * jQuery JavaScript Library v1.4.4
 * http://jquery.com/
 *
 * Copyright 2010, John Resig
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * Includes Sizzle.js
 * http://sizzlejs.com/
 * Copyright 2010, The Dojo Foundation
 * Released under the MIT, BSD, and GPL Licenses.
 *
 * Date: Thu Nov 11 19:04:53 2010 -0500
 */
(function(E,B){function ka(a,b,d){if(d===B&&a.nodeType===1){d=a.getAttribute("data-"+b);if(typeof d==="string"){try{d=d==="true"?true:d==="false"?false:d==="null"?null:!c.isNaN(d)?parseFloat(d):Ja.test(d)?c.parseJSON(d):d}catch(e){}c.data(a,b,d)}else d=B}return d}function U(){return false}function ca(){return true}function la(a,b,d){d[0].type=a;return c.event.handle.apply(b,d)}function Ka(a){var b,d,e,f,h,l,k,o,x,r,A,C=[];f=[];h=c.data(this,this.nodeType?"events":"__events__");if(typeof h==="function")h=
h.events;if(!(a.liveFired===this||!h||!h.live||a.button&&a.type==="click")){if(a.namespace)A=RegExp("(^|\\.)"+a.namespace.split(".").join("\\.(?:.*\\.)?")+"(\\.|$)");a.liveFired=this;var J=h.live.slice(0);for(k=0;k<J.length;k++){h=J[k];h.origType.replace(X,"")===a.type?f.push(h.selector):J.splice(k--,1)}f=c(a.target).closest(f,a.currentTarget);o=0;for(x=f.length;o<x;o++){r=f[o];for(k=0;k<J.length;k++){h=J[k];if(r.selector===h.selector&&(!A||A.test(h.namespace))){l=r.elem;e=null;if(h.preType==="mouseenter"||
h.preType==="mouseleave"){a.type=h.preType;e=c(a.relatedTarget).closest(h.selector)[0]}if(!e||e!==l)C.push({elem:l,handleObj:h,level:r.level})}}}o=0;for(x=C.length;o<x;o++){f=C[o];if(d&&f.level>d)break;a.currentTarget=f.elem;a.data=f.handleObj.data;a.handleObj=f.handleObj;A=f.handleObj.origHandler.apply(f.elem,arguments);if(A===false||a.isPropagationStopped()){d=f.level;if(A===false)b=false;if(a.isImmediatePropagationStopped())break}}return b}}function Y(a,b){return(a&&a!=="*"?a+".":"")+b.replace(La,
"`").replace(Ma,"&")}function ma(a,b,d){if(c.isFunction(b))return c.grep(a,function(f,h){return!!b.call(f,h,f)===d});else if(b.nodeType)return c.grep(a,function(f){return f===b===d});else if(typeof b==="string"){var e=c.grep(a,function(f){return f.nodeType===1});if(Na.test(b))return c.filter(b,e,!d);else b=c.filter(b,e)}return c.grep(a,function(f){return c.inArray(f,b)>=0===d})}function na(a,b){var d=0;b.each(function(){if(this.nodeName===(a[d]&&a[d].nodeName)){var e=c.data(a[d++]),f=c.data(this,
e);if(e=e&&e.events){delete f.handle;f.events={};for(var h in e)for(var l in e[h])c.event.add(this,h,e[h][l],e[h][l].data)}}})}function Oa(a,b){b.src?c.ajax({url:b.src,async:false,dataType:"script"}):c.globalEval(b.text||b.textContent||b.innerHTML||"");b.parentNode&&b.parentNode.removeChild(b)}function oa(a,b,d){var e=b==="width"?a.offsetWidth:a.offsetHeight;if(d==="border")return e;c.each(b==="width"?Pa:Qa,function(){d||(e-=parseFloat(c.css(a,"padding"+this))||0);if(d==="margin")e+=parseFloat(c.css(a,
"margin"+this))||0;else e-=parseFloat(c.css(a,"border"+this+"Width"))||0});return e}function da(a,b,d,e){if(c.isArray(b)&&b.length)c.each(b,function(f,h){d||Ra.test(a)?e(a,h):da(a+"["+(typeof h==="object"||c.isArray(h)?f:"")+"]",h,d,e)});else if(!d&&b!=null&&typeof b==="object")c.isEmptyObject(b)?e(a,""):c.each(b,function(f,h){da(a+"["+f+"]",h,d,e)});else e(a,b)}function S(a,b){var d={};c.each(pa.concat.apply([],pa.slice(0,b)),function(){d[this]=a});return d}function qa(a){if(!ea[a]){var b=c("<"+
a+">").appendTo("body"),d=b.css("display");b.remove();if(d==="none"||d==="")d="block";ea[a]=d}return ea[a]}function fa(a){return c.isWindow(a)?a:a.nodeType===9?a.defaultView||a.parentWindow:false}var t=E.document,c=function(){function a(){if(!b.isReady){try{t.documentElement.doScroll("left")}catch(j){setTimeout(a,1);return}b.ready()}}var b=function(j,s){return new b.fn.init(j,s)},d=E.jQuery,e=E.$,f,h=/^(?:[^<]*(<[\w\W]+>)[^>]*$|#([\w\-]+)$)/,l=/\S/,k=/^\s+/,o=/\s+$/,x=/\W/,r=/\d/,A=/^<(\w+)\s*\/?>(?:<\/\1>)?$/,
C=/^[\],:{}\s]*$/,J=/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,w=/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,I=/(?:^|:|,)(?:\s*\[)+/g,L=/(webkit)[ \/]([\w.]+)/,g=/(opera)(?:.*version)?[ \/]([\w.]+)/,i=/(msie) ([\w.]+)/,n=/(mozilla)(?:.*? rv:([\w.]+))?/,m=navigator.userAgent,p=false,q=[],u,y=Object.prototype.toString,F=Object.prototype.hasOwnProperty,M=Array.prototype.push,N=Array.prototype.slice,O=String.prototype.trim,D=Array.prototype.indexOf,R={};b.fn=b.prototype={init:function(j,
s){var v,z,H;if(!j)return this;if(j.nodeType){this.context=this[0]=j;this.length=1;return this}if(j==="body"&&!s&&t.body){this.context=t;this[0]=t.body;this.selector="body";this.length=1;return this}if(typeof j==="string")if((v=h.exec(j))&&(v[1]||!s))if(v[1]){H=s?s.ownerDocument||s:t;if(z=A.exec(j))if(b.isPlainObject(s)){j=[t.createElement(z[1])];b.fn.attr.call(j,s,true)}else j=[H.createElement(z[1])];else{z=b.buildFragment([v[1]],[H]);j=(z.cacheable?z.fragment.cloneNode(true):z.fragment).childNodes}return b.merge(this,
j)}else{if((z=t.getElementById(v[2]))&&z.parentNode){if(z.id!==v[2])return f.find(j);this.length=1;this[0]=z}this.context=t;this.selector=j;return this}else if(!s&&!x.test(j)){this.selector=j;this.context=t;j=t.getElementsByTagName(j);return b.merge(this,j)}else return!s||s.jquery?(s||f).find(j):b(s).find(j);else if(b.isFunction(j))return f.ready(j);if(j.selector!==B){this.selector=j.selector;this.context=j.context}return b.makeArray(j,this)},selector:"",jquery:"1.4.4",length:0,size:function(){return this.length},
toArray:function(){return N.call(this,0)},get:function(j){return j==null?this.toArray():j<0?this.slice(j)[0]:this[j]},pushStack:function(j,s,v){var z=b();b.isArray(j)?M.apply(z,j):b.merge(z,j);z.prevObject=this;z.context=this.context;if(s==="find")z.selector=this.selector+(this.selector?" ":"")+v;else if(s)z.selector=this.selector+"."+s+"("+v+")";return z},each:function(j,s){return b.each(this,j,s)},ready:function(j){b.bindReady();if(b.isReady)j.call(t,b);else q&&q.push(j);return this},eq:function(j){return j===
-1?this.slice(j):this.slice(j,+j+1)},first:function(){return this.eq(0)},last:function(){return this.eq(-1)},slice:function(){return this.pushStack(N.apply(this,arguments),"slice",N.call(arguments).join(","))},map:function(j){return this.pushStack(b.map(this,function(s,v){return j.call(s,v,s)}))},end:function(){return this.prevObject||b(null)},push:M,sort:[].sort,splice:[].splice};b.fn.init.prototype=b.fn;b.extend=b.fn.extend=function(){var j,s,v,z,H,G=arguments[0]||{},K=1,Q=arguments.length,ga=false;
if(typeof G==="boolean"){ga=G;G=arguments[1]||{};K=2}if(typeof G!=="object"&&!b.isFunction(G))G={};if(Q===K){G=this;--K}for(;K<Q;K++)if((j=arguments[K])!=null)for(s in j){v=G[s];z=j[s];if(G!==z)if(ga&&z&&(b.isPlainObject(z)||(H=b.isArray(z)))){if(H){H=false;v=v&&b.isArray(v)?v:[]}else v=v&&b.isPlainObject(v)?v:{};G[s]=b.extend(ga,v,z)}else if(z!==B)G[s]=z}return G};b.extend({noConflict:function(j){E.$=e;if(j)E.jQuery=d;return b},isReady:false,readyWait:1,ready:function(j){j===true&&b.readyWait--;
if(!b.readyWait||j!==true&&!b.isReady){if(!t.body)return setTimeout(b.ready,1);b.isReady=true;if(!(j!==true&&--b.readyWait>0))if(q){var s=0,v=q;for(q=null;j=v[s++];)j.call(t,b);b.fn.trigger&&b(t).trigger("ready").unbind("ready")}}},bindReady:function(){if(!p){p=true;if(t.readyState==="complete")return setTimeout(b.ready,1);if(t.addEventListener){t.addEventListener("DOMContentLoaded",u,false);E.addEventListener("load",b.ready,false)}else if(t.attachEvent){t.attachEvent("onreadystatechange",u);E.attachEvent("onload",
b.ready);var j=false;try{j=E.frameElement==null}catch(s){}t.documentElement.doScroll&&j&&a()}}},isFunction:function(j){return b.type(j)==="function"},isArray:Array.isArray||function(j){return b.type(j)==="array"},isWindow:function(j){return j&&typeof j==="object"&&"setInterval"in j},isNaN:function(j){return j==null||!r.test(j)||isNaN(j)},type:function(j){return j==null?String(j):R[y.call(j)]||"object"},isPlainObject:function(j){if(!j||b.type(j)!=="object"||j.nodeType||b.isWindow(j))return false;if(j.constructor&&
!F.call(j,"constructor")&&!F.call(j.constructor.prototype,"isPrototypeOf"))return false;for(var s in j);return s===B||F.call(j,s)},isEmptyObject:function(j){for(var s in j)return false;return true},error:function(j){throw j;},parseJSON:function(j){if(typeof j!=="string"||!j)return null;j=b.trim(j);if(C.test(j.replace(J,"@").replace(w,"]").replace(I,"")))return E.JSON&&E.JSON.parse?E.JSON.parse(j):(new Function("return "+j))();else b.error("Invalid JSON: "+j)},noop:function(){},globalEval:function(j){if(j&&
l.test(j)){var s=t.getElementsByTagName("head")[0]||t.documentElement,v=t.createElement("script");v.type="text/javascript";if(b.support.scriptEval)v.appendChild(t.createTextNode(j));else v.text=j;s.insertBefore(v,s.firstChild);s.removeChild(v)}},nodeName:function(j,s){return j.nodeName&&j.nodeName.toUpperCase()===s.toUpperCase()},each:function(j,s,v){var z,H=0,G=j.length,K=G===B||b.isFunction(j);if(v)if(K)for(z in j){if(s.apply(j[z],v)===false)break}else for(;H<G;){if(s.apply(j[H++],v)===false)break}else if(K)for(z in j){if(s.call(j[z],
z,j[z])===false)break}else for(v=j[0];H<G&&s.call(v,H,v)!==false;v=j[++H]);return j},trim:O?function(j){return j==null?"":O.call(j)}:function(j){return j==null?"":j.toString().replace(k,"").replace(o,"")},makeArray:function(j,s){var v=s||[];if(j!=null){var z=b.type(j);j.length==null||z==="string"||z==="function"||z==="regexp"||b.isWindow(j)?M.call(v,j):b.merge(v,j)}return v},inArray:function(j,s){if(s.indexOf)return s.indexOf(j);for(var v=0,z=s.length;v<z;v++)if(s[v]===j)return v;return-1},merge:function(j,
s){var v=j.length,z=0;if(typeof s.length==="number")for(var H=s.length;z<H;z++)j[v++]=s[z];else for(;s[z]!==B;)j[v++]=s[z++];j.length=v;return j},grep:function(j,s,v){var z=[],H;v=!!v;for(var G=0,K=j.length;G<K;G++){H=!!s(j[G],G);v!==H&&z.push(j[G])}return z},map:function(j,s,v){for(var z=[],H,G=0,K=j.length;G<K;G++){H=s(j[G],G,v);if(H!=null)z[z.length]=H}return z.concat.apply([],z)},guid:1,proxy:function(j,s,v){if(arguments.length===2)if(typeof s==="string"){v=j;j=v[s];s=B}else if(s&&!b.isFunction(s)){v=
s;s=B}if(!s&&j)s=function(){return j.apply(v||this,arguments)};if(j)s.guid=j.guid=j.guid||s.guid||b.guid++;return s},access:function(j,s,v,z,H,G){var K=j.length;if(typeof s==="object"){for(var Q in s)b.access(j,Q,s[Q],z,H,v);return j}if(v!==B){z=!G&&z&&b.isFunction(v);for(Q=0;Q<K;Q++)H(j[Q],s,z?v.call(j[Q],Q,H(j[Q],s)):v,G);return j}return K?H(j[0],s):B},now:function(){return(new Date).getTime()},uaMatch:function(j){j=j.toLowerCase();j=L.exec(j)||g.exec(j)||i.exec(j)||j.indexOf("compatible")<0&&n.exec(j)||
[];return{browser:j[1]||"",version:j[2]||"0"}},browser:{}});b.each("Boolean Number String Function Array Date RegExp Object".split(" "),function(j,s){R["[object "+s+"]"]=s.toLowerCase()});m=b.uaMatch(m);if(m.browser){b.browser[m.browser]=true;b.browser.version=m.version}if(b.browser.webkit)b.browser.safari=true;if(D)b.inArray=function(j,s){return D.call(s,j)};if(!/\s/.test("\u00a0")){k=/^[\s\xA0]+/;o=/[\s\xA0]+$/}f=b(t);if(t.addEventListener)u=function(){t.removeEventListener("DOMContentLoaded",u,
false);b.ready()};else if(t.attachEvent)u=function(){if(t.readyState==="complete"){t.detachEvent("onreadystatechange",u);b.ready()}};return E.jQuery=E.$=b}();(function(){c.support={};var a=t.documentElement,b=t.createElement("script"),d=t.createElement("div"),e="script"+c.now();d.style.display="none";d.innerHTML="   <link/><table></table><a href='/a' style='color:red;float:left;opacity:.55;'>a</a><input type='checkbox'/>";var f=d.getElementsByTagName("*"),h=d.getElementsByTagName("a")[0],l=t.createElement("select"),
k=l.appendChild(t.createElement("option"));if(!(!f||!f.length||!h)){c.support={leadingWhitespace:d.firstChild.nodeType===3,tbody:!d.getElementsByTagName("tbody").length,htmlSerialize:!!d.getElementsByTagName("link").length,style:/red/.test(h.getAttribute("style")),hrefNormalized:h.getAttribute("href")==="/a",opacity:/^0.55$/.test(h.style.opacity),cssFloat:!!h.style.cssFloat,checkOn:d.getElementsByTagName("input")[0].value==="on",optSelected:k.selected,deleteExpando:true,optDisabled:false,checkClone:false,
scriptEval:false,noCloneEvent:true,boxModel:null,inlineBlockNeedsLayout:false,shrinkWrapBlocks:false,reliableHiddenOffsets:true};l.disabled=true;c.support.optDisabled=!k.disabled;b.type="text/javascript";try{b.appendChild(t.createTextNode("window."+e+"=1;"))}catch(o){}a.insertBefore(b,a.firstChild);if(E[e]){c.support.scriptEval=true;delete E[e]}try{delete b.test}catch(x){c.support.deleteExpando=false}a.removeChild(b);if(d.attachEvent&&d.fireEvent){d.attachEvent("onclick",function r(){c.support.noCloneEvent=
false;d.detachEvent("onclick",r)});d.cloneNode(true).fireEvent("onclick")}d=t.createElement("div");d.innerHTML="<input type='radio' name='radiotest' checked='checked'/>";a=t.createDocumentFragment();a.appendChild(d.firstChild);c.support.checkClone=a.cloneNode(true).cloneNode(true).lastChild.checked;c(function(){var r=t.createElement("div");r.style.width=r.style.paddingLeft="1px";t.body.appendChild(r);c.boxModel=c.support.boxModel=r.offsetWidth===2;if("zoom"in r.style){r.style.display="inline";r.style.zoom=
1;c.support.inlineBlockNeedsLayout=r.offsetWidth===2;r.style.display="";r.innerHTML="<div style='width:4px;'></div>";c.support.shrinkWrapBlocks=r.offsetWidth!==2}r.innerHTML="<table><tr><td style='padding:0;display:none'></td><td>t</td></tr></table>";var A=r.getElementsByTagName("td");c.support.reliableHiddenOffsets=A[0].offsetHeight===0;A[0].style.display="";A[1].style.display="none";c.support.reliableHiddenOffsets=c.support.reliableHiddenOffsets&&A[0].offsetHeight===0;r.innerHTML="";t.body.removeChild(r).style.display=
"none"});a=function(r){var A=t.createElement("div");r="on"+r;var C=r in A;if(!C){A.setAttribute(r,"return;");C=typeof A[r]==="function"}return C};c.support.submitBubbles=a("submit");c.support.changeBubbles=a("change");a=b=d=f=h=null}})();var ra={},Ja=/^(?:\{.*\}|\[.*\])$/;c.extend({cache:{},uuid:0,expando:"jQuery"+c.now(),noData:{embed:true,object:"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000",applet:true},data:function(a,b,d){if(c.acceptData(a)){a=a==E?ra:a;var e=a.nodeType,f=e?a[c.expando]:null,h=
c.cache;if(!(e&&!f&&typeof b==="string"&&d===B)){if(e)f||(a[c.expando]=f=++c.uuid);else h=a;if(typeof b==="object")if(e)h[f]=c.extend(h[f],b);else c.extend(h,b);else if(e&&!h[f])h[f]={};a=e?h[f]:h;if(d!==B)a[b]=d;return typeof b==="string"?a[b]:a}}},removeData:function(a,b){if(c.acceptData(a)){a=a==E?ra:a;var d=a.nodeType,e=d?a[c.expando]:a,f=c.cache,h=d?f[e]:e;if(b){if(h){delete h[b];d&&c.isEmptyObject(h)&&c.removeData(a)}}else if(d&&c.support.deleteExpando)delete a[c.expando];else if(a.removeAttribute)a.removeAttribute(c.expando);
else if(d)delete f[e];else for(var l in a)delete a[l]}},acceptData:function(a){if(a.nodeName){var b=c.noData[a.nodeName.toLowerCase()];if(b)return!(b===true||a.getAttribute("classid")!==b)}return true}});c.fn.extend({data:function(a,b){var d=null;if(typeof a==="undefined"){if(this.length){var e=this[0].attributes,f;d=c.data(this[0]);for(var h=0,l=e.length;h<l;h++){f=e[h].name;if(f.indexOf("data-")===0){f=f.substr(5);ka(this[0],f,d[f])}}}return d}else if(typeof a==="object")return this.each(function(){c.data(this,
a)});var k=a.split(".");k[1]=k[1]?"."+k[1]:"";if(b===B){d=this.triggerHandler("getData"+k[1]+"!",[k[0]]);if(d===B&&this.length){d=c.data(this[0],a);d=ka(this[0],a,d)}return d===B&&k[1]?this.data(k[0]):d}else return this.each(function(){var o=c(this),x=[k[0],b];o.triggerHandler("setData"+k[1]+"!",x);c.data(this,a,b);o.triggerHandler("changeData"+k[1]+"!",x)})},removeData:function(a){return this.each(function(){c.removeData(this,a)})}});c.extend({queue:function(a,b,d){if(a){b=(b||"fx")+"queue";var e=
c.data(a,b);if(!d)return e||[];if(!e||c.isArray(d))e=c.data(a,b,c.makeArray(d));else e.push(d);return e}},dequeue:function(a,b){b=b||"fx";var d=c.queue(a,b),e=d.shift();if(e==="inprogress")e=d.shift();if(e){b==="fx"&&d.unshift("inprogress");e.call(a,function(){c.dequeue(a,b)})}}});c.fn.extend({queue:function(a,b){if(typeof a!=="string"){b=a;a="fx"}if(b===B)return c.queue(this[0],a);return this.each(function(){var d=c.queue(this,a,b);a==="fx"&&d[0]!=="inprogress"&&c.dequeue(this,a)})},dequeue:function(a){return this.each(function(){c.dequeue(this,
a)})},delay:function(a,b){a=c.fx?c.fx.speeds[a]||a:a;b=b||"fx";return this.queue(b,function(){var d=this;setTimeout(function(){c.dequeue(d,b)},a)})},clearQueue:function(a){return this.queue(a||"fx",[])}});var sa=/[\n\t]/g,ha=/\s+/,Sa=/\r/g,Ta=/^(?:href|src|style)$/,Ua=/^(?:button|input)$/i,Va=/^(?:button|input|object|select|textarea)$/i,Wa=/^a(?:rea)?$/i,ta=/^(?:radio|checkbox)$/i;c.props={"for":"htmlFor","class":"className",readonly:"readOnly",maxlength:"maxLength",cellspacing:"cellSpacing",rowspan:"rowSpan",
colspan:"colSpan",tabindex:"tabIndex",usemap:"useMap",frameborder:"frameBorder"};c.fn.extend({attr:function(a,b){return c.access(this,a,b,true,c.attr)},removeAttr:function(a){return this.each(function(){c.attr(this,a,"");this.nodeType===1&&this.removeAttribute(a)})},addClass:function(a){if(c.isFunction(a))return this.each(function(x){var r=c(this);r.addClass(a.call(this,x,r.attr("class")))});if(a&&typeof a==="string")for(var b=(a||"").split(ha),d=0,e=this.length;d<e;d++){var f=this[d];if(f.nodeType===
1)if(f.className){for(var h=" "+f.className+" ",l=f.className,k=0,o=b.length;k<o;k++)if(h.indexOf(" "+b[k]+" ")<0)l+=" "+b[k];f.className=c.trim(l)}else f.className=a}return this},removeClass:function(a){if(c.isFunction(a))return this.each(function(o){var x=c(this);x.removeClass(a.call(this,o,x.attr("class")))});if(a&&typeof a==="string"||a===B)for(var b=(a||"").split(ha),d=0,e=this.length;d<e;d++){var f=this[d];if(f.nodeType===1&&f.className)if(a){for(var h=(" "+f.className+" ").replace(sa," "),
l=0,k=b.length;l<k;l++)h=h.replace(" "+b[l]+" "," ");f.className=c.trim(h)}else f.className=""}return this},toggleClass:function(a,b){var d=typeof a,e=typeof b==="boolean";if(c.isFunction(a))return this.each(function(f){var h=c(this);h.toggleClass(a.call(this,f,h.attr("class"),b),b)});return this.each(function(){if(d==="string")for(var f,h=0,l=c(this),k=b,o=a.split(ha);f=o[h++];){k=e?k:!l.hasClass(f);l[k?"addClass":"removeClass"](f)}else if(d==="undefined"||d==="boolean"){this.className&&c.data(this,
"__className__",this.className);this.className=this.className||a===false?"":c.data(this,"__className__")||""}})},hasClass:function(a){a=" "+a+" ";for(var b=0,d=this.length;b<d;b++)if((" "+this[b].className+" ").replace(sa," ").indexOf(a)>-1)return true;return false},val:function(a){if(!arguments.length){var b=this[0];if(b){if(c.nodeName(b,"option")){var d=b.attributes.value;return!d||d.specified?b.value:b.text}if(c.nodeName(b,"select")){var e=b.selectedIndex;d=[];var f=b.options;b=b.type==="select-one";
if(e<0)return null;var h=b?e:0;for(e=b?e+1:f.length;h<e;h++){var l=f[h];if(l.selected&&(c.support.optDisabled?!l.disabled:l.getAttribute("disabled")===null)&&(!l.parentNode.disabled||!c.nodeName(l.parentNode,"optgroup"))){a=c(l).val();if(b)return a;d.push(a)}}return d}if(ta.test(b.type)&&!c.support.checkOn)return b.getAttribute("value")===null?"on":b.value;return(b.value||"").replace(Sa,"")}return B}var k=c.isFunction(a);return this.each(function(o){var x=c(this),r=a;if(this.nodeType===1){if(k)r=
a.call(this,o,x.val());if(r==null)r="";else if(typeof r==="number")r+="";else if(c.isArray(r))r=c.map(r,function(C){return C==null?"":C+""});if(c.isArray(r)&&ta.test(this.type))this.checked=c.inArray(x.val(),r)>=0;else if(c.nodeName(this,"select")){var A=c.makeArray(r);c("option",this).each(function(){this.selected=c.inArray(c(this).val(),A)>=0});if(!A.length)this.selectedIndex=-1}else this.value=r}})}});c.extend({attrFn:{val:true,css:true,html:true,text:true,data:true,width:true,height:true,offset:true},
attr:function(a,b,d,e){if(!a||a.nodeType===3||a.nodeType===8)return B;if(e&&b in c.attrFn)return c(a)[b](d);e=a.nodeType!==1||!c.isXMLDoc(a);var f=d!==B;b=e&&c.props[b]||b;var h=Ta.test(b);if((b in a||a[b]!==B)&&e&&!h){if(f){b==="type"&&Ua.test(a.nodeName)&&a.parentNode&&c.error("type property can't be changed");if(d===null)a.nodeType===1&&a.removeAttribute(b);else a[b]=d}if(c.nodeName(a,"form")&&a.getAttributeNode(b))return a.getAttributeNode(b).nodeValue;if(b==="tabIndex")return(b=a.getAttributeNode("tabIndex"))&&
b.specified?b.value:Va.test(a.nodeName)||Wa.test(a.nodeName)&&a.href?0:B;return a[b]}if(!c.support.style&&e&&b==="style"){if(f)a.style.cssText=""+d;return a.style.cssText}f&&a.setAttribute(b,""+d);if(!a.attributes[b]&&a.hasAttribute&&!a.hasAttribute(b))return B;a=!c.support.hrefNormalized&&e&&h?a.getAttribute(b,2):a.getAttribute(b);return a===null?B:a}});var X=/\.(.*)$/,ia=/^(?:textarea|input|select)$/i,La=/\./g,Ma=/ /g,Xa=/[^\w\s.|`]/g,Ya=function(a){return a.replace(Xa,"\\$&")},ua={focusin:0,focusout:0};
c.event={add:function(a,b,d,e){if(!(a.nodeType===3||a.nodeType===8)){if(c.isWindow(a)&&a!==E&&!a.frameElement)a=E;if(d===false)d=U;else if(!d)return;var f,h;if(d.handler){f=d;d=f.handler}if(!d.guid)d.guid=c.guid++;if(h=c.data(a)){var l=a.nodeType?"events":"__events__",k=h[l],o=h.handle;if(typeof k==="function"){o=k.handle;k=k.events}else if(!k){a.nodeType||(h[l]=h=function(){});h.events=k={}}if(!o)h.handle=o=function(){return typeof c!=="undefined"&&!c.event.triggered?c.event.handle.apply(o.elem,
arguments):B};o.elem=a;b=b.split(" ");for(var x=0,r;l=b[x++];){h=f?c.extend({},f):{handler:d,data:e};if(l.indexOf(".")>-1){r=l.split(".");l=r.shift();h.namespace=r.slice(0).sort().join(".")}else{r=[];h.namespace=""}h.type=l;if(!h.guid)h.guid=d.guid;var A=k[l],C=c.event.special[l]||{};if(!A){A=k[l]=[];if(!C.setup||C.setup.call(a,e,r,o)===false)if(a.addEventListener)a.addEventListener(l,o,false);else a.attachEvent&&a.attachEvent("on"+l,o)}if(C.add){C.add.call(a,h);if(!h.handler.guid)h.handler.guid=
d.guid}A.push(h);c.event.global[l]=true}a=null}}},global:{},remove:function(a,b,d,e){if(!(a.nodeType===3||a.nodeType===8)){if(d===false)d=U;var f,h,l=0,k,o,x,r,A,C,J=a.nodeType?"events":"__events__",w=c.data(a),I=w&&w[J];if(w&&I){if(typeof I==="function"){w=I;I=I.events}if(b&&b.type){d=b.handler;b=b.type}if(!b||typeof b==="string"&&b.charAt(0)==="."){b=b||"";for(f in I)c.event.remove(a,f+b)}else{for(b=b.split(" ");f=b[l++];){r=f;k=f.indexOf(".")<0;o=[];if(!k){o=f.split(".");f=o.shift();x=RegExp("(^|\\.)"+
c.map(o.slice(0).sort(),Ya).join("\\.(?:.*\\.)?")+"(\\.|$)")}if(A=I[f])if(d){r=c.event.special[f]||{};for(h=e||0;h<A.length;h++){C=A[h];if(d.guid===C.guid){if(k||x.test(C.namespace)){e==null&&A.splice(h--,1);r.remove&&r.remove.call(a,C)}if(e!=null)break}}if(A.length===0||e!=null&&A.length===1){if(!r.teardown||r.teardown.call(a,o)===false)c.removeEvent(a,f,w.handle);delete I[f]}}else for(h=0;h<A.length;h++){C=A[h];if(k||x.test(C.namespace)){c.event.remove(a,r,C.handler,h);A.splice(h--,1)}}}if(c.isEmptyObject(I)){if(b=
w.handle)b.elem=null;delete w.events;delete w.handle;if(typeof w==="function")c.removeData(a,J);else c.isEmptyObject(w)&&c.removeData(a)}}}}},trigger:function(a,b,d,e){var f=a.type||a;if(!e){a=typeof a==="object"?a[c.expando]?a:c.extend(c.Event(f),a):c.Event(f);if(f.indexOf("!")>=0){a.type=f=f.slice(0,-1);a.exclusive=true}if(!d){a.stopPropagation();c.event.global[f]&&c.each(c.cache,function(){this.events&&this.events[f]&&c.event.trigger(a,b,this.handle.elem)})}if(!d||d.nodeType===3||d.nodeType===
8)return B;a.result=B;a.target=d;b=c.makeArray(b);b.unshift(a)}a.currentTarget=d;(e=d.nodeType?c.data(d,"handle"):(c.data(d,"__events__")||{}).handle)&&e.apply(d,b);e=d.parentNode||d.ownerDocument;try{if(!(d&&d.nodeName&&c.noData[d.nodeName.toLowerCase()]))if(d["on"+f]&&d["on"+f].apply(d,b)===false){a.result=false;a.preventDefault()}}catch(h){}if(!a.isPropagationStopped()&&e)c.event.trigger(a,b,e,true);else if(!a.isDefaultPrevented()){var l;e=a.target;var k=f.replace(X,""),o=c.nodeName(e,"a")&&k===
"click",x=c.event.special[k]||{};if((!x._default||x._default.call(d,a)===false)&&!o&&!(e&&e.nodeName&&c.noData[e.nodeName.toLowerCase()])){try{if(e[k]){if(l=e["on"+k])e["on"+k]=null;c.event.triggered=true;e[k]()}}catch(r){}if(l)e["on"+k]=l;c.event.triggered=false}}},handle:function(a){var b,d,e,f;d=[];var h=c.makeArray(arguments);a=h[0]=c.event.fix(a||E.event);a.currentTarget=this;b=a.type.indexOf(".")<0&&!a.exclusive;if(!b){e=a.type.split(".");a.type=e.shift();d=e.slice(0).sort();e=RegExp("(^|\\.)"+
d.join("\\.(?:.*\\.)?")+"(\\.|$)")}a.namespace=a.namespace||d.join(".");f=c.data(this,this.nodeType?"events":"__events__");if(typeof f==="function")f=f.events;d=(f||{})[a.type];if(f&&d){d=d.slice(0);f=0;for(var l=d.length;f<l;f++){var k=d[f];if(b||e.test(k.namespace)){a.handler=k.handler;a.data=k.data;a.handleObj=k;k=k.handler.apply(this,h);if(k!==B){a.result=k;if(k===false){a.preventDefault();a.stopPropagation()}}if(a.isImmediatePropagationStopped())break}}}return a.result},props:"altKey attrChange attrName bubbles button cancelable charCode clientX clientY ctrlKey currentTarget data detail eventPhase fromElement handler keyCode layerX layerY metaKey newValue offsetX offsetY pageX pageY prevValue relatedNode relatedTarget screenX screenY shiftKey srcElement target toElement view wheelDelta which".split(" "),
fix:function(a){if(a[c.expando])return a;var b=a;a=c.Event(b);for(var d=this.props.length,e;d;){e=this.props[--d];a[e]=b[e]}if(!a.target)a.target=a.srcElement||t;if(a.target.nodeType===3)a.target=a.target.parentNode;if(!a.relatedTarget&&a.fromElement)a.relatedTarget=a.fromElement===a.target?a.toElement:a.fromElement;if(a.pageX==null&&a.clientX!=null){b=t.documentElement;d=t.body;a.pageX=a.clientX+(b&&b.scrollLeft||d&&d.scrollLeft||0)-(b&&b.clientLeft||d&&d.clientLeft||0);a.pageY=a.clientY+(b&&b.scrollTop||
d&&d.scrollTop||0)-(b&&b.clientTop||d&&d.clientTop||0)}if(a.which==null&&(a.charCode!=null||a.keyCode!=null))a.which=a.charCode!=null?a.charCode:a.keyCode;if(!a.metaKey&&a.ctrlKey)a.metaKey=a.ctrlKey;if(!a.which&&a.button!==B)a.which=a.button&1?1:a.button&2?3:a.button&4?2:0;return a},guid:1E8,proxy:c.proxy,special:{ready:{setup:c.bindReady,teardown:c.noop},live:{add:function(a){c.event.add(this,Y(a.origType,a.selector),c.extend({},a,{handler:Ka,guid:a.handler.guid}))},remove:function(a){c.event.remove(this,
Y(a.origType,a.selector),a)}},beforeunload:{setup:function(a,b,d){if(c.isWindow(this))this.onbeforeunload=d},teardown:function(a,b){if(this.onbeforeunload===b)this.onbeforeunload=null}}}};c.removeEvent=t.removeEventListener?function(a,b,d){a.removeEventListener&&a.removeEventListener(b,d,false)}:function(a,b,d){a.detachEvent&&a.detachEvent("on"+b,d)};c.Event=function(a){if(!this.preventDefault)return new c.Event(a);if(a&&a.type){this.originalEvent=a;this.type=a.type}else this.type=a;this.timeStamp=
c.now();this[c.expando]=true};c.Event.prototype={preventDefault:function(){this.isDefaultPrevented=ca;var a=this.originalEvent;if(a)if(a.preventDefault)a.preventDefault();else a.returnValue=false},stopPropagation:function(){this.isPropagationStopped=ca;var a=this.originalEvent;if(a){a.stopPropagation&&a.stopPropagation();a.cancelBubble=true}},stopImmediatePropagation:function(){this.isImmediatePropagationStopped=ca;this.stopPropagation()},isDefaultPrevented:U,isPropagationStopped:U,isImmediatePropagationStopped:U};
var va=function(a){var b=a.relatedTarget;try{for(;b&&b!==this;)b=b.parentNode;if(b!==this){a.type=a.data;c.event.handle.apply(this,arguments)}}catch(d){}},wa=function(a){a.type=a.data;c.event.handle.apply(this,arguments)};c.each({mouseenter:"mouseover",mouseleave:"mouseout"},function(a,b){c.event.special[a]={setup:function(d){c.event.add(this,b,d&&d.selector?wa:va,a)},teardown:function(d){c.event.remove(this,b,d&&d.selector?wa:va)}}});if(!c.support.submitBubbles)c.event.special.submit={setup:function(){if(this.nodeName.toLowerCase()!==
"form"){c.event.add(this,"click.specialSubmit",function(a){var b=a.target,d=b.type;if((d==="submit"||d==="image")&&c(b).closest("form").length){a.liveFired=B;return la("submit",this,arguments)}});c.event.add(this,"keypress.specialSubmit",function(a){var b=a.target,d=b.type;if((d==="text"||d==="password")&&c(b).closest("form").length&&a.keyCode===13){a.liveFired=B;return la("submit",this,arguments)}})}else return false},teardown:function(){c.event.remove(this,".specialSubmit")}};if(!c.support.changeBubbles){var V,
xa=function(a){var b=a.type,d=a.value;if(b==="radio"||b==="checkbox")d=a.checked;else if(b==="select-multiple")d=a.selectedIndex>-1?c.map(a.options,function(e){return e.selected}).join("-"):"";else if(a.nodeName.toLowerCase()==="select")d=a.selectedIndex;return d},Z=function(a,b){var d=a.target,e,f;if(!(!ia.test(d.nodeName)||d.readOnly)){e=c.data(d,"_change_data");f=xa(d);if(a.type!=="focusout"||d.type!=="radio")c.data(d,"_change_data",f);if(!(e===B||f===e))if(e!=null||f){a.type="change";a.liveFired=
B;return c.event.trigger(a,b,d)}}};c.event.special.change={filters:{focusout:Z,beforedeactivate:Z,click:function(a){var b=a.target,d=b.type;if(d==="radio"||d==="checkbox"||b.nodeName.toLowerCase()==="select")return Z.call(this,a)},keydown:function(a){var b=a.target,d=b.type;if(a.keyCode===13&&b.nodeName.toLowerCase()!=="textarea"||a.keyCode===32&&(d==="checkbox"||d==="radio")||d==="select-multiple")return Z.call(this,a)},beforeactivate:function(a){a=a.target;c.data(a,"_change_data",xa(a))}},setup:function(){if(this.type===
"file")return false;for(var a in V)c.event.add(this,a+".specialChange",V[a]);return ia.test(this.nodeName)},teardown:function(){c.event.remove(this,".specialChange");return ia.test(this.nodeName)}};V=c.event.special.change.filters;V.focus=V.beforeactivate}t.addEventListener&&c.each({focus:"focusin",blur:"focusout"},function(a,b){function d(e){e=c.event.fix(e);e.type=b;return c.event.trigger(e,null,e.target)}c.event.special[b]={setup:function(){ua[b]++===0&&t.addEventListener(a,d,true)},teardown:function(){--ua[b]===
0&&t.removeEventListener(a,d,true)}}});c.each(["bind","one"],function(a,b){c.fn[b]=function(d,e,f){if(typeof d==="object"){for(var h in d)this[b](h,e,d[h],f);return this}if(c.isFunction(e)||e===false){f=e;e=B}var l=b==="one"?c.proxy(f,function(o){c(this).unbind(o,l);return f.apply(this,arguments)}):f;if(d==="unload"&&b!=="one")this.one(d,e,f);else{h=0;for(var k=this.length;h<k;h++)c.event.add(this[h],d,l,e)}return this}});c.fn.extend({unbind:function(a,b){if(typeof a==="object"&&!a.preventDefault)for(var d in a)this.unbind(d,
a[d]);else{d=0;for(var e=this.length;d<e;d++)c.event.remove(this[d],a,b)}return this},delegate:function(a,b,d,e){return this.live(b,d,e,a)},undelegate:function(a,b,d){return arguments.length===0?this.unbind("live"):this.die(b,null,d,a)},trigger:function(a,b){return this.each(function(){c.event.trigger(a,b,this)})},triggerHandler:function(a,b){if(this[0]){var d=c.Event(a);d.preventDefault();d.stopPropagation();c.event.trigger(d,b,this[0]);return d.result}},toggle:function(a){for(var b=arguments,d=
1;d<b.length;)c.proxy(a,b[d++]);return this.click(c.proxy(a,function(e){var f=(c.data(this,"lastToggle"+a.guid)||0)%d;c.data(this,"lastToggle"+a.guid,f+1);e.preventDefault();return b[f].apply(this,arguments)||false}))},hover:function(a,b){return this.mouseenter(a).mouseleave(b||a)}});var ya={focus:"focusin",blur:"focusout",mouseenter:"mouseover",mouseleave:"mouseout"};c.each(["live","die"],function(a,b){c.fn[b]=function(d,e,f,h){var l,k=0,o,x,r=h||this.selector;h=h?this:c(this.context);if(typeof d===
"object"&&!d.preventDefault){for(l in d)h[b](l,e,d[l],r);return this}if(c.isFunction(e)){f=e;e=B}for(d=(d||"").split(" ");(l=d[k++])!=null;){o=X.exec(l);x="";if(o){x=o[0];l=l.replace(X,"")}if(l==="hover")d.push("mouseenter"+x,"mouseleave"+x);else{o=l;if(l==="focus"||l==="blur"){d.push(ya[l]+x);l+=x}else l=(ya[l]||l)+x;if(b==="live"){x=0;for(var A=h.length;x<A;x++)c.event.add(h[x],"live."+Y(l,r),{data:e,selector:r,handler:f,origType:l,origHandler:f,preType:o})}else h.unbind("live."+Y(l,r),f)}}return this}});
c.each("blur focus focusin focusout load resize scroll unload click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select submit keydown keypress keyup error".split(" "),function(a,b){c.fn[b]=function(d,e){if(e==null){e=d;d=null}return arguments.length>0?this.bind(b,d,e):this.trigger(b)};if(c.attrFn)c.attrFn[b]=true});E.attachEvent&&!E.addEventListener&&c(E).bind("unload",function(){for(var a in c.cache)if(c.cache[a].handle)try{c.event.remove(c.cache[a].handle.elem)}catch(b){}});
(function(){function a(g,i,n,m,p,q){p=0;for(var u=m.length;p<u;p++){var y=m[p];if(y){var F=false;for(y=y[g];y;){if(y.sizcache===n){F=m[y.sizset];break}if(y.nodeType===1&&!q){y.sizcache=n;y.sizset=p}if(y.nodeName.toLowerCase()===i){F=y;break}y=y[g]}m[p]=F}}}function b(g,i,n,m,p,q){p=0;for(var u=m.length;p<u;p++){var y=m[p];if(y){var F=false;for(y=y[g];y;){if(y.sizcache===n){F=m[y.sizset];break}if(y.nodeType===1){if(!q){y.sizcache=n;y.sizset=p}if(typeof i!=="string"){if(y===i){F=true;break}}else if(k.filter(i,
[y]).length>0){F=y;break}}y=y[g]}m[p]=F}}}var d=/((?:\((?:\([^()]+\)|[^()]+)+\)|\[(?:\[[^\[\]]*\]|['"][^'"]*['"]|[^\[\]'"]+)+\]|\\.|[^ >+~,(\[\\]+)+|[>+~])(\s*,\s*)?((?:.|\r|\n)*)/g,e=0,f=Object.prototype.toString,h=false,l=true;[0,0].sort(function(){l=false;return 0});var k=function(g,i,n,m){n=n||[];var p=i=i||t;if(i.nodeType!==1&&i.nodeType!==9)return[];if(!g||typeof g!=="string")return n;var q,u,y,F,M,N=true,O=k.isXML(i),D=[],R=g;do{d.exec("");if(q=d.exec(R)){R=q[3];D.push(q[1]);if(q[2]){F=q[3];
break}}}while(q);if(D.length>1&&x.exec(g))if(D.length===2&&o.relative[D[0]])u=L(D[0]+D[1],i);else for(u=o.relative[D[0]]?[i]:k(D.shift(),i);D.length;){g=D.shift();if(o.relative[g])g+=D.shift();u=L(g,u)}else{if(!m&&D.length>1&&i.nodeType===9&&!O&&o.match.ID.test(D[0])&&!o.match.ID.test(D[D.length-1])){q=k.find(D.shift(),i,O);i=q.expr?k.filter(q.expr,q.set)[0]:q.set[0]}if(i){q=m?{expr:D.pop(),set:C(m)}:k.find(D.pop(),D.length===1&&(D[0]==="~"||D[0]==="+")&&i.parentNode?i.parentNode:i,O);u=q.expr?k.filter(q.expr,
q.set):q.set;if(D.length>0)y=C(u);else N=false;for(;D.length;){q=M=D.pop();if(o.relative[M])q=D.pop();else M="";if(q==null)q=i;o.relative[M](y,q,O)}}else y=[]}y||(y=u);y||k.error(M||g);if(f.call(y)==="[object Array]")if(N)if(i&&i.nodeType===1)for(g=0;y[g]!=null;g++){if(y[g]&&(y[g]===true||y[g].nodeType===1&&k.contains(i,y[g])))n.push(u[g])}else for(g=0;y[g]!=null;g++)y[g]&&y[g].nodeType===1&&n.push(u[g]);else n.push.apply(n,y);else C(y,n);if(F){k(F,p,n,m);k.uniqueSort(n)}return n};k.uniqueSort=function(g){if(w){h=
l;g.sort(w);if(h)for(var i=1;i<g.length;i++)g[i]===g[i-1]&&g.splice(i--,1)}return g};k.matches=function(g,i){return k(g,null,null,i)};k.matchesSelector=function(g,i){return k(i,null,null,[g]).length>0};k.find=function(g,i,n){var m;if(!g)return[];for(var p=0,q=o.order.length;p<q;p++){var u,y=o.order[p];if(u=o.leftMatch[y].exec(g)){var F=u[1];u.splice(1,1);if(F.substr(F.length-1)!=="\\"){u[1]=(u[1]||"").replace(/\\/g,"");m=o.find[y](u,i,n);if(m!=null){g=g.replace(o.match[y],"");break}}}}m||(m=i.getElementsByTagName("*"));
return{set:m,expr:g}};k.filter=function(g,i,n,m){for(var p,q,u=g,y=[],F=i,M=i&&i[0]&&k.isXML(i[0]);g&&i.length;){for(var N in o.filter)if((p=o.leftMatch[N].exec(g))!=null&&p[2]){var O,D,R=o.filter[N];D=p[1];q=false;p.splice(1,1);if(D.substr(D.length-1)!=="\\"){if(F===y)y=[];if(o.preFilter[N])if(p=o.preFilter[N](p,F,n,y,m,M)){if(p===true)continue}else q=O=true;if(p)for(var j=0;(D=F[j])!=null;j++)if(D){O=R(D,p,j,F);var s=m^!!O;if(n&&O!=null)if(s)q=true;else F[j]=false;else if(s){y.push(D);q=true}}if(O!==
B){n||(F=y);g=g.replace(o.match[N],"");if(!q)return[];break}}}if(g===u)if(q==null)k.error(g);else break;u=g}return F};k.error=function(g){throw"Syntax error, unrecognized expression: "+g;};var o=k.selectors={order:["ID","NAME","TAG"],match:{ID:/#((?:[\w\u00c0-\uFFFF\-]|\\.)+)/,CLASS:/\.((?:[\w\u00c0-\uFFFF\-]|\\.)+)/,NAME:/\[name=['"]*((?:[\w\u00c0-\uFFFF\-]|\\.)+)['"]*\]/,ATTR:/\[\s*((?:[\w\u00c0-\uFFFF\-]|\\.)+)\s*(?:(\S?=)\s*(['"]*)(.*?)\3|)\s*\]/,TAG:/^((?:[\w\u00c0-\uFFFF\*\-]|\\.)+)/,CHILD:/:(only|nth|last|first)-child(?:\((even|odd|[\dn+\-]*)\))?/,
POS:/:(nth|eq|gt|lt|first|last|even|odd)(?:\((\d*)\))?(?=[^\-]|$)/,PSEUDO:/:((?:[\w\u00c0-\uFFFF\-]|\\.)+)(?:\((['"]?)((?:\([^\)]+\)|[^\(\)]*)+)\2\))?/},leftMatch:{},attrMap:{"class":"className","for":"htmlFor"},attrHandle:{href:function(g){return g.getAttribute("href")}},relative:{"+":function(g,i){var n=typeof i==="string",m=n&&!/\W/.test(i);n=n&&!m;if(m)i=i.toLowerCase();m=0;for(var p=g.length,q;m<p;m++)if(q=g[m]){for(;(q=q.previousSibling)&&q.nodeType!==1;);g[m]=n||q&&q.nodeName.toLowerCase()===
i?q||false:q===i}n&&k.filter(i,g,true)},">":function(g,i){var n,m=typeof i==="string",p=0,q=g.length;if(m&&!/\W/.test(i))for(i=i.toLowerCase();p<q;p++){if(n=g[p]){n=n.parentNode;g[p]=n.nodeName.toLowerCase()===i?n:false}}else{for(;p<q;p++)if(n=g[p])g[p]=m?n.parentNode:n.parentNode===i;m&&k.filter(i,g,true)}},"":function(g,i,n){var m,p=e++,q=b;if(typeof i==="string"&&!/\W/.test(i)){m=i=i.toLowerCase();q=a}q("parentNode",i,p,g,m,n)},"~":function(g,i,n){var m,p=e++,q=b;if(typeof i==="string"&&!/\W/.test(i)){m=
i=i.toLowerCase();q=a}q("previousSibling",i,p,g,m,n)}},find:{ID:function(g,i,n){if(typeof i.getElementById!=="undefined"&&!n)return(g=i.getElementById(g[1]))&&g.parentNode?[g]:[]},NAME:function(g,i){if(typeof i.getElementsByName!=="undefined"){for(var n=[],m=i.getElementsByName(g[1]),p=0,q=m.length;p<q;p++)m[p].getAttribute("name")===g[1]&&n.push(m[p]);return n.length===0?null:n}},TAG:function(g,i){return i.getElementsByTagName(g[1])}},preFilter:{CLASS:function(g,i,n,m,p,q){g=" "+g[1].replace(/\\/g,
"")+" ";if(q)return g;q=0;for(var u;(u=i[q])!=null;q++)if(u)if(p^(u.className&&(" "+u.className+" ").replace(/[\t\n]/g," ").indexOf(g)>=0))n||m.push(u);else if(n)i[q]=false;return false},ID:function(g){return g[1].replace(/\\/g,"")},TAG:function(g){return g[1].toLowerCase()},CHILD:function(g){if(g[1]==="nth"){var i=/(-?)(\d*)n((?:\+|-)?\d*)/.exec(g[2]==="even"&&"2n"||g[2]==="odd"&&"2n+1"||!/\D/.test(g[2])&&"0n+"+g[2]||g[2]);g[2]=i[1]+(i[2]||1)-0;g[3]=i[3]-0}g[0]=e++;return g},ATTR:function(g,i,n,
m,p,q){i=g[1].replace(/\\/g,"");if(!q&&o.attrMap[i])g[1]=o.attrMap[i];if(g[2]==="~=")g[4]=" "+g[4]+" ";return g},PSEUDO:function(g,i,n,m,p){if(g[1]==="not")if((d.exec(g[3])||"").length>1||/^\w/.test(g[3]))g[3]=k(g[3],null,null,i);else{g=k.filter(g[3],i,n,true^p);n||m.push.apply(m,g);return false}else if(o.match.POS.test(g[0])||o.match.CHILD.test(g[0]))return true;return g},POS:function(g){g.unshift(true);return g}},filters:{enabled:function(g){return g.disabled===false&&g.type!=="hidden"},disabled:function(g){return g.disabled===
true},checked:function(g){return g.checked===true},selected:function(g){return g.selected===true},parent:function(g){return!!g.firstChild},empty:function(g){return!g.firstChild},has:function(g,i,n){return!!k(n[3],g).length},header:function(g){return/h\d/i.test(g.nodeName)},text:function(g){return"text"===g.type},radio:function(g){return"radio"===g.type},checkbox:function(g){return"checkbox"===g.type},file:function(g){return"file"===g.type},password:function(g){return"password"===g.type},submit:function(g){return"submit"===
g.type},image:function(g){return"image"===g.type},reset:function(g){return"reset"===g.type},button:function(g){return"button"===g.type||g.nodeName.toLowerCase()==="button"},input:function(g){return/input|select|textarea|button/i.test(g.nodeName)}},setFilters:{first:function(g,i){return i===0},last:function(g,i,n,m){return i===m.length-1},even:function(g,i){return i%2===0},odd:function(g,i){return i%2===1},lt:function(g,i,n){return i<n[3]-0},gt:function(g,i,n){return i>n[3]-0},nth:function(g,i,n){return n[3]-
0===i},eq:function(g,i,n){return n[3]-0===i}},filter:{PSEUDO:function(g,i,n,m){var p=i[1],q=o.filters[p];if(q)return q(g,n,i,m);else if(p==="contains")return(g.textContent||g.innerText||k.getText([g])||"").indexOf(i[3])>=0;else if(p==="not"){i=i[3];n=0;for(m=i.length;n<m;n++)if(i[n]===g)return false;return true}else k.error("Syntax error, unrecognized expression: "+p)},CHILD:function(g,i){var n=i[1],m=g;switch(n){case "only":case "first":for(;m=m.previousSibling;)if(m.nodeType===1)return false;if(n===
"first")return true;m=g;case "last":for(;m=m.nextSibling;)if(m.nodeType===1)return false;return true;case "nth":n=i[2];var p=i[3];if(n===1&&p===0)return true;var q=i[0],u=g.parentNode;if(u&&(u.sizcache!==q||!g.nodeIndex)){var y=0;for(m=u.firstChild;m;m=m.nextSibling)if(m.nodeType===1)m.nodeIndex=++y;u.sizcache=q}m=g.nodeIndex-p;return n===0?m===0:m%n===0&&m/n>=0}},ID:function(g,i){return g.nodeType===1&&g.getAttribute("id")===i},TAG:function(g,i){return i==="*"&&g.nodeType===1||g.nodeName.toLowerCase()===
i},CLASS:function(g,i){return(" "+(g.className||g.getAttribute("class"))+" ").indexOf(i)>-1},ATTR:function(g,i){var n=i[1];n=o.attrHandle[n]?o.attrHandle[n](g):g[n]!=null?g[n]:g.getAttribute(n);var m=n+"",p=i[2],q=i[4];return n==null?p==="!=":p==="="?m===q:p==="*="?m.indexOf(q)>=0:p==="~="?(" "+m+" ").indexOf(q)>=0:!q?m&&n!==false:p==="!="?m!==q:p==="^="?m.indexOf(q)===0:p==="$="?m.substr(m.length-q.length)===q:p==="|="?m===q||m.substr(0,q.length+1)===q+"-":false},POS:function(g,i,n,m){var p=o.setFilters[i[2]];
if(p)return p(g,n,i,m)}}},x=o.match.POS,r=function(g,i){return"\\"+(i-0+1)},A;for(A in o.match){o.match[A]=RegExp(o.match[A].source+/(?![^\[]*\])(?![^\(]*\))/.source);o.leftMatch[A]=RegExp(/(^(?:.|\r|\n)*?)/.source+o.match[A].source.replace(/\\(\d+)/g,r))}var C=function(g,i){g=Array.prototype.slice.call(g,0);if(i){i.push.apply(i,g);return i}return g};try{Array.prototype.slice.call(t.documentElement.childNodes,0)}catch(J){C=function(g,i){var n=0,m=i||[];if(f.call(g)==="[object Array]")Array.prototype.push.apply(m,
g);else if(typeof g.length==="number")for(var p=g.length;n<p;n++)m.push(g[n]);else for(;g[n];n++)m.push(g[n]);return m}}var w,I;if(t.documentElement.compareDocumentPosition)w=function(g,i){if(g===i){h=true;return 0}if(!g.compareDocumentPosition||!i.compareDocumentPosition)return g.compareDocumentPosition?-1:1;return g.compareDocumentPosition(i)&4?-1:1};else{w=function(g,i){var n,m,p=[],q=[];n=g.parentNode;m=i.parentNode;var u=n;if(g===i){h=true;return 0}else if(n===m)return I(g,i);else if(n){if(!m)return 1}else return-1;
for(;u;){p.unshift(u);u=u.parentNode}for(u=m;u;){q.unshift(u);u=u.parentNode}n=p.length;m=q.length;for(u=0;u<n&&u<m;u++)if(p[u]!==q[u])return I(p[u],q[u]);return u===n?I(g,q[u],-1):I(p[u],i,1)};I=function(g,i,n){if(g===i)return n;for(g=g.nextSibling;g;){if(g===i)return-1;g=g.nextSibling}return 1}}k.getText=function(g){for(var i="",n,m=0;g[m];m++){n=g[m];if(n.nodeType===3||n.nodeType===4)i+=n.nodeValue;else if(n.nodeType!==8)i+=k.getText(n.childNodes)}return i};(function(){var g=t.createElement("div"),
i="script"+(new Date).getTime(),n=t.documentElement;g.innerHTML="<a name='"+i+"'/>";n.insertBefore(g,n.firstChild);if(t.getElementById(i)){o.find.ID=function(m,p,q){if(typeof p.getElementById!=="undefined"&&!q)return(p=p.getElementById(m[1]))?p.id===m[1]||typeof p.getAttributeNode!=="undefined"&&p.getAttributeNode("id").nodeValue===m[1]?[p]:B:[]};o.filter.ID=function(m,p){var q=typeof m.getAttributeNode!=="undefined"&&m.getAttributeNode("id");return m.nodeType===1&&q&&q.nodeValue===p}}n.removeChild(g);
n=g=null})();(function(){var g=t.createElement("div");g.appendChild(t.createComment(""));if(g.getElementsByTagName("*").length>0)o.find.TAG=function(i,n){var m=n.getElementsByTagName(i[1]);if(i[1]==="*"){for(var p=[],q=0;m[q];q++)m[q].nodeType===1&&p.push(m[q]);m=p}return m};g.innerHTML="<a href='#'></a>";if(g.firstChild&&typeof g.firstChild.getAttribute!=="undefined"&&g.firstChild.getAttribute("href")!=="#")o.attrHandle.href=function(i){return i.getAttribute("href",2)};g=null})();t.querySelectorAll&&
function(){var g=k,i=t.createElement("div");i.innerHTML="<p class='TEST'></p>";if(!(i.querySelectorAll&&i.querySelectorAll(".TEST").length===0)){k=function(m,p,q,u){p=p||t;m=m.replace(/\=\s*([^'"\]]*)\s*\]/g,"='$1']");if(!u&&!k.isXML(p))if(p.nodeType===9)try{return C(p.querySelectorAll(m),q)}catch(y){}else if(p.nodeType===1&&p.nodeName.toLowerCase()!=="object"){var F=p.getAttribute("id"),M=F||"__sizzle__";F||p.setAttribute("id",M);try{return C(p.querySelectorAll("#"+M+" "+m),q)}catch(N){}finally{F||
p.removeAttribute("id")}}return g(m,p,q,u)};for(var n in g)k[n]=g[n];i=null}}();(function(){var g=t.documentElement,i=g.matchesSelector||g.mozMatchesSelector||g.webkitMatchesSelector||g.msMatchesSelector,n=false;try{i.call(t.documentElement,"[test!='']:sizzle")}catch(m){n=true}if(i)k.matchesSelector=function(p,q){q=q.replace(/\=\s*([^'"\]]*)\s*\]/g,"='$1']");if(!k.isXML(p))try{if(n||!o.match.PSEUDO.test(q)&&!/!=/.test(q))return i.call(p,q)}catch(u){}return k(q,null,null,[p]).length>0}})();(function(){var g=
t.createElement("div");g.innerHTML="<div class='test e'></div><div class='test'></div>";if(!(!g.getElementsByClassName||g.getElementsByClassName("e").length===0)){g.lastChild.className="e";if(g.getElementsByClassName("e").length!==1){o.order.splice(1,0,"CLASS");o.find.CLASS=function(i,n,m){if(typeof n.getElementsByClassName!=="undefined"&&!m)return n.getElementsByClassName(i[1])};g=null}}})();k.contains=t.documentElement.contains?function(g,i){return g!==i&&(g.contains?g.contains(i):true)}:t.documentElement.compareDocumentPosition?
function(g,i){return!!(g.compareDocumentPosition(i)&16)}:function(){return false};k.isXML=function(g){return(g=(g?g.ownerDocument||g:0).documentElement)?g.nodeName!=="HTML":false};var L=function(g,i){for(var n,m=[],p="",q=i.nodeType?[i]:i;n=o.match.PSEUDO.exec(g);){p+=n[0];g=g.replace(o.match.PSEUDO,"")}g=o.relative[g]?g+"*":g;n=0;for(var u=q.length;n<u;n++)k(g,q[n],m);return k.filter(p,m)};c.find=k;c.expr=k.selectors;c.expr[":"]=c.expr.filters;c.unique=k.uniqueSort;c.text=k.getText;c.isXMLDoc=k.isXML;
c.contains=k.contains})();var Za=/Until$/,$a=/^(?:parents|prevUntil|prevAll)/,ab=/,/,Na=/^.[^:#\[\.,]*$/,bb=Array.prototype.slice,cb=c.expr.match.POS;c.fn.extend({find:function(a){for(var b=this.pushStack("","find",a),d=0,e=0,f=this.length;e<f;e++){d=b.length;c.find(a,this[e],b);if(e>0)for(var h=d;h<b.length;h++)for(var l=0;l<d;l++)if(b[l]===b[h]){b.splice(h--,1);break}}return b},has:function(a){var b=c(a);return this.filter(function(){for(var d=0,e=b.length;d<e;d++)if(c.contains(this,b[d]))return true})},
not:function(a){return this.pushStack(ma(this,a,false),"not",a)},filter:function(a){return this.pushStack(ma(this,a,true),"filter",a)},is:function(a){return!!a&&c.filter(a,this).length>0},closest:function(a,b){var d=[],e,f,h=this[0];if(c.isArray(a)){var l,k={},o=1;if(h&&a.length){e=0;for(f=a.length;e<f;e++){l=a[e];k[l]||(k[l]=c.expr.match.POS.test(l)?c(l,b||this.context):l)}for(;h&&h.ownerDocument&&h!==b;){for(l in k){e=k[l];if(e.jquery?e.index(h)>-1:c(h).is(e))d.push({selector:l,elem:h,level:o})}h=
h.parentNode;o++}}return d}l=cb.test(a)?c(a,b||this.context):null;e=0;for(f=this.length;e<f;e++)for(h=this[e];h;)if(l?l.index(h)>-1:c.find.matchesSelector(h,a)){d.push(h);break}else{h=h.parentNode;if(!h||!h.ownerDocument||h===b)break}d=d.length>1?c.unique(d):d;return this.pushStack(d,"closest",a)},index:function(a){if(!a||typeof a==="string")return c.inArray(this[0],a?c(a):this.parent().children());return c.inArray(a.jquery?a[0]:a,this)},add:function(a,b){var d=typeof a==="string"?c(a,b||this.context):
c.makeArray(a),e=c.merge(this.get(),d);return this.pushStack(!d[0]||!d[0].parentNode||d[0].parentNode.nodeType===11||!e[0]||!e[0].parentNode||e[0].parentNode.nodeType===11?e:c.unique(e))},andSelf:function(){return this.add(this.prevObject)}});c.each({parent:function(a){return(a=a.parentNode)&&a.nodeType!==11?a:null},parents:function(a){return c.dir(a,"parentNode")},parentsUntil:function(a,b,d){return c.dir(a,"parentNode",d)},next:function(a){return c.nth(a,2,"nextSibling")},prev:function(a){return c.nth(a,
2,"previousSibling")},nextAll:function(a){return c.dir(a,"nextSibling")},prevAll:function(a){return c.dir(a,"previousSibling")},nextUntil:function(a,b,d){return c.dir(a,"nextSibling",d)},prevUntil:function(a,b,d){return c.dir(a,"previousSibling",d)},siblings:function(a){return c.sibling(a.parentNode.firstChild,a)},children:function(a){return c.sibling(a.firstChild)},contents:function(a){return c.nodeName(a,"iframe")?a.contentDocument||a.contentWindow.document:c.makeArray(a.childNodes)}},function(a,
b){c.fn[a]=function(d,e){var f=c.map(this,b,d);Za.test(a)||(e=d);if(e&&typeof e==="string")f=c.filter(e,f);f=this.length>1?c.unique(f):f;if((this.length>1||ab.test(e))&&$a.test(a))f=f.reverse();return this.pushStack(f,a,bb.call(arguments).join(","))}});c.extend({filter:function(a,b,d){if(d)a=":not("+a+")";return b.length===1?c.find.matchesSelector(b[0],a)?[b[0]]:[]:c.find.matches(a,b)},dir:function(a,b,d){var e=[];for(a=a[b];a&&a.nodeType!==9&&(d===B||a.nodeType!==1||!c(a).is(d));){a.nodeType===1&&
e.push(a);a=a[b]}return e},nth:function(a,b,d){b=b||1;for(var e=0;a;a=a[d])if(a.nodeType===1&&++e===b)break;return a},sibling:function(a,b){for(var d=[];a;a=a.nextSibling)a.nodeType===1&&a!==b&&d.push(a);return d}});var za=/ jQuery\d+="(?:\d+|null)"/g,$=/^\s+/,Aa=/<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:]+)[^>]*)\/>/ig,Ba=/<([\w:]+)/,db=/<tbody/i,eb=/<|&#?\w+;/,Ca=/<(?:script|object|embed|option|style)/i,Da=/checked\s*(?:[^=]|=\s*.checked.)/i,fb=/\=([^="'>\s]+\/)>/g,P={option:[1,
"<select multiple='multiple'>","</select>"],legend:[1,"<fieldset>","</fieldset>"],thead:[1,"<table>","</table>"],tr:[2,"<table><tbody>","</tbody></table>"],td:[3,"<table><tbody><tr>","</tr></tbody></table>"],col:[2,"<table><tbody></tbody><colgroup>","</colgroup></table>"],area:[1,"<map>","</map>"],_default:[0,"",""]};P.optgroup=P.option;P.tbody=P.tfoot=P.colgroup=P.caption=P.thead;P.th=P.td;if(!c.support.htmlSerialize)P._default=[1,"div<div>","</div>"];c.fn.extend({text:function(a){if(c.isFunction(a))return this.each(function(b){var d=
c(this);d.text(a.call(this,b,d.text()))});if(typeof a!=="object"&&a!==B)return this.empty().append((this[0]&&this[0].ownerDocument||t).createTextNode(a));return c.text(this)},wrapAll:function(a){if(c.isFunction(a))return this.each(function(d){c(this).wrapAll(a.call(this,d))});if(this[0]){var b=c(a,this[0].ownerDocument).eq(0).clone(true);this[0].parentNode&&b.insertBefore(this[0]);b.map(function(){for(var d=this;d.firstChild&&d.firstChild.nodeType===1;)d=d.firstChild;return d}).append(this)}return this},
wrapInner:function(a){if(c.isFunction(a))return this.each(function(b){c(this).wrapInner(a.call(this,b))});return this.each(function(){var b=c(this),d=b.contents();d.length?d.wrapAll(a):b.append(a)})},wrap:function(a){return this.each(function(){c(this).wrapAll(a)})},unwrap:function(){return this.parent().each(function(){c.nodeName(this,"body")||c(this).replaceWith(this.childNodes)}).end()},append:function(){return this.domManip(arguments,true,function(a){this.nodeType===1&&this.appendChild(a)})},
prepend:function(){return this.domManip(arguments,true,function(a){this.nodeType===1&&this.insertBefore(a,this.firstChild)})},before:function(){if(this[0]&&this[0].parentNode)return this.domManip(arguments,false,function(b){this.parentNode.insertBefore(b,this)});else if(arguments.length){var a=c(arguments[0]);a.push.apply(a,this.toArray());return this.pushStack(a,"before",arguments)}},after:function(){if(this[0]&&this[0].parentNode)return this.domManip(arguments,false,function(b){this.parentNode.insertBefore(b,
this.nextSibling)});else if(arguments.length){var a=this.pushStack(this,"after",arguments);a.push.apply(a,c(arguments[0]).toArray());return a}},remove:function(a,b){for(var d=0,e;(e=this[d])!=null;d++)if(!a||c.filter(a,[e]).length){if(!b&&e.nodeType===1){c.cleanData(e.getElementsByTagName("*"));c.cleanData([e])}e.parentNode&&e.parentNode.removeChild(e)}return this},empty:function(){for(var a=0,b;(b=this[a])!=null;a++)for(b.nodeType===1&&c.cleanData(b.getElementsByTagName("*"));b.firstChild;)b.removeChild(b.firstChild);
return this},clone:function(a){var b=this.map(function(){if(!c.support.noCloneEvent&&!c.isXMLDoc(this)){var d=this.outerHTML,e=this.ownerDocument;if(!d){d=e.createElement("div");d.appendChild(this.cloneNode(true));d=d.innerHTML}return c.clean([d.replace(za,"").replace(fb,'="$1">').replace($,"")],e)[0]}else return this.cloneNode(true)});if(a===true){na(this,b);na(this.find("*"),b.find("*"))}return b},html:function(a){if(a===B)return this[0]&&this[0].nodeType===1?this[0].innerHTML.replace(za,""):null;
else if(typeof a==="string"&&!Ca.test(a)&&(c.support.leadingWhitespace||!$.test(a))&&!P[(Ba.exec(a)||["",""])[1].toLowerCase()]){a=a.replace(Aa,"<$1></$2>");try{for(var b=0,d=this.length;b<d;b++)if(this[b].nodeType===1){c.cleanData(this[b].getElementsByTagName("*"));this[b].innerHTML=a}}catch(e){this.empty().append(a)}}else c.isFunction(a)?this.each(function(f){var h=c(this);h.html(a.call(this,f,h.html()))}):this.empty().append(a);return this},replaceWith:function(a){if(this[0]&&this[0].parentNode){if(c.isFunction(a))return this.each(function(b){var d=
c(this),e=d.html();d.replaceWith(a.call(this,b,e))});if(typeof a!=="string")a=c(a).detach();return this.each(function(){var b=this.nextSibling,d=this.parentNode;c(this).remove();b?c(b).before(a):c(d).append(a)})}else return this.pushStack(c(c.isFunction(a)?a():a),"replaceWith",a)},detach:function(a){return this.remove(a,true)},domManip:function(a,b,d){var e,f,h,l=a[0],k=[];if(!c.support.checkClone&&arguments.length===3&&typeof l==="string"&&Da.test(l))return this.each(function(){c(this).domManip(a,
b,d,true)});if(c.isFunction(l))return this.each(function(x){var r=c(this);a[0]=l.call(this,x,b?r.html():B);r.domManip(a,b,d)});if(this[0]){e=l&&l.parentNode;e=c.support.parentNode&&e&&e.nodeType===11&&e.childNodes.length===this.length?{fragment:e}:c.buildFragment(a,this,k);h=e.fragment;if(f=h.childNodes.length===1?h=h.firstChild:h.firstChild){b=b&&c.nodeName(f,"tr");f=0;for(var o=this.length;f<o;f++)d.call(b?c.nodeName(this[f],"table")?this[f].getElementsByTagName("tbody")[0]||this[f].appendChild(this[f].ownerDocument.createElement("tbody")):
this[f]:this[f],f>0||e.cacheable||this.length>1?h.cloneNode(true):h)}k.length&&c.each(k,Oa)}return this}});c.buildFragment=function(a,b,d){var e,f,h;b=b&&b[0]?b[0].ownerDocument||b[0]:t;if(a.length===1&&typeof a[0]==="string"&&a[0].length<512&&b===t&&!Ca.test(a[0])&&(c.support.checkClone||!Da.test(a[0]))){f=true;if(h=c.fragments[a[0]])if(h!==1)e=h}if(!e){e=b.createDocumentFragment();c.clean(a,b,e,d)}if(f)c.fragments[a[0]]=h?e:1;return{fragment:e,cacheable:f}};c.fragments={};c.each({appendTo:"append",
prependTo:"prepend",insertBefore:"before",insertAfter:"after",replaceAll:"replaceWith"},function(a,b){c.fn[a]=function(d){var e=[];d=c(d);var f=this.length===1&&this[0].parentNode;if(f&&f.nodeType===11&&f.childNodes.length===1&&d.length===1){d[b](this[0]);return this}else{f=0;for(var h=d.length;f<h;f++){var l=(f>0?this.clone(true):this).get();c(d[f])[b](l);e=e.concat(l)}return this.pushStack(e,a,d.selector)}}});c.extend({clean:function(a,b,d,e){b=b||t;if(typeof b.createElement==="undefined")b=b.ownerDocument||
b[0]&&b[0].ownerDocument||t;for(var f=[],h=0,l;(l=a[h])!=null;h++){if(typeof l==="number")l+="";if(l){if(typeof l==="string"&&!eb.test(l))l=b.createTextNode(l);else if(typeof l==="string"){l=l.replace(Aa,"<$1></$2>");var k=(Ba.exec(l)||["",""])[1].toLowerCase(),o=P[k]||P._default,x=o[0],r=b.createElement("div");for(r.innerHTML=o[1]+l+o[2];x--;)r=r.lastChild;if(!c.support.tbody){x=db.test(l);k=k==="table"&&!x?r.firstChild&&r.firstChild.childNodes:o[1]==="<table>"&&!x?r.childNodes:[];for(o=k.length-
1;o>=0;--o)c.nodeName(k[o],"tbody")&&!k[o].childNodes.length&&k[o].parentNode.removeChild(k[o])}!c.support.leadingWhitespace&&$.test(l)&&r.insertBefore(b.createTextNode($.exec(l)[0]),r.firstChild);l=r.childNodes}if(l.nodeType)f.push(l);else f=c.merge(f,l)}}if(d)for(h=0;f[h];h++)if(e&&c.nodeName(f[h],"script")&&(!f[h].type||f[h].type.toLowerCase()==="text/javascript"))e.push(f[h].parentNode?f[h].parentNode.removeChild(f[h]):f[h]);else{f[h].nodeType===1&&f.splice.apply(f,[h+1,0].concat(c.makeArray(f[h].getElementsByTagName("script"))));
d.appendChild(f[h])}return f},cleanData:function(a){for(var b,d,e=c.cache,f=c.event.special,h=c.support.deleteExpando,l=0,k;(k=a[l])!=null;l++)if(!(k.nodeName&&c.noData[k.nodeName.toLowerCase()]))if(d=k[c.expando]){if((b=e[d])&&b.events)for(var o in b.events)f[o]?c.event.remove(k,o):c.removeEvent(k,o,b.handle);if(h)delete k[c.expando];else k.removeAttribute&&k.removeAttribute(c.expando);delete e[d]}}});var Ea=/alpha\([^)]*\)/i,gb=/opacity=([^)]*)/,hb=/-([a-z])/ig,ib=/([A-Z])/g,Fa=/^-?\d+(?:px)?$/i,
jb=/^-?\d/,kb={position:"absolute",visibility:"hidden",display:"block"},Pa=["Left","Right"],Qa=["Top","Bottom"],W,Ga,aa,lb=function(a,b){return b.toUpperCase()};c.fn.css=function(a,b){if(arguments.length===2&&b===B)return this;return c.access(this,a,b,true,function(d,e,f){return f!==B?c.style(d,e,f):c.css(d,e)})};c.extend({cssHooks:{opacity:{get:function(a,b){if(b){var d=W(a,"opacity","opacity");return d===""?"1":d}else return a.style.opacity}}},cssNumber:{zIndex:true,fontWeight:true,opacity:true,
zoom:true,lineHeight:true},cssProps:{"float":c.support.cssFloat?"cssFloat":"styleFloat"},style:function(a,b,d,e){if(!(!a||a.nodeType===3||a.nodeType===8||!a.style)){var f,h=c.camelCase(b),l=a.style,k=c.cssHooks[h];b=c.cssProps[h]||h;if(d!==B){if(!(typeof d==="number"&&isNaN(d)||d==null)){if(typeof d==="number"&&!c.cssNumber[h])d+="px";if(!k||!("set"in k)||(d=k.set(a,d))!==B)try{l[b]=d}catch(o){}}}else{if(k&&"get"in k&&(f=k.get(a,false,e))!==B)return f;return l[b]}}},css:function(a,b,d){var e,f=c.camelCase(b),
h=c.cssHooks[f];b=c.cssProps[f]||f;if(h&&"get"in h&&(e=h.get(a,true,d))!==B)return e;else if(W)return W(a,b,f)},swap:function(a,b,d){var e={},f;for(f in b){e[f]=a.style[f];a.style[f]=b[f]}d.call(a);for(f in b)a.style[f]=e[f]},camelCase:function(a){return a.replace(hb,lb)}});c.curCSS=c.css;c.each(["height","width"],function(a,b){c.cssHooks[b]={get:function(d,e,f){var h;if(e){if(d.offsetWidth!==0)h=oa(d,b,f);else c.swap(d,kb,function(){h=oa(d,b,f)});if(h<=0){h=W(d,b,b);if(h==="0px"&&aa)h=aa(d,b,b);
if(h!=null)return h===""||h==="auto"?"0px":h}if(h<0||h==null){h=d.style[b];return h===""||h==="auto"?"0px":h}return typeof h==="string"?h:h+"px"}},set:function(d,e){if(Fa.test(e)){e=parseFloat(e);if(e>=0)return e+"px"}else return e}}});if(!c.support.opacity)c.cssHooks.opacity={get:function(a,b){return gb.test((b&&a.currentStyle?a.currentStyle.filter:a.style.filter)||"")?parseFloat(RegExp.$1)/100+"":b?"1":""},set:function(a,b){var d=a.style;d.zoom=1;var e=c.isNaN(b)?"":"alpha(opacity="+b*100+")",f=
d.filter||"";d.filter=Ea.test(f)?f.replace(Ea,e):d.filter+" "+e}};if(t.defaultView&&t.defaultView.getComputedStyle)Ga=function(a,b,d){var e;d=d.replace(ib,"-$1").toLowerCase();if(!(b=a.ownerDocument.defaultView))return B;if(b=b.getComputedStyle(a,null)){e=b.getPropertyValue(d);if(e===""&&!c.contains(a.ownerDocument.documentElement,a))e=c.style(a,d)}return e};if(t.documentElement.currentStyle)aa=function(a,b){var d,e,f=a.currentStyle&&a.currentStyle[b],h=a.style;if(!Fa.test(f)&&jb.test(f)){d=h.left;
e=a.runtimeStyle.left;a.runtimeStyle.left=a.currentStyle.left;h.left=b==="fontSize"?"1em":f||0;f=h.pixelLeft+"px";h.left=d;a.runtimeStyle.left=e}return f===""?"auto":f};W=Ga||aa;if(c.expr&&c.expr.filters){c.expr.filters.hidden=function(a){var b=a.offsetHeight;return a.offsetWidth===0&&b===0||!c.support.reliableHiddenOffsets&&(a.style.display||c.css(a,"display"))==="none"};c.expr.filters.visible=function(a){return!c.expr.filters.hidden(a)}}var mb=c.now(),nb=/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
ob=/^(?:select|textarea)/i,pb=/^(?:color|date|datetime|email|hidden|month|number|password|range|search|tel|text|time|url|week)$/i,qb=/^(?:GET|HEAD)$/,Ra=/\[\]$/,T=/\=\?(&|$)/,ja=/\?/,rb=/([?&])_=[^&]*/,sb=/^(\w+:)?\/\/([^\/?#]+)/,tb=/%20/g,ub=/#.*$/,Ha=c.fn.load;c.fn.extend({load:function(a,b,d){if(typeof a!=="string"&&Ha)return Ha.apply(this,arguments);else if(!this.length)return this;var e=a.indexOf(" ");if(e>=0){var f=a.slice(e,a.length);a=a.slice(0,e)}e="GET";if(b)if(c.isFunction(b)){d=b;b=null}else if(typeof b===
"object"){b=c.param(b,c.ajaxSettings.traditional);e="POST"}var h=this;c.ajax({url:a,type:e,dataType:"html",data:b,complete:function(l,k){if(k==="success"||k==="notmodified")h.html(f?c("<div>").append(l.responseText.replace(nb,"")).find(f):l.responseText);d&&h.each(d,[l.responseText,k,l])}});return this},serialize:function(){return c.param(this.serializeArray())},serializeArray:function(){return this.map(function(){return this.elements?c.makeArray(this.elements):this}).filter(function(){return this.name&&
!this.disabled&&(this.checked||ob.test(this.nodeName)||pb.test(this.type))}).map(function(a,b){var d=c(this).val();return d==null?null:c.isArray(d)?c.map(d,function(e){return{name:b.name,value:e}}):{name:b.name,value:d}}).get()}});c.each("ajaxStart ajaxStop ajaxComplete ajaxError ajaxSuccess ajaxSend".split(" "),function(a,b){c.fn[b]=function(d){return this.bind(b,d)}});c.extend({get:function(a,b,d,e){if(c.isFunction(b)){e=e||d;d=b;b=null}return c.ajax({type:"GET",url:a,data:b,success:d,dataType:e})},
getScript:function(a,b){return c.get(a,null,b,"script")},getJSON:function(a,b,d){return c.get(a,b,d,"json")},post:function(a,b,d,e){if(c.isFunction(b)){e=e||d;d=b;b={}}return c.ajax({type:"POST",url:a,data:b,success:d,dataType:e})},ajaxSetup:function(a){c.extend(c.ajaxSettings,a)},ajaxSettings:{url:location.href,global:true,type:"GET",contentType:"application/x-www-form-urlencoded",processData:true,async:true,xhr:function(){return new E.XMLHttpRequest},accepts:{xml:"application/xml, text/xml",html:"text/html",
script:"text/javascript, application/javascript",json:"application/json, text/javascript",text:"text/plain",_default:"*/*"}},ajax:function(a){var b=c.extend(true,{},c.ajaxSettings,a),d,e,f,h=b.type.toUpperCase(),l=qb.test(h);b.url=b.url.replace(ub,"");b.context=a&&a.context!=null?a.context:b;if(b.data&&b.processData&&typeof b.data!=="string")b.data=c.param(b.data,b.traditional);if(b.dataType==="jsonp"){if(h==="GET")T.test(b.url)||(b.url+=(ja.test(b.url)?"&":"?")+(b.jsonp||"callback")+"=?");else if(!b.data||
!T.test(b.data))b.data=(b.data?b.data+"&":"")+(b.jsonp||"callback")+"=?";b.dataType="json"}if(b.dataType==="json"&&(b.data&&T.test(b.data)||T.test(b.url))){d=b.jsonpCallback||"jsonp"+mb++;if(b.data)b.data=(b.data+"").replace(T,"="+d+"$1");b.url=b.url.replace(T,"="+d+"$1");b.dataType="script";var k=E[d];E[d]=function(m){if(c.isFunction(k))k(m);else{E[d]=B;try{delete E[d]}catch(p){}}f=m;c.handleSuccess(b,w,e,f);c.handleComplete(b,w,e,f);r&&r.removeChild(A)}}if(b.dataType==="script"&&b.cache===null)b.cache=
false;if(b.cache===false&&l){var o=c.now(),x=b.url.replace(rb,"$1_="+o);b.url=x+(x===b.url?(ja.test(b.url)?"&":"?")+"_="+o:"")}if(b.data&&l)b.url+=(ja.test(b.url)?"&":"?")+b.data;b.global&&c.active++===0&&c.event.trigger("ajaxStart");o=(o=sb.exec(b.url))&&(o[1]&&o[1].toLowerCase()!==location.protocol||o[2].toLowerCase()!==location.host);if(b.dataType==="script"&&h==="GET"&&o){var r=t.getElementsByTagName("head")[0]||t.documentElement,A=t.createElement("script");if(b.scriptCharset)A.charset=b.scriptCharset;
A.src=b.url;if(!d){var C=false;A.onload=A.onreadystatechange=function(){if(!C&&(!this.readyState||this.readyState==="loaded"||this.readyState==="complete")){C=true;c.handleSuccess(b,w,e,f);c.handleComplete(b,w,e,f);A.onload=A.onreadystatechange=null;r&&A.parentNode&&r.removeChild(A)}}}r.insertBefore(A,r.firstChild);return B}var J=false,w=b.xhr();if(w){b.username?w.open(h,b.url,b.async,b.username,b.password):w.open(h,b.url,b.async);try{if(b.data!=null&&!l||a&&a.contentType)w.setRequestHeader("Content-Type",
b.contentType);if(b.ifModified){c.lastModified[b.url]&&w.setRequestHeader("If-Modified-Since",c.lastModified[b.url]);c.etag[b.url]&&w.setRequestHeader("If-None-Match",c.etag[b.url])}o||w.setRequestHeader("X-Requested-With","XMLHttpRequest");w.setRequestHeader("Accept",b.dataType&&b.accepts[b.dataType]?b.accepts[b.dataType]+", */*; q=0.01":b.accepts._default)}catch(I){}if(b.beforeSend&&b.beforeSend.call(b.context,w,b)===false){b.global&&c.active--===1&&c.event.trigger("ajaxStop");w.abort();return false}b.global&&
c.triggerGlobal(b,"ajaxSend",[w,b]);var L=w.onreadystatechange=function(m){if(!w||w.readyState===0||m==="abort"){J||c.handleComplete(b,w,e,f);J=true;if(w)w.onreadystatechange=c.noop}else if(!J&&w&&(w.readyState===4||m==="timeout")){J=true;w.onreadystatechange=c.noop;e=m==="timeout"?"timeout":!c.httpSuccess(w)?"error":b.ifModified&&c.httpNotModified(w,b.url)?"notmodified":"success";var p;if(e==="success")try{f=c.httpData(w,b.dataType,b)}catch(q){e="parsererror";p=q}if(e==="success"||e==="notmodified")d||
c.handleSuccess(b,w,e,f);else c.handleError(b,w,e,p);d||c.handleComplete(b,w,e,f);m==="timeout"&&w.abort();if(b.async)w=null}};try{var g=w.abort;w.abort=function(){w&&Function.prototype.call.call(g,w);L("abort")}}catch(i){}b.async&&b.timeout>0&&setTimeout(function(){w&&!J&&L("timeout")},b.timeout);try{w.send(l||b.data==null?null:b.data)}catch(n){c.handleError(b,w,null,n);c.handleComplete(b,w,e,f)}b.async||L();return w}},param:function(a,b){var d=[],e=function(h,l){l=c.isFunction(l)?l():l;d[d.length]=
encodeURIComponent(h)+"="+encodeURIComponent(l)};if(b===B)b=c.ajaxSettings.traditional;if(c.isArray(a)||a.jquery)c.each(a,function(){e(this.name,this.value)});else for(var f in a)da(f,a[f],b,e);return d.join("&").replace(tb,"+")}});c.extend({active:0,lastModified:{},etag:{},handleError:function(a,b,d,e){a.error&&a.error.call(a.context,b,d,e);a.global&&c.triggerGlobal(a,"ajaxError",[b,a,e])},handleSuccess:function(a,b,d,e){a.success&&a.success.call(a.context,e,d,b);a.global&&c.triggerGlobal(a,"ajaxSuccess",
[b,a])},handleComplete:function(a,b,d){a.complete&&a.complete.call(a.context,b,d);a.global&&c.triggerGlobal(a,"ajaxComplete",[b,a]);a.global&&c.active--===1&&c.event.trigger("ajaxStop")},triggerGlobal:function(a,b,d){(a.context&&a.context.url==null?c(a.context):c.event).trigger(b,d)},httpSuccess:function(a){try{return!a.status&&location.protocol==="file:"||a.status>=200&&a.status<300||a.status===304||a.status===1223}catch(b){}return false},httpNotModified:function(a,b){var d=a.getResponseHeader("Last-Modified"),
e=a.getResponseHeader("Etag");if(d)c.lastModified[b]=d;if(e)c.etag[b]=e;return a.status===304},httpData:function(a,b,d){var e=a.getResponseHeader("content-type")||"",f=b==="xml"||!b&&e.indexOf("xml")>=0;a=f?a.responseXML:a.responseText;f&&a.documentElement.nodeName==="parsererror"&&c.error("parsererror");if(d&&d.dataFilter)a=d.dataFilter(a,b);if(typeof a==="string")if(b==="json"||!b&&e.indexOf("json")>=0)a=c.parseJSON(a);else if(b==="script"||!b&&e.indexOf("javascript")>=0)c.globalEval(a);return a}});
if(E.ActiveXObject)c.ajaxSettings.xhr=function(){if(E.location.protocol!=="file:")try{return new E.XMLHttpRequest}catch(a){}try{return new E.ActiveXObject("Microsoft.XMLHTTP")}catch(b){}};c.support.ajax=!!c.ajaxSettings.xhr();var ea={},vb=/^(?:toggle|show|hide)$/,wb=/^([+\-]=)?([\d+.\-]+)(.*)$/,ba,pa=[["height","marginTop","marginBottom","paddingTop","paddingBottom"],["width","marginLeft","marginRight","paddingLeft","paddingRight"],["opacity"]];c.fn.extend({show:function(a,b,d){if(a||a===0)return this.animate(S("show",
3),a,b,d);else{d=0;for(var e=this.length;d<e;d++){a=this[d];b=a.style.display;if(!c.data(a,"olddisplay")&&b==="none")b=a.style.display="";b===""&&c.css(a,"display")==="none"&&c.data(a,"olddisplay",qa(a.nodeName))}for(d=0;d<e;d++){a=this[d];b=a.style.display;if(b===""||b==="none")a.style.display=c.data(a,"olddisplay")||""}return this}},hide:function(a,b,d){if(a||a===0)return this.animate(S("hide",3),a,b,d);else{a=0;for(b=this.length;a<b;a++){d=c.css(this[a],"display");d!=="none"&&c.data(this[a],"olddisplay",
d)}for(a=0;a<b;a++)this[a].style.display="none";return this}},_toggle:c.fn.toggle,toggle:function(a,b,d){var e=typeof a==="boolean";if(c.isFunction(a)&&c.isFunction(b))this._toggle.apply(this,arguments);else a==null||e?this.each(function(){var f=e?a:c(this).is(":hidden");c(this)[f?"show":"hide"]()}):this.animate(S("toggle",3),a,b,d);return this},fadeTo:function(a,b,d,e){return this.filter(":hidden").css("opacity",0).show().end().animate({opacity:b},a,d,e)},animate:function(a,b,d,e){var f=c.speed(b,
d,e);if(c.isEmptyObject(a))return this.each(f.complete);return this[f.queue===false?"each":"queue"](function(){var h=c.extend({},f),l,k=this.nodeType===1,o=k&&c(this).is(":hidden"),x=this;for(l in a){var r=c.camelCase(l);if(l!==r){a[r]=a[l];delete a[l];l=r}if(a[l]==="hide"&&o||a[l]==="show"&&!o)return h.complete.call(this);if(k&&(l==="height"||l==="width")){h.overflow=[this.style.overflow,this.style.overflowX,this.style.overflowY];if(c.css(this,"display")==="inline"&&c.css(this,"float")==="none")if(c.support.inlineBlockNeedsLayout)if(qa(this.nodeName)===
"inline")this.style.display="inline-block";else{this.style.display="inline";this.style.zoom=1}else this.style.display="inline-block"}if(c.isArray(a[l])){(h.specialEasing=h.specialEasing||{})[l]=a[l][1];a[l]=a[l][0]}}if(h.overflow!=null)this.style.overflow="hidden";h.curAnim=c.extend({},a);c.each(a,function(A,C){var J=new c.fx(x,h,A);if(vb.test(C))J[C==="toggle"?o?"show":"hide":C](a);else{var w=wb.exec(C),I=J.cur()||0;if(w){var L=parseFloat(w[2]),g=w[3]||"px";if(g!=="px"){c.style(x,A,(L||1)+g);I=(L||
1)/J.cur()*I;c.style(x,A,I+g)}if(w[1])L=(w[1]==="-="?-1:1)*L+I;J.custom(I,L,g)}else J.custom(I,C,"")}});return true})},stop:function(a,b){var d=c.timers;a&&this.queue([]);this.each(function(){for(var e=d.length-1;e>=0;e--)if(d[e].elem===this){b&&d[e](true);d.splice(e,1)}});b||this.dequeue();return this}});c.each({slideDown:S("show",1),slideUp:S("hide",1),slideToggle:S("toggle",1),fadeIn:{opacity:"show"},fadeOut:{opacity:"hide"},fadeToggle:{opacity:"toggle"}},function(a,b){c.fn[a]=function(d,e,f){return this.animate(b,
d,e,f)}});c.extend({speed:function(a,b,d){var e=a&&typeof a==="object"?c.extend({},a):{complete:d||!d&&b||c.isFunction(a)&&a,duration:a,easing:d&&b||b&&!c.isFunction(b)&&b};e.duration=c.fx.off?0:typeof e.duration==="number"?e.duration:e.duration in c.fx.speeds?c.fx.speeds[e.duration]:c.fx.speeds._default;e.old=e.complete;e.complete=function(){e.queue!==false&&c(this).dequeue();c.isFunction(e.old)&&e.old.call(this)};return e},easing:{linear:function(a,b,d,e){return d+e*a},swing:function(a,b,d,e){return(-Math.cos(a*
Math.PI)/2+0.5)*e+d}},timers:[],fx:function(a,b,d){this.options=b;this.elem=a;this.prop=d;if(!b.orig)b.orig={}}});c.fx.prototype={update:function(){this.options.step&&this.options.step.call(this.elem,this.now,this);(c.fx.step[this.prop]||c.fx.step._default)(this)},cur:function(){if(this.elem[this.prop]!=null&&(!this.elem.style||this.elem.style[this.prop]==null))return this.elem[this.prop];var a=parseFloat(c.css(this.elem,this.prop));return a&&a>-1E4?a:0},custom:function(a,b,d){function e(l){return f.step(l)}
var f=this,h=c.fx;this.startTime=c.now();this.start=a;this.end=b;this.unit=d||this.unit||"px";this.now=this.start;this.pos=this.state=0;e.elem=this.elem;if(e()&&c.timers.push(e)&&!ba)ba=setInterval(h.tick,h.interval)},show:function(){this.options.orig[this.prop]=c.style(this.elem,this.prop);this.options.show=true;this.custom(this.prop==="width"||this.prop==="height"?1:0,this.cur());c(this.elem).show()},hide:function(){this.options.orig[this.prop]=c.style(this.elem,this.prop);this.options.hide=true;
this.custom(this.cur(),0)},step:function(a){var b=c.now(),d=true;if(a||b>=this.options.duration+this.startTime){this.now=this.end;this.pos=this.state=1;this.update();this.options.curAnim[this.prop]=true;for(var e in this.options.curAnim)if(this.options.curAnim[e]!==true)d=false;if(d){if(this.options.overflow!=null&&!c.support.shrinkWrapBlocks){var f=this.elem,h=this.options;c.each(["","X","Y"],function(k,o){f.style["overflow"+o]=h.overflow[k]})}this.options.hide&&c(this.elem).hide();if(this.options.hide||
this.options.show)for(var l in this.options.curAnim)c.style(this.elem,l,this.options.orig[l]);this.options.complete.call(this.elem)}return false}else{a=b-this.startTime;this.state=a/this.options.duration;b=this.options.easing||(c.easing.swing?"swing":"linear");this.pos=c.easing[this.options.specialEasing&&this.options.specialEasing[this.prop]||b](this.state,a,0,1,this.options.duration);this.now=this.start+(this.end-this.start)*this.pos;this.update()}return true}};c.extend(c.fx,{tick:function(){for(var a=
c.timers,b=0;b<a.length;b++)a[b]()||a.splice(b--,1);a.length||c.fx.stop()},interval:13,stop:function(){clearInterval(ba);ba=null},speeds:{slow:600,fast:200,_default:400},step:{opacity:function(a){c.style(a.elem,"opacity",a.now)},_default:function(a){if(a.elem.style&&a.elem.style[a.prop]!=null)a.elem.style[a.prop]=(a.prop==="width"||a.prop==="height"?Math.max(0,a.now):a.now)+a.unit;else a.elem[a.prop]=a.now}}});if(c.expr&&c.expr.filters)c.expr.filters.animated=function(a){return c.grep(c.timers,function(b){return a===
b.elem}).length};var xb=/^t(?:able|d|h)$/i,Ia=/^(?:body|html)$/i;c.fn.offset="getBoundingClientRect"in t.documentElement?function(a){var b=this[0],d;if(a)return this.each(function(l){c.offset.setOffset(this,a,l)});if(!b||!b.ownerDocument)return null;if(b===b.ownerDocument.body)return c.offset.bodyOffset(b);try{d=b.getBoundingClientRect()}catch(e){}var f=b.ownerDocument,h=f.documentElement;if(!d||!c.contains(h,b))return d||{top:0,left:0};b=f.body;f=fa(f);return{top:d.top+(f.pageYOffset||c.support.boxModel&&
h.scrollTop||b.scrollTop)-(h.clientTop||b.clientTop||0),left:d.left+(f.pageXOffset||c.support.boxModel&&h.scrollLeft||b.scrollLeft)-(h.clientLeft||b.clientLeft||0)}}:function(a){var b=this[0];if(a)return this.each(function(x){c.offset.setOffset(this,a,x)});if(!b||!b.ownerDocument)return null;if(b===b.ownerDocument.body)return c.offset.bodyOffset(b);c.offset.initialize();var d,e=b.offsetParent,f=b.ownerDocument,h=f.documentElement,l=f.body;d=(f=f.defaultView)?f.getComputedStyle(b,null):b.currentStyle;
for(var k=b.offsetTop,o=b.offsetLeft;(b=b.parentNode)&&b!==l&&b!==h;){if(c.offset.supportsFixedPosition&&d.position==="fixed")break;d=f?f.getComputedStyle(b,null):b.currentStyle;k-=b.scrollTop;o-=b.scrollLeft;if(b===e){k+=b.offsetTop;o+=b.offsetLeft;if(c.offset.doesNotAddBorder&&!(c.offset.doesAddBorderForTableAndCells&&xb.test(b.nodeName))){k+=parseFloat(d.borderTopWidth)||0;o+=parseFloat(d.borderLeftWidth)||0}e=b.offsetParent}if(c.offset.subtractsBorderForOverflowNotVisible&&d.overflow!=="visible"){k+=
parseFloat(d.borderTopWidth)||0;o+=parseFloat(d.borderLeftWidth)||0}d=d}if(d.position==="relative"||d.position==="static"){k+=l.offsetTop;o+=l.offsetLeft}if(c.offset.supportsFixedPosition&&d.position==="fixed"){k+=Math.max(h.scrollTop,l.scrollTop);o+=Math.max(h.scrollLeft,l.scrollLeft)}return{top:k,left:o}};c.offset={initialize:function(){var a=t.body,b=t.createElement("div"),d,e,f,h=parseFloat(c.css(a,"marginTop"))||0;c.extend(b.style,{position:"absolute",top:0,left:0,margin:0,border:0,width:"1px",
height:"1px",visibility:"hidden"});b.innerHTML="<div style='position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;'><div></div></div><table style='position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;' cellpadding='0' cellspacing='0'><tr><td></td></tr></table>";a.insertBefore(b,a.firstChild);d=b.firstChild;e=d.firstChild;f=d.nextSibling.firstChild.firstChild;this.doesNotAddBorder=e.offsetTop!==5;this.doesAddBorderForTableAndCells=
f.offsetTop===5;e.style.position="fixed";e.style.top="20px";this.supportsFixedPosition=e.offsetTop===20||e.offsetTop===15;e.style.position=e.style.top="";d.style.overflow="hidden";d.style.position="relative";this.subtractsBorderForOverflowNotVisible=e.offsetTop===-5;this.doesNotIncludeMarginInBodyOffset=a.offsetTop!==h;a.removeChild(b);c.offset.initialize=c.noop},bodyOffset:function(a){var b=a.offsetTop,d=a.offsetLeft;c.offset.initialize();if(c.offset.doesNotIncludeMarginInBodyOffset){b+=parseFloat(c.css(a,
"marginTop"))||0;d+=parseFloat(c.css(a,"marginLeft"))||0}return{top:b,left:d}},setOffset:function(a,b,d){var e=c.css(a,"position");if(e==="static")a.style.position="relative";var f=c(a),h=f.offset(),l=c.css(a,"top"),k=c.css(a,"left"),o=e==="absolute"&&c.inArray("auto",[l,k])>-1;e={};var x={};if(o)x=f.position();l=o?x.top:parseInt(l,10)||0;k=o?x.left:parseInt(k,10)||0;if(c.isFunction(b))b=b.call(a,d,h);if(b.top!=null)e.top=b.top-h.top+l;if(b.left!=null)e.left=b.left-h.left+k;"using"in b?b.using.call(a,
e):f.css(e)}};c.fn.extend({position:function(){if(!this[0])return null;var a=this[0],b=this.offsetParent(),d=this.offset(),e=Ia.test(b[0].nodeName)?{top:0,left:0}:b.offset();d.top-=parseFloat(c.css(a,"marginTop"))||0;d.left-=parseFloat(c.css(a,"marginLeft"))||0;e.top+=parseFloat(c.css(b[0],"borderTopWidth"))||0;e.left+=parseFloat(c.css(b[0],"borderLeftWidth"))||0;return{top:d.top-e.top,left:d.left-e.left}},offsetParent:function(){return this.map(function(){for(var a=this.offsetParent||t.body;a&&!Ia.test(a.nodeName)&&
c.css(a,"position")==="static";)a=a.offsetParent;return a})}});c.each(["Left","Top"],function(a,b){var d="scroll"+b;c.fn[d]=function(e){var f=this[0],h;if(!f)return null;if(e!==B)return this.each(function(){if(h=fa(this))h.scrollTo(!a?e:c(h).scrollLeft(),a?e:c(h).scrollTop());else this[d]=e});else return(h=fa(f))?"pageXOffset"in h?h[a?"pageYOffset":"pageXOffset"]:c.support.boxModel&&h.document.documentElement[d]||h.document.body[d]:f[d]}});c.each(["Height","Width"],function(a,b){var d=b.toLowerCase();
c.fn["inner"+b]=function(){return this[0]?parseFloat(c.css(this[0],d,"padding")):null};c.fn["outer"+b]=function(e){return this[0]?parseFloat(c.css(this[0],d,e?"margin":"border")):null};c.fn[d]=function(e){var f=this[0];if(!f)return e==null?null:this;if(c.isFunction(e))return this.each(function(l){var k=c(this);k[d](e.call(this,l,k[d]()))});if(c.isWindow(f))return f.document.compatMode==="CSS1Compat"&&f.document.documentElement["client"+b]||f.document.body["client"+b];else if(f.nodeType===9)return Math.max(f.documentElement["client"+
b],f.body["scroll"+b],f.documentElement["scroll"+b],f.body["offset"+b],f.documentElement["offset"+b]);else if(e===B){f=c.css(f,d);var h=parseFloat(f);return c.isNaN(h)?f:h}else return this.css(d,typeof e==="string"?e:e+"px")}})})(window);
/* Copyright (c) 2006 Brandon Aaron (http://brandonaaron.net)
 * Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) 
 * and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
 *
 * $LastChangedDate: 2007-07-21 18:44:59 -0500 (Sat, 21 Jul 2007) $
 * $Rev: 2446 $
 *
 * Version 2.1.1
 */

(function($){

/**
 * The bgiframe is chainable and applies the iframe hack to get 
 * around zIndex issues in IE6. It will only apply itself in IE6 
 * and adds a class to the iframe called 'bgiframe'. The iframe
 * is appeneded as the first child of the matched element(s) 
 * with a tabIndex and zIndex of -1.
 * 
 * By default the plugin will take borders, sized with pixel units,
 * into account. If a different unit is used for the border's width,
 * then you will need to use the top and left settings as explained below.
 *
 * NOTICE: This plugin has been reported to cause perfromance problems
 * when used on elements that change properties (like width, height and
 * opacity) a lot in IE6. Most of these problems have been caused by 
 * the expressions used to calculate the elements width, height and 
 * borders. Some have reported it is due to the opacity filter. All 
 * these settings can be changed if needed as explained below.
 *
 * @example $('div').bgiframe();
 * @before <div><p>Paragraph</p></div>
 * @result <div><iframe class="bgiframe".../><p>Paragraph</p></div>
 *
 * @param Map settings Optional settings to configure the iframe.
 * @option String|Number top The iframe must be offset to the top
 * 		by the width of the top border. This should be a negative 
 *      number representing the border-top-width. If a number is 
 * 		is used here, pixels will be assumed. Otherwise, be sure
 *		to specify a unit. An expression could also be used. 
 * 		By default the value is "auto" which will use an expression 
 * 		to get the border-top-width if it is in pixels.
 * @option String|Number left The iframe must be offset to the left
 * 		by the width of the left border. This should be a negative 
 *      number representing the border-left-width. If a number is 
 * 		is used here, pixels will be assumed. Otherwise, be sure
 *		to specify a unit. An expression could also be used. 
 * 		By default the value is "auto" which will use an expression 
 * 		to get the border-left-width if it is in pixels.
 * @option String|Number width This is the width of the iframe. If
 *		a number is used here, pixels will be assume. Otherwise, be sure
 * 		to specify a unit. An experssion could also be used.
 *		By default the value is "auto" which will use an experssion
 * 		to get the offsetWidth.
 * @option String|Number height This is the height of the iframe. If
 *		a number is used here, pixels will be assume. Otherwise, be sure
 * 		to specify a unit. An experssion could also be used.
 *		By default the value is "auto" which will use an experssion
 * 		to get the offsetHeight.
 * @option Boolean opacity This is a boolean representing whether or not
 * 		to use opacity. If set to true, the opacity of 0 is applied. If
 *		set to false, the opacity filter is not applied. Default: true.
 * @option String src This setting is provided so that one could change 
 *		the src of the iframe to whatever they need.
 *		Default: "javascript:false;"
 *
 * @name bgiframe
 * @type jQuery
 * @cat Plugins/bgiframe
 * @author Brandon Aaron (brandon.aaron@gmail.com || http://brandonaaron.net)
 */
$.fn.bgIframe = $.fn.bgiframe = function(s) {
	// This is only for IE6
	if ( $.browser.msie && /6.0/.test(navigator.userAgent) ) {
		s = $.extend({
			top     : 'auto', // auto == .currentStyle.borderTopWidth
			left    : 'auto', // auto == .currentStyle.borderLeftWidth
			width   : 'auto', // auto == offsetWidth
			height  : 'auto', // auto == offsetHeight
			opacity : true,
			src     : 'javascript:false;'
		}, s || {});
		var prop = function(n){return n&&n.constructor==Number?n+'px':n;},
		    html = '<iframe class="bgiframe"frameborder="0"tabindex="-1"src="'+s.src+'"'+
		               'style="display:block;position:absolute;z-index:-1;'+
			               (s.opacity !== false?'filter:Alpha(Opacity=\'0\');':'')+
					       'top:'+(s.top=='auto'?'expression(((parseInt(this.parentNode.currentStyle.borderTopWidth)||0)*-1)+\'px\')':prop(s.top))+';'+
					       'left:'+(s.left=='auto'?'expression(((parseInt(this.parentNode.currentStyle.borderLeftWidth)||0)*-1)+\'px\')':prop(s.left))+';'+
					       'width:'+(s.width=='auto'?'expression(this.parentNode.offsetWidth+\'px\')':prop(s.width))+';'+
					       'height:'+(s.height=='auto'?'expression(this.parentNode.offsetHeight+\'px\')':prop(s.height))+';'+
					'"/>';
		return this.each(function() {
			if ( $('> iframe.bgiframe', this).length == 0 )
				this.insertBefore( document.createElement(html), this.firstChild );
		});
	}
	return this;
};

})(jQuery);/* Copyright (c) 2010 Brandon Aaron (http://brandonaaron.net)
 * Licensed under the MIT License (LICENSE.txt).
 *
 * Version 2.1.2
 */
(function(a){a.fn.bgiframe=(a.browser.msie&&/msie 6\.0/i.test(navigator.userAgent)?function(d){d=a.extend({top:"auto",left:"auto",width:"auto",height:"auto",opacity:true,src:"javascript:false;"},d);var c='<iframe class="bgiframe"frameborder="0"tabindex="-1"src="'+d.src+'"style="display:block;position:absolute;z-index:-1;'+(d.opacity!==false?"filter:Alpha(Opacity='0');":"")+"top:"+(d.top=="auto"?"expression(((parseInt(this.parentNode.currentStyle.borderTopWidth)||0)*-1)+'px')":b(d.top))+";left:"+(d.left=="auto"?"expression(((parseInt(this.parentNode.currentStyle.borderLeftWidth)||0)*-1)+'px')":b(d.left))+";width:"+(d.width=="auto"?"expression(this.parentNode.offsetWidth+'px')":b(d.width))+";height:"+(d.height=="auto"?"expression(this.parentNode.offsetHeight+'px')":b(d.height))+';"/>';return this.each(function(){if(a(this).children("iframe.bgiframe").length===0){this.insertBefore(document.createElement(c),this.firstChild)}})}:function(){return this});a.fn.bgIframe=a.fn.bgiframe;function b(c){return c&&c.constructor===Number?c+"px":c}})(jQuery);
/*
 * jQuery UI 1.9m3
 *
 * Copyright 2010, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI
 */
(function(a,c){a.ui=a.ui||{};if(a.ui.version){return}a.extend(a.ui,{version:"1.9m3",keyCode:{ALT:18,BACKSPACE:8,CAPS_LOCK:20,COMMA:188,COMMAND:91,COMMAND_LEFT:91,COMMAND_RIGHT:93,CONTROL:17,DELETE:46,DOWN:40,END:35,ENTER:13,ESCAPE:27,HOME:36,INSERT:45,LEFT:37,MENU:93,NUMPAD_ADD:107,NUMPAD_DECIMAL:110,NUMPAD_DIVIDE:111,NUMPAD_ENTER:108,NUMPAD_MULTIPLY:106,NUMPAD_SUBTRACT:109,PAGE_DOWN:34,PAGE_UP:33,PERIOD:190,RIGHT:39,SHIFT:16,SPACE:32,TAB:9,UP:38,WINDOWS:91}});a.fn.extend({_focus:a.fn.focus,focus:function(d,e){return typeof d==="number"?this.each(function(){var f=this;setTimeout(function(){a(f).focus();if(e){e.call(f)}},d)}):this._focus.apply(this,arguments)},scrollParent:function(){var d;if((a.browser.msie&&(/(static|relative)/).test(this.css("position")))||(/absolute/).test(this.css("position"))){d=this.parents().filter(function(){return(/(relative|absolute|fixed)/).test(a.curCSS(this,"position",1))&&(/(auto|scroll)/).test(a.curCSS(this,"overflow",1)+a.curCSS(this,"overflow-y",1)+a.curCSS(this,"overflow-x",1))}).eq(0)}else{d=this.parents().filter(function(){return(/(auto|scroll)/).test(a.curCSS(this,"overflow",1)+a.curCSS(this,"overflow-y",1)+a.curCSS(this,"overflow-x",1))}).eq(0)}return(/fixed/).test(this.css("position"))||!d.length?a(document):d},zIndex:function(g){if(g!==c){return this.css("zIndex",g)}if(this.length){var e=a(this[0]),d,f;while(e.length&&e[0]!==document){d=e.css("position");if(d==="absolute"||d==="relative"||d==="fixed"){f=parseInt(e.css("zIndex"),10);if(!isNaN(f)&&f!==0){return f}}e=e.parent()}}return 0},disableSelection:function(){return this.bind((a.support.selectstart?"selectstart":"mousedown")+".ui-disableSelection",function(d){d.preventDefault()})},enableSelection:function(){return this.unbind(".ui-disableSelection")}});a.each(["Width","Height"],function(f,d){var e=d==="Width"?["Left","Right"]:["Top","Bottom"],g=d.toLowerCase(),j={innerWidth:a.fn.innerWidth,innerHeight:a.fn.innerHeight,outerWidth:a.fn.outerWidth,outerHeight:a.fn.outerHeight};function h(l,k,i,m){a.each(e,function(){k-=parseFloat(a.curCSS(l,"padding"+this,true))||0;if(i){k-=parseFloat(a.curCSS(l,"border"+this+"Width",true))||0}if(m){k-=parseFloat(a.curCSS(l,"margin"+this,true))||0}});return k}a.fn["inner"+d]=function(i){if(i===c){return j["inner"+d].call(this)}return this.each(function(){a(this).css(g,h(this,i)+"px")})};a.fn["outer"+d]=function(i,k){if(typeof i!=="number"){return j["outer"+d].call(this,i)}return this.each(function(){a(this).css(g,h(this,i,true,k)+"px")})}});function b(d){return !a(d).parents().andSelf().filter(function(){return a.curCSS(this,"visibility")==="hidden"||a.expr.filters.hidden(this)}).length}a.extend(a.expr[":"],{data:function(f,e,d){return !!a.data(f,d[3])},focusable:function(f){var i=f.nodeName.toLowerCase(),d=a.attr(f,"tabindex");if("area"===i){var h=f.parentNode,g=h.name,e;if(!f.href||!g||h.nodeName.toLowerCase()!=="map"){return false}e=a("img[usemap=#"+g+"]")[0];return !!e&&b(e)}return(/input|select|textarea|button|object/.test(i)?!f.disabled:"a"==i?f.href||!isNaN(d):!isNaN(d))&&b(f)},tabbable:function(e){var d=a.attr(e,"tabindex");return(isNaN(d)||d>=0)&&a(e).is(":focusable")}});a(function(){var d=document.body,e=d.appendChild(e=document.createElement("div"));a.extend(e.style,{minHeight:"100px",height:"auto",padding:0,borderWidth:0});a.support.minHeight=e.offsetHeight===100;a.support.selectstart="onselectstart" in e;d.removeChild(e).style.display="none"});a.extend(a.ui,{plugin:{add:function(e,f,h){var g=a.ui[e].prototype;for(var d in h){g.plugins[d]=g.plugins[d]||[];g.plugins[d].push([f,h[d]])}},call:function(d,f,e){var h=d.plugins[f];if(!h||!d.element[0].parentNode){return}for(var g=0;g<h.length;g++){if(d.options[h[g][0]]){h[g][1].apply(d.element,e)}}}},contains:function(e,d){return document.compareDocumentPosition?e.compareDocumentPosition(d)&16:e!==d&&e.contains(d)},hasScroll:function(g,e){if(a(g).css("overflow")==="hidden"){return false}var d=(e&&e==="left")?"scrollLeft":"scrollTop",f=false;if(g[d]>0){return true}g[d]=1;f=(g[d]>0);g[d]=0;return f},isOverAxis:function(e,d,f){return(e>d)&&(e<(d+f))},isOver:function(i,e,h,g,d,f){return a.ui.isOverAxis(i,h,d)&&a.ui.isOverAxis(e,g,f)}})})(jQuery);
/*
 * jQuery UI Widget 1.9m3
 *
 * Copyright 2010, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI/Widget
 */
(function(b,d){if(b.cleanData){var c=b.cleanData;b.cleanData=function(e){for(var f=0,g;(g=e[f])!=null;f++){b(g).triggerHandler("remove")}c(e)}}else{var a=b.fn.remove;b.fn.remove=function(e,f){return this.each(function(){if(!f){if(!e||b.filter(e,[this]).length){b("*",this).add([this]).each(function(){b(this).triggerHandler("remove")})}}return a.call(b(this),e,f)})}}b.widget=function(f,h,e){var g=f.split(".")[0],j;f=f.split(".")[1];j=g+"-"+f;if(!e){e=h;h=b.Widget}b.expr[":"][j]=function(k){return !!b.data(k,f)};b[g]=b[g]||{};b[g][f]=function(k,l){if(arguments.length){this._createWidget(k,l)}};var i=new h();i.options=b.extend(true,{},i.options);b[g][f].prototype=b.extend(true,i,{namespace:g,widgetName:f,widgetEventPrefix:b[g][f].prototype.widgetEventPrefix||f,widgetBaseClass:j,base:h.prototype},e);b.widget.bridge(f,b[g][f])};b.widget.bridge=function(f,e){b.fn[f]=function(i){var g=typeof i==="string",h=Array.prototype.slice.call(arguments,1),j=this;i=!g&&h.length?b.extend.apply(null,[true,i].concat(h)):i;if(g&&i.charAt(0)==="_"){return j}if(g){this.each(function(){var k=b.data(this,f),l=k&&b.isFunction(k[i])?k[i].apply(k,h):k;if(l!==k&&l!==d){j=l;return false}})}else{this.each(function(){var k=b.data(this,f);if(k){k.option(i||{})._init()}else{b.data(this,f,new e(i,this))}})}return j}};b.Widget=function(e,f){if(arguments.length){this._createWidget(e,f)}};b.Widget.prototype={widgetName:"widget",widgetEventPrefix:"",options:{disabled:false},_createWidget:function(f,g){b.data(g,this.widgetName,this);this.element=b(g);this.options=b.extend(true,{},this.options,this._getCreateOptions(),f);var e=this;this.element.bind("remove."+this.widgetName,function(){e.destroy()});this._create();this._trigger("create");this._init()},_getCreateOptions:function(){return b.metadata&&b.metadata.get(this.element[0])[this.widgetName]},_create:function(){},_init:function(){},_super:function(e){return this.base[e].apply(this,Array.prototype.slice.call(arguments,1))},_superApply:function(f,e){return this.base[f].apply(this,e)},destroy:function(){this.element.unbind("."+this.widgetName).removeData(this.widgetName);this.widget().unbind("."+this.widgetName).removeAttr("aria-disabled").removeClass(this.widgetBaseClass+"-disabled ui-state-disabled")},widget:function(){return this.element},option:function(f,g){var e=f;if(arguments.length===0){return b.extend({},this.options)}if(typeof f==="string"){if(g===d){return this.options[f]}e={};e[f]=g}this._setOptions(e);return this},_setOptions:function(f){var e=this;b.each(f,function(g,h){e._setOption(g,h)});return this},_setOption:function(e,f){this.options[e]=f;if(e==="disabled"){this.widget()[f?"addClass":"removeClass"](this.widgetBaseClass+"-disabled ui-state-disabled").attr("aria-disabled",f)}return this},enable:function(){return this._setOption("disabled",false)},disable:function(){return this._setOption("disabled",true)},_trigger:function(f,g,h){var k=this.options[f];g=b.Event(g);g.type=(f===this.widgetEventPrefix?f:this.widgetEventPrefix+f).toLowerCase();h=h||{};if(g.originalEvent){for(var e=b.event.props.length,j;e;){j=b.event.props[--e];g[j]=g.originalEvent[j]}}this.element.trigger(g,h);return !(b.isFunction(k)&&k.call(this.element[0],g,h)===false||g.isDefaultPrevented())}}})(jQuery);
/*
 * jQuery UI Mouse 1.9m3
 *
 * Copyright 2010, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI/Mouse
 *
 * Depends:
 *	jquery.ui.widget.js
 */
(function(a,b){a.widget("ui.mouse",{options:{cancel:":input,option",distance:1,delay:0},_mouseInit:function(){var c=this;this.element.bind("mousedown."+this.widgetName,function(d){return c._mouseDown(d)}).bind("click."+this.widgetName,function(d){if(c._preventClickEvent){c._preventClickEvent=false;d.stopImmediatePropagation();return false}});this.started=false},_mouseDestroy:function(){this.element.unbind("."+this.widgetName)},_mouseDown:function(e){e.originalEvent=e.originalEvent||{};if(e.originalEvent.mouseHandled){return}(this._mouseStarted&&this._mouseUp(e));this._mouseDownEvent=e;var d=this,f=(e.which==1),c=(typeof this.options.cancel=="string"?a(e.target).parents().add(e.target).filter(this.options.cancel).length:false);if(!f||c||!this._mouseCapture(e)){return true}this.mouseDelayMet=!this.options.delay;if(!this.mouseDelayMet){this._mouseDelayTimer=setTimeout(function(){d.mouseDelayMet=true},this.options.delay)}if(this._mouseDistanceMet(e)&&this._mouseDelayMet(e)){this._mouseStarted=(this._mouseStart(e)!==false);if(!this._mouseStarted){e.preventDefault();return true}}this._mouseMoveDelegate=function(g){return d._mouseMove(g)};this._mouseUpDelegate=function(g){return d._mouseUp(g)};a(document).bind("mousemove."+this.widgetName,this._mouseMoveDelegate).bind("mouseup."+this.widgetName,this._mouseUpDelegate);e.preventDefault();e.originalEvent.mouseHandled=true;return true},_mouseMove:function(c){if(a.browser.msie&&!(document.documentMode>=9)&&!c.button){return this._mouseUp(c)}if(this._mouseStarted){this._mouseDrag(c);return c.preventDefault()}if(this._mouseDistanceMet(c)&&this._mouseDelayMet(c)){this._mouseStarted=(this._mouseStart(this._mouseDownEvent,c)!==false);(this._mouseStarted?this._mouseDrag(c):this._mouseUp(c))}return !this._mouseStarted},_mouseUp:function(c){a(document).unbind("mousemove."+this.widgetName,this._mouseMoveDelegate).unbind("mouseup."+this.widgetName,this._mouseUpDelegate);if(this._mouseStarted){this._mouseStarted=false;this._preventClickEvent=(c.target==this._mouseDownEvent.target);this._mouseStop(c)}return false},_mouseDistanceMet:function(c){return(Math.max(Math.abs(this._mouseDownEvent.pageX-c.pageX),Math.abs(this._mouseDownEvent.pageY-c.pageY))>=this.options.distance)},_mouseDelayMet:function(c){return this.mouseDelayMet},_mouseStart:function(c){},_mouseDrag:function(c){},_mouseStop:function(c){},_mouseCapture:function(c){return true}})})(jQuery);(function(a,b){a.widget("ui.draggable",a.ui.mouse,{widgetEventPrefix:"drag",options:{addClasses:true,appendTo:"parent",axis:false,connectToSortable:false,containment:false,cursor:"auto",cursorAt:false,grid:false,handle:false,helper:"original",iframeFix:false,opacity:false,refreshPositions:false,revert:false,revertDuration:500,scope:"default",scroll:true,scrollSensitivity:20,scrollSpeed:20,snap:false,snapMode:"both",snapTolerance:20,stack:false,zIndex:false},_create:function(){if(this.options.helper=="original"&&!(/^(?:r|a|f)/).test(this.element.css("position"))){this.element[0].style.position="relative"}(this.options.addClasses&&this.element.addClass("ui-draggable"));(this.options.disabled&&this.element.addClass("ui-draggable-disabled"));this._mouseInit()},destroy:function(){if(!this.element.data("draggable")){return}this.element.removeData("draggable").unbind(".draggable").removeClass("ui-draggable ui-draggable-dragging ui-draggable-disabled");this._mouseDestroy();return this},_mouseCapture:function(c){var d=this.options;if(this.helper||d.disabled||a(c.target).is(".ui-resizable-handle")){return false}this.handle=this._getHandle(c);if(!this.handle){return false}return true},_mouseStart:function(c){var d=this.options;this.helper=this._createHelper(c);this._cacheHelperProportions();if(a.ui.ddmanager){a.ui.ddmanager.current=this}this._cacheMargins();this.cssPosition=this.helper.css("position");this.scrollParent=this.helper.scrollParent();this.offset=this.positionAbs=this.element.offset();this.offset={top:this.offset.top-this.margins.top,left:this.offset.left-this.margins.left};a.extend(this.offset,{click:{left:c.pageX-this.offset.left,top:c.pageY-this.offset.top},parent:this._getParentOffset(),relative:this._getRelativeOffset()});this.originalPosition=this.position=this._generatePosition(c);this.originalPageX=c.pageX;this.originalPageY=c.pageY;(d.cursorAt&&this._adjustOffsetFromHelper(d.cursorAt));if(d.containment){this._setContainment()}if(this._trigger("start",c)===false){this._clear();return false}this._cacheHelperProportions();if(a.ui.ddmanager&&!d.dropBehaviour){a.ui.ddmanager.prepareOffsets(this,c)}this.helper.addClass("ui-draggable-dragging");this._mouseDrag(c,true);return true},_mouseDrag:function(c,e){this.position=this._generatePosition(c);this.positionAbs=this._convertPositionTo("absolute");if(!e){var d=this._uiHash();if(this._trigger("drag",c,d)===false){this._mouseUp({});return false}this.position=d.position}if(!this.options.axis||this.options.axis!="y"){this.helper[0].style.left=this.position.left+"px"}if(!this.options.axis||this.options.axis!="x"){this.helper[0].style.top=this.position.top+"px"}if(a.ui.ddmanager){a.ui.ddmanager.drag(this,c)}return false},_mouseStop:function(d){var e=false;if(a.ui.ddmanager&&!this.options.dropBehaviour){e=a.ui.ddmanager.drop(this,d)}if(this.dropped){e=this.dropped;this.dropped=false}if(!this.element[0]||!this.element[0].parentNode){return false}if((this.options.revert=="invalid"&&!e)||(this.options.revert=="valid"&&e)||this.options.revert===true||(a.isFunction(this.options.revert)&&this.options.revert.call(this.element,e))){var c=this;a(this.helper).animate(this.originalPosition,parseInt(this.options.revertDuration,10),function(){if(c._trigger("stop",d)!==false){c._clear()}})}else{if(this._trigger("stop",d)!==false){this._clear()}}return false},cancel:function(){if(this.helper.is(".ui-draggable-dragging")){this._mouseUp({})}else{this._clear()}return this},_getHandle:function(c){var d=!this.options.handle||!a(this.options.handle,this.element).length?true:false;a(this.options.handle,this.element).find("*").andSelf().each(function(){if(this==c.target){d=true}});return d},_createHelper:function(d){var e=this.options;var c=a.isFunction(e.helper)?a(e.helper.apply(this.element[0],[d])):(e.helper=="clone"?this.element.clone():this.element);if(!c.parents("body").length){c.appendTo((e.appendTo=="parent"?this.element[0].parentNode:e.appendTo))}if(c[0]!=this.element[0]&&!(/(fixed|absolute)/).test(c.css("position"))){c.css("position","absolute")}return c},_adjustOffsetFromHelper:function(c){if(typeof c=="string"){c=c.split(" ")}if(a.isArray(c)){c={left:+c[0],top:+c[1]||0}}if("left" in c){this.offset.click.left=c.left+this.margins.left}if("right" in c){this.offset.click.left=this.helperProportions.width-c.right+this.margins.left}if("top" in c){this.offset.click.top=c.top+this.margins.top}if("bottom" in c){this.offset.click.top=this.helperProportions.height-c.bottom+this.margins.top}},_getParentOffset:function(){this.offsetParent=this.helper.offsetParent();var c=this.offsetParent.offset();if(this.cssPosition=="absolute"&&this.scrollParent[0]!=document&&a.ui.contains(this.scrollParent[0],this.offsetParent[0])){c.left+=this.scrollParent.scrollLeft();c.top+=this.scrollParent.scrollTop()}if((this.offsetParent[0]==document.body)||(this.offsetParent[0].tagName&&this.offsetParent[0].tagName.toLowerCase()=="html"&&a.browser.msie)){c={top:0,left:0}}return{top:c.top+(parseInt(this.offsetParent.css("borderTopWidth"),10)||0),left:c.left+(parseInt(this.offsetParent.css("borderLeftWidth"),10)||0)}},_getRelativeOffset:function(){if(this.cssPosition=="relative"){var c=this.element.position();return{top:c.top-(parseInt(this.helper.css("top"),10)||0)+this.scrollParent.scrollTop(),left:c.left-(parseInt(this.helper.css("left"),10)||0)+this.scrollParent.scrollLeft()}}else{return{top:0,left:0}}},_cacheMargins:function(){this.margins={left:(parseInt(this.element.css("marginLeft"),10)||0),top:(parseInt(this.element.css("marginTop"),10)||0)}},_cacheHelperProportions:function(){this.helperProportions={width:this.helper.outerWidth(),height:this.helper.outerHeight()}},_setContainment:function(){var f=this.options;if(f.containment=="parent"){f.containment=this.helper[0].parentNode}if(f.containment=="document"||f.containment=="window"){this.containment=[0-this.offset.relative.left-this.offset.parent.left,0-this.offset.relative.top-this.offset.parent.top,a(f.containment=="document"?document:window).width()-this.helperProportions.width-this.margins.left,(a(f.containment=="document"?document:window).height()||document.body.parentNode.scrollHeight)-this.helperProportions.height-this.margins.top]}if(!(/^(document|window|parent)$/).test(f.containment)&&f.containment.constructor!=Array){var d=a(f.containment)[0];if(!d){return}var e=a(f.containment).offset();var c=(a(d).css("overflow")!="hidden");this.containment=[e.left+(parseInt(a(d).css("borderLeftWidth"),10)||0)+(parseInt(a(d).css("paddingLeft"),10)||0)-this.margins.left,e.top+(parseInt(a(d).css("borderTopWidth"),10)||0)+(parseInt(a(d).css("paddingTop"),10)||0)-this.margins.top,e.left+(c?Math.max(d.scrollWidth,d.offsetWidth):d.offsetWidth)-(parseInt(a(d).css("borderLeftWidth"),10)||0)-(parseInt(a(d).css("paddingRight"),10)||0)-this.helperProportions.width-this.margins.left,e.top+(c?Math.max(d.scrollHeight,d.offsetHeight):d.offsetHeight)-(parseInt(a(d).css("borderTopWidth"),10)||0)-(parseInt(a(d).css("paddingBottom"),10)||0)-this.helperProportions.height-this.margins.top]}else{if(f.containment.constructor==Array){this.containment=f.containment}}},_convertPositionTo:function(g,i){if(!i){i=this.position}var e=g=="absolute"?1:-1;var f=this.options,c=this.cssPosition=="absolute"&&!(this.scrollParent[0]!=document&&a.ui.contains(this.scrollParent[0],this.offsetParent[0]))?this.offsetParent:this.scrollParent,h=(/(html|body)/i).test(c[0].tagName);return{top:(i.top+this.offset.relative.top*e+this.offset.parent.top*e-(a.browser.safari&&a.browser.version<526&&this.cssPosition=="fixed"?0:(this.cssPosition=="fixed"?-this.scrollParent.scrollTop():(h?0:c.scrollTop()))*e)),left:(i.left+this.offset.relative.left*e+this.offset.parent.left*e-(a.browser.safari&&a.browser.version<526&&this.cssPosition=="fixed"?0:(this.cssPosition=="fixed"?-this.scrollParent.scrollLeft():h?0:c.scrollLeft())*e))}},_generatePosition:function(f){var i=this.options,c=this.cssPosition=="absolute"&&!(this.scrollParent[0]!=document&&a.ui.contains(this.scrollParent[0],this.offsetParent[0]))?this.offsetParent:this.scrollParent,j=(/(html|body)/i).test(c[0].tagName);var e=f.pageX;var d=f.pageY;if(this.originalPosition){if(this.containment){if(f.pageX-this.offset.click.left<this.containment[0]){e=this.containment[0]+this.offset.click.left}if(f.pageY-this.offset.click.top<this.containment[1]){d=this.containment[1]+this.offset.click.top}if(f.pageX-this.offset.click.left>this.containment[2]){e=this.containment[2]+this.offset.click.left}if(f.pageY-this.offset.click.top>this.containment[3]){d=this.containment[3]+this.offset.click.top}}if(i.grid){var h=this.originalPageY+Math.round((d-this.originalPageY)/i.grid[1])*i.grid[1];d=this.containment?(!(h-this.offset.click.top<this.containment[1]||h-this.offset.click.top>this.containment[3])?h:(!(h-this.offset.click.top<this.containment[1])?h-i.grid[1]:h+i.grid[1])):h;var g=this.originalPageX+Math.round((e-this.originalPageX)/i.grid[0])*i.grid[0];e=this.containment?(!(g-this.offset.click.left<this.containment[0]||g-this.offset.click.left>this.containment[2])?g:(!(g-this.offset.click.left<this.containment[0])?g-i.grid[0]:g+i.grid[0])):g}}return{top:(d-this.offset.click.top-this.offset.relative.top-this.offset.parent.top+(a.browser.safari&&a.browser.version<526&&this.cssPosition=="fixed"?0:(this.cssPosition=="fixed"?-this.scrollParent.scrollTop():(j?0:c.scrollTop())))),left:(e-this.offset.click.left-this.offset.relative.left-this.offset.parent.left+(a.browser.safari&&a.browser.version<526&&this.cssPosition=="fixed"?0:(this.cssPosition=="fixed"?-this.scrollParent.scrollLeft():j?0:c.scrollLeft())))}},_clear:function(){this.helper.removeClass("ui-draggable-dragging");if(this.helper[0]!=this.element[0]&&!this.cancelHelperRemoval){this.helper.remove()}this.helper=null;this.cancelHelperRemoval=false},_trigger:function(c,d,e){e=e||this._uiHash();a.ui.plugin.call(this,c,[d,e]);if(c=="drag"){this.positionAbs=this._convertPositionTo("absolute")}return a.Widget.prototype._trigger.call(this,c,d,e)},plugins:{},_uiHash:function(c){return{helper:this.helper,position:this.position,originalPosition:this.originalPosition,offset:this.positionAbs}}});a.extend(a.ui.draggable,{version:"1.9m3"});a.ui.plugin.add("draggable","connectToSortable",{start:function(d,f){var e=a(this).data("draggable"),g=e.options,c=a.extend({},f,{item:e.element});e.sortables=[];a(g.connectToSortable).each(function(){var h=a.data(this,"sortable");if(h&&!h.options.disabled){e.sortables.push({instance:h,shouldRevert:h.options.revert});h._refreshItems();h._trigger("activate",d,c)}})},stop:function(d,f){var e=a(this).data("draggable"),c=a.extend({},f,{item:e.element});a.each(e.sortables,function(){if(this.instance.isOver){this.instance.isOver=0;e.cancelHelperRemoval=true;this.instance.cancelHelperRemoval=false;if(this.shouldRevert){this.instance.options.revert=true}this.instance._mouseStop(d);this.instance.options.helper=this.instance.options._helper;if(e.options.helper=="original"){this.instance.currentItem.css({top:"auto",left:"auto"})}}else{this.instance.cancelHelperRemoval=false;this.instance._trigger("deactivate",d,c)}})},drag:function(d,g){var f=a(this).data("draggable"),c=this;var e=function(j){var p=this.offset.click.top,n=this.offset.click.left;var h=this.positionAbs.top,l=this.positionAbs.left;var k=j.height,m=j.width;var q=j.top,i=j.left;return a.ui.isOver(h+p,l+n,q,i,k,m)};a.each(f.sortables,function(h){this.instance.positionAbs=f.positionAbs;this.instance.helperProportions=f.helperProportions;this.instance.offset.click=f.offset.click;if(this.instance._intersectsWith(this.instance.containerCache)){if(!this.instance.isOver){this.instance.isOver=1;this.instance.currentItem=a(c).clone().appendTo(this.instance.element).data("sortable-item",true);this.instance.options._helper=this.instance.options.helper;this.instance.options.helper=function(){return g.helper[0]};d.target=this.instance.currentItem[0];this.instance._mouseCapture(d,true);this.instance._mouseStart(d,true,true);this.instance.offset.click.top=f.offset.click.top;this.instance.offset.click.left=f.offset.click.left;this.instance.offset.parent.left-=f.offset.parent.left-this.instance.offset.parent.left;this.instance.offset.parent.top-=f.offset.parent.top-this.instance.offset.parent.top;f._trigger("toSortable",d);f.dropped=this.instance.element;f.currentItem=f.element;this.instance.fromOutside=f}if(this.instance.currentItem){this.instance._mouseDrag(d)}}else{if(this.instance.isOver){this.instance.isOver=0;this.instance.cancelHelperRemoval=true;this.instance.options.revert=false;this.instance._trigger("out",d,this.instance._uiHash(this.instance));this.instance._mouseStop(d,true);this.instance.options.helper=this.instance.options._helper;this.instance.currentItem.remove();if(this.instance.placeholder){this.instance.placeholder.remove()}f._trigger("fromSortable",d);f.dropped=false}}})}});a.ui.plugin.add("draggable","cursor",{start:function(d,e){var c=a("body"),f=a(this).data("draggable").options;if(c.css("cursor")){f._cursor=c.css("cursor")}c.css("cursor",f.cursor)},stop:function(c,d){var e=a(this).data("draggable").options;if(e._cursor){a("body").css("cursor",e._cursor)}}});a.ui.plugin.add("draggable","iframeFix",{start:function(c,d){var e=a(this).data("draggable").options;a(e.iframeFix===true?"iframe":e.iframeFix).each(function(){a('<div class="ui-draggable-iframeFix" style="background: #fff;"></div>').css({width:this.offsetWidth+"px",height:this.offsetHeight+"px",position:"absolute",opacity:"0.001",zIndex:1000}).css(a(this).offset()).appendTo("body")})},stop:function(c,d){a("div.ui-draggable-iframeFix").each(function(){this.parentNode.removeChild(this)})}});a.ui.plugin.add("draggable","opacity",{start:function(d,e){var c=a(e.helper),f=a(this).data("draggable").options;if(c.css("opacity")){f._opacity=c.css("opacity")}c.css("opacity",f.opacity)},stop:function(c,d){var e=a(this).data("draggable").options;if(e._opacity){a(d.helper).css("opacity",e._opacity)}}});a.ui.plugin.add("draggable","scroll",{start:function(d,e){var c=a(this).data("draggable");if(c.scrollParent[0]!=document&&c.scrollParent[0].tagName!="HTML"){c.overflowOffset=c.scrollParent.offset()}},drag:function(e,f){var d=a(this).data("draggable"),g=d.options,c=false;if(d.scrollParent[0]!=document&&d.scrollParent[0].tagName!="HTML"){if(!g.axis||g.axis!="x"){if((d.overflowOffset.top+d.scrollParent[0].offsetHeight)-e.pageY<g.scrollSensitivity){d.scrollParent[0].scrollTop=c=d.scrollParent[0].scrollTop+g.scrollSpeed}else{if(e.pageY-d.overflowOffset.top<g.scrollSensitivity){d.scrollParent[0].scrollTop=c=d.scrollParent[0].scrollTop-g.scrollSpeed}}}if(!g.axis||g.axis!="y"){if((d.overflowOffset.left+d.scrollParent[0].offsetWidth)-e.pageX<g.scrollSensitivity){d.scrollParent[0].scrollLeft=c=d.scrollParent[0].scrollLeft+g.scrollSpeed}else{if(e.pageX-d.overflowOffset.left<g.scrollSensitivity){d.scrollParent[0].scrollLeft=c=d.scrollParent[0].scrollLeft-g.scrollSpeed}}}}else{if(!g.axis||g.axis!="x"){if(e.pageY-a(document).scrollTop()<g.scrollSensitivity){c=a(document).scrollTop(a(document).scrollTop()-g.scrollSpeed)}else{if(a(window).height()-(e.pageY-a(document).scrollTop())<g.scrollSensitivity){c=a(document).scrollTop(a(document).scrollTop()+g.scrollSpeed)}}}if(!g.axis||g.axis!="y"){if(e.pageX-a(document).scrollLeft()<g.scrollSensitivity){c=a(document).scrollLeft(a(document).scrollLeft()-g.scrollSpeed)}else{if(a(window).width()-(e.pageX-a(document).scrollLeft())<g.scrollSensitivity){c=a(document).scrollLeft(a(document).scrollLeft()+g.scrollSpeed)}}}}if(c!==false&&a.ui.ddmanager&&!g.dropBehaviour){a.ui.ddmanager.prepareOffsets(d,e)}}});a.ui.plugin.add("draggable","snap",{start:function(d,e){var c=a(this).data("draggable"),f=c.options;c.snapElements=[];a(f.snap.constructor!=String?(f.snap.items||":data(draggable)"):f.snap).each(function(){var h=a(this);var g=h.offset();if(this!=c.element[0]){c.snapElements.push({item:this,width:h.outerWidth(),height:h.outerHeight(),top:g.top,left:g.left})}})},drag:function(u,p){var g=a(this).data("draggable"),q=g.options;var y=q.snapTolerance;var x=p.offset.left,w=x+g.helperProportions.width,f=p.offset.top,e=f+g.helperProportions.height;for(var v=g.snapElements.length-1;v>=0;v--){var s=g.snapElements[v].left,n=s+g.snapElements[v].width,m=g.snapElements[v].top,A=m+g.snapElements[v].height;if(!((s-y<x&&x<n+y&&m-y<f&&f<A+y)||(s-y<x&&x<n+y&&m-y<e&&e<A+y)||(s-y<w&&w<n+y&&m-y<f&&f<A+y)||(s-y<w&&w<n+y&&m-y<e&&e<A+y))){if(g.snapElements[v].snapping){(g.options.snap.release&&g.options.snap.release.call(g.element,u,a.extend(g._uiHash(),{snapItem:g.snapElements[v].item})))}g.snapElements[v].snapping=false;continue}if(q.snapMode!="inner"){var c=Math.abs(m-e)<=y;var z=Math.abs(A-f)<=y;var j=Math.abs(s-w)<=y;var k=Math.abs(n-x)<=y;if(c){p.position.top=g._convertPositionTo("relative",{top:m-g.helperProportions.height,left:0}).top-g.margins.top}if(z){p.position.top=g._convertPositionTo("relative",{top:A,left:0}).top-g.margins.top}if(j){p.position.left=g._convertPositionTo("relative",{top:0,left:s-g.helperProportions.width}).left-g.margins.left}if(k){p.position.left=g._convertPositionTo("relative",{top:0,left:n}).left-g.margins.left}}var h=(c||z||j||k);if(q.snapMode!="outer"){var c=Math.abs(m-f)<=y;var z=Math.abs(A-e)<=y;var j=Math.abs(s-x)<=y;var k=Math.abs(n-w)<=y;if(c){p.position.top=g._convertPositionTo("relative",{top:m,left:0}).top-g.margins.top}if(z){p.position.top=g._convertPositionTo("relative",{top:A-g.helperProportions.height,left:0}).top-g.margins.top}if(j){p.position.left=g._convertPositionTo("relative",{top:0,left:s}).left-g.margins.left}if(k){p.position.left=g._convertPositionTo("relative",{top:0,left:n-g.helperProportions.width}).left-g.margins.left}}if(!g.snapElements[v].snapping&&(c||z||j||k||h)){(g.options.snap.snap&&g.options.snap.snap.call(g.element,u,a.extend(g._uiHash(),{snapItem:g.snapElements[v].item})))}g.snapElements[v].snapping=(c||z||j||k||h)}}});a.ui.plugin.add("draggable","stack",{start:function(d,e){var g=a(this).data("draggable").options;var f=a.makeArray(a(g.stack)).sort(function(i,h){return(parseInt(a(i).css("zIndex"),10)||0)-(parseInt(a(h).css("zIndex"),10)||0)});if(!f.length){return}var c=parseInt(f[0].style.zIndex)||0;a(f).each(function(h){this.style.zIndex=c+h});this[0].style.zIndex=c+f.length}});a.ui.plugin.add("draggable","zIndex",{start:function(d,e){var c=a(e.helper),f=a(this).data("draggable").options;if(c.css("zIndex")){f._zIndex=c.css("zIndex")}c.css("zIndex",f.zIndex)},stop:function(c,d){var e=a(this).data("draggable").options;if(e._zIndex){a(d.helper).css("zIndex",e._zIndex)}}})})(jQuery);(function(a,b){a.widget("ui.droppable",{widgetEventPrefix:"drop",options:{accept:"*",activeClass:false,addClasses:true,greedy:false,hoverClass:false,scope:"default",tolerance:"intersect"},_create:function(){var d=this.options,c=d.accept;this.isover=0;this.isout=1;this.accept=a.isFunction(c)?c:function(e){return e.is(c)};this.proportions={width:this.element[0].offsetWidth,height:this.element[0].offsetHeight};a.ui.ddmanager.droppables[d.scope]=a.ui.ddmanager.droppables[d.scope]||[];a.ui.ddmanager.droppables[d.scope].push(this);(d.addClasses&&this.element.addClass("ui-droppable"))},destroy:function(){var c=a.ui.ddmanager.droppables[this.options.scope];for(var d=0;d<c.length;d++){if(c[d]==this){c.splice(d,1)}}this.element.removeClass("ui-droppable ui-droppable-disabled").removeData("droppable").unbind(".droppable");return this},_setOption:function(c,d){if(c=="accept"){this.accept=a.isFunction(d)?d:function(e){return e.is(d)}}a.Widget.prototype._setOption.apply(this,arguments)},_activate:function(d){var c=a.ui.ddmanager.current;if(this.options.activeClass){this.element.addClass(this.options.activeClass)}(c&&this._trigger("activate",d,this.ui(c)))},_deactivate:function(d){var c=a.ui.ddmanager.current;if(this.options.activeClass){this.element.removeClass(this.options.activeClass)}(c&&this._trigger("deactivate",d,this.ui(c)))},_over:function(d){var c=a.ui.ddmanager.current;if(!c||(c.currentItem||c.element)[0]==this.element[0]){return}if(this.accept.call(this.element[0],(c.currentItem||c.element))){if(this.options.hoverClass){this.element.addClass(this.options.hoverClass)}this._trigger("over",d,this.ui(c))}},_out:function(d){var c=a.ui.ddmanager.current;if(!c||(c.currentItem||c.element)[0]==this.element[0]){return}if(this.accept.call(this.element[0],(c.currentItem||c.element))){if(this.options.hoverClass){this.element.removeClass(this.options.hoverClass)}this._trigger("out",d,this.ui(c))}},_drop:function(d,e){var c=e||a.ui.ddmanager.current;if(!c||(c.currentItem||c.element)[0]==this.element[0]){return false}var f=false;this.element.find(":data(droppable)").not(".ui-draggable-dragging").each(function(){var g=a.data(this,"droppable");if(g.options.greedy&&!g.options.disabled&&g.options.scope==c.options.scope&&g.accept.call(g.element[0],(c.currentItem||c.element))&&a.ui.intersect(c,a.extend(g,{offset:g.element.offset()}),g.options.tolerance)){f=true;return false}});if(f){return false}if(this.accept.call(this.element[0],(c.currentItem||c.element))){if(this.options.activeClass){this.element.removeClass(this.options.activeClass)}if(this.options.hoverClass){this.element.removeClass(this.options.hoverClass)}this._trigger("drop",d,this.ui(c));return this.element}return false},ui:function(d){return{draggable:(d.currentItem||d.element),helper:d.helper,position:d.position,offset:d.positionAbs}}});a.extend(a.ui.droppable,{version:"1.9m3"});a.ui.intersect=function(q,j,o){if(!j.offset){return false}var e=(q.positionAbs||q.position.absolute).left,d=e+q.helperProportions.width,n=(q.positionAbs||q.position.absolute).top,m=n+q.helperProportions.height;var g=j.offset.left,c=g+j.proportions.width,p=j.offset.top,k=p+j.proportions.height;switch(o){case"fit":return(g<=e&&d<=c&&p<=n&&m<=k);break;case"intersect":return(g<e+(q.helperProportions.width/2)&&d-(q.helperProportions.width/2)<c&&p<n+(q.helperProportions.height/2)&&m-(q.helperProportions.height/2)<k);break;case"pointer":var h=((q.positionAbs||q.position.absolute).left+(q.clickOffset||q.offset.click).left),i=((q.positionAbs||q.position.absolute).top+(q.clickOffset||q.offset.click).top),f=a.ui.isOver(i,h,p,g,j.proportions.height,j.proportions.width);return f;break;case"touch":return((n>=p&&n<=k)||(m>=p&&m<=k)||(n<p&&m>k))&&((e>=g&&e<=c)||(d>=g&&d<=c)||(e<g&&d>c));break;default:return false;break}};a.ui.ddmanager={current:null,droppables:{"default":[]},prepareOffsets:function(f,h){var c=a.ui.ddmanager.droppables[f.options.scope]||[];var g=h?h.type:null;var k=(f.currentItem||f.element).find(":data(droppable)").andSelf();droppablesLoop:for(var e=0;e<c.length;e++){if(c[e].options.disabled||(f&&!c[e].accept.call(c[e].element[0],(f.currentItem||f.element)))){continue}for(var d=0;d<k.length;d++){if(k[d]==c[e].element[0]){c[e].proportions.height=0;continue droppablesLoop}}c[e].visible=c[e].element.css("display")!="none";if(!c[e].visible){continue}c[e].offset=c[e].element.offset();c[e].proportions={width:c[e].element[0].offsetWidth,height:c[e].element[0].offsetHeight};if(g=="mousedown"){c[e]._activate.call(c[e],h)}}},drop:function(c,d){var e=false;a.each(a.ui.ddmanager.droppables[c.options.scope]||[],function(){if(!this.options){return}if(!this.options.disabled&&this.visible&&a.ui.intersect(c,this,this.options.tolerance)){e=e||this._drop.call(this,d)}if(!this.options.disabled&&this.visible&&this.accept.call(this.element[0],(c.currentItem||c.element))){this.isout=1;this.isover=0;this._deactivate.call(this,d)}});return e},drag:function(c,d){if(c.options.refreshPositions){a.ui.ddmanager.prepareOffsets(c,d)}a.each(a.ui.ddmanager.droppables[c.options.scope]||[],function(){if(this.options.disabled||this.greedyChild||!this.visible){return}var f=a.ui.intersect(c,this,this.options.tolerance);var h=!f&&this.isover==1?"isout":(f&&this.isover==0?"isover":null);if(!h){return}var g;if(this.options.greedy){var e=this.element.parents(":data(droppable):eq(0)");if(e.length){g=a.data(e[0],"droppable");g.greedyChild=(h=="isover"?1:0)}}if(g&&h=="isover"){g.isover=0;g.isout=1;g._out.call(g,d)}this[h]=1;this[h=="isout"?"isover":"isout"]=0;this[h=="isover"?"_over":"_out"].call(this,d);if(g&&h=="isout"){g.isout=0;g.isover=1;g._over.call(g,d)}})}}})(jQuery);(function(c,d){c.widget("ui.resizable",c.ui.mouse,{widgetEventPrefix:"resize",options:{alsoResize:false,animate:false,animateDuration:"slow",animateEasing:"swing",aspectRatio:false,autoHide:false,containment:false,ghost:false,grid:false,handles:"e,s,se",helper:false,maxHeight:null,maxWidth:null,minHeight:10,minWidth:10,zIndex:1000},_create:function(){var f=this,k=this.options;this.element.addClass("ui-resizable");c.extend(this,{_aspectRatio:!!(k.aspectRatio),aspectRatio:k.aspectRatio,originalElement:this.element,_proportionallyResizeElements:[],_helper:k.helper||k.ghost||k.animate?k.helper||"ui-resizable-helper":null});if(this.element[0].nodeName.match(/canvas|textarea|input|select|button|img/i)){if(/relative/.test(this.element.css("position"))&&c.browser.opera){this.element.css({position:"relative",top:"auto",left:"auto"})}this.element.wrap(c('<div class="ui-wrapper" style="overflow: hidden;"></div>').css({position:this.element.css("position"),width:this.element.outerWidth(),height:this.element.outerHeight(),top:this.element.css("top"),left:this.element.css("left")}));this.element=this.element.parent().data("resizable",this.element.data("resizable"));this.elementIsWrapper=true;this.element.css({marginLeft:this.originalElement.css("marginLeft"),marginTop:this.originalElement.css("marginTop"),marginRight:this.originalElement.css("marginRight"),marginBottom:this.originalElement.css("marginBottom")});this.originalElement.css({marginLeft:0,marginTop:0,marginRight:0,marginBottom:0});this.originalResizeStyle=this.originalElement.css("resize");this.originalElement.css("resize","none");this._proportionallyResizeElements.push(this.originalElement.css({position:"static",zoom:1,display:"block"}));this.originalElement.css({margin:this.originalElement.css("margin")});this._proportionallyResize()}this.handles=k.handles||(!c(".ui-resizable-handle",this.element).length?"e,s,se":{n:".ui-resizable-n",e:".ui-resizable-e",s:".ui-resizable-s",w:".ui-resizable-w",se:".ui-resizable-se",sw:".ui-resizable-sw",ne:".ui-resizable-ne",nw:".ui-resizable-nw"});if(this.handles.constructor==String){if(this.handles=="all"){this.handles="n,e,s,w,se,sw,ne,nw"}var l=this.handles.split(",");this.handles={};for(var g=0;g<l.length;g++){var j=c.trim(l[g]),e="ui-resizable-"+j;var h=c('<div class="ui-resizable-handle '+e+'"></div>');if(/sw|se|ne|nw/.test(j)){h.css({zIndex:++k.zIndex})}if("se"==j){h.addClass("ui-icon ui-icon-gripsmall-diagonal-se")}this.handles[j]=".ui-resizable-"+j;this.element.append(h)}}this._renderAxis=function(q){q=q||this.element;for(var n in this.handles){if(this.handles[n].constructor==String){this.handles[n]=c(this.handles[n],this.element).show()}if(this.elementIsWrapper&&this.originalElement[0].nodeName.match(/textarea|input|select|button/i)){var o=c(this.handles[n],this.element),p=0;p=/sw|ne|nw|se|n|s/.test(n)?o.outerHeight():o.outerWidth();var m=["padding",/ne|nw|n/.test(n)?"Top":/se|sw|s/.test(n)?"Bottom":/^e$/.test(n)?"Right":"Left"].join("");q.css(m,p);this._proportionallyResize()}if(!c(this.handles[n]).length){continue}}};this._renderAxis(this.element);this._handles=c(".ui-resizable-handle",this.element).disableSelection();this._handles.mouseover(function(){if(!f.resizing){if(this.className){var i=this.className.match(/ui-resizable-(se|sw|ne|nw|n|e|s|w)/i)}f.axis=i&&i[1]?i[1]:"se"}});if(k.autoHide){this._handles.hide();c(this.element).addClass("ui-resizable-autohide").hover(function(){c(this).removeClass("ui-resizable-autohide");f._handles.show()},function(){if(!f.resizing){c(this).addClass("ui-resizable-autohide");f._handles.hide()}})}this._mouseInit()},destroy:function(){this._mouseDestroy();var e=function(g){c(g).removeClass("ui-resizable ui-resizable-disabled ui-resizable-resizing").removeData("resizable").unbind(".resizable").find(".ui-resizable-handle").remove()};if(this.elementIsWrapper){e(this.element);var f=this.element;f.after(this.originalElement.css({position:f.css("position"),width:f.outerWidth(),height:f.outerHeight(),top:f.css("top"),left:f.css("left")})).remove()}this.originalElement.css("resize",this.originalResizeStyle);e(this.originalElement);return this},_mouseCapture:function(f){var g=false;for(var e in this.handles){if(c(this.handles[e])[0]==f.target){g=true}}return !this.options.disabled&&g},_mouseStart:function(g){var j=this.options,f=this.element.position(),e=this.element;this.resizing=true;this.documentScroll={top:c(document).scrollTop(),left:c(document).scrollLeft()};if(e.is(".ui-draggable")||(/absolute/).test(e.css("position"))){e.css({position:"absolute",top:f.top,left:f.left})}if(c.browser.opera&&(/relative/).test(e.css("position"))){e.css({position:"relative",top:"auto",left:"auto"})}this._renderProxy();var k=b(this.helper.css("left")),h=b(this.helper.css("top"));if(j.containment){k+=c(j.containment).scrollLeft()||0;h+=c(j.containment).scrollTop()||0}this.offset=this.helper.offset();this.position={left:k,top:h};this.size=this._helper?{width:e.outerWidth(),height:e.outerHeight()}:{width:e.width(),height:e.height()};this.originalSize=this._helper?{width:e.outerWidth(),height:e.outerHeight()}:{width:e.width(),height:e.height()};this.originalPosition={left:k,top:h};this.sizeDiff={width:e.outerWidth()-e.width(),height:e.outerHeight()-e.height()};this.originalMousePosition={left:g.pageX,top:g.pageY};this.aspectRatio=(typeof j.aspectRatio=="number")?j.aspectRatio:((this.originalSize.width/this.originalSize.height)||1);var i=c(".ui-resizable-"+this.axis).css("cursor");c("body").css("cursor",i=="auto"?this.axis+"-resize":i);e.addClass("ui-resizable-resizing");this._propagate("start",g);return true},_mouseDrag:function(e){var h=this.helper,g=this.options,m={},q=this,j=this.originalMousePosition,n=this.axis;var r=(e.pageX-j.left)||0,p=(e.pageY-j.top)||0;var i=this._change[n];if(!i){return false}var l=i.apply(this,[e,r,p]),k=c.browser.msie&&c.browser.version<7,f=this.sizeDiff;if(this._aspectRatio||e.shiftKey){l=this._updateRatio(l,e)}l=this._respectSize(l,e);this._propagate("resize",e);h.css({top:this.position.top+"px",left:this.position.left+"px",width:this.size.width+"px",height:this.size.height+"px"});if(!this._helper&&this._proportionallyResizeElements.length){this._proportionallyResize()}this._updateCache(l);this._trigger("resize",e,this.ui());return false},_mouseStop:function(h){this.resizing=false;var i=this.options,m=this;if(this._helper){var g=this._proportionallyResizeElements,e=g.length&&(/textarea/i).test(g[0].nodeName),f=e&&c.ui.hasScroll(g[0],"left")?0:m.sizeDiff.height,k=e?0:m.sizeDiff.width;var n={width:(m.size.width-k),height:(m.size.height-f)},j=(parseInt(m.element.css("left"),10)+(m.position.left-m.originalPosition.left))||null,l=(parseInt(m.element.css("top"),10)+(m.position.top-m.originalPosition.top))||null;if(!i.animate){this.element.css(c.extend(n,{top:l,left:j}))}m.helper.height(m.size.height);m.helper.width(m.size.width);if(this._helper&&!i.animate){this._proportionallyResize()}}c("body").css("cursor","auto");this.element.removeClass("ui-resizable-resizing");this._propagate("stop",h);if(this._helper){this.helper.remove()}return false},_updateCache:function(e){var f=this.options;this.offset=this.helper.offset();if(a(e.left)){this.position.left=e.left}if(a(e.top)){this.position.top=e.top}if(a(e.height)){this.size.height=e.height}if(a(e.width)){this.size.width=e.width}},_updateRatio:function(h,g){var i=this.options,j=this.position,f=this.size,e=this.axis;if(h.height){h.width=(f.height*this.aspectRatio)}else{if(h.width){h.height=(f.width/this.aspectRatio)}}if(e=="sw"){h.left=j.left+(f.width-h.width);h.top=null}if(e=="nw"){h.top=j.top+(f.height-h.height);h.left=j.left+(f.width-h.width)}return h},_respectSize:function(l,g){var j=this.helper,i=this.options,r=this._aspectRatio||g.shiftKey,q=this.axis,u=a(l.width)&&i.maxWidth&&(i.maxWidth<l.width),m=a(l.height)&&i.maxHeight&&(i.maxHeight<l.height),h=a(l.width)&&i.minWidth&&(i.minWidth>l.width),s=a(l.height)&&i.minHeight&&(i.minHeight>l.height);if(h){l.width=i.minWidth}if(s){l.height=i.minHeight}if(u){l.width=i.maxWidth}if(m){l.height=i.maxHeight}var f=this.originalPosition.left+this.originalSize.width,p=this.position.top+this.size.height;var k=/sw|nw|w/.test(q),e=/nw|ne|n/.test(q);if(h&&k){l.left=f-i.minWidth}if(u&&k){l.left=f-i.maxWidth}if(s&&e){l.top=p-i.minHeight}if(m&&e){l.top=p-i.maxHeight}var n=!l.width&&!l.height;if(n&&!l.left&&l.top){l.top=null}else{if(n&&!l.top&&l.left){l.left=null}}return l},_proportionallyResize:function(){var k=this.options;if(!this._proportionallyResizeElements.length){return}var g=this.helper||this.element;for(var f=0;f<this._proportionallyResizeElements.length;f++){var h=this._proportionallyResizeElements[f];if(!this.borderDif){var e=[h.css("borderTopWidth"),h.css("borderRightWidth"),h.css("borderBottomWidth"),h.css("borderLeftWidth")],j=[h.css("paddingTop"),h.css("paddingRight"),h.css("paddingBottom"),h.css("paddingLeft")];this.borderDif=c.map(e,function(l,n){var m=parseInt(l,10)||0,o=parseInt(j[n],10)||0;return m+o})}if(c.browser.msie&&!(!(c(g).is(":hidden")||c(g).parents(":hidden").length))){continue}h.css({height:(g.height()-this.borderDif[0]-this.borderDif[2])||0,width:(g.width()-this.borderDif[1]-this.borderDif[3])||0})}},_renderProxy:function(){var f=this.element,i=this.options;this.elementOffset=f.offset();if(this._helper){this.helper=this.helper||c('<div style="overflow:hidden;"></div>');var e=c.browser.msie&&c.browser.version<7,g=(e?1:0),h=(e?2:-1);this.helper.addClass(this._helper).css({width:this.element.outerWidth()+h,height:this.element.outerHeight()+h,position:"absolute",left:this.elementOffset.left-g+"px",top:this.elementOffset.top-g+"px",zIndex:++i.zIndex});this.helper.appendTo("body").disableSelection()}else{this.helper=this.element}},_change:{e:function(g,f,e){return{width:this.originalSize.width+f}},w:function(h,f,e){var j=this.options,g=this.originalSize,i=this.originalPosition;return{left:i.left+f,width:g.width-f}},n:function(h,f,e){var j=this.options,g=this.originalSize,i=this.originalPosition;return{top:i.top+e,height:g.height-e}},s:function(g,f,e){return{height:this.originalSize.height+e}},se:function(g,f,e){return c.extend(this._change.s.apply(this,arguments),this._change.e.apply(this,[g,f,e]))},sw:function(g,f,e){return c.extend(this._change.s.apply(this,arguments),this._change.w.apply(this,[g,f,e]))},ne:function(g,f,e){return c.extend(this._change.n.apply(this,arguments),this._change.e.apply(this,[g,f,e]))},nw:function(g,f,e){return c.extend(this._change.n.apply(this,arguments),this._change.w.apply(this,[g,f,e]))}},_propagate:function(f,e){c.ui.plugin.call(this,f,[e,this.ui()]);(f!="resize"&&this._trigger(f,e,this.ui()))},plugins:{},ui:function(){return{originalElement:this.originalElement,element:this.element,helper:this.helper,position:this.position,size:this.size,originalSize:this.originalSize,originalPosition:this.originalPosition}}});c.extend(c.ui.resizable,{version:"1.9m3"});c.ui.plugin.add("resizable","alsoResize",{start:function(f,g){var e=c(this).data("resizable"),i=e.options;var h=function(j){c(j).each(function(){var k=c(this);k.data("resizable-alsoresize",{width:parseInt(k.width(),10),height:parseInt(k.height(),10),left:parseInt(k.css("left"),10),top:parseInt(k.css("top"),10),position:k.css("position")})})};if(typeof(i.alsoResize)=="object"&&!i.alsoResize.parentNode){if(i.alsoResize.length){i.alsoResize=i.alsoResize[0];h(i.alsoResize)}else{c.each(i.alsoResize,function(j){h(j)})}}else{h(i.alsoResize)}},resize:function(g,i){var f=c(this).data("resizable"),j=f.options,h=f.originalSize,l=f.originalPosition;var k={height:(f.size.height-h.height)||0,width:(f.size.width-h.width)||0,top:(f.position.top-l.top)||0,left:(f.position.left-l.left)||0},e=function(m,n){c(m).each(function(){var q=c(this),r=c(this).data("resizable-alsoresize"),p={},o=n&&n.length?n:q.parents(i.originalElement[0]).length?["width","height"]:["width","height","top","left"];c.each(o,function(s,v){var u=(r[v]||0)+(k[v]||0);if(u&&u>=0){p[v]=u||null}});if(c.browser.opera&&/relative/.test(q.css("position"))){f._revertToRelativePosition=true;q.css({position:"absolute",top:"auto",left:"auto"})}q.css(p)})};if(typeof(j.alsoResize)=="object"&&!j.alsoResize.nodeType){c.each(j.alsoResize,function(m,n){e(m,n)})}else{e(j.alsoResize)}},stop:function(g,h){var f=c(this).data("resizable"),i=f.options;var e=function(j){c(j).each(function(){var k=c(this);k.css({position:k.data("resizable-alsoresize").position})})};if(f._revertToRelativePosition){f._revertToRelativePosition=false;if(typeof(i.alsoResize)=="object"&&!i.alsoResize.nodeType){c.each(i.alsoResize,function(j){e(j)})}else{e(i.alsoResize)}}c(this).removeData("resizable-alsoresize")}});c.ui.plugin.add("resizable","animate",{stop:function(i,n){var p=c(this).data("resizable"),j=p.options;var h=p._proportionallyResizeElements,e=h.length&&(/textarea/i).test(h[0].nodeName),f=e&&c.ui.hasScroll(h[0],"left")?0:p.sizeDiff.height,l=e?0:p.sizeDiff.width;var g={width:(p.size.width-l),height:(p.size.height-f)},k=(parseInt(p.element.css("left"),10)+(p.position.left-p.originalPosition.left))||null,m=(parseInt(p.element.css("top"),10)+(p.position.top-p.originalPosition.top))||null;p.element.animate(c.extend(g,m&&k?{top:m,left:k}:{}),{duration:j.animateDuration,easing:j.animateEasing,step:function(){var o={width:parseInt(p.element.css("width"),10),height:parseInt(p.element.css("height"),10),top:parseInt(p.element.css("top"),10),left:parseInt(p.element.css("left"),10)};if(h&&h.length){c(h[0]).css({width:o.width,height:o.height})}p._updateCache(o);p._propagate("resize",i)}})}});c.ui.plugin.add("resizable","containment",{start:function(f,r){var u=c(this).data("resizable"),j=u.options,l=u.element;var g=j.containment,k=(g instanceof c)?g.get(0):(/parent/.test(g))?l.parent().get(0):g;if(!k){return}u.containerElement=c(k);if(/document/.test(g)||g==document){u.containerOffset={left:0,top:0};u.containerPosition={left:0,top:0};u.parentData={element:c(document),left:0,top:0,width:c(document).width(),height:c(document).height()||document.body.parentNode.scrollHeight}}else{var n=c(k),i=[];c(["Top","Right","Left","Bottom"]).each(function(p,o){i[p]=b(n.css("padding"+o))});u.containerOffset=n.offset();u.containerPosition=n.position();u.containerSize={height:(n.innerHeight()-i[3]),width:(n.innerWidth()-i[1])};var q=u.containerOffset,e=u.containerSize.height,m=u.containerSize.width,h=(c.ui.hasScroll(k,"left")?k.scrollWidth:m),s=(c.ui.hasScroll(k)?k.scrollHeight:e);u.parentData={element:k,left:q.left,top:q.top,width:h,height:s}}},resize:function(g,q){var u=c(this).data("resizable"),i=u.options,f=u.containerSize,p=u.containerOffset,m=u.size,n=u.position,r=u._aspectRatio||g.shiftKey,e={top:0,left:0},h=u.containerElement;if(h[0]!=document&&(/static/).test(h.css("position"))){e=p}if(n.left<(u._helper?p.left:0)){u.size.width=u.size.width+(u._helper?(u.position.left-p.left):(u.position.left-e.left));if(r){u.size.height=u.size.width/i.aspectRatio}u.position.left=i.helper?p.left:0}if(n.top<(u._helper?p.top:0)){u.size.height=u.size.height+(u._helper?(u.position.top-p.top):u.position.top);if(r){u.size.width=u.size.height*i.aspectRatio}u.position.top=u._helper?p.top:0}u.offset.left=u.parentData.left+u.position.left;u.offset.top=u.parentData.top+u.position.top;var l=Math.abs((u._helper?u.offset.left-e.left:(u.offset.left-e.left))+u.sizeDiff.width),s=Math.abs((u._helper?u.offset.top-e.top:(u.offset.top-p.top))+u.sizeDiff.height);var k=u.containerElement.get(0)==u.element.parent().get(0),j=/relative|absolute/.test(u.containerElement.css("position"));if(k&&j){l-=u.parentData.left}if(l+u.size.width>=u.parentData.width){u.size.width=u.parentData.width-l;if(r){u.size.height=u.size.width/u.aspectRatio}}if(s+u.size.height>=u.parentData.height){u.size.height=u.parentData.height-s;if(r){u.size.width=u.size.height*u.aspectRatio}}},stop:function(f,n){var q=c(this).data("resizable"),g=q.options,l=q.position,m=q.containerOffset,e=q.containerPosition,i=q.containerElement;var j=c(q.helper),r=j.offset(),p=j.outerWidth()-q.sizeDiff.width,k=j.outerHeight()-q.sizeDiff.height;if(q._helper&&!g.animate&&(/relative/).test(i.css("position"))){c(this).css({left:r.left-e.left-m.left,width:p,height:k})}if(q._helper&&!g.animate&&(/static/).test(i.css("position"))){c(this).css({left:r.left-e.left-m.left,width:p,height:k})}}});c.ui.plugin.add("resizable","ghost",{start:function(g,h){var e=c(this).data("resizable"),i=e.options,f=e.size;e.ghost=e.originalElement.clone();e.ghost.css({opacity:0.25,display:"block",position:"relative",height:f.height,width:f.width,margin:0,left:0,top:0}).addClass("ui-resizable-ghost").addClass(typeof i.ghost=="string"?i.ghost:"");e.ghost.appendTo(e.helper)},resize:function(f,g){var e=c(this).data("resizable"),h=e.options;if(e.ghost){e.ghost.css({position:"relative",height:e.size.height,width:e.size.width})}},stop:function(f,g){var e=c(this).data("resizable"),h=e.options;if(e.ghost&&e.helper){e.helper.get(0).removeChild(e.ghost.get(0))}}});c.ui.plugin.add("resizable","grid",{resize:function(e,m){var p=c(this).data("resizable"),h=p.options,k=p.size,i=p.originalSize,j=p.originalPosition,n=p.axis,l=h._aspectRatio||e.shiftKey;h.grid=typeof h.grid=="number"?[h.grid,h.grid]:h.grid;var g=Math.round((k.width-i.width)/(h.grid[0]||1))*(h.grid[0]||1),f=Math.round((k.height-i.height)/(h.grid[1]||1))*(h.grid[1]||1);if(/^(se|s|e)$/.test(n)){p.size.width=i.width+g;p.size.height=i.height+f}else{if(/^(ne)$/.test(n)){p.size.width=i.width+g;p.size.height=i.height+f;p.position.top=j.top-f}else{if(/^(sw)$/.test(n)){p.size.width=i.width+g;p.size.height=i.height+f;p.position.left=j.left-g}else{p.size.width=i.width+g;p.size.height=i.height+f;p.position.top=j.top-f;p.position.left=j.left-g}}}}});var b=function(e){return parseInt(e,10)||0};var a=function(e){return !isNaN(parseInt(e,10))}})(jQuery);(function(a,b){a.widget("ui.selectable",a.ui.mouse,{options:{appendTo:"body",autoRefresh:true,distance:0,filter:"*",tolerance:"touch"},_create:function(){var c=this;this.element.addClass("ui-selectable");this.dragged=false;var d;this.refresh=function(){d=a(c.options.filter,c.element[0]);d.each(function(){var e=a(this);var f=e.offset();a.data(this,"selectable-item",{element:this,$element:e,left:f.left,top:f.top,right:f.left+e.outerWidth(),bottom:f.top+e.outerHeight(),startselected:false,selected:e.hasClass("ui-selected"),selecting:e.hasClass("ui-selecting"),unselecting:e.hasClass("ui-unselecting")})})};this.refresh();this.selectees=d.addClass("ui-selectee");this._mouseInit();this.helper=a("<div class='ui-selectable-helper'></div>")},destroy:function(){this.selectees.removeClass("ui-selectee").removeData("selectable-item");this.element.removeClass("ui-selectable ui-selectable-disabled").removeData("selectable").unbind(".selectable");this._mouseDestroy();return this},_mouseStart:function(e){var c=this;this.opos=[e.pageX,e.pageY];if(this.options.disabled){return}var d=this.options;this.selectees=a(d.filter,this.element[0]);this._trigger("start",e);a(d.appendTo).append(this.helper);this.helper.css({left:e.clientX,top:e.clientY,width:0,height:0});if(d.autoRefresh){this.refresh()}this.selectees.filter(".ui-selected").each(function(){var f=a.data(this,"selectable-item");f.startselected=true;if(!e.metaKey){f.$element.removeClass("ui-selected");f.selected=false;f.$element.addClass("ui-unselecting");f.unselecting=true;c._trigger("unselecting",e,{unselecting:f.element})}});a(e.target).parents().andSelf().each(function(){var g=a.data(this,"selectable-item");if(g){var f=!e.metaKey||!g.$element.hasClass("ui-selected");g.$element.removeClass(f?"ui-unselecting":"ui-selected").addClass(f?"ui-selecting":"ui-unselecting");g.unselecting=!f;g.selecting=f;g.selected=f;if(f){c._trigger("selecting",e,{selecting:g.element})}else{c._trigger("unselecting",e,{unselecting:g.element})}return false}})},_mouseDrag:function(j){var d=this;this.dragged=true;if(this.options.disabled){return}var f=this.options;var e=this.opos[0],i=this.opos[1],c=j.pageX,h=j.pageY;if(e>c){var g=c;c=e;e=g}if(i>h){var g=h;h=i;i=g}this.helper.css({left:e,top:i,width:c-e,height:h-i});this.selectees.each(function(){var k=a.data(this,"selectable-item");if(!k||k.element==d.element[0]){return}var l=false;if(f.tolerance=="touch"){l=(!(k.left>c||k.right<e||k.top>h||k.bottom<i))}else{if(f.tolerance=="fit"){l=(k.left>e&&k.right<c&&k.top>i&&k.bottom<h)}}if(l){if(k.selected){k.$element.removeClass("ui-selected");k.selected=false}if(k.unselecting){k.$element.removeClass("ui-unselecting");k.unselecting=false}if(!k.selecting){k.$element.addClass("ui-selecting");k.selecting=true;d._trigger("selecting",j,{selecting:k.element})}}else{if(k.selecting){if(j.metaKey&&k.startselected){k.$element.removeClass("ui-selecting");k.selecting=false;k.$element.addClass("ui-selected");k.selected=true}else{k.$element.removeClass("ui-selecting");k.selecting=false;if(k.startselected){k.$element.addClass("ui-unselecting");k.unselecting=true}d._trigger("unselecting",j,{unselecting:k.element})}}if(k.selected){if(!j.metaKey&&!k.startselected){k.$element.removeClass("ui-selected");k.selected=false;k.$element.addClass("ui-unselecting");k.unselecting=true;d._trigger("unselecting",j,{unselecting:k.element})}}}});return false},_mouseStop:function(e){var c=this;this.dragged=false;var d=this.options;a(".ui-unselecting",this.element[0]).each(function(){var f=a.data(this,"selectable-item");f.$element.removeClass("ui-unselecting");f.unselecting=false;f.startselected=false;c._trigger("unselected",e,{unselected:f.element})});a(".ui-selecting",this.element[0]).each(function(){var f=a.data(this,"selectable-item");f.$element.removeClass("ui-selecting").addClass("ui-selected");f.selecting=false;f.selected=true;f.startselected=true;c._trigger("selected",e,{selected:f.element})});this._trigger("stop",e);this.helper.remove();return false}});a.extend(a.ui.selectable,{version:"1.9m3"})})(jQuery);(function(a,b){a.widget("ui.sortable",a.ui.mouse,{widgetEventPrefix:"sort",options:{appendTo:"parent",axis:false,connectWith:false,containment:false,cursor:"auto",cursorAt:false,dropOnEmpty:true,forcePlaceholderSize:false,forceHelperSize:false,grid:false,handle:false,helper:"original",items:"> *",opacity:false,placeholder:false,revert:false,scroll:true,scrollSensitivity:20,scrollSpeed:20,scope:"default",tolerance:"intersect",zIndex:1000},_create:function(){var c=this.options;this.containerCache={};this.element.addClass("ui-sortable");this.refresh();this.floating=this.items.length?(/left|right/).test(this.items[0].item.css("float")):false;this.offset=this.element.offset();this._mouseInit()},destroy:function(){this.element.removeClass("ui-sortable ui-sortable-disabled").removeData("sortable").unbind(".sortable");this._mouseDestroy();for(var c=this.items.length-1;c>=0;c--){this.items[c].item.removeData("sortable-item")}return this},_setOption:function(c,d){if(c==="disabled"){this.options[c]=d;this.widget()[d?"addClass":"removeClass"]("ui-sortable-disabled")}else{this._superApply("_setOption",arguments)}},_mouseCapture:function(f,g){if(this.reverting){return false}if(this.options.disabled||this.options.type=="static"){return false}this._refreshItems(f);var e=null,d=this,c=a(f.target).parents().each(function(){if(a.data(this,"sortable-item")==d){e=a(this);return false}});if(a.data(f.target,"sortable-item")==d){e=a(f.target)}if(!e){return false}if(this.options.handle&&!g){var h=false;a(this.options.handle,e).find("*").andSelf().each(function(){if(this==f.target){h=true}});if(!h){return false}}this.currentItem=e;this._removeCurrentsFromItems();return true},_mouseStart:function(f,g,c){var h=this.options,d=this;this.currentContainer=this;this.refreshPositions();this.helper=this._createHelper(f);this._cacheHelperProportions();this._cacheMargins();this.scrollParent=this.helper.scrollParent();this.offset=this.currentItem.offset();this.offset={top:this.offset.top-this.margins.top,left:this.offset.left-this.margins.left};this.helper.css("position","absolute");this.cssPosition=this.helper.css("position");a.extend(this.offset,{click:{left:f.pageX-this.offset.left,top:f.pageY-this.offset.top},parent:this._getParentOffset(),relative:this._getRelativeOffset()});this.originalPosition=this._generatePosition(f);this.originalPageX=f.pageX;this.originalPageY=f.pageY;(h.cursorAt&&this._adjustOffsetFromHelper(h.cursorAt));this.domPosition={prev:this.currentItem.prev()[0],parent:this.currentItem.parent()[0]};if(this.helper[0]!=this.currentItem[0]){this.currentItem.hide()}this._createPlaceholder();if(h.containment){this._setContainment()}if(h.cursor){if(a("body").css("cursor")){this._storedCursor=a("body").css("cursor")}a("body").css("cursor",h.cursor)}if(h.opacity){if(this.helper.css("opacity")){this._storedOpacity=this.helper.css("opacity")}this.helper.css("opacity",h.opacity)}if(h.zIndex){if(this.helper.css("zIndex")){this._storedZIndex=this.helper.css("zIndex")}this.helper.css("zIndex",h.zIndex)}if(this.scrollParent[0]!=document&&this.scrollParent[0].tagName!="HTML"){this.overflowOffset=this.scrollParent.offset()}this._trigger("start",f,this._uiHash());if(!this._preserveHelperProportions){this._cacheHelperProportions()}if(!c){for(var e=this.containers.length-1;e>=0;e--){this.containers[e]._trigger("activate",f,d._uiHash(this))}}if(a.ui.ddmanager){a.ui.ddmanager.current=this}if(a.ui.ddmanager&&!h.dropBehaviour){a.ui.ddmanager.prepareOffsets(this,f)}this.dragging=true;this.helper.addClass("ui-sortable-helper");this._mouseDrag(f);return true},_mouseDrag:function(g){this.position=this._generatePosition(g);this.positionAbs=this._convertPositionTo("absolute");if(!this.lastPositionAbs){this.lastPositionAbs=this.positionAbs}if(this.options.scroll){var h=this.options,c=false;if(this.scrollParent[0]!=document&&this.scrollParent[0].tagName!="HTML"){if((this.overflowOffset.top+this.scrollParent[0].offsetHeight)-g.pageY<h.scrollSensitivity){this.scrollParent[0].scrollTop=c=this.scrollParent[0].scrollTop+h.scrollSpeed}else{if(g.pageY-this.overflowOffset.top<h.scrollSensitivity){this.scrollParent[0].scrollTop=c=this.scrollParent[0].scrollTop-h.scrollSpeed}}if((this.overflowOffset.left+this.scrollParent[0].offsetWidth)-g.pageX<h.scrollSensitivity){this.scrollParent[0].scrollLeft=c=this.scrollParent[0].scrollLeft+h.scrollSpeed}else{if(g.pageX-this.overflowOffset.left<h.scrollSensitivity){this.scrollParent[0].scrollLeft=c=this.scrollParent[0].scrollLeft-h.scrollSpeed}}}else{if(g.pageY-a(document).scrollTop()<h.scrollSensitivity){c=a(document).scrollTop(a(document).scrollTop()-h.scrollSpeed)}else{if(a(window).height()-(g.pageY-a(document).scrollTop())<h.scrollSensitivity){c=a(document).scrollTop(a(document).scrollTop()+h.scrollSpeed)}}if(g.pageX-a(document).scrollLeft()<h.scrollSensitivity){c=a(document).scrollLeft(a(document).scrollLeft()-h.scrollSpeed)}else{if(a(window).width()-(g.pageX-a(document).scrollLeft())<h.scrollSensitivity){c=a(document).scrollLeft(a(document).scrollLeft()+h.scrollSpeed)}}}if(c!==false&&a.ui.ddmanager&&!h.dropBehaviour){a.ui.ddmanager.prepareOffsets(this,g)}}this.positionAbs=this._convertPositionTo("absolute");if(!this.options.axis||this.options.axis!="y"){this.helper[0].style.left=this.position.left+"px"}if(!this.options.axis||this.options.axis!="x"){this.helper[0].style.top=this.position.top+"px"}for(var e=this.items.length-1;e>=0;e--){var f=this.items[e],d=f.item[0],j=this._intersectsWithPointer(f);if(!j){continue}if(d!=this.currentItem[0]&&this.placeholder[j==1?"next":"prev"]()[0]!=d&&!a.ui.contains(this.placeholder[0],d)&&(this.options.type=="semi-dynamic"?!a.ui.contains(this.element[0],d):true)){this.direction=j==1?"down":"up";if(this.options.tolerance=="pointer"||this._intersectsWithSides(f)){this._rearrange(g,f)}else{break}this._trigger("change",g,this._uiHash());break}}this._contactContainers(g);if(a.ui.ddmanager){a.ui.ddmanager.drag(this,g)}this._trigger("sort",g,this._uiHash());this.lastPositionAbs=this.positionAbs;return false},_mouseStop:function(d,e){if(!d){return}if(a.ui.ddmanager&&!this.options.dropBehaviour){a.ui.ddmanager.drop(this,d)}if(this.options.revert){var c=this;var f=c.placeholder.offset();c.reverting=true;a(this.helper).animate({left:f.left-this.offset.parent.left-c.margins.left+(this.offsetParent[0]==document.body?0:this.offsetParent[0].scrollLeft),top:f.top-this.offset.parent.top-c.margins.top+(this.offsetParent[0]==document.body?0:this.offsetParent[0].scrollTop)},parseInt(this.options.revert,10)||500,function(){c._clear(d)})}else{this._clear(d,e)}return false},cancel:function(){var c=this;if(this.dragging){this._mouseUp();if(this.options.helper=="original"){this.currentItem.css(this._storedCSS).removeClass("ui-sortable-helper")}else{this.currentItem.show()}for(var d=this.containers.length-1;d>=0;d--){this.containers[d]._trigger("deactivate",null,c._uiHash(this));if(this.containers[d].containerCache.over){this.containers[d]._trigger("out",null,c._uiHash(this));this.containers[d].containerCache.over=0}}}if(this.placeholder[0].parentNode){this.placeholder[0].parentNode.removeChild(this.placeholder[0])}if(this.options.helper!="original"&&this.helper&&this.helper[0].parentNode){this.helper.remove()}a.extend(this,{helper:null,dragging:false,reverting:false,_noFinalSort:null});if(this.domPosition.prev){a(this.domPosition.prev).after(this.currentItem)}else{a(this.domPosition.parent).prepend(this.currentItem)}return this},serialize:function(e){var c=this._getItemsAsjQuery(e&&e.connected);var d=[];e=e||{};a(c).each(function(){var f=(a(e.item||this).attr(e.attribute||"id")||"").match(e.expression||(/(.+)[-=_](.+)/));if(f){d.push((e.key||f[1]+"[]")+"="+(e.key&&e.expression?f[1]:f[2]))}});if(!d.length&&e.key){d.push(e.key+"=")}return d.join("&")},toArray:function(e){var c=this._getItemsAsjQuery(e&&e.connected);var d=[];e=e||{};c.each(function(){d.push(a(e.item||this).attr(e.attribute||"id")||"")});return d},_intersectsWith:function(m){var e=this.positionAbs.left,d=e+this.helperProportions.width,k=this.positionAbs.top,j=k+this.helperProportions.height;var f=m.left,c=f+m.width,n=m.top,i=n+m.height;var o=this.offset.click.top,h=this.offset.click.left;var g=(k+o)>n&&(k+o)<i&&(e+h)>f&&(e+h)<c;if(this.options.tolerance=="pointer"||this.options.forcePointerForContainers||(this.options.tolerance!="pointer"&&this.helperProportions[this.floating?"width":"height"]>m[this.floating?"width":"height"])){return g}else{return(f<e+(this.helperProportions.width/2)&&d-(this.helperProportions.width/2)<c&&n<k+(this.helperProportions.height/2)&&j-(this.helperProportions.height/2)<i)}},_intersectsWithPointer:function(e){var f=a.ui.isOverAxis(this.positionAbs.top+this.offset.click.top,e.top,e.height),d=a.ui.isOverAxis(this.positionAbs.left+this.offset.click.left,e.left,e.width),h=f&&d,c=this._getDragVerticalDirection(),g=this._getDragHorizontalDirection();if(!h){return false}return this.floating?(((g&&g=="right")||c=="down")?2:1):(c&&(c=="down"?2:1))},_intersectsWithSides:function(f){var d=a.ui.isOverAxis(this.positionAbs.top+this.offset.click.top,f.top+(f.height/2),f.height),e=a.ui.isOverAxis(this.positionAbs.left+this.offset.click.left,f.left+(f.width/2),f.width),c=this._getDragVerticalDirection(),g=this._getDragHorizontalDirection();if(this.floating&&g){return((g=="right"&&e)||(g=="left"&&!e))}else{return c&&((c=="down"&&d)||(c=="up"&&!d))}},_getDragVerticalDirection:function(){var c=this.positionAbs.top-this.lastPositionAbs.top;return c!=0&&(c>0?"down":"up")},_getDragHorizontalDirection:function(){var c=this.positionAbs.left-this.lastPositionAbs.left;return c!=0&&(c>0?"right":"left")},refresh:function(c){this._refreshItems(c);this.refreshPositions();return this},_connectWith:function(){var c=this.options;return c.connectWith.constructor==String?[c.connectWith]:c.connectWith},_getItemsAsjQuery:function(c){var m=this;var h=[];var f=[];var k=this._connectWith();if(k&&c){for(var e=k.length-1;e>=0;e--){var l=a(k[e]);for(var d=l.length-1;d>=0;d--){var g=a.data(l[d],"sortable");if(g&&g!=this&&!g.options.disabled){f.push([a.isFunction(g.options.items)?g.options.items.call(g.element):a(g.options.items,g.element).not(".ui-sortable-helper").not(".ui-sortable-placeholder"),g])}}}}f.push([a.isFunction(this.options.items)?this.options.items.call(this.element,null,{options:this.options,item:this.currentItem}):a(this.options.items,this.element).not(".ui-sortable-helper").not(".ui-sortable-placeholder"),this]);for(var e=f.length-1;e>=0;e--){f[e][0].each(function(){h.push(this)})}return a(h)},_removeCurrentsFromItems:function(){var e=this.currentItem.find(":data(sortable-item)");for(var d=0;d<this.items.length;d++){for(var c=0;c<e.length;c++){if(e[c]==this.items[d].item[0]){this.items.splice(d,1)}}}},_refreshItems:function(c){this.items=[];this.containers=[this];var k=this.items;var q=this;var g=[[a.isFunction(this.options.items)?this.options.items.call(this.element[0],c,{item:this.currentItem}):a(this.options.items,this.element),this]];var m=this._connectWith();if(m){for(var f=m.length-1;f>=0;f--){var n=a(m[f]);for(var e=n.length-1;e>=0;e--){var h=a.data(n[e],"sortable");if(h&&h!=this&&!h.options.disabled){g.push([a.isFunction(h.options.items)?h.options.items.call(h.element[0],c,{item:this.currentItem}):a(h.options.items,h.element),h]);this.containers.push(h)}}}}for(var f=g.length-1;f>=0;f--){var l=g[f][1];var d=g[f][0];for(var e=0,o=d.length;e<o;e++){var p=a(d[e]);p.data("sortable-item",l);k.push({item:p,instance:l,width:0,height:0,left:0,top:0})}}},refreshPositions:function(c){if(this.offsetParent&&this.helper){this.offset.parent=this._getParentOffset()}for(var e=this.items.length-1;e>=0;e--){var f=this.items[e];var d=this.options.toleranceElement?a(this.options.toleranceElement,f.item):f.item;if(!c){f.width=d.outerWidth();f.height=d.outerHeight()}var g=d.offset();f.left=g.left;f.top=g.top}if(this.options.custom&&this.options.custom.refreshContainers){this.options.custom.refreshContainers.call(this)}else{for(var e=this.containers.length-1;e>=0;e--){var g=this.containers[e].element.offset();this.containers[e].containerCache.left=g.left;this.containers[e].containerCache.top=g.top;this.containers[e].containerCache.width=this.containers[e].element.outerWidth();this.containers[e].containerCache.height=this.containers[e].element.outerHeight()}}return this},_createPlaceholder:function(e){var c=e||this,f=c.options;if(!f.placeholder||f.placeholder.constructor==String){var d=f.placeholder;f.placeholder={element:function(){var g=a(document.createElement(c.currentItem[0].nodeName)).addClass(d||c.currentItem[0].className+" ui-sortable-placeholder").removeClass("ui-sortable-helper")[0];if(!d){g.style.visibility="hidden"}return g},update:function(g,h){if(d&&!f.forcePlaceholderSize){return}if(!h.height()){h.height(c.currentItem.innerHeight()-parseInt(c.currentItem.css("paddingTop")||0,10)-parseInt(c.currentItem.css("paddingBottom")||0,10))}if(!h.width()){h.width(c.currentItem.innerWidth()-parseInt(c.currentItem.css("paddingLeft")||0,10)-parseInt(c.currentItem.css("paddingRight")||0,10))}}}}c.placeholder=a(f.placeholder.element.call(c.element,c.currentItem));c.currentItem.after(c.placeholder);f.placeholder.update(c,c.placeholder)},_contactContainers:function(c){var e=null,l=null;for(var g=this.containers.length-1;g>=0;g--){if(a.ui.contains(this.currentItem[0],this.containers[g].element[0])){continue}if(this._intersectsWith(this.containers[g].containerCache)){if(e&&a.ui.contains(this.containers[g].element[0],e.element[0])){continue}e=this.containers[g];l=g}else{if(this.containers[g].containerCache.over){this.containers[g]._trigger("out",c,this._uiHash(this));this.containers[g].containerCache.over=0}}}if(!e){return}if(this.containers.length===1){this.containers[l]._trigger("over",c,this._uiHash(this));this.containers[l].containerCache.over=1}else{if(this.currentContainer!=this.containers[l]){var k=10000;var h=null;var d=this.positionAbs[this.containers[l].floating?"left":"top"];for(var f=this.items.length-1;f>=0;f--){if(!a.ui.contains(this.containers[l].element[0],this.items[f].item[0])){continue}var m=this.items[f][this.containers[l].floating?"left":"top"];if(Math.abs(m-d)<k){k=Math.abs(m-d);h=this.items[f]}}if(!h&&!this.options.dropOnEmpty){return}this.currentContainer=this.containers[l];h?this._rearrange(c,h,null,true):this._rearrange(c,null,this.containers[l].element,true);this._trigger("change",c,this._uiHash());this.containers[l]._trigger("change",c,this._uiHash(this));this.options.placeholder.update(this.currentContainer,this.placeholder);this.containers[l]._trigger("over",c,this._uiHash(this));this.containers[l].containerCache.over=1}}},_createHelper:function(d){var e=this.options;var c=a.isFunction(e.helper)?a(e.helper.apply(this.element[0],[d,this.currentItem])):(e.helper=="clone"?this.currentItem.clone():this.currentItem);if(!c.parents("body").length){a(e.appendTo!="parent"?e.appendTo:this.currentItem[0].parentNode)[0].appendChild(c[0])}if(c[0]==this.currentItem[0]){this._storedCSS={width:this.currentItem[0].style.width,height:this.currentItem[0].style.height,position:this.currentItem.css("position"),top:this.currentItem.css("top"),left:this.currentItem.css("left")}}if(c[0].style.width==""||e.forceHelperSize){c.width(this.currentItem.width())}if(c[0].style.height==""||e.forceHelperSize){c.height(this.currentItem.height())}return c},_adjustOffsetFromHelper:function(c){if(typeof c=="string"){c=c.split(" ")}if(a.isArray(c)){c={left:+c[0],top:+c[1]||0}}if("left" in c){this.offset.click.left=c.left+this.margins.left}if("right" in c){this.offset.click.left=this.helperProportions.width-c.right+this.margins.left}if("top" in c){this.offset.click.top=c.top+this.margins.top}if("bottom" in c){this.offset.click.top=this.helperProportions.height-c.bottom+this.margins.top}},_getParentOffset:function(){this.offsetParent=this.helper.offsetParent();var c=this.offsetParent.offset();if(this.cssPosition=="absolute"&&this.scrollParent[0]!=document&&a.ui.contains(this.scrollParent[0],this.offsetParent[0])){c.left+=this.scrollParent.scrollLeft();c.top+=this.scrollParent.scrollTop()}if((this.offsetParent[0]==document.body)||(this.offsetParent[0].tagName&&this.offsetParent[0].tagName.toLowerCase()=="html"&&a.browser.msie)){c={top:0,left:0}}return{top:c.top+(parseInt(this.offsetParent.css("borderTopWidth"),10)||0),left:c.left+(parseInt(this.offsetParent.css("borderLeftWidth"),10)||0)}},_getRelativeOffset:function(){if(this.cssPosition=="relative"){var c=this.currentItem.position();return{top:c.top-(parseInt(this.helper.css("top"),10)||0)+this.scrollParent.scrollTop(),left:c.left-(parseInt(this.helper.css("left"),10)||0)+this.scrollParent.scrollLeft()}}else{return{top:0,left:0}}},_cacheMargins:function(){this.margins={left:(parseInt(this.currentItem.css("marginLeft"),10)||0),top:(parseInt(this.currentItem.css("marginTop"),10)||0)}},_cacheHelperProportions:function(){this.helperProportions={width:this.helper.outerWidth(),height:this.helper.outerHeight()}},_setContainment:function(){var f=this.options;if(f.containment=="parent"){f.containment=this.helper[0].parentNode}if(f.containment=="document"||f.containment=="window"){this.containment=[0-this.offset.relative.left-this.offset.parent.left,0-this.offset.relative.top-this.offset.parent.top,a(f.containment=="document"?document:window).width()-this.helperProportions.width-this.margins.left,(a(f.containment=="document"?document:window).height()||document.body.parentNode.scrollHeight)-this.helperProportions.height-this.margins.top]}if(!(/^(document|window|parent)$/).test(f.containment)){var d=a(f.containment)[0];var e=a(f.containment).offset();var c=(a(d).css("overflow")!="hidden");this.containment=[e.left+(parseInt(a(d).css("borderLeftWidth"),10)||0)+(parseInt(a(d).css("paddingLeft"),10)||0)-this.margins.left,e.top+(parseInt(a(d).css("borderTopWidth"),10)||0)+(parseInt(a(d).css("paddingTop"),10)||0)-this.margins.top,e.left+(c?Math.max(d.scrollWidth,d.offsetWidth):d.offsetWidth)-(parseInt(a(d).css("borderLeftWidth"),10)||0)-(parseInt(a(d).css("paddingRight"),10)||0)-this.helperProportions.width-this.margins.left,e.top+(c?Math.max(d.scrollHeight,d.offsetHeight):d.offsetHeight)-(parseInt(a(d).css("borderTopWidth"),10)||0)-(parseInt(a(d).css("paddingBottom"),10)||0)-this.helperProportions.height-this.margins.top]}},_convertPositionTo:function(g,i){if(!i){i=this.position}var e=g=="absolute"?1:-1;var f=this.options,c=this.cssPosition=="absolute"&&!(this.scrollParent[0]!=document&&a.ui.contains(this.scrollParent[0],this.offsetParent[0]))?this.offsetParent:this.scrollParent,h=(/(html|body)/i).test(c[0].tagName);return{top:(i.top+this.offset.relative.top*e+this.offset.parent.top*e-(a.browser.safari&&this.cssPosition=="fixed"?0:(this.cssPosition=="fixed"?-this.scrollParent.scrollTop():(h?0:c.scrollTop()))*e)),left:(i.left+this.offset.relative.left*e+this.offset.parent.left*e-(a.browser.safari&&this.cssPosition=="fixed"?0:(this.cssPosition=="fixed"?-this.scrollParent.scrollLeft():h?0:c.scrollLeft())*e))}},_generatePosition:function(f){var i=this.options,c=this.cssPosition=="absolute"&&!(this.scrollParent[0]!=document&&a.ui.contains(this.scrollParent[0],this.offsetParent[0]))?this.offsetParent:this.scrollParent,j=(/(html|body)/i).test(c[0].tagName);if(this.cssPosition=="relative"&&!(this.scrollParent[0]!=document&&this.scrollParent[0]!=this.offsetParent[0])){this.offset.relative=this._getRelativeOffset()}var e=f.pageX;var d=f.pageY;if(this.originalPosition){if(this.containment){if(f.pageX-this.offset.click.left<this.containment[0]){e=this.containment[0]+this.offset.click.left}if(f.pageY-this.offset.click.top<this.containment[1]){d=this.containment[1]+this.offset.click.top}if(f.pageX-this.offset.click.left>this.containment[2]){e=this.containment[2]+this.offset.click.left}if(f.pageY-this.offset.click.top>this.containment[3]){d=this.containment[3]+this.offset.click.top}}if(i.grid){var h=this.originalPageY+Math.round((d-this.originalPageY)/i.grid[1])*i.grid[1];d=this.containment?(!(h-this.offset.click.top<this.containment[1]||h-this.offset.click.top>this.containment[3])?h:(!(h-this.offset.click.top<this.containment[1])?h-i.grid[1]:h+i.grid[1])):h;var g=this.originalPageX+Math.round((e-this.originalPageX)/i.grid[0])*i.grid[0];e=this.containment?(!(g-this.offset.click.left<this.containment[0]||g-this.offset.click.left>this.containment[2])?g:(!(g-this.offset.click.left<this.containment[0])?g-i.grid[0]:g+i.grid[0])):g}}return{top:(d-this.offset.click.top-this.offset.relative.top-this.offset.parent.top+(a.browser.safari&&this.cssPosition=="fixed"?0:(this.cssPosition=="fixed"?-this.scrollParent.scrollTop():(j?0:c.scrollTop())))),left:(e-this.offset.click.left-this.offset.relative.left-this.offset.parent.left+(a.browser.safari&&this.cssPosition=="fixed"?0:(this.cssPosition=="fixed"?-this.scrollParent.scrollLeft():j?0:c.scrollLeft())))}},_rearrange:function(h,g,d,f){d?d[0].appendChild(this.placeholder[0]):g.item[0].parentNode.insertBefore(this.placeholder[0],(this.direction=="down"?g.item[0]:g.item[0].nextSibling));this.counter=this.counter?++this.counter:1;var e=this,c=this.counter;window.setTimeout(function(){if(c==e.counter){e.refreshPositions(!f)}},0)},_clear:function(e,f){this.reverting=false;var g=[],c=this;if(!this._noFinalSort&&this.currentItem[0].parentNode){this.placeholder.before(this.currentItem)}this._noFinalSort=null;if(this.helper[0]==this.currentItem[0]){for(var d in this._storedCSS){if(this._storedCSS[d]=="auto"||this._storedCSS[d]=="static"){this._storedCSS[d]=""}}this.currentItem.css(this._storedCSS).removeClass("ui-sortable-helper")}else{this.currentItem.show()}if(this.fromOutside&&!f){g.push(function(h){this._trigger("receive",h,this._uiHash(this.fromOutside))})}if((this.fromOutside||this.domPosition.prev!=this.currentItem.prev().not(".ui-sortable-helper")[0]||this.domPosition.parent!=this.currentItem.parent()[0])&&!f){g.push(function(h){this._trigger("update",h,this._uiHash())})}if(!a.ui.contains(this.element[0],this.currentItem[0])){if(!f){g.push(function(h){this._trigger("remove",h,this._uiHash())})}for(var d=this.containers.length-1;d>=0;d--){if(a.ui.contains(this.containers[d].element[0],this.currentItem[0])&&!f){g.push((function(h){return function(i){h._trigger("receive",i,this._uiHash(this))}}).call(this,this.containers[d]));g.push((function(h){return function(i){h._trigger("update",i,this._uiHash(this))}}).call(this,this.containers[d]))}}}for(var d=this.containers.length-1;d>=0;d--){if(!f){g.push((function(h){return function(i){h._trigger("deactivate",i,this._uiHash(this))}}).call(this,this.containers[d]))}if(this.containers[d].containerCache.over){g.push((function(h){return function(i){h._trigger("out",i,this._uiHash(this))}}).call(this,this.containers[d]));this.containers[d].containerCache.over=0}}if(this._storedCursor){a("body").css("cursor",this._storedCursor)}if(this._storedOpacity){this.helper.css("opacity",this._storedOpacity)}if(this._storedZIndex){this.helper.css("zIndex",this._storedZIndex=="auto"?"":this._storedZIndex)}this.dragging=false;if(this.cancelHelperRemoval){if(!f){this._trigger("beforeStop",e,this._uiHash());for(var d=0;d<g.length;d++){g[d].call(this,e)}this._trigger("stop",e,this._uiHash())}return false}if(!f){this._trigger("beforeStop",e,this._uiHash())}this.placeholder[0].parentNode.removeChild(this.placeholder[0]);if(this.helper[0]!=this.currentItem[0]){this.helper.remove()}this.helper=null;if(!f){for(var d=0;d<g.length;d++){g[d].call(this,e)}this._trigger("stop",e,this._uiHash())}this.fromOutside=false;return true},_trigger:function(){if(a.Widget.prototype._trigger.apply(this,arguments)===false){this.cancel()}},_uiHash:function(d){var c=d||this;return{helper:c.helper,placeholder:c.placeholder||a([]),position:c.position,originalPosition:c.originalPosition,offset:c.positionAbs,item:c.currentItem,sender:d?d.element:null}}});a.extend(a.ui.sortable,{version:"1.9m3"})})(jQuery);(function(a,b){a.widget("ui.accordion",{options:{active:0,animated:"slide",autoHeight:true,clearStyle:false,collapsible:false,event:"click",fillSpace:false,header:"> li > :first-child,> :not(li):even",icons:{header:"ui-icon-triangle-1-e",headerSelected:"ui-icon-triangle-1-s"},navigation:false,navigationFilter:function(){return this.href.toLowerCase()===location.href.toLowerCase()}},_create:function(){var c=this,d=c.options;c.running=0;c.element.addClass("ui-accordion ui-widget ui-helper-reset").children("li").addClass("ui-accordion-li-fix");c.headers=c.element.find(d.header).addClass("ui-accordion-header ui-helper-reset ui-state-default ui-corner-all").bind("mouseenter.accordion",function(){if(d.disabled){return}a(this).addClass("ui-state-hover")}).bind("mouseleave.accordion",function(){if(d.disabled){return}a(this).removeClass("ui-state-hover")}).bind("focus.accordion",function(){if(d.disabled){return}a(this).addClass("ui-state-focus")}).bind("blur.accordion",function(){if(d.disabled){return}a(this).removeClass("ui-state-focus")});c.headers.next().addClass("ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom");if(d.navigation){var e=c.element.find("a").filter(d.navigationFilter).eq(0);if(e.length){var f=e.closest(".ui-accordion-header");if(f.length){c.active=f}else{c.active=e.closest(".ui-accordion-content").prev()}}}c.active=c._findActive(c.active||d.active).addClass("ui-state-default ui-state-active").toggleClass("ui-corner-all").toggleClass("ui-corner-top");c.active.next().addClass("ui-accordion-content-active");c._createIcons();c.resize();c.element.attr("role","tablist");c.headers.attr("role","tab").bind("keydown.accordion",function(g){return c._keydown(g)}).next().attr("role","tabpanel");c.headers.not(c.active||"").attr({"aria-expanded":"false",tabIndex:-1}).next().hide();if(!c.active.length){c.headers.eq(0).attr("tabIndex",0)}else{c.active.attr({"aria-expanded":"true",tabIndex:0})}if(!a.browser.safari){c.headers.find("a").attr("tabIndex",-1)}if(d.event){c.headers.bind(d.event.split(" ").join(".accordion ")+".accordion",function(g){c._clickHandler.call(c,g,this);g.preventDefault()})}},_createIcons:function(){var c=this.options;if(c.icons){a("<span></span>").addClass("ui-icon "+c.icons.header).prependTo(this.headers);this.active.children(".ui-icon").toggleClass(c.icons.header).toggleClass(c.icons.headerSelected);this.element.addClass("ui-accordion-icons")}},_destroyIcons:function(){this.headers.children(".ui-icon").remove();this.element.removeClass("ui-accordion-icons")},destroy:function(){var c=this.options;this.element.removeClass("ui-accordion ui-widget ui-helper-reset").removeAttr("role");this.headers.unbind(".accordion").removeClass("ui-accordion-header ui-accordion-disabled ui-helper-reset ui-state-default ui-corner-all ui-state-active ui-state-disabled ui-corner-top").removeAttr("role").removeAttr("aria-expanded").removeAttr("tabIndex");this.headers.find("a").removeAttr("tabIndex");this._destroyIcons();var d=this.headers.next().css("display","").removeAttr("role").removeClass("ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content ui-accordion-content-active ui-accordion-disabled ui-state-disabled");if(c.autoHeight||c.fillHeight){d.css("height","")}return a.Widget.prototype.destroy.call(this)},_setOption:function(c,d){this._superApply("_setOption",arguments);if(c=="active"){this.activate(d)}if(c=="icons"){this._destroyIcons();if(d){this._createIcons()}}if(c=="disabled"){this.headers.add(this.headers.next())[d?"addClass":"removeClass"]("ui-accordion-disabled ui-state-disabled")}},_keydown:function(f){if(this.options.disabled||f.altKey||f.ctrlKey){return}var g=a.ui.keyCode,e=this.headers.length,c=this.headers.index(f.target),d=false;switch(f.keyCode){case g.RIGHT:case g.DOWN:d=this.headers[(c+1)%e];break;case g.LEFT:case g.UP:d=this.headers[(c-1+e)%e];break;case g.SPACE:case g.ENTER:this._clickHandler({target:f.target},f.target);f.preventDefault()}if(d){a(f.target).attr("tabIndex",-1);a(d).attr("tabIndex",0);d.focus();return false}return true},resize:function(){var c=this.options,e;if(c.fillSpace){if(a.browser.msie){var d=this.element.parent().css("overflow");this.element.parent().css("overflow","hidden")}e=this.element.parent().height();if(a.browser.msie){this.element.parent().css("overflow",d)}this.headers.each(function(){e-=a(this).outerHeight(true)});this.headers.next().each(function(){a(this).height(Math.max(0,e-a(this).innerHeight()+a(this).height()))}).css("overflow","auto")}else{if(c.autoHeight){e=0;this.headers.next().each(function(){e=Math.max(e,a(this).height("").height())}).height(e)}}return this},activate:function(c){this.options.active=c;var d=this._findActive(c)[0];this._clickHandler({target:d},d);return this},_findActive:function(c){return c?typeof c==="number"?this.headers.filter(":eq("+c+")"):this.headers.not(this.headers.not(c)):c===false?a([]):this.headers.filter(":eq(0)")},_clickHandler:function(c,f){var k=this.options;if(k.disabled){return}if(!c.target){if(!k.collapsible){return}this.active.removeClass("ui-state-active ui-corner-top").addClass("ui-state-default ui-corner-all").children(".ui-icon").removeClass(k.icons.headerSelected).addClass(k.icons.header);this.active.next().addClass("ui-accordion-content-active");var h=this.active.next(),e={options:k,newHeader:a([]),oldHeader:k.active,newContent:a([]),oldContent:h},d=(this.active=a([]));this._toggle(d,h,e);return}var g=a(c.currentTarget||f),i=g[0]===this.active[0];k.active=k.collapsible&&i?false:this.headers.index(g);if(this.running||(!k.collapsible&&i)){return}this.active.removeClass("ui-state-active ui-corner-top").addClass("ui-state-default ui-corner-all").children(".ui-icon").removeClass(k.icons.headerSelected).addClass(k.icons.header);if(!i){g.removeClass("ui-state-default ui-corner-all").addClass("ui-state-active ui-corner-top").children(".ui-icon").removeClass(k.icons.header).addClass(k.icons.headerSelected);g.next().addClass("ui-accordion-content-active")}var d=g.next(),h=this.active.next(),e={options:k,newHeader:i&&k.collapsible?a([]):g,oldHeader:this.active,newContent:i&&k.collapsible?a([]):d,oldContent:h},j=this.headers.index(this.active[0])>this.headers.index(g[0]);this.active=i?a([]):g;this._toggle(d,h,e,i,j);return},_toggle:function(c,i,g,j,k){var m=this,n=m.options;m.toShow=c;m.toHide=i;m.data=g;var d=function(){if(!m){return}return m._completed.apply(m,arguments)};m._trigger("changestart",null,m.data);m.running=i.size()===0?c.size():i.size();if(n.animated){var f={};if(n.collapsible&&j){f={toShow:a([]),toHide:i,complete:d,down:k,autoHeight:n.autoHeight||n.fillSpace}}else{f={toShow:c,toHide:i,complete:d,down:k,autoHeight:n.autoHeight||n.fillSpace}}if(!n.proxied){n.proxied=n.animated}if(!n.proxiedDuration){n.proxiedDuration=n.duration}n.animated=a.isFunction(n.proxied)?n.proxied(f):n.proxied;n.duration=a.isFunction(n.proxiedDuration)?n.proxiedDuration(f):n.proxiedDuration;var l=a.ui.accordion.animations,e=n.duration,h=n.animated;if(h&&!l[h]&&!a.easing[h]){h="slide"}if(!l[h]){l[h]=function(o){this.slide(o,{easing:h,duration:e||700})}}l[h](f)}else{if(n.collapsible&&j){c.toggle()}else{i.hide();c.show()}d(true)}i.prev().attr({"aria-expanded":"false",tabIndex:-1}).blur();c.prev().attr({"aria-expanded":"true",tabIndex:0}).focus()},_completed:function(c){this.running=c?0:--this.running;if(this.running){return}if(this.options.clearStyle){this.toShow.add(this.toHide).css({height:"",overflow:""})}this.toHide.removeClass("ui-accordion-content-active");this._trigger("change",null,this.data)}});a.extend(a.ui.accordion,{version:"1.9m3",animations:{slide:function(k,i){k=a.extend({easing:"swing",duration:300},k,i);if(!k.toHide.size()){k.toShow.animate({height:"show",paddingTop:"show",paddingBottom:"show"},k);return}if(!k.toShow.size()){k.toHide.animate({height:"hide",paddingTop:"hide",paddingBottom:"hide"},k);return}var d=k.toShow.css("overflow"),h=0,e={},g={},f=["height","paddingTop","paddingBottom"],c;var j=k.toShow;c=j[0].style.width;j.width(parseInt(j.parent().width(),10)-parseInt(j.css("paddingLeft"),10)-parseInt(j.css("paddingRight"),10)-(parseInt(j.css("borderLeftWidth"),10)||0)-(parseInt(j.css("borderRightWidth"),10)||0));a.each(f,function(l,n){g[n]="hide";var m=(""+a.css(k.toShow[0],n)).match(/^([\d+-.]+)(.*)$/);e[n]={value:m[1],unit:m[2]||"px"}});k.toShow.css({height:0,overflow:"hidden"}).show();k.toHide.filter(":hidden").each(k.complete).end().filter(":visible").animate(g,{step:function(l,m){if(m.prop=="height"){h=(m.end-m.start===0)?0:(m.now-m.start)/(m.end-m.start)}k.toShow[0].style[m.prop]=(h*e[m.prop].value)+e[m.prop].unit},duration:k.duration,easing:k.easing,complete:function(){if(!k.autoHeight){k.toShow.css("height","")}k.toShow.css({width:c,overflow:d});k.complete()}})},bounceslide:function(c){this.slide(c,{easing:c.down?"easeOutBounce":"swing",duration:c.down?1000:200})}}})})(jQuery);(function(a,b){a.widget("ui.autocomplete",{options:{appendTo:"body",delay:300,minLength:1,position:{my:"left top",at:"left bottom",collision:"none"},source:null},_create:function(){var c=this,e=this.element[0].ownerDocument,d;this.element.addClass("ui-autocomplete-input").attr("autocomplete","off").attr({role:"textbox","aria-autocomplete":"list","aria-haspopup":"true"}).bind("keydown.autocomplete",function(f){if(c.options.disabled||c.element.attr("readonly")){return}d=false;var g=a.ui.keyCode;switch(f.keyCode){case g.PAGE_UP:c._move("previousPage",f);break;case g.PAGE_DOWN:c._move("nextPage",f);break;case g.UP:c._move("previous",f);f.preventDefault();break;case g.DOWN:c._move("next",f);f.preventDefault();break;case g.ENTER:case g.NUMPAD_ENTER:if(c.menu.active){d=true;f.preventDefault()}case g.TAB:if(!c.menu.active){return}c.menu.select(f);break;case g.ESCAPE:c.element.val(c.term);c.close(f);break;default:clearTimeout(c.searching);c.searching=setTimeout(function(){if(c.term!=c.element.val()){c.selectedItem=null;c.search(null,f)}},c.options.delay);break}}).bind("keypress.autocomplete",function(f){if(d){d=false;f.preventDefault()}}).bind("focus.autocomplete",function(){if(c.options.disabled){return}c.selectedItem=null;c.previous=c.element.val()}).bind("blur.autocomplete",function(f){if(c.options.disabled){return}clearTimeout(c.searching);c.closing=setTimeout(function(){c.close(f);c._change(f)},150)});this._initSource();this.response=function(){return c._response.apply(c,arguments)};this.menu=a("<ul></ul>").addClass("ui-autocomplete").appendTo(a(this.options.appendTo||"body",e)[0]).mousedown(function(f){var g=c.menu.element[0];if(!a(f.target).closest(".ui-menu-item").length){setTimeout(function(){a(document).one("mousedown",function(h){if(h.target!==c.element[0]&&h.target!==g&&!a.ui.contains(g,h.target)){c.close()}})},1)}setTimeout(function(){clearTimeout(c.closing)},13)}).menu({input:a(),focus:function(g,h){var f=h.item.data("item.autocomplete");if(false!==c._trigger("focus",g,{item:f})){if(/^key/.test(g.originalEvent.type)){c.element.val(f.value)}}},select:function(h,i){var g=i.item.data("item.autocomplete"),f=c.previous;if(c.element[0]!==e.activeElement){c.element.focus();c.previous=f;setTimeout(function(){c.previous=f},1)}if(false!==c._trigger("select",h,{item:g})){c.element.val(g.value)}c.term=c.element.val();c.close(h);c.selectedItem=g},blur:function(f,g){if(c.menu.element.is(":visible")&&(c.element.val()!==c.term)){c.element.val(c.term)}}}).zIndex(this.element.zIndex()+1).css({top:0,left:0}).hide().data("menu");if(a.fn.bgiframe){this.menu.element.bgiframe()}},destroy:function(){this.element.removeClass("ui-autocomplete-input").removeAttr("autocomplete").removeAttr("role").removeAttr("aria-autocomplete").removeAttr("aria-haspopup");this.menu.element.remove();this._super("destroy")},_setOption:function(c){this._superApply("_setOption",arguments);if(c==="source"){this._initSource()}if(c==="appendTo"){this.menu.element.appendTo(a(value||"body",this.element[0].ownerDocument)[0])}},_initSource:function(){var c=this,e,d;if(a.isArray(this.options.source)){e=this.options.source;this.source=function(g,f){f(a.ui.autocomplete.filter(e,g.term))}}else{if(typeof this.options.source==="string"){d=this.options.source;this.source=function(g,f){if(c.xhr){c.xhr.abort()}c.xhr=a.getJSON(d,g,function(i,h,j){if(j===c.xhr){f(i)}c.xhr=null})}}else{this.source=this.options.source}}},search:function(d,c){d=d!=null?d:this.element.val();this.term=this.element.val();if(d.length<this.options.minLength){return this.close(c)}clearTimeout(this.closing);if(this._trigger("search",c)===false){return}return this._search(d)},_search:function(c){this.element.addClass("ui-autocomplete-loading");this.source({term:c},this.response)},_response:function(c){if(c&&c.length){c=this._normalize(c);this._suggest(c);this._trigger("open")}else{this.close()}this.element.removeClass("ui-autocomplete-loading")},close:function(c){clearTimeout(this.closing);if(this.menu.element.is(":visible")){this._trigger("close",c);this.menu.element.hide();this.menu.deactivate()}},_change:function(c){if(this.previous!==this.element.val()){this._trigger("change",c,{item:this.selectedItem})}},_normalize:function(c){if(c.length&&c[0].label&&c[0].value){return c}return a.map(c,function(d){if(typeof d==="string"){return{label:d,value:d}}return a.extend({label:d.label||d.value,value:d.value||d.label},d)})},_suggest:function(c){var d=this.menu.element.empty().zIndex(this.element.zIndex()+1);this._renderMenu(d,c);this.menu.deactivate();this.menu.refresh();this.menu.element.show().position(a.extend({of:this.element},this.options.position));this._resizeMenu()},_resizeMenu:function(){var c=this.menu.element;c.outerWidth(Math.max(c.width("").outerWidth(),this.element.outerWidth()))},_renderMenu:function(e,d){var c=this;a.each(d,function(f,g){c._renderItem(e,g)})},_renderItem:function(c,d){return a("<li></li>").data("item.autocomplete",d).append(a("<a></a>").text(d.label)).appendTo(c)},_move:function(d,c){if(!this.menu.element.is(":visible")){this.search(null,c);return}if(this.menu.first()&&/^previous/.test(d)||this.menu.last()&&/^next/.test(d)){this.element.val(this.term);this.menu.deactivate();return}this.menu[d](c)},widget:function(){return this.menu.element}});a.extend(a.ui.autocomplete,{escapeRegex:function(c){return c.replace(/[-[\]{}()*+?.,\\^$|#\s]/g,"\\$&")},filter:function(e,c){var d=new RegExp(a.ui.autocomplete.escapeRegex(c),"i");return a.grep(e,function(f){return d.test(f.label||f.value||f)})}})}(jQuery));(function(e,h){var c,b="ui-button ui-widget ui-state-default ui-corner-all",g="ui-state-hover ui-state-active ",f="ui-button-icons-only ui-button-icon-only ui-button-text-icons ui-button-text-icon-primary ui-button-text-icon-secondary ui-button-text-only",d=function(i){e(":ui-button",i.target.form).each(function(){var j=e(this).data("button");setTimeout(function(){j.refresh()},1)})},a=function(j){var i=j.name,k=j.form,l=e([]);if(i){if(k){l=e(k).find("[name='"+i+"']")}else{l=e("[name='"+i+"']",j.ownerDocument).filter(function(){return !this.form})}}return l};e.widget("ui.button",{options:{disabled:null,text:true,label:null,icons:{primary:null,secondary:null}},_create:function(){this.element.closest("form").unbind("reset.button").bind("reset.button",d);if(typeof this.options.disabled!=="boolean"){this.options.disabled=this.element.attr("disabled")}this._determineButtonType();this.hasTitle=!!this.buttonElement.attr("title");var i=this,k=this.options,l=this.type==="checkbox"||this.type==="radio",m="ui-state-hover"+(!l?" ui-state-active":""),j="ui-state-focus";if(k.label===null){k.label=this.buttonElement.html()}if(this.element.is(":disabled")){k.disabled=true}this.buttonElement.addClass(b).attr("role","button").bind("mouseenter.button",function(){if(k.disabled){return}e(this).addClass("ui-state-hover");if(this===c){e(this).addClass("ui-state-active")}}).bind("mouseleave.button",function(){if(k.disabled){return}e(this).removeClass(m)}).bind("focus.button",function(){e(this).addClass(j)}).bind("blur.button",function(){e(this).removeClass(j)});if(l){this.element.bind("change.button",function(){i.refresh()})}if(this.type==="checkbox"){this.buttonElement.bind("click.button",function(){if(k.disabled){return false}e(this).toggleClass("ui-state-active");i.buttonElement.attr("aria-pressed",i.element[0].checked)})}else{if(this.type==="radio"){this.buttonElement.bind("click.button",function(){if(k.disabled){return false}e(this).addClass("ui-state-active");i.buttonElement.attr("aria-pressed",true);var n=i.element[0];a(n).not(n).map(function(){return e(this).button("widget")[0]}).removeClass("ui-state-active").attr("aria-pressed",false)})}else{this.buttonElement.bind("mousedown.button",function(){if(k.disabled){return false}e(this).addClass("ui-state-active");c=this;e(document).one("mouseup",function(){c=null})}).bind("mouseup.button",function(){if(k.disabled){return false}e(this).removeClass("ui-state-active")}).bind("keydown.button",function(n){if(k.disabled){return false}if(n.keyCode==e.ui.keyCode.SPACE||n.keyCode==e.ui.keyCode.ENTER){e(this).addClass("ui-state-active")}}).bind("keyup.button",function(){e(this).removeClass("ui-state-active")});if(this.buttonElement.is("a")){this.buttonElement.keyup(function(n){if(n.keyCode===e.ui.keyCode.SPACE){e(this).click()}})}}}this._setOption("disabled",k.disabled)},_determineButtonType:function(){if(this.element.is(":checkbox")){this.type="checkbox"}else{if(this.element.is(":radio")){this.type="radio"}else{if(this.element.is("input")){this.type="input"}else{this.type="button"}}}if(this.type==="checkbox"||this.type==="radio"){this.buttonElement=this.element.parents().last().find("label[for="+this.element.attr("id")+"]");this.element.addClass("ui-helper-hidden-accessible");var i=this.element.is(":checked");if(i){this.buttonElement.addClass("ui-state-active")}this.buttonElement.attr("aria-pressed",i)}else{this.buttonElement=this.element}},widget:function(){return this.buttonElement},destroy:function(){this.element.removeClass("ui-helper-hidden-accessible");this.buttonElement.removeClass(b+" "+g+" "+f).removeAttr("role").removeAttr("aria-pressed").html(this.buttonElement.find(".ui-button-text").html());if(!this.hasTitle){this.buttonElement.removeAttr("title")}this._super("destroy")},_setOption:function(i,j){this._superApply("_setOption",arguments);if(i==="disabled"){if(j){this.element.attr("disabled",true)}else{this.element.removeAttr("disabled")}}this._resetButton()},refresh:function(){var i=this.element.is(":disabled");if(i!==this.options.disabled){this._setOption("disabled",i)}if(this.type==="radio"){a(this.element[0]).each(function(){if(e(this).is(":checked")){e(this).button("widget").addClass("ui-state-active").attr("aria-pressed",true)}else{e(this).button("widget").removeClass("ui-state-active").attr("aria-pressed",false)}})}else{if(this.type==="checkbox"){if(this.element.is(":checked")){this.buttonElement.addClass("ui-state-active").attr("aria-pressed",true)}else{this.buttonElement.removeClass("ui-state-active").attr("aria-pressed",false)}}}},_resetButton:function(){if(this.type==="input"){if(this.options.label){this.element.val(this.options.label)}return}var l=this.buttonElement.removeClass(f),k=e("<span></span>").addClass("ui-button-text").html(this.options.label).appendTo(l.empty()).text(),j=this.options.icons,i=j.primary&&j.secondary;if(j.primary||j.secondary){l.addClass("ui-button-text-icon"+(i?"s":(j.primary?"-primary":"-secondary")));if(j.primary){l.prepend("<span class='ui-button-icon-primary ui-icon "+j.primary+"'></span>")}if(j.secondary){l.append("<span class='ui-button-icon-secondary ui-icon "+j.secondary+"'></span>")}if(!this.options.text){l.addClass(i?"ui-button-icons-only":"ui-button-icon-only").removeClass("ui-button-text-icons ui-button-text-icon-primary ui-button-text-icon-secondary");if(!this.hasTitle){l.attr("title",k)}}}else{l.addClass("ui-button-text-only")}}});e.widget("ui.buttonset",{_create:function(){this.element.addClass("ui-buttonset")},_init:function(){this.refresh()},_setOption:function(i,j){if(i==="disabled"){this.buttons.button("option",i,j)}this._superApply("_setOption",arguments)},refresh:function(){this.buttons=this.element.find(":button, :submit, :reset, :checkbox, :radio, a, :data(button)").filter(":ui-button").button("refresh").end().not(":ui-button").button().end().map(function(){return e(this).button("widget")[0]}).removeClass("ui-corner-all ui-corner-left ui-corner-right").filter(":visible").filter(":first").addClass("ui-corner-left").end().filter(":last").addClass("ui-corner-right").end().end().end()},destroy:function(){this.element.removeClass("ui-buttonset");this.buttons.map(function(){return e(this).button("widget")[0]}).removeClass("ui-corner-left ui-corner-right").end().button("destroy");this._super("destroy")}})}(jQuery));(function($,undefined){$.extend($.ui,{datepicker:{version:"1.9m3"}});var PROP_NAME="datepicker";var dpuuid=new Date().getTime();function Datepicker(){this.debug=false;this._curInst=null;this._keyEvent=false;this._disabledInputs=[];this._datepickerShowing=false;this._inDialog=false;this._mainDivId="ui-datepicker-div";this._inlineClass="ui-datepicker-inline";this._appendClass="ui-datepicker-append";this._triggerClass="ui-datepicker-trigger";this._dialogClass="ui-datepicker-dialog";this._disableClass="ui-datepicker-disabled";this._unselectableClass="ui-datepicker-unselectable";this._currentClass="ui-datepicker-current-day";this._dayOverClass="ui-datepicker-days-cell-over";this.regional=[];this.regional[""]={closeText:"Done",prevText:"Prev",nextText:"Next",currentText:"Today",monthNames:["January","February","March","April","May","June","July","August","September","October","November","December"],monthNamesShort:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],dayNames:["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],dayNamesShort:["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],dayNamesMin:["Su","Mo","Tu","We","Th","Fr","Sa"],weekHeader:"Wk",dateFormat:"mm/dd/yy",firstDay:0,isRTL:false,showMonthAfterYear:false,yearSuffix:""};this._defaults={showOn:"focus",showAnim:"fadeIn",showOptions:{},defaultDate:null,appendText:"",buttonText:"...",buttonImage:"",buttonImageOnly:false,hideIfNoPrevNext:false,navigationAsDateFormat:false,gotoCurrent:false,changeMonth:false,changeYear:false,yearRange:"c-10:c+10",showOtherMonths:false,selectOtherMonths:false,showWeek:false,calculateWeek:this.iso8601Week,shortYearCutoff:"+10",minDate:null,maxDate:null,duration:"fast",beforeShowDay:null,beforeShow:null,onSelect:null,onChangeMonthYear:null,onClose:null,numberOfMonths:1,showCurrentAtPos:0,stepMonths:1,stepBigMonths:12,altField:"",altFormat:"",constrainInput:true,showButtonPanel:false,autoSize:false};$.extend(this._defaults,this.regional[""]);this.dpDiv=$('<div id="'+this._mainDivId+'" class="ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all ui-helper-hidden-accessible"></div>')}$.extend(Datepicker.prototype,{markerClassName:"hasDatepicker",log:function(){if(this.debug){console.log.apply("",arguments)}},_widgetDatepicker:function(){return this.dpDiv},setDefaults:function(settings){extendRemove(this._defaults,settings||{});return this},_attachDatepicker:function(target,settings){var inlineSettings=null;for(var attrName in this._defaults){var attrValue=target.getAttribute("date:"+attrName);if(attrValue){inlineSettings=inlineSettings||{};try{inlineSettings[attrName]=eval(attrValue)}catch(err){inlineSettings[attrName]=attrValue}}}var nodeName=target.nodeName.toLowerCase();var inline=(nodeName=="div"||nodeName=="span");if(!target.id){this.uuid+=1;target.id="dp"+this.uuid}var inst=this._newInst($(target),inline);inst.settings=$.extend({},settings||{},inlineSettings||{});if(nodeName=="input"){this._connectDatepicker(target,inst)}else{if(inline){this._inlineDatepicker(target,inst)}}},_newInst:function(target,inline){var id=target[0].id.replace(/([^A-Za-z0-9_-])/g,"\\\\$1");return{id:id,input:target,selectedDay:0,selectedMonth:0,selectedYear:0,drawMonth:0,drawYear:0,inline:inline,dpDiv:(!inline?this.dpDiv:$('<div class="'+this._inlineClass+' ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all"></div>'))}},_connectDatepicker:function(target,inst){var input=$(target);inst.append=$([]);inst.trigger=$([]);if(input.hasClass(this.markerClassName)){return}this._attachments(input,inst);input.addClass(this.markerClassName).keydown(this._doKeyDown).keypress(this._doKeyPress).keyup(this._doKeyUp).bind("setData.datepicker",function(event,key,value){inst.settings[key]=value}).bind("getData.datepicker",function(event,key){return this._get(inst,key)});this._autoSize(inst);$.data(target,PROP_NAME,inst)},_attachments:function(input,inst){var appendText=this._get(inst,"appendText");var isRTL=this._get(inst,"isRTL");if(inst.append){inst.append.remove()}if(appendText){inst.append=$('<span class="'+this._appendClass+'">'+appendText+"</span>");input[isRTL?"before":"after"](inst.append)}input.unbind("focus",this._showDatepicker);if(inst.trigger){inst.trigger.remove()}var showOn=this._get(inst,"showOn");if(showOn=="focus"||showOn=="both"){input.focus(this._showDatepicker)}if(showOn=="button"||showOn=="both"){var buttonText=this._get(inst,"buttonText");var buttonImage=this._get(inst,"buttonImage");inst.trigger=$(this._get(inst,"buttonImageOnly")?$("<img/>").addClass(this._triggerClass).attr({src:buttonImage,alt:buttonText,title:buttonText}):$('<button type="button"></button>').addClass(this._triggerClass).html(buttonImage==""?buttonText:$("<img/>").attr({src:buttonImage,alt:buttonText,title:buttonText})));input[isRTL?"before":"after"](inst.trigger);inst.trigger.click(function(){if($.datepicker._datepickerShowing&&$.datepicker._lastInput==input[0]){$.datepicker._hideDatepicker()}else{$.datepicker._showDatepicker(input[0])}return false})}},_autoSize:function(inst){if(this._get(inst,"autoSize")&&!inst.inline){var date=new Date(2009,12-1,20);var dateFormat=this._get(inst,"dateFormat");if(dateFormat.match(/[DM]/)){var findMax=function(names){var max=0;var maxI=0;for(var i=0;i<names.length;i++){if(names[i].length>max){max=names[i].length;maxI=i}}return maxI};date.setMonth(findMax(this._get(inst,(dateFormat.match(/MM/)?"monthNames":"monthNamesShort"))));date.setDate(findMax(this._get(inst,(dateFormat.match(/DD/)?"dayNames":"dayNamesShort")))+20-date.getDay())}inst.input.attr("size",this._formatDate(inst,date).length)}},_inlineDatepicker:function(target,inst){var divSpan=$(target);if(divSpan.hasClass(this.markerClassName)){return}divSpan.addClass(this.markerClassName).append(inst.dpDiv).bind("setData.datepicker",function(event,key,value){inst.settings[key]=value}).bind("getData.datepicker",function(event,key){return this._get(inst,key)});$.data(target,PROP_NAME,inst);this._setDate(inst,this._getDefaultDate(inst),true);this._updateDatepicker(inst);this._updateAlternate(inst)},_dialogDatepicker:function(input,date,onSelect,settings,pos){var inst=this._dialogInst;if(!inst){this.uuid+=1;var id="dp"+this.uuid;this._dialogInput=$('<input type="text" id="'+id+'" style="position: absolute; top: -100px; width: 0px; z-index: -10;"/>');this._dialogInput.keydown(this._doKeyDown);$("body").append(this._dialogInput);inst=this._dialogInst=this._newInst(this._dialogInput,false);inst.settings={};$.data(this._dialogInput[0],PROP_NAME,inst)}extendRemove(inst.settings,settings||{});date=(date&&date.constructor==Date?this._formatDate(inst,date):date);this._dialogInput.val(date);this._pos=(pos?(pos.length?pos:[pos.pageX,pos.pageY]):null);if(!this._pos){var browserWidth=document.documentElement.clientWidth;var browserHeight=document.documentElement.clientHeight;var scrollX=document.documentElement.scrollLeft||document.body.scrollLeft;var scrollY=document.documentElement.scrollTop||document.body.scrollTop;this._pos=[(browserWidth/2)-100+scrollX,(browserHeight/2)-150+scrollY]}this._dialogInput.css("left",(this._pos[0]+20)+"px").css("top",this._pos[1]+"px");inst.settings.onSelect=onSelect;this._inDialog=true;this.dpDiv.addClass(this._dialogClass);this._showDatepicker(this._dialogInput[0]);if($.blockUI){$.blockUI(this.dpDiv)}$.data(this._dialogInput[0],PROP_NAME,inst);return this},_destroyDatepicker:function(target){var $target=$(target);var inst=$.data(target,PROP_NAME);if(!$target.hasClass(this.markerClassName)){return}var nodeName=target.nodeName.toLowerCase();$.removeData(target,PROP_NAME);if(nodeName=="input"){inst.append.remove();inst.trigger.remove();$target.removeClass(this.markerClassName).unbind("focus",this._showDatepicker).unbind("keydown",this._doKeyDown).unbind("keypress",this._doKeyPress).unbind("keyup",this._doKeyUp)}else{if(nodeName=="div"||nodeName=="span"){$target.removeClass(this.markerClassName).empty()}}},_enableDatepicker:function(target){var $target=$(target);var inst=$.data(target,PROP_NAME);if(!$target.hasClass(this.markerClassName)){return}var nodeName=target.nodeName.toLowerCase();if(nodeName=="input"){target.disabled=false;inst.trigger.filter("button").each(function(){this.disabled=false}).end().filter("img").css({opacity:"1.0",cursor:""})}else{if(nodeName=="div"||nodeName=="span"){var inline=$target.children("."+this._inlineClass);inline.children().removeClass("ui-state-disabled")}}this._disabledInputs=$.map(this._disabledInputs,function(value){return(value==target?null:value)})},_disableDatepicker:function(target){var $target=$(target);var inst=$.data(target,PROP_NAME);if(!$target.hasClass(this.markerClassName)){return}var nodeName=target.nodeName.toLowerCase();if(nodeName=="input"){target.disabled=true;inst.trigger.filter("button").each(function(){this.disabled=true}).end().filter("img").css({opacity:"0.5",cursor:"default"})}else{if(nodeName=="div"||nodeName=="span"){var inline=$target.children("."+this._inlineClass);inline.children().addClass("ui-state-disabled")}}this._disabledInputs=$.map(this._disabledInputs,function(value){return(value==target?null:value)});this._disabledInputs[this._disabledInputs.length]=target},_isDisabledDatepicker:function(target){if(!target){return false}for(var i=0;i<this._disabledInputs.length;i++){if(this._disabledInputs[i]==target){return true}}return false},_getInst:function(target){try{return $.data(target,PROP_NAME)}catch(err){throw"Missing instance data for this datepicker"}},_optionDatepicker:function(target,name,value){var inst=this._getInst(target);if(arguments.length==2&&typeof name=="string"){return(name=="defaults"?$.extend({},$.datepicker._defaults):(inst?(name=="all"?$.extend({},inst.settings):this._get(inst,name)):null))}var settings=name||{};if(typeof name=="string"){settings={};settings[name]=value}if(inst){if(this._curInst==inst){this._hideDatepicker()}var date=this._getDateDatepicker(target,true);extendRemove(inst.settings,settings);this._attachments($(target),inst);this._autoSize(inst);this._setDateDatepicker(target,date);this._updateDatepicker(inst)}},_changeDatepicker:function(target,name,value){this._optionDatepicker(target,name,value)},_refreshDatepicker:function(target){var inst=this._getInst(target);if(inst){this._updateDatepicker(inst)}},_setDateDatepicker:function(target,date){var inst=this._getInst(target);if(inst){this._setDate(inst,date);this._updateDatepicker(inst);this._updateAlternate(inst)}},_getDateDatepicker:function(target,noDefault){var inst=this._getInst(target);if(inst&&!inst.inline){this._setDateFromField(inst,noDefault)}return(inst?this._getDate(inst):null)},_doKeyDown:function(event){var inst=$.datepicker._getInst(event.target);var handled=true;var isRTL=inst.dpDiv.is(".ui-datepicker-rtl");inst._keyEvent=true;if($.datepicker._datepickerShowing){switch(event.keyCode){case 9:$.datepicker._hideDatepicker();handled=false;break;case 13:var sel=$("td."+$.datepicker._dayOverClass,inst.dpDiv).add($("td."+$.datepicker._currentClass,inst.dpDiv));if(sel[0]){$.datepicker._selectDay(event.target,inst.selectedMonth,inst.selectedYear,sel[0])}else{$.datepicker._hideDatepicker()}return false;break;case 27:$.datepicker._hideDatepicker();break;case 33:$.datepicker._adjustDate(event.target,(event.ctrlKey?-$.datepicker._get(inst,"stepBigMonths"):-$.datepicker._get(inst,"stepMonths")),"M");break;case 34:$.datepicker._adjustDate(event.target,(event.ctrlKey?+$.datepicker._get(inst,"stepBigMonths"):+$.datepicker._get(inst,"stepMonths")),"M");break;case 35:if(event.ctrlKey||event.metaKey){$.datepicker._clearDate(event.target)}handled=event.ctrlKey||event.metaKey;break;case 36:if(event.ctrlKey||event.metaKey){$.datepicker._gotoToday(event.target)}handled=event.ctrlKey||event.metaKey;break;case 37:if(event.ctrlKey||event.metaKey){$.datepicker._adjustDate(event.target,(isRTL?+1:-1),"D")}handled=event.ctrlKey||event.metaKey;if(event.originalEvent.altKey){$.datepicker._adjustDate(event.target,(event.ctrlKey?-$.datepicker._get(inst,"stepBigMonths"):-$.datepicker._get(inst,"stepMonths")),"M")}break;case 38:if(event.ctrlKey||event.metaKey){$.datepicker._adjustDate(event.target,-7,"D")}handled=event.ctrlKey||event.metaKey;break;case 39:if(event.ctrlKey||event.metaKey){$.datepicker._adjustDate(event.target,(isRTL?-1:+1),"D")}handled=event.ctrlKey||event.metaKey;if(event.originalEvent.altKey){$.datepicker._adjustDate(event.target,(event.ctrlKey?+$.datepicker._get(inst,"stepBigMonths"):+$.datepicker._get(inst,"stepMonths")),"M")}break;case 40:if(event.ctrlKey||event.metaKey){$.datepicker._adjustDate(event.target,+7,"D")}handled=event.ctrlKey||event.metaKey;break;default:handled=false}}else{if(event.keyCode==36&&event.ctrlKey){$.datepicker._showDatepicker(this)}else{handled=false}}if(handled){event.preventDefault();event.stopPropagation()}},_doKeyPress:function(event){var inst=$.datepicker._getInst(event.target);if($.datepicker._get(inst,"constrainInput")){var chars=$.datepicker._possibleChars($.datepicker._get(inst,"dateFormat"));var chr=String.fromCharCode(event.charCode==undefined?event.keyCode:event.charCode);return event.ctrlKey||(chr<" "||!chars||chars.indexOf(chr)>-1)}},_doKeyUp:function(event){var inst=$.datepicker._getInst(event.target);if(inst.input.val()!=inst.lastVal){try{var date=$.datepicker.parseDate($.datepicker._get(inst,"dateFormat"),(inst.input?inst.input.val():null),$.datepicker._getFormatConfig(inst));if(date){$.datepicker._setDateFromField(inst);$.datepicker._updateAlternate(inst);$.datepicker._updateDatepicker(inst)}}catch(event){$.datepicker.log(event)}}return true},_showDatepicker:function(input){input=input.target||input;if(input.nodeName.toLowerCase()!="input"){input=$("input",input.parentNode)[0]}if($.datepicker._isDisabledDatepicker(input)||$.datepicker._lastInput==input){return}var inst=$.datepicker._getInst(input);if($.datepicker._curInst&&$.datepicker._curInst!=inst){$.datepicker._curInst.dpDiv.stop(true,true)}var beforeShow=$.datepicker._get(inst,"beforeShow");extendRemove(inst.settings,(beforeShow?beforeShow.apply(input,[input,inst]):{}));inst.lastVal=null;$.datepicker._lastInput=input;$.datepicker._setDateFromField(inst);if($.datepicker._inDialog){input.value=""}if(!$.datepicker._pos){$.datepicker._pos=$.datepicker._findPos(input);$.datepicker._pos[1]+=input.offsetHeight}var isFixed=false;$(input).parents().each(function(){isFixed|=$(this).css("position")=="fixed";return !isFixed});if(isFixed&&$.browser.opera){$.datepicker._pos[0]-=document.documentElement.scrollLeft;$.datepicker._pos[1]-=document.documentElement.scrollTop}var offset={left:$.datepicker._pos[0],top:$.datepicker._pos[1]};$.datepicker._pos=null;inst.dpDiv.css({position:"absolute",display:"block",top:"-1000px"});$.datepicker._updateDatepicker(inst);offset=$.datepicker._checkOffset(inst,offset,isFixed);inst.dpDiv.css({position:($.datepicker._inDialog&&$.blockUI?"static":(isFixed?"fixed":"absolute")),display:"none",left:offset.left+"px",top:offset.top+"px"});if(!inst.inline){var showAnim=$.datepicker._get(inst,"showAnim");var duration=$.datepicker._get(inst,"duration");var postProcess=function(){$.datepicker._datepickerShowing=true;var borders=$.datepicker._getBorders(inst.dpDiv);inst.dpDiv.find("iframe.ui-datepicker-cover").css({left:-borders[0],top:-borders[1],width:inst.dpDiv.outerWidth(),height:inst.dpDiv.outerHeight()})};inst.dpDiv.zIndex($(input).zIndex()+1);if($.effects&&$.effects[showAnim]){inst.dpDiv.show(showAnim,$.datepicker._get(inst,"showOptions"),duration,postProcess)}else{inst.dpDiv[showAnim||"show"]((showAnim?duration:null),postProcess)}if(!showAnim||!duration){postProcess()}if(inst.input.is(":visible")&&!inst.input.is(":disabled")){inst.input.focus()}$.datepicker._curInst=inst}},_updateDatepicker:function(inst){var self=this;var borders=$.datepicker._getBorders(inst.dpDiv);inst.dpDiv.empty().append(this._generateHTML(inst)).find("iframe.ui-datepicker-cover").css({left:-borders[0],top:-borders[1],width:inst.dpDiv.outerWidth(),height:inst.dpDiv.outerHeight()}).end().find("button, .ui-datepicker-prev, .ui-datepicker-next, .ui-datepicker-calendar td a").bind("mouseout",function(){$(this).removeClass("ui-state-hover");if(this.className.indexOf("ui-datepicker-prev")!=-1){$(this).removeClass("ui-datepicker-prev-hover")}if(this.className.indexOf("ui-datepicker-next")!=-1){$(this).removeClass("ui-datepicker-next-hover")}}).bind("mouseover",function(){if(!self._isDisabledDatepicker(inst.inline?inst.dpDiv.parent()[0]:inst.input[0])){$(this).parents(".ui-datepicker-calendar").find("a").removeClass("ui-state-hover");$(this).addClass("ui-state-hover");if(this.className.indexOf("ui-datepicker-prev")!=-1){$(this).addClass("ui-datepicker-prev-hover")}if(this.className.indexOf("ui-datepicker-next")!=-1){$(this).addClass("ui-datepicker-next-hover")}}}).end().find("."+this._dayOverClass+" a").trigger("mouseover").end();var numMonths=this._getNumberOfMonths(inst);var cols=numMonths[1];var width=17;if(cols>1){inst.dpDiv.addClass("ui-datepicker-multi-"+cols).css("width",(width*cols)+"em")}else{inst.dpDiv.removeClass("ui-datepicker-multi-2 ui-datepicker-multi-3 ui-datepicker-multi-4").width("")}inst.dpDiv[(numMonths[0]!=1||numMonths[1]!=1?"add":"remove")+"Class"]("ui-datepicker-multi");inst.dpDiv[(this._get(inst,"isRTL")?"add":"remove")+"Class"]("ui-datepicker-rtl");if(inst==$.datepicker._curInst&&$.datepicker._datepickerShowing&&inst.input&&inst.input.is(":visible")&&!inst.input.is(":disabled")){inst.input.focus()}},_getBorders:function(elem){var convert=function(value){return{thin:1,medium:2,thick:3}[value]||value};return[parseFloat(convert(elem.css("border-left-width"))),parseFloat(convert(elem.css("border-top-width")))]},_checkOffset:function(inst,offset,isFixed){var dpWidth=inst.dpDiv.outerWidth();var dpHeight=inst.dpDiv.outerHeight();var inputWidth=inst.input?inst.input.outerWidth():0;var inputHeight=inst.input?inst.input.outerHeight():0;var viewWidth=document.documentElement.clientWidth+$(document).scrollLeft();var viewHeight=document.documentElement.clientHeight+$(document).scrollTop();offset.left-=(this._get(inst,"isRTL")?(dpWidth-inputWidth):0);offset.left-=(isFixed&&offset.left==inst.input.offset().left)?$(document).scrollLeft():0;offset.top-=(isFixed&&offset.top==(inst.input.offset().top+inputHeight))?$(document).scrollTop():0;offset.left-=Math.min(offset.left,(offset.left+dpWidth>viewWidth&&viewWidth>dpWidth)?Math.abs(offset.left+dpWidth-viewWidth):0);offset.top-=Math.min(offset.top,(offset.top+dpHeight>viewHeight&&viewHeight>dpHeight)?Math.abs(dpHeight+inputHeight):0);return offset},_findPos:function(obj){var inst=this._getInst(obj);var isRTL=this._get(inst,"isRTL");while(obj&&(obj.type=="hidden"||obj.nodeType!=1)){obj=obj[isRTL?"previousSibling":"nextSibling"]}var position=$(obj).offset();return[position.left,position.top]},_hideDatepicker:function(input){var inst=this._curInst;if(!inst||(input&&inst!=$.data(input,PROP_NAME))){return}if(this._datepickerShowing){var showAnim=this._get(inst,"showAnim");var duration=this._get(inst,"duration");var postProcess=function(){$.datepicker._tidyDialog(inst);this._curInst=null};if($.effects&&$.effects[showAnim]){inst.dpDiv.hide(showAnim,$.datepicker._get(inst,"showOptions"),duration,postProcess)}else{inst.dpDiv[(showAnim=="slideDown"?"slideUp":(showAnim=="fadeIn"?"fadeOut":"hide"))]((showAnim?duration:null),postProcess)}if(!showAnim){postProcess()}var onClose=this._get(inst,"onClose");if(onClose){onClose.apply((inst.input?inst.input[0]:null),[(inst.input?inst.input.val():""),inst])}this._datepickerShowing=false;this._lastInput=null;if(this._inDialog){this._dialogInput.css({position:"absolute",left:"0",top:"-100px"});if($.blockUI){$.unblockUI();$("body").append(this.dpDiv)}}this._inDialog=false}},_tidyDialog:function(inst){inst.dpDiv.removeClass(this._dialogClass).unbind(".ui-datepicker-calendar")},_checkExternalClick:function(event){if(!$.datepicker._curInst){return}var $target=$(event.target);if($target[0].id!=$.datepicker._mainDivId&&$target.parents("#"+$.datepicker._mainDivId).length==0&&!$target.hasClass($.datepicker.markerClassName)&&!$target.hasClass($.datepicker._triggerClass)&&$.datepicker._datepickerShowing&&!($.datepicker._inDialog&&$.blockUI)){$.datepicker._hideDatepicker()}},_adjustDate:function(id,offset,period){var target=$(id);var inst=this._getInst(target[0]);if(this._isDisabledDatepicker(target[0])){return}this._adjustInstDate(inst,offset+(period=="M"?this._get(inst,"showCurrentAtPos"):0),period);this._updateDatepicker(inst)},_gotoToday:function(id){var target=$(id);var inst=this._getInst(target[0]);if(this._get(inst,"gotoCurrent")&&inst.currentDay){inst.selectedDay=inst.currentDay;inst.drawMonth=inst.selectedMonth=inst.currentMonth;inst.drawYear=inst.selectedYear=inst.currentYear}else{var date=new Date();inst.selectedDay=date.getDate();inst.drawMonth=inst.selectedMonth=date.getMonth();inst.drawYear=inst.selectedYear=date.getFullYear()}this._notifyChange(inst);this._adjustDate(target)},_selectMonthYear:function(id,select,period){var target=$(id);var inst=this._getInst(target[0]);inst._selectingMonthYear=false;inst["selected"+(period=="M"?"Month":"Year")]=inst["draw"+(period=="M"?"Month":"Year")]=parseInt(select.options[select.selectedIndex].value,10);this._notifyChange(inst);this._adjustDate(target)},_clickMonthYear:function(id){var target=$(id);var inst=this._getInst(target[0]);if(inst.input&&inst._selectingMonthYear){setTimeout(function(){inst.input.focus()},0)}inst._selectingMonthYear=!inst._selectingMonthYear},_selectDay:function(id,month,year,td){var target=$(id);if($(td).hasClass(this._unselectableClass)||this._isDisabledDatepicker(target[0])){return}var inst=this._getInst(target[0]);inst.selectedDay=inst.currentDay=$("a",td).html();inst.selectedMonth=inst.currentMonth=month;inst.selectedYear=inst.currentYear=year;this._selectDate(id,this._formatDate(inst,inst.currentDay,inst.currentMonth,inst.currentYear))},_clearDate:function(id){var target=$(id);var inst=this._getInst(target[0]);this._selectDate(target,"")},_selectDate:function(id,dateStr){var target=$(id);var inst=this._getInst(target[0]);dateStr=(dateStr!=null?dateStr:this._formatDate(inst));if(inst.input){inst.input.val(dateStr)}this._updateAlternate(inst);var onSelect=this._get(inst,"onSelect");if(onSelect){onSelect.apply((inst.input?inst.input[0]:null),[dateStr,inst])}else{if(inst.input){inst.input.trigger("change")}}if(inst.inline){this._updateDatepicker(inst)}else{this._hideDatepicker();this._lastInput=inst.input[0];if(typeof(inst.input[0])!="object"){inst.input.focus()}this._lastInput=null}},_updateAlternate:function(inst){var altField=this._get(inst,"altField");if(altField){var altFormat=this._get(inst,"altFormat")||this._get(inst,"dateFormat");var date=this._getDate(inst);var dateStr=this.formatDate(altFormat,date,this._getFormatConfig(inst));$(altField).each(function(){$(this).val(dateStr)})}},noWeekends:function(date){var day=date.getDay();return[(day>0&&day<6),""]},iso8601Week:function(date){var checkDate=new Date(date.getTime());checkDate.setDate(checkDate.getDate()+4-(checkDate.getDay()||7));var time=checkDate.getTime();checkDate.setMonth(0);checkDate.setDate(1);return Math.floor(Math.round((time-checkDate)/86400000)/7)+1},parseDate:function(format,value,settings){if(format==null||value==null){throw"Invalid arguments"}value=(typeof value=="object"?value.toString():value+"");if(value==""){return null}var shortYearCutoff=(settings?settings.shortYearCutoff:null)||this._defaults.shortYearCutoff;var dayNamesShort=(settings?settings.dayNamesShort:null)||this._defaults.dayNamesShort;var dayNames=(settings?settings.dayNames:null)||this._defaults.dayNames;var monthNamesShort=(settings?settings.monthNamesShort:null)||this._defaults.monthNamesShort;var monthNames=(settings?settings.monthNames:null)||this._defaults.monthNames;var year=-1;var month=-1;var day=-1;var doy=-1;var literal=false;var lookAhead=function(match){var matches=(iFormat+1<format.length&&format.charAt(iFormat+1)==match);if(matches){iFormat++}return matches};var getNumber=function(match){lookAhead(match);var size=(match=="@"?14:(match=="!"?20:(match=="y"?4:(match=="o"?3:2))));var digits=new RegExp("^\\d{1,"+size+"}");var num=value.substring(iValue).match(digits);if(!num){throw"Missing number at position "+iValue}iValue+=num[0].length;return parseInt(num[0],10)};var getName=function(match,shortNames,longNames){var names=(lookAhead(match)?longNames:shortNames);for(var i=0;i<names.length;i++){if(value.substr(iValue,names[i].length).toLowerCase()==names[i].toLowerCase()){iValue+=names[i].length;return i+1}}throw"Unknown name at position "+iValue};var checkLiteral=function(){if(value.charAt(iValue)!=format.charAt(iFormat)){throw"Unexpected literal at position "+iValue}iValue++};var iValue=0;for(var iFormat=0;iFormat<format.length;iFormat++){if(literal){if(format.charAt(iFormat)=="'"&&!lookAhead("'")){literal=false}else{checkLiteral()}}else{switch(format.charAt(iFormat)){case"d":day=getNumber("d");break;case"D":getName("D",dayNamesShort,dayNames);break;case"o":doy=getNumber("o");break;case"m":month=getNumber("m");break;case"M":month=getName("M",monthNamesShort,monthNames);break;case"y":year=getNumber("y");break;case"@":var date=new Date(getNumber("@"));year=date.getFullYear();month=date.getMonth()+1;day=date.getDate();break;case"!":var date=new Date((getNumber("!")-this._ticksTo1970)/10000);year=date.getFullYear();month=date.getMonth()+1;day=date.getDate();break;case"'":if(lookAhead("'")){checkLiteral()}else{literal=true}break;default:checkLiteral()}}}if(year==-1){year=new Date().getFullYear()}else{if(year<100){year+=new Date().getFullYear()-new Date().getFullYear()%100+(year<=shortYearCutoff?0:-100)}}if(doy>-1){month=1;day=doy;do{var dim=this._getDaysInMonth(year,month-1);if(day<=dim){break}month++;day-=dim}while(true)}var date=this._daylightSavingAdjust(new Date(year,month-1,day));if(date.getFullYear()!=year||date.getMonth()+1!=month||date.getDate()!=day){throw"Invalid date"}return date},ATOM:"yy-mm-dd",COOKIE:"D, dd M yy",ISO_8601:"yy-mm-dd",RFC_822:"D, d M y",RFC_850:"DD, dd-M-y",RFC_1036:"D, d M y",RFC_1123:"D, d M yy",RFC_2822:"D, d M yy",RSS:"D, d M y",TICKS:"!",TIMESTAMP:"@",W3C:"yy-mm-dd",_ticksTo1970:(((1970-1)*365+Math.floor(1970/4)-Math.floor(1970/100)+Math.floor(1970/400))*24*60*60*10000000),formatDate:function(format,date,settings){if(!date){return""}var dayNamesShort=(settings?settings.dayNamesShort:null)||this._defaults.dayNamesShort;var dayNames=(settings?settings.dayNames:null)||this._defaults.dayNames;var monthNamesShort=(settings?settings.monthNamesShort:null)||this._defaults.monthNamesShort;var monthNames=(settings?settings.monthNames:null)||this._defaults.monthNames;var lookAhead=function(match){var matches=(iFormat+1<format.length&&format.charAt(iFormat+1)==match);if(matches){iFormat++}return matches};var formatNumber=function(match,value,len){var num=""+value;if(lookAhead(match)){while(num.length<len){num="0"+num}}return num};var formatName=function(match,value,shortNames,longNames){return(lookAhead(match)?longNames[value]:shortNames[value])};var output="";var literal=false;if(date){for(var iFormat=0;iFormat<format.length;iFormat++){if(literal){if(format.charAt(iFormat)=="'"&&!lookAhead("'")){literal=false}else{output+=format.charAt(iFormat)}}else{switch(format.charAt(iFormat)){case"d":output+=formatNumber("d",date.getDate(),2);break;case"D":output+=formatName("D",date.getDay(),dayNamesShort,dayNames);break;case"o":output+=formatNumber("o",(date.getTime()-new Date(date.getFullYear(),0,0).getTime())/86400000,3);break;case"m":output+=formatNumber("m",date.getMonth()+1,2);break;case"M":output+=formatName("M",date.getMonth(),monthNamesShort,monthNames);break;case"y":output+=(lookAhead("y")?date.getFullYear():(date.getYear()%100<10?"0":"")+date.getYear()%100);break;case"@":output+=date.getTime();break;case"!":output+=date.getTime()*10000+this._ticksTo1970;break;case"'":if(lookAhead("'")){output+="'"}else{literal=true}break;default:output+=format.charAt(iFormat)}}}}return output},_possibleChars:function(format){var chars="";var literal=false;var lookAhead=function(match){var matches=(iFormat+1<format.length&&format.charAt(iFormat+1)==match);if(matches){iFormat++}return matches};for(var iFormat=0;iFormat<format.length;iFormat++){if(literal){if(format.charAt(iFormat)=="'"&&!lookAhead("'")){literal=false}else{chars+=format.charAt(iFormat)}}else{switch(format.charAt(iFormat)){case"d":case"m":case"y":case"@":chars+="0123456789";break;case"D":case"M":return null;case"'":if(lookAhead("'")){chars+="'"}else{literal=true}break;default:chars+=format.charAt(iFormat)}}}return chars},_get:function(inst,name){return inst.settings[name]!==undefined?inst.settings[name]:this._defaults[name]},_setDateFromField:function(inst,noDefault){if(inst.input.val()==inst.lastVal){return}var dateFormat=this._get(inst,"dateFormat");var dates=inst.lastVal=inst.input?inst.input.val():null;var date,defaultDate;date=defaultDate=this._getDefaultDate(inst);var settings=this._getFormatConfig(inst);try{date=this.parseDate(dateFormat,dates,settings)||defaultDate}catch(event){this.log(event);dates=(noDefault?"":dates)}inst.selectedDay=date.getDate();inst.drawMonth=inst.selectedMonth=date.getMonth();inst.drawYear=inst.selectedYear=date.getFullYear();inst.currentDay=(dates?date.getDate():0);inst.currentMonth=(dates?date.getMonth():0);inst.currentYear=(dates?date.getFullYear():0);this._adjustInstDate(inst)},_getDefaultDate:function(inst){return this._restrictMinMax(inst,this._determineDate(inst,this._get(inst,"defaultDate"),new Date()))},_determineDate:function(inst,date,defaultDate){var offsetNumeric=function(offset){var date=new Date();date.setDate(date.getDate()+offset);return date};var offsetString=function(offset){try{return $.datepicker.parseDate($.datepicker._get(inst,"dateFormat"),offset,$.datepicker._getFormatConfig(inst))}catch(e){}var date=(offset.toLowerCase().match(/^c/)?$.datepicker._getDate(inst):null)||new Date();var year=date.getFullYear();var month=date.getMonth();var day=date.getDate();var pattern=/([+-]?[0-9]+)\s*(d|D|w|W|m|M|y|Y)?/g;var matches=pattern.exec(offset);while(matches){switch(matches[2]||"d"){case"d":case"D":day+=parseInt(matches[1],10);break;case"w":case"W":day+=parseInt(matches[1],10)*7;break;case"m":case"M":month+=parseInt(matches[1],10);day=Math.min(day,$.datepicker._getDaysInMonth(year,month));break;case"y":case"Y":year+=parseInt(matches[1],10);day=Math.min(day,$.datepicker._getDaysInMonth(year,month));break}matches=pattern.exec(offset)}return new Date(year,month,day)};date=(date==null?defaultDate:(typeof date=="string"?offsetString(date):(typeof date=="number"?(isNaN(date)?defaultDate:offsetNumeric(date)):date)));date=(date&&date.toString()=="Invalid Date"?defaultDate:date);if(date){date.setHours(0);date.setMinutes(0);date.setSeconds(0);date.setMilliseconds(0)}return this._daylightSavingAdjust(date)},_daylightSavingAdjust:function(date){if(!date){return null}date.setHours(date.getHours()>12?date.getHours()+2:0);return date},_setDate:function(inst,date,noChange){var clear=!(date);var origMonth=inst.selectedMonth;var origYear=inst.selectedYear;date=this._restrictMinMax(inst,this._determineDate(inst,date,new Date()));inst.selectedDay=inst.currentDay=date.getDate();inst.drawMonth=inst.selectedMonth=inst.currentMonth=date.getMonth();inst.drawYear=inst.selectedYear=inst.currentYear=date.getFullYear();if((origMonth!=inst.selectedMonth||origYear!=inst.selectedYear)&&!noChange){this._notifyChange(inst)}this._adjustInstDate(inst);if(inst.input){inst.input.val(clear?"":this._formatDate(inst))}},_getDate:function(inst){var startDate=(!inst.currentYear||(inst.input&&inst.input.val()=="")?null:this._daylightSavingAdjust(new Date(inst.currentYear,inst.currentMonth,inst.currentDay)));return startDate},_generateHTML:function(inst){var today=new Date();today=this._daylightSavingAdjust(new Date(today.getFullYear(),today.getMonth(),today.getDate()));var isRTL=this._get(inst,"isRTL");var showButtonPanel=this._get(inst,"showButtonPanel");var hideIfNoPrevNext=this._get(inst,"hideIfNoPrevNext");var navigationAsDateFormat=this._get(inst,"navigationAsDateFormat");var numMonths=this._getNumberOfMonths(inst);var showCurrentAtPos=this._get(inst,"showCurrentAtPos");var stepMonths=this._get(inst,"stepMonths");var isMultiMonth=(numMonths[0]!=1||numMonths[1]!=1);var currentDate=this._daylightSavingAdjust((!inst.currentDay?new Date(9999,9,9):new Date(inst.currentYear,inst.currentMonth,inst.currentDay)));var minDate=this._getMinMaxDate(inst,"min");var maxDate=this._getMinMaxDate(inst,"max");var drawMonth=inst.drawMonth-showCurrentAtPos;var drawYear=inst.drawYear;if(drawMonth<0){drawMonth+=12;drawYear--}if(maxDate){var maxDraw=this._daylightSavingAdjust(new Date(maxDate.getFullYear(),maxDate.getMonth()-(numMonths[0]*numMonths[1])+1,maxDate.getDate()));maxDraw=(minDate&&maxDraw<minDate?minDate:maxDraw);while(this._daylightSavingAdjust(new Date(drawYear,drawMonth,1))>maxDraw){drawMonth--;if(drawMonth<0){drawMonth=11;drawYear--}}}inst.drawMonth=drawMonth;inst.drawYear=drawYear;var prevText=this._get(inst,"prevText");prevText=(!navigationAsDateFormat?prevText:this.formatDate(prevText,this._daylightSavingAdjust(new Date(drawYear,drawMonth-stepMonths,1)),this._getFormatConfig(inst)));var prev=(this._canAdjustMonth(inst,-1,drawYear,drawMonth)?'<a class="ui-datepicker-prev ui-corner-all" onclick="DP_jQuery_'+dpuuid+".datepicker._adjustDate('#"+inst.id+"', -"+stepMonths+", 'M');\" title=\""+prevText+'"><span class="ui-icon ui-icon-circle-triangle-'+(isRTL?"e":"w")+'">'+prevText+"</span></a>":(hideIfNoPrevNext?"":'<a class="ui-datepicker-prev ui-corner-all ui-state-disabled" title="'+prevText+'"><span class="ui-icon ui-icon-circle-triangle-'+(isRTL?"e":"w")+'">'+prevText+"</span></a>"));var nextText=this._get(inst,"nextText");nextText=(!navigationAsDateFormat?nextText:this.formatDate(nextText,this._daylightSavingAdjust(new Date(drawYear,drawMonth+stepMonths,1)),this._getFormatConfig(inst)));var next=(this._canAdjustMonth(inst,+1,drawYear,drawMonth)?'<a class="ui-datepicker-next ui-corner-all" onclick="DP_jQuery_'+dpuuid+".datepicker._adjustDate('#"+inst.id+"', +"+stepMonths+", 'M');\" title=\""+nextText+'"><span class="ui-icon ui-icon-circle-triangle-'+(isRTL?"w":"e")+'">'+nextText+"</span></a>":(hideIfNoPrevNext?"":'<a class="ui-datepicker-next ui-corner-all ui-state-disabled" title="'+nextText+'"><span class="ui-icon ui-icon-circle-triangle-'+(isRTL?"w":"e")+'">'+nextText+"</span></a>"));var currentText=this._get(inst,"currentText");var gotoDate=(this._get(inst,"gotoCurrent")&&inst.currentDay?currentDate:today);currentText=(!navigationAsDateFormat?currentText:this.formatDate(currentText,gotoDate,this._getFormatConfig(inst)));var controls=(!inst.inline?'<button type="button" class="ui-datepicker-close ui-state-default ui-priority-primary ui-corner-all" onclick="DP_jQuery_'+dpuuid+'.datepicker._hideDatepicker();">'+this._get(inst,"closeText")+"</button>":"");var buttonPanel=(showButtonPanel)?'<div class="ui-datepicker-buttonpane ui-widget-content">'+(isRTL?controls:"")+(this._isInRange(inst,gotoDate)?'<button type="button" class="ui-datepicker-current ui-state-default ui-priority-secondary ui-corner-all" onclick="DP_jQuery_'+dpuuid+".datepicker._gotoToday('#"+inst.id+"');\">"+currentText+"</button>":"")+(isRTL?"":controls)+"</div>":"";var firstDay=parseInt(this._get(inst,"firstDay"),10);firstDay=(isNaN(firstDay)?0:firstDay);var showWeek=this._get(inst,"showWeek");var dayNames=this._get(inst,"dayNames");var dayNamesShort=this._get(inst,"dayNamesShort");var dayNamesMin=this._get(inst,"dayNamesMin");var monthNames=this._get(inst,"monthNames");var monthNamesShort=this._get(inst,"monthNamesShort");var beforeShowDay=this._get(inst,"beforeShowDay");var showOtherMonths=this._get(inst,"showOtherMonths");var selectOtherMonths=this._get(inst,"selectOtherMonths");var calculateWeek=this._get(inst,"calculateWeek")||this.iso8601Week;var defaultDate=this._getDefaultDate(inst);var html="";for(var row=0;row<numMonths[0];row++){var group="";for(var col=0;col<numMonths[1];col++){var selectedDate=this._daylightSavingAdjust(new Date(drawYear,drawMonth,inst.selectedDay));var cornerClass=" ui-corner-all";var calender="";if(isMultiMonth){calender+='<div class="ui-datepicker-group';if(numMonths[1]>1){switch(col){case 0:calender+=" ui-datepicker-group-first";cornerClass=" ui-corner-"+(isRTL?"right":"left");break;case numMonths[1]-1:calender+=" ui-datepicker-group-last";cornerClass=" ui-corner-"+(isRTL?"left":"right");break;default:calender+=" ui-datepicker-group-middle";cornerClass="";break}}calender+='">'}calender+='<div class="ui-datepicker-header ui-widget-header ui-helper-clearfix'+cornerClass+'">'+(/all|left/.test(cornerClass)&&row==0?(isRTL?next:prev):"")+(/all|right/.test(cornerClass)&&row==0?(isRTL?prev:next):"")+this._generateMonthYearHeader(inst,drawMonth,drawYear,minDate,maxDate,row>0||col>0,monthNames,monthNamesShort)+'</div><table class="ui-datepicker-calendar"><thead><tr>';var thead=(showWeek?'<th class="ui-datepicker-week-col">'+this._get(inst,"weekHeader")+"</th>":"");for(var dow=0;dow<7;dow++){var day=(dow+firstDay)%7;thead+="<th"+((dow+firstDay+6)%7>=5?' class="ui-datepicker-week-end"':"")+'><span title="'+dayNames[day]+'">'+dayNamesMin[day]+"</span></th>"}calender+=thead+"</tr></thead><tbody>";var daysInMonth=this._getDaysInMonth(drawYear,drawMonth);if(drawYear==inst.selectedYear&&drawMonth==inst.selectedMonth){inst.selectedDay=Math.min(inst.selectedDay,daysInMonth)}var leadDays=(this._getFirstDayOfMonth(drawYear,drawMonth)-firstDay+7)%7;var numRows=(isMultiMonth?6:Math.ceil((leadDays+daysInMonth)/7));var printDate=this._daylightSavingAdjust(new Date(drawYear,drawMonth,1-leadDays));for(var dRow=0;dRow<numRows;dRow++){calender+="<tr>";var tbody=(!showWeek?"":'<td class="ui-datepicker-week-col">'+this._get(inst,"calculateWeek")(printDate)+"</td>");for(var dow=0;dow<7;dow++){var daySettings=(beforeShowDay?beforeShowDay.apply((inst.input?inst.input[0]:null),[printDate]):[true,""]);var otherMonth=(printDate.getMonth()!=drawMonth);var unselectable=(otherMonth&&!selectOtherMonths)||!daySettings[0]||(minDate&&printDate<minDate)||(maxDate&&printDate>maxDate);tbody+='<td class="'+((dow+firstDay+6)%7>=5?" ui-datepicker-week-end":"")+(otherMonth?" ui-datepicker-other-month":"")+((printDate.getTime()==selectedDate.getTime()&&drawMonth==inst.selectedMonth&&inst._keyEvent)||(defaultDate.getTime()==printDate.getTime()&&defaultDate.getTime()==selectedDate.getTime())?" "+this._dayOverClass:"")+(unselectable?" "+this._unselectableClass+" ui-state-disabled":"")+(otherMonth&&!showOtherMonths?"":" "+daySettings[1]+(printDate.getTime()==currentDate.getTime()?" "+this._currentClass:"")+(printDate.getTime()==today.getTime()?" ui-datepicker-today":""))+'"'+((!otherMonth||showOtherMonths)&&daySettings[2]?' title="'+daySettings[2]+'"':"")+(unselectable?"":' onclick="DP_jQuery_'+dpuuid+".datepicker._selectDay('#"+inst.id+"',"+printDate.getMonth()+","+printDate.getFullYear()+', this);return false;"')+">"+(otherMonth&&!showOtherMonths?"&#xa0;":(unselectable?'<span class="ui-state-default">'+printDate.getDate()+"</span>":'<a class="ui-state-default'+(printDate.getTime()==today.getTime()?" ui-state-highlight":"")+(printDate.getTime()==currentDate.getTime()?" ui-state-active":"")+(otherMonth?" ui-priority-secondary":"")+'" href="#">'+printDate.getDate()+"</a>"))+"</td>";printDate.setDate(printDate.getDate()+1);printDate=this._daylightSavingAdjust(printDate)}calender+=tbody+"</tr>"}drawMonth++;if(drawMonth>11){drawMonth=0;drawYear++}calender+="</tbody></table>"+(isMultiMonth?"</div>"+((numMonths[0]>0&&col==numMonths[1]-1)?'<div class="ui-datepicker-row-break"></div>':""):"");group+=calender}html+=group}html+=buttonPanel+($.browser.msie&&parseInt($.browser.version,10)<7&&!inst.inline?'<iframe src="javascript:false;" class="ui-datepicker-cover" frameborder="0"></iframe>':"");inst._keyEvent=false;return html},_generateMonthYearHeader:function(inst,drawMonth,drawYear,minDate,maxDate,secondary,monthNames,monthNamesShort){var changeMonth=this._get(inst,"changeMonth");var changeYear=this._get(inst,"changeYear");var showMonthAfterYear=this._get(inst,"showMonthAfterYear");var html='<div class="ui-datepicker-title">';var monthHtml="";if(secondary||!changeMonth){monthHtml+='<span class="ui-datepicker-month">'+monthNames[drawMonth]+"</span>"}else{var inMinYear=(minDate&&minDate.getFullYear()==drawYear);var inMaxYear=(maxDate&&maxDate.getFullYear()==drawYear);monthHtml+='<select class="ui-datepicker-month" onchange="DP_jQuery_'+dpuuid+".datepicker._selectMonthYear('#"+inst.id+"', this, 'M');\" onclick=\"DP_jQuery_"+dpuuid+".datepicker._clickMonthYear('#"+inst.id+"');\">";for(var month=0;month<12;month++){if((!inMinYear||month>=minDate.getMonth())&&(!inMaxYear||month<=maxDate.getMonth())){monthHtml+='<option value="'+month+'"'+(month==drawMonth?' selected="selected"':"")+">"+monthNamesShort[month]+"</option>"}}monthHtml+="</select>"}if(!showMonthAfterYear){html+=monthHtml+(secondary||!(changeMonth&&changeYear)?"&#xa0;":"")}if(secondary||!changeYear){html+='<span class="ui-datepicker-year">'+drawYear+"</span>"}else{var years=this._get(inst,"yearRange").split(":");var thisYear=new Date().getFullYear();var determineYear=function(value){var year=(value.match(/c[+-].*/)?drawYear+parseInt(value.substring(1),10):(value.match(/[+-].*/)?thisYear+parseInt(value,10):parseInt(value,10)));return(isNaN(year)?thisYear:year)};var year=determineYear(years[0]);var endYear=Math.max(year,determineYear(years[1]||""));year=(minDate?Math.max(year,minDate.getFullYear()):year);endYear=(maxDate?Math.min(endYear,maxDate.getFullYear()):endYear);html+='<select class="ui-datepicker-year" onchange="DP_jQuery_'+dpuuid+".datepicker._selectMonthYear('#"+inst.id+"', this, 'Y');\" onclick=\"DP_jQuery_"+dpuuid+".datepicker._clickMonthYear('#"+inst.id+"');\">";for(;year<=endYear;year++){html+='<option value="'+year+'"'+(year==drawYear?' selected="selected"':"")+">"+year+"</option>"}html+="</select>"}html+=this._get(inst,"yearSuffix");if(showMonthAfterYear){html+=(secondary||!(changeMonth&&changeYear)?"&#xa0;":"")+monthHtml}html+="</div>";return html},_adjustInstDate:function(inst,offset,period){var year=inst.drawYear+(period=="Y"?offset:0);var month=inst.drawMonth+(period=="M"?offset:0);var day=Math.min(inst.selectedDay,this._getDaysInMonth(year,month))+(period=="D"?offset:0);var date=this._restrictMinMax(inst,this._daylightSavingAdjust(new Date(year,month,day)));inst.selectedDay=date.getDate();inst.drawMonth=inst.selectedMonth=date.getMonth();inst.drawYear=inst.selectedYear=date.getFullYear();if(period=="M"||period=="Y"){this._notifyChange(inst)}},_restrictMinMax:function(inst,date){var minDate=this._getMinMaxDate(inst,"min");var maxDate=this._getMinMaxDate(inst,"max");date=(minDate&&date<minDate?minDate:date);date=(maxDate&&date>maxDate?maxDate:date);return date},_notifyChange:function(inst){var onChange=this._get(inst,"onChangeMonthYear");if(onChange){onChange.apply((inst.input?inst.input[0]:null),[inst.selectedYear,inst.selectedMonth+1,inst])}},_getNumberOfMonths:function(inst){var numMonths=this._get(inst,"numberOfMonths");return(numMonths==null?[1,1]:(typeof numMonths=="number"?[1,numMonths]:numMonths))},_getMinMaxDate:function(inst,minMax){return this._determineDate(inst,this._get(inst,minMax+"Date"),null)},_getDaysInMonth:function(year,month){return 32-new Date(year,month,32).getDate()},_getFirstDayOfMonth:function(year,month){return new Date(year,month,1).getDay()},_canAdjustMonth:function(inst,offset,curYear,curMonth){var numMonths=this._getNumberOfMonths(inst);var date=this._daylightSavingAdjust(new Date(curYear,curMonth+(offset<0?offset:numMonths[0]*numMonths[1]),1));if(offset<0){date.setDate(this._getDaysInMonth(date.getFullYear(),date.getMonth()))}return this._isInRange(inst,date)},_isInRange:function(inst,date){var minDate=this._getMinMaxDate(inst,"min");var maxDate=this._getMinMaxDate(inst,"max");return((!minDate||date.getTime()>=minDate.getTime())&&(!maxDate||date.getTime()<=maxDate.getTime()))},_getFormatConfig:function(inst){var shortYearCutoff=this._get(inst,"shortYearCutoff");shortYearCutoff=(typeof shortYearCutoff!="string"?shortYearCutoff:new Date().getFullYear()%100+parseInt(shortYearCutoff,10));return{shortYearCutoff:shortYearCutoff,dayNamesShort:this._get(inst,"dayNamesShort"),dayNames:this._get(inst,"dayNames"),monthNamesShort:this._get(inst,"monthNamesShort"),monthNames:this._get(inst,"monthNames")}},_formatDate:function(inst,day,month,year){if(!day){inst.currentDay=inst.selectedDay;inst.currentMonth=inst.selectedMonth;inst.currentYear=inst.selectedYear}var date=(day?(typeof day=="object"?day:this._daylightSavingAdjust(new Date(year,month,day))):this._daylightSavingAdjust(new Date(inst.currentYear,inst.currentMonth,inst.currentDay)));return this.formatDate(this._get(inst,"dateFormat"),date,this._getFormatConfig(inst))}});function extendRemove(target,props){$.extend(target,props);for(var name in props){if(props[name]==null||props[name]==undefined){target[name]=props[name]}}return target}function isArray(a){return(a&&(($.browser.safari&&typeof a=="object"&&a.length)||(a.constructor&&a.constructor.toString().match(/\Array\(\)/))))}$.fn.datepicker=function(options){if(!$.datepicker.initialized){$(document).mousedown($.datepicker._checkExternalClick).find("body").append($.datepicker.dpDiv);$.datepicker.initialized=true}var otherArgs=Array.prototype.slice.call(arguments,1);if(typeof options=="string"&&(options=="isDisabled"||options=="getDate"||options=="widget")){return $.datepicker["_"+options+"Datepicker"].apply($.datepicker,[this[0]].concat(otherArgs))}if(options=="option"&&arguments.length==2&&typeof arguments[1]=="string"){return $.datepicker["_"+options+"Datepicker"].apply($.datepicker,[this[0]].concat(otherArgs))}return this.each(function(){typeof options=="string"?$.datepicker["_"+options+"Datepicker"].apply($.datepicker,[this].concat(otherArgs)):$.datepicker._attachDatepicker(this,options)})};$.datepicker=new Datepicker();$.datepicker.initialized=false;$.datepicker.uuid=new Date().getTime();$.datepicker.version="1.9m3";window["DP_jQuery_"+dpuuid]=$})(jQuery);(function(d,e){var b="ui-dialog ui-widget ui-widget-content ui-corner-all ",a={buttons:true,height:true,maxHeight:true,maxWidth:true,minHeight:true,minWidth:true,width:true},c={maxHeight:true,maxWidth:true,minHeight:true,minWidth:true};d.widget("ui.dialog",{options:{autoOpen:true,buttons:{},closeOnEscape:true,closeText:"close",dialogClass:"",draggable:true,hide:null,height:"auto",maxHeight:false,maxWidth:false,minHeight:150,minWidth:150,modal:false,position:{my:"center",at:"center",of:window,collision:"fit",using:function(g){var f=d(this).css(g).offset().top;if(f<0){d(this).css("top",g.top-f)}}},resizable:true,show:null,stack:true,title:"",width:300,zIndex:1000},_create:function(){this.originalTitle=this.element.attr("title");if(typeof this.originalTitle!=="string"){this.originalTitle=""}this.options.title=this.options.title||this.originalTitle;var n=this,o=n.options,l=o.title||"&#160;",g=d.ui.dialog.getTitleId(n.element),m=(n.uiDialog=d("<div></div>")).appendTo(document.body).hide().addClass(b+o.dialogClass).css({zIndex:o.zIndex}).attr("tabIndex",-1).css("outline",0).keydown(function(p){if(o.closeOnEscape&&p.keyCode&&p.keyCode===d.ui.keyCode.ESCAPE){n.close(p);p.preventDefault()}}).attr({role:"dialog","aria-labelledby":g}).mousedown(function(p){n.moveToTop(false,p)}),i=n.element.show().removeAttr("title").addClass("ui-dialog-content ui-widget-content").appendTo(m),h=(n.uiDialogTitlebar=d("<div></div>")).addClass("ui-dialog-titlebar ui-widget-header ui-corner-all ui-helper-clearfix").prependTo(m),k=d('<a href="#"></a>').addClass("ui-dialog-titlebar-close ui-corner-all").attr("role","button").hover(function(){k.addClass("ui-state-hover")},function(){k.removeClass("ui-state-hover")}).focus(function(){k.addClass("ui-state-focus")}).blur(function(){k.removeClass("ui-state-focus")}).click(function(p){n.close(p);return false}).appendTo(h),j=(n.uiDialogTitlebarCloseText=d("<span></span>")).addClass("ui-icon ui-icon-closethick").text(o.closeText).appendTo(k),f=d("<span></span>").addClass("ui-dialog-title").attr("id",g).html(l).prependTo(h);if(d.isFunction(o.beforeclose)&&!d.isFunction(o.beforeClose)){o.beforeClose=o.beforeclose}h.find("*").add(h).disableSelection();if(o.draggable&&d.fn.draggable){n._makeDraggable()}if(o.resizable&&d.fn.resizable){n._makeResizable()}n._createButtons(o.buttons);n._isOpen=false;if(d.fn.bgiframe){m.bgiframe()}},_init:function(){if(this.options.autoOpen){this.open()}},destroy:function(){var f=this;if(f.overlay){f.overlay.destroy()}f.uiDialog.hide();f.element.unbind(".dialog").removeData("dialog").removeClass("ui-dialog-content ui-widget-content").hide().appendTo("body");f.uiDialog.remove();if(f.originalTitle){f.element.attr("title",f.originalTitle)}return f},widget:function(){return this.uiDialog},close:function(h){var f=this,g;if(false===f._trigger("beforeClose",h)){return}if(f.overlay){f.overlay.destroy()}f.uiDialog.unbind("keypress.ui-dialog");f._isOpen=false;if(f.options.hide){f.uiDialog.hide(f.options.hide,function(){f._trigger("close",h)})}else{f.uiDialog.hide();f._trigger("close",h)}d.ui.dialog.overlay.resize();if(f.options.modal){g=0;d(".ui-dialog").each(function(){if(this!==f.uiDialog[0]){g=Math.max(g,d(this).css("z-index"))}});d.ui.dialog.maxZ=g}return f},isOpen:function(){return this._isOpen},moveToTop:function(j,i){var f=this,h=f.options,g;if((h.modal&&!j)||(!h.stack&&!h.modal)){return f._trigger("focus",i)}if(h.zIndex>d.ui.dialog.maxZ){d.ui.dialog.maxZ=h.zIndex}if(f.overlay){d.ui.dialog.maxZ+=1;f.overlay.$el.css("z-index",d.ui.dialog.overlay.maxZ=d.ui.dialog.maxZ)}g={scrollTop:f.element.attr("scrollTop"),scrollLeft:f.element.attr("scrollLeft")};d.ui.dialog.maxZ+=1;f.uiDialog.css("z-index",d.ui.dialog.maxZ);f.element.attr(g);f._trigger("focus",i);return f},open:function(){if(this._isOpen){return}var g=this,h=g.options,f=g.uiDialog;g.overlay=h.modal?new d.ui.dialog.overlay(g):null;g._size();g._position(h.position);f.show(h.show);g.moveToTop(true);if(h.modal){f.bind("keypress.ui-dialog",function(k){if(k.keyCode!==d.ui.keyCode.TAB){return}var j=d(":tabbable",this),l=j.filter(":first"),i=j.filter(":last");if(k.target===i[0]&&!k.shiftKey){l.focus(1);return false}else{if(k.target===l[0]&&k.shiftKey){i.focus(1);return false}}})}d(g.element.find(":tabbable").get().concat(f.find(".ui-dialog-buttonpane :tabbable").get().concat(f.get()))).eq(0).focus();g._isOpen=true;g._trigger("open");return g},_createButtons:function(i){var h=this,f=false,g=d("<div></div>").addClass("ui-dialog-buttonpane ui-widget-content ui-helper-clearfix"),j=d("<div></div>").addClass("ui-dialog-buttonset").appendTo(g);h.uiDialog.find(".ui-dialog-buttonpane").remove();if(typeof i==="object"&&i!==null){d.each(i,function(){return !(f=true)})}if(f){d.each(i,function(k,m){m=d.isFunction(m)?{click:m,text:k}:m;var l=d('<button type="button"></button>').attr(m,true).unbind("click").click(function(){m.click.apply(h.element[0],arguments)}).appendTo(j);if(d.fn.button){l.button()}});g.appendTo(h.uiDialog)}},_makeDraggable:function(){var f=this,i=f.options,j=d(document),h;function g(k){return{position:k.position,offset:k.offset}}f.uiDialog.draggable({cancel:".ui-dialog-content, .ui-dialog-titlebar-close",handle:".ui-dialog-titlebar",containment:"document",start:function(k,l){h=i.height==="auto"?"auto":d(this).height();d(this).height(d(this).height()).addClass("ui-dialog-dragging");f._trigger("dragStart",k,g(l))},drag:function(k,l){f._trigger("drag",k,g(l))},stop:function(k,l){i.position=[l.position.left-j.scrollLeft(),l.position.top-j.scrollTop()];d(this).removeClass("ui-dialog-dragging").height(h);f._trigger("dragStop",k,g(l));d.ui.dialog.overlay.resize()}})},_makeResizable:function(k){k=(k===e?this.options.resizable:k);var g=this,j=g.options,f=g.uiDialog.css("position"),i=(typeof k==="string"?k:"n,e,s,w,se,sw,ne,nw");function h(l){return{originalPosition:l.originalPosition,originalSize:l.originalSize,position:l.position,size:l.size}}g.uiDialog.resizable({cancel:".ui-dialog-content",containment:"document",alsoResize:g.element,maxWidth:j.maxWidth,maxHeight:j.maxHeight,minWidth:j.minWidth,minHeight:g._minHeight(),handles:i,start:function(l,m){d(this).addClass("ui-dialog-resizing");g._trigger("resizeStart",l,h(m))},resize:function(l,m){g._trigger("resize",l,h(m))},stop:function(l,m){d(this).removeClass("ui-dialog-resizing");j.height=d(this).height();j.width=d(this).width();g._trigger("resizeStop",l,h(m));d.ui.dialog.overlay.resize()}}).css("position",f).find(".ui-resizable-se").addClass("ui-icon ui-icon-grip-diagonal-se")},_minHeight:function(){var f=this.options;if(f.height==="auto"){return f.minHeight}else{return Math.min(f.minHeight,f.height)}},_position:function(g){var h=[],i=[0,0],f;if(g){if(typeof g==="string"||(typeof g==="object"&&"0" in g)){h=g.split?g.split(" "):[g[0],g[1]];if(h.length===1){h[1]=h[0]}d.each(["left","top"],function(k,j){if(+h[k]===h[k]){i[k]=h[k];h[k]=j}});g={my:h.join(" "),at:h.join(" "),offset:i.join(" ")}}g=d.extend({},d.ui.dialog.prototype.options.position,g)}else{g=d.ui.dialog.prototype.options.position}f=this.uiDialog.is(":visible");if(!f){this.uiDialog.show()}this.uiDialog.css({top:0,left:0}).position(g);if(!f){this.uiDialog.hide()}},_setOptions:function(i){var g=this,f={},h=false;d.each(i,function(j,k){g._setOption(j,k);if(j in a){h=true}if(j in c){f[j]=k}});if(h){this._size()}if(this.uiDialog.is(":data(resizable)")){this.uiDialog.resizable("option",f)}},_setOption:function(i,j){var g=this,f=g.uiDialog;switch(i){case"beforeclose":i="beforeClose";break;case"buttons":g._createButtons(j);break;case"closeText":g.uiDialogTitlebarCloseText.text(""+j);break;case"dialogClass":f.removeClass(g.options.dialogClass).addClass(b+j);break;case"disabled":if(j){f.addClass("ui-dialog-disabled")}else{f.removeClass("ui-dialog-disabled")}break;case"draggable":var h=f.is(":data(draggable)");if(h&&!j){f.draggable("destroy")}if(!h&&j){g._makeDraggable()}break;case"position":g._position(j);break;case"resizable":var k=f.is(":data(resizable)");if(k&&!j){f.resizable("destroy")}if(k&&typeof j==="string"){f.resizable("option","handles",j)}if(!k&&j!==false){g._makeResizable(j)}break;case"title":d(".ui-dialog-title",g.uiDialogTitlebar).html(""+(j||"&#160;"));break}d.Widget.prototype._setOption.apply(g,arguments)},_size:function(){var i=this.options,f,h;this.element.show().css({width:"auto",minHeight:0,height:0});if(i.minWidth>i.width){i.width=i.minWidth}f=this.uiDialog.css({height:"auto",width:i.width}).height();h=Math.max(0,i.minHeight-f);if(i.height==="auto"){if(d.support.minHeight){this.element.css({minHeight:h,height:"auto"})}else{this.uiDialog.show();var g=this.element.css("height","auto").height();this.uiDialog.hide();this.element.height(Math.max(g,h))}}else{this.element.height(Math.max(i.height-f,0))}if(this.uiDialog.is(":data(resizable)")){this.uiDialog.resizable("option","minHeight",this._minHeight())}}});d.extend(d.ui.dialog,{version:"1.9m3",uuid:0,maxZ:0,getTitleId:function(f){var g=f.attr("id");if(!g){this.uuid+=1;g=this.uuid}return"ui-dialog-title-"+g},overlay:function(f){this.$el=d.ui.dialog.overlay.create(f)}});d.extend(d.ui.dialog.overlay,{instances:[],oldInstances:[],maxZ:0,events:d.map("focus,mousedown,mouseup,keydown,keypress,click".split(","),function(f){return f+".dialog-overlay"}).join(" "),create:function(g){if(this.instances.length===0){setTimeout(function(){if(d.ui.dialog.overlay.instances.length){d(document).bind(d.ui.dialog.overlay.events,function(h){if(d(h.target).zIndex()<d.ui.dialog.overlay.maxZ){return false}})}},1);d(document).bind("keydown.dialog-overlay",function(h){if(g.options.closeOnEscape&&h.keyCode&&h.keyCode===d.ui.keyCode.ESCAPE){g.close(h);h.preventDefault()}});d(window).bind("resize.dialog-overlay",d.ui.dialog.overlay.resize)}var f=(this.oldInstances.pop()||d("<div></div>").addClass("ui-widget-overlay")).appendTo(document.body).css({width:this.width(),height:this.height()});if(d.fn.bgiframe){f.bgiframe()}this.instances.push(f);return f},destroy:function(f){this.oldInstances.push(this.instances.splice(d.inArray(f,this.instances),1)[0]);if(this.instances.length===0){d([document,window]).unbind(".dialog-overlay")}f.remove();var g=0;d.each(this.instances,function(){g=Math.max(g,this.css("z-index"))});this.maxZ=g},height:function(){var g,f;if(d.browser.msie&&d.browser.version<7){g=Math.max(document.documentElement.scrollHeight,document.body.scrollHeight);f=Math.max(document.documentElement.offsetHeight,document.body.offsetHeight);if(g<f){return d(window).height()+"px"}else{return g+"px"}}else{return d(document).height()+"px"}},width:function(){var f,g;if(d.browser.msie&&d.browser.version<7){f=Math.max(document.documentElement.scrollWidth,document.body.scrollWidth);g=Math.max(document.documentElement.offsetWidth,document.body.offsetWidth);if(f<g){return d(window).width()+"px"}else{return f+"px"}}else{return d(document).width()+"px"}},resize:function(){var f=d([]);d.each(d.ui.dialog.overlay.instances,function(){f=f.add(this)});f.css({width:0,height:0}).css({width:d.ui.dialog.overlay.width(),height:d.ui.dialog.overlay.height()})}});d.extend(d.ui.dialog.overlay.prototype,{destroy:function(){d.ui.dialog.overlay.destroy(this.$el)}})}(jQuery));(function(b){var a=0;b.widget("ui.menu",{_create:function(){var c=this;this.menuId=this.element.attr("id")||"ui-menu-"+a++;this.element.addClass("ui-menu ui-widget ui-widget-content ui-corner-all").attr({id:this.menuId,role:"listbox"}).bind("click.menu",function(d){if(c.options.disabled){return false}if(!b(d.target).closest(".ui-menu-item a").length){return}d.preventDefault();c.select(d)}).bind("mouseover.menu",function(d){if(c.options.disabled){return}var e=b(d.target).closest(".ui-menu-item");if(e.length&&e.parent()[0]===c.element[0]){c.activate(d,e)}}).bind("mouseout.menu",function(d){if(c.options.disabled){return}var e=b(d.target).closest(".ui-menu-item");if(e.length&&e.parent()[0]===c.element[0]){c.deactivate(d)}});this.refresh();if(!this.options.input){this.options.input=this.element.attr("tabIndex",0)}this.options.input.bind("keydown.menu",function(d){if(c.options.disabled){return}switch(d.keyCode){case b.ui.keyCode.PAGE_UP:c.previousPage();d.preventDefault();d.stopImmediatePropagation();break;case b.ui.keyCode.PAGE_DOWN:c.nextPage();d.preventDefault();d.stopImmediatePropagation();break;case b.ui.keyCode.UP:c.previous();d.preventDefault();d.stopImmediatePropagation();break;case b.ui.keyCode.DOWN:c.next();d.preventDefault();d.stopImmediatePropagation();break;case b.ui.keyCode.ENTER:c.select();d.preventDefault();d.stopImmediatePropagation();break}})},destroy:function(){b.Widget.prototype.destroy.apply(this,arguments);this.element.removeClass("ui-menu ui-widget ui-widget-content ui-corner-all").removeAttr("tabIndex").removeAttr("role").removeAttr("aria-activedescendant");this.element.children(".ui-menu-item").removeClass("ui-menu-item").removeAttr("role").children("a").removeClass("ui-corner-all").removeAttr("tabIndex").unbind(".menu")},refresh:function(){var c=this.element.children("li:not(.ui-menu-item):has(a)").addClass("ui-menu-item").attr("role","menuitem");c.children("a").addClass("ui-corner-all").attr("tabIndex",-1)},activate:function(c,j){var k=this;this.deactivate();if(this._hasScroll()){var e=parseFloat(b.curCSS(this.element[0],"borderTopWidth",true))||0,i=parseFloat(b.curCSS(this.element[0],"paddingTop",true))||0,f=j.offset().top-this.element.offset().top-e-i,h=this.element.attr("scrollTop"),g=this.element.height(),d=j.height();if(f<0){this.element.attr("scrollTop",h+f)}else{if(f+d>g){this.element.attr("scrollTop",h+f-g+d)}}}this.active=j.first().children("a").addClass("ui-state-hover").attr("id",function(l,m){return(k.itemId=m||k.menuId+"-activedescendant")}).end();this.element.removeAttr("aria-activedescenant").attr("aria-activedescenant",k.itemId);this._trigger("focus",c,{item:j})},deactivate:function(d){if(!this.active){return}var c=this;this.active.children("a").removeClass("ui-state-hover");b("#"+c.menuId+"-activedescendant").removeAttr("id");this.element.removeAttr("aria-activedescenant");this._trigger("blur",d);this.active=null},next:function(c){this._move("next",".ui-menu-item","first",c)},previous:function(c){this._move("prev",".ui-menu-item","last",c)},first:function(){return this.active&&!this.active.prevAll(".ui-menu-item").length},last:function(){return this.active&&!this.active.nextAll(".ui-menu-item").length},_move:function(g,f,d,e){if(!this.active){this.activate(e,this.element.children(f)[d]());return}var c=this.active[g+"All"](".ui-menu-item").eq(0);if(c.length){this.activate(e,c)}else{this.activate(e,this.element.children(f)[d]())}},nextPage:function(e){if(this._hasScroll()){if(!this.active||this.last()){this.activate(e,this.element.children(".ui-menu-item").first());return}var f=this.active.offset().top,d=this.element.height(),c;this.active.nextAll(".ui-menu-item").each(function(){c=b(this);return b(this).offset().top-f-d<0});this.activate(e,c)}else{this.activate(e,this.element.children(".ui-menu-item")[!this.active||this.last()?"first":"last"]())}},previousPage:function(e){if(this._hasScroll()){if(!this.active||this.first()){this.activate(e,this.element.children(".ui-menu-item").last());return}var f=this.active.offset().top,d=this.element.height(),c;this.active.prevAll(".ui-menu-item").each(function(){c=b(this);return b(this).offset().top-f+d>0});this.activate(e,c)}else{this.activate(e,this.element.children(".ui-menu-item")[!this.active||this.first()?":last":":first"]())}},_hasScroll:function(){return this.element.height()<this.element.attr("scrollHeight")},select:function(c){this._trigger("select",c,{item:this.active})}})}(jQuery));(function(f,g){f.ui=f.ui||{};var d=/left|center|right/,e=/top|center|bottom/,a="center",b=f.fn.position,c=f.fn.offset;f.fn.position=function(i){if(!i||!i.of){return b.apply(this,arguments)}i=f.extend({},i);var m=f(i.of),l=m[0],o=(i.collision||"flip").split(" "),n=i.offset?i.offset.split(" "):[0,0],k,h,j;if(l.nodeType===9){k=m.width();h=m.height();j={top:0,left:0}}else{if(l.setTimeout){k=m.width();h=m.height();j={top:m.scrollTop(),left:m.scrollLeft()}}else{if(l.preventDefault){i.at="left top";k=h=0;j={top:i.of.pageY,left:i.of.pageX}}else{k=m.outerWidth();h=m.outerHeight();j=m.offset()}}}f.each(["my","at"],function(){var p=(i[this]||"").split(" ");if(p.length===1){p=d.test(p[0])?p.concat([a]):e.test(p[0])?[a].concat(p):[a,a]}p[0]=d.test(p[0])?p[0]:a;p[1]=e.test(p[1])?p[1]:a;i[this]=p});if(o.length===1){o[1]=o[0]}n[0]=parseInt(n[0],10)||0;if(n.length===1){n[1]=n[0]}n[1]=parseInt(n[1],10)||0;if(i.at[0]==="right"){j.left+=k}else{if(i.at[0]===a){j.left+=k/2}}if(i.at[1]==="bottom"){j.top+=h}else{if(i.at[1]===a){j.top+=h/2}}j.left+=n[0];j.top+=n[1];return this.each(function(){var s=f(this),v=s.outerWidth(),r=s.outerHeight(),u=parseInt(f.curCSS(this,"marginLeft",true))||0,q=parseInt(f.curCSS(this,"marginTop",true))||0,x=v+u+parseInt(f.curCSS(this,"marginRight",true))||0,y=r+q+parseInt(f.curCSS(this,"marginBottom",true))||0,w=f.extend({},j),p;if(i.my[0]==="right"){w.left-=v}else{if(i.my[0]===a){w.left-=v/2}}if(i.my[1]==="bottom"){w.top-=r}else{if(i.my[1]===a){w.top-=r/2}}w.left=parseInt(w.left);w.top=parseInt(w.top);p={left:w.left-u,top:w.top-q};f.each(["left","top"],function(A,z){if(f.ui.position[o[A]]){f.ui.position[o[A]][z](w,{targetWidth:k,targetHeight:h,elemWidth:v,elemHeight:r,collisionPosition:p,collisionWidth:x,collisionHeight:y,offset:n,my:i.my,at:i.at})}});if(f.fn.bgiframe){s.bgiframe()}s.offset(f.extend(w,{using:i.using}))})};f.ui.position={fit:{left:function(h,i){var k=f(window),j=i.collisionPosition.left+i.collisionWidth-k.width()-k.scrollLeft();h.left=j>0?h.left-j:Math.max(h.left-i.collisionPosition.left,h.left)},top:function(h,i){var k=f(window),j=i.collisionPosition.top+i.collisionHeight-k.height()-k.scrollTop();h.top=j>0?h.top-j:Math.max(h.top-i.collisionPosition.top,h.top)}},flip:{left:function(i,k){if(k.at[0]===a){return}var m=f(window),l=k.collisionPosition.left+k.collisionWidth-m.width()-m.scrollLeft(),h=k.my[0]==="left"?-k.elemWidth:k.my[0]==="right"?k.elemWidth:0,j=k.at[0]==="left"?k.targetWidth:-k.targetWidth,n=-2*k.offset[0];i.left+=k.collisionPosition.left<0?h+j+n:l>0?h+j+n:0},top:function(i,k){if(k.at[1]===a){return}var m=f(window),l=k.collisionPosition.top+k.collisionHeight-m.height()-m.scrollTop(),h=k.my[1]==="top"?-k.elemHeight:k.my[1]==="bottom"?k.elemHeight:0,j=k.at[1]==="top"?k.targetHeight:-k.targetHeight,n=-2*k.offset[1];i.top+=k.collisionPosition.top<0?h+j+n:l>0?h+j+n:0}}};if(!f.offset.setOffset){f.offset.setOffset=function(l,i){if(/static/.test(f.curCSS(l,"position"))){l.style.position="relative"}var k=f(l),n=k.offset(),h=parseInt(f.curCSS(l,"top",true),10)||0,m=parseInt(f.curCSS(l,"left",true),10)||0,j={top:(i.top-n.top)+h,left:(i.left-n.left)+m};if("using" in i){i.using.call(l,j)}else{k.css(j)}};f.fn.offset=function(h){var i=this[0];if(!i||!i.ownerDocument){return null}if(h){return this.each(function(){f.offset.setOffset(this,h)})}return c.call(this)}}}(jQuery));(function(a,b){a.widget("ui.progressbar",{options:{value:0},min:0,max:100,_create:function(){this.element.addClass("ui-progressbar ui-widget ui-widget-content ui-corner-all").attr({role:"progressbar","aria-valuemin":this.min,"aria-valuemax":this.max,"aria-valuenow":this._value()});this.valueDiv=a("<div class='ui-progressbar-value ui-widget-header ui-corner-left'></div>").appendTo(this.element);this._refreshValue()},destroy:function(){this.element.removeClass("ui-progressbar ui-widget ui-widget-content ui-corner-all").removeAttr("role").removeAttr("aria-valuemin").removeAttr("aria-valuemax").removeAttr("aria-valuenow");this.valueDiv.remove();this._superApply("destroy",arguments)},value:function(c){if(c===b){return this._value()}this._setOption("value",c);return this},_setOption:function(c,d){if(c==="value"){this.options.value=d;this._refreshValue();this._trigger("change");if(this._value()===this.max){this._trigger("complete")}}this._superApply("_setOption",arguments)},_value:function(){var c=this.options.value;if(typeof c!=="number"){c=0}return Math.min(this.max,Math.max(this.min,c))},_refreshValue:function(){var c=this.value();this.valueDiv.toggleClass("ui-corner-right",c===this.max).width(c+"%");this.element.attr("aria-valuenow",c)}});a.extend(a.ui.progressbar,{version:"1.9m3"})})(jQuery);(function(b,c){var a=5;b.widget("ui.slider",b.ui.mouse,{widgetEventPrefix:"slide",options:{animate:false,distance:0,max:100,min:0,orientation:"horizontal",range:false,step:1,value:0,values:null},_create:function(){var d=this,e=this.options;this._keySliding=false;this._mouseSliding=false;this._animateOff=true;this._handleIndex=null;this._detectOrientation();this._mouseInit();this.element.addClass("ui-slider ui-slider-"+this.orientation+" ui-widget ui-widget-content ui-corner-all");if(e.disabled){this.element.addClass("ui-slider-disabled ui-disabled")}this.range=b([]);if(e.range){if(e.range===true){this.range=b("<div></div>");if(!e.values){e.values=[this._valueMin(),this._valueMin()]}if(e.values.length&&e.values.length!==2){e.values=[e.values[0],e.values[0]]}}else{this.range=b("<div></div>")}this.range.appendTo(this.element).addClass("ui-slider-range");if(e.range==="min"||e.range==="max"){this.range.addClass("ui-slider-range-"+e.range)}this.range.addClass("ui-widget-header")}if(b(".ui-slider-handle",this.element).length===0){b("<a href='#'></a>").appendTo(this.element).addClass("ui-slider-handle")}if(e.values&&e.values.length){while(b(".ui-slider-handle",this.element).length<e.values.length){b("<a href='#'></a>").appendTo(this.element).addClass("ui-slider-handle")}}this.handles=b(".ui-slider-handle",this.element).addClass("ui-state-default ui-corner-all");this.handle=this.handles.eq(0);this.handles.add(this.range).filter("a").click(function(f){f.preventDefault()}).hover(function(){if(!e.disabled){b(this).addClass("ui-state-hover")}},function(){b(this).removeClass("ui-state-hover")}).focus(function(){if(!e.disabled){b(".ui-slider .ui-state-focus").removeClass("ui-state-focus");b(this).addClass("ui-state-focus")}else{b(this).blur()}}).blur(function(){b(this).removeClass("ui-state-focus")});this.handles.each(function(f){b(this).data("index.ui-slider-handle",f)});this.handles.keydown(function(k){var h=true,g=b(this).data("index.ui-slider-handle"),l,i,f,j;if(d.options.disabled){return}switch(k.keyCode){case b.ui.keyCode.HOME:case b.ui.keyCode.END:case b.ui.keyCode.PAGE_UP:case b.ui.keyCode.PAGE_DOWN:case b.ui.keyCode.UP:case b.ui.keyCode.RIGHT:case b.ui.keyCode.DOWN:case b.ui.keyCode.LEFT:h=false;if(!d._keySliding){d._keySliding=true;b(this).addClass("ui-state-active");l=d._start(k,g);if(l===false){return}}break}j=d.options.step;if(d.options.values&&d.options.values.length){i=f=d.values(g)}else{i=f=d.value()}switch(k.keyCode){case b.ui.keyCode.HOME:f=d._valueMin();break;case b.ui.keyCode.END:f=d._valueMax();break;case b.ui.keyCode.PAGE_UP:f=d._trimAlignValue(i+((d._valueMax()-d._valueMin())/a));break;case b.ui.keyCode.PAGE_DOWN:f=d._trimAlignValue(i-((d._valueMax()-d._valueMin())/a));break;case b.ui.keyCode.UP:case b.ui.keyCode.RIGHT:if(i===d._valueMax()){return}f=d._trimAlignValue(i+j);break;case b.ui.keyCode.DOWN:case b.ui.keyCode.LEFT:if(i===d._valueMin()){return}f=d._trimAlignValue(i-j);break}d._slide(k,g,f);return h}).keyup(function(g){var f=b(this).data("index.ui-slider-handle");if(d._keySliding){d._keySliding=false;d._stop(g,f);d._change(g,f);b(this).removeClass("ui-state-active")}});this._refreshValue();this._animateOff=false},destroy:function(){this.handles.remove();this.range.remove();this.element.removeClass("ui-slider ui-slider-horizontal ui-slider-vertical ui-slider-disabled ui-widget ui-widget-content ui-corner-all").removeData("slider").unbind(".slider");this._mouseDestroy();return this},_mouseCapture:function(f){var g=this.options,j,l,e,h,n,k,m,i,d;if(g.disabled){return false}this.elementSize={width:this.element.outerWidth(),height:this.element.outerHeight()};this.elementOffset=this.element.offset();j={x:f.pageX,y:f.pageY};l=this._normValueFromMouse(j);e=this._valueMax()-this._valueMin()+1;n=this;this.handles.each(function(o){var p=Math.abs(l-n.values(o));if(e>p){e=p;h=b(this);k=o}});if(g.range===true&&this.values(1)===g.min){k+=1;h=b(this.handles[k])}m=this._start(f,k);if(m===false){return false}this._mouseSliding=true;n._handleIndex=k;h.addClass("ui-state-active").focus();i=h.offset();d=!b(f.target).parents().andSelf().is(".ui-slider-handle");this._clickOffset=d?{left:0,top:0}:{left:f.pageX-i.left-(h.width()/2),top:f.pageY-i.top-(h.height()/2)-(parseInt(h.css("borderTopWidth"),10)||0)-(parseInt(h.css("borderBottomWidth"),10)||0)+(parseInt(h.css("marginTop"),10)||0)};this._slide(f,k,l);this._animateOff=true;return true},_mouseStart:function(d){return true},_mouseDrag:function(f){var d={x:f.pageX,y:f.pageY},e=this._normValueFromMouse(d);this._slide(f,this._handleIndex,e);return false},_mouseStop:function(d){this.handles.removeClass("ui-state-active");this._mouseSliding=false;this._stop(d,this._handleIndex);this._change(d,this._handleIndex);this._handleIndex=null;this._clickOffset=null;this._animateOff=false;return false},_detectOrientation:function(){this.orientation=(this.options.orientation==="vertical")?"vertical":"horizontal"},_normValueFromMouse:function(e){var d,h,g,f,i;if(this.orientation==="horizontal"){d=this.elementSize.width;h=e.x-this.elementOffset.left-(this._clickOffset?this._clickOffset.left:0)}else{d=this.elementSize.height;h=e.y-this.elementOffset.top-(this._clickOffset?this._clickOffset.top:0)}g=(h/d);if(g>1){g=1}if(g<0){g=0}if(this.orientation==="vertical"){g=1-g}f=this._valueMax()-this._valueMin();i=this._valueMin()+g*f;return this._trimAlignValue(i)},_start:function(f,e){var d={handle:this.handles[e],value:this.value()};if(this.options.values&&this.options.values.length){d.value=this.values(e);d.values=this.values()}return this._trigger("start",f,d)},_slide:function(h,g,f){var d,e,i;if(this.options.values&&this.options.values.length){d=this.values(g?0:1);if((this.options.values.length===2&&this.options.range===true)&&((g===0&&f>d)||(g===1&&f<d))){f=d}if(f!==this.values(g)){e=this.values();e[g]=f;i=this._trigger("slide",h,{handle:this.handles[g],value:f,values:e});d=this.values(g?0:1);if(i!==false){this.values(g,f,true)}}}else{if(f!==this.value()){i=this._trigger("slide",h,{handle:this.handles[g],value:f});if(i!==false){this.value(f)}}}},_stop:function(f,e){var d={handle:this.handles[e],value:this.value()};if(this.options.values&&this.options.values.length){d.value=this.values(e);d.values=this.values()}this._trigger("stop",f,d)},_change:function(f,e){if(!this._keySliding&&!this._mouseSliding){var d={handle:this.handles[e],value:this.value()};if(this.options.values&&this.options.values.length){d.value=this.values(e);d.values=this.values()}this._trigger("change",f,d)}},value:function(d){if(arguments.length){this.options.value=this._trimAlignValue(d);this._refreshValue();this._change(null,0)}return this._value()},values:function(e,h){var g,d,f;if(arguments.length>1){this.options.values[e]=this._trimAlignValue(h);this._refreshValue();this._change(null,e)}if(arguments.length){if(b.isArray(arguments[0])){g=this.options.values;d=arguments[0];for(f=0;f<g.length;f+=1){g[f]=this._trimAlignValue(d[f]);this._change(null,f)}this._refreshValue()}else{if(this.options.values&&this.options.values.length){return this._values(e)}else{return this.value()}}}else{return this._values()}},_setOption:function(e,f){var d,g=0;if(b.isArray(this.options.values)){g=this.options.values.length}this._superApply("_setOption",arguments);switch(e){case"disabled":if(f){this.handles.filter(".ui-state-focus").blur();this.handles.removeClass("ui-state-hover");this.handles.attr("disabled","disabled");this.element.addClass("ui-disabled")}else{this.handles.removeAttr("disabled");this.element.removeClass("ui-disabled")}break;case"orientation":this._detectOrientation();this.element.removeClass("ui-slider-horizontal ui-slider-vertical").addClass("ui-slider-"+this.orientation);this._refreshValue();break;case"value":this._animateOff=true;this._refreshValue();this._change(null,0);this._animateOff=false;break;case"values":this._animateOff=true;this._refreshValue();for(d=0;d<g;d+=1){this._change(null,d)}this._animateOff=false;break}},_value:function(){var d=this.options.value;d=this._trimAlignValue(d);return d},_values:function(d){var g,f,e;if(arguments.length){g=this.options.values[d];g=this._trimAlignValue(g);return g}else{f=this.options.values.slice();for(e=0;e<f.length;e+=1){f[e]=this._trimAlignValue(f[e])}return f}},_trimAlignValue:function(g){if(g<this._valueMin()){return this._valueMin()}if(g>this._valueMax()){return this._valueMax()}var d=(this.options.step>0)?this.options.step:1,f=g%d,e=g-f;if(Math.abs(f)*2>=d){e+=(f>0)?d:(-d)}return parseFloat(e.toFixed(5))},_valueMin:function(){return this.options.min},_valueMax:function(){return this.options.max},_refreshValue:function(){var g=this.options.range,f=this.options,m=this,e=(!this._animateOff)?f.animate:false,h,d={},i,k,j,l;if(this.options.values&&this.options.values.length){this.handles.each(function(o,n){h=(m.values(o)-m._valueMin())/(m._valueMax()-m._valueMin())*100;d[m.orientation==="horizontal"?"left":"bottom"]=h+"%";b(this).stop(1,1)[e?"animate":"css"](d,f.animate);if(m.options.range===true){if(m.orientation==="horizontal"){if(o===0){m.range.stop(1,1)[e?"animate":"css"]({left:h+"%"},f.animate)}if(o===1){m.range[e?"animate":"css"]({width:(h-i)+"%"},{queue:false,duration:f.animate})}}else{if(o===0){m.range.stop(1,1)[e?"animate":"css"]({bottom:(h)+"%"},f.animate)}if(o===1){m.range[e?"animate":"css"]({height:(h-i)+"%"},{queue:false,duration:f.animate})}}}i=h})}else{k=this.value();j=this._valueMin();l=this._valueMax();h=(l!==j)?(k-j)/(l-j)*100:0;d[m.orientation==="horizontal"?"left":"bottom"]=h+"%";this.handle.stop(1,1)[e?"animate":"css"](d,f.animate);if(g==="min"&&this.orientation==="horizontal"){this.range.stop(1,1)[e?"animate":"css"]({width:h+"%"},f.animate)}if(g==="max"&&this.orientation==="horizontal"){this.range[e?"animate":"css"]({width:(100-h)+"%"},{queue:false,duration:f.animate})}if(g==="min"&&this.orientation==="vertical"){this.range.stop(1,1)[e?"animate":"css"]({height:h+"%"},f.animate)}if(g==="max"&&this.orientation==="vertical"){this.range[e?"animate":"css"]({height:(100-h)+"%"},{queue:false,duration:f.animate})}}}});b.extend(b.ui.slider,{version:"1.9m3"})}(jQuery));(function(a){var b=10;a.widget("ui.spinner",{options:{incremental:true,max:null,min:null,numberformat:null,step:null,value:null},_create:function(){this._draw();this._markupOptions();this._mousewheel();this._aria()},_markupOptions:function(){var c=this;a.each({min:-Number.MAX_VALUE,max:Number.MAX_VALUE,step:1},function(d,e){if(c.options[d]===null){var f=c.element.attr(d);c.options[d]=typeof f=="string"&&f.length>0?c._parse(f):e}});this.value(this.options.value!==null?this.options.value:this.element.val()||0)},_draw:function(){var c=this,d=c.options;var e=this.uiSpinner=c.element.addClass("ui-spinner-input").attr("autocomplete","off").wrap(c._uiSpinnerHtml()).parent().append(c._buttonHtml()).hover(function(){if(!d.disabled){a(this).addClass("ui-state-hover")}c.hovered=true},function(){a(this).removeClass("ui-state-hover");c.hovered=false});if(!a.support.opacity&&e.css("display")=="inline-block"&&a.browser.version<8){e.css("display","inline")}this.element.bind("keydown.spinner",function(f){if(c.options.disabled){return}if(c._start(f)){return c._keydown(f)}return true}).bind("keyup.spinner",function(f){if(c.options.disabled){return}if(c.spinning){c._stop(f);c._change(f)}}).bind("focus.spinner",function(){e.addClass("ui-state-active");c.focused=true}).bind("blur.spinner",function(f){c.value(c.element.val());if(!c.hovered){e.removeClass("ui-state-active")}c.focused=false});this.buttons=e.find(".ui-spinner-button").attr("tabIndex",-1).button().removeClass("ui-corner-all").bind("mousedown",function(f){if(c.options.disabled){return}if(c._start(f)===false){return false}c._repeat(null,a(this).hasClass("ui-spinner-up")?1:-1,f)}).bind("mouseup",function(f){if(c.options.disabled){return}if(c.spinning){c._stop(f);c._change(f)}}).bind("mouseenter",function(){if(c.options.disabled){return}if(a(this).hasClass("ui-state-active")){if(c._start(event)===false){return false}c._repeat(null,a(this).hasClass("ui-spinner-up")?1:-1,event)}}).bind("mouseleave",function(){if(c.spinning){c._stop(event);c._change(event)}});if(d.disabled){this.disable()}},_keydown:function(d){var e=this.options,c=a.ui.keyCode;switch(d.keyCode){case c.UP:this._repeat(null,1,d);return false;case c.DOWN:this._repeat(null,-1,d);return false;case c.PAGE_UP:this._repeat(null,b,d);return false;case c.PAGE_DOWN:this._repeat(null,-b,d);return false;case c.ENTER:this.value(this.element.val())}return true},_mousewheel:function(){if(!a.fn.mousewheel){return}var c=this;this.element.bind("mousewheel.spinner",function(d,e){if(c.options.disabled){return}if(!c.spinning&&!c._start(d)){return false}c._spin((e>0?1:-1)*c.options.step,d);clearTimeout(c.timeout);c.timeout=setTimeout(function(){if(c.spinning){c._stop(d);c._change(d)}},100);d.preventDefault()})},_uiSpinnerHtml:function(){return'<div role="spinbutton" class="ui-spinner ui-state-default ui-widget ui-widget-content ui-corner-all"></div>'},_buttonHtml:function(){return'<a class="ui-spinner-button ui-spinner-up ui-corner-tr"><span class="ui-icon ui-icon-triangle-1-n">&#9650;</span></a><a class="ui-spinner-button ui-spinner-down ui-corner-br"><span class="ui-icon ui-icon-triangle-1-s">&#9660;</span></a>'},_start:function(c){if(!this.spinning&&this._trigger("start",c)!==false){if(!this.counter){this.counter=1}this.spinning=true;return true}return false},_repeat:function(e,d,f){var c=this;e=e||500;clearTimeout(this.timer);this.timer=setTimeout(function(){c._repeat(40,d,f)},e);c._spin(d*c.options.step,f)},_spin:function(e,d){if(!this.counter){this.counter=1}var c=this.value()+e*(this.options.incremental&&this.counter>20?this.counter>100?this.counter>200?100:10:2:1);if(this._trigger("spin",d,{value:c})!==false){this.value(c);this.counter++}},_stop:function(c){this.counter=0;if(this.timer){window.clearTimeout(this.timer)}this.element[0].focus();this.spinning=false;this._trigger("stop",c)},_change:function(c){this._trigger("change",c)},_setOption:function(c,d){if(c=="value"){d=this._parse(d);if(d<this.options.min){d=this.options.min}if(d>this.options.max){d=this.options.max}}if(c=="disabled"){if(d){this.element.attr("disabled",true);this.buttons.button("disable")}else{this.element.removeAttr("disabled");this.buttons.button("enable")}}a.Widget.prototype._setOption.call(this,c,d)},_setOptions:function(c){a.Widget.prototype._setOptions.call(this,c);if("value" in c){this._format(this.options.value)}this._aria()},_aria:function(){this.uiSpinner.attr("aria-valuemin",this.options.min).attr("aria-valuemax",this.options.max).attr("aria-valuenow",this.options.value)},_parse:function(e){var d=e;if(typeof e=="string"){if(this.options.numberformat=="C"&&window.Globalization){var c=Globalization.culture||Globalization.cultures["default"];e=e.replace(c.numberFormat.currency.symbol,"")}e=window.Globalization&&this.options.numberformat?Globalization.parseFloat(e):+e}return isNaN(e)?null:e},_format:function(c){var c=this.options.value;this.element.val(window.Globalization&&this.options.numberformat?Globalization.format(c,this.options.numberformat):c)},destroy:function(){this.element.removeClass("ui-spinner-input").removeAttr("disabled").removeAttr("autocomplete");a.Widget.prototype.destroy.call(this);this.uiSpinner.replaceWith(this.element)},stepUp:function(c){this._spin((c||1)*this.options.step)},stepDown:function(c){this._spin((c||1)*-this.options.step)},pageUp:function(c){this.stepUp((c||1)*b)},pageDown:function(c){this.stepDown((c||1)*b)},value:function(c){if(!arguments.length){return this._parse(this.element.val())}this.option("value",c)},widget:function(){return this.uiSpinner}})})(jQuery);(function(d,f){var c=0,b=0;function e(){return ++c}function a(){return ++b}d.widget("ui.tabs",{options:{add:null,ajaxOptions:null,cache:false,cookie:null,collapsible:false,disable:null,disabled:[],enable:null,event:"click",fx:null,idPrefix:"ui-tabs-",load:null,panelTemplate:"<div></div>",remove:null,select:null,show:null,spinner:"<em>Loading&#8230;</em>",tabTemplate:"<li><a href='#{href}'><span>#{label}</span></a></li>"},_create:function(){this._tabify(true)},_setOption:function(g,h){if(g=="selected"){if(this.options.collapsible&&h==this.options.selected){return}this.select(h)}else{this.options[g]=h;this._tabify()}},_tabId:function(g){return g.title&&g.title.replace(/\s/g,"_").replace(/[^\w\u00c0-\uFFFF-]/g,"")||this.options.idPrefix+e()},_sanitizeSelector:function(g){return g.replace(/:/g,"\\:")},_cookie:function(){var g=this.cookie||(this.cookie=this.options.cookie.name||"ui-tabs-"+a());return d.cookie.apply(null,[g].concat(d.makeArray(arguments)))},_ui:function(h,g){return{tab:h,panel:g,index:this.anchors.index(h)}},_cleanup:function(){this.lis.filter(".ui-state-processing").removeClass("ui-state-processing").find("span:data(label.tabs)").each(function(){var g=d(this);g.html(g.data("label.tabs")).removeData("label.tabs")})},_tabify:function(u){var v=this,j=this.options,h=/^#.+/;this.list=this.element.find("ol,ul").eq(0);this.lis=d(" > li:has(a[href])",this.list);this.anchors=this.lis.map(function(){return d("a",this)[0]});this.panels=d([]);this.anchors.each(function(x,o){var w=d(o).attr("href");var y=w.split("#")[0],z;if(y&&(y===location.toString().split("#")[0]||(z=d("base")[0])&&y===z.href)){w=o.hash;o.href=w}if(h.test(w)){v.panels=v.panels.add(v._sanitizeSelector(w))}else{if(w&&w!=="#"){d.data(o,"href.tabs",w);d.data(o,"load.tabs",w.replace(/#.*$/,""));var B=v._tabId(o);o.href="#"+B;var A=d("#"+B);if(!A.length){A=d(j.panelTemplate).attr("id",B).addClass("ui-tabs-panel ui-widget-content ui-corner-bottom").insertAfter(v.panels[x-1]||v.list);A.data("destroy.tabs",true)}v.panels=v.panels.add(A)}else{j.disabled.push(x)}}});if(u){this.element.addClass("ui-tabs ui-widget ui-widget-content ui-corner-all");this.list.addClass("ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all");this.lis.addClass("ui-state-default ui-corner-top");this.panels.addClass("ui-tabs-panel ui-widget-content ui-corner-bottom");if(j.selected===f){if(location.hash){this.anchors.each(function(w,o){if(o.hash==location.hash){j.selected=w;return false}})}if(typeof j.selected!=="number"&&j.cookie){j.selected=parseInt(v._cookie(),10)}if(typeof j.selected!=="number"&&this.lis.filter(".ui-tabs-selected").length){j.selected=this.lis.index(this.lis.filter(".ui-tabs-selected"))}j.selected=j.selected||(this.lis.length?0:-1)}else{if(j.selected===null){j.selected=-1}}j.selected=((j.selected>=0&&this.anchors[j.selected])||j.selected<0)?j.selected:0;j.disabled=d.unique(j.disabled.concat(d.map(this.lis.filter(".ui-state-disabled"),function(w,o){return v.lis.index(w)}))).sort();if(d.inArray(j.selected,j.disabled)!=-1){j.disabled.splice(d.inArray(j.selected,j.disabled),1)}this.panels.addClass("ui-tabs-hide");this.lis.removeClass("ui-tabs-selected ui-state-active");if(j.selected>=0&&this.anchors.length){d(v._sanitizeSelector(v.anchors[j.selected].hash)).removeClass("ui-tabs-hide");this.lis.eq(j.selected).addClass("ui-tabs-selected ui-state-active");v.element.queue("tabs",function(){v._trigger("show",null,v._ui(v.anchors[j.selected],d(v._sanitizeSelector(v.anchors[j.selected].hash))))});this.load(j.selected)}d(window).bind("unload",function(){v.lis.add(v.anchors).unbind(".tabs");v.lis=v.anchors=v.panels=null})}else{j.selected=this.lis.index(this.lis.filter(".ui-tabs-selected"))}this.element[j.collapsible?"addClass":"removeClass"]("ui-tabs-collapsible");if(j.cookie){this._cookie(j.selected,j.cookie)}for(var m=0,s;(s=this.lis[m]);m++){d(s)[d.inArray(m,j.disabled)!=-1&&!d(s).hasClass("ui-tabs-selected")?"addClass":"removeClass"]("ui-state-disabled")}if(j.cache===false){this.anchors.removeData("cache.tabs")}this.lis.add(this.anchors).unbind(".tabs");if(j.event!=="mouseover"){var l=function(o,i){if(i.is(":not(.ui-state-disabled)")){i.addClass("ui-state-"+o)}};var p=function(o,i){i.removeClass("ui-state-"+o)};this.lis.bind("mouseover.tabs",function(){l("hover",d(this))});this.lis.bind("mouseout.tabs",function(){p("hover",d(this))});this.anchors.bind("focus.tabs",function(){l("focus",d(this).closest("li"))});this.anchors.bind("blur.tabs",function(){p("focus",d(this).closest("li"))})}var g,n;if(j.fx){if(d.isArray(j.fx)){g=j.fx[0];n=j.fx[1]}else{g=n=j.fx}}function k(i,o){i.css("display","");if(!d.support.opacity&&o.opacity){i[0].style.removeAttribute("filter")}}var q=n?function(i,o){d(i).closest("li").addClass("ui-tabs-selected ui-state-active");o.hide().removeClass("ui-tabs-hide").animate(n,n.duration||"normal",function(){k(o,n);v._trigger("show",null,v._ui(i,o[0]))})}:function(i,o){d(i).closest("li").addClass("ui-tabs-selected ui-state-active");o.removeClass("ui-tabs-hide");v._trigger("show",null,v._ui(i,o[0]))};var r=g?function(o,i){i.animate(g,g.duration||"normal",function(){v.lis.removeClass("ui-tabs-selected ui-state-active");i.addClass("ui-tabs-hide");k(i,g);v.element.dequeue("tabs")})}:function(o,i,w){v.lis.removeClass("ui-tabs-selected ui-state-active");i.addClass("ui-tabs-hide");v.element.dequeue("tabs")};this.anchors.bind(j.event+".tabs",function(){var o=this,x=d(o).closest("li"),i=v.panels.filter(":not(.ui-tabs-hide)"),w=d(v._sanitizeSelector(o.hash));if((x.hasClass("ui-tabs-selected")&&!j.collapsible)||x.hasClass("ui-state-disabled")||x.hasClass("ui-state-processing")||v.panels.filter(":animated").length||v._trigger("select",null,v._ui(this,w[0]))===false){this.blur();return false}j.selected=v.anchors.index(this);v.abort();if(j.collapsible){if(x.hasClass("ui-tabs-selected")){j.selected=-1;if(j.cookie){v._cookie(j.selected,j.cookie)}v.element.queue("tabs",function(){r(o,i)}).dequeue("tabs");this.blur();return false}else{if(!i.length){if(j.cookie){v._cookie(j.selected,j.cookie)}v.element.queue("tabs",function(){q(o,w)});v.load(v.anchors.index(this));this.blur();return false}}}if(j.cookie){v._cookie(j.selected,j.cookie)}if(w.length){if(i.length){v.element.queue("tabs",function(){r(o,i)})}v.element.queue("tabs",function(){q(o,w)});v.load(v.anchors.index(this))}else{throw"jQuery UI Tabs: Mismatching fragment identifier."}if(d.browser.msie){this.blur()}});this.anchors.bind("click.tabs",function(){return false})},_getIndex:function(g){if(typeof g=="string"){g=this.anchors.index(this.anchors.filter("[href$="+g+"]"))}return g},destroy:function(){var g=this.options;this.abort();this.element.unbind(".tabs").removeClass("ui-tabs ui-widget ui-widget-content ui-corner-all ui-tabs-collapsible").removeData("tabs");this.list.removeClass("ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all");this.anchors.each(function(){var h=d.data(this,"href.tabs");if(h){this.href=h}var i=d(this).unbind(".tabs");d.each(["href","load","cache"],function(j,k){i.removeData(k+".tabs")})});this.lis.unbind(".tabs").add(this.panels).each(function(){if(d.data(this,"destroy.tabs")){d(this).remove()}else{d(this).removeClass(["ui-state-default","ui-corner-top","ui-tabs-selected","ui-state-active","ui-state-hover","ui-state-focus","ui-state-disabled","ui-tabs-panel","ui-widget-content","ui-corner-bottom","ui-tabs-hide"].join(" "))}});if(g.cookie){this._cookie(null,g.cookie)}return this},add:function(j,i,h){if(h===f){h=this.anchors.length}var g=this,l=this.options,n=d(l.tabTemplate.replace(/#\{href\}/g,j).replace(/#\{label\}/g,i)),m=!j.indexOf("#")?j.replace("#",""):this._tabId(d("a",n)[0]);n.addClass("ui-state-default ui-corner-top").data("destroy.tabs",true);var k=d("#"+m);if(!k.length){k=d(l.panelTemplate).attr("id",m).data("destroy.tabs",true)}k.addClass("ui-tabs-panel ui-widget-content ui-corner-bottom ui-tabs-hide");if(h>=this.lis.length){n.appendTo(this.list);k.appendTo(this.list[0].parentNode)}else{n.insertBefore(this.lis[h]);k.insertBefore(this.panels[h])}l.disabled=d.map(l.disabled,function(p,o){return p>=h?++p:p});this._tabify();if(this.anchors.length==1){l.selected=0;n.addClass("ui-tabs-selected ui-state-active");k.removeClass("ui-tabs-hide");this.element.queue("tabs",function(){g._trigger("show",null,g._ui(g.anchors[0],g.panels[0]))});this.load(0)}this._trigger("add",null,this._ui(this.anchors[h],this.panels[h]));return this},remove:function(g){g=this._getIndex(g);var i=this.options,j=this.lis.eq(g).remove(),h=this.panels.eq(g).remove();if(j.hasClass("ui-tabs-selected")&&this.anchors.length>1){this.select(g+(g+1<this.anchors.length?1:-1))}i.disabled=d.map(d.grep(i.disabled,function(l,k){return l!=g}),function(l,k){return l>=g?--l:l});this._tabify();this._trigger("remove",null,this._ui(j.find("a")[0],h[0]));return this},enable:function(g){g=this._getIndex(g);var h=this.options;if(d.inArray(g,h.disabled)==-1){return}this.lis.eq(g).removeClass("ui-state-disabled");h.disabled=d.grep(h.disabled,function(k,j){return k!=g});this._trigger("enable",null,this._ui(this.anchors[g],this.panels[g]));return this},disable:function(h){h=this._getIndex(h);var g=this,i=this.options;if(h!=i.selected){this.lis.eq(h).addClass("ui-state-disabled");i.disabled.push(h);i.disabled.sort();this._trigger("disable",null,this._ui(this.anchors[h],this.panels[h]))}return this},select:function(g){g=this._getIndex(g);if(g==-1){if(this.options.collapsible&&this.options.selected!=-1){g=this.options.selected}else{return this}}this.anchors.eq(g).trigger(this.options.event+".tabs");return this},load:function(j){j=this._getIndex(j);var h=this,l=this.options,g=this.anchors.eq(j)[0],i=d.data(g,"load.tabs");this.abort();if(!i||this.element.queue("tabs").length!==0&&d.data(g,"cache.tabs")){this.element.dequeue("tabs");return}this.lis.eq(j).addClass("ui-state-processing");if(l.spinner){var k=d("span",g);k.data("label.tabs",k.html()).html(l.spinner)}this.xhr=d.ajax(d.extend({},l.ajaxOptions,{url:i,success:function(n,m){d(h._sanitizeSelector(g.hash)).html(n);h._cleanup();if(l.cache){d.data(g,"cache.tabs",true)}h._trigger("load",null,h._ui(h.anchors[j],h.panels[j]));try{l.ajaxOptions.success(n,m)}catch(o){}},error:function(o,m,n){h._cleanup();h._trigger("load",null,h._ui(h.anchors[j],h.panels[j]));try{l.ajaxOptions.error(o,m,j,g)}catch(n){}}}));h.element.dequeue("tabs");return this},abort:function(){this.element.queue([]);this.panels.stop(false,true);this.element.queue("tabs",this.element.queue("tabs").splice(-2,2));if(this.xhr){this.xhr.abort();delete this.xhr}this._cleanup();return this},url:function(h,g){this.anchors.eq(h).removeData("cache.tabs").data("load.tabs",g);return this},length:function(){return this.anchors.length}});d.extend(d.ui.tabs,{version:"1.9m3"});d.extend(d.ui.tabs.prototype,{rotation:null,rotate:function(i,k){var g=this,l=this.options;var h=g._rotate||(g._rotate=function(m){clearTimeout(g.rotation);g.rotation=setTimeout(function(){var n=l.selected;g.select(++n<g.anchors.length?n:0)},i);if(m){m.stopPropagation()}});var j=g._unrotate||(g._unrotate=!k?function(m){if(m.clientX){g.rotate(null)}}:function(m){t=l.selected;h()});if(i){this.element.bind("tabsshow",h);this.anchors.bind(l.event+".tabs",j);h()}else{clearTimeout(g.rotation);this.element.unbind("tabsshow",h);this.anchors.unbind(l.event+".tabs",j);delete this._rotate;delete this._unrotate}return this}})})(jQuery);(function(b){var a=0;b.widget("ui.tooltip",{options:{items:"[title]",content:function(){return b(this).attr("title")},position:{my:"left center",at:"right center",offset:"15 0"}},_create:function(){var c=this;this.tooltip=b("<div></div>").attr("id","ui-tooltip-"+a++).attr("role","tooltip").attr("aria-hidden","true").addClass("ui-tooltip ui-widget ui-corner-all ui-widget-content").appendTo(document.body).hide();this.tooltipContent=b("<div></div>").addClass("ui-tooltip-content").appendTo(this.tooltip);this.opacity=this.tooltip.css("opacity");this.element.bind("focus.tooltip mouseover.tooltip",function(d){c.open(d)}).bind("blur.tooltip mouseout.tooltip",function(d){c.close(d)})},enable:function(){this.options.disabled=false},disable:function(){this.options.disabled=true},destroy:function(){this.tooltip.remove();b.Widget.prototype.destroy.apply(this,arguments)},widget:function(){return this.element.pushStack(this.tooltip.get())},open:function(e){var f=b(e&&e.target||this.element).closest(this.options.items);if(this.current&&this.current[0]==f[0]){return}var c=this;this.current=f;this.currentTitle=f.attr("title");var d=this.options.content.call(f[0],function(g){setTimeout(function(){if(c.current==f){c._show(e,f,g)}},13)});if(d){c._show(e,f,d)}},_show:function(d,e,c){if(!c){return}e.attr("title","");if(this.options.disabled){return}this.tooltipContent.html(c);this.tooltip.css({top:0,left:0}).show().position(b.extend({of:e},this.options.position)).hide();this.tooltip.attr("aria-hidden","false");e.attr("aria-describedby",this.tooltip.attr("id"));this.tooltip.stop(false,true).fadeIn();this._trigger("open",d)},close:function(c){if(!this.current){return}var d=this.current.attr("title",this.currentTitle);this.current=null;if(this.options.disabled){return}d.removeAttr("aria-describedby");this.tooltip.attr("aria-hidden","true");this.tooltip.stop(false,true).fadeOut();this._trigger("close",c)}})})(jQuery);jQuery.effects||(function(h,e){h.effects={};h.each(["backgroundColor","borderBottomColor","borderLeftColor","borderRightColor","borderTopColor","borderColor","color","outlineColor"],function(n,m){h.fx.step[m]=function(o){if(!o.colorInit){o.start=l(o.elem,m);o.end=j(o.end);o.colorInit=true}o.elem.style[m]="rgb("+Math.max(Math.min(parseInt((o.pos*(o.end[0]-o.start[0]))+o.start[0],10),255),0)+","+Math.max(Math.min(parseInt((o.pos*(o.end[1]-o.start[1]))+o.start[1],10),255),0)+","+Math.max(Math.min(parseInt((o.pos*(o.end[2]-o.start[2]))+o.start[2],10),255),0)+")"}});function j(n){var m;if(n&&n.constructor==Array&&n.length==3){return n}if(m=/rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)/.exec(n)){return[parseInt(m[1],10),parseInt(m[2],10),parseInt(m[3],10)]}if(m=/rgb\(\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*\)/.exec(n)){return[parseFloat(m[1])*2.55,parseFloat(m[2])*2.55,parseFloat(m[3])*2.55]}if(m=/#([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})/.exec(n)){return[parseInt(m[1],16),parseInt(m[2],16),parseInt(m[3],16)]}if(m=/#([a-fA-F0-9])([a-fA-F0-9])([a-fA-F0-9])/.exec(n)){return[parseInt(m[1]+m[1],16),parseInt(m[2]+m[2],16),parseInt(m[3]+m[3],16)]}if(m=/rgba\(0, 0, 0, 0\)/.exec(n)){return a.transparent}return a[h.trim(n).toLowerCase()]}function l(o,m){var n;do{n=h.curCSS(o,m);if(n!=""&&n!="transparent"||h.nodeName(o,"body")){break}m="backgroundColor"}while(o=o.parentNode);return j(n)}var a={aqua:[0,255,255],azure:[240,255,255],beige:[245,245,220],black:[0,0,0],blue:[0,0,255],brown:[165,42,42],cyan:[0,255,255],darkblue:[0,0,139],darkcyan:[0,139,139],darkgrey:[169,169,169],darkgreen:[0,100,0],darkkhaki:[189,183,107],darkmagenta:[139,0,139],darkolivegreen:[85,107,47],darkorange:[255,140,0],darkorchid:[153,50,204],darkred:[139,0,0],darksalmon:[233,150,122],darkviolet:[148,0,211],fuchsia:[255,0,255],gold:[255,215,0],green:[0,128,0],indigo:[75,0,130],khaki:[240,230,140],lightblue:[173,216,230],lightcyan:[224,255,255],lightgreen:[144,238,144],lightgrey:[211,211,211],lightpink:[255,182,193],lightyellow:[255,255,224],lime:[0,255,0],magenta:[255,0,255],maroon:[128,0,0],navy:[0,0,128],olive:[128,128,0],orange:[255,165,0],pink:[255,192,203],purple:[128,0,128],violet:[128,0,128],red:[255,0,0],silver:[192,192,192],white:[255,255,255],yellow:[255,255,0],transparent:[255,255,255]};var f=["add","remove","toggle"],c={border:1,borderBottom:1,borderColor:1,borderLeft:1,borderRight:1,borderTop:1,borderWidth:1,margin:1,padding:1};function g(){var p=document.defaultView?document.defaultView.getComputedStyle(this,null):this.currentStyle,q={},n,o;if(p&&p.length&&p[0]&&p[p[0]]){var m=p.length;while(m--){n=p[m];if(typeof p[n]=="string"){o=n.replace(/\-(\w)/g,function(r,s){return s.toUpperCase()});q[o]=p[n]}}}else{for(n in p){if(typeof p[n]==="string"){q[n]=p[n]}}}return q}function b(n){var m,o;for(m in n){o=n[m];if(o==null||h.isFunction(o)||m in c||(/scrollbar/).test(m)||(!(/color/i).test(m)&&isNaN(parseFloat(o)))){delete n[m]}}return n}function i(m,o){var p={_:0},n;for(n in o){if(m[n]!=o[n]){p[n]=o[n]}}return p}h.effects.animateClass=function(m,n,p,o){if(h.isFunction(p)){o=p;p=null}return this.each(function(){var u=h(this),q=u.attr("style")||" ",v=b(g.call(this)),s,r=u.attr("className");h.each(f,function(w,x){if(m[x]){u[x+"Class"](m[x])}});s=b(g.call(this));u.attr("className",r);u.animate(i(v,s),n,p,function(){h.each(f,function(w,x){if(m[x]){u[x+"Class"](m[x])}});if(typeof u.attr("style")=="object"){u.attr("style").cssText="";u.attr("style").cssText=q}else{u.attr("style",q)}if(o){o.apply(this,arguments)}})})};h.fn.extend({_addClass:h.fn.addClass,addClass:function(n,m,p,o){return m?h.effects.animateClass.apply(this,[{add:n},m,p,o]):this._addClass(n)},_removeClass:h.fn.removeClass,removeClass:function(n,m,p,o){return m?h.effects.animateClass.apply(this,[{remove:n},m,p,o]):this._removeClass(n)},_toggleClass:h.fn.toggleClass,toggleClass:function(o,n,m,q,p){if(typeof n=="boolean"||n===e){if(!m){return this._toggleClass(o,n)}else{return h.effects.animateClass.apply(this,[(n?{add:o}:{remove:o}),m,q,p])}}else{return h.effects.animateClass.apply(this,[{toggle:o},n,m,q])}},switchClass:function(m,o,n,q,p){return h.effects.animateClass.apply(this,[{add:o,remove:m},n,q,p])}});h.extend(h.effects,{version:"1.9m3",save:function(n,o){for(var m=0;m<o.length;m++){if(o[m]!==null){n.data("ec.storage."+o[m],n[0].style[o[m]])}}},restore:function(n,o){for(var m=0;m<o.length;m++){if(o[m]!==null){n.css(o[m],n.data("ec.storage."+o[m]))}}},setMode:function(m,n){if(n=="toggle"){n=m.is(":hidden")?"show":"hide"}return n},getBaseline:function(n,o){var p,m;switch(n[0]){case"top":p=0;break;case"middle":p=0.5;break;case"bottom":p=1;break;default:p=n[0]/o.height}switch(n[1]){case"left":m=0;break;case"center":m=0.5;break;case"right":m=1;break;default:m=n[1]/o.width}return{x:m,y:p}},createWrapper:function(m){if(m.parent().is(".ui-effects-wrapper")){return m.parent()}var n={width:m.outerWidth(true),height:m.outerHeight(true),"float":m.css("float")},o=h("<div></div>").addClass("ui-effects-wrapper").css({fontSize:"100%",background:"transparent",border:"none",margin:0,padding:0});m.wrap(o);o=m.parent();if(m.css("position")=="static"){o.css({position:"relative"});m.css({position:"relative"})}else{h.extend(n,{position:m.css("position"),zIndex:m.css("z-index")});h.each(["top","left","bottom","right"],function(p,q){n[q]=m.css(q);if(isNaN(parseInt(n[q],10))){n[q]="auto"}});m.css({position:"relative",top:0,left:0})}return o.css(n).show()},removeWrapper:function(m){if(m.parent().is(".ui-effects-wrapper")){return m.parent().replaceWith(m)}return m},setTransition:function(n,p,m,o){o=o||{};h.each(p,function(r,q){unit=n.cssUnit(q);if(unit[0]>0){o[q]=unit[0]*m+unit[1]}});return o}});function d(n,m,o,p){if(typeof n=="object"){p=m;o=null;m=n;n=m.effect}if(h.isFunction(m)){p=m;o=null;m={}}if(typeof m=="number"||h.fx.speeds[m]){p=o;o=m;m={}}if(h.isFunction(o)){p=o;o=null}m=m||{};o=o||m.duration;o=h.fx.off?0:typeof o=="number"?o:h.fx.speeds[o]||h.fx.speeds._default;p=p||m.complete;return[n,m,o,p]}function k(m){if(!m||typeof m==="number"||h.fx.speeds[m]){return true}if(typeof m==="string"&&!h.effects[m]){return true}return false}h.fn.extend({effect:function(p,o,r,u){var n=d.apply(this,arguments),q={options:n[1],duration:n[2],callback:n[3]},s=q.options.mode,m=h.effects[p];if(h.fx.off||!m){if(s){return this[s](q.duration,q.callback)}else{return this.each(function(){if(q.callback){q.callback.call(this)}})}}return m.call(this,q)},_show:h.fn.show,show:function(n){if(k(n)){return this._show.apply(this,arguments)}else{var m=d.apply(this,arguments);m[1].mode="show";return this.effect.apply(this,m)}},_hide:h.fn.hide,hide:function(n){if(k(n)){return this._hide.apply(this,arguments)}else{var m=d.apply(this,arguments);m[1].mode="hide";return this.effect.apply(this,m)}},__toggle:h.fn.toggle,toggle:function(n){if(k(n)||typeof n==="boolean"||h.isFunction(n)){return this.__toggle.apply(this,arguments)}else{var m=d.apply(this,arguments);m[1].mode="toggle";return this.effect.apply(this,m)}},cssUnit:function(m){var n=this.css(m),o=[];h.each(["em","px","%","pt"],function(p,q){if(n.indexOf(q)>0){o=[parseFloat(n),q]}});return o}});h.easing.jswing=h.easing.swing;h.extend(h.easing,{def:"easeOutQuad",swing:function(n,o,m,q,p){return h.easing[h.easing.def](n,o,m,q,p)},easeInQuad:function(n,o,m,q,p){return q*(o/=p)*o+m},easeOutQuad:function(n,o,m,q,p){return -q*(o/=p)*(o-2)+m},easeInOutQuad:function(n,o,m,q,p){if((o/=p/2)<1){return q/2*o*o+m}return -q/2*((--o)*(o-2)-1)+m},easeInCubic:function(n,o,m,q,p){return q*(o/=p)*o*o+m},easeOutCubic:function(n,o,m,q,p){return q*((o=o/p-1)*o*o+1)+m},easeInOutCubic:function(n,o,m,q,p){if((o/=p/2)<1){return q/2*o*o*o+m}return q/2*((o-=2)*o*o+2)+m},easeInQuart:function(n,o,m,q,p){return q*(o/=p)*o*o*o+m},easeOutQuart:function(n,o,m,q,p){return -q*((o=o/p-1)*o*o*o-1)+m},easeInOutQuart:function(n,o,m,q,p){if((o/=p/2)<1){return q/2*o*o*o*o+m}return -q/2*((o-=2)*o*o*o-2)+m},easeInQuint:function(n,o,m,q,p){return q*(o/=p)*o*o*o*o+m},easeOutQuint:function(n,o,m,q,p){return q*((o=o/p-1)*o*o*o*o+1)+m},easeInOutQuint:function(n,o,m,q,p){if((o/=p/2)<1){return q/2*o*o*o*o*o+m}return q/2*((o-=2)*o*o*o*o+2)+m},easeInSine:function(n,o,m,q,p){return -q*Math.cos(o/p*(Math.PI/2))+q+m},easeOutSine:function(n,o,m,q,p){return q*Math.sin(o/p*(Math.PI/2))+m},easeInOutSine:function(n,o,m,q,p){return -q/2*(Math.cos(Math.PI*o/p)-1)+m},easeInExpo:function(n,o,m,q,p){return(o==0)?m:q*Math.pow(2,10*(o/p-1))+m},easeOutExpo:function(n,o,m,q,p){return(o==p)?m+q:q*(-Math.pow(2,-10*o/p)+1)+m},easeInOutExpo:function(n,o,m,q,p){if(o==0){return m}if(o==p){return m+q}if((o/=p/2)<1){return q/2*Math.pow(2,10*(o-1))+m}return q/2*(-Math.pow(2,-10*--o)+2)+m},easeInCirc:function(n,o,m,q,p){return -q*(Math.sqrt(1-(o/=p)*o)-1)+m},easeOutCirc:function(n,o,m,q,p){return q*Math.sqrt(1-(o=o/p-1)*o)+m},easeInOutCirc:function(n,o,m,q,p){if((o/=p/2)<1){return -q/2*(Math.sqrt(1-o*o)-1)+m}return q/2*(Math.sqrt(1-(o-=2)*o)+1)+m},easeInElastic:function(n,q,m,w,v){var r=1.70158;var u=0;var o=w;if(q==0){return m}if((q/=v)==1){return m+w}if(!u){u=v*0.3}if(o<Math.abs(w)){o=w;var r=u/4}else{var r=u/(2*Math.PI)*Math.asin(w/o)}return -(o*Math.pow(2,10*(q-=1))*Math.sin((q*v-r)*(2*Math.PI)/u))+m},easeOutElastic:function(n,q,m,w,v){var r=1.70158;var u=0;var o=w;if(q==0){return m}if((q/=v)==1){return m+w}if(!u){u=v*0.3}if(o<Math.abs(w)){o=w;var r=u/4}else{var r=u/(2*Math.PI)*Math.asin(w/o)}return o*Math.pow(2,-10*q)*Math.sin((q*v-r)*(2*Math.PI)/u)+w+m},easeInOutElastic:function(n,q,m,w,v){var r=1.70158;var u=0;var o=w;if(q==0){return m}if((q/=v/2)==2){return m+w}if(!u){u=v*(0.3*1.5)}if(o<Math.abs(w)){o=w;var r=u/4}else{var r=u/(2*Math.PI)*Math.asin(w/o)}if(q<1){return -0.5*(o*Math.pow(2,10*(q-=1))*Math.sin((q*v-r)*(2*Math.PI)/u))+m}return o*Math.pow(2,-10*(q-=1))*Math.sin((q*v-r)*(2*Math.PI)/u)*0.5+w+m},easeInBack:function(n,o,m,r,q,p){if(p==e){p=1.70158}return r*(o/=q)*o*((p+1)*o-p)+m},easeOutBack:function(n,o,m,r,q,p){if(p==e){p=1.70158}return r*((o=o/q-1)*o*((p+1)*o+p)+1)+m},easeInOutBack:function(n,o,m,r,q,p){if(p==e){p=1.70158}if((o/=q/2)<1){return r/2*(o*o*(((p*=(1.525))+1)*o-p))+m}return r/2*((o-=2)*o*(((p*=(1.525))+1)*o+p)+2)+m},easeInBounce:function(n,o,m,q,p){return q-h.easing.easeOutBounce(n,p-o,0,q,p)+m},easeOutBounce:function(n,o,m,q,p){if((o/=p)<(1/2.75)){return q*(7.5625*o*o)+m}else{if(o<(2/2.75)){return q*(7.5625*(o-=(1.5/2.75))*o+0.75)+m}else{if(o<(2.5/2.75)){return q*(7.5625*(o-=(2.25/2.75))*o+0.9375)+m}else{return q*(7.5625*(o-=(2.625/2.75))*o+0.984375)+m}}}},easeInOutBounce:function(n,o,m,q,p){if(o<p/2){return h.easing.easeInBounce(n,o*2,0,q,p)*0.5+m}return h.easing.easeOutBounce(n,o*2-p,0,q,p)*0.5+q*0.5+m}})})(jQuery);(function(a,b){a.effects.blind=function(c){return this.queue(function(){var e=a(this),d=["position","top","left"];var i=a.effects.setMode(e,c.options.mode||"hide");var h=c.options.direction||"vertical";a.effects.save(e,d);e.show();var k=a.effects.createWrapper(e).css({overflow:"hidden"});var f=(h=="vertical")?"height":"width";var j=(h=="vertical")?k.height():k.width();if(i=="show"){k.css(f,0)}var g={};g[f]=i=="show"?j:0;k.animate(g,c.duration,c.options.easing,function(){if(i=="hide"){e.hide()}a.effects.restore(e,d);a.effects.removeWrapper(e);if(c.callback){c.callback.apply(e[0],arguments)}e.dequeue()})})}})(jQuery);(function(a,b){a.effects.bounce=function(c){return this.queue(function(){var f=a(this),m=["position","top","left"];var l=a.effects.setMode(f,c.options.mode||"effect");var o=c.options.direction||"up";var d=c.options.distance||20;var e=c.options.times||5;var h=c.duration||250;if(/show|hide/.test(l)){m.push("opacity")}a.effects.save(f,m);f.show();a.effects.createWrapper(f);var g=(o=="up"||o=="down")?"top":"left";var q=(o=="up"||o=="left")?"pos":"neg";var d=c.options.distance||(g=="top"?f.outerHeight({margin:true})/3:f.outerWidth({margin:true})/3);if(l=="show"){f.css("opacity",0).css(g,q=="pos"?-d:d)}if(l=="hide"){d=d/(e*2)}if(l!="hide"){e--}if(l=="show"){var j={opacity:1};j[g]=(q=="pos"?"+=":"-=")+d;f.animate(j,h/2,c.options.easing);d=d/2;e--}for(var k=0;k<e;k++){var p={},n={};p[g]=(q=="pos"?"-=":"+=")+d;n[g]=(q=="pos"?"+=":"-=")+d;f.animate(p,h/2,c.options.easing).animate(n,h/2,c.options.easing);d=(l=="hide")?d*2:d/2}if(l=="hide"){var j={opacity:0};j[g]=(q=="pos"?"-=":"+=")+d;f.animate(j,h/2,c.options.easing,function(){f.hide();a.effects.restore(f,m);a.effects.removeWrapper(f);if(c.callback){c.callback.apply(this,arguments)}})}else{var p={},n={};p[g]=(q=="pos"?"-=":"+=")+d;n[g]=(q=="pos"?"+=":"-=")+d;f.animate(p,h/2,c.options.easing).animate(n,h/2,c.options.easing,function(){a.effects.restore(f,m);a.effects.removeWrapper(f);if(c.callback){c.callback.apply(this,arguments)}})}f.queue("fx",function(){f.dequeue()});f.dequeue()})}})(jQuery);(function(a,b){a.effects.clip=function(c){return this.queue(function(){var g=a(this),k=["position","top","left","height","width"];var j=a.effects.setMode(g,c.options.mode||"hide");var l=c.options.direction||"vertical";a.effects.save(g,k);g.show();var d=a.effects.createWrapper(g).css({overflow:"hidden"});var f=g[0].tagName=="IMG"?d:g;var h={size:(l=="vertical")?"height":"width",position:(l=="vertical")?"top":"left"};var e=(l=="vertical")?f.height():f.width();if(j=="show"){f.css(h.size,0);f.css(h.position,e/2)}var i={};i[h.size]=j=="show"?e:0;i[h.position]=j=="show"?0:e/2;f.animate(i,{queue:false,duration:c.duration,easing:c.options.easing,complete:function(){if(j=="hide"){g.hide()}a.effects.restore(g,k);a.effects.removeWrapper(g);if(c.callback){c.callback.apply(g[0],arguments)}g.dequeue()}})})}})(jQuery);(function(a,b){a.effects.drop=function(c){return this.queue(function(){var f=a(this),e=["position","top","left","opacity"];var j=a.effects.setMode(f,c.options.mode||"hide");var i=c.options.direction||"left";a.effects.save(f,e);f.show();a.effects.createWrapper(f);var g=(i=="up"||i=="down")?"top":"left";var d=(i=="up"||i=="left")?"pos":"neg";var k=c.options.distance||(g=="top"?f.outerHeight({margin:true})/2:f.outerWidth({margin:true})/2);if(j=="show"){f.css("opacity",0).css(g,d=="pos"?-k:k)}var h={opacity:j=="show"?1:0};h[g]=(j=="show"?(d=="pos"?"+=":"-="):(d=="pos"?"-=":"+="))+k;f.animate(h,{queue:false,duration:c.duration,easing:c.options.easing,complete:function(){if(j=="hide"){f.hide()}a.effects.restore(f,e);a.effects.removeWrapper(f);if(c.callback){c.callback.apply(this,arguments)}f.dequeue()}})})}})(jQuery);(function(a,b){a.effects.explode=function(c){return this.queue(function(){var l=c.options.pieces?Math.round(Math.sqrt(c.options.pieces)):3;var f=c.options.pieces?Math.round(Math.sqrt(c.options.pieces)):3;c.options.mode=c.options.mode=="toggle"?(a(this).is(":visible")?"hide":"show"):c.options.mode;var k=a(this).show().css("visibility","hidden");var m=k.offset();m.top-=parseInt(k.css("marginTop"),10)||0;m.left-=parseInt(k.css("marginLeft"),10)||0;var h=k.outerWidth(true);var d=k.outerHeight(true);for(var g=0;g<l;g++){for(var e=0;e<f;e++){k.clone().appendTo("body").wrap("<div></div>").css({position:"absolute",visibility:"visible",left:-e*(h/f),top:-g*(d/l)}).parent().addClass("ui-effects-explode").css({position:"absolute",overflow:"hidden",width:h/f,height:d/l,left:m.left+e*(h/f)+(c.options.mode=="show"?(e-Math.floor(f/2))*(h/f):0),top:m.top+g*(d/l)+(c.options.mode=="show"?(g-Math.floor(l/2))*(d/l):0),opacity:c.options.mode=="show"?0:1}).animate({left:m.left+e*(h/f)+(c.options.mode=="show"?0:(e-Math.floor(f/2))*(h/f)),top:m.top+g*(d/l)+(c.options.mode=="show"?0:(g-Math.floor(l/2))*(d/l)),opacity:c.options.mode=="show"?1:0},c.duration||500)}}setTimeout(function(){c.options.mode=="show"?k.css({visibility:"visible"}):k.css({visibility:"visible"}).hide();if(c.callback){c.callback.apply(k[0])}k.dequeue();a("div.ui-effects-explode").remove()},c.duration||500)})}})(jQuery);(function(a,b){a.effects.fade=function(c){return this.queue(function(){var d=a(this),e=a.effects.setMode(d,c.options.mode||"hide");d.animate({opacity:e},{queue:false,duration:c.duration,easing:c.options.easing,complete:function(){(c.callback&&c.callback.apply(this,arguments));d.dequeue()}})})}})(jQuery);(function(a,b){a.effects.fold=function(c){return this.queue(function(){var f=a(this),l=["position","top","left"];var i=a.effects.setMode(f,c.options.mode||"hide");var p=c.options.size||15;var o=!(!c.options.horizFirst);var h=c.duration?c.duration/2:a.fx.speeds._default/2;a.effects.save(f,l);f.show();var e=a.effects.createWrapper(f).css({overflow:"hidden"});var j=((i=="show")!=o);var g=j?["width","height"]:["height","width"];var d=j?[e.width(),e.height()]:[e.height(),e.width()];var k=/([0-9]+)%/.exec(p);if(k){p=parseInt(k[1],10)/100*d[i=="hide"?0:1]}if(i=="show"){e.css(o?{height:0,width:p}:{height:p,width:0})}var n={},m={};n[g[0]]=i=="show"?d[0]:p;m[g[1]]=i=="show"?d[1]:0;e.animate(n,h,c.options.easing).animate(m,h,c.options.easing,function(){if(i=="hide"){f.hide()}a.effects.restore(f,l);a.effects.removeWrapper(f);if(c.callback){c.callback.apply(f[0],arguments)}f.dequeue()})})}})(jQuery);(function(a,b){a.effects.highlight=function(c){return this.queue(function(){var e=a(this),d=["backgroundImage","backgroundColor","opacity"],g=a.effects.setMode(e,c.options.mode||"show"),f={backgroundColor:e.css("backgroundColor")};if(g=="hide"){f.opacity=0}a.effects.save(e,d);e.show().css({backgroundImage:"none",backgroundColor:c.options.color||"#ffff99"}).animate(f,{queue:false,duration:c.duration,easing:c.options.easing,complete:function(){(g=="hide"&&e.hide());a.effects.restore(e,d);(g=="show"&&!a.support.opacity&&this.style.removeAttribute("filter"));(c.callback&&c.callback.apply(this,arguments));e.dequeue()}})})}})(jQuery);(function(a,b){a.effects.pulsate=function(c){return this.queue(function(){var e=a(this),f=a.effects.setMode(e,c.options.mode||"show");times=((c.options.times||5)*2)-1;duration=c.duration?c.duration/2:a.fx.speeds._default/2,isVisible=e.is(":visible"),animateTo=0;if(!isVisible){e.css("opacity",0).show();animateTo=1}if((f=="hide"&&isVisible)||(f=="show"&&!isVisible)){times--}for(var d=0;d<times;d++){e.animate({opacity:animateTo},duration,c.options.easing);animateTo=(animateTo+1)%2}e.animate({opacity:animateTo},duration,c.options.easing,function(){if(animateTo==0){e.hide()}(c.callback&&c.callback.apply(this,arguments))});e.queue("fx",function(){e.dequeue()}).dequeue()})}})(jQuery);(function(a,b){a.effects.puff=function(c){return this.queue(function(){var g=a(this),h=a.effects.setMode(g,c.options.mode||"hide"),f=parseInt(c.options.percent,10)||150,e=f/100,d={height:g.height(),width:g.width()};a.extend(c.options,{fade:true,mode:h,percent:h=="hide"?f:100,from:h=="hide"?d:{height:d.height*e,width:d.width*e}});g.effect("scale",c.options,c.duration,c.callback);g.dequeue()})};a.effects.scale=function(c){return this.queue(function(){var h=a(this);var e=a.extend(true,{},c.options);var k=a.effects.setMode(h,c.options.mode||"effect");var i=parseInt(c.options.percent,10)||(parseInt(c.options.percent,10)==0?0:(k=="hide"?0:100));var j=c.options.direction||"both";var d=c.options.origin;if(k!="effect"){e.origin=d||["middle","center"];e.restore=true}var g={height:h.height(),width:h.width()};h.from=c.options.from||(k=="show"?{height:0,width:0}:g);var f={y:j!="horizontal"?(i/100):1,x:j!="vertical"?(i/100):1};h.to={height:g.height*f.y,width:g.width*f.x};if(c.options.fade){if(k=="show"){h.from.opacity=0;h.to.opacity=1}if(k=="hide"){h.from.opacity=1;h.to.opacity=0}}e.from=h.from;e.to=h.to;e.mode=k;h.effect("size",e,c.duration,c.callback);h.dequeue()})};a.effects.size=function(c){return this.queue(function(){var d=a(this),o=["position","top","left","width","height","overflow","opacity"];var n=["position","top","left","overflow","opacity"];var k=["width","height","overflow"];var q=["fontSize"];var l=["borderTopWidth","borderBottomWidth","paddingTop","paddingBottom"];var g=["borderLeftWidth","borderRightWidth","paddingLeft","paddingRight"];var h=a.effects.setMode(d,c.options.mode||"effect");var j=c.options.restore||false;var f=c.options.scale||"both";var p=c.options.origin;var e={height:d.height(),width:d.width()};d.from=c.options.from||e;d.to=c.options.to||e;if(p){var i=a.effects.getBaseline(p,e);d.from.top=(e.height-d.from.height)*i.y;d.from.left=(e.width-d.from.width)*i.x;d.to.top=(e.height-d.to.height)*i.y;d.to.left=(e.width-d.to.width)*i.x}var m={from:{y:d.from.height/e.height,x:d.from.width/e.width},to:{y:d.to.height/e.height,x:d.to.width/e.width}};if(f=="box"||f=="both"){if(m.from.y!=m.to.y){o=o.concat(l);d.from=a.effects.setTransition(d,l,m.from.y,d.from);d.to=a.effects.setTransition(d,l,m.to.y,d.to)}if(m.from.x!=m.to.x){o=o.concat(g);d.from=a.effects.setTransition(d,g,m.from.x,d.from);d.to=a.effects.setTransition(d,g,m.to.x,d.to)}}if(f=="content"||f=="both"){if(m.from.y!=m.to.y){o=o.concat(q);d.from=a.effects.setTransition(d,q,m.from.y,d.from);d.to=a.effects.setTransition(d,q,m.to.y,d.to)}}a.effects.save(d,j?o:n);d.show();a.effects.createWrapper(d);d.css("overflow","hidden").css(d.from);if(f=="content"||f=="both"){l=l.concat(["marginTop","marginBottom"]).concat(q);g=g.concat(["marginLeft","marginRight"]);k=o.concat(l).concat(g);d.find("*[width]").each(function(){child=a(this);if(j){a.effects.save(child,k)}var r={height:child.height(),width:child.width()};child.from={height:r.height*m.from.y,width:r.width*m.from.x};child.to={height:r.height*m.to.y,width:r.width*m.to.x};if(m.from.y!=m.to.y){child.from=a.effects.setTransition(child,l,m.from.y,child.from);child.to=a.effects.setTransition(child,l,m.to.y,child.to)}if(m.from.x!=m.to.x){child.from=a.effects.setTransition(child,g,m.from.x,child.from);child.to=a.effects.setTransition(child,g,m.to.x,child.to)}child.css(child.from);child.animate(child.to,c.duration,c.options.easing,function(){if(j){a.effects.restore(child,k)}})})}d.animate(d.to,{queue:false,duration:c.duration,easing:c.options.easing,complete:function(){if(d.to.opacity===0){d.css("opacity",d.from.opacity)}if(h=="hide"){d.hide()}a.effects.restore(d,j?o:n);a.effects.removeWrapper(d);if(c.callback){c.callback.apply(this,arguments)}d.dequeue()}})})}})(jQuery);(function(a,b){a.effects.shake=function(c){return this.queue(function(){var f=a(this),m=["position","top","left"];var l=a.effects.setMode(f,c.options.mode||"effect");var o=c.options.direction||"left";var d=c.options.distance||20;var e=c.options.times||3;var h=c.duration||c.options.duration||140;a.effects.save(f,m);f.show();a.effects.createWrapper(f);var g=(o=="up"||o=="down")?"top":"left";var q=(o=="up"||o=="left")?"pos":"neg";var j={},p={},n={};j[g]=(q=="pos"?"-=":"+=")+d;p[g]=(q=="pos"?"+=":"-=")+d*2;n[g]=(q=="pos"?"-=":"+=")+d*2;f.animate(j,h,c.options.easing);for(var k=1;k<e;k++){f.animate(p,h,c.options.easing).animate(n,h,c.options.easing)}f.animate(p,h,c.options.easing).animate(j,h/2,c.options.easing,function(){a.effects.restore(f,m);a.effects.removeWrapper(f);if(c.callback){c.callback.apply(this,arguments)}});f.queue("fx",function(){f.dequeue()});f.dequeue()})}})(jQuery);(function(a,b){a.effects.slide=function(c){return this.queue(function(){var f=a(this),e=["position","top","left"];var j=a.effects.setMode(f,c.options.mode||"show");var i=c.options.direction||"left";a.effects.save(f,e);f.show();a.effects.createWrapper(f).css({overflow:"hidden"});var g=(i=="up"||i=="down")?"top":"left";var d=(i=="up"||i=="left")?"pos":"neg";var k=c.options.distance||(g=="top"?f.outerHeight({margin:true}):f.outerWidth({margin:true}));if(j=="show"){f.css(g,d=="pos"?-k:k)}var h={};h[g]=(j=="show"?(d=="pos"?"+=":"-="):(d=="pos"?"-=":"+="))+k;f.animate(h,{queue:false,duration:c.duration,easing:c.options.easing,complete:function(){if(j=="hide"){f.hide()}a.effects.restore(f,e);a.effects.removeWrapper(f);if(c.callback){c.callback.apply(this,arguments)}f.dequeue()}})})}})(jQuery);(function(a,b){a.effects.transfer=function(c){return this.queue(function(){var g=a(this),i=a(c.options.to),f=i.offset(),h={top:f.top,left:f.left,height:i.innerHeight(),width:i.innerWidth()},e=g.offset(),d=a('<div class="ui-effects-transfer"></div>').appendTo(document.body).addClass(c.options.className).css({top:e.top,left:e.left,height:g.innerHeight(),width:g.innerWidth(),position:"absolute"}).animate(h,c.duration,c.options.easing,function(){d.remove();(c.callback&&c.callback.apply(g[0],arguments));g.dequeue()})})}})(jQuery);(function($){

$.widget('ui.grid', {

	options: {
		width: 500,
		height: 300,

		limit: false,
		pagination: true,
		allocateRows: true, //Only used for infinite scrolling
		chunk: 20, //Only used for infinite scrolling

		footer: true,
		toolbar: false,

		multipleSelection: true
	},

	_generateToolbar: function() {
		this.toolbar = $('<tr class="ui-grid-toolbar"><td>Toolbar</td></tr>').appendTo(this.grid);
		this.toolbar = $('td', this.toolbar);
	},

	_generateColumns: function() {

		this.columnsContainer = $('<tr class="ui-grid-columns"><td><div class="ui-grid-columns-constrainer"><table cellpadding="0" cellspacing="0"><tbody><tr class="ui-grid-header ui-grid-inner"></tr></tbody></table></div></td></tr>')
			.appendTo(this.grid).find('table tbody tr');

		$('.ui-grid-columns-constrainer', this.grid).css({
			width: this.options.width,
			overflow: 'hidden'
		});

		this.columnsContainer.gridSortable({ instance: this });

	},

	_generateFooter: function() {
		this.footer = $('<tr class="ui-grid-footer"><td>'+
		'<div class="ui-grid-footer-text ui-grid-limits"></div>'+
		'</td></tr>').appendTo(this.grid).find('td');
	},

	_generatePagination: function(response) {
		this.pagination = $('<div class="ui-grid-footer-text" style="float: right;"></div>').appendTo(this.footer);
		var pages = Math.round(response.totalRecords/this.options.limit);
		this._updatePagination(response);
	},

	_updatePagination: function(response) {

		var pages = Math.round(response.totalRecords/this.options.limit),
			current = Math.round(this.offset / this.options.limit) + 1,
			displayed = [];

		this.pagination.empty();

		for (var i=current-1; i > 0 && i > current-3; i--) {
			this.pagination.prepend('<a href="#" class="ui-grid-pagination">'+i+'</a>');
			displayed.push(i);
		};

		for (var i=current; i < pages+1 && i < current+3; i++) {
			this.pagination.append(i==current? '<span class="ui-grid-pagination-current">'+i+'</span>' : '<a href="#" class="ui-grid-pagination">'+i+'</a>' );
			displayed.push(i);
		};


		if(pages > 1 && $.inArray(2, displayed) == -1) //Show front dots if the '2' is not already displayed and there are more pages than 1
			this.pagination.prepend('<span class="ui-grid-pagination-dots">...</span>');

		if($.inArray(1, displayed) == -1) //Show the '1' if it's not already shown
			this.pagination.prepend('<a href="#" class="ui-grid-pagination">1</a>');

		if($.inArray(pages-1, displayed) == -1) //Show the dots between the current elipse and the last if the one before last is not shown
			this.pagination.append('<span class="ui-grid-pagination-dots">...</span>');

		if($.inArray(pages, displayed) == -1) //Show the last if it's not already shown
			this.pagination.append('<a href="#" class="ui-grid-pagination">'+pages+'</a>');

		this.pagination.prepend(current-1 > 0 ? '<a href="#" class="ui-grid-pagination">&lt;&lt;</a>' : '<span class="ui-grid-pagination">&lt;&lt;</span>');
		this.pagination.append(current+1 > pages ? '<span class="ui-grid-pagination">&gt;&gt;</span>' : '<a href="#" class="ui-grid-pagination">&gt;&gt;</a>');

	},

	_create: function() {

		var self = this;
		this.offset = 0;

                // Set initial sort direction (if specified)
                this.sortColumn = this.options.sortColumn;
                this.sortDirection = this.options.sortDirection;

		//Generate the grid element
		this.grid = $('<table class="ui-grid ui-component ui-component-content" cellpadding="0" cellspacing="0" width="100%" height="100%"></table>')
						.css({ width: this.options.width })
						.appendTo(this.element);

		//Generate toolbar
		if(this.options.toolbar)
			this._generateToolbar();

		//Generate columns
		this._generateColumns();

		//Generate content element and table
		this.content = $('<tr><td><div class="ui-grid-content"><table cellpadding="0" cellspacing="0"><tbody></tbody></table></div></td></tr>')
			.appendTo(this.grid).find('tbody');

		this.contentDiv = $('.ui-grid-content', this.grid);

                // Set height of the height of the content div
                this.contentDiv.height(this.options.height);

		//Generate footer
		if(this.options.footer)
			this._generateFooter();

		//Prepare data
		this.gridmodel = $.ui.grid.model({
			url: this.options.url
		});

		//Call update for the first time
                this._initialUpdate();

		//Event bindings
		this.grid
			.bind('click.grid', function(event) {
				return self._handleClick(event);
			})
			.bind('mousemove.grid', function(event) {
				return self._handleMove(event);
			})
			.bind('mouseleave.grid', function(event) {
				$(self.tableRowHovered).removeClass('ui-grid-row-hover');
			});

		this.contentDiv
			.bind('scroll.grid', function(event) {
				$('div.ui-grid-columns-constrainer', self.grid)[0].scrollLeft = this.scrollLeft;
			});

		//Selection of rows
		this._makeRowsSelectable();

	},

	_initialUpdate: function() {
		this._update({ columns: true });
        },

	_handleMove: function(event) {

		// If we're over a columns header
		if(this.columnHandleHovered) {
			$('td.ui-grid-column-header *', this.grid).css('cursor', '');
			this.columnHandleHovered = false;
		}

		if($(event.target).is('.ui-grid-column-header') || $(event.target).parent().is('.ui-grid-column-header')) {

			var target = $(event.target).is('.ui-grid-column-header') ? $(event.target) : $(event.target).parent();
                        var widget = $(target).data('gridResizable');
			if (! (widget && widget._mouseCapture(event))) return;

			$('td.ui-grid-column-header *', this.grid).css('cursor', 'e-resize');
			this.columnHandleHovered = true;
			return; //Stop here to save performance

		}


		//If we're over a table row
		if($(event.target).parents('.ui-grid-row').length) {

			var target = $(event.target).parents('.ui-grid-row');

			if(this.tableRowHovered && this.tableRowHovered != target[0])
				$(this.tableRowHovered).removeClass('ui-grid-row-hover');

			target.addClass('ui-grid-row-hover');
			this.tableRowHovered = target[0];
			return; //Stop here to save performance

		} else {
			if(this.tableRowHovered)
				$(this.tableRowHovered).removeClass('ui-grid-row-hover');
		}

	},

	_handleClick: function(event) {

		//Click on column header toggles sorting
		if($(event.target.parentNode).is('.ui-grid-column-header')) {
			var data = $.data(event.target.parentNode, 'grid-column-header');
			this.sortDirection = this.sortDirection == 'desc' ? 'asc' : 'desc';
			this.sortColumn = data.id;
			this._update({ columns: false, refresh: true });
		}

		if($(event.target).is('a.ui-grid-pagination')) {
			var html = event.target.innerHTML, current = Math.round(this.offset / this.options.limit) + 1;
			if(html == '&gt;&gt;') current = current+1;
			if(html == '&lt;&lt;') current = current-1;
			if(!isNaN(parseInt(event.target.innerHTML,10))) current = parseInt(event.target.innerHTML,10);

			this.offset = (current-1) * this.options.limit;
			this._update();
		}

		return false;

	},

	_makeRowsSelectable: function() {

		this.content.parent().parent().selectable({
			filter: 'tr',
			multiple: this.options.multipleSelection,
			selectClass: 'ui-grid-row-selected',
			focusClass: 'ui-grid-row-focussed',
			select: function(e, ui) {

				var itemOffset = ui.currentFocus.offset();
				var itemHeight = ui.currentFocus.height();
				var listOffset = $(this).offset();
				var listHeight = $(this).height();

				if(itemOffset.top - listOffset.top + itemHeight > listHeight) {
					this.scrollTop = ((itemOffset.top + this.scrollTop - listOffset.top + itemHeight) - listHeight);
				} else if(itemOffset.top < listOffset.top) {
					this.scrollTop = itemOffset.top + this.scrollTop - listOffset.top;
				};

			}
		});

	},

	_update: function(o) {

		var self = this,
			options = $.extend({}, o, {
				limit: this.options.limit,
				start: (!(o && o.refresh) && this.offset) || 0,
				refresh: (o && o.refresh) || (o && o.columns)
			}),
			fetchOptions = $.extend({}, options, { fill: null });

			if(options.refresh) {
				fetchOptions.start = self.infiniteScrolling ? 0 : (this.offset || 0);
			}

		//Somehow the keys for these must stay undefined no matter what
		if(this.sortColumn) fetchOptions.sortColumn = this.sortColumn;
		if(this.sortDirection) fetchOptions.sortDirection = this.sortDirection;

		//Do the ajax call
		this.gridmodel.fetch(fetchOptions, function(response) {

			//Generate or update pagination
			if(self.options.pagination && !self.pagination) {
				self._generatePagination(response);
			} else if(self.options.pagination && self.pagination) {
				self._updatePagination(response);
			}

			//Empty the content if we either use pagination or we have to restart infinite scrolling
			if(!self.infiniteScrolling || options.refresh)
				self.content.empty();

			//Empty the columns
			if(options.refresh) {
				self.columnsContainer.empty();
				self._addColumns(response.columns);
			}


			//If infiniteScrolling is used and there's no full refresh, fill rows
			if(self.infiniteScrolling && !options.refresh) {

				var data = [];
				for (var i=0; i < response.records.length; i++) {
					data.push(self._addRow(response.records[i]));
				};

				options.fill({
					chunk: options.chunk,
					data: data
				});

			} else { //otherwise, simply append the rows to the now emptied list

				for (var i=0; i < response.records.length; i++) {
					self._addRow(response.records[i]);
				};

				self._syncColumnWidth();

				//If we're using infinite scrolling, we have to restart it
				if(self.infiniteScrolling) {
					self.contentDiv.infiniteScrolling('restart');
				}

			}

			//Initiate infinite scrolling if we don't use pagination and total records exceed the displayed records
			if(!self.infiniteScrolling && !self.options.pagination && self.options.limit < response.totalRecords) {

				self.infiniteScrolling = true;
				self.contentDiv.infiniteScrolling({
					total: self.options.allocateRows ? response.totalRecords : false,
					chunk: self.options.chunk,
					scroll: function(e, ui) {
						self.offset = ui.start;
						self._update({ fill: ui.fill, chunk: ui.chunk });
					},
					update: function(e, ui) {
						$('div.ui-grid-limits', self.footer).html('Result ' + ui.firstItem + '-' + ui.lastItem + (ui.total ? ' of '+ui.total : ''));
					}
				});

			}

			if(!self.infiniteScrolling)
				$('div.ui-grid-limits', self.footer).html('Result ' + options.start + '-' + (options.start + options.limit) + ' of ' + response.totalRecords);

		});

	},

	_syncColumnWidth: function() {

		var testTR = $('tr:first td', this.content);
		var totalWidth = 0;

		for (var i=0; i < this.columns.length; i++) {
			$(testTR[i]).width($('td:eq('+i+')', this.columnsContainer)[0].style.width);
			totalWidth += parseInt($('td:eq('+i+')', this.columnsContainer)[0].style.width, 10);
			//$('td:eq('+i+') div', this.columnsContainer).width(testTR[i].offsetWidth - 10); //TODO: Subtract real paddings of inner divs
		};

		this.content.parent().width(totalWidth);

	},

	_addColumns: function(item) {

		this.columns = item;
		var totalWidth = 25;

		for (var i=0; i < item.length; i++) {
			var column = $('<td class="ui-grid-column-header ui-state-default"><div>'+item[i].label+'</div></td>')
				.width(item[i].width)
				.data('grid-column-header', item[i])
				.appendTo(this.columnsContainer)
				.gridResizable();
			totalWidth += item[i].width;
		};

		//This column is the last and only used to serve as placeholder for a non-existant scrollbar
		$('<td class="ui-grid-column-header ui-state-default"><div></div></td>').width(25).appendTo(this.columnsContainer);

		//Update the total width of the wrapper of the column headers
		this.columnsContainer.parent().parent().width(totalWidth);

	},

	_addRow: function(item, dontAdd) {

		var row = $('<tr class="ui-grid-row"></tr>');
		if(!dontAdd) row.appendTo(this.content);

		for (var i=0; i < this.columns.length; i++) {
			$('<td class="ui-grid-column ui-state-active"><div>'+item[this.columns[i].id]+'</div></td>')
				.appendTo(row);
		};

		return row;

	}

});


$.widget('ui.gridResizable', $.extend({}, $.ui.mouse, {

	options: {
		handle: false,
		cancel: ":input",
		delay: 0,
		distance: 1
	},

	_create: function() {
		this.table = this.element.parent().parent().parent();
		this.gridTable = this.element.parents('.ui-grid').find('div.ui-grid-content > table');
		this._mouseInit();
	},

	_mouseCapture: function(event) {

		this.offset = this.element.offset();
		if((this.offset.left + this.element.width()) - event.pageX < 5) {
			return true;
		};

		return false;

	},

	_mouseStart: function(event) {

		$.extend(this, {
			startPosition: event.pageX,
			startWidth: this.element.width(),
			tableStartWidth: this.table.width(),
			gridTableStartWidth: this.gridTable.width(),
			index: this.element.parent().find('td').index(this.element[0])
		});

	},

	_mouseDrag: function(event) {

		this.element.css('width', this.startWidth + (event.pageX - this.startPosition));
		this.table.css('width', this.tableStartWidth + (event.pageX - this.startPosition));

		$('tr:eq(0) td:eq('+this.index+')', this.gridTable).css('width', this.startWidth + (event.pageX - this.startPosition));
		this.gridTable.css('width', this.gridTableStartWidth + (event.pageX - this.startPosition));

	},

	_mouseStop: function(event) {
		//TODO: Send column width update to the backend, and/or fire callback
	}

}));


$.widget('ui.gridSortable', $.extend({}, $.ui.mouse, {

	options: {
		handle: false,
		cancel: ":input",
		delay: 0,
		distance: 1
	},

	_create: function() {
		this._mouseInit();
	},

	_mouseCapture: function(event) {

                var el = $(event.target);
                this.item = el.hasClass('ui-grid-column-header') ? el : el.parents('.ui-grid-column-header');
		this.offset = this.item.offset();

		return true;

	},

	_mouseStart: function(event) {

		var self = this;

		this.offsets = [];
		this.items = this.element.find('td').each(function(i) {
			if(self.item[0] != this) self.offsets.push([this, $(this).offset().left]);
		});

		$.extend(this, {
			startPosition: event.pageX,
			index: this.items.index(this.item[0])
		});

	},

	_mouseDrag: function(event) {

		var self = this;
			//this.element.css('width', this.startWidth + (event.pageX - this.startPosition));
		$(self.offsets).each(function(i) {

			if(
				$.ui.isOverAxis(event.pageX, this[1], this[0].offsetWidth)
			) {
				var dir = $.ui.isOverAxis(event.pageX, this[1], this[0].offsetWidth/2) ? 'left' : 'right';
				if(!self.lastHovered || self.lastHovered[0] != this[0] || self.lastHovered[1] != dir) {

					if(self.lastHovered) $(self.lastHovered[0]).removeClass('ui-grid-column-sort-right ui-grid-column-sort-left');

					self.lastHovered = [this[0], dir];
					$(self.lastHovered[0]).addClass('ui-grid-column-sort-'+dir);
				}
			}

		});

	},

	_mouseStop: function(event) {

		var self = this;
		if(this.lastHovered) {
			$(this.lastHovered[0]).removeClass('ui-grid-column-sort-right ui-grid-column-sort-left');
			$(this.lastHovered[0])[this.lastHovered[1] == 'right' ? 'after' : 'before'](this.item);

			//TODO: Reorder actual data columns
			$('tr', this.options.instance.contentDiv).each(function(i) {
				$('> td:eq('+self.items.index(self.lastHovered[0])+')', this)[self.lastHovered[1] == 'right' ? 'after' : 'before']($('> td:eq('+self.index+')', this));
			});

		}
	}

}));

})(jQuery);
(function($) {

	$.extend($.ui.grid, {
		model: function(options) {
			options = $.extend({}, $.ui.grid.model.defaults, options);
			return {
				fetch: function(request, callback) {
					$.ajax($.extend(true, {
						url: options.url,
						data: request,
						success: function(response) {
							callback(options.parse(response));
						}
					}, options.ajax));
				}
			}
		}
	});

	$.ui.grid.model.defaults = {
		ajax: {
			dataType: "json",
			cache: false
		},
		parse: function(response) {
			var records = [];
			$.each(response.records, function() {
				var record = this;
				var result = {};
				$.each(response.columns, function(index) {
					result[this.id] = record[index];
				})
				records.push(result);
			});
			return {
				totalRecords: response.totalRecords,
				columns: response.columns,
				records: records
			};
		}
	}

})(jQuery);
/**
 * Copyright Yehuda Katz
 * with assistance by Jay Freeman
 * 
 * You may distribute this code under the same license as jQuery (BSD or GPL
 **/

/*

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8">
    <title>Templating</title>
    <script src="../../jquery/dist/jquery.min.js"></script>
    <script src="jquery.templating.js"></script>
    <script>
      jQuery(function ($) {
          $("a.updateTemplate").click(function() {
            $(this.rel).loadTemplate(this.href);
            return false;
          });
          $("._template").templatize();
      });
    </script>
  </head>
  <body>
    <div class="_template" id="myTemplate">
      <![CDATA[
        <{{tag}} href={{href}}>{{first}} {{last}}</{{tag}}>
        <p>Bar</p>
        <div>First Name: {{first}}</div>
        <div>Last Name: {{last}}</div>
      ]]>
    </div>
    <a href="foo" rel="#myTemplate" class="updateTemplate">Click</a>
  </body>
</html>
  
*/

(function ($) {
  $.makeTemplate = function (template, begin, end) {
    var rebegin = begin.replace(/([\]{}[\\])/g, '\\$1');
    var reend = end.replace(/([\]{}[\\])/g, '\\$1');

    var code = "try { with (_context) {" +
      "var _result = '';" +
        template
          .replace(/[\t\r\n]/g, ' ')
          .replace(/^(.*)$/, end + '$1' + begin)
          .replace(new RegExp(reend + "(.*?)" + rebegin, "g"), function (text) {
            return text
              .replace(new RegExp("^" + reend + "(.*)" + rebegin + "$"), "$1")
              .replace(/\\/g, "\\\\")
              .replace(/'/g, "\\'")
              .replace(/^(.*)$/, end + "_result += '$1';" + begin);
          })
          .replace(new RegExp(rebegin + "=(.*?)" + reend, "g"), "_result += ($1);")
          .replace(new RegExp(rebegin + "(.*?)" + reend, "g"), ' $1 ')
          .replace(new RegExp("^" + reend + "(.*)" + rebegin + "$"), '$1') +
      "return _result;" +
    "} } catch(e) { return '' } ";

    return new Function("_context", code);
  };
})(jQuery);/*
 * jQuery UI Autocomplete
 * version: 1.0 (1/2/2008)
 * @requires: jQuery v1.2 or later, dimensions plugin
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Copyright 2007 Yehuda Katz, Rein Henrichs
 */

(function($) {
  $.ui = $.ui || {};
  $.ui.autobox = $.ui.autobox || {};
  $.ui.autobox.ext = $.ui.autobox.ext || {};

  // create request manager
  var log;
  if (window.console) {
      log = console.log;
  } else {
      log = function() {};
  }
  var MiniRM = function(opt) {
    this.chainedGetJSON = opt.jsonhandler || $.getJSON;
    this.maxActive = opt.maxActive || 1;
    this.maxQueue = opt.maxQueue || 1;
    this.active = 0;
    this.queue = [];
  };
  $.extend(MiniRM.prototype, {
      getJSON: function(url, query, handler) {
        var self = this;
        var wrappedHandler = function(json) {
            self.active -= 1;
            self.log ('MiniRM IN', url, query);
            handler(json);
            var nextJob = self.queue.shift();
            if (nextJob !== undefined) {
                self.active += 1;
                self.log ('MiniRM POP/OUT', nextJob[0], nextJob[1]);
                self.chainedGetJSON.apply(null, nextJob);
            }
        };
        if (this.active < this.maxActive) {
            this.active += 1;
            this.log ('MiniRM OUT', url, query);
            this.chainedGetJSON(url, query, wrappedHandler);
        } else {
            if (this.queue.length == this.maxQueue) {
                var discardJob = this.queue.shift();
                this.log('MiniRM POP/DISCARD', discardJob[0], discardJob[1]);
            }
            this.queue.push([url, query, wrappedHandler]);
            this.log ('MiniRM PUSH', url, query);
        }
      },
      log: function(msg, url, query) {
        //log (msg, 'ACT=' + this.active, 'QUE=' + this.queue.length, url + "?" + query);
      }
  });
  var miniRM = new MiniRM({});

  $.ui.autobox.ext.ajax = function(opt) {
    var ajax = opt.ajax;
    return { getList: function(input, hash) {
      var val = input.val();
      var minQueryLength = this.options.minQueryLength;
      var minQueryNotice = this.options.minQueryNotice; 

      function tooShort(word, minQueryLength) {
        return minQueryLength && (! word || word.length < minQueryLength);
      }

      // filter words by short/long
      var words = val.replace(/\s+/, " ").split(" "), short = [], long = [];
      for (i = 0, j = words.length; i < j; i++) {
        var word = words[i];
        if (word == "") continue;
        tooShort(word, minQueryLength) ? short.push(word) : long.push(word);        
      }
      val = long.join(" ");

      // only send request if we have a long word
      if (long.length > 0) {
        miniRM.getJSON(ajax, "val=" + val, function(json) {
          if (hash) { 
            if (short.length > 0 && minQueryNotice) { 
              json.unshift(minQueryNotice); 
            }
            json = $(json).filter(function(){ return !hash[this.text]; });
            input.trigger("updateList", [json]);
          }
        });
        
      // only short words - show notice
      } else if (short.length > 0 && minQueryNotice) {
        input.trigger("updateList", [[minQueryNotice]]);
      }

    }};
  };

  $.ui.autobox.ext.templateText = function(opt) {
    var template = $.makeTemplate(opt.templateText, "<%", "%>");
    return { template: function(obj) { return template(obj); } };
  };

})(jQuery);
/**
 * jQuery Autobox Plugin
 * Copyright (c) 2008 Big Red Switch
 *
 * http://www.bigredswitch.com/blog/2008/12/autobox2/
 *
 * Dual licensed under the BSD and GPL licenses:
 *  http://en.wikipedia.org/wiki/Bsd_license
 *  http://en.wikipedia.org/wiki/GNU_General_Public_License
 *
 * 0.7.1 : Add prepop to options to pre-populate autobox
 *         Add addBox function to populate autobox via JS
 *         (css) Add margin-bottom to .bit-box
 * 0.7.0 : Initial version
 *         Rolled up autocomplete and autotext plugins
 *
 * ****************************************************************************
 *
 * jQuery Autocomplete
 * Written by Yehuda Katz (wycats@gmail.com) and Rein Henrichs (reinh@reinh.com)
 * Copyright 2007 Yehuda Katz, Rein Henrichs
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Facebook style text list from Guillermo Rauch's mootools script:
 *  http://devthought.com/textboxlist-fancy-facebook-like-dynamic-inputs/
 *
 * Caret position method: Diego Perini: http://javascript.nwbox.com/cursor_position/cursor.js
 *
 * 2009 Changes by Balazs Ree <ree@greenfinity.hu>
 * - change the code to be more OO and offer a reusable widget
 *
 */
(function($){

  function LOG(obj){
    if(console && console.log){
      console.log(obj);
    }
    else{
      var cons=$('#log');
      if(!cons){cons=$('<div id="log"></div>');}
      if(cons){cons.append(obj).append('<br/>\n');}
    }
  }

  $.fn.resizableTextbox=function(el, options) {
    var opts=$.extend({ min: 5, max: 500, step: 7 }, options);
    var width=el.attr('offsetWidth');
    el.bind('keydown', function(e) {
        $(this).data('rt-value', this.value.length);
    })
    .bind('keyup', function(e) {
        var self=$(this);
        var newsize=opts.step * self.val().length;
        if (newsize <= opts.min) {
          newsize=width;
        }
        if (!(self.val().length == self.data('rt-value') ||
              newsize <= opts.min || newsize >= opts.max)) {
          self.width(newsize);
        }
     });
  };

  $.ui=$.ui || {}; $.ui.autobox=$.ui.autobox || {}; var count=0;

  var KEY={
    ESC: 27,
    RETURN: 13,
    TAB: 9,
    BS: 8,
    DEL: 46,
    LEFT: 37,
    RIGHT: 39,
    UP: 38,
    DOWN: 40
  };

  // Only used if directly $.fn.autobox is used
  function addBox(input, text, name){
    throw 'Wrong addBox!';
  }

$.widget('ui.autobox3', {

    options: {
        timeout: 500,
        template: function(str) {
            return "<li>" + this.options.insertText(str) + "</li>";
        },
        insertText: function(str) {
            return str;
        },
        match: function(typed) {
            return this.match(new RegExp(typed));
        },
        wrapper: '<ul class="autobox-list"></ul>',
        resizable: {},
        selectHoverable: '> li',
        // if specified, a query starts at minimum this many characters
        minQueryLength: 0,
        minQueryNotice: null,
        // maximum width of the search container
        maxSearchContainerWidth: 400
    },

    _create: function() {

        var t = this;
        var opt = this.options;

        if($.ui.autobox.ext){
          for(var ext in $.ui.autobox.ext){
            if(opt[ext]){
              this.options = opt = $.extend(opt, $.ui.autobox.ext[ext](opt));
              delete opt[ext];
            }
        } }

        // setup the widget
        t._setupWidget();

        // populate methods from options
        if (opt.getList) this._getList = opt.getList;
        if (opt.getBoxFromSelection) this._getBoxFromSelection = opt.getBoxFromSelection;
        if (opt.getBoxOnEnter) this._getBoxOnEnter = opt.getBoxOnEnter;

        this.active = null;
        this.hovered = null;
        this.off();
    },

    _bindInput: function(input) {
        var opt = this.options;
        var t = this;
        var self = this;

        // Some closed functions
        function preventTabInAutocompleteMode(e){
          var k=e.which || e.keyCode;
          if(self.activelist.is_active && k == KEY.TAB){
            e.preventDefault();
          }
        }
        function startTypingTimeout(e, input, timeout){
          $.data(input, "typingTimeout", window.setTimeout(function(){
            $(e.target || e.srcElement).trigger("autobox");
          }, timeout));
        }
        function clearTypingTimeout(input){
            var typingTimeout=$.data(input, "typingTimeout");
            if(typingTimeout) window.clearInterval(typingTimeout);
        }
        // set up the input using the above closed functions
        input
            .keydown(function(e){
              preventTabInAutocompleteMode(e);
            })
            .keyup(function(e){
              var k=e.which || e.keyCode;
              if(! self.activelist.is_active &&
                  (k == KEY.UP || k == KEY.DOWN)){
                clearTypingTimeout(this);
                startTypingTimeout(e, this, 0);
              }
              else{
                preventTabInAutocompleteMode(e);
              }
            })
            .keypress(function(e){
              var k=e.keyCode || e.which; // keyCode == 0 in Gecko/FF on keypress
              clearTypingTimeout(this);
              if($.data(document.body, "suppressKey")){
                $.data(document.body, "suppressKey", false);
                //note that IE does not generate keypress for arrow/tab keys
                if(k == KEY.TAB || k == KEY.UP || k == KEY.DOWN) return false;
              }
              if(self.activelist.is_active && k < 32 && k != KEY.BS && k != KEY.DEL) return false;
              else if(k == KEY.RETURN){
                var record = t._getBoxOnEnter();
                if (record) { t._addBox(record); }
                e.preventDefault();
              }
              else if(k == KEY.BS || k == KEY.DEL || k > 32){ // more than ESC and RETURN and the like
                startTypingTimeout(e, this, opt.timeout);
              }
            })
            .bind("paste", function(e) {
              startTypingTimeout(e, this, 0);
            })
            .bind("autobox", function(){
              var self=$(this);
              self.one("updateList", function(e, list){//clear/update/redraw list
                t._updateList(list);
              });
              t._getList(self, t._getCurrentValsHash(self));
            })

            // Bind key event in active mode to input
            .bind("keydown.autobox", function(e){
                // Prevent if the list is not active
                if (! self.activelist.is_active) { return true; }
                var k = e.which || e.keyCode;
                if (k == KEY.ESC) {
                    self.cancel();
                } else if (k == KEY.RETURN) { 
                    // pressing return in the input will do the activation,
                    // which in turn triggers the adding of the current value.
                    self.activate();
                    e.preventDefault();
                    }
                else if(k == KEY.UP || k == KEY.TAB || k == KEY.DOWN){
                    var keystep = (k == KEY.UP) ? -1 : 1;
                    var index = -1;
                    var hlength = self.activelist.hoverable.length;
                    if (self.hovered) {
                        index = self.activelist.hoverable.index(self.hovered);
                    }
                    index += keystep;
                    if (index >= hlength) {
                        index = 0;
                    } else if (index < 0) {
                        index = hlength - 1;
                    }
                    self._setActive(self.activelist.hoverable.eq(index));
                } else { return true; }
                $.data(document.body, "suppressKey", true);
              });


        return input;
    },
    
    _updateList: function(list){
        var self = this;
        var opt = this.options;
        // input may not be set at this point...
        var val = this.input && this.input.val() || '';
        list = $(list)
            .filter(function() {
                return opt.match.call(this, val);
            })
            .map(function() {
                var node=$(opt.template.call(self, this))[0];
                $.data(node, "originalObject", this);
                return node;
            });
        this.off();
        if (!list.length) return false;
        
        var container = list.wrapAll(opt.wrapper).parents(":last");

        var offset = this.input.offset();
        this.container = container
            .css({
                top: offset.top + this.input.outerHeight(),
                left: offset.left
            })
            .appendTo("body");

        // set the container to the minimum of the input field's width,
        // but leave it if it already extends the input.
        // Also maximize to max_width.
        var container_width = Math.max(container.width(), this.input.width());
        container_width = Math.min(container_width, this.options.maxSearchContainerWidth);
        this.container
            .css({
                width: container_width
            });

        this.activelist = {
            is_active: true,
            original: this.input.val(),
            list: list,
            // Hoverables are by default the li's, but this
            // can be changed from options.
            // XXX Current code only works if the hoverables
            // are not embedded in more levels of li's.
            hoverable: container.find(this.options.selectHoverable)
        };

       this.activelist.hoverable
            .hover(
                function() {
                    self._setActive(this);
                },
                function() {
                    self._unsetActive();
                }
            );

        container
            .bind("click.autobox", function(e) {
                self.activate();
                $.data(document.body, "suppressKey", false);
            });

    },

    //return the currently selected values as a hash
    _getCurrentValsHash: function(input){
        var vals = input.parent().parent().find('li');
        var hash = {};
        for (var i=0; i < vals.length; ++i) {
            var s = vals[i].innerHTML.match(/^[^<]+/);
            if (s) {
                hash[s]=true;
            }
        }
        return hash;
    },

    _createHolder: function (element) {
        var input = this._bindInput($('<input type="text"></input>'));
        var holder=$('<ul class="autobox-hldr ui-helper-clearfix"></ul>')
            .append($('<li class="autobox-input"></li>')
            .append(input));
        $.fn.resizableTextbox(input, $.extend(this.options.resizable, { min: input.attr('offsetWidth'), max: holder.width() }));
        return holder;
    },

    _setupWidget: function() {
        var self = this;

        // create and wire up widget from above functions 
        var opt = this.options;
        var e = this.element;
        this.holder = this._createHolder(e).insertAfter(e);
        this.input = this.holder.find('input');
        e.removeAttr('name');
        e.hide();

        // set starting values
        if(opt.prevals) {
            for(var i in opt.prevals) {
                this._addBox(opt.prevals[i], true);
            }
        }

        // to be sure there is no FF-autocomplete
        this.input.attr('autocomplete', 'off');

        // If a click bubbles all the way up to the window, close the autobox
        // (Note, bind to document and not to windows.
        // If windows is used, event does not bubble up on IE.
        $(document).bind("click.autobox", function(){
            self.cancel();
        });

    },
    
    // This used to be in options. We keep that possibility.
    _getList: function(input, hash){
        var list = this.options.list;
        if(hash){ list=$(list).filter(function(){  return !hash[this.text]; }); }
        input.trigger("updateList", [list]);
    },

    _addBox: function(record, /*optional*/ initializing){
        var self = this;
        var input = this.input;
        var name = this.options.name;
        var ii = $('<input type="hidden"></input>');ii.attr('name', name);ii.val(record.tag);
        var li=$('<li class="bit-box"></li>').attr('id', 'bit-' + count++).text(record.tag);
        li.append($('<a href="#" class="closebutton"></a>')
              .bind('click', function(e) {
                  self._delBox(li);
                  e.preventDefault();
              }))
          .append(ii);
        input.parent().before(li);
        input.val('');
    },

    // Keep original stub on the API.
    addBox: function (text, /*optional*/ initializing){
        return this._addBox({tag: text}, initializing);
    },

    // Produce the tag record if enter is pressed, ie text typed in.
    // The method has a way to prevent adding the box if
    // nothing is returned.
    _getBoxOnEnter: function(){
        var val = this.input.val();
        if (val) {
            return {tag: val};
        }
        // Prevent add from happening.
        return;
    },

    _getBoxFromSelection: function() {
        return {tag: $.data(this.active[0], "originalObject").text};
    },

    _delBox: function(li) {
        li.remove();
    },

    activate: function() {
        // Try hitting return to activate autobox and then hitting it again on blank input
        // to close it.  w/o checking the active object first this input.trigger() will barf.
        if(this.active && this.active[0] && $.data(this.active[0], "originalObject")){
            // Adding a value from the search results selection
            this._addBox(this._getBoxFromSelection());
        } else {
            // Adding the typed in value
            // We generate the record first...
            // (null result means we need not add it)
            var record = this._getBoxOnEnter();
            if (record) { this._addBox(record); }
        }
        if (this.active) {
            this.input.trigger("activate.autobox", [$.data(this.active[0], "originalObject")]);
        }
        //this.active && this.input.trigger("activate.autobox", [$.data(this.active[0], "originalObject")]);
        //$("body").trigger("off.autobox");
        this.off();
    },

    off: function() {
        if (this.container) {
          this.container.remove();
          this.container = null;
        }
        this.activelist = {is_active: false};
          //this.input.unbind("keydown.autobox");
          //$("body").add(window).unbind("click.autobox").unbind("cancel.autobox").unbind("activate.autobox");
    },
         
    _setActive: function(el) {
        if (! this.activelist.is_active) {
            return;
        }
        this._unsetActive();
        var el = $(el)
        this.hovered = el;
        // Find the active parent, which is the li containing the hovered element
        this.active = el.is('li') ? el : el.parents('li').eq(0);
        // add the classes
        this.hovered.addClass('hover');
        this.active.addClass('active');
        // do the selection
        this.input.trigger("itemSelected.autobox", [$.data(this.active[0], "originalObject")]);
        this._handleActive()
    },

    _handleActive: function() {
        this.input.val(this.options.insertText($.data(this.active[0], "originalObject")));
    },

    _unsetActive: function() {
        this.activelist.list.removeClass('active');
        this.activelist.hoverable.removeClass('hover');
        this.active = null;
        this.hovered = null;
    },

    cancel: function() {
        this.input.trigger("cancel.autobox");
        // revert value to the one before we activated the autobox
        this.input.val(this.activelist.original);
        this.off();
    }

});   // END widget ui.autobox3


})(jQuery);

(function($){


$.widget('karl.multistatusbox', {
 
    options: {
        clsContainer: 'ui-widget',
        clsItem: 'ui-state-highlight ui-corner-all',
        hasCloseButton: true
    },
   
    _create: function() {
        // initialize the queue
        this.queue = [];
        // add container class to container
        this.element.addClass(this.options.clsContainer);
    },

    /*
     * Public methods
     **/

    /* Clear all messages, or all messages with a given queueCategory */
    clear: function(/*optional*/ queueCategory) {
        if (queueCategory === undefined) {
            // shortcut: clear all items
            this.element.empty();
            this.queue = [];
        } else {
            // Clear items of the given category
            var newQueue = [];
            $(this.queue).each(function() {
                // The element may have been deleted (by closebutton),
                // but we don't check for this, since remove() works
                // safe with elements already removed.
                if (this.queueCategory == queueCategory) {
                    this.item.remove();
                } else {
                    // keep item in queue
                    newQueue.push(this);
                }
            });
            this.queue = newQueue;
        }
    },

    /* Append a message */
    append: function(message, /*optional*/ queueCategory, clsItem) {
        // default queue category is null.
        if (queueCategory === undefined) {
            queueCategory = null;
        }
        // Append the item
        var item = $('<div class="karl-multistatusbox-item ui-helper-clearfix"></div>');
        // Add item classes to the item
        if (clsItem === undefined) {
            clsItem = this.options.clsItem;
        }
        item.addClass(clsItem);
        // Create message and (if needed) a close button
        item.append($('<div class="karl-multistatusbox-message"></div>').append(message));
        if (this.options.hasCloseButton) {
            item.append($('<a href="#" class="karl-multistatusbox-closebutton">' + 
                          '<span class="ui-icon ui-icon-closethick">X</span></a>')
                        .hover(
                            function(e) { $(this).addClass('ui-state-hover'); },
                            function(e) { $(this).removeClass('ui-state-hover'); }
                        )
                        .click(function(e) {
                            item.remove();    
                            e.preventDefault();
                        })
            );
        }
        this.element.append(item);
        // Remember it on the queue
        this.queue.push({
            item: item,
            queueCategory: queueCategory
        });
    },

    /* Append a message after clearing previous messages.
     * If queueCategory is specified, only the messages added with the
     * same category are cleared. */
    clearAndAppend: function(message, /*optional*/ queueCategory, clsItem) {
        this.clear(queueCategory);
        this.append(message, queueCategory, clsItem);
    }


    /*
     * Private methods
     **/


});

})(jQuery);


(function($){

/**
 * Captioned images
 */
$.widget('karl.karlcaptionedimage', {

    options: {
        clsWrapper: 'karl-captionedimage-wrapper'
    },

    _create: function() {
        var self = this;
        this.wrapper = $('<div></div>');
        this.proxy = $('<img>').appendTo(this.wrapper);
        this.wrapper.append('<br />');
        this.caption = $('<span></span>').appendTo(this.wrapper);
        // Copy image attributes to proxy
        var captiontext = this.element.attr('alt');
        var width = this.element.attr('width');
        this.proxy
            .attr('alt', captiontext)
            .attr('width', width)
            .attr('height', this.element.attr('height'))
            .attr('src', this.element.attr('src'))
            .addClass('karl-captionedimage-image');
        // Copy image attributes to wrapper
        this.wrapper[0].style.cssText = this.element[0].style.cssText;
        // Copy the css from the original element to the wrapper
        this.wrapper
            .attr('class', this.element.attr('class'))
            .removeClass('tiny-imagedrawer-captioned')
            .addClass(this.options.clsWrapper)
            // Set width of the wrapper, to allow easy centering. 
            .width(width);
        // convert image alignment to wrapper
        var align = this.element.attr('align');
        if (align == 'left') {
            this.wrapper.css('float', 'left');
        } else if (align == 'right') {
            this.wrapper.css('float', 'right');
        }
        // set caption text
        this.caption
            .text(captiontext)
            .addClass('karl-captionedimage-caption');
        // wrap the image
        // centerer plays a role on IE
        // XXX inlines don't work currently, though:
        // they become centered.
        this.centerer = $('<div></div>')
            .css('text-align', 'center')
            .append(this.wrapper);
        this.element.after(this.centerer);
        this.element
            .hide()
            .appendTo(this.centerer);
    },

    _destroy: function() {
        // unwrap the image
        this.centerer.replaceWith(this.element);
        this.element.show();
        $.Widget.prototype.destroy.call( this );
    }

});


})(jQuery);


(function($){

/**
 * Extended slider
 */
var ui_slider = $.ui.slider;
$.widget('karl.karlslider', $.extend({}, ui_slider.prototype, {

    options: $.extend({}, ui_slider.prototype.options, {
        enableClickJump: false, // clicking will jump instead of positioning the slider
        jumpStep: undefined,    // unit of jump step. Should be a multiple of 'step'.
        enableKeyJump: false    // up-down keys will also use the jump unit instead of the step unit.
    }),

    _create: function() {
        var o = this.options;
        if (! o.jumpStep) {
            // jumpStep equals the step by default.
            o.jumpStep = o.step;
            o.alignStep = o.step;
        } else {
            // Well... there is one place, where it accesses o.step
            // directly, for the keys... and there is no way to override
            // this. So, we rename
            //      jumpStep -> step
            //      step ->     alignStep
            // and we will use alignStep instead of step everywhere else.
            o.alignStep = o.step;
            // o.step will _only_ be used for keys now (from keydown handler)
            o.step = o.enableKeyJump ? o.jumpStep : o.step;
        }
        ui_slider.prototype._create.call(this);
    },

    destroy: function() {
        ui_slider.prototype.destroy.call(this);
    },

    // Copypaste _mouseCapture 
    //
    _mouseCapture: function( event ) {
        var o = this.options,
            position,
            normValue,
            distance,
            closestHandle,
            self,
            index,
            allowed,
            offset,
            mouseOverHandle;

        if ( o.disabled ) {
            return false;
        }

        this.elementSize = {
            width: this.element.outerWidth(),
            height: this.element.outerHeight()
        };
        this.elementOffset = this.element.offset();

        position = { x: event.pageX, y: event.pageY };
        normValue = this._normValueFromMouse( position );
        distance = this._valueMax() - this._valueMin() + 1;
        self = this;
        this.handles.each(function( i ) {
            var thisDistance = Math.abs( normValue - self.values(i) );
            if ( distance > thisDistance ) {
                distance = thisDistance;
                closestHandle = $( this );
                index = i;
            }
        });

        // workaround for bug #3736 (if both handles of a range are at 0,
        // the first is always used as the one with least distance,
        // and moving it is obviously prevented by preventing negative ranges)
        if( o.range === true && this.values(1) === o.min ) {
            index += 1;
            closestHandle = $( this.handles[index] );
        }

        allowed = this._start( event, index );
        if ( allowed === false ) {
            return false;
        }
        this._mouseSliding = true;

        self._handleIndex = index;

        closestHandle
            .addClass( "ui-state-active" )
            .focus();
        
        offset = closestHandle.offset();
        mouseOverHandle = !$( event.target ).parents().andSelf().is( ".ui-slider-handle" );
        this._clickOffset = mouseOverHandle ? { left: 0, top: 0 } : {
            left: event.pageX - offset.left - ( closestHandle.width() / 2 ),
            top: event.pageY - offset.top -
                ( closestHandle.height() / 2 ) -
                ( parseInt( closestHandle.css("borderTopWidth"), 10 ) || 0 ) -
                ( parseInt( closestHandle.css("borderBottomWidth"), 10 ) || 0) +
                ( parseInt( closestHandle.css("marginTop"), 10 ) || 0)
        };

        normValue = this._normValueFromMouse( position );

        if (this.options.enableClickJump) {
            var current = this.values(index);
            var delta = normValue - current; 
            if (delta == 0) {
                // clicked on handle. Do not slide, but permit the mouse capture.
                //console.log('nulldelta', normValue);
                return true;
            } else {
                var stepping = o.jumpStep;
                // mod the stepping with the step
                var mod = stepping % o.alignStep;
                if (mod > 0) {
                    // round upwards. So, always step.
                    stepping = stepping - mod + o.alignStep;
                }
                var value;
                if (delta < 0) {
                    value = current - stepping;
                } else {
                    value = current + stepping;
                }

                //console.log('stepping', normValue,  stepping);
                // value will be limited into the range from _slide.
                this._slide(event, index, value);
                // Prevent the capture.
                this._mouseStop(event);
                this._animateOff = true;
                return false;
            }
        } else {
            // compatibility default
            this._slide(event, index, normValue);
            this._animateOff = true;
            return true;
        }

    },

    _slide: function(event, index, newVal) {
        // limit the value with the minimum and maximum
        // this will make limits effective for both click and key movements
        // as the clicks don't do limitation, this is crucial for enableKeyJump
        newVal = Math.max(newVal, this._valueMin());
        newVal = Math.min(newVal, this._valueMax());
        // (XXX should also mod it here ???, otherwise key movements could fall
        // out the step grid if jumpStep is not a multiple of step)
        ui_slider.prototype._slide.call(this, event, index, newVal);
    },

    // Handling the jumpStep differently from (alignStep) step.
    // (it is burned directly into the keydown handle and changing
    // it would require to replicate the whole _create)
    //
    // XXX options.step -> options.alignStep
    //
    // returns the alignStep-aligned value that val is closest to, between (inclusive) min and max
    _trimAlignValue: function( val ) {
        if ( val < this._valueMin() ) {
            return this._valueMin();
        }
        if ( val > this._valueMax() ) {
            return this._valueMax();
        }
        var step = ( this.options.alignStep > 0 ) ? this.options.alignStep : 1,
            valModStep = val % step,
            alignValue = val - valModStep;

        if ( Math.abs(valModStep) * 2 >= step ) {
            alignValue += ( valModStep > 0 ) ? step : ( -step );
        }

        // Since JavaScript has problems with large floats, round
        // the final value to 5 digits after the decimal point (see #4124)
        return parseFloat( alignValue.toFixed(5) );
    },

    _setOption: function(key, value) {
        if (key == 'jump') {
            this.options.alignStep = value;
            if (! this.options.enableKeyJump) {
                // set step the same, as jumpStep.
                this.options.step = value;
            }
        } else if (key == 'jumpStep') {
            this.options.jumpStep = value;
            if (this.options.enableKeyJump) {
                // set step the same, as jumpStep.
                this.options.step = value;
            }
        } else {
            ui_slider.prototype._setOption.apply(this, arguments);
        }
    }

}));

})(jQuery);

(function($){

/* XXX we repeat the namespace as a prefix of the name,
 * because ui creates a global jQuery plugin with the name
 * only */
$.widget('karl.karlbuttonset', {

    options: {
        clsContainer: null
    },

    _create: function() {
        var self = this;
        
        // fetch parameters from original markup
        if (this.element.is('select')) {
            // Markup for single/multiple selector buttons:
            //
            // qualifier classes are:
            // "karl-buttonset-compact" or "compact"
            // "karl-buttonset-icons-only" or "icons-only"
            //
            // <select id="buttons2" name="buttons2" multiple="single"
            //         class="compact icons-only">
            //   <option value="Save" class="ui-icon-disk" selected="selected">Save</option>
            //   <option value="Delete" class="ui-icon-trash">Delete</option>
            // </select>
            //
            this.selectionType = this.element.attr('multiple') ? 'M' : 'S';
        } else {
            // Markup for pushable selector buttons:
            //
            // qualifier classes are:
            // "karl-buttonset-compact" or "compact"
            // "karl-buttonset-icons-only" or "icons-only"
            //
            // <div id="buttons1" class="compact icons-only">
            //   <button class="ui-icon-disk">Save</button>
            //   <button class="ui-icon-trash">Delete</button>
            //  </div>
            //
            this.selectionType = '';
        }
        this.compact = this.element.is('.compact') ||
                       this.element.is('.karl-buttonset-compact');
        this.iconsOnly = this.element.is('.icons-only') ||
                       this.element.is('.karl-buttonset-icons-only');

        // calculate classes needed to create the widget markup
        var clsContainer = 'fg-buttonset ui-helper-clearfix ';
        var clsButton = 'fg-button ui-state-default';
        if (this.compact) {
            clsContainer += ' fg-buttonset-single'; 
            //clsButton += ' ui-priority-primary'; // XXX ???
            // corners will be added to 1st and last button only
        } else {
            // corners added to all buttons
            clsButton += ' ui-corner-all';
        }

        if (this.options.clsContainer) {
            clsContainer += ' ' + this.options.clsContainer;
        }

        // wrap the element
        this.element.wrap('<div></div>');
        this.wrapper = this.element.parent();
        // make widget appear bound on wrapper
        this.wrapper.data(this.widgetName, this);
        // make original element disappear
        this.originalWasHidden = this.element.hasClass('ui-helper-hidden');
        this.element.addClass('ui-helper-hidden');

        // apply container class on the wrapper
        this.wrapper
            .addClass(clsContainer);

        // build buttons based on the original element
        this.buttons = []
        this.element.children().each(function(button_index) {
            var button = $(this);
            var text = button.text();
            // XXX XXX Need to test for title attr handling!
            var title = button.attr('title') || text;
            var icon_class = button.attr('class');
            var selected = button.attr('selected');
            var disabled = button.attr('disabled');
            
            var icon = '';
            if (icon_class) {
                icon = '<span class="ui-icon ' + icon_class + '"/>';
            }
            var button_class = clsButton;
            // handle disabled and selected state
            if (disabled) {
                button_class += ' ui-state-disabled';
            } else {
                if (selected) {
                    button_class += ' ui-state-active';
                }
            }
            if (self.iconsOnly) {
                button_class += ' fg-button-icon-solo';
            } else if (icon_class) {
                button_class += ' fg-button-icon-right';
                // TODO fg-button-icon-left could be supported too
            }


            var new_button = $('<span class="' + button_class + '"><a' +
                       '     title="' + title + '" href="#">' +
                       icon +
                       text +
                       '</a></span>');
            new_button
                .appendTo(self.wrapper)
                // Clicking on buttons
                .click(function(event) {
                    // Only act if the button is currently enabled.
                    if (! new_button.hasClass('ui-state-disabled')) {
                        self._click(button_index); 
                    }
                    // Needs to prevent default in all cases. We never
                    // want to follow the # link which is the default href
                    // for the buttons.
                    event.preventDefault();
                })
                .hover(
                    function() {
                        // Only add the cue if the button is not disabled
                        if (! new_button.hasClass('ui-state-disabled')) {
                            new_button.addClass('ui-state-hover');
                        }
                    },
                    function() { new_button.removeClass('ui-state-hover'); }
                );
            self.buttons.push(new_button[0]);
        });
        this.buttons = $(this.buttons);

        // arrange corners for first and last button
        if (this.compact) {
            this.buttons.eq(0).addClass('ui-corner-left');
            this.buttons.eq(this.buttons.length - 1).addClass('ui-corner-right');
        }

    },

    destroy: function() {
        if (this.wrapper.parent().length) {
            // avoid running this twice.
            this.wrapper.removeData(this.widgetName, this);
            this.element.removeData(this.widgetName, this);
            if (! this.originalWasHidden) {
                this.element.removeClass('ui-helper-hidden');
            }
            this.element.insertAfter(this.wrapper);
            this.wrapper.remove();
        }
        $.Widget.prototype.destroy.call(this);
    },

    // Gets the button control with the given index
    getButton: function(button_index) {
        return this.buttons.eq(button_index);
    },

    _click: function(button_index) {
        var self = this;
        if (this.selectionType == 'M') {
            var button = this.buttons.eq(button_index);
            button.toggleClass('ui-state-active');
            self._change(button_index, button.hasClass('ui-state-active'));
        } else if (this.selectionType == 'S') {
            var changed = false;
            this.buttons.each(function(index) {
                if (index != button_index) {
                    var button = $(this);
                    if (button.hasClass('ui-state-active')) {
                        button.removeClass('ui-state-active');
                        self._change(index, false);
                    }
                }
            });
            var new_button = this.buttons.eq(button_index);
            if (! new_button.hasClass('ui-state-active')) {
                new_button.addClass('ui-state-active');
                self._change(button_index, true);
            }
        } else { // selectionType == 'none'
            self._change(button_index, true);
        }
    },

    _change: function(button_index, value) {
        // update the event on the original element
        if (this.selectionType != '') {
            this.element.children().eq(button_index).attr('selected', value);
        }
        // trigger the change event on both the original and wrapper node.
        // We only trigger on the original node, it will bubble out.
        this.element.trigger('change.karlbuttonset', [button_index, value]);
    }

});

})(jQuery);

/**
* DD_roundies, this adds rounded-corner CSS in standard browsers and VML sublayers in IE that accomplish a similar appearance when comparing said browsers.
* Author: Drew Diller
* Email: drew.diller@gmail.com
* URL: http://www.dillerdesign.com/experiment/DD_roundies/
* Version: 0.0.2a -  preview 2008.12.26
* Licensed under the MIT License: http://dillerdesign.com/experiment/DD_roundies/#license
*
* Usage:
* DD_roundies.addRule('#doc .container', '10px 5px'); // selector and multiple radii
* DD_roundies.addRule('.box', 5, true); // selector, radius, and optional addition of border-radius code for standard browsers.
* 
* Just want the PNG fixing effect for IE6, and don't want to also use the DD_belatedPNG library?  Don't give any additional arguments after the CSS selector.
* DD_roundies.addRule('.your .example img');
**/

eval(function(p,a,c,k,e,r){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--)r[e(c)]=k[c]||e(c);k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('t K={16:\'K\',1L:G,1M:G,1d:G,2f:y(){u(D.2g!=8&&D.1N&&!D.1N[q.16]){q.1L=M;q.1M=M}17 u(D.2g==8){q.1d=M}},2h:D.2i,1O:[],1b:{},2j:y(){u(q.1L||q.1M){D.1N.2L(q.16,\'2M:2N-2O-2P:x\')}u(q.1d){D.2Q(\'<?2R 2S="\'+q.16+\'" 2T="#1P#2k" ?>\')}},2l:y(){t a=D.1k(\'z\');D.2m.1w.1Q(a,D.2m.1w.1w);u(a.12){2n{t b=a.12;b.1x(q.16+\'\\\\:*\',\'{1l:2U(#1P#2k)}\');q.12=b}2o(2p){}}17{q.12=a}},1x:y(a,b,c){u(1R b==\'1S\'||b===2V){b=0}u(b.2W.2q().1y(\'2X\')==-1){b=b.2q().2Y(/[^0-9 ]/g,\'\').1T(\' \')}H(t i=0;i<4;i++){b[i]=(!b[i]&&b[i]!==0)?b[C.1e((i-2),0)]:b[i]}u(q.12){u(q.12.1x){t d=a.1T(\',\');H(t i=0;i<d.1U;i++){q.12.1x(d[i],\'1l:2Z(K.1V.2r(q, [\'+b.1W(\',\')+\']))\')}}17 u(c){t e=b.1W(\'F \')+\'F\';q.12.1z(D.2s(a+\' {Q-1f:\'+e+\'; -30-Q-1f:\'+e+\';}\'));q.12.1z(D.2s(a+\' {-1A-Q-1m-1n-1f:\'+b[0]+\'F \'+b[0]+\'F; -1A-Q-1m-1X-1f:\'+b[1]+\'F \'+b[1]+\'F; -1A-Q-1Y-1X-1f:\'+b[2]+\'F \'+b[2]+\'F; -1A-Q-1Y-1n-1f:\'+b[3]+\'F \'+b[3]+\'F;}\'))}}17 u(q.1d){q.1O.31({\'2t\':a,\'2u\':b})}},2v:y(a){2w(32.33){I\'z.Q\':I\'z.34\':I\'z.1B\':q.1o(a);13;I\'z.2x\':q.1Z(a);13;I\'z.1p\':I\'z.2y\':I\'z.2z\':q.1o(a);13;I\'z.20\':a.18.z.20=(a.z.20==\'S\')?\'S\':\'35\';13;I\'z.21\':q.22(a);13;I\'z.1c\':a.18.z.1c=a.z.1c;13}},1o:y(a){a.14.23=\'\';q.2A(a);q.1Z(a);q.1C(a);q.1D(a);q.24(a);q.2B(a);q.22(a)},22:y(a){u(a.W.21.1y(\'36\')!=-1){t b=a.W.21;b=1g(b.37(b.25(\'=\')+1,b.25(\')\')),10)/2C;H(t v 1h a.x){a.x[v].1i.38=b}}},2A:y(a){u(!a.W){1q}17{t b=a.W}a.14.1p=\'\';a.14.1E=\'\';t c=(b.1p==\'2D\');t d=M;u(b.1E!=\'S\'||a.1F){u(!a.1F){a.J=b.1E;a.J=a.J.39(5,a.J.25(\'")\')-5)}17{a.J=a.26}t e=q;u(!e.1b[a.J]){t f=D.1k(\'3a\');f.1r(\'3b\',y(){q.1s=q.3c;q.1t=q.3d;e.1D(a)});f.3e=e.16+\'3f\';f.14.23=\'1l:S; 1j:27; 1m:-2E; 1n:-2E; Q:S;\';f.26=a.J;f.2F(\'1s\');f.2F(\'1t\');D.2G.1Q(f,D.2G.1w);e.1b[a.J]=f}a.x.Z.1i.26=a.J;d=G}a.x.Z.2H=!d;a.x.Z.1G=\'S\';a.x.1u.2H=!c;a.x.1u.1G=b.1p;a.14.1E=\'S\';a.14.1p=\'2D\'},1Z:y(a){a.x.1H.1G=a.W.2x},1C:y(a){t c=[\'N\',\'19\',\'1a\',\'O\'];a.P={};H(t b=0;b<4;b++){a.P[c[b]]=1g(a.W[\'Q\'+c[b]+\'U\'],10)||0}},1D:y(c){t e=[\'O\',\'N\',\'U\',\'V\'];H(t d=0;d<4;d++){c.E[e[d]]=c[\'3g\'+e[d]]}t f=y(a,b){a.z.1n=(b?0:c.E.O)+\'F\';a.z.1m=(b?0:c.E.N)+\'F\';a.z.1s=c.E.U+\'F\';a.z.1t=c.E.V+\'F\'};H(t v 1h c.x){t g=(v==\'Z\')?1:2;c.x[v].3h=(c.E.U*g)+\', \'+(c.E.V*g);f(c.x[v],M)}f(c.18,G);u(K.1d){c.x.1H.z.28=\'-3i\';u(1R c.P==\'1S\'){q.1C(c)}c.x.1u.z.28=(c.P.N-1)+\'F \'+(c.P.O-1)+\'F\'}},24:y(j){t k=y(a,w,h,r,b,c,d){t e=a?[\'m\',\'1I\',\'l\',\'1J\',\'l\',\'1I\',\'l\',\'1J\',\'l\']:[\'1J\',\'l\',\'1I\',\'l\',\'1J\',\'l\',\'1I\',\'l\',\'m\'];b*=d;c*=d;w*=d;h*=d;t R=r.2I();H(t i=0;i<4;i++){R[i]*=d;R[i]=C.3j(w/2,h/2,R[i])}t f=[e[0]+C.11(0+b)+\',\'+C.11(R[0]+c),e[1]+C.11(R[0]+b)+\',\'+C.11(0+c),e[2]+C.15(w-R[1]+b)+\',\'+C.11(0+c),e[3]+C.15(w+b)+\',\'+C.11(R[1]+c),e[4]+C.15(w+b)+\',\'+C.15(h-R[2]+c),e[5]+C.15(w-R[2]+b)+\',\'+C.15(h+c),e[6]+C.11(R[3]+b)+\',\'+C.15(h+c),e[7]+C.11(0+b)+\',\'+C.15(h-R[3]+c),e[8]+C.11(0+b)+\',\'+C.11(R[0]+c)];u(!a){f.3k()}t g=f.1W(\'\');1q g};u(1R j.P==\'1S\'){q.1C(j)}t l=j.P;t m=j.2J.2I();t n=k(M,j.E.U,j.E.V,m,0,0,2);m[0]-=C.1e(l.O,l.N);m[1]-=C.1e(l.N,l.19);m[2]-=C.1e(l.19,l.1a);m[3]-=C.1e(l.1a,l.O);H(t i=0;i<4;i++){m[i]=C.1e(m[i],0)}t o=k(G,j.E.U-l.O-l.19,j.E.V-l.N-l.1a,m,l.O,l.N,2);t p=k(M,j.E.U-l.O-l.19+1,j.E.V-l.N-l.1a+1,m,l.O,l.N,1);j.x.1u.29=o;j.x.Z.29=p;j.x.1H.29=n+o;q.2K(j)},2B:y(a){t s=a.W;t b=[\'N\',\'O\',\'19\',\'1a\'];H(t i=0;i<4;i++){a.14[\'1B\'+b[i]]=(1g(s[\'1B\'+b[i]],10)||0)+(1g(s[\'Q\'+b[i]+\'U\'],10)||0)+\'F\'}a.14.Q=\'S\'},2K:y(e){t f=K;u(!e.J||!f.1b[e.J]){1q}t g=e.W;t h={\'X\':0,\'Y\':0};t i=y(a,b){t c=M;2w(b){I\'1n\':I\'1m\':h[a]=0;13;I\'3l\':h[a]=0.5;13;I\'1X\':I\'1Y\':h[a]=1;13;1P:u(b.1y(\'%\')!=-1){h[a]=1g(b,10)*0.3m}17{c=G}}t d=(a==\'X\');h[a]=C.15(c?((e.E[d?\'U\':\'V\']-(e.P[d?\'O\':\'N\']+e.P[d?\'19\':\'1a\']))*h[a])-(f.1b[e.J][d?\'1s\':\'1t\']*h[a]):1g(b,10));h[a]+=1};H(t b 1h h){i(b,g[\'2y\'+b])}e.x.Z.1i.1j=(h.X/(e.E.U-e.P.O-e.P.19+1))+\',\'+(h.Y/(e.E.V-e.P.N-e.P.1a+1));t j=g.2z;t c={\'T\':1,\'R\':e.E.U+1,\'B\':e.E.V+1,\'L\':1};t k={\'X\':{\'2a\':\'L\',\'2b\':\'R\',\'d\':\'U\'},\'Y\':{\'2a\':\'T\',\'2b\':\'B\',\'d\':\'V\'}};u(j!=\'2c\'){c={\'T\':(h.Y),\'R\':(h.X+f.1b[e.J].1s),\'B\':(h.Y+f.1b[e.J].1t),\'L\':(h.X)};u(j.1y(\'2c-\')!=-1){t v=j.1T(\'2c-\')[1].3n();c[k[v].2a]=1;c[k[v].2b]=e.E[k[v].d]+1}u(c.B>e.E.V){c.B=e.E.V+1}}e.x.Z.z.3o=\'3p(\'+c.T+\'F \'+c.R+\'F \'+c.B+\'F \'+c.L+\'F)\'},1v:y(a){t b=q;2d(y(){b.1o(a)},1)},2e:y(a){q.1D(a);q.24(a)},1V:y(b){q.z.1l=\'S\';u(!q.W){1q}17{t c=q.W}t d={3q:G,3r:G,3s:G,3t:G,3u:G,3v:G,3w:G};u(d[q.1K]===G){1q}t e=q;t f=K;q.2J=b;q.E={};t g={3x:\'2e\',3y:\'2e\'};u(q.1K==\'A\'){t i={3z:\'1v\',3A:\'1v\',3B:\'1v\',3C:\'1v\'};H(t a 1h i){g[a]=i[a]}}H(t h 1h g){q.1r(\'3D\'+h,y(){f[g[h]](e)})}q.1r(\'3E\',y(){f.2v(e)});t j=y(a){a.z.3F=1;u(a.W.1j==\'3G\'){a.z.1j=\'3H\'}};j(q.3I);j(q);q.18=D.1k(\'3J\');q.18.14.23=\'1l:S; 1j:27; 28:0; 1B:0; Q:0; 3K:S;\';q.18.z.1c=c.1c;q.x={\'1u\':M,\'Z\':M,\'1H\':M};H(t v 1h q.x){q.x[v]=D.1k(f.16+\':3L\');q.x[v].1i=D.1k(f.16+\':3M\');q.x[v].1z(q.x[v].1i);q.x[v].3N=G;q.x[v].z.1j=\'27\';q.x[v].z.1c=c.1c;q.x[v].3O=\'1,1\';q.18.1z(q.x[v])}q.x.Z.1G=\'S\';q.x.Z.1i.3P=\'3Q\';q.3R.1Q(q.18,q);q.1F=G;u(q.1K==\'3S\'){q.1F=M;q.z.3T=\'3U\'}2d(y(){f.1o(e)},1)}};2n{D.3V("3W",G,M)}2o(2p){}K.2f();K.2j();K.2l();u(K.1d&&D.1r&&K.2h){D.1r(\'3X\',y(){u(D.3Y==\'3Z\'){t d=K.1O;t e=d.1U;t f=y(a,b,c){2d(y(){K.1V.2r(a,b)},c*2C)};H(t i=0;i<e;i++){t g=D.2i(d[i].2t);t h=g.1U;H(t r=0;r<h;r++){u(g[r].1K!=\'40\'){f(g[r],d[i].2u,r)}}}}})}',62,249,'||||||||||||||||||||||||||this|||var|if|||vml|function|style|||Math|document|dim|px|false|for|case|vmlBg|DD_roundies||true|Top|Left|bW|border||none||Width|Height|currentStyle|||image||floor|styleSheet|break|runtimeStyle|ceil|ns|else|vmlBox|Right|Bottom|imgSize|zIndex|IE8|max|radius|parseInt|in|filler|position|createElement|behavior|top|left|applyVML|backgroundColor|return|attachEvent|width|height|color|pseudoClass|firstChild|addRule|search|appendChild|webkit|padding|vmlStrokeWeight|vmlOffsets|backgroundImage|isImg|fillcolor|stroke|qy|qx|nodeName|IE6|IE7|namespaces|selectorsToProcess|default|insertBefore|typeof|undefined|split|length|roundify|join|right|bottom|vmlStrokeColor|display|filter|vmlOpacity|cssText|vmlPath|lastIndexOf|src|absolute|margin|path|b1|b2|repeat|setTimeout|reposition|IEversion|documentMode|querySelector|querySelectorAll|createVmlNameSpace|VML|createVmlStyleSheet|documentElement|try|catch|err|toString|call|createTextNode|selector|radii|readPropertyChanges|switch|borderColor|backgroundPosition|backgroundRepeat|vmlFill|nixBorder|100|transparent|10000px|removeAttribute|body|filled|slice|DD_radii|clipImage|add|urn|schemas|microsoft|com|writeln|import|namespace|implementation|url|null|constructor|Array|replace|expression|moz|push|event|propertyName|borderWidth|block|lpha|substring|opacity|substr|img|onload|offsetWidth|offsetHeight|className|_sizeFinder|offset|coordsize|1px|min|reverse|center|01|toUpperCase|clip|rect|BODY|TABLE|TR|TD|SELECT|OPTION|TEXTAREA|resize|move|mouseleave|mouseenter|focus|blur|on|onpropertychange|zoom|static|relative|offsetParent|ignore|background|shape|fill|stroked|coordorigin|type|tile|parentNode|IMG|visibility|hidden|execCommand|BackgroundImageCache|onreadystatechange|readyState|complete|INPUT'.split('|'),0,{}))
/**
 * jQuery.ScrollTo - Easy element scrolling using jQuery.
 * Copyright (c) 2007-2008 Ariel Flesler - aflesler(at)gmail(dot)com | http://flesler.blogspot.com
 * Dual licensed under MIT and GPL.
 * Date: 9/11/2008
 * @author Ariel Flesler
 * @version 1.4
 *
 * http://flesler.blogspot.com/2007/10/jqueryscrollto.html
 */
;(function(h){var m=h.scrollTo=function(b,c,g){h(window).scrollTo(b,c,g)};m.defaults={axis:'y',duration:1};m.window=function(b){return h(window).scrollable()};h.fn.scrollable=function(){return this.map(function(){var b=this.parentWindow||this.defaultView,c=this.nodeName=='#document'?b.frameElement||b:this,g=c.contentDocument||(c.contentWindow||c).document,i=c.setInterval;return c.nodeName=='IFRAME'||i&&h.browser.safari?g.body:i?g.documentElement:this})};h.fn.scrollTo=function(r,j,a){if(typeof j=='object'){a=j;j=0}if(typeof a=='function')a={onAfter:a};a=h.extend({},m.defaults,a);j=j||a.speed||a.duration;a.queue=a.queue&&a.axis.length>1;if(a.queue)j/=2;a.offset=n(a.offset);a.over=n(a.over);return this.scrollable().each(function(){var k=this,o=h(k),d=r,l,e={},p=o.is('html,body');switch(typeof d){case'number':case'string':if(/^([+-]=)?\d+(px)?$/.test(d)){d=n(d);break}d=h(d,this);case'object':if(d.is||d.style)l=(d=h(d)).offset()}h.each(a.axis.split(''),function(b,c){var g=c=='x'?'Left':'Top',i=g.toLowerCase(),f='scroll'+g,s=k[f],t=c=='x'?'Width':'Height',v=t.toLowerCase();if(l){e[f]=l[i]+(p?0:s-o.offset()[i]);if(a.margin){e[f]-=parseInt(d.css('margin'+g))||0;e[f]-=parseInt(d.css('border'+g+'Width'))||0}e[f]+=a.offset[i]||0;if(a.over[i])e[f]+=d[v]()*a.over[i]}else e[f]=d[i];if(/^\d+$/.test(e[f]))e[f]=e[f]<=0?0:Math.min(e[f],u(t));if(!b&&a.queue){if(s!=e[f])q(a.onAfterFirst);delete e[f]}});q(a.onAfter);function q(b){o.animate(e,j,a.easing,b&&function(){b.call(this,r,a)})};function u(b){var c='scroll'+b,g=k.ownerDocument;return p?Math.max(g.documentElement[c],g.body[c]):k[c]}}).end()};function n(b){return typeof b=='object'?b:{top:b,left:b}}})(jQuery);/*
 * jquery.tools 1.1.0 - The missing UI library for the Web
 * 
 * [tools.tooltip-1.1.0]
 * 
 * Copyright (c) 2009 Tero Piirainen
 * http://flowplayer.org/tools/
 *
 * Dual licensed under MIT and GPL 2+ licenses
 * http://www.opensource.org/licenses
 * 
 * -----
 * 
 * File generated: Thu Sep 03 11:27:27 GMT+00:00 2009
 */
(function(c){c.tools=c.tools||{};c.tools.tooltip={version:"1.1.0",conf:{effect:"slide",direction:"up",bounce:false,slideOffset:10,slideInSpeed:200,slideOutSpeed:200,slideFade:!c.browser.msie,fadeOutSpeed:"fast",tip:null,predelay:0,delay:30,opacity:1,lazy:undefined,position:["top","center"],cancelDefault:true,offset:[0,0],api:false,events:{def:"mouseover,mouseout",input:"focus,blur",widget:"focus mouseover,blur mouseout"}},addEffect:function(e,g,f){b[e]=[g,f]}};var b={toggle:[function(e){var f=this.getConf();this.getTip().css({opacity:f.opacity}).show();e.call()},function(e){this.getTip().hide();e.call()}],fade:[function(e){this.getTip().fadeIn(this.getConf().fadeInSpeed,e)},function(e){this.getTip().fadeOut(this.getConf().fadeOutSpeed,e)}]};var d={up:["-","top"],down:["+","top"],left:["-","left"],right:["+","left"]};c.tools.tooltip.addEffect("slide",function(e){var g=this.getConf(),h=this.getTip(),i=g.slideFade?{opacity:g.opacity}:{},f=d[g.direction]||d.up;i[f[1]]=f[0]+"="+g.slideOffset;if(g.slideFade){h.css({opacity:0})}h.show().animate(i,g.slideInSpeed,e)},function(f){var h=this.getConf(),j=h.slideOffset,i=h.slideFade?{opacity:0}:{},g=d[h.direction]||d.up;var e=""+g[0];if(h.bounce){e=e=="+"?"-":"+"}i[g[1]]=e+"="+j;this.getTip().animate(i,h.slideOutSpeed,function(){c(this).hide();f.call()})});function a(f,g){var p=this;f.data("tooltip",p);var l=f.next();if(g.tip){l=c(g.tip);if(l.length>1){l=f.nextAll(g.tip).eq(0);if(!l.length){l=f.parent().nextAll(g.tip).eq(0)}}}function h(q,r){c(p).bind(q,function(t,s){if(r&&r.call(this,s?s.position:undefined)===false&&s){s.proceed=false}});return p}function o(){var t=f.position().top-l.outerHeight();var q=l.outerHeight()+f.outerHeight();var u=g.position[0];if(u=="center"){t+=q/2}if(u=="bottom"){t+=q}var r=f.outerWidth()+l.outerWidth();var s=f.position().left+f.outerWidth();u=g.position[1];if(u=="center"){s-=r/2}if(u=="left"){s-=r}t+=g.offset[0];s+=g.offset[1];return{top:t,left:s}}c.each(g,function(q,r){if(c.isFunction(r)){h(q,r)}});var j=f.is(":input"),e=j&&f.is(":checkbox, :radio, select, :button"),i=f.attr("type"),n=g.events[i]||g.events[j?(e?"widget":"input"):"def"];n=n.split(/,\s*/);f.bind(n[0],function(r){var q=l.data("trigger");if(q&&q[0]!=this){l.hide()}r.target=this;p.show(r);l.hover(p.show,function(s){p.hide()})});f.bind(n[1],function(){p.hide()});if(!c.browser.msie&&!j){f.mousemove(function(){if(!p.isShown()){f.triggerHandler("mouseover")}})}if(g.opacity<1){l.css("opacity",g.opacity)}var m=0,k=f.attr("title");if(k&&g.cancelDefault){f.removeAttr("title");f.data("title",k)}c.extend(p,{show:function(r){if(r){f=c(r.target)}clearTimeout(l.data("timer"));if(l.is(":animated")||l.is(":visible")){return p}function q(){l.data("trigger",f);var t=o();if(g.tip&&k){l.html(k)}var s={proceed:true,position:t};c(p).trigger("onBeforeShow",s);if(s.proceed===false){return p}t=o();l.css({position:"absolute",top:t.top,left:t.left});b[g.effect][0].call(p,function(){c(p).trigger("onShow")})}if(g.predelay){clearTimeout(m);m=setTimeout(q,g.predelay)}else{q()}return p},hide:function(){clearTimeout(l.data("timer"));clearTimeout(m);if(!l.is(":visible")){return}function q(){var r={proceed:true};c(p).trigger("onBeforeHide",r);if(r.proceed===false){return}b[g.effect][1].call(p,function(){c(p).trigger("onHide")})}if(g.delay){l.data("timer",setTimeout(q,g.delay))}else{q()}return p},isShown:function(){return l.is(":visible, :animated")},getConf:function(){return g},getTip:function(){return l},getTrigger:function(){return f},onBeforeShow:function(q){return h("onBeforeShow",q)},onShow:function(q){return h("onShow",q)},onBeforeHide:function(q){return h("onBeforeHide",q)},onHide:function(q){return h("onHide",q)}})}c.prototype.tooltip=function(e){var f=this.eq(typeof e=="number"?e:0).data("tooltip");if(f){return f}var g=c.extend(true,{},c.tools.tooltip.conf);if(c.isFunction(e)){e={onBeforeShow:e}}else{if(typeof e=="string"){e={tip:e}}}c.extend(true,g,e);if(typeof g.position=="string"){g.position=g.position.split(/,?\s/)}if(g.lazy!==false&&(g.lazy===true||this.length>20)){this.one("mouseover",function(){f=new a(c(this),g);f.show()})}else{this.each(function(){f=new a(c(this),g)})}return g.api?f:this}})(jQuery);
