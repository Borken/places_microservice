from flask import make_response, abort
from sqlalchemy.exc import IntegrityError
import logging

from config import db
from api.models import Place, PlaceSchema

logger = logging.getLogger(__name__)


def get_all_places():
    places = Place.query.order_by(Place.name).all()
    place_schema = PlaceSchema(many=True)
    data = place_schema.dump(places).data
    return data


def get_place(place_id):
    place = Place.query.get_or_404(place_id, description=f'Place not found with the id: {place_id}')
    place_schema = PlaceSchema()
    data = place_schema.dump(place).data
    return data


def update_place(place_id, place_data):
    place = Place.query.get_or_404(place_id, description=f'Place not found with the id: {place_id}')
    place_schema = PlaceSchema()
    updated_place = place_schema.load(place_data, session=db.session).data
    updated_place.place_id = place.place_id
    db.session.merge(updated_place)
    try:
        db.session.commit()
        data = place_schema.dump(updated_place).data
        return data
    except IntegrityError as i:
        logger.error(f'IntegrityError: {i}')
        abort(500, f'Place: {place_id} could not be updated')


def post_place(place_data):
    place = Place.query.filter(Place.name == place_data.get('name')).one_or_none()
    if place is None:
        schema = PlaceSchema()
        new_place = schema.load(place_data, session=db.session).data
        db.session.add(new_place)
        db.session.commit()
        data = schema.dump(new_place).data
        return data, 201
    else:
        abort(409, f"Place: {place_data.get('name')} already exists")


def delete_place(place_id):
    place = Place.query.get_or_404(place_id, description=f'Place not found with the id: {place_id}')
    db.session.delete(place)
    db.session.commit()
    return 204

