
from locust import HttpLocust, TaskSet, task, between
import random, sys, json

prefix = 'uwsgi-http'
url = "http://localhost/" + prefix + "/quotes"

class UserBehaviour(TaskSet):
    @task(1)
    def getAQuote (self):
        quoteId = random.randint(1,900000)
        self.client.get(url + "/byId?id="+str(quoteId))

class WebsiteUser(HttpLocust):
    task_set = UserBehaviour
    wait_time = between(1, 3)

