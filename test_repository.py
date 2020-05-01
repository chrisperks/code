# pylint: disable=protected-access
from model import Batch, OrderLine, allocate
import repository
import pytest
from datetime import date

def test_repository_can_save_a_batch(session):
    session.add(Batch("batch1", "Chair", 123, date(2011, 4, 11)))
    
    expected = Batch("batch1", "Chair", 123, date(2011, 4, 11))

    assert expected in session.query(Batch).all()

def test_repository_can_retrieve_a_batch_with_allocations(session):
    batch = Batch("batch1", "Chair", 500, date(2011, 4, 11))
    line = OrderLine("order1", "Chair", 200)
    allocate(line, [ batch ])
    session.add(batch)

    assert line in session.query(Batch).filter(Batch.reference == batch.reference).first()._allocations

def get_allocations(session, batchid):
    pytest.fail()
    
def test_updating_a_batch(session):

    sut = repository.SqlRepository(session)

    batch = Batch("batch1", "Chair", 500, date(2011, 4, 11))
    sut.add(batch)
    
    retrieved = sut.get("batch1")
    retrieved.eta = date(2012, 4, 12)

    session.commit()

    retrieved2 = sut.get("batch1")
    
    assert retrieved2.eta == date(2012, 4, 12)