from django.shortcuts import render
from pymongo import MongoClient
# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
import datetime
from random import randint
from sklearn import tree


def index(request):
    template = loader.get_template('EVCharge/index.html')
    
    return HttpResponse(template.render(request))

def ev(request, car_id):
    client = MongoClient('mongodb://ev_user:ee135@ds064188.mlab.com:64188/evdb')
    db = client['evdb']
    carCollection = db['car']

    result = carCollection.find_one({"carID": car_id})
    if result!=None:
        print(result)
    template = loader.get_template('EVCharge/EVs.html')
    context = {
        'car':result,
    }
    return HttpResponse(template.render(context, request))

def processing(request):
    print(request.GET.get('carid'))
    if request.GET.get('carid')!=None and request.GET.get('userid')!=None and request.GET.get('si')!=None and request.GET.get('ei')!=None and request.GET.get('ri')!=None and request.GET.get('durexp')!=None:
        print(request.POST.get('carid'))
        print(request.POST.get('userid'))
        print(request.POST.get('si'))
        print(request.POST.get('ei'))
        print(request.POST.get('ri'))
        print(request.POST.get('durexp'))
        dt = datetime.timedelta(hours = 8)
        endtime = datetime.datetime.now()-dt
        
        insertHistory(request.GET.get('carid'), request.GET.get('userid'), request.GET.get('si'), 
            endtime.strftime("%a %b %d %Y %H:%M:%S"), request.GET.get('ei'), request.GET.get('ri'), request.GET.get('durexp'))
        return HttpResponseRedirect("/EVCharge")

def charging(request, car_id, user_id, duration, distance):
    client = MongoClient('mongodb://ev_user:ee135@ds064188.mlab.com:64188/evdb')
    db = client['evdb']
    carCollection = db['car']
    historyCollection = db['history']
    
    my_car = carCollection.find_one({"carID": car_id})
    mpk = my_car['milePerKWh']
    X = []
    Y = []
    cur = historyCollection.find({"carID": car_id, "userID": user_id})
    for data in cur:
        starttime = str(data['si'])[0:24]
        endtime = str(data['ti'])[0:24]
        expect = float(data['duration_exp'])
        print starttime
        print endtime
        print expect
        stime = datetime.datetime.strptime(starttime, '%a %b %d %Y %H:%M:%S')
        etime = datetime.datetime.strptime(endtime, '%a %b %d %Y %H:%M:%S')
        ws = stime.isoweekday()
        ys = stime.year
        ms = stime.month
        ds = stime.day
        hs = stime.hour
        we = (etime-stime).days*24+(etime-stime).seconds/3600
        X.append([expect, ws, ys, ms, ds, hs])
        Y.append(we)
    if ((len(Y)>0)and(len(X)>0)):
        model = train_model(X,Y)
        curTime = datetime.datetime.now()
        pre_x = [duration, curTime.isoweekday(), curTime.year, curTime.month, curTime.day, curTime.hour]
        pre_y = model.predict(pre_x)
    else: 
        pre_y = duration
    # train_data = historyCollection.find({"carID": car_id, "userID": user_id})
    # print train_data

    context = {
        'car': my_car,
        'userID': user_id,
        'duration': duration,
        'distance': float(distance)/mpk,
        'prediction': str(pre_y),
    }
    template = loader.get_template('EVCharge/charging.html')
    return HttpResponse(template.render(context, request))
 
def regist(request):
    print(request.POST.get('fileName'))
    print(request.GET.get('fileName'))

    template = loader.get_template('EVCharge/regist.html')
    return HttpResponse(template.render(request))

