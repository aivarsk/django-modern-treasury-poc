# django-debitcredit
DebitCredit with Django ORM


```
root@1fe9bdd54e32:/app# python3 manage.py shell
Python 3.12.4 (main, Aug  2 2024, 14:41:31) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from debitcredit.models import *
>>> a1 = Account.objects.create(balance=100)
>>> a2 = Account.objects.create(balance=100)
>>> run(a1, a2, 1000)
2000 transfers in 8.460346221923828 seconds and 236.39694494029973 tps
>>>
```
