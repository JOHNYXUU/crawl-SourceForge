# crawl-SourceForge
***

## Summary:

This is a file for crawling information of projects on **SourceForge**.

In this repository , i just crawled projects of **java in linux**

Here is the url https://sourceforge.net/directory/language:java/os:linux/


## To use this program,please follow steps below:

###    1 if you want to crawl other categories :
        
        change the url in config.py

        change the url in spider.py line 44
        
###     2 please control the number of projects that in your category :
        
        if the number of projects that in your category is too large,
        
        this code will turn into error,too :)

        advice:no more than 25000 in English category
        
###      3 remember too change the dir_name in your PC :
        
        in config.py line3
        
###      4 run spider.py in pycharm or other IDE 

## Information you can crawl (for now):

        name
        summary
        user-ratings :  average rating
                        number of stars(1 star  ... and 5 stars)
                        dimensional_ratings
        Categories(may be none)
        License(may be none)
        user_reviews (may be none) :  
                      for each user: user_name
                                     number of stars
                                     review
                                     number of people thinking it useful(may be none)
