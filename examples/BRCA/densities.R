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

LT <- read.table("lumA.train.in",header=TRUE)
BT <- read.table("basal.train.in",header=TRUE)

cdfL <- ddply(LT, .(subtype), summarize, rating.mean=mean(logl))
# each has $subtype and $logl fields

# Density plots with semi-transparent fill
pdf("lt.pdf")
#ggplot(LT, aes(x=logl, fill=subtype)) + geom_histogram(binwidth=.5, position="dodge") + 
ggplot(LT, aes(x=logl, fill=subtype)) + stat_density(position="stack", kernel="rectangular") + 
opts(title = "Luminal A Trained Signature", plot.title=theme_text(size=20), axis.title.x = theme_text(size=18))

pdf("bt.pdf")
#ggplot(BT, aes(x=logl, fill=subtype)) + geom_histogram(binwidth=.5, position="dodge") + 
ggplot(BT, aes(x=logl, fill=subtype)) + stat_density(position="stack", kernel="rectangular") + 
opts(title = "Basal Trained Signature", plot.title=theme_text(size=20), axis.title.x = theme_text(size=18))


print ("KS p-value for luminal trained:")
L_b <- as.numeric(LT[which(LT[,1] == "BASAL"),2])
L_l <- as.numeric(LT[which(LT[,1] == "LUM_A"),2])
print (ks.test(L_b, L_l))

print ("KS p-value for basal trained:")
B_b <- as.numeric(BT[which(BT[,1] == "BASAL"),2])
B_l <- as.numeric(BT[which(BT[,1] == "LUM_A"),2])
print (ks.test(B_b, B_l))


