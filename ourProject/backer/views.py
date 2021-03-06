from django.http import HttpResponse, JsonResponse
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt
import json
import random
import re
import os
from .service import reptiles
from . import zhenzismsclient as smsclient

from .models import *

from backer.algorithm.CNN import test as classifyAlgorithm
from backer.algorithm.knn import knn as knnAlgorithm
from backer.algorithm.bp import test as bpAlgorithm
from backer.algorithm.HOG_SVM import hog_svm as svmAlgorithm

def DataTest(request):
    print("===========")
    return HttpResponse(['后台列表数据1', '后台列表数据2'])


num = ''


def code(n=6, alpha=True):
    s = ''  # 创建字符串变量,存储生成的验证码
    for i in range(n):  # 通过for循环控制验证码位数
        num = random.randint(0, 9)  # 生成随机数字0-9
        if alpha:  # 需要字母验证码,不用传参,如果不需要字母的,关键字alpha=False
            upper_alpha = chr(random.randint(65, 90))
            lower_alpha = chr(random.randint(97, 122))
            num = random.choice([num, upper_alpha, lower_alpha])
        s = s + str(num)
    return s


@csrf_exempt
def sendmessage(request):
    data = {}
    username = json.load(request).get('username')

    ret = re.match(r"^1[35678]\d{9}$", username)
    if ret is None:
        data['errno'] = 405
        data['msg'] = '请输入正确的手机号'
        return JsonResponse(data)

    client = smsclient.ZhenziSmsClient("https://sms_developer.zhenzikj.com", "102561",
                                       "3d8791f5-8cfa-4468-b9e7-13cb5b3f0ef8")
    global num
    num = str(code(6, False))
    client.send(username, '您的验证码为：' + num)
    data['errno'] = 200
    data['msg'] = '发送成功'
    return JsonResponse(data)


@csrf_exempt
def login(request):
    # request是WSGIRequest类型
    form = json.load(request)
    form = form.get('form')
    data = {}
    # 如果数据库没有，则user为None
    user = User.objects.filter(username=form.get('username'), password=form.get('password')).first()
    print(user)
    if (user is not None):
        data['errno'] = 200
        data['msg'] = '登录成功'
        data['role'] = user.type
    else:
        data['errno'] = 405
        data['msg'] = '账号或密码错误'

    return JsonResponse(data)


@csrf_exempt
def register(request):
    form = json.load(request)
    form = form.get('form')
    data = {}

    if (form.get('role') == ''):
        data['errno'] = 405
        data['msg'] = '请选择角色'
        return JsonResponse(data)

    if (form.get('verification') == ''):
        data['errno'] = 405
        data['msg'] = '请输入验证码'
        return JsonResponse(data)

    # 如果数据库没有，则user为None
    user = User.objects.filter(username=form.get('username')).first()
    if (user is not None):
        data['errno'] = 405
        data['msg'] = '用户名或手机号已经注册'
        return JsonResponse(data)

    global num
    if (num != form.get('verification')):
        data['errno'] = 405
        data['msg'] = '验证码错误'
        return JsonResponse(data)
    # 验证码置空
    num = ''

    user = User()
    user.username = form.get('username')
    user.password = form.get('password')
    user.type = form.get('role')
    user.save()

    data['errno'] = 200
    data['msg'] = '注册成功'
    return JsonResponse(data)


# 增
def insertPerson(request):
    # 创建一个对象
    person = Person()
    # 设置属性
    person.p_name = "王" + str(random.randint(1, 100))
    person.p_age = random.randint(1, 100)
    person.p_sex = random.randint(0, 1)
    # 保存数据
    person.save()
    return HttpResponse("插入成功")


# 删
def delPerson(request):
    id = 2
    person = Person.objects.filter(id=id)  # 用变量person接收获取到的对象
    person.delete()
    return HttpResponse("删除成功")


