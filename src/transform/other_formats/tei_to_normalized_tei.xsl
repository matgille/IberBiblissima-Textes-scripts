<?xml version="1.0" encoding="UTF-8"?>
<!--Transformation de la TEI structurée à de la TEI lisible par l'humain-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    xmlns:tei="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="xs math"
    version="3.0">

    <xsl:mode on-no-match="shallow-copy"/>


    <xsl:template match="tei:choice">
        <xsl:apply-templates select="corr"/>
        <xsl:apply-templates select="tei:reg"/>
    </xsl:template>

    <xsl:template match="tei:ex | tei:hi">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:g[@ref = '#calderon1']">
        <xsl:text>¶ </xsl:text>
    </xsl:template>


    <xsl:template match="tei:lb | tei:fw"/>
</xsl:stylesheet>
