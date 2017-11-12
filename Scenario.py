import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import scipy.stats as stats
import seaborn as sns
import sys


if len(sys.argv) < 2:
    raise Exception('missing file argument')
filename = sys.argv[1]

print("Please wait while importing and cleaning the data...")

# we read the data from the file
data1 = pd.read_csv(filename,names=["tn","Cn","Rn"],sep="\t")

# We add columns corresponding to our useful parameters
df=pd.DataFrame({"tn":data1.tn,'Cn':data1.Cn,'Rn':data1.Rn,"mean_Rn":'NaN', 'Tn':'NaN',
                 "Sn":'NaN',"mean_Sn":'NaN',"Dn":'NaN'
                 ,"mean_Dn":'NaN',"Day":'NaN',"Week":'NaN'})

# please read the presentation for details about parameters calculations
df.mean_Rn=df.Rn/df.Cn

# we prefer the matrix format for better performances
dm=df.as_matrix(columns=['tn','Cn','Rn','mean_Rn','Tn','Sn',"mean_Sn","Dn","mean_Dn","Day","Week"])
dm[0,4]=0
dm[0,7]=0
dm[0,8]=0
dm[0,5]=dm[0,2]
dm[0,6]=dm[0,2]/dm[0,1]
for i in range(1,len(df.Cn)):
    dm[i,4]=dm[i,0]-dm[i-1,0]
    dm[i,7]=max(0,dm[i-1,2]-dm[i,4])
    dm[i,5]=dm[i,2]-dm[i,7]
    dm[i,6]=dm[i,5]/dm[i,1]
    dm[i,8]=dm[i,7]/dm[i,1]




# we convert the result matrix into a dataframe
df=pd.DataFrame(dm)
df=df.rename(columns={0:'tn',1:'Cn',2:'Rn',3:'mean_Rn',4:'Tn',5:'Sn',6:"mean_Sn",7:"Dn",8:"mean_Dn",9:"Day",10:"Week"})

# for convenience, we consider the time frame to start at unix time
df.index= pd.to_datetime(df.pop('tn'),unit='s')

# reindexing for adding missing rows with 0 requests : useful for timeseries decomposition
idx=pd.date_range(start='1970-01-01 06:00:01', end='1970-01-15 06:00:00', freq='s')
df=df.reindex(idx)

# seconds with 0 requests have Cn=0;Rn=0;Sn=0;Dn=0  , while mean_(Rn/Sn/Dn) per request are not defined
df.Cn[df.Cn.isnull()]=0
df.Rn[df.Rn.isnull()]=0
df.Sn[df.Sn.isnull()]=0
df.Dn[df.Dn.isnull()]=0

# about 10 values of Sn are negative, which is impossible in the reality
# we treat them as missing values

df.mean_Sn[df.mean_Sn<0]='NaN'
df.Sn[df.Sn<0]='Nan'

# we define days and weeks as the problem instructions, starting at 6 am
for i in range(1,15):
    df.Day.loc['1970-01-0%d 06:00:01'%i:'1970-01-0%d 06:00:00'%(i+1)]=i

df.Week.loc['1970-01-01 06:00:01':'1970-01-08 06:00:00']=1
df.Week.loc['1970-01-08 06:00:01':]=2

# convert values to numeric format to avoid errors
df.Cn=pd.to_numeric(df.Cn, errors='coerce')
df.mean_Rn=pd.to_numeric(df.mean_Rn, errors='coerce')
df.mean_Sn=pd.to_numeric(df.mean_Sn, errors='coerce')



# fill the missing values for the seconds with no request using weighted neighbours average
df.mean_Rn= df.mean_Rn.interpolate()
df.mean_Sn= df.mean_Sn.interpolate()

# first plot
plt.figure(1)
plt.plot(df.mean_Rn.index,df.mean_Rn.values)
plt.title(filename)
plt.xlabel("Day")
plt.ylabel("Mean Response Time per Request")


# plot of the daily mean_Rn mean
plt.figure(2)
daily_mean=df.groupby('Day').mean_Rn.mean().plot(title=filename)
daily_mean.set_xlabel("Day")
daily_mean.set_ylabel("Mean response time per request")
plt.grid(True)


#the weekly mean of mean_Rn and maximum value
print("maximum value of the response time per request : ")
print(df.mean_Rn.max())
print("weekly mean of the response time per request : ")
print(df.groupby('Week').mean_Rn.mean())
print("Please wait while creating all the plots...")

# plot of the daily mean_Rn standard deviation
plt.figure(3)
daily_mean=df.groupby('Day').mean_Rn.std().plot(title="filename")
daily_mean.set_xlabel("Day")
daily_mean.set_ylabel("Standard deviation")
plt.grid(True)

#obtain the hourly mean of the mean_Rn
hourly_data= df.resample('h').mean()


# Time series decomposition
decompfreq=24
res=sm.tsa.seasonal_decompose(hourly_data.mean_Rn,
                                freq=decompfreq,
                                model='additive')
resplot = res.plot()


# fit a log-normal distribution to the service time per request
# need to convert the series into a list, otherwise seaborn returns an error
plt.figure(5)
sns.distplot(list(df.mean_Sn),kde=False,fit=stats.lognorm)
plt.title(filename +" : distribution of the service time per request")
plt.xlabel("service time per request ( s )")
plt.ylabel("Relative Proportion ( % )")
plt.grid(True)


# plot of hourly mean of service time er request against the hourly number of requests
plt.figure(6)
plt.plot(hourly_data.Cn,hourly_data.mean_Sn,'bo')
plt.title("filename")
plt.xlabel("Number of requests per hour")
plt.ylabel("Mean Service time")
plt.grid(True)


# see how correlated are number of requests and service time
plt.figure(7)
plt.subplot(211)
plt.plot(hourly_data.Cn)
plt.title(filename +" : Cause of the Service Time")
plt.ylabel("Hourly number of requests")
plt.grid(True)

plt.subplot(212)
plt.plot(hourly_data.mean_Sn)
plt.ylabel("Mean Service time")
plt.grid(True)
plt.show()

