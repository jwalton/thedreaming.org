<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform version="2.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:xs="http://www.w3.org/XMLSchema"
 xmlns:fn="http://www.w3.org/2005/xpath-functions"
 xmlns:td="http://www.thedreaming.org/itunesToM3u"
>
  <!-- iTunes XML to M3U XSLT Converter 
     - By: Jason Walton (qtz [!at!] thedreaming [!dot!] org)
     -
     - This is an XSLT transform which will take an XML playlist exported by iTunes
     - and covert it to an M3U file.
     -
     - This requires a XSLT-2.0 compatible XSLT processor such as Saxon (http://saxon.sourceforge.net).
     -
     - To use, export your playlist from iTunes as an XML file, and then:
     -
     -   java -jar saxon9.jar -s:MyPlaylist.xml -xsl:itunesToM3u.xsl -o:MyPlaylist.m3u
     -
     - Tested with Saxon v9.0.0.2 and iTunes 7.5.0.20.
    -->

  <xsl:output method='text'/>

  <xsl:function name="td:decodeUri">
    <xsl:param name="uri"/>
    <xsl:variable name="tokenizedUri" select="fn:tokenize($uri, '%')"/>
    <xsl:value-of select="td:decodeUriHelper($tokenizedUri[1], fn:remove($tokenizedUri, 1))"/>
  </xsl:function>

  <xsl:function name="td:decodeUriHelper">
    <xsl:param name="decodedUri"/>
    <xsl:param name="uriFragments"/>
    <xsl:choose>
      <xsl:when test="fn:empty($uriFragments)">
        <xsl:value-of select="$decodedUri"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="nextFragment" select="$uriFragments[1]"/>
        <xsl:variable name="fragmentChar" select="fn:codepoints-to-string(
	  td:hex-to-char(fn:substring($nextFragment, 1, 2)))"/>
	<xsl:variable name="fragmentRemainder" select="fn:substring($nextFragment, 3)"/>
	<xsl:variable name="newDecodedUri">
	  <xsl:value-of select="$decodedUri"/>
	  <xsl:value-of select="$fragmentChar"/>
	  <xsl:value-of select="$fragmentRemainder"/>
	</xsl:variable>
	<xsl:value-of select="td:decodeUriHelper($newDecodedUri, fn:remove($uriFragments, 1))"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  
  
  <!-- Courtesy Michael Kay -->
  <xsl:function name="td:hex-to-char">
    <xsl:param name="in"/>
    <xsl:sequence select="
      if(string-length($in) eq 1) then
        td:hex-digit-to-integer($in)
      else
        16*td:hex-to-char(substring($in, 1, string-length($in)-1)) +
	td:hex-digit-to-integer(substring($in, string-length($in)))"/>
  </xsl:function>
  
  <xsl:function name="td:hex-digit-to-integer">
    <xsl:param name="char"/>
    <xsl:sequence select="string-length(substring-before('0123456789ABCDEF',
      fn:upper-case($char)))"/>
  </xsl:function>
  
  <xsl:template match="/">
    <xsl:text>#EXTM3U&#10;</xsl:text>

    <xsl:for-each select="plist/dict/dict/dict">

      <!-- Write the EXTINF line -->
      <xsl:text>#EXTINF:</xsl:text>
      <xsl:value-of select="key[.='Total Time']/following-sibling::*[1] idiv 1000"/>
      <xsl:text>,</xsl:text>
      <xsl:value-of select="key[.='Name']/following-sibling::*[1]"/>
      <xsl:text>&#10;</xsl:text>

      <!-- Write the location of the file -->
      <xsl:variable name="locationUrl"><xsl:value-of select="key[.='Location']/following-sibling::*[1]"/></xsl:variable>
      <xsl:value-of select="fn:replace(td:decodeUri($locationUrl), 'file://localhost/', '')"/>
      <xsl:text>&#10;</xsl:text>

    </xsl:for-each>
  </xsl:template>
</xsl:transform>
