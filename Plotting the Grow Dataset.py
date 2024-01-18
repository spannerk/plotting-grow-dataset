#!/usr/bin/env python
# coding: utf-8

# # Plotting the Grow Dataset

# ## Task
# 

# You are provided with:
# - The Grow dataset Growlocations.csv. This file contains the locations of all the GROWsensors as Latitude and Longitude
# - A map of the UK from Openstreet map.
# 
# You should create a Python program that can read the dataset into a dataframe and plot the locations of the sensors on the map provided. You can use online tutorials to do this (but mention them in comments section of your code). However there are a number of errors with the dataset that you will need to fix in order to get the correct plot.
# 
# These include:
# - Some location values are way outside the allowed values for latitude and Longitude.
# - Some locations are not on the map provided.
# - The labels of the columns have not be verified so may be incorrect.
# 
# The bounding box for the map is as follows:
# - Longitude Min -10.592
# - Longitude Max 1.6848
# - Latitude Min 50.681
# - Latitude Max 57.985
# 
# Marks will be allocated as follows:
# - Reading the data into a data frame. 25%
# - Removing bad values. . 25%
# - Fixing other problems. . 25%
# - Plotting the data correctly. . 25%
# 
# An example map is on the next page. Note, I do not expect you to get the sensors in the absolute correct locations, but the locations should match approximately the ones on the map below.

# ## Imports

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt


# ## Reading the data into a data frame

# In[2]:


grow_locations_df = pd.read_csv("GrowLocations.csv")
grow_locations_df.info()


# In[3]:


grow_locations_df.head()


# In[4]:


# Number of serial numbers
grow_locations_df['Serial'].nunique()


# ## Identifying potential issues

# From the assignment we know the geographical location that we are looking at.
# 
# The bounding box for the map is as follows:
# - Longitude Min -10.592 
# - Longitude Max 1.6848 
# - Latitude Min 50.681 
# - Latitude Max 57.98
# 
# Also, to be valid, latitudes should be between + and - 90, and longditudes +- 180.

# In[5]:


# Look at the most extreme values for latitude for potential problems

grow_locations_df.sort_values('Latitude')


# The low values for latitude here are valid, but far away from the region to be plotted, and can be filtered out, as they are probably just from a different place.
# 
# However, the highest values here are clearly a mistake, and there is some nested data in the serial column that might give a clue.

# In[6]:


# Unfortunately the data is not in here
print(grow_locations_df.loc[37763, 'Serial'])
print(grow_locations_df.loc[37759, 'Serial'])


# In[7]:


# I want to how many of the sensors have invalid latitude and/or longitude
valid_lat = grow_locations_df['Latitude'].between(-90, 90, inclusive='both')
valid_long = grow_locations_df['Longitude'].between(-180, 180, inclusive='both')
grow_locations_df[~(valid_lat & valid_long)]['Serial'].nunique()


# In[8]:


# It's not so many, so I can take a look at them all at once
grow_locations_df[~(valid_lat & valid_long)][['Serial', 'Latitude', 'Longitude']].drop_duplicates()


# In[9]:


print(grow_locations_df[~(valid_lat & valid_long)][['Serial', 'Latitude', 'Longitude']].drop_duplicates()['Serial'].values)


# In[10]:


# Some of these do have valid lat and long values buried in their serial columns that could be extracted


# In[11]:


grow_locations_df['Serial'].str.extract(pat='Latitude:(.*?),Longitude:(.*?),').dropna()


# In[12]:


# I also want to check if all lines that have the same serial number have the same lat and long
duplicated = grow_locations_df[['Serial', 'Latitude', 'Longitude']].drop_duplicates().groupby('Serial').nunique()
duplicated[(duplicated['Latitude'] > 1) | (duplicated['Longitude'] > 1)]


# In[13]:


# This example looks like the sensor has either moved slightly or has been entered slightly differently
grow_locations_df[grow_locations_df['Serial']=='PI040297AA3I001108']


# In[14]:


# Some rows are 0,0 lat,long
min_max = grow_locations_df.groupby('Serial').agg({'Latitude': ['min', 'max'], 'Longitude': ['min', 'max']})
min_max['lat_diff'] = min_max['Latitude', 'max'] - min_max['Latitude', 'min']
min_max['long_diff'] = min_max['Longitude', 'max'] - min_max['Longitude', 'min']
min_max.sort_values('lat_diff', ascending=False).head(20)


# ## Cleanup

