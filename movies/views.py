# Author: anishreddyravula@gmail.com


from django.shortcuts import render
import requests
import json
from random import randint
from collections import OrderedDict
from django.http import JsonResponse
from movies.models import *
import random
"""
Functions for each operation
"""

#to get random the popular list
def popular(page):
		url = "http://api.themoviedb.org/3/movie/popular?page="+str(page)+"&language=en-US&api_key=32b8e2401c6259d29d1bb91c8d1b5e1c"
		image_url = "http://image.tmdb.org/t/p/w300"
		payload = "{}"
		response = requests.request("GET", url, data=payload)
		js = json.loads(response.text)
		return js, image_url

#to get any 5 random watched movies from the database
def get_random_five_movies():
	rand_count = Watched.objects.all().count()
	slice_n = randint(0, rand_count-4)
	rand_movies_objects = Watched.objects.all()[slice_n: slice_n+5]
	return rand_movies_objects

#to get recomendation for each watched movie
def recomendations(rand_movies_object):
		url = "https://api.themoviedb.org/3/movie/"+str(rand_movies_object.movie_id)+"/recommendations?api_key=32b8e2401c6259d29d1bb91c8d1b5e1c&language=en-US&page=1"
		image_url = "http://image.tmdb.org/t/p/w300"
		payload = "{}"
		response = requests.request("GET", url, data=payload)
		js = json.loads(response.text)
		try:
			if len(js["results"]) < 0:
				return None, None
			else:
				rand_recom = randint(0,len(js["results"]) - 2)
				return js["results"][rand_recom : rand_recom + 2], image_url
		except IndexError:
			return None, None

#To generate, random movies, recomended movies
def index(request):
	movie = []
	count = 0
	html = ''
	num = Watched.objects.all().count()

	#generate recommended movies only when watched movies are greater than 5
	if num > 5:
		rand_movies_objects =  get_random_five_movies()
		for rand_movies_object in rand_movies_objects:

			#call the fucntion to get recomenneded movies from each watched movie
			recommended_movies, image_url1 = recomendations(rand_movies_object)
			if recommended_movies is None:
				break

			#parse through every recomended movie and html generate a card for each movie
			for recommended_movie in recommended_movies:
				watch = Watched.objects.filter(movie_id = recommended_movie["id"])
				if watch.count() > 0 or recommended_movies.count(recommended_movie) > 1:
					continue
				html = html + "<div class=\"column\" id=\""+str(recommended_movie["id"])+"\">\
					<div class=\"ui special fluid card\">\
					<div class=\"card\">\
					<div class=\"blurring dimmable image\">\
					<div class=\"ui dimmer\">\
					<!--  <div class=\"circular right ui icon button \">\
					<i class=\"icon settings\">\
					</i>\
					</div>\
					-->\
					<div class=\"content\">\
					<div class=\"center\">\
					<div class=\"ui tiny buttons\">\
					<button  name =\"watched\" value=\""+str(recommended_movie["id"])+"\" class=\"ui button\">\
					Watched</button>\
					<button  class=\"ui button\" name =\"not_watched\" value=\""+str(recommended_movie["id"])+"\">\
					Not Watched</button>\
					</div>\
					<!-- <div class=\"ui inverted button positive\">\
					Watched               </div>\
					-->\
					</div>\
					</div>\
					</div>\
					<img src=\""+image_url1+str(recommended_movie["poster_path"])+"\" alt=\"Slide 1\" %} alt=\"Movie 3\" %}>\
					</div>\
					<div class=\"content\">\
					<a class=\"header\">\
					"+str(recommended_movie["title"])+"</a>\
					<div class=\"meta\">\
					<span class=\"date\">\
					"+str(recommended_movie["release_date"])+"</span>\
					</div>\
					Popularity: <div class=\"ui heart rating\" data-rating=\""+str(int(recommended_movie["vote_average"]/2))+"\" data-max-rating=\"5\"></div>\
					</div>\
					<div class=\"extra content\">\
					<div class=\"ui star rating\" data-rating=\"0\">\
					</div>\
					</div>\
					</div>\
					</div>\
					</div>\
					"
		count = 0
		movie = []

	"""
	To generate random movies
	"""
	page = randint(0,300)

	#get the popular images list
	js, image_url = popular(page)

	for movies in js['results']:
		if movies['poster_path'] is None:
			continue
		movie.append(OrderedDict())
		watch = Watched.objects.filter(movie_id = movies['id'])
		not_watch = Not_Watched.objects.filter(movie_id = movies['id'])
		if watch.count() > 0 and not_watch.count() > 0:
			break
		if movies['poster_path'] is not None :
			movie[count]['image_path'] = image_url + movies['poster_path'] 
			movie[count]['title'] = movies['title']
			movie[count]['release_date'] = movies['release_date']
			movie[count]['id'] = movies['id']
			movie[count]['popularity'] = int(movies['vote_average']/2)
			count = count + 1
		else:
			continue
	"""
	movies list contains a dictionary with random movies details
	"""

	#if number of movies from the result is less than 8 movies append additional movies to movie list
	if len(movie) < 8:
		js, image_url = popular(page)
		count = 0
		for movies in js['results']:
			if movies['poster_path'] is None:
				continue
			movie.append(OrderedDict())
			watch = Watched.objects.filter(movie_id = movies['id'])
			if watch.count() > 0:
				break
			movie[count]['image_path'] = image_url+movies['poster_path']
			movie[count]['title'] = movies['title']
			movie[count]['release_date'] = movies['release_date']
			movie[count]['id'] = movies['id']
			count = count + 1

	#pass arguments to template
	args = {"movies":movie, "recommended" :html}
	return render(request, 'movies/index.html', args)

