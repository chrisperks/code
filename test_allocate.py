import pytest
from datetime import date, timedelta
from model import Batch, OrderLine, OutOfStock, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

def test_prefers_current_stock_batches_to_shipments():
  # Arrange
  line = OrderLine("order_1", "Chair", 10)
  batch_warehouse = Batch("batch_warehouse", "Chair", 10, None)
  batch_sea = Batch("batch_sea", "Chair", 10, tomorrow)

  # Act
  allocate(line, [batch_warehouse, batch_sea])

  # Assert
  assert batch_warehouse.available_quantity == 0
  assert batch_sea.available_quantity == 10

def test_prefers_earlier_batches():
  # Arrange
  line = OrderLine("order_1", "Chair", 10)
  batch_sea = Batch("batch_sea", "Chair", 10, tomorrow)
  batch_far_sea = Batch("batch_far_sea", "Chair", 10, later)

  # Act
  allocate(line, [batch_sea, batch_far_sea])

  # Assert
  assert batch_sea.available_quantity == 0
  assert batch_far_sea.available_quantity == 10

def test_returns_allocated_batch_ref():
  # Arrange
  line = OrderLine("order_1", "Chair", 10)
  batch_sea = Batch("batch_sea", "Chair", 10, tomorrow)
  batch_far_sea = Batch("batch_far_sea", "Chair", 10, later)

  # Act
  expected = batch_sea.reference
  actual = allocate(line, [batch_sea, batch_far_sea])

  # Assert
  assert expected == actual

def test_raises_out_of_stock_exception_if_cannot_allocate():
  # Arrange
  line = OrderLine("order_1", "Chair", 15)
  batch_sea = Batch("batch_sea", "Chair", 10, tomorrow) 

  # Act / Assert
  with pytest.raises(OutOfStock): 
    allocate(line, [batch_sea])