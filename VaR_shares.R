#VaR for shares

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

r_10<-select(return_10, -Date)%>%xts(order.by = Date_10)

#log_returns
class(log_r_1)
ts_lr_1<-select(log_r_1, -Date)%>%xts(order.by = Date_lg)

#finaly data to use

View(ts_lr_1)
View(r_10)

autoplot.zoo(ts_lr_1)
autoplot.zoo(r_10)

#Desc_Statistics

statistics<-summary(ts_lr_1)
skewness(ts_lr_1)

#first try Value-a-risk and Expected Shortfall

VaR(r_1, p=0.99, method = "historical", portfolio_method = "component", weights = c(.1,.1,.1, .1, .125,.125,.175,.175)) 
ES(ts_lr_1, p=0.99, method = "historical", portfolio_method = "single")
