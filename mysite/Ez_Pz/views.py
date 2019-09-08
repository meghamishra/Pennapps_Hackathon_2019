from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .forms import SearchForm
from django.http import HttpResponseRedirect
import csv
import os
import pickle
import google.oauth2.credentials
from urllib.request import urlopen
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import json
import pandas as pd
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
API_KEY='AIzaSyAX138kTwRTIhhDRnECCW6ZFoMQM-iDPJ8'

final_list=[]

def get_authenticated_service():
	credentials = None
	flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
	credentials = flow.run_console()

	return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)


def get_video_comments(**kwargs):
	comments = []
	comment_likes_list=[]
	#results = service.commentThreads().list(**kwargs).execute()
	response1=urlopen("https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=50&videoId="+kwargs['videoId']+"&textFormat=plainText&alt=json&key="+API_KEY)
	results = json.load(response1)

	print("*****************COMMENTS RESULTS************************", results)
	print("*****************COMMENTS RESULTS DONE************************")
	print()
	print("*****************COMMENTS RESULTS['items']************************",results['items'])
	print("*****************COMMENTS RESULTS['items'] DONE************************")
	print()

	while results:
		for item in results['items']:
			comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
			comment_likes=item['snippet']['topLevelComment']['snippet']['likeCount']
			comments.append(comment)
			comment_likes_list.append(comment_likes)
		print("___________________________COMMENTS LIKES__________________________________________", comment_likes_list)

		# Check if another page exists
		if 'nextPageToken' in results:
			kwargs['pageToken'] = results['nextPageToken']
			results = service.commentThreads().list(**kwargs).execute()
		else:
			break
	print("$$$$$$$$$$$$$$$$$$$$$$$$Comments$$$$$$$$$$$$$$$$$$$$$$$$", comments, len(comments))
	print("$$$$$$$$$$$$$$$$$$$$$$$$CommentsLikes$$$$$$$$$$$$$$$$$$$$$$$$", comment_likes_list, len(comment_likes_list))
	return comments, comment_likes_list

	#return comments, comment_likes_list


def write_to_csv(keyword, comments):
	with open('comments.csv', 'w', encoding="utf-8") as comments_file:
		comments_writer = csv.writer(comments_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		comments_writer.writerow(['Video ID', 'Title', 'Comment', 'Comment_Likes'])
		for row in comments:
			# convert the tuple to a list and write to the output file
			try:

				comments_writer.writerow(list(row))
			except:
				pass
	

service = get_authenticated_service()
#search_videos_by_keyword(service, part='id,snippet', eventType='completed', type='video')

def index(request):
	# if this is a POST request we need to process the form data
	print("HELlOOOoooo")
	if request.method == 'POST':
		
		print("podst")
		# create a form instance and populate it with data from the request:
		form = SearchForm(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
			print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",form.cleaned_data['keyword'])
			keyword = form.cleaned_data['keyword']
			comments=[]
			comment_likes_list=[]
			#df=pd.read_csv("keyword_list.csv")
			#keyword_list=list(df['keyword_list'])
			final_results=[]
			#keyword=kwargs['q'].replace(" ","_")

			#keyword="knapsack algorithm"
			
			search_query="https://www.googleapis.com/youtube/v3/search?part=snippet&q="+keyword.replace(" ","+")+"&maxResults=20&order=viewCount&key="+API_KEY
			response_search = urlopen(search_query) #makes the call to a specific YouTube
			videos_inorder = json.load(response_search)

			print("***************************Videos_INOREDR***************",videos_inorder['items'])
			print("***************************Videos_INOREDR***************")

			#results = get_videos(service, **kwargs)
			title_list=[]
			video_id_list=[]
			viewCount_list=[]
			likeCount_list=[]
			dislikeCount_list=[]


			final_result = []
			for item in videos_inorder['items']:
				title = item['snippet']['title']
				title_list.append(title)
				try:
					video_id = item['id']['videoId']
					video_id_list.append(item['id']['videoId'])
				except:
					print("#$%^&*#$%^&#$%^&#$%^&$%^&EXCEPTION@#$%^&#$%^#$%^&$%^")
					continue

				print()
				print("video_id=",video_id)

				
				SpecificVideoID = video_id

				SpecificVideoUrl = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id='+SpecificVideoID+'&key='+API_KEY
				response = urlopen(SpecificVideoUrl) #makes the call to a specific YouTube
				videos = json.load(response) #decodes the response so we can work with it
				
				print("video_items=",videos['items'])

				print("===================done items================")

				for video in videos['items']: 
					if video['kind'] == 'youtube#video':
						try:
							print("VIEWS================================",video['statistics']['viewCount'])
							viewCount_list.append(video['statistics']['viewCount'])
						except:
							viewCount_list.append(-1)

						try:
							print("VIEWS================================",video['statistics']['likeCount'])
							likeCount_list.append(video['statistics']['likeCount'])
						except:
							likeCount_list.append(-1)

						try:
							print("VIEWS================================",video['statistics']['dislikeCount'])
							dislikeCount_list.append(video['statistics']['dislikeCount'])
						except:
							dislikeCount_list.append(-1)

				print("===============================",len(viewCount_list),len(likeCount_list),len(dislikeCount_list))



				try:
					comment, comment_likes = get_video_comments(part='snippet', videoId=video_id, textFormat='plainText')
					
					final_results.extend([(video_id, title, c, comment_likes[i]) for i,c in enumerate(comment)])
					
					
				except:
					print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@COMMENTS EXCEPTION-------------------=======================")
					pass
				# make a tuple consisting of the video id, title, comment and add the result to 
				# the final list
				#final_result.extend([(video_id, title, comment) for comment in comments]) 

			rows = zip(video_id_list,title_list,viewCount_list,likeCount_list,dislikeCount_list)
			with open("keyword.csv", "w", encoding="utf-8") as f:
				writer = csv.writer(f)
				for row in rows:
					writer.writerow(row)


			write_to_csv(keyword, final_results)

			os.system("python C:\\Users\\Commander\\Documents\\mysite\\Ez_Pz_Algorithm_final.py")


			f= open("output.txt","r")
			global final_list
			final_list=f.readlines()
			print(final_list)

			return HttpResponseRedirect('/output/')

	# if a GET (or any other method) we'll create a blank form
	else:
		form = SearchForm()

	return render(request, 'search.html', {'form': form})


def output(request):
	global final_list
	print("redtyuijrtfyguhjk")
	return render(request, 'videos.html', {'list_of_videos': final_list})