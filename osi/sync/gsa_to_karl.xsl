<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:exsl="http://exslt.org/common" xmlns:set="http://exslt.org/sets"
    xmlns:f="http://xml.spacelabstudio.com/foreign"
    xmlns:c="http://xml.karlproject.org/people/category" xmlns:p="http://xml.karlproject.org/people/userprofile"
    exclude-result-prefixes="set exsl" version="1.0">
    <xsl:output indent="yes"/>



    <!-- Start processing -->
    <xsl:template match="/">
        <xsl:apply-templates select="users"/>
    </xsl:template>
    <xsl:template match="users">
        <datastream>
            <xsl:apply-templates select="user"/>
            <!-- Make each of the categories -->
            <xsl:for-each select="set:distinct(/users/user/categories/category/category_item/id)">
                <c:category-item id="{.}">
                    <c:category id="{../../@id}">
                        <xsl:value-of select="../../@title"/>
                    </c:category>
                    <c:title>
                        <xsl:value-of select="../title"/>
                    </c:title>
                    <xsl:apply-templates select="../hcard"/>
                </c:category-item>
            </xsl:for-each>
        </datastream>
    </xsl:template>
    <xsl:template match="user">
        <p:profile>
            <p:username>
                <xsl:value-of select="username"/>
            </p:username>
            <p:auth_method>
                <xsl:value-of select="authentication"/>
            </p:auth_method>
            <p:sso_id>
                <xsl:value-of select="sso_id"/>
            </p:sso_id>
            <p:sha_password>
                <xsl:value-of select="password"/>
            </p:sha_password>
            <p:firstname>
                <xsl:value-of select="firstname"/>
            </p:firstname>
            <p:lastname>
                <xsl:value-of select="lastname"/>
            </p:lastname>
            <p:email>
                <xsl:value-of select="email"/>
            </p:email>
            <p:phone>
                <xsl:value-of select="phone"/>
            </p:phone>
            <p:extension>
                <xsl:value-of select="extension"/>
            </p:extension>
            <p:department>
                <xsl:value-of select="department"/>
            </p:department>
            <p:board>
                <xsl:value-of select="board"/>
            </p:board>
            <p:position>
                <xsl:value-of select="position"/>
            </p:position>
            <p:organization>
                <xsl:value-of select="organization"/>
            </p:organization>
            <p:location>
                <xsl:value-of select="location"/>
            </p:location>
            <p:country>
                <xsl:value-of select="country"/>
            </p:country>
            <p:website>
                <xsl:value-of select="website"/>
            </p:website>
            <p:languages>
                <xsl:value-of select="languages"/>
            </p:languages>
            <p:office>
                <xsl:value-of select="office"/>
            </p:office>
            <p:room_no>
                <xsl:value-of select="room_no"/>
            </p:room_no>
            <p:home_path>
                <xsl:value-of select="home_path"/>
            </p:home_path>
            <xsl:apply-templates select="categories/category[category_item]"/>
            <p:groups>
                <xsl:for-each select="groups/group/title">
                    <p:item>
                        <xsl:value-of select="."/>
                    </p:item>
                </xsl:for-each>
            </p:groups>
            <p:inactive>
              <xsl:if test="inactive">
                <xsl:value-of select="inactive"/>
              </xsl:if>
            </p:inactive>
        </p:profile>
    </xsl:template>
    <xsl:template match="category">
        <xsl:element name="p:{@id}">
            <xsl:for-each select="category_item">
                <p:item>
                    <xsl:value-of select="id"/>
                </p:item>
            </xsl:for-each>
        </xsl:element>
    </xsl:template>
    <xsl:template match="hcard">
        <xsl:variable name="adr" select="adrs/adr[@type='Main']"/>
        <xsl:variable name="tel" select="tels/tel[@type='Tel']"/>
        <xsl:variable name="fax" select="tels/tel[@type='Fax']"/>
        <xsl:variable name="email" select="emails/email"/>
        <xsl:variable name="note" select="note"/>
        <c:description>
        <xsl:if test="$tel/text() or $fax/text() or url/text()">

            &lt;div class=&quot;peopledir-hcard&quot;&gt;
                &lt;div class=&quot;vcard&quot;&gt;
                    &lt;div class=&quot;hcard-main&quot;&gt;
                    &lt;span class=&quot;fn org url&quot; href=&quot;<xsl:value-of select="url"/>&quot;&gt;<xsl:value-of select="fn"/>&lt;/span&gt;
                        &lt;div class=&quot;adr&quot;&gt;
                        &lt;div class=&quot;street-address&quot;&gt;<xsl:value-of select="$adr/street-address"/>&lt;/div&gt;
            &lt;span class=&quot;locality&quot;&gt;<xsl:value-of select="$adr/locality"/>&lt;/span&gt;
            &lt;abbr class=&quot;region&quot;&gt;<xsl:value-of select="$adr/region"/>&lt;/abbr&gt;
            &lt;span class=&quot;postal-code&quot;&gt;<xsl:value-of select="$adr/postal-code"/>&lt;/span&gt;
            &lt;div class=&quot;country-name&quot;&gt;<xsl:value-of select="$adr/country-name"/>&lt;/div&gt;
                        &lt;/div&gt;
                    &lt;/div&gt;
                    &lt;div class=&quot;hcard-secondary&quot;&gt;
            <xsl:if test="$tel/text()">
                        &lt;div class=&quot;tel&quot;&gt;
                        &lt;span class=&quot;type&quot;&gt;Tel&lt;/span&gt;: <xsl:value-of select="$tel"/> &lt;/div&gt;
            </xsl:if>
            <xsl:if test="$fax/text()">
                &lt;div class=&quot;tel&quot;&gt;
                &lt;span class=&quot;type&quot;&gt;Fax&lt;/span&gt;: <xsl:value-of select="$fax"/> &lt;/div&gt;
            </xsl:if>
            <xsl:if test="$email/text()">
                        &lt;div&gt;Email: &lt;span class=&quot;email&quot;&gt;
                            &lt;a href=&quot;mailto:<xsl:value-of select="$email"/>&quot;
                &gt;<xsl:value-of select="$email"/>&lt;/a&gt;
                        &lt;/span&gt;
                        &lt;/div&gt;
            </xsl:if>Website: &lt;a class=&quot;url&quot; href=&quot;<xsl:value-of select="url"/>&quot;&gt;<xsl:value-of select="url"/>&lt;/a&gt;
                        &lt;div class=&quot;note&quot;&gt; &lt;/div&gt;
                    &lt;/div&gt;
                    &lt;div style=&quot;clear: both&quot;&gt;&lt;/div&gt;

            <xsl:if test="$note/text()">
                &lt;p class=&quot;note&quot;&gt;<xsl:value-of select="$note"/>&lt;/p&gt;
            </xsl:if>

                &lt;/div&gt;
            &lt;/div&gt;
        </xsl:if>

        </c:description>
    </xsl:template>
    <xsl:template match="node()" mode="cleaner">
        <!-- Convenience function to not generate a node when
        the input node's text value is a series of blank spaces. -->
        <xsl:choose>
            <xsl:when test="normalize-space()">
                <xsl:element name="c:{name()}">.</xsl:element>
            </xsl:when>
        </xsl:choose>
    </xsl:template>
    <xsl:template match="adrs">
        <c:adrs xmlns:c="http://xml.soros.org/karl/people-category">
            <xsl:apply-templates select="adr"/>
        </c:adrs>
    </xsl:template>
    <xsl:template match="adr">
        <c:adr type="{@type}">
            <c:street-address>
                <xsl:value-of select="street-address"/>
            </c:street-address>
            <c:extended-address>
                <xsl:value-of select="extended-address"/>
            </c:extended-address>
            <c:locality>
                <xsl:value-of select="locality"/>
            </c:locality>
            <c:region>
                <xsl:value-of select="region"/>
            </c:region>
            <c:postal-code>
                <xsl:value-of select="postal-code"/>
            </c:postal-code>
            <c:country-name>
                <xsl:value-of select="country-name"/>
            </c:country-name>
        </c:adr>
    </xsl:template>
    <xsl:template match="tels">
        <c:tels xmlns:c="http://xml.soros.org/karl/people-category">
            <xsl:apply-templates select="tel"/>
        </c:tels>
    </xsl:template>
    <xsl:template match="tel">
        <c:tel type="{@type}">
            <xsl:value-of select="."/>
        </c:tel>
    </xsl:template>
    <xsl:template match="emails">
        <c:emails xmlns:c="http://xml.soros.org/karl/people-category">
            <xsl:apply-templates select="email"/>
        </c:emails>
    </xsl:template>
    <xsl:template match="email">
        <c:email type="{@type}">
            <xsl:value-of select="."/>
        </c:email>
    </xsl:template>



    <!-- Utility stuff -->
    <xsl:template name="set:distinct">
        <xsl:param name="nodes" select="/.."/>
        <xsl:param name="distinct" select="/.."/>
        <xsl:choose>
            <xsl:when test="$nodes">
                <xsl:call-template name="set:distinct">
                    <xsl:with-param name="distinct"
                        select="$distinct | $nodes[1][not(. = $distinct)]"/>
                    <xsl:with-param name="nodes" select="$nodes[position() > 1]"/>

                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates select="$distinct" mode="set:distinct"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="node()|@*" mode="set:distinct">
        <xsl:copy-of select="."/>

    </xsl:template>
</xsl:stylesheet>
