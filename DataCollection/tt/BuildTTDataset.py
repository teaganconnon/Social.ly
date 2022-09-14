from TikTokApi import TikTokApi

USERNAMES = ['siennasanter', 'k8888888', 'nicovee03', 'harvardhoneyyy', 'andrew.lobo', 'alicerubyferguson', 'adaacruz', 'leah_tad', 'ethanckelly', 'marycatherine78', 'm_spankey', 'a_vmack', 'harrystylesinadress', 'frankadvice']
TEST_USER = 'a_vmack'

with TikTokApi() as tt:
    for user in tt.search.users(TEST_USER):
        print(user)

#REEEEEEEE CAPTCHAAAAASSSSSSSSSSS >:()