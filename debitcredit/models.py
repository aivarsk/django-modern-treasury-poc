import time

from django.db import models, transaction
from django.db.models import Case, F, Q, When


class Account(models.Model):
    balance = models.DecimalField(max_digits=19, decimal_places=3)


class Journal(models.Model):
    debit = models.ForeignKey(
        Account, on_delete=models.DO_NOTHING, related_name="debits"
    )
    credit = models.ForeignKey(
        Account, on_delete=models.DO_NOTHING, related_name="credits"
    )
    amount = models.DecimalField(max_digits=19, decimal_places=3)


class InsufficientBalance(Exception):
    pass


def transfer(debit: Account, credit: Account, amount: int):
    with transaction.atomic():
        Journal.objects.create(debit=debit, credit=credit, amount=amount)
        count = Account.objects.filter(
            Q(pk=debit.pk, balance__gte=amount) | Q(pk=credit.pk)
        ).update(
            balance=Case(
                When(pk=debit.pk, then=F("balance") - amount),
                When(pk=credit.pk, then=F("balance") + amount),
            )
        )
        if count != 2:
            raise InsufficientBalance()


def run(a1: Account, a2: Account, n: int):
    start = time.time()
    for _ in range(n):
        transfer(a1, a2, 1)
        transfer(a2, a1, 1)
    end = time.time()
    print(f"{n*2} transfers in {end-start} seconds and {(n*2)/(end-start)} tps")
