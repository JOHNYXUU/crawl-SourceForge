# Crawl-SourceForge

## Summary

This is a project for crawling information of projects on **SourceForge**.

In this repository, the crawled projects are **java in linux**.

Here is the url [https://sourceforge.net/directory/language:java/os:linux](https://sourceforge.net/directory/language:java/os:linux).

## Usage
To use this program, please follow the steps below:

1. If you want to crawl other categories, please change the URL in [config.py](./config.py) and change the URL in [spider.py](./spider.py) line 44.
        
2. Please control the number of projects that in your category - If the number of projects that in your category is too large, this code will run into error :( The recommended number is no more than 25000 categories.
        
3. Change the `dir_name` in your PC in config.py line3.
4. Run spider.py in pycharm or other IDE.

**Note**: Make sure the Internet in your country is good ('GOOD' means for browsing Sourceforge or you'll need the proxy to access it.
         
## Information you can crawl (for now):

````yml
name
summary
user-ratings:   average rating
                number of stars(1 star  ... and 5 stars)
                dimensional_ratings
Categories(may be none)
License(may be none)
user_reviews (may be none) :  
                for each user:  user_name
                                number of stars
                                review
                                the number of people thinking it useful (maybe none)
````
