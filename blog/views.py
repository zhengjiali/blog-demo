from django.shortcuts import render,get_object_or_404,redirect
from .models import Post,Comment
from django.http import Http404,HttpResponseRedirect
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm
from django.core.mail import send_mail
from django.core.urlresolvers import reverse  
from django.db.models import Count

# Create your views here.

def post_share(request,post_id):
	#Retrieve post by id
	# post = get_object_or_404(Post,id=post_id)
	sent = False
	try:
		post = Post.objects.get(id=post_id)
	except:
		return Http404

	if request.method == 'POST':
		#Form was submitted
		form = EmailPostForm(request.POST)
		if form.is_valid():
			# Form fields passed validation
			cd = form.cleaned_data
			post_url = request.build_absolute_uri(
				post.get_absolute_url())
			subject = '{} ({}) recommends you reading "{}"' .format(cd['name'],cd['email'],post.title)
			message = 'Read "{}" at {} \n\n {}\'s comments:{}' .format(post.title,post_url,cd['name'],cd['comments'])
			send_mail(subject, message, 'zhengjiali2014@163.com', [cd['to']])
			sent = True
	else:
		form = EmailPostForm()
	return render(request, 'blog/post/share.html',{'post':post,'form':form,'sent':sent})

class PostListView(ListView):
	queryset = Post.published.all()
	context_object_name = 'posts'
	paginate_by = 10
	template_name = 'blog/post/list.html'

def post_list(request,tag_slug=None):
	object_list = Post.published.all()
	tag = None
	page = request.GET.get('page')
	if tag_slug:
		tag = Post.tags.get(slug=tag_slug)
		object_list = object_list.filter(tags__in=[tag])

	paginator = Paginator(object_list, 10) # 3 posts in each page

	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer deliver the first page
		posts = paginator.page(1)
	except EmptyPage:
		# If page is out of range deliver last page of results
		posts = paginator.page(paginator.num_pages)
	return render(request, 'blog/post/list.html',{'page':page,'posts':posts,'tag':tag})

def post_detail(request,year,month,day,post):
	try:
		post = Post.objects.get(slug=post)
		comments = post.comments.filter(active=True)
		new_comment = False

		if request.method == 'POST':
			# A comment was posted
			comment_form = CommentForm(data=request.POST)
			if comment_form.is_valid():
				# Create Comment object but don't save to database yet
				new_comment = comment_form.save(commit=False)
				# Assign the current post to the comment
				new_comment.post=post
				# Save the comment to the database
				new_comment.save()
			# return HttpResponseRedirect(reverse("blog:post_detail",kwargs={'post':post,'comments':comments,'form':comment_form,"new_comment":new_comment}))
		else:
			comment_form = CommentForm()
	except:
		# return Http404
		return render(request, 'blog/404.html')
	post_tags_ids = post.tags.values_list('id',flat=True)
	similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
	similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
	return render(request,'blog/post/detail.html',{'post':post,'comments':comments,'form':comment_form,'new_comment':new_comment,'similar_posts':similar_posts})




