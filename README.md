#Final Project

###By Alexandra Qin

===

A GoogleAppEngine App that allows you to create/vote on items in categories

**Files:**

* Models/Handlers:
	* app.py
* Templates:
	* index.html
	* edit.html
	* new.html
	* results.html
	* vote.html
	* export.xml
* Stylesheets:
	* stylesheets/bootstrap.css
* Config:
	* app.yaml
	* index.yaml
	
**Models:**

* Category
	* author: String
	* name: String
	* date: DateTime
* Item
	* content: String (name of item)
	* category: Category
	* votes: int
	* losses: int
	* percent_win: int
	
A Category has many fields.

An Item has a Category.
	
**Controllers/Templates:**

* MainPage 
	* lists all the categories
	* renders index.html
	* gives the following options for each category listed:
	 	* Edit, Vote, Results, Delete, Export
* Create
	* creates a new Category
	* renders new.html
	* user either enters a new category name + item or imports a .xml file
	* redirects to MainPage when Category has been created
* Edit
	* edits a Category
	* renders edit.html
	* user can add items, remove items, or import a .xml file to add new items/replace items of the category
	* will throw an error if user tries to Edit a Category he/she has not authored
	* will throw an exception if imported category file has a different category name
* Delete
	* deletes an Item or a Category by its id
	* will throw an error if user tries to delete a category/item he/she has not authored
* Vote
	* votes on a Category Item
	* renders vote.html
	* any user can vote on any item
	* user is presented with 2 random items from the chosen category
	* user can vote or skip
	* shows win/losses of both items after the vote
	* Item.win_percent is recalculated at the end of each vote and saved
* AllResults
	* shows all results for all categories
	* renders results.html
* Results
	* shows results for the given category
	* renders results.html
	* shows item, wins, losses, percent win
* Export
	* exports a Category to a .xml file
	* renders export.xml
	
**Users:**

You must have a google account to Log in. You can create a category as an anonymous user, but you cannot edit it.

**Extra Features:**

* Users can delete items in a category. If a user imports a Category to an existing category, the duplicated items will be deleted and replaced with the new items of the same name.
* All category leaderboard
	 