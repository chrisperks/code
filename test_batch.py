import pytest
from model import Batch, OrderLine, OutOfStock, allocate
from datetime import date, timedelta

def make_batch_and_line(sku, batch_qty, line_qty):
  batch = Batch("batch_" + date.today().strftime('%s'), sku, batch_qty, None)
  line = OrderLine("order_" + date.today().strftime('%s'), sku, line_qty)
  return batch, line

def test_allocating_to_a_batch_reduces_the_available_quantity():
  # Arrange
  batch, line = make_batch_and_line("Chair", 10, 10)

  # Act 
  allocate(line, [batch])

  # Assert
  assert batch.available_quantity == 0

def test_can_allocate_if_available_greater_than_required():
  # Arrange
  batch, line = make_batch_and_line("Chair", 20, 10)

  # Act 
  allocate(line, [batch])

  # Assert
  assert batch.can_allocate(line) == True

def test_cannot_allocate_if_available_smaller_than_required():
  # Arrange
  batch, line = make_batch_and_line("Chair", 10, 20)
  
  # Act / Assert
  with pytest.raises(OutOfStock): 
    allocate(line, [batch])  

def test_can_allocate_if_available_equal_to_required():
  # Arrange
  batch, line = make_batch_and_line("Chair", 10, 10)

  # Act 
  can_allocate = batch.can_allocate(line)

  # Assert
  assert can_allocate == True

def test_cannot_allocate_if_skus_do_not_match():
  # Arrange
  batch, line = make_batch_and_line("Chair", 20, 10)
  _, line2 = make_batch_and_line("Table", 20, 10)

  # Act 
  can_allocate = batch.can_allocate(line2)

  # Assert
  assert can_allocate == False

def test_allocation_is_idempotent():
  # Arrange
  batch, line = make_batch_and_line("Chair", 10, 5)

  # Act 
  allocate(line, [batch])
  allocate(line, [batch])

  # Assert
  assert batch.available_quantity == 5

def test_deallocate():
  # Arrange
  batch, line = make_batch_and_line("Chair", 10, 5)

  # Act / Assert 
  allocate(line, [batch])
  assert line in batch._allocations
  batch.deallocate(line)
  assert line not in batch._allocations
  

def test_can_only_deallocate_allocated_lines():
  # Arrange
  batch, line = make_batch_and_line("Chair", 10, 5)
  _, line2 = make_batch_and_line("Table", 10, 5)

  # Act / Assert 
  allocate(line, [batch])
  assert line in batch._allocations
  batch.deallocate(line2)
  assert line2 not in batch._allocations