from django.contrib import admin

from .models import Comment, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
        'is_published'
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_editable = ('group', 'text', 'is_published',)


class PostComment(admin.ModelAdmin):

    list_display = (
        'pk',
        'post',
        'text',
        'created',
        'author',
    )
    search_fields = ('text',)
    list_filter = ('created',)
    list_editable = ('text',)
    empty_value_display = '-пусто-'


admin.site.register(Group)
admin.site.register(Comment, PostComment)
