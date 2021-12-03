# evenTO Update

##### 2/12/2021
Added:
*EventOwner model
*User model
*Follower model
*Registration model
*Role model --> Admin,User,EventOwner,Moderator [STILL NEED TO IMPLEMENT]
*Post an event section still not working (Not Posting)
*form.py fixed
*edit event page ready I guess?
*pagination to the event page

But without posting, nothing really matters. We need to post 




##### 1/12/2021

Categories model added and I have added 4 categories to the database. When a user want to post an event they have to choose from the given types.



##### 29/11/2021
model.py update








##### 28/11/2021
###### BIG CHANGES
I changed the whole file structure. Now, everything is inside `website`.
To get everything working well, left click to the website and from "mark directory as" pick sources root. For the `templates` folder inside do pick "templates folder".

* Register and Login Works Fine.
* Errors appear if something is wrong.
* Post an event appears if we are logged in
* Error message appears but breadcrumbs disappear  
* run.py is used for running (ofkors)
* routes.py are for routes
* models.py for classes
* form.py for register & login
* __init__.py contains all the initializations
