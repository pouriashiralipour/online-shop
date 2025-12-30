import json

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Answer, Comment, ContactMessage, Question


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            "title",
            "text",
            "advantages",
            "disadvantages",
            "build_quality",
            "value_for_price",
            "innovation",
            "features",
            "ease_of_use",
            "design",
        ]
        widgets = {
            "text": forms.Textarea(
                attrs={"rows": 5, "placeholder": _("Please enter your review text.")}
            ),
            "build_quality": forms.NumberInput(attrs={"type": "hidden", "id": "ex19"}),
            "value_for_price": forms.NumberInput(
                attrs={"type": "hidden", "id": "ex20"}
            ),
            "innovation": forms.NumberInput(attrs={"type": "hidden", "id": "ex21"}),
            "features": forms.NumberInput(attrs={"type": "hidden", "id": "ex22"}),
            "ease_of_use": forms.NumberInput(attrs={"type": "hidden", "id": "ex23"}),
            "design": forms.NumberInput(attrs={"type": "hidden", "id": "ex24"}),
            "advantages": forms.HiddenInput(),
            "disadvantages": forms.HiddenInput(),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={"placeholder": _("Question text"), "rows": 3}
            ),
        }
        labels = {
            "text": _("Please enter your question."),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"placeholder": _("Answer Text"), "rows": 3}),
        }
        labels = {
            "text": _("Please enter your Answer."),
        }


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["subject", "full_name", "email", "phone", "message", "attachment"]
