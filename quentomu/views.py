from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from .models import *
from apis.gph_api_tests import Chikka_Api as chk,hasher as hs
import requests as rq
from django.core.mail import send_mail
import types

global content
content = ''
def home(request):
	if request.user.is_anonymous():
		return render(request, 'index.html')
	else:
		topics = Topic.objects.all()
		messages = Message.objects.all()

		return render(request, 'home.html',
			{"topics": topics, "messages": messages.__dict__}
		)

def Remittance(request):
	pass
def DeliveryNotif(request,number,msg):
	hashed =hs.hashme(number)
	r = chk.sendMessage(msg,number,'SEND', hashed )
	global content 
	content = "I sent a message "+ r.text + " "+ str(r.status_code)
	send_mail('Sent message by '+str(hashed), content, 'pagong@quentomu.herokuapp.com',
	['pjinxed.aranzaellej@gmail	.com'], fail_silently=False)
	r = chk.chkDeliveryOf()
	content = "I confirmed the sent message by "+ str(hashed),+ r.text + " "+ str(r.status_code)
	send_mail('Confirm msg sent by' +str(hashed), content, 'pagong@quentomu.herokuapp.com',
	['pjinxed.aranzaellej@gmail.com'], fail_silently=False)
	return render(request, 'home.html',
			{"topics": topics, "messages": messages.__dict__}
		)
def ReceivedMsgs(request):
	r = chk.rcvMessage()
	global content
	content = "Message Recieved by "+ str(hashed),+ r.text + " "+ str(r.status_code)
	send_mail('inbox by' +str(hashed), content, 'pagong@quentomu.herokuapp.com',
	['pjinxed.aranzaellej@gmail.com'], fail_silently=False)
	
def conversation(request):
	if request.method == 'POST':

		print(request.body)

		print (User.objects.get(id=request.body['friend_id']))

		Message(
			sender=request.user,
			receiver=User.objects.get(id=request.body['friend_id'])[0],
			content=request.body['reply']
		).save()

		return JsonResponse({"successful": True})
	else:
		messages = Message.objects.filter(
			Q(sender=request.user) |
			Q(receiver=request.user)
		)

		people_conversed_with = set([
			message.contact_number
				if message.contact_number is not ''
			else message.sender
				if message.sender is not ''
					and message.sender != request.user
			else message.receiver
		for message in messages])

		conversations = [
			{
				'friend': friend if type(friend) is str
					else {"id": friend.id, "username": friend.username},
				'messages': [
					{
						"you": message.sender == request.user,
						"content": message.content
					}
					for message in messages
					if message.sender == friend or message.receiver == friend
					or message.contact_number == friend
				]
			}
			for friend in people_conversed_with
		]

		return JsonResponse(conversations, safe=False);

def topics(request):
	topics = [{
		"id": topic.id,
		"title": topic.title,
		"body": topic.body,
		"posts_count": topic.post_set.count()
	} for topic in Topic.objects.all()]

	return JsonResponse(topics, safe=False);

def topics_create(request, id):
	if request.method == 'POST':
		topic = Topic.objects.get(id=id)

		Post(
			title=request.POST['post'],
			author=request.user,
			parent=None,
			topic=topic
		).save()

		return redirect("/topics/%d"%topic.id)
	else:
		topic = Topic.objects.get(id=id)
		return render(request, 'topics/create.html', {"topic": topic})


def get_replies(post):
	replies = post.post_set.all()

	for reply in replies:
		reply.replies = get_replies(reply)

	return replies

def topics_show(request, id):
	topic = Topic.objects.get(id=id)
	original_posts = topic.post_set.filter(parent=None)

	for post in original_posts:
		post.replies = get_replies(post)

	return render(request, 'topics/show.html', {
		"topic": topic,
		"original_posts": original_posts,
	})

def get_original_post(post):
	if post.parent == None:
		return post
	else:
		return get_original_post(post.parent)

def topics_reply(request, id):
	if request.method == 'POST':
		post = Post.objects.get(id=id)

		Post(
			title=request.POST['reply'],
			author=request.user,
			parent=post,
			topic=post.topic
		).save()

		return redirect("/topics/%d"%post.topic.id)
	else:
		post = Post.objects.get(id=id)

		return render(request, 'topics/reply.html', {"post": post})
