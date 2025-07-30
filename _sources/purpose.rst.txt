Purpose
=======

A Publisher-Subscriber simulation game between film **directors** and **composers**, using pdm and pydantic:

- a movie database is built by querying the `TMDb API <https://developer.themoviedb.org/docs/getting-started>`_, retrieving details from each movie (title, director, composer, cast, year).
- then movie announcements are randomly published: a director (publisher) tells that he is working on a movie from the database and looking for a composer.
- all composers (subscribers) from the database subscribe to these announcements, and wait for a movie in which they are credited.
- if that is the case, they take the assignment.
- the winner is the 1st composer to secure a given number of contracts.
