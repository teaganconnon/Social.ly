# df = pd.read_csv('DataCollection/csv/US_youtube_trending_data.csv', index_col=0)

# # get all unique channels with videos trending in date range
# channels = df.channelId.unique()

# # query api to get top 50 videos of each unique channel

# # assemble dataset of videos grouped by channels which have trended
# # theory being that channels which trending often are likely to produce videos with high view counts, implying a higher level of production, implying a larger budget, implying sponsorships
# # train text classifier capable of unsupervised learning given keywords to identify sponsored videos based on description (maybe tags)
# # then train new supervised classifier with labeled sponsored data based on all other factors besides description probably