from datetime import date, timedelta
from model import Batch, OrderLine, OutOfStock, allocate
import pytest

# from model import ...

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch_333", "Chair", 30, None)
    line = OrderLine("order_123", "Chair", 10)
    allocate(line, [batch])
    assert batch._purchased_quantity == 30
    assert batch.available_quantity == 20

def test_can_allocate_if_available_greater_than_required():
    batch = Batch("batch_333", "Chair", 30, None)
    line = OrderLine("order_123", "Chair", 10)
    allocate(line, [batch])
    line2 = OrderLine("order_124", "Chair", 10)
    allocate(line2, [batch])
    assert batch._purchased_quantity == 30
    assert batch.available_quantity == 10

def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch("batch_333", "Chair", 10, None)
    line = OrderLine("order_123", "Chair", 30)
    with pytest.raises(OutOfStock, match="Chair"): 
        allocate(line, [batch])

def test_can_allocate_if_available_equal_to_required():
    batch = Batch("batch_333", "Chair", 10, None)
    line = OrderLine("order_123", "Chair", 10)
    allocate(line, [batch])
    assert batch.available_quantity == 0

def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch("batch_warehouse", "Chair", 10, None)
    at_sea_batch = Batch("batch_sea", "Chair", 10, date.today() + timedelta(days=2))
    line = OrderLine("order_123", "Chair", 10)
    allocate(line, [in_stock_batch, at_sea_batch])
    assert in_stock_batch.available_quantity == 0
    assert at_sea_batch.available_quantity == 10

def test_prefers_earlier_batches():
    at_sea_batch = Batch("batch_sea", "Chair", 10, date.today() + timedelta(days=2))
    further_at_sea_batch = Batch("batch_sea", "Chair", 10, date.today() + timedelta(days=10))
    line = OrderLine("order_123", "Chair", 10)
    allocate(line, [at_sea_batch, further_at_sea_batch])
    assert at_sea_batch.available_quantity == 0
    assert further_at_sea_batch.available_quantity == 10

