# Webscraper projects
I wrote the scrapers so they cannot be used with Terminal. These scrapers do not expect any passed arguments. They can be run through an IDE. 

Download each file and put it into the directory of your files you want to update. 

I used a links.py fiel which holds all links and passwords. 

The scrape_ebay.py file is dependent on both the link.py and the insolvenzregister.py file. You could also just copy the functions used in Insolvenzregister to scrape_ebay.py so you cut the dependency. 
 

## Insolvenzregister

In this project I webscraped the [german insolvency register](www.google.de) for different keys.

The keys can be updated to whatever one prefers. 
Furthermore the file uses Excel to create output and even can send emails when detected something new.

The output can be change in the payload variable. 

Using the MIMEMultipart package is much easier then typing everything in one string. 

### My findings
It was very hard to understand how to post with the bs4 package. Especially when new windows pop up the moment one presses a button on the site. Therefore I had to figure out how to do so and came up with that idea. 

Furthermore I had some problems with the email smtplib because I used Spyder IDE it was not quite clear that I have to run the script for sending the email all at one and not line by line. Therefore I got a lot of connection errors.   

Another problem was the naming of the dataframe columns. German umlaute (Ä ä Ö ö Ü ü) are very problematic. I found that if one uses umlaute in the columnnames one should put a u infromt of the string
```
df[u"Ähnlich"] = <some input>
```
## Ebay Kleinanzeigen
This scraper scrapes [Ebay Kleinanzeigen](https://www.ebay-kleinanzeigen.de/) In the manner where the base_url is given and you only need to make your search on the website and copy teh content of the link that comes after 'https://www.ebay-kleinanzeigen.de'

### My findings
This scraper was a bit harder because the classes I used at first had spaces in them like 
```
soup.find_all('li', class_='add-item lazy-load')
``` 

I had to seacrh for classes that where defined without any spaces in the class names so my programm would work regardless this behavior. Luckily I could do so otherwise i would have to parse the soup element  not to 'html' but 'lxml'


# Amazon AWS
I was searching for a very long time for a server that is cheap and can run my scripts automatically. After using heliohost, which is actually nice and free, I figured out that it can not fit my needs. Because my Cron jobs where conditional and I needed to have a Terminal.

Therefore Thanks to a friend of mine he introduced me to AWS. It is very easy to use. In the following I will explain and document for myself how to create an instance in AWS with an static IP and start the instance from your own terminal. 

## Create new Instance

1. Go to [Amazon AWS](https://aws.amazon.com/de/)
2. Create Sign up or Sign in 
3. Click on EC2
4. Click on Instances new
5. Chose a server that fits your needs. I choosed German servers you can look up the [prices](https://aws.amazon.com/de/ec2/pricing/on-demand/) here and compare them to each other
6. Install an OS I choosed Ubuntu 
7. Choose an Insatnce t2.micro has a free tier and perectly for small things like scrapers and small websites.
8. Press Review and Launch button 
9. :exclamation: Name the Pem file and download it :exclamation: Very important action it holds the key to your connection to the server. If you loose it you wont be able to connect anymore.
10. Open Terminal on your host laptop or PC
11. change directory to where you downloaded the pem file and ```sudo chmod 400 name_der_file.pem```
12. Go Back to AWS and copy the public IP Adress in teh details panel
13. Go back to your Terminal and type ```ssh -i name_der_file.pem ubuntu@ip_adresse``` This will start the instance
14. In AWS you can click on Elastik IP  in the sidebar and create one so your instance IP wont be dynamic anymore and you will not need to handle different IP adresses when you want to start your instance.
15. Click on new add IP adress then choose teh instance. Make sure you are in teh reagion where you created the instance in. Otherwise it wont find your instance. Neue IP hinzufügen dann die Instanz auswählen und die IP wird der Instanz zugewiesen 
16. Change display name of instance by ```sudo nano /etc/hostname``` and type anything you want
17. Reboot ```sudo reboot```
18. Start service ```ssh -i name_der_file.pem ubuntu@elastic_ipadresse``` This command you will use to start the service each and every time.
19. Done




