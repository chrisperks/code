from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

import config
import model
import orm
import repository
import services


clear_mappers()
orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)

@app.route("/addbatch", methods=['POST'])
def add_batch_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    batch = model.Batch(
        request.json['ref'],
        request.json['sku'],
        request.json['qty'],
        request.json['eta'],
    )
    batchref = services.add_batch(batch, repo, session)
    return jsonify({'batchref': batchref}), 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json['orderid'],
        request.json['sku'],
        request.json['qty'],
    )
    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201


@app.route("/deallocate", methods=['POST'])
def deallocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json['orderid'],
        request.json['sku'],
        100,
    )
    batchref = services.deallocate(line, repo, session)
    return jsonify({'batchref': batchref}), 201