# 改
def updatePerson(request):
    id = 1
    person = Person.objects.filter(id=id).first()
    person.p_name = "王小明"
    person.p_age = 18
    person.p_sex = 0
    person.save()
    return HttpResponse("修改成功")


# 查
def listPerson(request):
    persons = Person.objects.all()
    for item in persons:
        print(item.id)

    # 可以使用JsonResponse返回json数据到前端
    return HttpResponse("查询成功")


# 爬虫
@csrf_exempt
def reptile(request):
    result = []
    date = json.load(request)
    print(date)
    url_value = int(date.get('url_value'))
    word = date.get('word')
    time_value = date.get('time_value')
    reptiles.run(url_value, word, time_value)
    data = {}

    print(data)
    return JsonResponse(data)


# 获取图片
@csrf_exempt
def get_img(request):
    images = Image.objects.all()
    re.findall(r'\d+', str(images[len(images) - 1].path))
    img_local = []
    for item in images:
        img_local.append(item.path)
    # data = json.loads(img_local)
    length = len(img_local)
    img_local = img_local[length - 8: length]
    data = {"img_local": img_local}
    return JsonResponse(data)
    pass


# 数据标注
# 前端获取数据库图片地址
@csrf_exempt
def getDataUrl(request):
    imgUrls = []
    img = Image.objects.all().filter(isTrue=False)
    img1 = random.sample(list(img), 8)
    print(img1)
    count = 0
    for x in img1:
        count += 1
        imgUrls.append({"img": x.path, "isTrue": x.isTrue, "id": x.id})
    data = {"img": imgUrls}
    return JsonResponse(data)


# 数据标注
# 修改数据库标记值
@csrf_exempt
def saveTransData(request):
    data = json.load(request)
    resultDict = data.get("result")
    try:
        for x in resultDict:
            img = Image.objects.filter(id=x.get('id')).first()
            img.isTrue = x.get('isTrue')
            img.save()
    except Exception as e:
        print(e)
    return HttpResponse("test")

#图片分类
@csrf_exempt
def classifyPhoto(request):
    data = json.load(request)
    imgname = data.get("imageUrl")
    classifyAlgorithm.photo_name = imgname
    classifyAlgorithm.classify_main_method()
    classifyResult = classifyAlgorithm.classify_result
    classifyAlgorithm.photo_name = ''
    result = {"result": classifyResult}
    return JsonResponse(result)
#算法展示

@csrf_exempt
def cnnTest(request):
    classifyAlgorithm.cnnTest()
    acc = classifyAlgorithm.acc
    runtime = classifyAlgorithm.runtime
    print(str(classifyAlgorithm.acc) + '___------------======______' + str(classifyAlgorithm.runtime))
    result = {"acc": acc, "runtime": runtime}
    return JsonResponse(result)

@csrf_exempt
def knnTest(request):
    print("------------------------")
    print("------------------------2222222222222222222222")
    knnAlgorithm.knnTest()
    acc = knnAlgorithm.acc
    runtime = knnAlgorithm.runtime
    result = {"acc": acc, "runtime": runtime}
    return JsonResponse(result)

@csrf_exempt
def bpTest(request):
    print("------------------------")
    print("------------------------3333333333333")
    bpAlgorithm.bpTest()
    acc = bpAlgorithm.acc
    runtime = bpAlgorithm.runtime
    result = {"acc": acc, "runtime": runtime}
    return JsonResponse(result)

@csrf_exempt
def svmTest(request):
    print("------------------------")
    svmAlgorithm.svmTest()
    print("------------------------3333333333333")

    acc = svmAlgorithm.acc
    runtime = svmAlgorithm.runtime
    result = {"acc": acc, "runtime": runtime}
    return JsonResponse(result)


# 作为测试
@csrf_exempt
def test(request):
    json_data = json.load(request)
    time_list = json_data.get('time_value')
    print(time_list[0])
    print(datetime.strptime(str(time_list[0]), "%Y-%m-%d"))
    return JsonResponse({})
