from django import forms
        
class QuestionForm(forms.Form):
    question = forms.CharField(label='Question',
                    widget=forms.Textarea(
                        attrs={
                            'class':'form-control',
                            'placeholder':'Type your question here.'   
                        }
                    )
                )
    
class AnswerForm(forms.Form):
    answer = forms.CharField(label='Answer',
                    widget=forms.Textarea(
                        attrs={
                            'class':'form-control',
                            'placeholder':'Type your answer here.'   
                        }
                    )
                )
