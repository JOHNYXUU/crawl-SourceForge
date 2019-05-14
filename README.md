# crawl-SourceForge

This is a file for crawling information of projects on SourceForge.

for testing , i just crawled projects of java in linux 

here is the url https://sourceforge.net/directory/language:java/os:linux/

if you want to use this program,please read tips below:

1
        if you want to crawl other categories , just change the url in config.py

        However,please do not select any selections of translations,
        
        because i use it to classfiy those projects

        if you use selections of translations,this code will turn into error

2
        please control the number of projects that in your category
        
        if the number of projects that in your category is too large,
        
        this code will turn into error,too(:)sorry,i am a newbie for python)


3
        You can now crawl these information (for now):

                name

                summary

                user-ratings : average rating
                               number of stars(1 star  ... and 5 stars)
                               dimensional_ratings

                Categories(may be none)

                License(may be none)

                user_reviews (may be none) :  for each user: user_name
                                              number of stars
                                              review
                                              number of people thinking it useful(may be none)