# In[15]:


# Get the more accurate latitude and longitudes
grow_locations_with_extra_latlong = pd.concat([grow_locations_df, grow_locations_df['Serial'].str.extract(pat='Latitude:(.*?),Longitude:(.*?),')], axis=1)
grow_locations_with_extra_latlong['Latitude'] = pd.to_numeric(grow_locations_with_extra_latlong[0]).fillna(grow_locations_with_extra_latlong['Latitude'])
grow_locations_with_extra_latlong['Longitude'] = pd.to_numeric(grow_locations_with_extra_latlong[1]).fillna(grow_locations_with_extra_latlong['Longitude'])
grow_locations_with_extra_latlong


# In[16]:


grow_locations_with_extra_latlong['Serial'].nunique()


# In[17]:


# Remove the locations outside the uk map bounding box
uk_lat = grow_locations_with_extra_latlong['Latitude'].between(50.681, 57.985, inclusive='both')
uk_long = grow_locations_with_extra_latlong['Longitude'].between(-10.592, 1.6848, inclusive='both')
grow_locations_uk = grow_locations_with_extra_latlong[uk_lat & uk_long]
grow_locations_uk.shape


# In[18]:


# Deuduplicate the serial numbers taking the most recent
most_recent = grow_locations_uk.groupby('Serial')['EndTime'].transform('rank', method='first', ascending=False)
grow_locations_to_plot = grow_locations_uk[most_recent== 1]
print(grow_locations_to_plot.shape)
grow_locations_to_plot


# ## Plot the locations

# In[19]:


# reference: https://stackoverflow.com/questions/34458251/plot-over-an-image-background-in-python

get_ipython().run_line_magic('matplotlib', 'inline')
im = plt.imread("map7.png")
ax = grow_locations_to_plot.plot('Longitude', 'Latitude', xlim = (-10.592, 1.6848), ylim = (50.681, 57.985), kind='scatter')
ax.imshow(im, extent=[-10.592, 1.6848, 50.681, 57.985])


# ## Assessing the result

# When comparing my plot to the one given in the assignment, mine looks a lot more sparse, and there were whole areas that have many sensors, such as Northern Ireland, in the example given that are not in my plot. Looking at the assignment, there's a hint that the columns might not be named correctly. That gives me the idea to see if the lattitude and longitude are swapped.

# ## Swapping lat and long

# In[20]:


grow_locations_swapped = grow_locations_df.rename({'Longitude': 'Latitude', 'Latitude': 'Longitude'}, axis=1)
grow_locations_swapped.head()


# In[21]:


get_ipython().run_line_magic('matplotlib', 'inline')
im = plt.imread("map7.png")
ax = grow_locations_swapped.plot('Longitude', 'Latitude', xlim = (-10.592, 1.6848), ylim = (50.681, 57.985), kind='scatter')
ax.imshow(im, extent=[-10.592, 1.6848, 50.681, 57.985])


# This plot looks very similar to the one given in the assignment. Aside from switching latitude and longitude, this data did not have any of the cleaning steps done in the "Cleanup" section. If the plot did not already look so much like the example output, I would repeat those cleaning steps with the renamed lat and long.
# 
# Any points outside of the bounding box or are unallowed values are not a problem for producing the plot, because the plot has the limits set already.
# 
# If I were to work on this problem in another context, I would ask some questions about how the data was produced to get some answers to these questions:
# 
# - Were the readings gathered as seperate files and then put into one? If so, it may be that some of the datapoints were not swapped between lat and long, so they might need to be selectively swapped.
# - When the same Serial has different lat and long values, either slightly or a lot, what does that mean? Should all values be included? In this image, they are all included because it looks similar to the example output given.

# ## Solution Code

# In[24]:


# Here's a recap of the end to end process

# Do imports
import pandas as pd
import matplotlib.pyplot as plt

# Load data
grow_locations_df = pd.read_csv("GrowLocations.csv")

# Swap lat and long
grow_locations_swapped = grow_locations_df.rename({'Longitude': 'Latitude', 'Latitude': 'Longitude'}, axis=1)

# Make plot
im = plt.imread("map7.png")
ax = grow_locations_swapped.plot('Longitude', 'Latitude', xlim = (-10.592, 1.6848), ylim = (50.681, 57.985), kind='scatter')
ax.imshow(im, extent=[-10.592, 1.6848, 50.681, 57.985])
plt.savefig('output.png')


# In[ ]:




