from django.forms import ModelForm

from messagin_service.models import Recipient


class ClientForm(ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        # exclude = ('owner')

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
        })

        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control',
        })

        self.fields['comment'].widget.attrs.update({
            'class': 'form-control',
        })
