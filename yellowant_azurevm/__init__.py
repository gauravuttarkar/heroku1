"""
Init file for azurevm app.
"""
import os
YA_DEVELOPER_TOKEN = os.environ.get("YA_DEVELOPER_TOKEN")
print(YA_DEVELOPER_TOKEN)
base = os.environ.get("HEROKU_APP_NAME")
#website = "https://{}.herokuapp.com/".format(base)
#api_url = "https://{}.herokuapp.com/yellowantauthurl/yellowant-api/".format(base)
#installation_website = "https://{}.herokuapp.com/".format(base)
#privacy_policy = "http://yellowant.com/privacy"
website = "https://{}.herokuapp.com/".format(base)

os.system("yellowant auth --token {} --host https://www.yellowant.com ".format(YA_DEVELOPER_TOKEN))
os.system('yellowant sync -q --api_url {}yellowant-api/ --website {} --install_page_url {} --\
privacy_policy_url {}privacy --redirect_uris {}yellowant-oauth-redirect/'.format(website,
                                                                                 website,
                                                                                 website,
                                                                                 website,
                                                                                 website))
os.system('ls -al')
