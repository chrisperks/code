import pytest
import model
from datetime import date

def test_orderline_mapper_can_load_lines(session):
    session.execute(
      'INSERT INTO order_lines (orderid, sku, qty) VALUES '
      '("order1", "RED-CHAIR", 12),'
      '("order1", "RED-TABLE", 13),'
      '("order2", "BLUE-LIPSTICK", 14)'
    )
    expected = [
        model.OrderLine("order1", "RED-CHAIR", 12),
        model.OrderLine("order1", "RED-TABLE", 13),
        model.OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    assert session.query(model.OrderLine).all() == expected

def test_orderline_mapper_can_save_lines(session):
    expected = [
        model.OrderLine("order1", "RED-CHAIR", 12),
        model.OrderLine("order1", "RED-TABLE", 13),
        model.OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]

    session.add(model.OrderLine("order1", "RED-CHAIR", 12));
    session.add(model.OrderLine("order1", "RED-TABLE", 13));
    session.add(model.OrderLine("order2", "BLUE-LIPSTICK", 14));

    assert session.query(model.OrderLine).all() == expected

def test_retrieving_batches(session):

  session.execute(
      'INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES ("batch1", "Chair", 123, "2011-04-11")'
    )

  session.execute(
      'INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES ("batch1", "Table", 123, null)'
    )

  expected = [
      model.Batch("batch1", "Chair", 123, date(2011, 4, 11)),
      model.Batch("batch1", "Table", 123, eta=None),
  ]
  assert session.query(model.Batch).all() == expected

def test_saving_batches(session):
  session.add(model.Batch("batch1", "Chair", 123, date(2011, 4, 11)));

  expected = [
    model.Batch("batch1", "Chair", 123, date(2011, 4, 11))
  ]

  assert session.query(model.Batch).all() == expected

def test_saving_allocations(session):
  batch = model.Batch("batch1", "Chair", 123, date(2011, 4, 11));
  line = model.OrderLine("order1", "Chair", 12)
  batch.allocate(line)

  session.add(batch)

  expected = model.OrderLine("order1", "Chair", 12)

  assert expected in session.query(model.Batch).first()._allocations

def test_retrieving_allocations(session):
  session.execute(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES ("order1", "sku1", 12)'
    )
  [[olid]] = session.execute(
      'SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku',
      dict(orderid='order1', sku='sku1')
  )
  session.execute(
      'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
      ' VALUES ("batch1", "sku1", 100, null)'
  )
  [[bid]] = session.execute(
      'SELECT id FROM batches WHERE reference=:ref AND sku=:sku',
      dict(ref='batch1', sku='sku1')
  )
  session.execute(
      'INSERT INTO allocations (orderline_id, batch_id) VALUES (:olid, :bid)',
      dict(olid=olid, bid=bid)
  )

  batch = session.query(model.Batch).one()

  assert batch._allocations == {
      model.OrderLine("order1", "sku1", 12)
  }
