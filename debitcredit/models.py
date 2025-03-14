import time
import uuid

from django.db import models, transaction
from django.db.models import Case, F, Q, When


class NormalBalance(models.TextChoices):
    DEBIT = "debit", "Debit"
    CREDIT = "credit", "Credit"


class Account(models.Model):
    credit = models.DecimalField(max_digits=19, decimal_places=3, default=0)
    debit = models.DecimalField(max_digits=19, decimal_places=3, default=0)
    normal_balance = models.CharField(max_length=8, choices=NormalBalance.choices)

    @property
    def balance(self):
        return self.credit - self.debit


class Journal(models.Model):
    debit = models.ForeignKey(
        Account, on_delete=models.DO_NOTHING, related_name="debits"
    )
    credit = models.ForeignKey(
        Account, on_delete=models.DO_NOTHING, related_name="credits"
    )
    amount = models.DecimalField(max_digits=19, decimal_places=3)
    external_id = models.CharField(max_length=64, unique=True)


class InsufficientBalance(Exception):
    pass


def transfer(external_id: str, debit: Account, credit: Account, amount: int):
    with transaction.atomic():
        Journal.objects.create(
            debit=debit, credit=credit, amount=amount, external_id=external_id
        )
        count = Account.objects.filter(
            Q(
                pk=debit.pk,
                normal_balance=NormalBalance.CREDIT,
                credit__gte=F("debit") + amount,
            )
            | Q(
                pk=debit.pk,
                normal_balance=NormalBalance.DEBIT,
                credit__lte=F("debit") + amount,
            )
            | Q(pk=credit.pk)
        ).update(
            debit=Case(When(pk=debit.pk, then=F("debit") + amount), default=F("debit")),
            credit=Case(
                When(pk=credit.pk, then=F("credit") + amount), default=F("credit")
            ),
        )
        if count != 2:
            raise InsufficientBalance()


def run(n: int):
    cash_account = Account.objects.create(normal_balance=NormalBalance.DEBIT)
    jane_account = Account.objects.create(normal_balance=NormalBalance.CREDIT)
    john_account = Account.objects.create(normal_balance=NormalBalance.CREDIT)

    start = time.time()
    for _ in range(n):
        transfer(str(uuid.uuid4()), cash_account, jane_account, 100)
        transfer(str(uuid.uuid4()), jane_account, john_account, 50)
        transfer(str(uuid.uuid4()), john_account, cash_account, 50)
    end = time.time()
    print(f"{n*3} transfers in {end-start} seconds and {(n*3)/(end-start)} tps")

    cash_account.refresh_from_db()
    assert cash_account.balance == -50 * n
    assert (
        Journal.objects.filter(debit=cash_account).aggregate(
            total=models.Sum("amount")
        )["total"]
        == 100 * n
    )
    assert (
        Journal.objects.filter(credit=cash_account).aggregate(
            total=models.Sum("amount")
        )["total"]
        == 50 * n
    )

    jane_account.refresh_from_db()
    assert jane_account.balance == 50 * n
    assert (
        Journal.objects.filter(debit=jane_account).aggregate(
            total=models.Sum("amount")
        )["total"]
        == 50 * n
    )
    assert (
        Journal.objects.filter(credit=jane_account).aggregate(
            total=models.Sum("amount")
        )["total"]
        == 100 * n
    )

    john_account.refresh_from_db()
    assert john_account.balance == 0
    assert (
        Journal.objects.filter(debit=john_account).aggregate(
            total=models.Sum("amount")
        )["total"]
        == 50 * n
    )
    assert (
        Journal.objects.filter(credit=john_account).aggregate(
            total=models.Sum("amount")
        )["total"]
        == 50 * n
    )