#to get the searched movie details
def search_movie(name):
	url = "https://api.themoviedb.org/3/search/movie?api_key=32b8e2401c6259d29d1bb91c8d1b5e1c&language=en-US&query="+name+"&page=1&include_adult=false"
	# print(url)
	image_url = "http://image.tmdb.org/t/p/w300"
	payload = "{}"
	response = requests.request("GET", url, data=payload)
	js = json.loads(response.text)
	return js, image_url

#to handle ajax requests from client
def submit_request(request):

	#to this when search is requested
	if "search" in request.POST:
		html = ''
		js, image_url = search_movie(request.POST['formDetails'])
		movie = {}
		for movies in js['results']:
			if movies['poster_path'] is None:
				continue
			else:
				movie['id'] = str(movies['id'] )
				movie['image_path'] = str(image_url+movies['poster_path'])
				movie['title'] = str(movies['title'])
				movie['release_date'] = str(movies['release_date'])
				movie['vote_average'] = str(movies['vote_average'])
				print(type(movie["vote_average"]))
				html = html +"<div class=\"column\" id=\""+str(movies["id"])+"\">\
					<div class=\"ui special fluid card\">\
					<div class=\"card\">\
					<div class=\"blurring dimmable image\">\
					<div class=\"ui dimmer\">\
					<!--  <div class=\"circular right ui icon button \">\
					<i class=\"icon settings\">\
					</i>\
					</div>\
					-->\
					<div class=\"content\">\
					<div class=\"center\">\
					<div class=\"ui tiny buttons\">\
					<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\""+request.POST['csrfmiddlewaretoken']+"\">\
					<button  name =\"watched\" value=\""+str(movies["id"])+"\" class=\"ui button\">\
					Watched</button>\
					<button  class=\"ui button\" name =\"not_watched\" value=\""+movies["id"]+"\">\
					Not Watched</button>\
					</div>\
					<!-- <div class=\"ui inverted button positive\">\
					Watched               </div>\
					-->\
					</div>\
					</div>\
					</div>\
					<img src=\""+movie["image_path"]+"\" alt=\"Slide 1\" %} alt=\"Movie 3\" %}>\
					</div>\
					<div class=\"content\">\
					<a class=\"header\">\
					"+movies["title"]+"</a>\
					<div class=\"meta\">\
					<span class=\"date\">\
					"+str(movies["release_date"])+"</span>\
					</div>\
					Popularity: <div class=\"ui heart rating\" data-rating=\""+movie['vote_average']+"\" data-max-rating=\"5\"></div>\
					</div>\
					<div class=\"extra content\">\
					<div class=\"ui star rating\" data-rating=\"0\">\
					</div>\
					</div>\
					</div>\
					</div>\
					</div>\
					"
		data = {"updated" : "updated", 'result' : html}
		#respond with searched movies html as cards
		return JsonResponse(data)

	#to handle a watched or not watched request from user
	else:
		if "watched" == request.POST['status']:
			watch = Watched(movie_id = request.POST['id'])
			watch.save()
		if "not_watched" == request.POST['status']:
			watch = Not_Watched(movie_id = request.POST['id'])
			watch.save()

		page = randint(0,300)
		js, image_url = popular(page)
		movie = {}

		for movies in js['results']:
			if movies['poster_path'] is None:
				continue
			else:
				movie['id'] = str(movies['id'] )
				movie['image_path'] = str(image_url+movies['poster_path'])
				movie['title'] = str(movies['title'])
				movie['release_date'] = str(movies['release_date'])
				break
		html = "<div class=\"column\" id=\""+str(movies["id"])+"\">\
			<div class=\"ui special fluid card\">\
			<div class=\"card\">\
			<div class=\"blurring dimmable image\">\
			<div class=\"ui dimmer\">\
			<!--  <div class=\"circular right ui icon button \">\
			<i class=\"icon settings\">\
			</i>\
			</div>\
			-->\
			<div class=\"content\">\
			<div class=\"center\">\
			<div class=\"ui tiny buttons\">\
			<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\""+request.POST['csrfmiddlewaretoken']+"\">\
			<button  name =\"watched\" value=\""+str(movies["id"])+"\" class=\"ui button\">\
			Watched</button>\
			<button  class=\"ui button\" name =\"not_watched\" value=\""+str(movies["id"])+"\">\
			Not Watched</button>\
			</div>\
			<!-- <div class=\"ui inverted button positive\">\
			Watched               </div>\
			-->\
			</div>\
			</div>\
			</div>\
			<img src=\""+movie["image_path"]+"\" alt=\"Slide 1\" %} alt=\"Movie 3\" %}>\
			</div>\
			<div class=\"content\">\
			<a class=\"header\">\
			"+movies["title"]+"</a>\
			<div class=\"meta\">\
			<span class=\"date\">\
			"+str(movies["release_date"])+"</span>\
			</div>\
			</div>\
			<div class=\"extra content\">\
			<div class=\"ui star rating\" data-rating=\"0\">\
			</div>\
			</div>\
			</div>\
			</div>\
			</div>\
			"
		data = {'updated' : "updated",'html' : html }
		return JsonResponse(data)
