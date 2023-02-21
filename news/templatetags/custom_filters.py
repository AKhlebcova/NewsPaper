from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

censor_words = {
    'дизайн',
    'валюта',
    'философия',
    'уникальность',
    'дом',
    'выставка',
}


@register.filter(is_safe=True)
@stringfilter
def censor(value):
    censor_obj = value.split()
    # print(censor_obj)
    obj_c = []
    for word in censor_obj:
        w = word.lower()
        w = filter(str.isalpha, w)
        w = ''.join(w)
        if w in censor_words:
            # print(w)
            if word[0].isalpha():
                word_c = word[0]
                for letter in word[1:len(word)]:
                    if letter.isalpha():
                        word_c += '*'
                    else:
                        word_c += letter
                word = word_c
            else:
                word_c = word[0:2]
                for letter in word[2:len(word)]:
                    if letter.isalpha():
                        word_c += '*'
                    else:
                        word_c += letter
                word = word_c
        obj_c.append(word)
    return ' '.join(obj_c)

# a = '"Валюта, дом.. дом,
# print(censor(a))