def upload(request):
    f=request.FILES['fileSelect']
    filepath = '/static/'+request.POST.get('make')+'_'+request.POST.get('model')+'.jpg'
    with open('EVCharge'+filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print (request.POST.get('carID'))
    print (request.POST.get('make'))
    print (request.POST.get('model'))
    print (request.POST.get('imageLink'))
    print (request.POST.get('maxRate'))
    print (request.POST.get('milePerKWh'))
    if request.POST.get('carID')!=None and request.POST.get('make')!=None and request.POST.get('model')!=None and request.POST.get('maxRate')!=None and request.POST.get('milePerKWh')!=None:
        temp = insertCar(request.POST.get('carID'), request.POST.get('make'), request.POST.get('model'), request.POST.get('milePerKWh'), request.POST.get('maxRate'), filepath)
        print temp
    template = loader.get_template('EVCharge/index.html')
    return HttpResponseRedirect("/EVCharge")

# sample data format:
'''
carCollection = db['car']
{
    "_id": {
        "$oid": "56d7e4759d1fa2129ad78250"
    },
    "carID": "A000001",
    "make": "Tesla",
    "imageLink": "/static/Tesla-Model-X.jpg",
    "maxRate": 1.5,
    "model": "Model X",
    "milePerKWh": 3
}

historyCollection = db['history']
{
    "_id": {
        "$oid": "56dd3b759d1fa21095034429"
    },
    "carID": "A000003",
    "userID": "2017000",
    "si": "Mon Mar 07 2016 00:27:26 GMT-0800 (PST)",
    "ti": "Mon Mar 07 2016 00:27:33",
    "ei": "1",
    "duration_exp": "1",
    "ri": "1.5"
}

'''
def populate():
    client = MongoClient('mongodb://ev_user:ee135@ds064188.mlab.com:64188/evdb')
    db = client['evdb']
    carCollection = db['car']
    car1 = {'carID': 'A000001',
        'make': 'Tesla',
        'model': 'Model S',
        'milePerKWh': 3.00,
        'maxRate': 1.5,
        'imageLink': '/static/Tesla-Model-S1.jpg',
        }
    uoload_id = carCollection.insert_one(car1).inserted_id

def insertHistory(carid, userid, si, ti, ei, ri, duration_exp):
    client = MongoClient('mongodb://ev_user:ee135@ds064188.mlab.com:64188/evdb')
    db = client['evdb']
    carCollection = db['history']
    car1 = {'carID': carid,
        'userID': userid,
        'si': si,
        'ti': ti,
        'ei': ei,
        'ri': ri,
        'duration_exp': duration_exp,
        }
    upload_id = carCollection.insert_one(car1).inserted_id
    return upload_id

def insertCar(carid, make, model, mpk, maxrate, imageLink):
    client = MongoClient('mongodb://ev_user:ee135@ds064188.mlab.com:64188/evdb')
    db = client['evdb']
    carCollection = db['car']
    car1 = {
        'carID':carid,
        'make':make,
        'model':model,
        'imageLink':imageLink,
        'maxRate':maxrate,
        'milePerKWh':mpk,
    }
    upload_id = carCollection.insert_one(car1).inserted_id
    return upload_id

def train_model(X, Y):
    clf = tree.DecisionTreeRegressor(min_samples_leaf=5)
    clf = clf.fit(X,Y)
    return clf


def populate_history(carID='A000002', userID='2017496'):
    chargeHistory = []
    client = MongoClient('mongodb://ev_user:ee135@ds064188.mlab.com:64188/evdb')
    db = client['evdb']
    historyCollection = db['history']
    # generate data for Thursdays:
    ratio = 1.1
    st = datetime.datetime(2015,1,1)
    dt = datetime.timedelta(days=7)
    for i in range(50):
        dh = randint(-2,2)
        dm = randint(-35, 35)
        ds = randint(-59, 59)
        delta = datetime.timedelta(hours=dh) + datetime.timedelta(minutes=dm) + datetime.timedelta(seconds=ds)
        si = st + i*dt + delta # start time
        duration = randint(6,9) # expected end time
        ti = si + datetime.timedelta(hours=ratio*duration+0.3*randint(-1,1)) # real left time
        ei = 10 * duration + randint (-20, 20)# expected travel distance
        ri = 1.5
        ch1 = {'si': si, 'ti': ti, 'duration_exp': duration,
               'ei': ei, 'ri': ri,
        }
        chargeHistory.append(ch1)
    # Fridays
    st = datetime.datetime(2015,1,2)
    dt = datetime.timedelta(days=7)
    ratio = 0.9
    for i in range(50):
        dh = randint(-2,2)
        dm = randint(-35, 35)
        ds = randint(-59, 59)
        delta = datetime.timedelta(hours=dh) + datetime.timedelta(minutes=dm) + datetime.timedelta(seconds=ds)
        si = st + i*dt + delta # start time
        duration = randint(4,12) # expected end time
        ti = si + datetime.timedelta(hours=ratio*duration+0.3*randint(-1,0)) # real left time
        ei = 10 * duration + randint (-20, 20)# expected travel distance
        ri = 1.5
        ch1 = {'si': si, 'ti': ti, 'duration_exp': duration,
               'ei': ei, 'ri': ri,
        }
        chargeHistory.append(ch1)
    # Mondays
    st = datetime.datetime(2015,1,5)
    dt = datetime.timedelta(days=7)
    ratio = 1.2
    for i in range(50):
        dh = randint(0,2)
        dm = randint(-35, 35)
        ds = randint(-59, 59)
        delta = datetime.timedelta(hours=dh) + datetime.timedelta(minutes=dm) + datetime.timedelta(seconds=ds)
        si = st + i*dt + delta # start time
        duration = randint(7,10) # expected end time
        ti = si + datetime.timedelta(hours=ratio*duration+0.3*randint(-1,0)) # real left time
        ei = 10 * duration + randint (-20, 20)# expected travel distance
        ri = 1.5
        ch1 = {'si': si, 'ti': ti, 'duration_exp': duration,
               'ei': ei, 'ri': ri,
        }
        chargeHistory.append(ch1)
    # Tuesdays
    st = datetime.datetime(2015,1,6)
    dt = datetime.timedelta(days=7)
    ratio = 1.0
    for i in range(50):
        dh = randint(-1,1)
        dm = randint(-35, 35)
        ds = randint(-59, 59)
        delta = datetime.timedelta(hours=dh) + datetime.timedelta(minutes=dm) + datetime.timedelta(seconds=ds)
        si = st + i*dt + delta # start time
        duration = randint(6,8) # expected end time
        ti = si + datetime.timedelta(hours=ratio*duration+0.3*randint(-1,0)) # real left time
        ei = 10 * duration + randint (-20, 20)# expected travel distance
        ri = 1.5
        ch1 = {'si': si, 'ti': ti, 'duration_exp': duration,
               'ei': ei, 'ri': ri,
        }
        chargeHistory.append(ch1)
    # Wednesdays
    st = datetime.datetime(2015,1,7)
    dt = datetime.timedelta(days=7)
    ratio = 1.0
    for i in range(50):
        dh = randint(0,2)
        dm = randint(-35, 35)
        ds = randint(-59, 59)
        delta = datetime.timedelta(hours=dh) + datetime.timedelta(minutes=dm) + datetime.timedelta(seconds=ds)
        si = st + i*dt + delta # start time
        duration = randint(6,8) # expected end time
        ti = si + datetime.timedelta(hours=ratio*duration+0.3*randint(-1,0)) # real left time
        ei = 10 * duration + randint (-20, 20)# expected travel distance
        ri = 1.5
        ch1 = {'si': si, 'ti': ti, 'duration_exp': duration,
               'ei': ei, 'ri': ri,
        }
        chargeHistory.append(ch1)
    history1 = {'carID': carID, 'userID': userID, 
                'chargeHistory':chargeHistory,
    }
    upload_id = historyCollection.insert_one(history1).inserted_id
    
    