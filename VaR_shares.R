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
prices<-select(-Date)%>%xts(order.by = Date_pr)
r_10<-select(return_10,-Date)%>%xts(order.by = Date_10)
r_1<-select(return_1,-Date)%>%xts(order.by = Date_1)


#log_returns
class(log_r_1)
ts_lr_1<-select(log_r_1,-Date)%>%xts(order.by = Date_lg)

#finaly data to use

View(ts_lr_1)
View(r_10)

autoplot.zoo(ts_lr_1)
autoplot.zoo(r_10)

#Desc_Statistics

<<<<<<< HEAD
statistics<-summary(ts_lr_1)
skewness(ts_lr_1)
kurtosis(ts_lr_1)

=======
a<-summary(ts_lr_1)
b<-skewness(ts_lr_1)
c<-kurtosis(ts_lr_1)

#Is it normal?
plot(density(return_1$HSBA.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$BARC.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$LLOY.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$RBS.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$BP.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$RDSA.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$RIO.UK),main="Empirical cumulative distribution function ")
plot(density(return_1$AAL.UK),main="Empirical cumulative distribution function ")


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

#VaR_Gaussian (need to model a R_Hui distr !!!)
VaR_DN_1<-qnorm(p=.01)*s_1
VaR_DN_10<-qnorm(p=.01)*s_10

max(s_i1)>VaR_DN_1
max(s_i10)>VaR_DN_10


#ES_Gaussian
ES_DN_1<-pnorm(q=.01)*s_1
ES_DN_10<-pnorm(q=.01)*s_10

VaR(ts_lr_1, p=0.99, method = "gaussian", portfolio_method = "component", weights = c(.1,.1,.1, .1, .125,.125,.175,.175)) 


#VaR_Historical_1
w
Scen<- r_1%*%w

i=0
for (i in 0:(nrow(r_1)-1)){
  i=i+1
  f[i]<-i/nrow(r_1)
  f
}
f

prob_1<-cbind(Scen, f)%>%as.data.frame()%>%arrange(desc(f)) #from the largest to the least !!!

n<-round(nrow(prob_1)*0.99, digits = 0)

VaR_HS_1<-prob_1[n, 2]

#VaR_Historical_10

Scen_10<- r_10%*%w

i=0
for (i in 0:(nrow(r_10)-1)){
  i=i+1
  f[i]<-i/nrow(r_10)
  f
}
f

prob_10<-cbind(Scen_10, f)%>%as.data.frame()%>%arrange(desc(f)) #from the largest to the least !!!
>>>>>>> 2c0138dc5427e945a31a74f19ba00650c80e5874

m<-round(nrow(prob_1)*0.99, digits = 0)

VaR_HS_10<-prob_10[m, 2]

#Dumb test
max(s_i1)>VaR_HS_1 #something wrong
max(s_i10)>VaR_HS_10

#ES_Historical NO, NOOOOO"

#VaR_Model_PCA
library(devtools)
#install_github("vqv/ggbiplot")
library(ggbiplot)

#under assumption of norm distribution

pca<-prcomp(ts_lr_1, center = T,scale. = T, retx = T)
summary(pca)

ggbiplot(pca)

# source("https://bioconductor.org/biocLite.R")
# biocLite("pcaMethods")
# library(pcaMethods)

#ES_Model



#VaR and ES with packages

#VaR(r_10, p=0.99, method = "historical", portfolio_method = "component", weights = c(.1,.1,.1, .1, .125,.125,.175,.175))
ES(ts_lr_1, p=0.99, method = "historical", portfolio_method = "single")


<<<<<<< HEAD
portfolio_returns <- ts_lr_1 %*% c(.1,.1,.1, .1, .125,.125,.175,.175) 

skewness(portfolio_returns)
kurtosis(portfolio_returns)

hist(portfolio_returns)

library(fitdistrplus)
library(logspline)

descdist(c(portfolio_returns), discrete = FALSE)
=======



>>>>>>> 2c0138dc5427e945a31a74f19ba00650c80e5874






