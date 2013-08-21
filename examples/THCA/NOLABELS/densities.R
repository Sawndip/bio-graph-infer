#!/usr/bin/env	Rscript

library(ggplot2)
library(plyr)


# Set the THEME
#theme_set( theme_bw( base_family= "serif"))
#theme_update( plot.title = theme_text(size=20),
#             axis.title.x= theme_text(size=16),
#             axis.text.x= theme_text( family= "serif",
#               angle= 90, hjust= 1 ),
#             axis.text.x= theme_text( family= "serif"),
#             axis.title.y= theme_text(size=14))
#
#theme_map <- theme_get()
#theme_set(theme_bw())

BRAF <- read.table("2cv.braf.in",header=TRUE,sep="\t")

cdfL <- ddply(BRAF, .(subtype), summarize, rating.mean=mean(logl))
# each has $subtype and $logl fields

# Density plots with semi-transparent fill
pdf("braf.pdf")
#ggplot(LT, aes(x=logl, fill=subtype)) + geom_histogram(binwidth=.5, position="dodge") + 
ggplot(BRAF, aes(x=logl, fill=subtype)) + stat_density(position="stack", kernel="rectangular") + 
opts(title = "THCA: TieDIE BRAF Mutation Signature", plot.title=theme_text(size=20), axis.title.x = theme_text(size=18))

