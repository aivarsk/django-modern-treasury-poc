# A PoC of implementing Modern Treasury 

Showing how to do double-entry accounting without overcomplicating things as MT does (https://www.youtube.com/watch?v=knnSIKCsX34)

- entries always add up to the balance amount because ACID
- no 25 request per second limit
- without complex implementation and background tasks
- without 100 requests per second limitation in prod https://docs.moderntreasury.com/platform/reference/rate-limits
- and I did not implement batching of events, doing account partitions, or aggregating updates of multiple events
- and all this with a standard Django ORM without doing other performance tricks

This is a simple PoC without bells and whistles and I am skipping "pending balances" on purpose. At least for payment card transactions it's a  "hold" or "blocked" amount but it behaves differently: You may block/reserve 10 EUR during the authorization but the transaction might be for 10 EUR, 9.99 EUR, or 10.01 EUR or 2 transactions for 5 EUR each. Therefore part of the complexity is to match the transaction(s) with the authorization. After that you reduce the blocked balance and update the "real" balance and the amounts may differ.

As promised in https://aivarsk.com/2023/11/04/re-double-entry-accounting-at-scale/ and https://aivarsk.com/2025/03/14/The-COST-of-double-entry-accounting/

Following the https://docs.moderntreasury.com/ledgers/docs/digital-wallet-tutorial and getting around 200 ledger entries per second in my single-threaded low-end setup.

```
root@c6caa1bea9a1:/app# python3 manage.py shell
Python 3.12.4 (main, Aug  2 2024, 14:41:31) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from debitcredit.models import *
>>> run(1000)
3000 transfers in 13.226809740066528 seconds and 226.81206269357818 tps
>>>
```

-----------------------------------------

Documentation from Postgres about how/why it works
https://www.postgresql.org/docs/current/transaction-iso.html#XACT-READ-COMMITTED

And my presentation about the topic:
https://2023.djangoday.dk/talks/aivars/

