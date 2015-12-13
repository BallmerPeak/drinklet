from django.forms import ModelForm
from user.models import RecipeComment

class RecipeCommentForm(ModelForm):
    class Meta:
        model = RecipeComment
        fields = ['comment_text']

    error = {'dup_comment':'Duplicate Post'}

    def clean(self):
        cleaned_data = super(RecipeCommentForm, self).clean()
        user = self.instance.user
        recipe = self.instance.recipe

        if recipe.recipecomment_set.filter(user = user).count():
            self.add_error('comment_text',self.error['dup_comment'])

        return cleaned_data




class EditRecipeCommentForm(RecipeCommentForm):
    def clean(self):
        cleaned_data = super(RecipeCommentForm, self).clean()

        return cleaned_data



