from pydantic import BaseModel


class Route(BaseModel):
    id: int
    agency_id: int
    short_name: str
    from_stop_name: str
    to_stop_name: str
    from_city: str
    to_city: str
    description: str
    type: int
    color: str

    @classmethod
    def from_row(cls, row: list) -> 'Route':
        return cls(
            id=row[0],
            agency_id=row[1],
            short_name=row[2],
            from_stop_name=row[3],
            to_stop_name=row[4],
            from_city=row[5],
            to_city=row[6],
            description=row[7],
            type=row[8],
            color=row[9]
        )


class StopLocation(BaseModel):
    type: str = 'Point'
    coordinates: tuple[float, float]


class Stop(BaseModel):
    id: int
    code: int
    name: str
    city: str | None = None
    street: str | None = None
    floor: str | None = None
    platform: int | None = None
    location: StopLocation
    location_type: int
    parent_station_id: int | None = None
    zone_id: int | None = None

    @classmethod
    def from_row(cls, row: list) -> 'Stop':
        return cls(
            id=row[0],
            code=row[2],
            name=row[6],
            city=row[1],
            street=row[9],
            floor=row[3],
            platform=row[8],
            location=StopLocation(coordinates=(row[11], row[12])),
            location_type=row[5],
            parent_station_id=row[7],
            zone_id=row[10]
        )

    class Config:
        collection = 'stops'

        schema_extra = {
            'example': {
                'id': 10846,
                'code': 5200,
                'name': 'בנייני האומה',
                'city': 'ירושלים',
                'street': 'שדרות שז''ר',
                'floor': None,
                'platform': None,
                'location': {
                    'type': 'Point',
                    'coordinates': [31.787909, 35.203428]
                },
                'location_type': '0',
                'parent_station_id': '',
                'zone_id': '3000'
            }
        }
