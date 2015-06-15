#-*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from blog.models import Entries, Categories, TagModel, Comments
import md5

def index(request, page=1):
    page = int(page)
    per_page = 5
    start_pos = (page-1) * per_page
    end_pos = start_pos + per_page
    count_pos = Entries.objects.count();
    last_page = (count_pos / per_page) + 1
    if count_pos % per_page > 0 :
        last_page += 1
    begin_page = ((page - 1) / per_page) * count_pos + 1
    entries = Entries.objects.all().order_by('-created')[start_pos:end_pos]
    tpl = loader.get_template('list.html')
    page_title = '블로그 목록 화면'
    ctx = Context({
                   'screen_title':page_title,
                   'entries':entries,
                   'current_page':page,
                   'range_page':range(begin_page, last_page),
                   })
    return HttpResponse(tpl.render(ctx))

def read(request, entry_id=None):
    page_title = 'blog read'
    current_entry = Entries.objects.get(id=int(entry_id))
    try:
        prev_entry = current_entry.get_previous_by_created()
    except:
        prev_entry = None    
    try:
        next_entry = current_entry.get_next_by_created()
    except:
        next_entry = None    

    try:
        current_entry = Entries.objects.get(id=int(entry_id))
        comments = Comments.objects.filter(Entry=current_entry).order_by('created')
    except:
        return HttpResponse('그런 글이 존재하지 않습니다.')

    tpl = loader.get_template('read.html')
    ctx = Context({
        'page_title':page_title,
        'current_entry':current_entry,
        'prev_entry':prev_entry,
        'next_entry':next_entry,
        'comments':comments,
    })
    return HttpResponse(tpl.render(ctx))

def write_form(request):
    page_title = '블로그 글 쓰기 화면'
    tpl = loader.get_template('write.html')
    categories = Categories.objects.all()
    ctx = Context({
        'page_title':page_title,
        'categories':categories
    })
    return HttpResponse(tpl.render(ctx))

@csrf_exempt
def add_post(request):
    # 제목 검증
    if request.POST.has_key('title') == False:
        return HttpResponse('글 제목을 입력해야 한다우.')
    else:
        if len(request.POST['title']) == 0:
            return HttpResponse('글 제목엔 적어도 한 글자는 넣자!')
        else:
            entry_title = request.POST['title']

    #본문 검증
    if request.POST.has_key('content') == False:
        return HttpResponse('글 본문을 입력해야 한다우.')
    else:
        if len(request.POST['content']) == 0:
            return HttpResponse('글 본문엔 적어도 한 글자는 넣자!')
        else:
            entry_content = request.POST['content']
    
    #카테고리 검증        
    try:
        entry_category = Categories.objects.get(id=request.POST['category'])
    except:
        return HttpResponse('이상한 글 갈래구려')
    
    #꼬리표 처리
    if request.POST.has_key('tags') == True:
        tags = map(lambda str: str.strip(), unicode(request.POST['tags']).split(','))
        tag_list = map(lambda tag: TagModel.objects.get_or_create(Title=tag)[0], tags)
    else:
        tag_list = []
    
    #꼬리표 저장을 위한 저장
    new_entry = Entries(Title=entry_title, Content=entry_content, Category=entry_category)
    try:
        new_entry.save()
    except:
        return HttpResponse('글을 써넣다가 오류가 발생했습니다.')
    
    #꼬리표 추가
    for tag in tag_list:
        new_entry.Tags.add(tag)
    
    #최종 저장
    if len(tag_list) > 0:
        try:
            new_entry.save()
        except:
            return HttpResponse('글을 써넣다가 오류가 발생했습니다.')
    
    return HttpResponse('%s번 글을 제대로 써넣었습니다.' % new_entry.id)

@csrf_exempt
def update_post(request):
    # 제목 검증
    if request.POST.has_key('title') == False:
        return HttpResponse('글 제목을 입력해야 한다우.')
    else:
        if len(request.POST['title']) == 0:
            return HttpResponse('글 제목엔 적어도 한 글자는 넣자!')
        else:
            entry_title = request.POST['title']

    #본문 검증
    if request.POST.has_key('content') == False:
        return HttpResponse('글 본문을 입력해야 한다우.')
    else:
        if len(request.POST['content']) == 0:
            return HttpResponse('글 본문엔 적어도 한 글자는 넣자!')
        else:
            entry_content = request.POST['content']
    
    #카테고리 검증        
    try:
        entry_category = Categories.objects.get(id=request.POST['category'])
    except:
        return HttpResponse('이상한 글 갈래구려')
    
    #꼬리표 처리
    if request.POST.has_key('tags') == True:
        tags = map(lambda str: str.strip(), unicode(request.POST['tags']).split(','))
        tag_list = map(lambda tag: TagModel.objects.get_or_create(Title=tag)[0], tags)
    else:
        tag_list = []
    
    #꼬리표 저장을 위한 저장
    entry = Entries.objects.get(request.POST['id'])
    entry(Title=entry_title, Content=entry_content, Category=entry_category)
    
    try:
        entry.save()
    except:
        return HttpResponse('글을 써넣다가 오류가 발생했습니다.')
    
    #꼬리표 추가
    for tag in tag_list:
        entry.Tags.add(tag)
    
    #최종 저장
    if len(tag_list) > 0:
        try:
            entry.save()
        except:
            return HttpResponse('글을 써넣다가 오류가 발생했습니다.')
    
    return HttpResponse('%s번 글을 제대로 수정했습니다.' % entry.id)

def add_comment(request):
    # 글쓴이 이름 처리
    cmt_name = request.POST.get('name', '')
    if not cmt_name.strip() :
        return HttpResponse('글쓴이 이름을 입력해야 한다우.')
    
    # 비밀번호
    cmt_password = request.POST.get('password', '')
    if not cmt_password.strip() :
        return HttpResponse('비밀번호를 입력해야 한다우.')
    cmt_password = md5.md5(cmt_password).hexdigest()
    
    # 댓글 본문 처리
    cmt_content = request.POST.get('content', '')
    if not cmt_content.strip() :
        return HttpResponse('댓글 내용을 입력해야 한다우.')
    
    if request.POST.has_key('entry_id') == False:
        return HttpResponse('댓글 달 글을 지정해야 한다우.')
    else:
        try:
            entry = Entries.objects.get(id=request.POST['entry_id'])
        except:
            return HttpResponse('그런 글은 없지롱')
    
    try:
        new_cmt = Comments(Name=cmt_name, Password=cmt_password, Content=cmt_content, Entry=entry)
        entry.Comments = entry.Comments + 1
        new_cmt.save()
        return HttpResponse('댓글 잘 매달았다, 얼쑤.')
    except:
        return HttpResponse('제대로 저장하지 못했습니다.')
    
    return HttpResponse('문제가 생겨 저장하지 못했습니다.')

def del_comment(request):
    try:
        del_entry = Entries.objects.get(id=request.POST['comment_id'], Password=md5.md5(request.POST['password']).hexdigest())
        del_entry.delete()
        return HttpResponse('댓글 잘 삭제했다, 얼쑤.')
    except:
        return HttpResponse('제대로 삭제하지 못했습니다.')        