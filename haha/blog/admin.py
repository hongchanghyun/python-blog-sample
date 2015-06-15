from django.contrib import admin

# Register your models here.
from .models import Entries
from .models import TagModel
from .models import Categories

class EntriesAdmin(admin.ModelAdmin):
    def tag_title(self, obj):
        return self.tag_title(obj)
    
    list_display = ('id','Title','created','tag_title',)

class TagModelAdmin(admin.ModelAdmin):
    list_display = ('id','Title',)    
    
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id','Title',)
        
admin.site.register(Entries, EntriesAdmin)
admin.site.register(TagModel, TagModelAdmin)
admin.site.register(Categories, CategoriesAdmin)

