from django.shortcuts import render, redirect
from .models import Article, Contribution, Change
from .forms import ArticleForm, ContributeArticleForm 
import difflib
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def articles_list(request):
	articles = Article.objects.all()

	query = request.GET.get("q")
	if query:
		articles = articles.filter(title__icontains=query)

	paginator = Paginator(articles, 3) # Show 3 articles per page
	page_number = request.GET.get('page')

	try:
		articles = paginator.page(page_number)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		articles = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		articles = paginator.page(paginator.num_pages)

	context = {
		"articles" : articles,
	}
	return render(request, "articles_list.html", context)

def article_details(request, article_slug):
	context = { 
		"article" : Article.objects.get(slug=article_slug)
	}
	return render(request, "article_details.html", context)

def create_article(request):
	if request.user.is_anonymous:
		return redirect("auth:signin")

	form = ArticleForm()
	if request.method == "POST":
		form = ArticleForm(request.POST)
		if form.is_valid():
			article = form.save(commit=False)
			article.author = request.user
			article.save()
			return redirect('main:article-details', article.id)

	context = {
		"form" : form
	}
	return render(request, "create_article.html", context)

def edit_article(request, article_slug):
	article = Article.objects.get(slug=article_slug)

	if article.author != request.user:
		return redirect('main:article-details', article_slug)

	form = ArticleForm(instance=article)
	if request.method == "POST":
		form = ArticleForm(request.POST, instance=article)

		if form.is_valid():
			form.save()
			return redirect('main:article-details', article_slug)

	context = {
		"form" : form,              
		"article" : article
	}
	return render(request, 'edit_article.html', context)

def my_articles_list(request):
	return render(request, "my_articles_list.html")

def contribute_to_article(request, article_slug):
	if request.user.is_anonymous:
		return redirect('auth:signin')
		
	article = Article.objects.get(slug=article_slug)
	
	if article.author == request.user:
		return redirect('main:edit-article', article_slug)

	form = ContributeArticleForm(instance=article)
	if request.method == "POST":
		form = ContributeArticleForm(request.POST)

		if form.is_valid():
			changed_article = form.save(commit=False)
			contribution = Contribution.objects.create(user=request.user, article=article)
			Change.objects.create(new_content=changed_article.content, contribution=contribution)
			return redirect('main:my-contributions-list')

	context = {
		"form" : form, 
		"article":article
	}
	return render(request, 'contribute_to_article.html', context)

def my_contributions_list(request):
	if request.user.is_anonymous:
		return redirect('auth:signin')

	return render(request, "my_contributions_list.html")

def contributions_list(request):
	if request.user.is_anonymous:
		return redirect('main:articles-list')

	contributions = Contribution.objects.filter(status=Contribution.PENDING, article__author=request.user)
	context = {
		"contributions" : contributions
	}
	return render(request, 'contributions_list.html', context)

def contribution_details(request, contribution_id):
	contribution = Contribution.objects.get(id=contribution_id)
	if request.user != contribution.article.author:
		return redirect('main:articles-list')

	d = difflib.Differ()
	comparison = list(d.compare(contribution.article.content.splitlines(True), contribution.change.new_content.splitlines(True)))


	context = {
		"contribution" : contribution,
		"comparison" : comparison,
	}
	
	return render(request, 'contribution_details.html', context)

def accept_changes(request, contribution_id):
	contribution = Contribution.objects.get(id=contribution_id)

	if request.user != contribution.article.author:
		return redirect('main:articles-list')

	
	contribution.status = Contribution.ACCEPTED
	contribution.save()

	article = contribution.article
	article.content = contribution.change.new_content
	article.save()

	contribution.change.delete()

	return redirect('main:contributions-list')

def decline_changes(request, contribution_id):
	contribution = Contribution.objects.get(id=contribution_id)

	if request.user != contribution.article.author :
		return redirect('main:articles-list')

	contribution.status = Contribution.DECLINED
	contribution.save()

	contribution.change.delete()

	return redirect('main:contributions-list')

