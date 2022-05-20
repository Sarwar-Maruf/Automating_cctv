from django.db import models

class Camera(models.Model):
    name = models.CharField(max_length=50)
    ip = models.CharField(max_length = 200)
    authority_no = models.CharField(max_length = 200, null= True, blank=True, default = "+8801710144505")
    authority_email = models.CharField(max_length = 200, null= True, blank=True, default = "sarwar15-8988@diu.edu.bd")

    def __str__(self):
        return self.name
class Filter(models.Model):
    filters = models.CharField(max_length= 100, null = False, blank = False)


    # def __str__(self):
    #     return self.name