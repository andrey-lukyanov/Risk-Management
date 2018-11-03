##VaR for shares

#librares

library(tidyverse)
library(PerformanceAnalytics)
library(zoo)
library(readxl)
library(readr)
library(ggplot2)
library(forecast)
library(tseries)
library(dplyr)

#glimpse on data
return_1<-read_csv("1_day_returns.csv")
return_10<-read_csv("10_days_returns.csv")
prices<-read_csv("stock_prices.csv")
log_r_1<-read_csv("log_returns.csv")

Date_1<-return_1$Date
Date_10<-return_10$Date
Date_pr<-prices$Date
Date_lg<-log_r_1$Date

#won't work with packages fitdistrplus and logspline due to conflict with MASS !!!
prices<-select(prices,-Date)%>%xts(order.by = Date_pr)
r_10<-select(return_10,-Date)%>%xts(order.by = Date_10)
r_1<-select(return_1,-Date)%>%xts(order.by = Date_1)

tsRainbow_r1 <- rainbow(ncol(r_1))
plot(r_1, col=tsRainbow_r1, plot.type="single", xaxt="n", yaxt="n")

tsRainbow_r10 <- rainbow(ncol(r_10))
plot(r_10, col=tsRainbow, plot.type="single", xaxt="n", yaxt="n") #vse ochen' plokho

tsRainbow_pr <- rainbow(ncol(prices))
plot(prices, col=tsRainbow_pr, plot.type="single", xaxt="n", yaxt="n")


#log_returns
class(log_r_1)
ts_lr_1<-select(log_r_1,-Date)%>%xts(order.by = Date_lg)

#finaly data to use

View(ts_lr_1)
View(r_10)

autoplot.zoo(ts_lr_1)
autoplot.zoo(r_10)

tsRainbow <- rainbow(ncol(ts_lr_1))
plot(ts_lr_1, col=tsRainbow, plot.type="single", xaxt="n", yaxt="n") #vse ochen' plokho

#Desc_Statistics

summary(ts_lr_1)
skewness(ts_lr_1)
kurtosis(ts_lr_1)

#Is it normal?
plot(density(return_1$HSBA.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$BARC.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$LLOY.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$RBS.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$BP.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$RDSA.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$RIO.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$AAL.UK),main="Empirical cumulative distribution function ")

#no, it is not. fckit

#VaR_Manually

##Cov and Corr

cov_ln_1<-CoVariance(ts_lr_1, ts_lr_1)
cov_10<-CoVariance(r_10, r_10)
s_i1<-diag(cov_ln_1)
s_i10<-diag(cov_10)

chart.Correlation(ts_lr_1, ts_lr_1)
cor(ts_lr_1)
cor(r_10)
w<-c(.1,.1,.1, .1, .125,.125,.175,.175)

s_1<-sqrt(t(w)%*%cov_ln_1%*%w)
s_10<-sqrt(t(w)%*%cov_10%*%w)

#Dumb test
max(s_i1)>s_1
max(s_i10)>s_10

#VaR_Gaussian (need to model a R_Hui distr !!!)
VaR_DN_1<- -qnorm(p=.01)*s_1
VaR_DN_10<- -qnorm(p=.01)*s_10

#ES_Gaussian
ES_DN_1<-pnorm(q=.01)*s_1
ES_DN_10<-pnorm(q=.01)*s_10

#Check-in with a help of the special package

PA_1<-VaR(ts_lr_1, p=0.99, method = "gaussian", portfolio_method = "component", weights = c(.1,.1,.1, .1, .125,.125,.175,.175))

#VaR_Historical_1
w
Scen<- r_1%*%w

i=0
g=c()
for (i in 0:(nrow(r_1)-1)){
  i=i+1
  g[i]<-i/nrow(r_1)
  g
}
g

prob_1<-cbind(Scen, f)%>%as.data.frame()%>%arrange(desc(f)) #from the largest to the least !!!

n<-round(nrow(prob_1)*0.99, digits = 0)

VaR_HS_1<-prob_1[n, 2]

#VaR_Historical_10

Scen_10<- r_10%*%w

i=0
f<-c()
for (i in 0:(nrow(r_10)-1)){
  i=i+1
  f[i]<-i/nrow(r_10)
  f
}
f

prob_10<-cbind(Scen_10, f)%>%as.data.frame()%>%arrange(desc(f)) #from the largest to the least !!!

m<-round(nrow(prob_10)*0.99, digits = 0)

VaR_HS_10<-prob_10[m, 2]

#Dumb test
max(s_i1)>VaR_HS_1 #something wrong
max(s_i10)>VaR_HS_10

#ES_Historical NO, NOOOOO

#VaR_Model_PCA
library(devtools)
#install_github("vqv/ggbiplot")
library(ggbiplot)

#under assumption of norm distribution

pca_1<-prcomp(ts_lr_1, center = T,scale. = T, retx = T)
glimpse(pca_1)

pca_directions1<-pca_1$scale%>%as.data.frame()
pca_factors1<-pca_1$x%>%as.data.frame()
coef_m<-t(pca_1$rotation)
summary(pca_factors1)
var_f1<-var(pca_factors1)%>%diag()
var_f1
var_coef<-var(coef_m)

ggplot(pca_factors1, alpha=.9)+geom_density(aes(x=PC1, fill='red',alpha=.5))+geom_density(aes(x=PC2,fill='blue',alpha=.5))+geom_density(aes(x=PC3, fill='green',alpha=.5))+geom_density(aes(x=PC4,fill='yellow',alpha=.5))+geom_density(aes(x=PC5, fill='purple',alpha=.5))+ 
  geom_density(aes(x=PC6, fill='orange',alpha=.5))+geom_density(aes(x=PC7, fill='pink',alpha=.5))+geom_density(aes(x=PC8, fill='black',alpha=.5))

# #Dumb test
# reconst_1<-pca_factors1%*%pca_directions1
#

#model ajustment LOST HERE 

mat1<-eigen(cor(scale(ts_lr_1)))
l_1<-mat1$vectors
ev_1<-mat1$values

library(Matrix)

share_pca<-l_1%*%t(Diagonal(ev_1))
pca_unajd<-t(w)%*%share_pca%*%w

cum_var<-sum(var_coef)
pca_rescale<-pca_unajd/cum_var

cross_val<-share_pca/sqrt(share_pca[8,8])
share_adj<-share_pca - cov_ln_1 #hernya kakaya-nto
pca_adj<-

ggbiplot(pca,labels=rownames(ts_lr_1))
ggbiplot(pca, choices = c(1,2),labels=rownames(ts_lr_1))

ggbiplot(pca,labels=rownames(ts_lr_1))



# source("https://bioconductor.org/biocLite.R")
# biocLite("pcaMethods")
library(pcaMethods)
pcamet<-pca(ts_lr_1, scale = "vector", center = F, nPcs = 4, method = "svd")
slplot(pcamet)
glimpse(pcamet)

#Finally, it's driven mad
require(ggplot2)
require(reshape2)


#ES_Model


#VaR and ES with packages

#VaR(r_10, p=0.99, method = "historical", portfolio_method = "component", weights = c(.1,.1,.1, .1, .125,.125,.175,.175))
ES(ts_lr_1, p=0.99, method = "historical", portfolio_method = "single")






